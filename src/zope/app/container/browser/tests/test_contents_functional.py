##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Functional tests for the Container's 'Contents' view
"""

import doctest
import unittest

import transaction
from persistent import Persistent
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.app.wsgi.testlayer import http
from zope.dublincore.interfaces import IZopeDublinCore
from zope.interface import Interface
from zope.interface import implementer

from zope import copypastemove
from zope.app.container.browser.tests import BrowserTestCase
from zope.app.container.browser.tests.test_contents import provideAdapter
from zope.app.container.interfaces import IContained
from zope.app.container.interfaces import IReadContainer
from zope.app.container.testing import AppContainerLayer


class IImmovable(Interface):
    """Marker interface for immovable objects."""


class IUncopyable(Interface):
    """Marker interface for uncopyable objects."""


@implementer(IAttributeAnnotatable)
class File(Persistent):
    pass


@implementer(IImmovable)
class ImmovableFile(File):
    pass


@implementer(IUncopyable)
class UncopyableFile(File):
    pass


class ObjectNonCopier(copypastemove.ObjectCopier):

    def copyable(self):
        return False


class ObjectNonMover(copypastemove.ObjectMover):

    def moveable(self):
        return False


@implementer(IReadContainer, IContained)
class ReadOnlyContainer(Persistent):

    __parent__ = __name__ = None

    def __init__(self):
        self.data = {}

    def keys(self):
        return self.data.keys()

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)

    def __iter__(self):
        return iter(self.data)

    def values(self):
        return self.data.values()

    def __len__(self):
        return len(self.data)

    def items(self):
        return self.data.items()

    def __contains__(self, key):
        return key in self.data

    def has_key(self, key):
        return key in self.data


class Test(BrowserTestCase):

    def test_inplace_add(self):
        root = self.getRootFolder()
        self.assertNotIn('foo', root)
        response = self.publish(
            '/@@contents.html',
            basic='mgr:mgrpw',
            form={'type_name': 'BrowserAdd__zope.site.folder.Folder'})
        body = response.unicode_normal_body
        self.assertIn('type="hidden" name="type_name"', body)
        self.assertIn('input name="new_value"', body)
        self.assertIn('type="submit" name="container_cancel_button"', body)
        self.assertNotIn('type="submit" name="container_rename_button"', body)

        response = self.publish(
            '/@@contents.html',
            basic='mgr:mgrpw',
            form={'type_name': 'BrowserAdd__zope.site.folder.Folder',
                  'new_value': 'foo'})
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.headers.get('Location'),
                         'http://localhost/@@contents.html')

        root._p_jar.sync()
        self.assertIn('foo', root)

    def test_inplace_rename_multiple(self):
        root = self.getRootFolder()
        root['foo'] = File()
        self.assertIn('foo', root)
        transaction.commit()

        # Check that we don't change mode if there are no items selected

        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'container_rename_button': ''})
        body = response.unicode_normal_body
        self.assertNotIn('input name="new_value:list"', body)
        self.assertNotIn('type="submit" name="container_cancel_button"', body)
        self.assertIn('type="submit" name="container_rename_button"', body)
        self.assertIn('div class="page_error"', body)

        # Check normal multiple select

        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'container_rename_button': '',
                                      'ids:list': ['foo']})
        body = response.unicode_normal_body
        self.assertIn('input name="new_value:list"', body)
        self.assertIn('type="submit" name="container_cancel_button"', body)
        self.assertNotIn('type="submit" name="container_rename_button"', body)

        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'rename_ids:list': ['foo'],
                                      'new_value:list': ['bar']})
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.headers.get('Location'),
                         'http://localhost/@@contents.html')

        root._p_jar.sync()
        self.assertNotIn('foo', root)
        self.assertIn('bar', root)

    def test_inplace_rename_single(self):
        root = self.getRootFolder()
        root['foo'] = File()
        self.assertIn('foo', root)
        transaction.commit()

        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'rename_ids:list': ['foo']})
        body = response.unicode_normal_body
        self.assertIn('input name="new_value:list"', body)
        self.assertIn('type="submit" name="container_cancel_button"', body)
        self.assertNotIn('type="submit" name="container_rename_button"', body)

        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'rename_ids:list': ['foo'],
                                      'new_value:list': ['bar']})
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.headers.get('Location'),
                         'http://localhost/@@contents.html')

        root._p_jar.sync()
        self.assertNotIn('foo', root)
        self.assertIn('bar', root)

    def test_inplace_change_title(self):
        root = self.getRootFolder()
        root['foo'] = File()
        transaction.commit()
        self.assertIn('foo', root)
        dc = IZopeDublinCore(root['foo'])
        self.assertEqual(dc.title, '')

        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'retitle_id': 'foo'})
        body = ' '.join(response.text.split())
        self.assertIn('type="hidden" name="retitle_id"', body)
        self.assertIn('input name="new_value"', body)
        self.assertIn('type="submit" name="container_cancel_button"', body)
        self.assertNotIn('type="submit" name="container_rename_button"', body)

        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'retitle_id': 'foo',
                                      'new_value': 'test title'})
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.headers.get('Location'),
                         'http://localhost/@@contents.html')

        root._p_jar.sync()
        self.assertIn('foo', root)
        dc = IZopeDublinCore(root['foo'])
        self.assertEqual(dc.title, 'test title')

    def test_pasteable_for_deleted_clipboard_item(self):
        """Test Paste button visibility when copied item is deleted."""
        root = self.getRootFolder()
        root['foo'] = File()    # item to be copied/deleted
        # Ensure that there's always an item in the collection view:
        root['bar'] = File()
        transaction.commit()

        # confirm foo in contents, Copy button visible, Paste not visible
        response = self.publish('/@@contents.html', basic='mgr:mgrpw')
        self.assertEqual(response.status_int, 200)
        self.assertIn(
            '<a href="foo/@@SelectedManagementView.html">foo</a>',
            response.text)
        self.assertIn(
            '<input type="submit" name="container_copy_button"',
            response.text)
        self.assertNotIn(
            '<input type="submit" name="container_paste_button"',
            response.text)

        # copy foo - confirm Paste visible
        response = self.publish('/@@contents.html', basic='mgr:mgrpw', form={
            'ids:list': ('foo',),
            'container_copy_button': ''})
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.headers.get('Location'),
                         'http://localhost/@@contents.html')
        response = self.publish('/@@contents.html', basic='mgr:mgrpw')
        self.assertEqual(response.status_int, 200)
        self.assertIn(
            '<input type="submit" name="container_paste_button"',
            response.text)

        # delete foo -> nothing valid to paste -> Paste should not be visible
        del root['foo']
        transaction.commit()
        response = self.publish('/@@contents.html', basic='mgr:mgrpw')
        self.assertEqual(response.status_int, 200)
        self.assertNotIn(
            '<input type="submit" name="container_paste_button"',
            response.text)

    def test_paste_for_deleted_clipboard_item(self):
        """Tests paste operation when one of two copied items is deleted."""

        root = self.getRootFolder()
        root['foo'] = File()
        root['bar'] = File()
        transaction.commit()

        # confirm foo/bar in contents, Copy button visible, Paste not visible
        response = self.publish('/@@contents.html', basic='mgr:mgrpw')
        self.assertEqual(response.status_int, 200)
        self.assertIn(
            '<a href="foo/@@SelectedManagementView.html">foo</a>',
            response.text)
        self.assertIn(
            '<a href="bar/@@SelectedManagementView.html">bar</a>',
            response.text)
        self.assertIn(
            '<input type="submit" name="container_copy_button"',
            response.text)
        self.assertNotIn(
            '<input type="submit" name="container_paste_button"',
            response.text)

        # copy foo and bar - confirm Paste visible
        response = self.publish('/@@contents.html', basic='mgr:mgrpw', form={
            'ids': ('foo', 'bar'),
            'container_copy_button': ''})
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.headers.get('Location'),
                         'http://localhost/@@contents.html')
        response = self.publish('/@@contents.html', basic='mgr:mgrpw')
        self.assertEqual(response.status_int, 200)
        self.assertIn(
            '<input type="submit" name="container_paste_button"',
            response.text)

        # delete only foo -> bar still available -> Paste should be visible
        del root['foo']
        transaction.commit()
        response = self.publish('/@@contents.html', basic='mgr:mgrpw')
        self.assertEqual(response.status_int, 200)
        self.assertIn(
            '<input type="submit" name="container_paste_button"',
            response.text)

        # paste clipboard contents - only bar should be copied
        response = self.publish('/@@contents.html', basic='mgr:mgrpw', form={
            'container_paste_button': ''})
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.headers.get('Location'),
                         'http://localhost/@@contents.html')
        response = self.publish('/@@contents.html', basic='mgr:mgrpw')
        self.assertEqual(response.status_int, 200)
        root._p_jar.sync()
        self.assertEqual(tuple(root.keys()), ('bar', 'bar-2'))

    def test_readonly_display(self):
        root = self.getRootFolder()
        root['foo'] = ReadOnlyContainer()
        transaction.commit()
        response = self.publish('/foo/@@contents.html', basic='mgr:mgrpw')
        self.assertEqual(response.status_int, 200)

    def test_uncopyable_object(self):
        provideAdapter(IUncopyable,
                       copypastemove.interfaces.IObjectCopier,
                       ObjectNonCopier)
        root = self.getRootFolder()
        root['uncopyable'] = UncopyableFile()
        transaction.commit()
        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'ids:list': ['uncopyable'],
                                      'container_copy_button': 'Copy'})
        self.assertEqual(response.status_int, 200)
        body = response.text
        self.assertIn("cannot be copied", body)

    def test_unmoveable_object(self):
        provideAdapter(IImmovable,
                       copypastemove.interfaces.IObjectMover,
                       ObjectNonMover)
        root = self.getRootFolder()
        root['immovable'] = ImmovableFile()
        transaction.commit()
        response = self.publish('/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'ids:list': ['immovable'],
                                      'container_cut_button': 'Cut'})
        self.assertEqual(response.status_int, 200)
        body = response.text
        self.assertIn("cannot be moved", body)

    def test_copy_then_delete_with_unicode_name(self):
        # Tests unicode on object copied then deleted (#238579)

        # The 'Accept-Charset' is important to get
        # the encoding correct. The query string is actually correctly
        # decoded to unicode (if it's ever even *encoded*) on the
        # receiving side, but
        # zope.publisher.browser.BrowserRequest._decode assumes it was
        # smuggled as latin-1, and thus encodes it back to those
        # bytes. If we don't specify latin-1 as a charset
        # zope.publsher.http.HTTPCharsets will only let it try to be
        # decoded as utf-8, which doesn't work.

        # This is most likely a mismatch
        # somewhere in the
        # webtest.TestApp/zope.app.wsgi.testlayer/zope.publisher stack.

        # create a file with an accentuated unicode name
        root = self.getRootFolder()
        root['voil\xe0'] = File()
        transaction.commit()

        # copy the object
        response = self.publish(
            '/@@contents.html',
            basic='mgr:mgrpw',
            form={
                'ids:list': 'voil\xe0'.encode(),
                'container_copy_button': '',
            },
            headers={
                'Accept-Charset': 'latin-1, utf-8',
            },
        )
        self.assertEqual(response.status_int, 302)
        self.assertEqual(response.headers.get('Location'),
                         'http://localhost/@@contents.html')
        response = self.publish('/@@contents.html', basic='mgr:mgrpw')
        self.assertEqual(response.status_int, 200)

        # delete the object
        del root['voil\xe0']
        transaction.commit()
        response = self.publish('/@@contents.html', basic='mgr:mgrpw')
        self.assertEqual(response.status_int, 200)


def test_suite():
    suite = unittest.TestSuite()
    Test.layer = AppContainerLayer
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Test))

    def _http(query_str, *args, **kwargs):
        wsgi_app = AppContainerLayer.make_wsgi_app()
        # Strip leading \n
        query_str = query_str.lstrip()
        return http(wsgi_app, query_str, *args, **kwargs)

    globs = {'http': _http}

    index = doctest.DocFileSuite("index.txt", globs=globs)
    index.layer = AppContainerLayer
    suite.addTest(index)
    return suite
