##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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

$Id$
"""
__docformat__ = 'restructuredtext'

# BBB
from zope.container.interfaces import (
    DuplicateIDError,
    ContainerError,
    InvalidContainerType,
    InvalidItemType,
    InvalidType,
    IContained,
    IItemContainer,
    ISimpleReadContainer,
    IReadContainer,
    IWriteContainer,
    IItemWriteContainer,
    IContainer,
    IBTreeContainer,
    IOrderedContainer,
    IContainerNamesContainer,
    IObjectMovedEvent,
    UnaddableError,
    IObjectAddedEvent,
    INameChooser,
    IObjectRemovedEvent,
    IContainerModifiedEvent,
    IFind,
    IObjectFindFilter,
    IIdFindFilter
)

import zope.publisher.interfaces.browser
import zope.interface


class IAdding(zope.publisher.interfaces.browser.IBrowserView):
    def add(content):
        """Add content object to container.

        Add using the name in `contentName`.  Returns the added object
        in the context of its container.

        If `contentName` is already used in container, raises
        ``DuplicateIDError``.
        """

    contentName = zope.interface.Attribute(
         """The content name, as usually set by the Adder traverser.

         If the content name hasn't been defined yet, returns ``None``.

         Some creation views might use this to optionally display the
         name on forms.
         """
         )

    def nextURL():
        """Return the URL that the creation view should redirect to.

        This is called by the creation view after calling add.

        It is the adder's responsibility, not the creation view's to
        decide what page to display after content is added.
        """

    def nameAllowed():
        """Return whether names can be input by the user."""

    def addingInfo():
        """Return add menu data as a sequence of mappings.

        Each mapping contains 'action', 'title', and possibly other keys.

        The result is sorted by title.
        """

    def isSingleMenuItem():
        """Return whether there is single menu item or not."""

    def hasCustomAddView():
        "This should be called only if there is `singleMenuItem` else return 0"
