##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Object Mover Tests

$Id$
"""
from unittest import TestCase, TestSuite, main, makeSuite

from zope.app.traversing.api import traverse
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.tests import ztapi
from zope.app.copypastemove.interfaces import IObjectMover
from zope.app.copypastemove import ObjectMover

class File(object):
    pass

class ObjectMoverTest(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)
        ztapi.provideAdapter(None, IObjectMover, ObjectMover)
 
    def test_movetosame(self):
        # Should be a noop, because "moving" to same location
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        file = traverse(root, 'folder1/file1')
        mover = IObjectMover(file)
        mover.moveTo(container, 'file1')
        self.failUnless('file1' in container)
        self.assertEquals(len(container), 3)

    def test_movetosamewithnewname(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        file = traverse(root, 'folder1/file1')
        mover = IObjectMover(file)
        mover.moveTo(container, 'file2')
        self.failIf('file1' in container)
        self.failUnless('file2' in container)

    def test_movetoother(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        target = traverse(root, 'folder2')
        file = traverse(root, 'folder1/file1')
        mover = IObjectMover(file)
        mover.moveTo(target, 'file1')
        self.failIf('file1' in container)
        self.failUnless('file1' in target)

    def test_movetootherwithnewname(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        target = traverse(root, 'folder2')
        file = traverse(root, 'folder1/file1')
        mover = IObjectMover(file)
        mover.moveTo(target, 'file2')
        self.failIf('file1' in container)
        self.failUnless('file2' in target)

    def test_movetootherwithnamecollision(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        target = traverse(root, 'folder2')
        target['file1'] = File()
        file = traverse(root, 'folder1/file1')
        mover = IObjectMover(file)
        mover.moveTo(target, 'file1')
        self.failIf('file1' in container)
        self.failUnless('file1' in target)
        self.failUnless('file1-2' in target)

    def test_moveable(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        file = traverse(root, 'folder1/file1')
        mover = IObjectMover(file)
        self.failUnless(mover.moveable())

    def test_moveableTo(self):
        #  A file should be moveable to a folder that has an
        #  object with the same id.
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        file = traverse(root, 'folder1/file1')
        mover = IObjectMover(file)
        self.failUnless(mover.moveableTo(container, 'file1'))

    def test_movefoldertosibling(self):
        root = self.rootFolder
        target = traverse(root, '/folder2')
        source = traverse(root, '/folder1/folder1_1')
        mover = IObjectMover(source)
        mover.moveTo(target)
        self.failUnless('folder1_1' in target)

    def test_movefoldertosame(self):
        # Should be a noop, because "moving" to same location
        root = self.rootFolder
        target = traverse(root, '/folder1')
        source = traverse(root, '/folder1/folder1_1')
        mover = IObjectMover(source)
        mover.moveTo(target)
        self.failUnless('folder1_1' in target)
        self.assertEquals(len(target), 2)

    def test_movefoldertosame2(self):
        # Should be a noop, because "moving" to same location
        root = self.rootFolder
        target = traverse(root, '/folder1/folder1_1')
        source = traverse(root, '/folder1/folder1_1/folder1_1_1')
        mover = IObjectMover(source)
        mover.moveTo(target)
        self.failUnless('folder1_1_1' in target)
        self.assertEquals(len(target), 2)

    def test_movefolderfromroot(self):
        root = self.rootFolder
        target = traverse(root, '/folder2')
        source = traverse(root, '/folder1')
        mover = IObjectMover(source)
        mover.moveTo(target)
        self.failUnless('folder1' in target)

    def test_movefolderfromroot2(self):
        root = self.rootFolder
        target = traverse(root, '/folder2/folder2_1/folder2_1_1')
        source = traverse(root, '/folder1')
        mover = IObjectMover(source)
        mover.moveTo(target)
        self.failUnless('folder1' in target)

        
def test_suite():
    return TestSuite((
        makeSuite(ObjectMoverTest),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
