##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Objects that take care of annotating dublin core meta data times

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app import zapi
from zope.app.dependable.interfaces import IDependable, DependencyError
from zope.proxy import removeAllProxies

def CheckDependency(event):

    # We have to remove the proxies here to be able to get at
    # annotations. Perhaps this should be a trusted subscriber, but we
    # don't have those yet.

    object = removeAllProxies(event.object)
    dependency = IDependable(object, None)
    if dependency is not None:
        dependents = dependency.dependents()
        if dependents:
            objectpath = zapi.getPath(event.object)
            raise DependencyError("Removal of object (%s)"
                                  " which has dependents (%s)"
                                  % (objectpath,
                                     ", ".join(dependents)))
