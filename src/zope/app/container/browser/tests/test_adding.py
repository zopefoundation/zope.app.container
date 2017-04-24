##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
"""Adding implementation tests
"""
import doctest
import unittest

import zope.interface
import zope.security.checker
from zope.component.interfaces import IFactory
from zope.component.interfaces import ComponentLookupError
from zope.interface import implementer, Interface, directlyProvides
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import BrowserView
from zope.browsermenu.interfaces import AddMenu
from zope.browsermenu.interfaces import IMenuItemType, IBrowserMenu
from zope.browsermenu.menu import BrowserMenuItem, BrowserMenu
from zope.security.interfaces import ForbiddenAttribute
from zope.exceptions.interfaces import UserError
from zope.traversing.api import getParent
from zope.traversing.browser import AbsoluteURL
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.interfaces import IContainmentRoot

from zope.app.testing import ztapi
from zope.app.testing.placelesssetup import PlacelessSetup, setUp, tearDown
from zope.app.container.interfaces import IAdding
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IContainerNamesContainer
from zope.app.container.interfaces import INameChooser
from zope.app.container.interfaces import IContainer
from zope.app.container.contained import contained
from zope.app.container.browser.adding import Adding
from zope.app.container.sample import SampleContainer

@implementer(IContainmentRoot)
class Root(object):
    pass

class Container(SampleContainer):
    pass

class CreationView(BrowserView):

    def action(self):
        return 'been there, done that'


class Content(object):
    pass


@implementer(IFactory)
class Factory(object):


    title = ''
    description = ''

    def __call__(self):
        return Content()


class AbsoluteURL(BrowserView):

    def __str__(self):
        if IContainmentRoot.providedBy(self.context):
            return ''
        name = self.context.__name__
        url = absoluteURL(getParent(self.context), self.request)
        url += '/' + name
        return url

    __call__ = __str__

def defineMenuItem(menuItemType, for_, action, title=u'', extra=None):
    newclass = type(title, (BrowserMenuItem,),
                    {'title':title, 'action':action,
                     '_for': for_, 'extra':extra})
    zope.interface.classImplements(newclass, menuItemType)
    ztapi.provideAdapter((for_, IBrowserRequest), menuItemType, newclass, title)

def registerAddMenu():
  ztapi.provideUtility(IMenuItemType, AddMenu, 'zope.app.container.add')
  ztapi.provideUtility(IBrowserMenu,
                       BrowserMenu('zope.app.container.add', u'', u''),
                       'zope.app.container.add')


class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(Test, self).setUp()

    def test(self):
        container = Container()
        request = TestRequest()
        adding = Adding(container, request)
        ztapi.browserView(IAdding, "Thing", CreationView)
        self.assertEqual(adding.contentName, None)
        view = adding.publishTraverse(request, 'Thing=foo')
        self.assertEqual(view.action(), 'been there, done that')
        self.assertEqual(adding.contentName, 'foo')

        o = object()
        result = adding.add(o)

        # Check the state of the container and result
        self.assertEqual(container["foo"], o)
        self.assertEqual(result, o)

    def testNoNameGiven(self):
        container = Container()
        request = TestRequest()
        adding = Adding(container, request)
        ztapi.browserView(IAdding, "Thing", CreationView)

        self.assertEqual(adding.contentName, None)
        view = adding.publishTraverse(request, 'Thing=')
        self.assertEqual(adding.contentName, '')

    def testAction(self):
        # make a private factory
        ztapi.provideUtility(IFactory, Factory(), 'fooprivate')

        factory = Factory()
        factory.__Security_checker__ = zope.security.checker.NamesChecker(
            ['__call__'])
        ztapi.provideUtility(IFactory, factory, 'foo')

        container = Container()
        adding = Adding(container, TestRequest())
        adding.nextURL = lambda: '.'
        adding.nameAllowed = lambda: True

        # we can't use a private factory:
        self.assertRaises(ForbiddenAttribute,
                          adding.action, type_name='fooprivate', id='bar')

        # typical add - id is provided by user
        adding.action(type_name='foo', id='bar')
        self.assertIn('bar', container)

        # missing type_name
        self.assertRaises(UserError, adding.action, id='bar')

        # missing id
        self.assertRaises(KeyError, adding.action, type_name='foo')

        # bad type_name
        self.assertRaises(ComponentLookupError, adding.action,
            type_name='***', id='bar')

        # alternative add - id is provided internally instead of from user
        adding.nameAllowed = lambda: False
        adding.contentName = 'baz'
        adding.action(type_name='foo')
        self.assertIn('baz', container)

        # alternative add w/missing contentName
        # Note: Passing is None as object name might be okay, if the container
        #       is able to hand out ids itself. Let's not require a content
        #       name to be specified!
        # For the container, (or really, the chooser, to choose, we have to
        # marke the container as a ContainerNamesContainer
        directlyProvides(container, IContainerNamesContainer)
        adding.contentName = None
        adding.action(type_name='foo')
        self.assertIn('Content', container)


    def test_action(self):
        container = Container()
        container = contained(container, Root(), "container")
        request = TestRequest()
        adding = Adding(container, request)
        adding.__name__ = '+'
        ztapi.browserView(IAdding, "Thing", CreationView)
        ztapi.browserView(Interface, "absolute_url", AbsoluteURL)
        ztapi.browserView(None, '', AbsoluteURL, providing=IAbsoluteURL)
        self.assertRaises(UserError, adding.action, '', 'foo')
        adding.action('Thing', 'foo')
        self.assertEqual(adding.request.response.getHeader('location'),
                         '/container/+/Thing=foo')
        adding.action('Thing/screen1', 'foo')
        self.assertEqual(adding.request.response.getHeader('location'),
                         '/container/+/Thing/screen1=foo')

    def test_publishTraverse_factory(self):
        factory = Factory()
        ztapi.provideUtility(IFactory, factory, 'foo')
        container = Container()
        request = TestRequest()
        adding = Adding(container, request)
        self.assertIs(adding.publishTraverse(request, 'foo'), factory)


def test_constraint_driven_addingInfo():
    """
    >>> registerAddMenu()

    >>> class TestMenu(zope.interface.Interface):
    ...     pass
    >>> zope.interface.directlyProvides(TestMenu, IMenuItemType)

    >>> ztapi.provideUtility(IMenuItemType, TestMenu, 'TestMenu')
    >>> ztapi.provideUtility(IBrowserMenu, BrowserMenu('TestMenu', u'', u''),
    ...                      'TestMenu')

    >>> defineMenuItem(TestMenu, IAdding, '', 'item1')
    >>> defineMenuItem(TestMenu, IAdding, '', 'Item2')

    >>> defineMenuItem(AddMenu, IAdding, '', 'item3', extra={'factory': 'f1'})
    >>> defineMenuItem(AddMenu, IAdding, '', 'item4', extra={'factory': 'f2'})

    >>> class F1(object):
    ...     pass

    >>> class F2(object):
    ...     pass

    >>> def pre(container, name, object):
    ...     if not isinstance(object, F1):
    ...         raise zope.interface.Invalid()
    >>> def prefactory(container, name, factory):
    ...     if factory._callable is not F1:
    ...         raise zope.interface.Invalid()
    >>> pre.factory = prefactory


    >>> class IContainer(zope.interface.Interface):
    ...     def __setitem__(name, object):
    ...         pass
    ...     __setitem__.precondition = pre

    >>> @zope.interface.implementer(IContainer)
    ... class Container(object):
    ...    pass

    >>> from zope.component.factory import Factory
    >>> ztapi.provideUtility(IFactory, Factory(F1), 'f1')
    >>> ztapi.provideUtility(IFactory, Factory(F2), 'f2')

    >>> from zope.app.container.browser.adding import Adding
    >>> adding = Adding(Container(), TestRequest())
    >>> items = adding.addingInfo()
    >>> len(items)
    1
    >>> items[0]['title']
    u'item3'

    >>> adding.menu_id = 'TestMenu'
    >>> items = adding.addingInfo()
    >>> len(items)
    3
    >>> items[0]['title']
    u'item1'
    >>> items[1]['title'] # the collator ordered this one correctly!
    u'Item2'
    >>> items[2]['title']
    u'item3'
    """

def test_constraint_driven_add():
    """
    >>> from zope.app.container.sample import SampleContainer
    >>> from zope.app.container.browser.adding import Adding

    >>> class F1(object):
    ...     pass

    >>> class F2(object):
    ...     pass

    >>> def pre(container, name, object):
    ...     "a mock item constraint "
    ...     if not isinstance(object, F1):
    ...         raise zope.interface.Invalid('not a valid child')

    >>> class ITestContainer(zope.interface.Interface):
    ...     def __setitem__(name, object):
    ...         pass
    ...     __setitem__.precondition = pre

    >>> @zope.interface.implementer(ITestContainer)
    ... class Container(SampleContainer):
    ...    pass

    >>> adding = Adding(Container(), TestRequest())
    >>> c = adding.add(F1())

    This test should fail, because the container only
    accepts instances of F1

    >>> adding.add(F2())
    Traceback (most recent call last):
    ...
    Invalid: not a valid child

    >>> @zope.interface.implementer(ITestContainer)
    ... class ValidContainer(SampleContainer):
    ...    pass

    >>> def constr(container):
    ...     "a mock container constraint"
    ...     if not isinstance(container, ValidContainer):
    ...         raise zope.interface.Invalid('not a valid container')
    ...     return True

    >>> class I2(zope.interface.Interface):
    ...     __parent__ = zope.schema.Field(constraint = constr)

    >>> zope.interface.classImplements(F1, I2)

    This adding now fails, because the Container is not a valid
    parent for F1

    >>> c = adding.add(F1())
    Traceback (most recent call last):
    ...
    Invalid: not a valid container

    >>> adding = Adding(ValidContainer(), TestRequest())
    >>> c = adding.add(F1())

    """


def test_nameAllowed():
    """
    Test for nameAllowed in adding.py

    >>> from zope.app.container.browser.adding import Adding
    >>> from zope.app.container.interfaces import IContainerNamesContainer

    Class implements IContainerNamesContainer

    >>> @zope.interface.implementer(IContainerNamesContainer)
    ... class FakeContainer(object):
    ...    pass

    nameAllowed returns False if the class imlements
    IContainerNamesContainer

    >>> adding = Adding(FakeContainer(),TestRequest())
    >>> adding.nameAllowed()
    False

    Fake class without IContainerNamesContainer

    >>> class Fake(object):
    ...    pass

    nameAllowed returns True if the class
    doesn't imlement IContainerNamesContainer

    >>> adding = Adding(Fake(),TestRequest())
    >>> adding.nameAllowed()
    True

    """



def test_chooseName():
    """If user don't enter name, pick one

    >>> @zope.interface.implementer(INameChooser, IContainer)
    ... class MyContainer(object):
    ...    args = {}
    ...
    ...    def chooseName(self, name, object):
    ...        self.args["choose"] = name, object
    ...        return 'pickone'
    ...    def checkName(self, name, object):
    ...        self.args["check"] = name, object
    ...    def __setitem__(self, name, object):
    ...        setattr(self, name, object)
    ...        self.name = name
    ...    def __getitem__(self, key):
    ...        return getattr(self, key)

    >>> request = TestRequest()
    >>> mycontainer = MyContainer()
    >>> adding = Adding(mycontainer, request)
    >>> o = object()
    >>> add_obj = adding.add(o)
    >>> mycontainer.name
    'pickone'
    >>> add_obj is o
    True

    Make sure right arguments passed to INameChooser adapter:

    >>> name, obj = mycontainer.args["choose"]
    >>> name
    ''
    >>> obj is o
    True
    >>> name, obj = mycontainer.args["check"]
    >>> name
    'pickone'
    >>> obj is o
    True
    """



def test_SingleMenuItem_and_CustomAddView_NonICNC():
    """
    This tests the condition if the content has Custom Add views and
    the container contains only a single content object

    >>> registerAddMenu()
    >>> defineMenuItem(AddMenu, IAdding, '', 'item3', extra={'factory': 'f1'})

    >>> class F1(object):
    ...     pass

    >>> class F2(object):
    ...     pass

    >>> def pre(container, name, object):
    ...     if not isinstance(object, F1):
    ...         raise zope.interface.Invalid()
    >>> def prefactory(container, name, factory):
    ...     if factory._callable is not F1:
    ...         raise zope.interface.Invalid()
    >>> pre.factory = prefactory


    >>> class IContainer(zope.interface.Interface):
    ...     def __setitem__(name, object):
    ...         pass
    ...     __setitem__.precondition = pre

    >>> @zope.interface.implementer(IContainer)
    ... class Container(object):
    ...     pass

    >>> from zope.component.factory import Factory
    >>> ztapi.provideUtility(IFactory, Factory(F1), 'f1')
    >>> ztapi.provideUtility(IFactory, Factory(F2), 'f2')

    >>> from zope.app.container.browser.adding import Adding
    >>> adding = Adding(Container(), TestRequest())
    >>> items = adding.addingInfo()
    >>> len(items)
    1

    isSingleMenuItem returns True if there is only one content class
    inside the Container

    >>> adding.isSingleMenuItem()
    True

    hasCustomAddView will return False as the content does not have
    a custom Add View

    >>> adding.hasCustomAddView()
    True

    """

def test_SingleMenuItem_and_NoCustomAddView_NonICNC():
    """

    This function checks the case where there is a single content object
    and there is non custom add view . Also the container does not
    implement IContainerNamesContainer

    >>> registerAddMenu()
    >>> defineMenuItem(AddMenu, None, '', 'item3', extra={'factory': ''})
    >>> class F1(object):
    ...     pass

    >>> class F2(object):
    ...     pass

    >>> def pre(container, name, object):
    ...     if not isinstance(object, F1):
    ...         raise zope.interface.Invalid()
    >>> def prefactory(container, name, factory):
    ...     if factory._callable is not F1:
    ...         raise zope.interface.Invalid()
    >>> pre.factory = prefactory


    >>> class IContainer(zope.interface.Interface):
    ...     def __setitem__(name, object):
    ...         pass
    ...     __setitem__.precondition = pre


    >>> @zope.interface.implementer(IContainer)
    ... class Container(object):
    ...     pass

    >>> from zope.component.factory import Factory
    >>> ztapi.provideUtility(IFactory, Factory(F1), 'f1')
    >>> ztapi.provideUtility(IFactory, Factory(F2), 'f2')

    >>> from zope.app.container.browser.adding import Adding
    >>> adding = Adding(Container(), TestRequest())
    >>> items = adding.addingInfo()
    >>> len(items)
    1

    The isSingleMenuItem will return True if there is one single content
    that can be added inside the Container

    >>> adding.isSingleMenuItem()
    True

    hasCustomAddView will return False as the content does not have
    a custom Add View

    >>> adding.hasCustomAddView()
    False

    """

def test_isSingleMenuItem_with_ICNC():
    """
    This test checks for whether there is a single content that can be added
    and the container uses IContainerNamesContaienr

    >>> registerAddMenu()
    >>> defineMenuItem(AddMenu, None, '', 'item3', extra={'factory': ''})

    >>> class F1(object):
    ...     pass

    >>> class F2(object):
    ...     pass

    >>> def pre(container, name, object):
    ...     if not isinstance(object, F1):
    ...         raise zope.interface.Invalid()
    >>> def prefactory(container, name, factory):
    ...     if factory._callable is not F1:
    ...         raise zope.interface.Invalid()
    >>> pre.factory = prefactory


    >>> class IContainer(zope.interface.Interface):
    ...     def __setitem__(name, object):
    ...         pass
    ...     __setitem__.precondition = pre


    >>> @zope.interface.implementer(IContainer, IContainerNamesContainer)
    ... class Container(object):
    ...     pass

    >>> from zope.app.container.browser.adding import Adding
    >>> adding = Adding(Container(), TestRequest())
    >>> items = adding.addingInfo()
    >>> len(items)
    1
    >>> adding.isSingleMenuItem()
    True
    >>> adding.hasCustomAddView()
    False

    """

from zope.testing import renormalizing
import re
checker = renormalizing.RENormalizing([
    (re.compile("u('.*?')"), r"\1"),
    (re.compile('u(".*?")'), r"\1"),
    # Python 3 adds module name to exceptions.
    (re.compile('zope.interface.exceptions.Invalid'), 'Invalid'),
])
def test_suite():
    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocTestSuite(setUp=setUp,
                             tearDown=tearDown,
                             checker=checker),
        ))
