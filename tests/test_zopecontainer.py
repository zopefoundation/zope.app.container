##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""ZopeContainerDecorator tests

$Id: test_zopecontainer.py,v 1.5 2003/08/17 06:06:24 philikon Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.interfaces.container import IAddNotifiable
from zope.app.interfaces.container import IDeleteNotifiable
from zope.app.container.sample import SampleContainer
from zope.app.container.tests.baseizopeitemcontainer import \
     BaseTestIZopeSimpleReadContainer, BaseTestIZopeReadContainer,\
     BaseTestIZopeWriteContainer
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.context import ContextAwareDescriptors
from zope.proxy import isProxy, getProxiedObject
from zope.interface import implements, directlyProvides, directlyProvidedBy
from zope.app.interfaces.container import IOptionalNamesContainer
from zope.app.interfaces.container import IContainerNamesContainer

class C:
    pass

class H:
    implements(IAddNotifiable, IDeleteNotifiable)
    notified = 0
    def beforeDeleteHook(self, object, container):
        self.notified -= 1
    def afterAddHook(self, object, container):
        self.notified += 1

class ItemContainer:
    "Container that implements only __getitem__ for reading."

    def __init__(self):
        self._d = {}

    def __getitem__(self, key):
        return self._d[key]

    def __setitem__(self, key, value):
        self._d[key] = value


class TestZopeItemContainerDecorator(PlacelessSetup,
                                     BaseTestIZopeSimpleReadContainer,
                                     TestCase):
    # Note that this test derives from BaseTestIZopeSimpleReadContainer.
    # This is because the ZopeItemContainerDecorator decorates IItemContainer,
    # and as well as providing context-awareness, it upgrades IItemContainer
    # to ISimpleReadContainer.

    def setUp(self):
        PlacelessSetup.setUp(self)
        self._container = ItemContainer()

    def decorate(self, container):
        from zope.app.container.zopecontainer import ZopeItemContainerDecorator
        return ZopeItemContainerDecorator(container)

    def _sampleMapping(self):
        container = self._container
        for k, v in self._sampleDict().items():
            container[k] = v
        return self.decorate(container)

    def _sampleContainer(self):
        return self._container

    _sample = {'Z': C(), 'O': C(),'P': C()}
    def _sampleDict(self):
        return self._sample

    def _absentKeys(self):
        return 'zc', 'ny'

class TestZopeSimpleReadContainerDecorator(TestZopeItemContainerDecorator,
                                           BaseTestIZopeSimpleReadContainer):

    def setUp(self):
        PlacelessSetup.setUp(self)
        self._container = {}

    def decorate(self, container):
        from zope.app.container.zopecontainer import \
            ZopeSimpleReadContainerDecorator
        return ZopeSimpleReadContainerDecorator(container)

class TestZopeReadContainerDecorator(TestZopeSimpleReadContainerDecorator,
                                     BaseTestIZopeReadContainer):

    def decorate(self, container):
        from zope.app.container.zopecontainer import \
            ZopeReadContainerDecorator
        return ZopeReadContainerDecorator(container)

class TestZopeItemWriteContainerDecorator(TestZopeItemContainerDecorator,
                                          BaseTestIZopeWriteContainer):
    # The ZopeItemWriteContainerDecorator depends on the container also being
    # an IItemContainer. It needs this to get values that are to be deleted
    # so they can be sent in events.
    # So, this unit test tests that the decorator implementation properly
    # decorates IZopeItemContainer and IZopeWriteContainer.

    def setUp(self):
        PlacelessSetup.setUp(self)
        self._container = SampleContainer()

    def _sampleMapping(self):
        container = self._container
        for k, v in self._sampleDict().items():
            container.setObject(k, v)
        return self.decorate(container)

    def decorate(self, container):
        from zope.app.container.zopecontainer import \
            ZopeItemWriteContainerDecorator
        return ZopeItemWriteContainerDecorator(container)

    __newItem = {'A': C(), 'B': C()}
    def _sample_newItem(self):
        return self.__newItem

    __newItemHooked = {'B': H(), 'E': H()}
    def _sample_newItemHooked(self):
        return self.__newItemHooked


class TestZopeContainerDecorator(TestZopeItemWriteContainerDecorator,
                                 TestZopeReadContainerDecorator):

    def decorate(self, container):
        from zope.app.container.zopecontainer import ZopeContainerDecorator
        return ZopeContainerDecorator(container)


class ContextAwareContainer(SampleContainer):
    '''A container that checks that its methods are context wrapped.
    '''

    ContextAwareDescriptors()

    def __getitem__(self, key):
        assert isProxy(self), "self is not wrapped"
        return super(ContextAwareContainer, getProxiedObject(self)).__getitem__(key)

    def __contains__(self, key):
        assert isProxy(self), "self is not wrapped"
        return super(ContextAwareContainer, getProxiedObject(self)).__contains__(key)

    def __delitem__(self, key):
        assert isProxy(self), "self is not wrapped"
        return super(ContextAwareContainer, getProxiedObject(self)).__delitem__(key)

    def get(self, key, default):
        assert isProxy(self), "self is not wrapped"
        return super(ContextAwareContainer, getProxiedObject(self)).get(key, default)

    def items(self):
        assert isProxy(self), "self is not wrapped"
        return super(ContextAwareContainer, getProxiedObject(self)).items()

    def values(self):
        assert isProxy(self), "self is not wrapped"
        return super(ContextAwareContainer, getProxiedObject(self)).values()

    def setObject(self, key, value):
        # XXX: setObject is called on a non-decorated container in the test fixtures
        # assert isProxy(self), "self is not wrapped"
        if key == '':
            key = str(id(value))
        return super(ContextAwareContainer, getProxiedObject(self)).setObject(key, value)


class TestZopeContainerDecoratorWrapper(TestZopeContainerDecorator):

    def setUp(self):
        TestZopeContainerDecorator.setUp(self)
        self._container = ContextAwareContainer()

    def test_setObject_optional_names(self):
        # Test that empty keys are allowed for containers which implement
        # IOptionalNamesContainer or IContainerNamesContainer
        container = ContextAwareContainer()
        directlyProvides(container, directlyProvidedBy(container),
                         IOptionalNamesContainer)
        decorated = self.decorate(container)
        decorated.setObject('', 'foo')

        container = ContextAwareContainer()
        directlyProvides(container, directlyProvidedBy(container),
                         IContainerNamesContainer)
        decorated = self.decorate(container)
        name = decorated.setObject('', 'foo')
        self.assert_(name != '')

        container = ContextAwareContainer()
        decorated = self.decorate(container)
        self.assertRaises(ValueError, decorated.setObject, '', 'foo')


def test_suite():
    return TestSuite((
        makeSuite(TestZopeItemContainerDecorator),
        makeSuite(TestZopeSimpleReadContainerDecorator),
        makeSuite(TestZopeReadContainerDecorator),
        makeSuite(TestZopeItemWriteContainerDecorator),
        makeSuite(TestZopeContainerDecorator),
        makeSuite(TestZopeContainerDecoratorWrapper),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
