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
"""Ordered container implementation.

Revision information:
$Id: ordered.py,v 1.3 2003/06/24 10:33:59 stevea Exp $
"""

from zope.app.interfaces.container import IOrderedContainer
from zope.interface import implements
from persistence import Persistent
from persistence.dict import PersistentDict
from persistence.list import PersistentList
from types import StringTypes

class OrderedContainer(Persistent):
    """ OrderedContainer maintains entries' order as added and moved.

    >>> oc = OrderedContainer()
    >>> int(IOrderedContainer.isImplementedBy(oc))
    1
    >>> len(oc)
    0
    """

    implements(IOrderedContainer)

    def __init__(self):

        self._data = PersistentDict()
        self._order = PersistentList()

    def keys(self):
        """ See IOrderedContainer.

        >>> oc = OrderedContainer()
        >>> oc.keys()
        []
        >>> key = oc.setObject('foo', 'bar')
        >>> oc.keys()
        ['foo']
        >>> key = oc.setObject('baz', 'quux')
        >>> oc.keys()
        ['foo', 'baz']
        >>> int(len(oc._order) == len(oc._data))
        1
        """

        return self._order[:]

    def __iter__(self):
        """ See IOrderedContainer.

        >>> oc = OrderedContainer()
        >>> oc.keys()
        []
        >>> key = oc.setObject('foo', 'bar')
        >>> key = oc.setObject('baz', 'quux')
        >>> [i for i in oc]
        ['foo', 'baz']
        >>> int(len(oc._order) == len(oc._data))
        1
        """

        return iter(self.keys())

    def __getitem__(self, key):
        """ See IOrderedContainer

        >>> oc = OrderedContainer()
        >>> key = oc.setObject('foo', 'bar')
        >>> oc['foo']
        'bar'
        """

        return self._data[key]

    def get(self, key, default=None):
        """ See IOrderedContainer

        >>> oc = OrderedContainer()
        >>> key = oc.setObject('foo', 'bar')
        >>> oc.get('foo')
        'bar'
        >>> oc.get('funky', 'No chance, dude.')
        'No chance, dude.'
        """

        return self._data.get(key, default)

    def values(self):
        """ See IOrderedContainer.

        >>> oc = OrderedContainer()
        >>> oc.keys()
        []
        >>> key = oc.setObject('foo', 'bar')
        >>> oc.values()
        ['bar']
        >>> key = oc.setObject('baz', 'quux')
        >>> oc.values()
        ['bar', 'quux']
        >>> int(len(oc._order) == len(oc._data))
        1
        """

        return [self._data[i] for i in self._order]

    def __len__(self):
        """ See IOrderedContainer

        >>> oc = OrderedContainer()
        >>> int(len(oc) == 0)
        1
        >>> key = oc.setObject('foo', 'bar')
        >>> int(len(oc) == 1)
        1
        """

        return len(self._data)

    def items(self):
        """ See IOrderedContainer.

        >>> oc = OrderedContainer()
        >>> oc.keys()
        []
        >>> key = oc.setObject('foo', 'bar')
        >>> oc.items()
        [('foo', 'bar')]
        >>> key = oc.setObject('baz', 'quux')
        >>> oc.items()
        [('foo', 'bar'), ('baz', 'quux')]
        >>> int(len(oc._order) == len(oc._data))
        1
        """

        return [(i, self._data[i]) for i in self._order]

    def __contains__(self, key):
        """ See IOrderedContainer.

        >>> oc = OrderedContainer()
        >>> key = oc.setObject('foo', 'bar')
        >>> int('foo' in oc)
        1
        >>> int('quux' in oc)
        0
        """

        return self._data.has_key(key)

    has_key = __contains__

    def setObject(self, key, object):
        """ See IOrderedContainer.

        >>> oc = OrderedContainer()
        >>> oc.keys()
        []
        >>> key = oc.setObject('foo', 'bar')
        >>> oc._order
        ['foo']
        >>> key = oc.setObject('baz', 'quux')
        >>> oc._order
        ['foo', 'baz']
        >>> int(len(oc._order) == len(oc._data))
        1
        """

        existed = self._data.has_key(key)

        bad = False
        if isinstance(key, StringTypes):
            try:
                unicode(key)
            except UnicodeError:
                bad = True
        else:
            bad = True
        if bad: 
            raise TypeError("'%s' is invalid, the key must be an "
                            "ascii or unicode string" % key)
        if len(key) == 0:
            raise ValueError("The key cannot be an empty string")
        self._data[key] = object

        if not existed:
            self._order.append(key)

        return key

    def __delitem__(self, key):
        """ See IOrderedContainer.

        >>> oc = OrderedContainer()
        >>> oc.keys()
        []
        >>> key = oc.setObject('foo', 'bar')
        >>> key = oc.setObject('baz', 'quux')
        >>> key = oc.setObject('zork', 'grue')
        >>> oc.items()
        [('foo', 'bar'), ('baz', 'quux'), ('zork', 'grue')]
        >>> int(len(oc._order) == len(oc._data))
        1
        >>> del oc['baz']
        >>> oc.items()
        [('foo', 'bar'), ('zork', 'grue')]
        >>> int(len(oc._order) == len(oc._data))
        1
        """

        del self._data[key]
        self._order.remove(key)

    def updateOrder(self, order):
        """ See IOrderedContainer

        >>> oc = OrderedContainer()
        >>> key = oc.setObject('foo', 'bar')
        >>> key = oc.setObject('baz', 'quux')
        >>> key = oc.setObject('zork', 'grue')
        >>> oc.keys()
        ['foo', 'baz', 'zork']
        >>> oc.updateOrder(['baz', 'foo', 'zork'])
        >>> oc.keys()
        ['baz', 'foo', 'zork']
        >>> oc.updateOrder(['baz', 'zork', 'foo'])
        >>> oc.keys()
        ['baz', 'zork', 'foo']
        >>> oc.updateOrder(['baz', 'zork', 'foo'])
        >>> oc.keys()
        ['baz', 'zork', 'foo']
        >>> oc.updateOrder(['baz', 'zork'])
        Traceback (most recent call last):
        ...
        ValueError: Incompatible key set.
        >>> oc.updateOrder(['foo', 'bar', 'baz', 'quux'])
        Traceback (most recent call last):
        ...
        ValueError: Incompatible key set.
        >>> oc.updateOrder(1)
        Traceback (most recent call last):
        ...
        TypeError: len() of unsized object
        >>> oc.updateOrder(['baz', 'zork', 'quux'])
        Traceback (most recent call last):
        ...
        ValueError: Incompatible key set.
        """

        if len(order) != len(self._order):
            raise ValueError("Incompatible key set.")

        was_dict = {}
        will_be_dict = {}

        for i in range(len(order)):
            was_dict[self._order[i]] = 1
            will_be_dict[order[i]] = 1

        if will_be_dict != was_dict:
            raise ValueError("Incompatible key set.")

        self._order = order
