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

$Id: find.py,v 1.4 2003/06/01 15:59:29 jim Exp $

"""

from zope.app.interfaces.container.find import IFind, IIdFindFilter
from zope.app.interfaces.container import IReadContainer
# XXX need to do this manually to wrap objects
from zope.app.context import ContextWrapper

class FindAdapter(object):

    __implements__ =  IFind

    __used_for__ = IReadContainer

    def __init__(self, context):
        self._context = context

    def find(self, id_filters=None, object_filters=None):
        'See IFind'
        id_filters = id_filters or []
        object_filters = object_filters or []
        result = []
        container = self._context
        for id, object in container.items():
            object = ContextWrapper(object, container, name=id)
            _find_helper(id, object, container,
                         id_filters, object_filters,
                         result)
        return result

    #
    ############################################################

def _find_helper(id, object, container, id_filters, object_filters, result):
    for id_filter in id_filters:
        if not id_filter.matches(id):
            break
    else:
        # if we didn't break out of the loop, all name filters matched
        # now check all object filters
        for object_filter in object_filters:
            if not object_filter.matches(object):
                break
        else:
            # if we didn't break out of the loop, all filters matched
            result.append(object)

    if not IReadContainer.isImplementedBy(object):
        return

    container = object
    for id, object in container.items():
        object = ContextWrapper(object, container, name=id)
        _find_helper(id, object, container, id_filters, object_filters, result)

class SimpleIdFindFilter(object):

    __implements__ =  IIdFindFilter

    def __init__(self, ids):
        self._ids = ids

    def matches(self, id):
        'See INameFindFilter'
        return id in self._ids
