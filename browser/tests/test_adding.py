##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Adding implementation tests

$Id: test_adding.py,v 1.4 2004/03/19 20:26:24 srichter Exp $
"""
import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.app import zapi
from zope.app.tests import ztapi
from zope.app.traversing.browser import AbsoluteURL
from zope.app.container.browser.adding import Adding
from zope.app.container.interfaces import IAdding
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.exception.interfaces import UserError
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.tests.placelesssetup import PlacelessSetup, setUp, tearDown
from zope.component.interfaces import IFactory
from zope.component.exceptions import ComponentLookupError
from zope.interface import implements, Interface, directlyProvides
from zope.publisher.browser import TestRequest
from zope.app.publisher.browser import BrowserView
from zope.app.container.contained import contained
import zope.security.checker
from zope.exceptions import ForbiddenAttribute
from zope.app.container.interfaces import IWriteContainer
from zope.app.container.interfaces import IContainerNamesContainer
import zope.interface
from zope.app.container.interfaces import INameChooser
from zope.app.container.interfaces import IContainer

class Root:
    implements(IContainmentRoot)

class Container(dict):
    implements(IWriteContainer)

class CreationView(BrowserView):

    def action(self):
        return 'been there, done that'


class Content:
    pass

class Factory:

    implements(IFactory)

    title = ''
    description = ''

    def getInterfaces(self):
        return ()

    def __call__(self):
        return Content()


class AbsoluteURL(BrowserView):

    def __str__(self):
        if IContainmentRoot.providedBy(self.context):
            return ''
        name = self.context.__name__
        url = str(zapi.getView(
            zapi.getParent(self.context), 'absolute_url', self.request))
        url += '/' + name
        return url


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
        adding.namesAccepted = lambda: True

        # we can't use a private factory:
        self.assertRaises(ForbiddenAttribute, 
                          adding.action, type_name='fooprivate', id='bar')

        # typical add - id is provided by user
        adding.action(type_name='foo', id='bar')
        self.assert_('bar' in container)

        # missing type_name
        self.assertRaises(UserError, adding.action, id='bar')

        # missing id
        self.assertRaises(UserError, adding.action, type_name='foo')

        # bad type_name
        self.assertRaises(ComponentLookupError, adding.action, 
            type_name='***', id='bar')

        # alternative add - id is provided internally instead of from user
        adding.namesAccepted = lambda: False
        adding.contentName = 'baz'
        adding.action(type_name='foo')
        self.assert_('baz' in container)

        # alternative add w/missing contentName
        # Note: Passing is None as object name might be okay, if the container
        #       is able to hand out ids itself. Let's not require a content
        #       name to be specified!
        # For the container, (or really, the chooser, to choose, we have to
        # marke the container as a ContainerNamesContainer
        directlyProvides(container, IContainerNamesContainer)
        adding.contentName = None
        adding.action(type_name='foo')
        self.assert_('Content' in container)
        

    def test_action(self):
        container = Container()
        container = contained(container, Root(), "container")
        request = TestRequest()
        adding = Adding(container, request)
        adding.__name__ = '+'
        ztapi.browserView(IAdding, "Thing", CreationView)
        ztapi.browserView(Interface, "absolute_url", AbsoluteURL)
        self.assertRaises(UserError, adding.action, '', 'foo')
        adding.action('Thing', 'foo')
        self.assertEqual(adding.request.response._headers['location'],
                         '/container/+/Thing=foo')
        adding.action('Thing/screen1', 'foo')
        self.assertEqual(adding.request.response._headers['location'],
                         '/container/+/Thing/screen1=foo')



def test_constraint_driven_adding():
    """
    >>> setUp()
    >>> serviceService = zapi.getService(None, zapi.servicenames.Services)
    >>> from zope.app.publisher.interfaces.browser import IBrowserMenuService
    >>> serviceService.defineService(zapi.servicenames.BrowserMenu,
    ...                              IBrowserMenuService)
    >>> from zope.app.publisher.browser.globalbrowsermenuservice """ \
                             """import globalBrowserMenuService
    >>> serviceService.provideService(zapi.servicenames.BrowserMenu,
    ...                               globalBrowserMenuService)

    >>> menuService = zapi.getService(None, zapi.servicenames.BrowserMenu)
    >>> menuService.menu('test', '')
    >>> menuService.menuItem('test', IAdding, '', 'item1', None)
    >>> menuService.menuItem('test', IAdding, '', 'item2', None)
    >>> menuService.menu('zope.app.container.add', '')
    >>> menuService.menuItem('zope.app.container.add', IAdding, '', 'item3',
    ...                      None, extra={'factory': 'f1'})
    >>> menuService.menuItem('zope.app.container.add', IAdding, '', 'item4',
    ...                      None, extra={'factory': 'f2'})

    >>> class F1:
    ...     pass

    >>> class F2:
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


    >>> class Container:
    ...     zope.interface.implements(IContainer)

    >>> from zope.component.factory import Factory
    >>> ztapi.provideUtility(IFactory, Factory(F1), 'f1')
    >>> ztapi.provideUtility(IFactory, Factory(F2), 'f2')

    >>> from zope.app.container.browser.adding import Adding
    >>> adding = Adding(Container(), TestRequest())
    >>> items = adding.addingInfo()
    >>> len(items)
    1
    >>> items[0]['title']
    'item3'
    
    >>> adding.menu_id = 'test'
    >>> items = adding.addingInfo()
    >>> len(items)
    3
    >>> items[0]['title']
    'item1'
    >>> items[1]['title']
    'item2'
    >>> items[2]['title']
    'item3'
    >>> tearDown()    
    """

def test_renderAddButton():
    """
    Test for renderAddButton in adding.py 
    
    >>> setUp()
    >>> from zope.app.container.browser.adding import Adding
    >>> from zope.app.container.interfaces import IContainerNamesContainer

    Class implements IContainerNamesContainer
    
    >>> class FakeContainer:
    ...    zope.interface.implements(IContainerNamesContainer)

    renderAddButton returns only 'Add' button if the class imlement
    IContainerNamesContainer
    
    >>> adding = Adding(FakeContainer(),TestRequest())
    >>> adding.renderAddButton()
    u" <input type='submit' name='UPDATE_SUBMIT' value='Add'>"

    Fake class without IContainerNamesContainer
    
    >>> class Fake:
    ...    pass

    renderAddButton returns only 'Add' and 'inputbox' if the class
    doest imlement IContainerNamesContainer

    >>> adding = Adding(Fake(),TestRequest())
    >>> adding.renderAddButton()
    u"&nbsp;&nbsp;<input type='submit' name='UPDATE_SUBMIT' value='Add'>&nbsp;&nbsp;<b>Object Name:</b>&nbsp;<input type='text' name='add_input_name' value=''>"
    >>> adding.contentName='myname'
    >>> adding.renderAddButton()
    u"&nbsp;&nbsp;<input type='submit' name='UPDATE_SUBMIT' value='Add'>&nbsp;&nbsp;<b>Object Name:</b>&nbsp;<input type='text' name='add_input_name' value='myname'>"
    >>> adding = Adding(Fake(),TestRequest())     

    To check request variable

    >>> from zope.app.container.interfaces import IContainer
    >>> from zope.app.publisher.browser import BrowserView

    >>> class MyContainer:
    ...    zope.interface.implements(INameChooser, IContainer)
    ...    def chooseName(self, name, object):
    ...        return "foo"
    ...    def checkName(self, name, object):
    ...        return "foo"
    ...    def __setitem__(self, name, object):
    ...        setattr(self, name, object)
    ...        self.name=name
    ...    def __getitem__(self, key):
    ...        return self

    >>> request = TestRequest()
    >>> request.form.update({'add_input_name': 'reqname'})
    >>> mycontainer = MyContainer()
    >>> adding = Adding(mycontainer, request)
    >>> o = object()
    >>> add_obj = adding.add(o)
    >>> add_obj.name
    'reqname'
    >>> mycontainer.reqname is o
    True
    >>> tearDown()

    """

def test_chooseName():
    """If user don't enter name, pick one
    
    >>> class MyContainer:
    ...    zope.interface.implements(INameChooser, IContainer)
    ...    def chooseName(self, name, object):
    ...        return 'pickone'
    ...    def checkName(self, name, object):
    ...        pass
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
    """
    


def test_SingleMenuItem_and_CustomAddView_NonICNC():
    """
    This tests the condition if the content has Custom Add views and
    the container contains only a single content object
    
    >>> setUp()
    >>> serviceService = zapi.getService(None, zapi.servicenames.Services)
    >>> from zope.app.publisher.interfaces.browser import IBrowserMenuService
    >>> serviceService.defineService(zapi.servicenames.BrowserMenu,
    ...                              IBrowserMenuService)
    >>> from zope.app.publisher.browser.globalbrowsermenuservice """ \
                             """import globalBrowserMenuService
    >>> serviceService.provideService(zapi.servicenames.BrowserMenu,
    ...                               globalBrowserMenuService)

    >>> menuService = zapi.getService(None, zapi.servicenames.BrowserMenu)
    >>> menuService.menu('zope.app.container.add', '')
    >>> menuService.menuItem('zope.app.container.add', IAdding, '', 'item3',
    ...                      None, extra={'factory': 'f1'})

    >>> class F1:
    ...     pass

    >>> class F2:
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


    >>> class Container:
    ...     zope.interface.implements(IContainer)

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
    
    >>> tearDown()    
    """

def test_SingleMenuItem_and_NoCustomAddView_NonICNC():
    """
    
    This function checks the case where there is a single content object
    and there is non custom add view . Also the container does not
    implement IContainerNamesContainer
    
    >>> setUp()
    >>> serviceService = zapi.getService(None, zapi.servicenames.Services)
    >>> from zope.app.publisher.interfaces.browser import IBrowserMenuService
    >>> serviceService.defineService(zapi.servicenames.BrowserMenu,
    ...                              IBrowserMenuService)
    >>> from zope.app.publisher.browser.globalbrowsermenuservice """ \
                             """import globalBrowserMenuService
    >>> serviceService.provideService(zapi.servicenames.BrowserMenu,
    ...                               globalBrowserMenuService)

    >>> menuService = zapi.getService(None, zapi.servicenames.BrowserMenu)
    >>> menuService.menu('zope.app.container.add', '')
    >>> menuService.menuItem('zope.app.container.add', None, '', 'item3',
    ...                      None, extra={'factory': ''})
    >>> class F1:
    ...     pass

    >>> class F2:
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


    >>> class Container:
    ...     zope.interface.implements(IContainer)

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
    
    >>> tearDown()
    """

def test_isSingleMenuItem_with_ICNC():
    """
    This test checks for whether there is a single content that can be added
    and the container uses IContainerNamesContaienr

    
    >>> setUp()
    >>> serviceService = zapi.getService(None, zapi.servicenames.Services)
    >>> from zope.app.publisher.interfaces.browser import IBrowserMenuService
    >>> serviceService.defineService(zapi.servicenames.BrowserMenu,
    ...                              IBrowserMenuService)
    >>> from zope.app.publisher.browser.globalbrowsermenuservice \
                      import globalBrowserMenuService
    >>> serviceService.provideService(zapi.servicenames.BrowserMenu,
    ...                               globalBrowserMenuService)
    
    >>> menuService = zapi.getService(None, zapi.servicenames.BrowserMenu)
    >>> menuService.menu('zope.app.container.add', '')
    >>> menuService.menuItem('zope.app.container.add', None, '', 'item3',
    ...                      None, extra={'factory': ''})
    
    >>> class F1:
    ...     pass

    >>> class F2:
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


    >>> class Container:
    ...     zope.interface.implements(IContainer, IContainerNamesContainer)

    >>> from zope.app.container.browser.adding import Adding
    >>> adding = Adding(Container(), TestRequest())
    >>> items = adding.addingInfo()
    >>> len(items)
    1
    >>> adding.isSingleMenuItem()
    True
    >>> adding.hasCustomAddView()
    False
    
    >>> tearDown()
    
    """

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        DocTestSuite(),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')

