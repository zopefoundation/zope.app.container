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
"""Test the IContainer interface.

$Id: test_icontainer.py,v 1.7 2004/03/03 10:38:39 philikon Exp $
"""

from unittest import TestCase, main, makeSuite
from zope.app.container.interfaces import IContainer
from zope.interface.verify import verifyObject
from zope.app.tests.placelesssetup import PlacelessSetup


def DefaultTestData():
        return [('3', '0'), ('2', '1'), ('4', '2'), ('6', '3'), ('0', '4'),
                ('5', '5'), ('1', '6'), ('8', '7'), ('7', '8'), ('9', '9')]

class BaseTestIContainer(PlacelessSetup):
    """Base test cases for containers.

    Subclasses must define a makeTestObject that takes no
    arguments and that returns a new empty test container,
    and a makeTestData that also takes no arguments and returns
    a sequence of (key, value) pairs that may be stored in
    the test container.  The list must be at least ten items long.
    'NoSuchKey' may not be used as a key value in the returned list.
    """

    def __setUp(self):
        self.__container = container = self.makeTestObject()
        self.__data = data = self.makeTestData()
        for k, v in data:
            container[k] = v
        return container, data

    ############################################################
    # Interface-driven tests:

    def testIContainerVerify(self):
        verifyObject(IContainer, self.makeTestObject())

    def test_keys(self):
        # See interface IReadContainer
        container = self.makeTestObject()
        keys = container.keys()
        self.assertEqual(list(keys), [])

        container, data = self.__setUp()
        keys = container.keys()
        keys = list(keys); keys.sort() # convert to sorted list
        ikeys = [ k for k, v in data ]; ikeys.sort() # sort input keys
        self.assertEqual(keys, ikeys)

    def test_get(self):
        # See interface IReadContainer
        default = object()
        data = self.makeTestData()
        container = self.makeTestObject()
        self.assertRaises(KeyError, container.__getitem__, data[0][0])
        self.assertEqual(container.get(data[0][0], default), default)

        container, data = self.__setUp()
        self.assertRaises(KeyError, container.__getitem__,
                          self.getUnknownKey())
        self.assertEqual(container.get(self.getUnknownKey(), default), default)
        for i in (1, 8, 7, 3, 4):
            self.assertEqual(container.get(data[i][0], default), data[i][1])
            self.assertEqual(container.get(data[i][0]), data[i][1])

    def test_values(self):
        # See interface IReadContainer
        container = self.makeTestObject()
        values = container.values()
        self.assertEqual(list(values), [])

        container, data = self.__setUp()
        values = container.values()
        # XXX: this assumes that sort produces a deterministic order for
        # the data returned by container.  This is valid for the data
        # in DefaultTestData, but it may not be valid for all IContainers.
        # Is there a better way to write this test?
        values = list(values); values.sort() # convert to sorted list
        ivalues = [ v for k, v in data ]; ivalues.sort() # sort original.
        self.assertEqual(values, ivalues)

    def test_len(self):
        # See interface IReadContainer
        container = self.makeTestObject()
        self.assertEqual(len(container), 0)

        container, data = self.__setUp()
        self.assertEqual(len(container), len(data))

    def test_items(self):
        # See interface IReadContainer
        container = self.makeTestObject()
        items = container.items()
        self.assertEqual(list(items), [])

        container, data = self.__setUp()
        items = container.items()
        items = list(items); items.sort() # convert to sorted list
        data.sort()                       # sort input data
        self.assertEqual(items, data)

    def test___contains__(self):
        # See interface IReadContainer
        container = self.makeTestObject()
        data = self.makeTestData()
        self.assertEqual(not not (data[6][0] in container), False)

        container, data = self.__setUp()
        self.assertEqual(not not (data[6][0] in container), True)
        for i in (1, 8, 7, 3, 4):
            self.assertEqual(not not (data[i][0] in container), 1)

    def test_delObject(self):
        # See interface IWriteContainer
        default = object()
        data = self.makeTestData()
        container = self.makeTestObject()
        self.assertRaises(KeyError, container.__delitem__, data[0][0])

        container, data = self.__setUp()
        self.assertRaises(KeyError, container.__delitem__,
                          self.getUnknownKey())
        for i in (1, 8, 7, 3, 4):
            del container[data[i][0]]
        for i in (1, 8, 7, 3, 4):
            self.assertRaises(KeyError, container.__getitem__, data[i][0])
            self.assertEqual(container.get(data[i][0], default), default)
        for i in (0, 2, 9, 6, 5):
            self.assertEqual(container[data[i][0]], data[i][1])

    ############################################################
    # Tests from Folder

    def testEmpty(self):
        folder = self.makeTestObject()
        data = self.makeTestData()
        self.failIf(folder.keys())
        self.failIf(folder.values())
        self.failIf(folder.items())
        self.failIf(len(folder))
        self.failIf(data[6][0] in folder)

        self.assertEquals(folder.get(data[6][0], None), None)
        self.assertRaises(KeyError, folder.__getitem__, data[6][0])

        self.assertRaises(KeyError, folder.__delitem__, data[6][0])

    def testBadKeyTypes(self):
        folder = self.makeTestObject()
        data = self.makeTestData()
        value = data[1][1]
        for name in self.getBadKeyTypes():
            self.assertRaises(TypeError, folder.__setitem__, name, value)

    def testOneItem(self):
        folder = self.makeTestObject()
        data = self.makeTestData()

        foo = data[0][1]
        folder['foo'] = foo
        name = 'foo'

        self.assertEquals(len(folder.keys()), 1)
        self.assertEquals(folder.keys()[0], 'foo')
        self.assertEquals(len(folder.values()), 1)
        self.assertEquals(folder.values()[0], foo)
        self.assertEquals(len(folder.items()), 1)
        self.assertEquals(folder.items()[0], ('foo', foo))
        self.assertEquals(len(folder), 1)

        self.failUnless('foo' in folder)
        # Use an arbitrary id frpm the data set; don;t just use any id, since
        # there might be restrictions on their form
        self.failIf(data[6][0] in folder)

        self.assertEquals(folder.get(name, None), foo)
        self.assertEquals(folder[name], foo)

        self.assertRaises(KeyError, folder.__getitem__, data[6][0])

        foo2 = data[1][1]
        
        name2 = 'foo2'
        folder[name2] = foo2

        self.assertEquals(len(folder.keys()), 2)
        self.assertEquals(not not name2 in folder.keys(), True)
        self.assertEquals(len(folder.values()), 2)
        self.assertEquals(not not foo2 in folder.values(), True)
        self.assertEquals(len(folder.items()), 2)
        self.assertEquals(not not (name2, foo2) in folder.items(), True)
        self.assertEquals(len(folder), 2)

        del folder[name]
        del folder[name2]

        self.failIf(folder.keys())
        self.failIf(folder.values())
        self.failIf(folder.items())
        self.failIf(len(folder))
        self.failIf(name in folder)

        self.assertRaises(KeyError, folder.__getitem__, name)
        self.assertEquals(folder.get(name, None), None)
        self.assertRaises(KeyError, folder.__delitem__, name)

    def testManyItems(self):
        folder = self.makeTestObject()
        data = self.makeTestData()
        objects = [ data[i][1] for i in range(4) ]
        name0 = 'foo'
        name1 = 'bar'
        name2 = 'baz'
        name3 = 'bam'
        folder['foo'] = objects[0]
        folder['bar'] = objects[1]
        folder['baz'] = objects[2]
        folder['bam'] = objects[3]

        self.assertEquals(len(folder.keys()), len(objects))
        self.failUnless(name0 in folder.keys())
        self.failUnless(name1 in folder.keys())
        self.failUnless(name2 in folder.keys())
        self.failUnless(name3 in folder.keys())

        self.assertEquals(len(folder.values()), len(objects))
        self.failUnless(objects[0] in folder.values())
        self.failUnless(objects[1] in folder.values())
        self.failUnless(objects[2] in folder.values())
        self.failUnless(objects[3] in folder.values())

        self.assertEquals(len(folder.items()), len(objects))
        self.failUnless((name0, objects[0]) in folder.items())
        self.failUnless((name1, objects[1]) in folder.items())
        self.failUnless((name2, objects[2]) in folder.items())
        self.failUnless((name3, objects[3]) in folder.items())

        self.assertEquals(len(folder), len(objects))

        self.failUnless(name0 in folder)
        self.failUnless(name1 in folder)
        self.failUnless(name2 in folder)
        self.failUnless(name3 in folder)
        self.failIf(data[5][0] in folder)

        self.assertEquals(folder.get(name0, None), objects[0])
        self.assertEquals(folder[name0], objects[0])
        self.assertEquals(folder.get(name1, None), objects[1])
        self.assertEquals(folder[name1], objects[1])
        self.assertEquals(folder.get(name2, None), objects[2])
        self.assertEquals(folder[name2], objects[2])
        self.assertEquals(folder.get(name3, None), objects[3])
        self.assertEquals(folder[name3], objects[3])

        self.assertEquals(folder.get(data[5][0], None), None)
        self.assertRaises(KeyError, folder.__getitem__, data[5][0])

        del folder[name0]
        self.assertEquals(len(folder), len(objects) - 1)
        self.failIf(name0 in folder)
        self.failIf(name0 in folder.keys())

        self.failIf(objects[0] in folder.values())
        self.failIf((name0, objects[0]) in folder.items())

        self.assertEquals(folder.get(name0, None), None)
        self.assertRaises(KeyError, folder.__getitem__, name0)

        self.assertRaises(KeyError, folder.__delitem__, name0)

        del folder[name1]
        del folder[name2]
        del folder[name3]

        self.failIf(folder.keys())
        self.failIf(folder.values())
        self.failIf(folder.items())
        self.failIf(len(folder))
        self.failIf(name0 in folder)
        self.failIf(name1 in folder)
        self.failIf(name2 in folder)
        self.failIf(name3 in folder)


class Test(BaseTestIContainer, TestCase):

    def makeTestObject(self):
        from zope.app.container.sample import SampleContainer
        return SampleContainer()

    def makeTestData(self):
        return DefaultTestData()

    def getUnknownKey(self):
        return '10'

    def getBadKeyTypes(self):
        return [None, ['foo'], 1, '\xf3abc']

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
