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

$Id: test_rename.py,v 1.2 2003/02/11 19:53:36 sidnei Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.traversing import traverse
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.component import getAdapter
from zope.component.adapter import provideAdapter
from zope.app.traversing import IObjectName
from zope.app.traversing.adapters import ObjectName
from zope.app.interfaces.copy import IObjectMover
from zope.app.interfaces.container import IContainer
from zope.app.interfaces.container import IPasteTarget
from zope.app.interfaces.container import IMoveSource
from zope.app.interfaces.container import IPasteNamesChooser
from zope.app.interfaces.container import IZopeContainer
from zope.app.container.copy import PasteTarget
from zope.app.container.copy import MoveSource
from zope.app.container.copy import PasteNamesChooser
from zope.app.copy import ObjectMover
from zope.app.content.folder import Folder
from zope.app.content.file import File
from zope.exceptions import NotFoundError, DuplicationError
from zope.app.container.zopecontainer \
     import ZopeContainerAdapter

class RenameTest(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)
        provideAdapter(None, IObjectMover, ObjectMover)
        provideAdapter(IContainer, IPasteTarget, PasteTarget)
        provideAdapter(IContainer, IMoveSource, MoveSource)
        provideAdapter(None, IObjectName, ObjectName)
        provideAdapter(IContainer, IPasteNamesChooser, PasteNamesChooser)
        provideAdapter(IContainer, IZopeContainer, ZopeContainerAdapter)
 
    def test_simplerename(self):
        root = self.rootFolder
        folder1 = traverse(root, 'folder1')
        self.failIf('file1' in folder1)
        folder1.setObject('file1', File())
        container = getAdapter(folder1, IZopeContainer)
        container.rename('file1', 'my_file1')
        self.failIf('file1' in container)
        self.failUnless('my_file1' in container)


    def test_renamenonexisting(self):
        root = self.rootFolder
        folder1 = traverse(root, 'folder1')
        self.failIf('a_test_file' in folder1)
        container = getAdapter(folder1, IZopeContainer)
        self.assertRaises(NotFoundError, container.rename, \
                          'file1', 'my_file1')


    def test_renamesamename(self):
        root = self.rootFolder
        folder1 = traverse(root, 'folder1')
        self.failIf('file1' in folder1)
        self.failIf('file2' in folder1)
        folder1.setObject('file1', File())
        folder1.setObject('file2', File())
        container = getAdapter(folder1, IZopeContainer)
        self.assertRaises(DuplicationError, container.rename, \
                          'file1', 'file2')

def test_suite():
    return TestSuite((
        makeSuite(RenameTest),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
