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

$Id: test_containertraversable.py,v 1.3 2003/03/13 18:49:05 alga Exp $
"""

import unittest, sys
from zope.app.container.traversal import ContainerTraversable
from zope.exceptions import NotFoundError
from zope.app.interfaces.container import IContainer
from zope.testing.cleanup import CleanUp


class Container:

    __implements__ = IContainer

    def __init__(self, attrs={}, objs={}):
        for attr,value in attrs.iteritems():
            setattr(self, attr, value)

        self.__objs = {}
        for name,value in objs.iteritems():
            self.__objs[name] = value


    def __getitem__(self, name):
        return self.__objs[name]

    def get(self, name, default=None):
        return self.__objs.get(name, default)

    def __contains__(self, name):
        return self.__objs.has_key(name)


class Test(CleanUp, unittest.TestCase):
    def testAttr(self):
        # test container path traversal
        foo = Container()
        bar = Container()
        baz = Container()
        c   = Container({'foo': foo}, {'bar': bar, 'foo': baz})

        T = ContainerTraversable(c)
        self.failUnless(T.traverse('foo', (), 'foo', []) is baz)
        self.failUnless(T.traverse('bar', (), 'bar', []) is bar)

        self.assertRaises(NotFoundError , T.traverse,
                          'morebar', (), 'morebar', [])


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
