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
"""BBB this module moved to zope.container
"""

# BBB
from zope.container.contained import Contained
from zope.container.contained import ContainedProxy
from zope.container.contained import ContainedProxyClassProvides
from zope.container.contained import ContainerModifiedEvent
from zope.container.contained import ContainerSublocations
from zope.container.contained import DecoratedSecurityCheckerDescriptor
from zope.container.contained import DecoratorSpecificationDescriptor
from zope.container.contained import NameChooser
from zope.container.contained import ObjectAddedEvent
from zope.container.contained import ObjectMovedEvent
from zope.container.contained import ObjectRemovedEvent
from zope.container.contained import contained
from zope.container.contained import containedEvent
from zope.container.contained import dispatchToSublocations
from zope.container.contained import fixing_up
from zope.container.contained import notifyContainerModified
from zope.container.contained import setitem
from zope.container.contained import uncontained
