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
$Id: btree.py,v 1.6 2004/02/20 16:57:24 fdrake Exp $
"""

from persistent import Persistent
from zodb.btrees.OOBTree import OOBTree
from zope.app.container.sample import SampleContainer

class BTreeContainer(SampleContainer, Persistent):

    # implements(what my base classes implement)

    # XXX It appears that BTreeContainer uses SampleContainer only to
    # get the implementation of __setitem__().  All the other methods
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
