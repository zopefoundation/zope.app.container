##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""BTree Container Tests

$Id$
"""
from unittest import TestCase, main, makeSuite, TestSuite
from zope.interface.verify import verifyObject
from zope.testing.doctestunit import DocTestSuite
from zope.app.testing import placelesssetup
from test_icontainer import TestSampleContainer
from zope.app.container.btree import BTreeContainer
from zope.app.container.interfaces import IContainer

class TestBTreeContainer(TestSampleContainer, TestCase):

    def makeTestObject(self):
        return BTreeContainer()

class TestBTreeLength(TestCase):

    def testStoredLength(self):
        #This is lazy for backward compatibility. If the len is not
        #stored already we set it to the length of the underlying
        #btree.
        bc = BTreeContainer()
        self.assertEqual(bc.__dict__['_BTreeContainer__len'](), 0)
        del bc.__dict__['_BTreeContainer__len']
        self.failIf(bc.__dict__.has_key('_BTreeContainer__len'))
        bc['1'] = 1
        self.assertEqual(len(bc), 1)
        self.assertEqual(bc.__dict__['_BTreeContainer__len'](), 1)

    def testContainerInterface(self):
        bc = BTreeContainer()
        self.assert_(verifyObject(IContainer, bc))
        self.checkIterable(bc.items())
        self.checkIterable(bc.keys())
        self.checkIterable(bc.values())


    def testCorrectLengthWhenAddingExistingItem(self):
        """
        for bug #175388
        """
        bc = BTreeContainer()
        bc[u'x'] = object()
        self.assertEqual(len(bc), 1)
        bc[u'x'] = bc[u'x']
        self.assertEqual(len(bc), 1)
        self.assertEqual(list(bc), [u'x'])

    def checkIterable(self, iterable):
        it = iter(iterable)
        self.assert_(callable(it.next))
        self.assert_(callable(it.__iter__))
        self.assert_(iter(it) is it)
        # Exhaust the iterator:
        first_time = list(it)
        self.assertRaises(StopIteration, it.next)
        # Subsequent iterations will return the same values:
        self.assertEqual(list(iterable), first_time)
        self.assertEqual(list(iterable), first_time)



def test_suite():
    return TestSuite((
        makeSuite(TestBTreeContainer),
        makeSuite(TestBTreeLength),
        DocTestSuite('zope.app.container.btree',
                     setUp=placelesssetup.setUp,
                     tearDown=placelesssetup.tearDown),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
