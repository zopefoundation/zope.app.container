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
$Id: test_icontainer.py,v 1.2 2002/12/25 14:12:47 jim Exp $
"""

from unittest import TestCase, main, makeSuite
from zope.app.interfaces.container import IContainer
from zope.interface.verify import verifyObject

class BaseTestIContainer:
    """Base test cases for containers.

    Subclasses need to define a method, '_Test__new', that
    takes no arguments and that returns a new empty test container.
    """

    def __setUp(self):
        self.__container = container = self._Test__new()
        for k,v in [('3', '0'), ('2', '1'), ('4', '2'), ('6', '3'), ('0', '4'),
                    ('5', '5'), ('1', '6'), ('8', '7'), ('7', '8'), ('9', '9')]:
            container.setObject(k, v)
        return container

    ############################################################
    # Interface-driven tests:

    def testIContainerVerify(self):
        verifyObject(IContainer, self._Test__new())

    def test_keys(self):
        # See interface IReadContainer
        container = self._Test__new()
        data = container.keys()
        self.assertEqual(list(data), [])

        container = self.__setUp()
        data = container.keys()
        # convert to sorted list
        data = list(data)
        data.sort()
        self.assertEqual(data, map(str, range(10)))

    def test_get(self):
        # See interface IReadContainer
        container = self._Test__new()
        self.assertRaises(KeyError, container.__getitem__, '1')
        self.assertEqual(container.get('1', '99'), '99')

        container = self.__setUp()
        self.assertRaises(KeyError, container.__getitem__, '100')
        self.assertEqual(container.get('100', '99'), '99')
        self.assertEqual(container.get('1', '99'), '6')
        self.assertEqual(container['7'], '8')
        self.assertEqual(container['0'], '4')
        self.assertEqual(container['9'], '9')

    def test_values(self):
        # See interface IReadContainer
        container = self._Test__new()
        data = container.values()
        self.assertEqual(list(data), [])

        container = self.__setUp()
        data = container.values()
        data = list(data); data.sort() # convert to sorted list
        self.assertEqual(data, map(str, range(10)))

    def test_len(self):
        # See interface IReadContainer
        container = self._Test__new()
        self.assertEqual(len(container), 0)

        container = self.__setUp()
        self.assertEqual(len(container), 10)

    def test_items(self):
        # See interface IReadContainer
        container = self._Test__new()
        data = container.items()
        self.assertEqual(list(data), [])

        container = self.__setUp()
        data = container.items()
        # convert to sorted list
        data = list(data)
        data.sort()
        self.assertEqual(data, [
            ('0', '4'), ('1', '6'), ('2', '1'), ('3', '0'), ('4', '2'),
            ('5', '5'), ('6', '3'), ('7', '8'), ('8', '7'), ('9', '9')
            ])

    def test___contains__(self):
        # See interface IReadContainer
        container = self._Test__new()
        self.assertEqual(not not ('1' in container), 0)

        container = self.__setUp()
        self.assertEqual(not not ('100' in container), 0)
        self.assertEqual(not not ('1' in container), 1)
        self.assertEqual(not not ('0' in container), 1)
        self.assertEqual(not not ('9' in container), 1)

    def test_delObject(self):
        # See interface IWriteContainer
        container = self._Test__new()
        self.assertRaises(KeyError, container.__delitem__, '1')

        container = self.__setUp()
        self.assertRaises(KeyError, container.__delitem__, '100')
        del container['1']
        del container['9']
        self.assertRaises(KeyError, container.__getitem__, '1')
        self.assertRaises(KeyError, container.__getitem__, '9')
        self.assertEqual(container.get('1', '99'), '99')
        self.assertEqual(container['7'], '8')
        self.assertEqual(container['0'], '4')
        self.assertEqual(container.get('9', '88'), '88')

    ############################################################
    # Tests from Folder

    def testEmpty(self):
        folder = self._Test__new()
        self.failIf(folder.keys())
        self.failIf(folder.values())
        self.failIf(folder.items())
        self.failIf(len(folder))
        self.failIf('foo' in folder)

        self.assertEquals(folder.get('foo', None), None)
        self.assertRaises(KeyError, folder.__getitem__, 'foo')

        self.assertRaises(KeyError, folder.__delitem__, 'foo')

    def testBadKeyTypes(self):
        folder = self._Test__new()
        value = []
        self.assertRaises(TypeError, folder.setObject, None, value)
        self.assertRaises(TypeError, folder.setObject, ['foo'], value)

    def testOneItem(self):
        folder = self._Test__new()
        foo = []
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

        foo2 = []
        folder.setObject('foo2', foo)

        self.assertEquals(len(folder.keys()), 2)
        self.assertEquals(folder.keys()[1], 'foo2')
        self.assertEquals(len(folder.values()), 2)
        self.assertEquals(folder.values()[1], foo2)
        self.assertEquals(len(folder.items()), 2)
        self.assertEquals(folder.items()[1], ('foo2', foo2))
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
        folder = self._Test__new()
        objects = [ [0], [1], [2], [3] ]
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
    def _Test__new(self):
        from zope.app.container.sample import SampleContainer
        return SampleContainer()

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
