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

$Id: placelesssetup.py,v 1.2 2003/06/05 12:41:55 stevea Exp $
"""
from zope.component.adapter import provideAdapter
from zope.app.container.zopecontainer import ZopeContainerDecorator
from zope.app.interfaces.context import IZopeContextWrapper
from zope.app.interfaces.container import IContainer

class PlacelessSetup:

    def setUp(self):
        provideAdapter(
            IContainer, IZopeContextWrapper, ZopeContainerDecorator)
