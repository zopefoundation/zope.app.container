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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: directory.py,v 1.1 2003/02/03 15:08:29 jim Exp $
"""
__metaclass__ = type

import zope.app.interfaces.file
from zope.proxy.introspection import removeAllProxies

def noop(container):
    return container

class Cloner:

    __implements__ = zope.app.interfaces.file.IDirectoryFactory

    def __init__(self, context):
        self.context = context

    def __call__(self, name):
        # We remove all of the proxies so we can actually
        # call the class. This should be OK as we are only
        # calling this for objects that get this adapter.
        return removeAllProxies(self.context).__class__()
