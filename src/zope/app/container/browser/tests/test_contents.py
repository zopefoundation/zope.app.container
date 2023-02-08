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
"""Test Container Contents
"""
import unittest

from zope.annotation.interfaces import IAnnotations
from zope.component.eventtesting import getEvents
from zope.container.contained import contained
from zope.container.interfaces import IContainer
from zope.copypastemove import ContainerItemRenamer
from zope.copypastemove import ObjectCopier
from zope.copypastemove import ObjectMover
from zope.copypastemove import PrincipalClipboard
from zope.copypastemove.interfaces import IContainerItemRenamer
from zope.copypastemove.interfaces import IObjectCopier
from zope.copypastemove.interfaces import IObjectMover
from zope.copypastemove.interfaces import IPrincipalClipboard
from zope.interface import Interface
from zope.interface import implementer
from zope.location.interfaces import IContained
from zope.security import checker
from zope.traversing.api import traverse

from zope.app.container.browser.tests import provideAdapter
from zope.app.container.testing import PlacefulSetup


class BaseTestContentsBrowserView(PlacefulSetup):
    """Base class for testing browser contents.

    Subclasses need to define a method, '_TestView__newContext', that
    takes no arguments and that returns a new empty test view context.

    Subclasses need to define a method, '_TestView__newView', that
    takes a context object and that returns a new test view.
    """

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)

        provideAdapter(IContained, IObjectCopier, ObjectCopier)
        provideAdapter(IContained, IObjectMover, ObjectMover)
        provideAdapter(IContainer, IContainerItemRenamer,
                       ContainerItemRenamer)

        provideAdapter(IAnnotations, IPrincipalClipboard,
                       PrincipalClipboard)
        provideAdapter(Principal, IAnnotations,
                       PrincipalAnnotations)

    def testInfo(self):
        # Do we get the correct information back from ContainerContents?
        container = self._TestView__newContext()
        subcontainer = self._TestView__newContext()
        container['subcontainer'] = subcontainer
        document = Document()
        container['document'] = document

        fc = self._TestView__newView(container)
        info_list = fc.listContentInfo()

        self.assertEqual(len(info_list), 2)

        ids = [x['id'] for x in info_list]
        self.assertIn('subcontainer', ids)

        objects = [x['object'] for x in info_list]
        self.assertIn(subcontainer, objects)

        urls = [x['url'] for x in info_list]
        self.assertIn('subcontainer', urls)

        icons = [x['icon'] for x in info_list if x['icon']]
        self.assertEqual([], icons)

    def testInfoUnicode(self):
        # If the id contains non-ASCII characters, url has to be quoted
        container = self._TestView__newContext()
        subcontainer = self._TestView__newContext()
        container['f\xf6\xf6'] = subcontainer

        fc = self._TestView__newView(container)
        info_list = fc.listContentInfo()

        urls = [x['url'] for x in info_list]
        self.assertIn('f%C3%B6%C3%B6', urls)

    def testInfoWDublinCore(self):
        container = self._TestView__newContext()
        document = Document()
        container['document'] = document

        from datetime import datetime

        from zope.dublincore.interfaces import IZopeDublinCore

        @implementer(IZopeDublinCore)
        class FauxDCAdapter:

            __Security_checker__ = checker.Checker(
                {"created": "zope.Public",
                 "modified": "zope.Public",
                 "title": "zope.Public",
                 },
                {"title": "zope.app.dublincore.change"})

            def __init__(self, context):
                pass
            title = 'faux title'
            size = 1024
            created = datetime(2001, 1, 1, 1, 1, 1)
            modified = datetime(2002, 2, 2, 2, 2, 2)

        provideAdapter(IDocument, IZopeDublinCore, FauxDCAdapter)

        fc = self._TestView__newView(container)
        info = fc.listContentInfo()[0]

        self.assertEqual(info['id'], 'document')
        self.assertEqual(info['url'], 'document')
        self.assertEqual(info['object'], document)
        self.assertEqual(info['title'], 'faux title')
        self.assertEqual(info['created'], '01/01/01 01:01')
        self.assertEqual(info['modified'], '02/02/02 02:02')

    def testRemove(self):
        container = self._TestView__newContext()
        subcontainer = self._TestView__newContext()
        container['subcontainer'] = subcontainer
        document = Document()
        container['document'] = document
        document2 = Document()
        container['document2'] = document2

        fc = self._TestView__newView(container)

        fc.request.form.update({'ids': ['document2']})

        fc.removeObjects()

        info_list = fc.listContentInfo()

        self.assertEqual(len(info_list), 2)

        ids = [x['id'] for x in info_list]
        self.assertIn('subcontainer', ids)

        objects = [x['object'] for x in info_list]
        self.assertIn(subcontainer, objects)

        urls = [x['url'] for x in info_list]
        self.assertIn('subcontainer', urls)

    def testChangeTitle(self):
        container = self._TestView__newContext()
        document = Document()
        container['document'] = document

        from zope.dublincore.interfaces import IDCDescriptiveProperties

        @implementer(IDCDescriptiveProperties)
        class FauxDCDescriptiveProperties:

            __Security_checker__ = checker.Checker(
                {"title": "zope.Public",
                 },
                {"title": "zope.app.dublincore.change"})

            def __init__(self, context):
                self.context = context

            def setTitle(self, title):
                self.context.title = title

            def getTitle(self):
                return self.context.title

            title = property(getTitle, setTitle)

        provideAdapter(
            IDocument,
            IDCDescriptiveProperties,
            FauxDCDescriptiveProperties)

        fc = self._TestView__newView(container)

        dc = IDCDescriptiveProperties(document)

        fc.request.form.update({'retitle_id': 'document', 'new_value': 'new'})
        fc.changeTitle()
        events = getEvents()
        self.assertEqual(dc.title, 'new')
        self.assertIn('title', events[-1].descriptions[0].attributes)


class IDocument(Interface):
    pass


@implementer(IDocument)
class Document:
    pass


class Principal:

    id = 'bob'


@implementer(IAnnotations)
class PrincipalAnnotations(dict):

    data = {}

    def __new__(class_, context):
        try:
            annotations = class_.data[context.id]
        except KeyError:
            annotations = dict.__new__(class_)
            class_.data[context.id] = annotations
        return annotations

    def __init__(self, context):
        pass

    def __repr__(self):  # pragma: no cover
        return "<%s.PrincipalAnnotations object>" % __name__


class TestCutCopyPaste(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)
        provideAdapter(IContained, IObjectCopier, ObjectCopier)
        provideAdapter(IContained, IObjectMover, ObjectMover)
        provideAdapter(IContainer, IContainerItemRenamer,
                       ContainerItemRenamer)

        provideAdapter(IAnnotations, IPrincipalClipboard,
                       PrincipalClipboard)
        provideAdapter(Principal, IAnnotations,
                       PrincipalAnnotations)

    def testRename(self):
        container = traverse(self.rootFolder, 'folder1')
        fc = self._TestView__newView(container)
        ids = ['document1', 'document2']
        for id in ids:
            document = Document()
            container[id] = document
        fc.request.form.update({'rename_ids': ids,
                                'new_value': ['document1_1', 'document2_2']
                                })
        fc.renameObjects()
        self.assertIn('document1_1', container)
        self.assertNotIn('document1', container)

    def testCopyPaste(self):
        container = traverse(self.rootFolder, 'folder1')
        fc = self._TestView__newView(container)
        ids = ['document1', 'document2']
        for id in ids:
            document = Document()
            container[id] = document

        fc.request.form['ids'] = ids
        fc.copyObjects()
        fc.pasteObjects()
        self.assertIn('document1', container)
        self.assertIn('document2', container)
        self.assertIn('document1-2', container)
        self.assertIn('document2-2', container)

    def testCopyFolder(self):
        container = traverse(self.rootFolder, 'folder1')
        fc = self._TestView__newView(container)
        ids = ['folder1_1']
        fc.request.form['ids'] = ids
        fc.copyObjects()
        fc.pasteObjects()
        self.assertIn('folder1_1', container)
        self.assertIn('folder1_1-2', container)

    def testCopyFolder2(self):
        container = traverse(self.rootFolder, '/folder1/folder1_1')
        fc = self._TestView__newView(container)
        ids = ['folder1_1_1']
        fc.request.form['ids'] = ids
        fc.copyObjects()
        fc.pasteObjects()
        self.assertIn('folder1_1_1', container)
        self.assertIn('folder1_1_1-2', container)

    def testCopyFolder3(self):
        container = traverse(self.rootFolder, '/folder1/folder1_1')
        target = traverse(self.rootFolder, '/folder2/folder2_1')
        fc = self._TestView__newView(container)
        tg = self._TestView__newView(target)
        ids = ['folder1_1_1']
        fc.request.form['ids'] = ids
        fc.copyObjects()
        tg.pasteObjects()
        self.assertIn('folder1_1_1', container)
        self.assertIn('folder1_1_1', target)

    def testCutPaste(self):
        container = traverse(self.rootFolder, 'folder1')
        fc = self._TestView__newView(container)
        ids = ['document1', 'document2']
        for id in ids:
            document = Document()
            container[id] = document
        fc.request.form['ids'] = ids
        fc.cutObjects()
        fc.pasteObjects()
        self.assertIn('document1', container)
        self.assertIn('document2', container)

    def testCutFolder(self):
        container = traverse(self.rootFolder, 'folder1')
        fc = self._TestView__newView(container)
        ids = ['folder1_1']
        fc.request.form['ids'] = ids
        fc.cutObjects()
        fc.pasteObjects()
        self.assertIn('folder1_1', container)

    def testCutFolder2(self):
        container = traverse(self.rootFolder, '/folder1/folder1_1')
        fc = self._TestView__newView(container)
        ids = ['folder1_1_1']
        fc.request.form['ids'] = ids
        fc.cutObjects()
        fc.pasteObjects()
        self.assertIn('folder1_1_1', container)

    def testCutFolder3(self):
        container = traverse(self.rootFolder, '/folder1/folder1_1')
        target = traverse(self.rootFolder, '/folder2/folder2_1')
        fc = self._TestView__newView(container)
        tg = self._TestView__newView(target)
        ids = ['folder1_1_1']
        fc.request.form['ids'] = ids
        fc.cutObjects()
        tg.pasteObjects()
        self.assertNotIn('folder1_1_1', container)
        self.assertIn('folder1_1_1', target)

    def _TestView__newView(self, container):
        from zope.publisher.browser import TestRequest

        from zope.app.container.browser.contents import Contents
        request = TestRequest()
        request.setPrincipal(Principal())
        return Contents(container, request)


class Test(BaseTestContentsBrowserView, unittest.TestCase):

    def _TestView__newContext(self):
        from zope.site.folder import rootFolder

        from zope.app.container.sample import SampleContainer
        root = rootFolder()
        container = SampleContainer()
        return contained(container, root, 'sample')

    def _TestView__newView(self, container):
        from zope.publisher.browser import TestRequest

        from zope.app.container.browser.contents import Contents
        request = TestRequest()
        request.setPrincipal(Principal())
        return Contents(container, request)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
