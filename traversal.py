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
"""Traversal components for containers

$Id: traversal.py,v 1.12 2004/03/19 03:17:23 srichter Exp $
"""
from zope.interface import implements
from zope.exceptions import NotFoundError
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.xmlrpc import IXMLRPCPublisher
from zope.publisher.interfaces import NotFound

from zope.app import zapi
from zope.app.container.interfaces import ISimpleReadContainer, IItemContainer
from zope.app.container.interfaces import IReadContainer
from zope.app.traversing.interfaces import ITraversable
from zope.app.traversing.namespace import UnexpectedParameters

# Note that the next two classes are included here because they
# can be used for multiple view types.

class ContainerTraverser:
    """A traverser that knows how to look up objects by name in a container."""

    implements(IBrowserPublisher, IXMLRPCPublisher)
    __used_for__ = ISimpleReadContainer

    def __init__(self, container, request):
        self.context = container
        self.request = request

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.IPublishTraverse"""
        subob = self.context.get(name, None)
        if subob is None:
            view = zapi.queryView(self.context, name, request)
            if view is not None:
                return view

            raise NotFound(self.context, name, request)

        return subob

    def browserDefault(self, request):
        """See zope.publisher.browser.interfaces.IBrowserPublisher"""
        view_name = zapi.getDefaultViewName(self.context, request)
        view_uri = "@@%s" %view_name
        return self.context, (view_uri,)


class ItemTraverser(ContainerTraverser):
    """A traverser that knows how to look up objects by name in an item
    container."""

    __used_for__ = IItemContainer

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.IPublishTraverse"""
        try:
            return self.context[name]
        except KeyError:
            view = zapi.queryView(self.context, name, request)
            if view is not None:
                return view

        raise NotFound(self.context, name, request)


_marker = object()

class ContainerTraversable:
    """Traverses containers via getattr and get."""

    implements(ITraversable)
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
