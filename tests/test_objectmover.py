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
$Id: test_objectmover.py,v 1.3 2003/02/17 15:10:40 sidnei Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.traversing import traverse
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.component import getAdapter
from zope.component.adapter import provideAdapter
from zope.app.traversing import IObjectName
from zope.app.traversing.adapters import ObjectName
from zope.app.interfaces.copypastemove import IObjectMover
from zope.app.interfaces.content.folder import IFolder
from zope.app.interfaces.container import IPasteTarget
from zope.app.interfaces.container import IMoveSource
from zope.app.interfaces.container import IPasteNamesChooser
from zope.app.container.copypastemove import PasteTarget
from zope.app.container.copypastemove import MoveSource
from zope.app.container.copypastemove import PasteNamesChooser
from zope.app.copypastemove import ObjectMover
from zope.app.content.folder import Folder
from zope.app.content.file import File

class ObjectMoverTest(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)
        provideAdapter(None, IObjectMover, ObjectMover)
        provideAdapter(IFolder, IPasteTarget, PasteTarget)
        provideAdapter(IFolder, IMoveSource, MoveSource)
        provideAdapter(None, IObjectName, ObjectName)
        provideAdapter(IFolder, IPasteNamesChooser, PasteNamesChooser)
 
    def test_movetosame(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container.setObject('file1', File())
        file = traverse(root, 'folder1/file1')
        mover = getAdapter(file, IObjectMover)
        mover.moveTo(container, 'file1')
        self.failUnless('file1' in container)

    def test_movetosamewithnewname(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container.setObject('file1', File())
        file = traverse(root, 'folder1/file1')
        mover = getAdapter(file, IObjectMover)
        mover.moveTo(container, 'file2')
        self.failIf('file1' in container)
        self.failUnless('file2' in container)

    def test_movetoother(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container.setObject('file1', File())
        target = traverse(root, 'folder2')
        file = traverse(root, 'folder1/file1')
        mover = getAdapter(file, IObjectMover)
        mover.moveTo(target, 'file1')
        self.failIf('file1' in container)
        self.failUnless('file1' in target)

    def test_movetootherwithnewname(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container.setObject('file1', File())
        target = traverse(root, 'folder2')
        file = traverse(root, 'folder1/file1')
        mover = getAdapter(file, IObjectMover)
        mover.moveTo(target, 'file2')
        self.failIf('file1' in container)
        self.failUnless('file2' in target)

    def test_movetootherwithnamecollision(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container.setObject('file1', File())
        target = traverse(root, 'folder2')
        target.setObject('file1', File())
        file = traverse(root, 'folder1/file1')
        mover = getAdapter(file, IObjectMover)
        mover.moveTo(target, 'file1')
        self.failIf('file1' in container)
        self.failUnless('file1' in target)
        self.failUnless('copy_of_file1' in target)

    def test_moveable(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container.setObject('file1', File())
        file = traverse(root, 'folder1/file1')
        mover = getAdapter(file, IObjectMover)
        self.failUnless(mover.moveable())

    def test_moveableTo(self):
        #  A file should be moveable to a folder that has an
        #  object with the same id.
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container.setObject('file1', File())
        file = traverse(root, 'folder1/file1')
        mover = getAdapter(file, IObjectMover)
        self.failUnless(mover.moveableTo(container, 'file1'))
        
def test_suite():
    return TestSuite((
        makeSuite(ObjectMoverTest),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
