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
"""Define view component for folder contents.

$Id: traversal.py,v 1.3 2002/12/28 14:13:23 stevea Exp $
"""

from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.xmlrpc import IXMLRPCPublisher
from zope.publisher.interfaces import NotFound
from zope.app.interfaces.container import ISimpleReadContainer, IItemContainer
from zope.component import queryView
from zope.component import getDefaultViewName

from zope.app.interfaces.traversing import ITraversable
from zope.app.traversing.exceptions import UnexpectedParameters
from zope.app.interfaces.container import IReadContainer
from zope.exceptions import NotFoundError
from zope.component.exceptions import ComponentLookupError


class ContainerTraverser:

    __implements__ = IBrowserPublisher, IXMLRPCPublisher
    __used_for__ = ISimpleReadContainer

    def __init__(self, container, request):
        self.context = container
        self.request = request

    def publishTraverse(self, request, name):
        c = self.context

        subob = c.get(name, None)
        if subob is None:

            view = queryView(c, name, request)
            if view is not None:
                return view

            raise NotFound(c, name, request)

        return subob

    def browserDefault(self, request):
        c = self.context
        view_name = getDefaultViewName(c, request)
        view_uri = "@@%s" % view_name
        return c, (view_uri,)


class ItemTraverser(ContainerTraverser):

    __used_for__ = IItemContainer

    def publishTraverse(self, request, name):
        context = self.context

        try:
            return context[name]

        except KeyError:
            view = queryView(context, name, request)
            if view is not None:
                return view

        raise NotFound(context, name, request)

_marker = object()

class ContainerTraversable:
    """Traverses containers via getattr and get.
    """

    __implements__ = ITraversable
    __used_for__ = IReadContainer

    def __init__(self, container):
        self._container = container


    def traverse(self, name, parameters, original_name, furtherPath):
        if parameters:
            raise UnexpectedParameters(parameters)

        container = self._container

        v = container.get(name, _marker)
        if v is _marker:
            v = getattr(container, name, _marker)
            if v is _marker:
                raise NotFoundError, original_name

        return v
