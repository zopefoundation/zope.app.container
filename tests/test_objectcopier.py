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

$Id: test_objectcopier.py,v 1.7 2003/05/01 19:35:09 faassen Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.traversing import traverse
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.component import getAdapter, ComponentLookupError
from zope.component.adapter import provideAdapter
from zope.app.traversing import IObjectName
from zope.app.traversing.adapters import ObjectName
from zope.app.interfaces.copypastemove import IObjectCopier, INoChildrenObjectCopier
from zope.app.interfaces.content.folder import IFolder
from zope.app.interfaces.container import CopyException
from zope.app.interfaces.container import IContainer
from zope.app.interfaces.container import IPasteTarget
from zope.app.interfaces.container import ICopySource, INoChildrenCopySource
from zope.app.interfaces.container import IPasteNamesChooser
from zope.app.container.copypastemove import PasteTarget
from zope.app.container.copypastemove import CopySource, NoChildrenCopySource
from zope.app.container.copypastemove import PasteNamesChooser
from zope.app.copypastemove import ObjectCopier, NoChildrenObjectCopier
from zope.app.content.file import File
from zope.app.container.sample import SampleContainer

class ObjectCopierTest(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)
        provideAdapter(None, IObjectCopier, ObjectCopier)
        provideAdapter(IFolder, IPasteTarget, PasteTarget)
        provideAdapter(IFolder, ICopySource, CopySource)
        provideAdapter(None, IObjectName, ObjectName)
        provideAdapter(IFolder, IPasteNamesChooser, PasteNamesChooser)
 
    def test_copytosame(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container.setObject('file1', File())
        file = traverse(root, 'folder1/file1')
        copier = getAdapter(file, IObjectCopier)
        copier.copyTo(container, 'file1')
        self.failUnless('file1' in container)
        self.failUnless('copy_of_file1' in container)

    def test_copytosamewithnewname(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container.setObject('file1', File())
        file = traverse(root, 'folder1/file1')
        copier = getAdapter(file, IObjectCopier)
        copier.copyTo(container, 'file2')
        self.failUnless('file1' in container)
        self.failUnless('file2' in container)

    def test_copytoother(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container.setObject('file1', File())
        target = traverse(root, 'folder2')
        file = traverse(root, 'folder1/file1')
        copier = getAdapter(file, IObjectCopier)
        copier.copyTo(target, 'file1')
        self.failUnless('file1' in container)
        self.failUnless('file1' in target)

    def test_copytootherwithnewname(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container.setObject('file1', File())
        target = traverse(root, 'folder2')
        file = traverse(root, 'folder1/file1')
        copier = getAdapter(file, IObjectCopier)
        copier.copyTo(target, 'file2')
        self.failUnless('file1' in container)
        self.failUnless('file2' in target)

    def test_copytootherwithnamecollision(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container.setObject('file1', File())
        target = traverse(root, 'folder2')
        target.setObject('file1', File())
        file = traverse(root, 'folder1/file1')
        copier = getAdapter(file, IObjectCopier)
        copier.copyTo(target, 'file1')
        # we do it twice, just to test auto-name generation
        copier.copyTo(target, 'file1')
        self.failUnless('file1' in container)
        self.failUnless('file1' in target)
        self.failUnless('copy_of_file1' in target)
        self.failUnless('copy2_of_file1' in target)

    def test_copyable(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container.setObject('file1', File())
        file = traverse(root, 'folder1/file1')
        copier = getAdapter(file, IObjectCopier)
        self.failUnless(copier.copyable())

    def test_copyableTo(self):
        #  A file should be copyable to a folder that has an
        #  object with the same id.
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container.setObject('file1', File())
        file = traverse(root, 'folder1/file1')
        copier = getAdapter(file, IObjectCopier)
        self.failUnless(copier.copyableTo(container, 'file1'))
        
    def test_copyfoldertosibling(self):
        root = self.rootFolder
        target = traverse(root, '/folder2')
        source = traverse(root, '/folder1/folder1_1')
        copier = getAdapter(source, IObjectCopier)
        copier.copyTo(target)
        self.failUnless('folder1_1' in target)

    def test_copyfoldertosame(self):
        root = self.rootFolder
        target = traverse(root, '/folder1')
        source = traverse(root, '/folder1/folder1_1')
        copier = getAdapter(source, IObjectCopier)
        copier.copyTo(target)
        self.failUnless('folder1_1' in target)

    def test_copyfoldertosame2(self):
        root = self.rootFolder
        target = traverse(root, '/folder1/folder1_1')
        source = traverse(root, '/folder1/folder1_1/folder1_1_1')
        copier = getAdapter(source, IObjectCopier)
        copier.copyTo(target)
        self.failUnless('folder1_1_1' in target)

    def test_copyfolderfromroot(self):
        root = self.rootFolder
        target = traverse(root, '/folder2')
        source = traverse(root, '/folder1')
        copier = getAdapter(source, IObjectCopier)
        copier.copyTo(target)
        self.failUnless('folder1' in target)

    def test_copyfolderfromroot2(self):
        root = self.rootFolder
        target = traverse(root, '/folder2/folder2_1/folder2_1_1')
        source = traverse(root, '/folder1')
        copier = getAdapter(source, IObjectCopier)
        copier.copyTo(target)
        self.failUnless('folder1' in target)

class NoChildrenObjectCopierTest(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)
        provideAdapter(None, IObjectCopier, ObjectCopier)
        provideAdapter(IFolder, INoChildrenObjectCopier, NoChildrenObjectCopier)
        provideAdapter(IContainer, INoChildrenObjectCopier, NoChildrenObjectCopier)
        provideAdapter(IFolder, IPasteTarget, PasteTarget)
        provideAdapter(IFolder, ICopySource, CopySource)
        provideAdapter(IFolder, INoChildrenCopySource, NoChildrenCopySource)
        provideAdapter(IContainer, INoChildrenCopySource, NoChildrenCopySource)
        provideAdapter(None, IObjectName, ObjectName)
        provideAdapter(IFolder, IPasteNamesChooser, PasteNamesChooser)
 
    def test_copytosame(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        folder1 = traverse(root, 'folder1')
        copier = getAdapter(folder1, INoChildrenObjectCopier)
        copier.copyTo(container, 'new_folder1')
        new_folder1 = traverse(container, 'new_folder1')
        self.assertEquals(len(new_folder1.keys()), 0)

    def test_notavailforfile(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container.setObject('file1', File())
        file = traverse(root, 'folder1/file1')
        self.assertRaises(ComponentLookupError, getAdapter, file, INoChildrenObjectCopier)

    def test_copytoother(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        target = traverse(root, 'folder2')
        folder1_1 = traverse(root, 'folder1/folder1_1')
        copier = getAdapter(folder1_1, INoChildrenObjectCopier)
        copier.copyTo(target, 'folder1_1')
        new_folder1_1 = traverse(root, 'folder2/folder1_1')
        self.assertEquals(len(new_folder1_1.keys()), 0)

    def test_notavailforfile(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container.setObject('file1', File())
        file = traverse(root, 'folder1/file1')
        self.assertRaises(ComponentLookupError, getAdapter, file, INoChildrenObjectCopier)

    def test_doesntimplementclonewithoutchildren(self):
        root = self.rootFolder
        root.setObject('sample', SampleContainer())
        folder = traverse(root, 'sample')
        copier = getAdapter(folder, INoChildrenObjectCopier)
        self.assertRaises(CopyException, copier.copyTo, root, 'new_sample')

def test_suite():
    return TestSuite((
        makeSuite(ObjectCopierTest),
        makeSuite(NoChildrenObjectCopierTest),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')