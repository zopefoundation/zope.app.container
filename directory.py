##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""File-system representation adapters for containers

This module includes two adapters (adapter factories, really) for
providing a file-system representation for containers:

noop
  Factory that "adapts" IContainer to IWriteDirectory.
  This is a lie, since it just returns the original object.

Cloner
  An IDirectoryFactory adapter that just clones the original object.

$Id$
"""
__metaclass__ = type

import zope.app.filerepresentation.interfaces
from zope.proxy import removeAllProxies
from zope.interface import implements

def noop(container):
    """XXX adapt an IContainer to an IWriteDirectory by just returning it

    This "works" because IContainer and IWriteDirectory have the same
    methods, however, the output doesn't actually imlement IWriteDirectory.
    """
    return container

class Cloner:
    """IContainer to IDirectoryFactory adapter that clones

    This adapter provides a factory that creates a new empty container
    of the same class as it's context.
    """

    implements(zope.app.filerepresentation.interfaces.IDirectoryFactory)

    def __init__(self, context):
        self.context = context

    def __call__(self, name):
        # We remove all of the proxies so we can actually
        # call the class. This should be OK as we are only
        # calling this for objects that get this adapter.
        return removeAllProxies(self.context).__class__()
