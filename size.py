
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
"""Adapters that give the size of an object.

$Id: size.py,v 1.1 2002/12/27 18:22:58 stevea Exp $
"""

from zope.app.interfaces.size import ISized

__metaclass__ = type

class ContainerSized:

    __implements__ = ISized
    
    def __init__(self, container):
        self._container = container

    def sizeForSorting(self):
        """See ISized"""
        return ('item', len(self._container))
        
    def sizeForDisplay(self):
        """See ISized"""
        num_items = len(self._container)
        if num_items == 1:
            return '1 item'
        return '%s items' % num_items
