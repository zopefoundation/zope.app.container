##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Unit test logic for setting up and tearing down basic infrastructure

$Id: placelesssetup.py,v 1.3 2003/09/21 17:31:39 jim Exp $
"""
from zope.component.adapter import provideAdapter
from zope.app.interfaces.container import IWriteContainer
from zope.app.interfaces.container import INameChooser
from zope.app.container.contained import NameChooser

class PlacelessSetup:

    def setUp(self):
        provideAdapter(IWriteContainer, INameChooser, NameChooser)
