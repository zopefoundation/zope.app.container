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

$Id: test_rename.py,v 1.1 2003/02/11 18:04:16 sidnei Exp $
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
from zope.app.interfaces.container import ICopySource
from zope.app.interfaces.container import IPasteNamesChooser
from zope.app.interfaces.container import IZopeContainer
from zope.app.container.copy import PasteTarget
from zope.app.container.copy import CopySource
from zope.app.container.copy import PasteNamesChooser
from zope.app.copy import ObjectMover
from zope.app.content.folder import Folder
from zope.app.content.file import File
from zope.app.container.zopecontainer \
     import ZopeContainerAdapter

class RenameTest(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)
        provideAdapter(None, IObjectMover, ObjectMover)
        provideAdapter(IContainer, IPasteTarget, PasteTarget)
        provideAdapter(IContainer, ICopySource, CopySource)
        provideAdapter(None, IObjectName, ObjectName)
        provideAdapter(IContainer, IPasteNamesChooser, PasteNamesChooser)
        provideAdapter(IContainer, IZopeContainer, ZopeContainerAdapter)
 
    def test_simplerename(self):
        root = self.rootFolder
        f1 = traverse(root, 'folder1')
        container = getAdapter(f1, IZopeContainer)
        container.rename('folder1', 'my_folder1')
        self.failIf('folder1' in container)
        self.failUnless('my_folder1' in container)

def test_suite():
    return TestSuite((
        makeSuite(RenameTest),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
