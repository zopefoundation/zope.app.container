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
"""Sample container implementation.

This is primarily for testing purposes.

It might be useful as a mix-in for some classes, but many classes will
need a very different implementation.

Revision information:
$Id: sample.py,v 1.5 2002/12/30 20:43:49 jeremy Exp $
"""

from types import StringTypes

from zope.app.interfaces.container import IContainer, UnaddableError

class SampleContainer(object):
    """Sample container implementation suitable for testing.

    It is not suitable, directly as a base class unless the subclass
    overrides _Container__newData to return a persistent mapping
    object.
    """

    __implements__ =  IContainer

    def __init__(self):
        self.__data = self._newContainerData()

    def _newContainerData(self):
        """Construct an item-data container

        Subclasses should override this if they want different data.

        The value returned is a mapping object that also has get,
        has_key, keys, items, and values methods.
        """
        return {}

    def keys(self):
        '''See interface IReadContainer'''
        return self.__data.keys()

    def __iter__(self):
        return iter(self.__data.keys())

    def __getitem__(self, key):
        '''See interface IReadContainer'''
        return self.__data[key]

    def get(self, key, default=None):
        '''See interface IReadContainer'''
        return self.__data.get(key, default)

    def values(self):
        '''See interface IReadContainer'''
        return self.__data.values()

    def __len__(self):
        '''See interface IReadContainer'''
        return len(self.__data)

    def items(self):
        '''See interface IReadContainer'''
        return self.__data.items()

    def __contains__(self, key):
        '''See interface IReadContainer'''
        return self.__data.has_key(key)

    has_key = __contains__

    def setObject(self, key, object):
        '''See interface IWriteContainer'''
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
        self.__data[key] = object
        return key

    def __delitem__(self, key):
        '''See interface IWriteContainer'''
        del self.__data[key]