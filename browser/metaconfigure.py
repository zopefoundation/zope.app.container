##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Container-specific browser ZCML namespace directive handlers

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.configuration.fields import GlobalObject
from zope.schema import Id
from zope.app.publisher.browser.viewmeta import page, view
from zope.app.container.browser.contents import Contents
from zope.app.container.browser.adding import Adding
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.security.fields import Permission

class IContainerViews(Interface):
    """Define several container views for an `IContainer` implementation."""

    for_ = GlobalObject(
        title=u"The interface this containerViews are for.",
        description=u"""
        The containerViews will be for all objects that implement this
        interface.""",
        required=True
        )
     
    contents = Permission(
        title=u"The permission needed for content page.",
        required=False,
        )

    index = Permission(
        title=u"The permission needed for index page.",
        required=False,
        )

    add = Permission(
        title=u"The permission needed for add page.",
        required=False,
        )


def containerViews(_context, for_, contents=None, add=None, index=None):
    """Create an container view for a given content type"""

    if for_ is None:
            raise ValueError("A for interface must be specified.")

    if contents is not None:
        page(_context, name='contents.html', permission=contents,
             for_=for_, class_=Contents, attribute='contents',
             menu='zmi_views', title=_('Contents'))
            
    if index is not None:
        page(_context, name='index.html', permission=index, for_=for_, 
             class_=Contents, attribute='index')

    if add is not None:
        viewObj = view(_context, name='+', menu='zmi_actions',
                       title=_('Add'), for_=for_, permission=add,
                       class_=Adding)
        viewObj.page(_context, name='index.html', attribute='index')
        viewObj.page(_context, name='action.html', attribute='action')
        viewObj()
