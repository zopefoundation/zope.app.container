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
$Id: copypastemove.py,v 1.5 2003/03/31 14:48:40 sidnei Exp $
"""

from zope.app.interfaces.container import IOptionalNamesContainer
from zope.app.interfaces.container import IContainerNamesContainer
from zope.app.interfaces.container import IMoveSource
from zope.app.interfaces.container import ICopySource, INoChildrenCopySource
from zope.app.interfaces.container import IPasteTarget
from zope.app.interfaces.container import IPasteNamesChooser
from zope.app.interfaces.content.folder import ICloneWithoutChildren
from zope.component import getAdapter
from zope.proxy.introspection import removeAllProxies
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.proxy.context import ContextWrapper
from zope.app.event import publish
from zope.proxy.introspection import removeAllProxies
from types import StringTypes
import copy

class PasteTarget:

    __implements__ = IPasteTarget

    def __init__(self, container):
        self.context = container

    def acceptsObject(self, key, obj):
        '''Allow the container to say if it accepts the given wrapped
        object.

        Returns True if the object would be accepted as contents of
        this container. Otherwise, returns False.
        '''
        container = self.context
        nameschooser = getAdapter(container, IPasteNamesChooser)
        key = nameschooser.getNewName(obj, key)
        if key in container:
            return False
        return True


    def pasteObject(self, key, obj):
        '''Add the given object to the container under the given key.

        Raises a ValueError if key is an empty string, unless the
        this object chooses a different key.

        Returns the key used, which might be different than the
        given key.

        This method must not issue an IObjectAddedEvent, nor must it
        call the afterAddHook method of the object.
        However, it must publish an IObjectModified event for the
        container.
        '''
        if not isinstance(key, StringTypes):
            raise TypeError("Item name is not a string.")

        container = self.context

        if not key:
            if not (IOptionalNamesContainer.isImplementedBy(container)
                    or IContainerNamesContainer.isImplementedBy(container)):
                raise ValueError("Empty names are not allowed")

        # We remove the proxies from the object before adding it to
        # the container, because we can't store proxies.
        obj = removeAllProxies(obj)

        nameschooser = getAdapter(container, IPasteNamesChooser)
        key = nameschooser.getNewName(obj, key)

        # Add the object
        key = container.setObject(key, obj)

        # we dont publish the added event here
        # and dont call the after add hook

        publish(container, ObjectModifiedEvent(container))
        return key

class MoveSource:

    __implements__ = IMoveSource

    def __init__(self, container):
        self.context = container

    def removeObject(self, key, movingTo):
        '''Remove and return the object with the given key, as the
        first part of a move.

        movingTo is the unicode path for where the move is to.
        This method should not publish an IObjectRemovedEvent, nor should
        it call the afterDeleteHook method of the object.
        However, it must publish an IObjectModified event for the
        container.
        '''
        container = self.context

        object = container[key]
        object = ContextWrapper(object, container, name=key)

        # here, we dont call the before delete hook
        del container[key]

        # and we dont publish an ObjectRemovedEvent
        publish(container, ObjectModifiedEvent(container))

        return object

class CopySource:

    __implements__ = ICopySource

    def __init__(self, container):
        self.context = container

    def copyObject(self, key, copyingTo):
        '''Return the object with the given key, as the first part of a
        copy.

        copyingTo is the unicode path for where the copy is to.
        '''
        value = self.context.get(key, None)
        if value is not None:
            value = removeAllProxies(value)
            value = copy.deepcopy(value)
            return ContextWrapper(value, self.context, name=key)


class NoChildrenCopySource:

    __implements__ = INoChildrenCopySource

    def __init__(self, container):
        self.context = container

    def copyObjectWithoutChildren(self, key, copyingTo):
        '''Return the object with the given key, without children, as
        the first part of a copy.

        copyingTo is the unicode path for where the copy is to.
        '''
        value = self.context.get(key, None)
        if value is not None:
            value = removeAllProxies(value)
            if not ICloneWithoutChildren.isImplementedBy(value):
                return None
            value = value.cloneWithoutChildren()
            return ContextWrapper(value, self.context, name=key)

class PasteNamesChooser:

    __implements__ = IPasteNamesChooser

    def __init__(self, container):
        self.context = container

    def getNewName(self, obj, key):
        '''See IPasteNamesChooser'''
        new_key = key
        container = self.context

        if key not in container:
            return key

        n = 1
        while new_key in container:
            if n > 1:
                new_key = 'copy%s_of_%s' % (n, key)
            else:
                new_key = 'copy_of_%s' % key
            n += 1
        return new_key
