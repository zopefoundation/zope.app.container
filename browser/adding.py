##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Adding View

The Adding View is used to add new objects to a container. It is sort of a
factory screen.

$Id: adding.py,v 1.1 2004/03/14 02:17:02 srichter Exp $
"""
__metaclass__ = type

import zope.security.checker
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.proxy import removeAllProxies
from zope.component.interfaces import IFactory

from zope.app.interfaces.exceptions import UserError
from zope.app.container.interfaces import IAdding
from zope.app.container.interfaces import IContainerNamesContainer
from zope.app.container.interfaces import INameChooser

from zope.app import zapi
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.event import publish
from zope.app.publisher.browser import BrowserView

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.i18n import translate
from zope.app.location import LocationProxy
from zope.app.container.constraints import checkFactory


class BasicAdding(BrowserView):
    implements(IAdding, IPublishTraverse)

    def add(self, content):
        """See zope.app.container.interfaces.IAdding
        """
        container = self.context
        name = self.contentName
        chooser = INameChooser(container)

        if IContainerNamesContainer.providedBy(container):
            # The container pick's it's own names.
            # We need to ask it to pick one.
            name = chooser.chooseName(self.contentName or '', content)
        else:
            request = self.request
            name = request.get('add_input_name', name)

            if name is None:
                name = chooser.chooseName(self.contentName or '', content)
            elif name == '':
                name = chooser.chooseName('', content)
            chooser.checkName(name, container)

        container[name] = content
        self.contentName = name # Set the added object Name
        return container[name]

    contentName = None # usually set by Adding traverser

    def nextURL(self):
        """See zope.app.container.interfaces.IAdding"""
        return (str(zapi.getView(self.context, "absolute_url", self.request))
                + '/@@contents.html')

    request = None # set in BrowserView.__init__

    context = None # set in BrowserView.__init__


    def renderAddButton(self):
        """To Render Add button with or without Inputbox"""
        container = self.context
        add_button_value = _('add-button', 'Add')
        add_button_label = _('add-button-label','Object Name')
        
        add_button_value = translate(self.context, add_button_value,
                                     context=self.request)
        add_button_label = translate(self.context, add_button_label,
                                     context=self.request)
        if IContainerNamesContainer.providedBy(container):
            return " <input type='submit' name='UPDATE_SUBMIT' value='%s'>" \
                   % add_button_value
        else:
            contentName = self.contentName or ''
            return (
               "&nbsp;&nbsp;<input type='submit' name='UPDATE_SUBMIT' value='%s'>"
               "&nbsp;&nbsp;<b>%s:</b>&nbsp;"
               "<input type='text' name='add_input_name' value='%s'>"
                    % (add_button_value, add_button_label, contentName))

    def publishTraverse(self, request, name):
        """See zope.app.container.interfaces.IAdding"""
        if '=' in name:
            view_name, content_name = name.split("=", 1)
            self.contentName = content_name

            if view_name.startswith('@@'):
                view_name = view_name[2:]
            return zapi.getView(self, view_name, request)

        if name.startswith('@@'):
            view_name = name[2:]
        else:
            view_name = name

        view = zapi.queryView(self, view_name, request)
        if view is not None:
            return view

        factory = zapi.queryFactory(self.context, name)
        if factory is None:
            return super(BasicAdding, self).publishTraverse(request, name)

        return factory

    def action(self, type_name='', id=''):
        if not type_name:
            raise UserError(_(u"You must select the type of object to add."))

        if type_name.startswith('@@'):
            type_name = type_name[2:]

        if '/' in type_name:
            view_name  = type_name.split('/', 1)[0]
        else:
            view_name = type_name

        if zapi.queryView(self, view_name, self.request) is not None:
            url = "%s/%s=%s" % (
                zapi.getView(self, "absolute_url", self.request),
                type_name, id)
            self.request.response.redirect(url)
            return

        if not self.contentName:
            self.contentName = id

        # XXX: If the factory wrapped by LocationProxy is already a Proxy,
        #      then ProxyFactory does not the right thing and the original's
        #      checker info gets lost. No factory that was registered via ZCML
        #      and was used via addMenuItem worked here. (SR)
        factory = zapi.getUtility(self, IFactory, type_name)
        if not type(factory) is zope.security.checker.Proxy:
            factory = LocationProxy(factory, self, type_name)
            factory = zope.security.checker.ProxyFactory(factory)
        content = factory()

        # Can't store security proxies.
        # Note that it is important to do this here, rather than
        # in add, otherwise, someone might be able to trick add
        # into unproxying an existing object,
        content = removeAllProxies(content)

        publish(self.context, ObjectCreatedEvent(content))

        self.add(content)
        self.request.response.redirect(self.nextURL())

    def namesAccepted(self):
        return not IContainerNamesContainer.providedBy(self.context)

class Adding(BasicAdding):

    menu_id = None

    index = ViewPageTemplateFile("add.pt")

    def addingInfo(self):
        """Return menu data.

        This is sorted by title.
        """
        container = self.context
        menu_service = zapi.getService(container, "BrowserMenu")
        result = []
        for menu_id in (self.menu_id, 'zope.app.container.add'):
            if not menu_id:
                continue
            for item in menu_service.getMenu(menu_id, self, self.request):
                extra = item.get('extra')
                if extra:
                    factory = extra.get('factory')
                    if factory:
                        factory = zapi.getUtility(container, IFactory, factory)
                        if not checkFactory(container, None, factory):
                            continue
                        elif item['extra']['factory'] != item['action']:
                            item['has_custom_add_view']=True
                result.append(item)

        result.sort(lambda a, b: cmp(a['title'], b['title']))
        return result

    def isSingleMenuItem(self):
        "Return whether there is single menu item or not."
        return len(self.addingInfo()) == 1

    def hasCustomAddView(self):
       "This should be called only if there is singleMenuItem else return 0"
       if self.isSingleMenuItem():
           menu_item = self.addingInfo()[0]
           if 'has_custom_add_view' in menu_item:
               return True
       return False

class ContentAdding(Adding):

    menu_id = "add_content"
