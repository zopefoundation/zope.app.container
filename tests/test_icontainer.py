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
$Id: test_icontainer.py,v 1.4 2002/12/27 18:36:28 rdmurray Exp $
"""

from unittest import TestCase, main, makeSuite
from zope.app.interfaces.container import IContainer
from zope.interface.verify import verifyObject


def DefaultTestData():
        return [('3', '0'), ('2', '1'), ('4', '2'), ('6', '3'), ('0', '4'),
                ('5', '5'), ('1', '6'), ('8', '7'), ('7', '8'), ('9', '9')]

class BaseTestIContainer:
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
            container.setObject(k, v)
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
        container = self.makeTestObject()
        self.assertRaises(KeyError, container.__getitem__, '1')
        self.assertEqual(container.get('1', default), default)

        container, data = self.__setUp()
        self.assertRaises(KeyError, container.__getitem__, 'NoSuchKey')
        self.assertEqual(container.get('NoSuchKey', default), default)
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
        self.assertEqual(not not ('1' in container), 0)

        container, data = self.__setUp()
        self.assertEqual(not not ('NoSuchKey' in container), 0)
        for i in (1, 8, 7, 3, 4):
            self.assertEqual(not not (data[i][0] in container), 1)

    def test_delObject(self):
        # See interface IWriteContainer
        default = object()
        container = self.makeTestObject()
        self.assertRaises(KeyError, container.__delitem__, '1')

        container, data = self.__setUp()
        self.assertRaises(KeyError, container.__delitem__, 'NoSuchKey')
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
        self.failIf(folder.keys())
        self.failIf(folder.values())
        self.failIf(folder.items())
        self.failIf(len(folder))
        self.failIf('foo' in folder)

        self.assertEquals(folder.get('foo', None), None)
        self.assertRaises(KeyError, folder.__getitem__, 'foo')

        self.assertRaises(KeyError, folder.__delitem__, 'foo')

    def testBadKeyTypes(self):
        folder = self.makeTestObject()
        value = []
        self.assertRaises(TypeError, folder.setObject, None, value)
        self.assertRaises(TypeError, folder.setObject, ['foo'], value)
        self.assertRaises(TypeError, folder.setObject, 1, value)
        self.assertRaises(TypeError, folder.setObject, '\xf3abc', value)

    def testOneItem(self):
        folder = self.makeTestObject()
        data = self.makeTestData()

        foo = data[0][1]
        folder.setObject('foo', foo)

        self.assertEquals(len(folder.keys()), 1)
        self.assertEquals(folder.keys()[0], 'foo')
        self.assertEquals(len(folder.values()), 1)
        self.assertEquals(folder.values()[0], foo)
        self.assertEquals(len(folder.items()), 1)
        self.assertEquals(folder.items()[0], ('foo', foo))
        self.assertEquals(len(folder), 1)

        self.failUnless('foo' in folder)
        self.failIf('bar' in folder)

        self.assertEquals(folder.get('foo', None), foo)
        self.assertEquals(folder['foo'], foo)

        self.assertRaises(KeyError, folder.__getitem__, 'qux')

        foo2 = data[1][1]
        folder.setObject('foo2', foo2)

        self.assertEquals(len(folder.keys()), 2)
        self.assertEquals(not not 'foo2' in folder.keys(), True)
        self.assertEquals(len(folder.values()), 2)
        self.assertEquals(not not foo2 in folder.values(), True)
        self.assertEquals(len(folder.items()), 2)
        self.assertEquals(not not ('foo2', foo2) in folder.items(), True)
        self.assertEquals(len(folder), 2)

        del folder['foo']
        del folder['foo2']

        self.failIf(folder.keys())
        self.failIf(folder.values())
        self.failIf(folder.items())
        self.failIf(len(folder))
        self.failIf('foo' in folder)

        self.assertRaises(KeyError, folder.__getitem__, 'foo')
        self.assertEquals(folder.get('foo', None), None)
        self.assertRaises(KeyError, folder.__delitem__, 'foo')

    def testManyItems(self):
        folder = self.makeTestObject()
        data = self.makeTestData()
        objects = [ data[i][1] for i in range(4) ]
        folder.setObject('foo', objects[0])
        folder.setObject('bar', objects[1])
        folder.setObject('baz', objects[2])
        folder.setObject('bam', objects[3])

        self.assertEquals(len(folder.keys()), len(objects))
        self.failUnless('foo' in folder.keys())
        self.failUnless('bar' in folder.keys())
        self.failUnless('baz' in folder.keys())
        self.failUnless('bam' in folder.keys())

        self.assertEquals(len(folder.values()), len(objects))
        self.failUnless(objects[0] in folder.values())
        self.failUnless(objects[1] in folder.values())
        self.failUnless(objects[2] in folder.values())
        self.failUnless(objects[3] in folder.values())

        self.assertEquals(len(folder.items()), len(objects))
        self.failUnless(('foo', objects[0]) in folder.items())
        self.failUnless(('bar', objects[1]) in folder.items())
        self.failUnless(('baz', objects[2]) in folder.items())
        self.failUnless(('bam', objects[3]) in folder.items())

        self.assertEquals(len(folder), len(objects))

        self.failUnless('foo' in folder)
        self.failUnless('bar' in folder)
        self.failUnless('baz' in folder)
        self.failUnless('bam' in folder)
        self.failIf('qux' in folder)

        self.assertEquals(folder.get('foo', None), objects[0])
        self.assertEquals(folder['foo'], objects[0])
        self.assertEquals(folder.get('bar', None), objects[1])
        self.assertEquals(folder['bar'], objects[1])
        self.assertEquals(folder.get('baz', None), objects[2])
        self.assertEquals(folder['baz'], objects[2])
        self.assertEquals(folder.get('bam', None), objects[3])
        self.assertEquals(folder['bam'], objects[3])

        self.assertEquals(folder.get('qux', None), None)
        self.assertRaises(KeyError, folder.__getitem__, 'qux')

        del folder['foo']
        self.assertEquals(len(folder), len(objects) - 1)
        self.failIf('foo' in folder)
        self.failIf('foo' in folder.keys())

        self.failIf(objects[0] in folder.values())
        self.failIf(('foo', objects[0]) in folder.items())

        self.assertEquals(folder.get('foo', None), None)
        self.assertRaises(KeyError, folder.__getitem__, 'foo')

        self.assertRaises(KeyError, folder.__delitem__, 'foo')

        del folder['bar']
        del folder['baz']
        del folder['bam']

        self.failIf(folder.keys())
        self.failIf(folder.values())
        self.failIf(folder.items())
        self.failIf(len(folder))
        self.failIf('foo' in folder)
        self.failIf('bar' in folder)
        self.failIf('baz' in folder)
        self.failIf('bam' in folder)


class Test(BaseTestIContainer, TestCase):

    def makeTestObject(self):
        from zope.app.container.sample import SampleContainer
        return SampleContainer()

    def makeTestData(self):
        return DefaultTestData()


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
