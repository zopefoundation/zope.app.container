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

"""Subscriber function checking dependencies if a removal is performed
on an object having dependencies. It raises an exception if it's the
case.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app import zapi
from zope.app.dependable.interfaces import IDependable, DependencyError

exception_msg = """
Removal of object (%s) which has dependents (%s) is not possible !

You must desactivate this object before trying to remove it.
"""

def CheckDependency(event):
    object = event.object
    dependency = IDependable(object, None)
    if dependency is not None:
        dependents = dependency.dependents()
        if dependents:
            objectpath = zapi.getPath(object)
            raise DependencyError(exception_msg
                                  % (objectpath,
                                     ", ".join(dependents)))
