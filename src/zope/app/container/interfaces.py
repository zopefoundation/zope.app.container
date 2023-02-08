##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Container-related interfaces
"""
__docformat__ = 'restructuredtext'

# BBB
from zope.browser.interfaces import IAdding
# BBB
from zope.container.interfaces import ContainerError
from zope.container.interfaces import DuplicateIDError
from zope.container.interfaces import IBTreeContainer
from zope.container.interfaces import IContainer
from zope.container.interfaces import IContainerModifiedEvent
from zope.container.interfaces import IContainerNamesContainer
from zope.container.interfaces import IFind
from zope.container.interfaces import IIdFindFilter
from zope.container.interfaces import IItemContainer
from zope.container.interfaces import IItemWriteContainer
from zope.container.interfaces import INameChooser
from zope.container.interfaces import InvalidContainerType
from zope.container.interfaces import InvalidItemType
from zope.container.interfaces import InvalidType
from zope.container.interfaces import IObjectFindFilter
from zope.container.interfaces import IOrderedContainer
from zope.container.interfaces import IReadContainer
from zope.container.interfaces import ISimpleReadContainer
from zope.container.interfaces import IWriteContainer
from zope.container.interfaces import UnaddableError
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectMovedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.location.interfaces import IContained
