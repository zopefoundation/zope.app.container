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
"""Object Copier Tests

$Id$
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.traversing.api import traverse
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.tests import ztapi
from zope.app.copypastemove.interfaces import IObjectCopier
from zope.app.copypastemove import ObjectCopier

class File(object):
    pass

class ObjectCopierTest(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)
        ztapi.provideAdapter(None, IObjectCopier, ObjectCopier)

    def test_copytosame(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        file = traverse(root, 'folder1/file1')
        copier = IObjectCopier(file)
        copier.copyTo(container, 'file1')
        self.failUnless('file1' in container)
        self.failUnless('file1-2' in container)

    def test_copytosamewithnewname(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        file = traverse(root, 'folder1/file1')
        copier = IObjectCopier(file)
        copier.copyTo(container, 'file2')
        self.failUnless('file1' in container)
        self.failUnless('file2' in container)

    def test_copytoother(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        target = traverse(root, 'folder2')
        file = traverse(root, 'folder1/file1')
        copier = IObjectCopier(file)
        copier.copyTo(target, 'file1')
        self.failUnless('file1' in container)
        self.failUnless('file1' in target)

    def test_copytootherwithnewname(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        target = traverse(root, 'folder2')
        file = traverse(root, 'folder1/file1')
        copier = IObjectCopier(file)
        copier.copyTo(target, 'file2')
        self.failUnless('file1' in container)
        self.failUnless('file2' in target)

    def test_copytootherwithnamecollision(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        target = traverse(root, 'folder2')
        target['file1'] = File()
        file = traverse(root, 'folder1/file1')
        copier = IObjectCopier(file)
        copier.copyTo(target, 'file1')
        # we do it twice, just to test auto-name generation
        copier.copyTo(target, 'file1')
        self.failUnless('file1' in container)
        self.failUnless('file1' in target)
        self.failUnless('file1-2' in target)
        self.failUnless('file1-3' in target)

    def test_copyable(self):
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        file = traverse(root, 'folder1/file1')
        copier = IObjectCopier(file)
        self.failUnless(copier.copyable())

    def test_copyableTo(self):
        #  A file should be copyable to a folder that has an
        #  object with the same id.
        root = self.rootFolder
        container = traverse(root, 'folder1')
        container['file1'] = File()
        file = traverse(root, 'folder1/file1')
        copier = IObjectCopier(file)
        self.failUnless(copier.copyableTo(container, 'file1'))
        
    def test_copyfoldertosibling(self):
        root = self.rootFolder
        target = traverse(root, '/folder2')
        source = traverse(root, '/folder1/folder1_1')
        copier = IObjectCopier(source)
        copier.copyTo(target)
        self.failUnless('folder1_1' in target)

    def test_copyfoldertosame(self):
        root = self.rootFolder
        target = traverse(root, '/folder1')
        source = traverse(root, '/folder1/folder1_1')
        copier = IObjectCopier(source)
        copier.copyTo(target)
        self.failUnless('folder1_1' in target)

    def test_copyfoldertosame2(self):
        root = self.rootFolder
        target = traverse(root, '/folder1/folder1_1')
        source = traverse(root, '/folder1/folder1_1/folder1_1_1')
        copier = IObjectCopier(source)
        copier.copyTo(target)
        self.failUnless('folder1_1_1' in target)

    def test_copyfolderfromroot(self):
        root = self.rootFolder
        target = traverse(root, '/folder2')
        source = traverse(root, '/folder1')
        copier = IObjectCopier(source)
        copier.copyTo(target)
        self.failUnless('folder1' in target)

    def test_copyfolderfromroot2(self):
        root = self.rootFolder
        target = traverse(root, '/folder2/folder2_1/folder2_1_1')
        source = traverse(root, '/folder1')
        copier = IObjectCopier(source)
        copier.copyTo(target)
        self.failUnless('folder1' in target)

def test_suite():
    return TestSuite((
        makeSuite(ObjectCopierTest),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
