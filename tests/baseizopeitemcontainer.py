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
"""

Revision information:
$Id: baseizopeitemcontainer.py,v 1.6 2003/07/16 17:02:59 alga Exp $
"""

from zope.context import getWrapperContainer, getWrapperData
from zope.interface.common.tests.basemapping \
     import BaseTestIReadMapping, BaseTestIEnumerableMapping
from zope.app.event.tests.placelesssetup import getEvents
from zope.app.interfaces.event \
     import IObjectRemovedEvent, IObjectModifiedEvent, IObjectAddedEvent


class BaseTestIZopeItemContainer:

    def _sampleMapping(self):
        """Return a new instance to be tested
        """
        raise TypeError('_sampleMapping was not implemented')

    def _sampleDict(self):
        """Return a sequence of items that should be in the container
        """
        raise TypeError('_sampleDict was not implemented')

    def _absentKeys(self):
        """This should return the keys not in the container
        """
        # XXX Is this supposed to be pseudocode? It doesn't make sense.
        absent_key = ''
        for key, value in testItems:
            absent_key += key
        return [absent_key]


    def test__getitem__(self):
        testOb = self._sampleMapping()
        testItems = self._sampleDict().items()
        testAd = self._sampleContainer()
        for key, value in testItems:
            stored = testOb[key]
            self.assertEqual(stored, value)
            self.assertEqual(getWrapperContainer(stored), testAd)

        for key in self._absentKeys():
            self.assertRaises(KeyError, testOb.__getitem__, key)


class BaseTestIZopeSimpleReadContainer(BaseTestIZopeItemContainer,
                                       BaseTestIReadMapping):

    def _IReadMapping__sample(self):
        return self._sampleMapping()

    def _IReadMapping__stateDict(self):
        return self._sampleDict()

    def _IReadMapping__absentKeys(self):
        return self._absentKeys()

    def test_zope_get(self):
        testOb = self._sampleMapping()
        testItems = self._sampleDict().items()
        testAd = self._sampleContainer()
        for key, value in testItems:
            stored = testOb.get(key)
            self.assertEqual(stored, value)
            self.assertEqual(getWrapperContainer(stored), testAd)
            self.assertEqual(getWrapperData(stored)['name'], key)


class BaseTestIZopeReadContainer(BaseTestIZopeItemContainer,
                                 BaseTestIEnumerableMapping):

    def _IEnumerableMapping__sample(self):
        return self._sampleMapping()

    def _IEnumerableMapping__stateDict(self):
        return self._sampleDict()

    def _IEnumerableMapping__absentKeys(self):
        return self._absentKeys()



    def test_zope_values(self):
        testOb = self._sampleMapping()
        data = testOb.values()
        testAd = self._sampleContainer()
        for value in data:
            self.assertEqual(getWrapperContainer(value), testAd)
            getWrapperData(value)['name']


    def test_zope_items(self):
        testOb = self._sampleMapping()
        testItems = self._sampleDict().items()
        testAd = self._sampleContainer()
        for key, value in testItems:
            stored = testOb[key]
            self.assertEqual(getWrapperData(stored)['name'], key)
            self.assertEqual(value, stored)
        self.assertEqual(testOb.items(), getWrapperContainer(stored).items())


class BaseTestIZopeWriteContainer(BaseTestIZopeItemContainer):

    def _sample_newItem(self):
        """Return a new item key and value for testing addition

        The new item must not have a IAddNotifiable adapter
        or a IDeleteNotifyable adapter.
        """
        raise TypeError("_sample_newItem was not implemented")

    def _sample_newItemHooked(self):
        """Return a new item key and value for testing addition

        The new item must implement IAddNotifiable
        and IDeleteNotifyable, and must have a notified attribute that
        is incremented when afterAddHook is called and decremented
        when beforeDeleteHook is called.
        """
        raise TypeError("_sample_newItem was not implemented")

    def test_zope_setObject(self):
        key, value = self._sample_newItem().items()[0]
        testOb = self._sampleMapping()
        testAd = self._sampleContainer()
        newkey = testOb.setObject(key, value)
        self.assertEqual(testOb[newkey], value)


        self.failUnless(
            [event
             for event in getEvents(IObjectAddedEvent)
             if event.object == value]
             )

        self.failUnless(
            [event
             for event in getEvents(IObjectModifiedEvent)
             if event.object == testAd]
             )

        key, value = self._sample_newItemHooked().items()[0]
        oldnotified = value.notified +1
        newkey = testOb.setObject(key, value)
        self.assertEqual(value.notified , oldnotified)

        self.failUnless(
            [event
             for event in getEvents(IObjectAddedEvent)
             if event.object == value]
             )

        self.failUnless(
            [event
             for event in getEvents(IObjectModifiedEvent)
             if event.object == testAd]
             )



    def test__zope_delitem__(self):
        testOb = self._sampleMapping()
        testObHook = self._sample_newItemHooked()
        testAd = self._sampleContainer()
        self.assertRaises(KeyError, testOb.__delitem__, 'zc')
        key, value = self._sample_newItem()
        newkey = testOb.setObject(key, value)
        del testOb[key]
        self.assertRaises(KeyError, testOb.__delitem__, key)



        self.failUnless(
            [event
             for event in getEvents(IObjectRemovedEvent)
             if event.object == value]
             )

        self.failUnless(
            [event
             for event in getEvents(IObjectModifiedEvent)
             if event.object == testAd]
             )

        key, value = self._sample_newItemHooked().items()[0]
        newkey = testOb.setObject(key, value)
        oldnotified = value.notified - 1
        del testOb[key]
        self.assertRaises(KeyError, testOb.__delitem__, key)

        self.assertEqual(value.notified , oldnotified)

        self.failUnless(
            [event
             for event in getEvents(IObjectRemovedEvent)
             if event.object == value]
             )

        self.failUnless(
            [event
             for event in getEvents(IObjectModifiedEvent)
             if event.object == testAd]
             )
