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
"""Objects that take care of annotating dublin core meta data times

$Id: dependency.py,v 1.8 2003/07/01 22:18:05 fdrake Exp $
"""
from zope.component import queryAdapter
from zope.app.interfaces.dependable import IDependable
from zope.app.interfaces.dependable import DependencyError
from zope.app.interfaces.event import ISubscriber
from zope.proxy import removeAllProxies
from zope.app.traversing import getPath, canonicalPath
from zope.interface import implements

class DependencyChecker:
    """Checking dependency  while deleting object
    """
    implements(ISubscriber)

    def __init__(self):
        pass

    def notify(self, event):
        object = removeAllProxies(event.object)
        dependency = queryAdapter(object, IDependable)
        if dependency is not None:
            dependents = dependency.dependents()
            if dependents:
                objectpath = getPath(event.object)
                raise DependencyError("Removal of object (%s)"
                                      " which has dependents (%s)"
                                      % (objectpath,
                                         ", ".join(dependents)))

CheckDependency = DependencyChecker()
