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
$Id: zopecontainer.py,v 1.8 2003/02/03 17:13:48 sidnei Exp $
"""

from zope.app.interfaces.container import IZopeContainer
from zope.app.interfaces.container import IOptionalNamesContainer
from zope.app.interfaces.container import IContainerNamesContainer
from zope.component import queryAdapter
from zope.proxy.context import ContextWrapper
from zope.app.event import publish
from zope.app.event.objectevent \
     import ObjectRemovedEvent, ObjectModifiedEvent, ObjectAddedEvent, \
            ObjectMovedEvent
from zope.app.interfaces.container import IAddNotifiable
from zope.app.interfaces.container import IDeleteNotifiable
from zope.app.interfaces.container import IMoveNotifiable
from zope.app.interfaces.container import IMoveSource
from zope.app.interfaces.container import IPasteTarget
from zope.app.interfaces.container import IPasteTarget
from zope.app.interfaces.container import IContainerCopyPasteMoveSupport
from zope.app.interfaces.copy import IObjectMover
from zope.app.interfaces.traversing import IPhysicallyLocatable
from types import StringTypes
from zope.proxy.introspection import removeAllProxies

_marker = object()

class ZopeContainerAdapter:

    __implements__ =  (IZopeContainer, IContainerCopyPasteMoveSupport)

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
            adapter.manage_afterAdd(object, container)

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
            adapter.manage_beforeDelete(object, container)
        elif hasattr(object, 'manage_beforeDelete'):
            # XXX: Ideally, only do this in debug mode.
            from warnings import warn
            warn('Class %s has manage_beforeDelete but is not'
                 ' IDeleteNotifiable' % object.__class__)

        del container[key]

        publish(container, ObjectRemovedEvent(object))
        publish(container, ObjectModifiedEvent(container))

        return key

    def __iter__(self):
        '''See interface IReadContainer'''
        return iter(self.context)

    def rename(currentKey, newKey):
        """Put the object found at 'currentKey' under 'newKey' instead.
        
        The container can choose different or modified 'newKey'. The
        'newKey' that was used is returned.
        
        If the object at 'currentKey' is IMoveNotifiable, its
        manage_beforeDelete method is called, with a movingTo
        argument of the container's path plus the 'newKey'.
        Otherwise, if the object at 'currentKey' is IDeleteNotifiable,
        its manage_beforeDelete method is called.
        
        Then, the object is removed from the container using the
        container's __del__ method.
        
        Then, If the object is IMoveNotifiable, its manage_afterAdd
        method is called, with a movedFrom argument of the container's
        path plus the 'currentKey'.
        Otherwise, if the object is IAddNotifiable, its manage_afterAdd
        method is called.
        
        Then, an IObjectMovedEvent is published.
        """

        object = self.get(currentKey)
        mover = getAdapter(object, IObjectMover)
        container = self.context
        target = getAdapter(container, IPasteTarget)

        if mover.moveable() and mover.moveableTo(target, newKey):
            physical = getAdapter(container, IPhysicallyLocatable)
            target_path = physical.getPhysicalPath()

            if queryAdapter(object, IMoveNotifiable):
              object.manage_beforeDelete(object, container, \
              movingTo=target_path)
            elif queryAdapter(object, IDeleteNotifiable):
              object.manage_beforeDelete(object, container)

            source = getAdapter(container, IMoveSource)
            object = source.removeObject(currentKey, target_path)

            mover = getAdapter(object, IObjectMover)
            mover.moveTo(target, newKey)
          
            publish(container, ObjectMovedEvent(object))




           