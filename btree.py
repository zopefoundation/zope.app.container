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
This module provides a sample container implementation.

This is primarily for testing purposes.

It might be useful as a mix-in for some classes, but many classes will
need a very different implementation.

Revision information:
$Id: btree.py,v 1.3 2002/12/30 20:43:49 jeremy Exp $
"""

from persistence import Persistent
from zodb.btrees.OOBTree import OOBTree
from zope.app.container.sample import SampleContainer

class BTreeContainer(SampleContainer, Persistent):

    __implements__ = SampleContainer.__implements__, Persistent.__implements__

    # XXX It appears that BTreeContainer uses SampleContainer only to
    # get the implementation of setObject().  All the other methods
    # provided by that base class are just slower replacements for
    # operations on the BTree itself.  It would probably be clearer to
    # just delegate those methods directly to the btree.

    def _newContainerData(self):
        """Construct an item-data container

        Subclasses should override this if they want different data.

        The value returned is a mapping object that also has get,
        has_key, keys, items, and values methods.
        """
        return OOBTree()
