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

Revision information:
$Id: zopecontainer.py,v 1.20 2003/06/13 17:53:34 stevea Exp $
"""

from zope.app.interfaces.container import IZopeContainer
from zope.app.interfaces.container import IOptionalNamesContainer
from zope.app.interfaces.container import IContainerNamesContainer
from zope.component import queryAdapter, getAdapter
from zope.app.context import ContextWrapper, Wrapper
from zope.app.event import publish
from zope.app.interfaces.container import IAddNotifiable
from zope.app.interfaces.container import IDeleteNotifiable
from zope.app.interfaces.copypastemove import IObjectMover
from types import StringTypes
from zope.proxy import removeAllProxies, getProxiedObject
from zope.exceptions import NotFoundError, DuplicationError
from zope.app.event.objectevent import ObjectRemovedEvent
from zope.app.event.objectevent import ObjectModifiedEvent, ObjectAddedEvent
from zope.interface import implements

_marker = object()

class xZopeContainerAdapter:

    implements(IZopeContainer)

    def __init__(self, container):
        self.context = container

    def __getitem__(self, key):
        "See IZopeItemContainer"
        value = self.context[key]
        return ContextWrapper(value, self.context, name=key)

    def get(self, key, default=None):
        "See IZopeSimpleReadContainer"
        value = self.context.get(key, _marker)
        if value is not _marker:
            return ContextWrapper(value, self.context, name=key)
        else:
            return default

    def __contains__(self, key):
        '''See interface IReadContainer'''
        return key in self.context


    def values(self):
        "See IZopeReadContainer"
        container = self.context
        result = []
        for key, value in container.items():
            result.append(ContextWrapper(value, container, name=key))
        return result

    def keys(self):
        '''See interface IReadContainer'''
        return self.context.keys()

    def __len__(self):
        '''See interface IReadContainer'''
        return len(self.context)

    def items(self):
        "See IZopeReadContainer"
        container = self.context
        result = []
        for key, value in container.items():
            result.append((key, ContextWrapper(value, container, name=key)))
        return result


    def setObject(self, key, object):
        "See IZopeWriteContainer"

        if not isinstance(key, StringTypes):
            raise TypeError("Item name is not a string.")

        container = self.context

        if not key:
            if not (IOptionalNamesContainer.isImplementedBy(container)
                    or IContainerNamesContainer.isImplementedBy(container)):
                raise ValueError("Empty names are not allowed")

        # We remove the proxies from the object before adding it to
        # the container, because we can't store proxies.
        object = removeAllProxies(object)

        # Add the object
        key = container.setObject(key, object)

        # Publish an added event
        # We explicitly get the object back from the container with
        # container[key], because some kinds of container may choose
        # to store a different object than the exact one we added.
        object = ContextWrapper(container[key], container, name=key)
        publish(container, ObjectAddedEvent(object))

        # Call the after add hook, if necessary
        adapter = queryAdapter(object, IAddNotifiable)
        if adapter is not None:
            adapter.afterAddHook(object, container)

        publish(container, ObjectModifiedEvent(container))
        return key

    def __delitem__(self, key):
        "See IZopeWriteContainer"
        container = self.context

        object = container[key]
        object = ContextWrapper(object, container, name=key)

        # Call the before delete hook, if necessary
        adapter = queryAdapter(object, IDeleteNotifiable)
        if adapter is not None:
            adapter.beforeDeleteHook(object, container)
        elif hasattr(object, 'beforeDeleteHook'):
            # XXX: Ideally, only do this in debug mode.
            from warnings import warn
            warn('Class %s has beforeDeleteHook but is not'
                 ' IDeleteNotifiable' % object.__class__)

        del container[key]

        publish(container, ObjectRemovedEvent(object))
        publish(container, ObjectModifiedEvent(container))

        return key

    def __iter__(self):
        '''See interface IReadContainer'''
        return iter(self.context)

    def rename(self, currentKey, newKey):
        """Put the object found at 'currentKey' under 'newKey' instead.

        The container can choose different or modified 'newKey'. The
        'newKey' that was used is returned.

        If the object at 'currentKey' is IMoveNotifiable, its
        beforeDeleteHook method is called, with a movingTo
        argument of the container's path plus the 'newKey'.
        Otherwise, if the object at 'currentKey' is IDeleteNotifiable,
        its beforeDeleteHook method is called.

        Then, the object is removed from the container using the
        container's __del__ method.

        Then, If the object is IMoveNotifiable, its afterAddHook
        method is called, with a movedFrom argument of the container's
        path plus the 'currentKey'.
        Otherwise, if the object is IAddNotifiable, its afterAddHook
        method is called.

        Then, an IObjectMovedEvent is published.
        """

        object = self.get(currentKey)
        if object is None:
            raise NotFoundError(self.context, currentKey)
        mover = getAdapter(object, IObjectMover)
        target = self.context

        if target.__contains__(newKey):
            raise DuplicationError("name, %s, is already in use" % newKey)

        if mover.moveable() and mover.moveableTo(target, newKey):
            # the mover will call beforeDeleteHook hook for us
            mover.moveTo(target, newKey)
            # the mover will call the afterAddHook hook for us
            # the mover will publish an ObjectMovedEvent for us

class ZopeContainerDecorator(Wrapper):
    implements(IZopeContainer)

    def __getitem__(self, key):
        "See IZopeItemContainer"
        container = getProxiedObject(self)
        value = container[key]
        return ContextWrapper(value, self, name=key)

    def get(self, key, default=None):
        "See IZopeSimpleReadContainer"
        container = getProxiedObject(self)
        value = container.get(key, _marker)
        if value is not _marker:
            return ContextWrapper(value, self, name=key)
        else:
            return default

    def values(self):
        "See IZopeReadContainer"
        container = getProxiedObject(self)
        result = []
        for key, value in container.items():
            result.append(ContextWrapper(value, self, name=key))
        return result

    def items(self):
        "See IZopeReadContainer"
        container = getProxiedObject(self)
        result = []
        for key, value in container.items():
            result.append((key, ContextWrapper(value, self, name=key)))
        return result

    def setObject(self, key, object):
        "See IZopeWriteContainer"
        if not isinstance(key, StringTypes):
            raise TypeError("Item name is not a string.")

        container = getProxiedObject(self)

        if not key:
            if not (IOptionalNamesContainer.isImplementedBy(container)
                    or IContainerNamesContainer.isImplementedBy(container)):
                raise ValueError("Empty names are not allowed")

        # We remove the proxies from the object before adding it to
        # the container, because we can't store proxies.
        object = removeAllProxies(object)

        # Add the object
        key = container.setObject(key, object)

        # Publish an added event
        # We explicitly get the object back from the container with
        # container[key], because some kinds of container may choose
        # to store a different object than the exact one we added.
        object = self[key]
        publish(self, ObjectAddedEvent(object))

        # Call the after add hook, if necessary
        adapter = queryAdapter(object, IAddNotifiable)
        if adapter is not None:
            adapter.afterAddHook(object, self)

        publish(self, ObjectModifiedEvent(self))
        return key

    def __delitem__(self, key):
        "See IZopeWriteContainer"
        container = getProxiedObject(self)

        object = ContextWrapper(container[key], self, name=key)

        # Call the before delete hook, if necessary
        adapter = queryAdapter(object, IDeleteNotifiable)
        if adapter is not None:
            adapter.beforeDeleteHook(object, self)
        elif hasattr(object, 'beforeDeleteHook'):
            # XXX: Ideally, only do this in debug mode.
            from warnings import warn
            warn('Class %s has beforeDeleteHook but is not'
                 ' IDeleteNotifiable' % object.__class__)

        del container[key]

        publish(self, ObjectRemovedEvent(object))
        publish(self, ObjectModifiedEvent(self))

        return key

    def rename(self, currentKey, newKey):
        """Put the object found at 'currentKey' under 'newKey' instead.

        The container can choose different or modified 'newKey'. The
        'newKey' that was used is returned.

        If the object at 'currentKey' is IMoveNotifiable, its
        beforeDeleteHook method is called, with a movingTo
        argument of the container's path plus the 'newKey'.
        Otherwise, if the object at 'currentKey' is IDeleteNotifiable,
        its beforeDeleteHook method is called.

        Then, the object is removed from the container using the
        container's __del__ method.

        Then, If the object is IMoveNotifiable, its afterAddHook
        method is called, with a movedFrom argument of the container's
        path plus the 'currentKey'.
        Otherwise, if the object is IAddNotifiable, its afterAddHook
        method is called.

        Then, an IObjectMovedEvent is published.
        """
        object = self.get(currentKey)
        if object is None:
            raise NotFoundError(self, currentKey)
        mover = getAdapter(object, IObjectMover)
        target = self

        if newKey in target:
            raise DuplicationError("name, %s, is already in use" % newKey)

        if mover.moveable() and mover.moveableTo(target, newKey):
            # the mover will call beforeDeleteHook hook for us
            mover.moveTo(target, newKey)
            # the mover will call the afterAddHook hook for us
            # the mover will publish an ObjectMovedEvent for us

