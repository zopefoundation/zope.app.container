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
$Id: zopecontainer.py,v 1.26 2003/07/17 14:45:17 alga Exp $
"""

from zope.app.interfaces.container import IZopeSimpleReadContainer
from zope.app.interfaces.container import IZopeReadContainer
from zope.app.interfaces.container import IZopeItemWriteContainer
from zope.app.interfaces.container import IZopeContainer
from zope.app.interfaces.container import IOptionalNamesContainer
from zope.app.interfaces.container import IContainerNamesContainer
from zope.component import queryAdapter, getAdapter
from zope.app.context import ContextWrapper, Wrapper
from zope.context import ContextDescriptor
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
from zope.context.wrapper import getdescriptor
_marker = object()

__metaclass__ = type

class ContainerDecoratorSuper:
    """Like a super() but for wrappers.

    The descriptors get their self rebound to a wrapper if they are
    context descriptors.

    XXX: this is just a plug to get context awareness work on Zope
    container instances.  This has to be implemented in wrapper.c
    """

    __slots__ = 'wrapper',

    def __init__(self, wrapper):
        self.wrapper = wrapper

    def _getDescriptor(self, attr):
        '''Returns a bound method with self rebound if the descriptor
        is a ContextDescriptor, and a normal method otherwise.
        '''
        wrapper = self.wrapper
        obj = getProxiedObject(wrapper)
        cls = getattr(obj, '__class__', type(obj))
        descriptor = getdescriptor(obj, attr)
        if isinstance(descriptor, ContextDescriptor):
            return descriptor.__get__(wrapper, cls)
        else:
            return getattr(obj, attr)

    def __getitem__(self, key):
        return self._getDescriptor('__getitem__')(key)

    def __contains__(self, key):
        return self._getDescriptor('__contains__')(key)

    def get(self, key, default):
        return self._getDescriptor('get')(key, default)

    def items(self):
        return self._getDescriptor('items')()

    def values(self):
        return self._getDescriptor('values')()

    def __delitem__(self, key):
        return self._getDescriptor('__delitem__')(key)

    def setObject(self, key, value):
        return self._getDescriptor('setObject')(key, value)



class ZopeItemContainerDecorator(Wrapper):
    """Decorates an IItemContainer object for context-awareness.

    Also, upgrades it to IZopeSimpleReadContainer.
    """
    implements(IZopeSimpleReadContainer)

    def __getitem__(self, key):
        "See IZopeItemContainer"
        return ContextWrapper(ContainerDecoratorSuper(self)[key],
                              self, name=key)

    def get(self, key, default=None):
        "See IZopeSimpleReadContainer"
        # 'get' defined in terms of __getitem__
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        "See IReadMapping"
        # '__contains__' in terms of __getitem__ on the proxied object
        container = ContainerDecoratorSuper(self)
        try:
            container[key]
            return True
        except KeyError:
            return False


class ZopeSimpleReadContainerDecorator(ZopeItemContainerDecorator):
    implements(IZopeSimpleReadContainer)

    def get(self, key, default=None):
        "See IZopeSimpleReadContainer"
        container = ContainerDecoratorSuper(self)
        value = container.get(key, _marker)
        if value is not _marker:
            return ContextWrapper(value, self, name=key)
        else:
            return default


class ZopeReadContainerDecorator(ZopeSimpleReadContainerDecorator):
    implements(IZopeReadContainer)

    def values(self):
        "See IZopeReadContainer"
        container = ContainerDecoratorSuper(self)
        result = []
        for key, value in container.items():
            result.append(ContextWrapper(value, self, name=key))
        return result

    def items(self):
        "See IZopeReadContainer"
        container = ContainerDecoratorSuper(self)
        result = []
        for key, value in container.items():
            result.append((key, ContextWrapper(value, self, name=key)))
        return result


class ZopeItemWriteContainerDecorator(ZopeItemContainerDecorator):
    # Both 'setObject' and '__delitem__' depend on the decorator having
    # '__getitem__'
    #
    # A ZopeWriteContainerDecorator could be written to work with other
    # means for getting objects from a container. However, in most cases,
    # IZopeWriteContainer depends on IItemContainer.

    implements(IZopeItemWriteContainer)

    def setObject(self, key, object):
        "See IZopeWriteContainer"
        container = ContainerDecoratorSuper(self)
        unwrapped = removeAllProxies(self)

        if not key:
            if not (IOptionalNamesContainer.isImplementedBy(unwrapped)
                    or IContainerNamesContainer.isImplementedBy(unwrapped)):
                raise ValueError("Empty names are not allowed")
            key = ''
        else:
            if not isinstance(key, StringTypes):
                raise TypeError("Item name is not a string.")

        # We remove the proxies from the object before adding it to
        # the container, because we can't store proxies.
        object = removeAllProxies(object)

        # Add the object
        key = container.setObject(key, object)

        # Publish an added event
        # We explicitly get the object back from the container with
        # container[key], because some kinds of container may choose
        # to store a different object than the exact one we added.
        #
        # Dependency Note: This is a dependency on IItemContainer
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
        container = ContainerDecoratorSuper(self)

        # Dependency Note: This is a dependency on IItemContainer
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


class ZopeContainerDecorator(ZopeItemWriteContainerDecorator,
                             ZopeReadContainerDecorator):
    implements(IZopeContainer)

    # XXX: rename should really be in IZopeWriteContainer, and should
    #      lose its dependence on decorator.get(). However, the whole
    #      renaming business will be refactored soon, so this method
    #      will go away at that point.
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

