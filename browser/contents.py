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
"""View Class for the Container's Contents view.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app.traversing.interfaces import TraversalError
from zope.security.interfaces import Unauthorized
from zope.security import checkPermission

from zope.app import zapi
from zope.app.size.interfaces import ISized
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser import BrowserView
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.dublincore.interfaces import IDCDescriptiveProperties
from zope.app.copypastemove.interfaces import IPrincipalClipboard
from zope.app.copypastemove.interfaces import IObjectCopier
from zope.app.copypastemove.interfaces import IObjectMover
from zope.app.copypastemove import rename

from zope.app.container.browser.adding import BasicAdding
from zope.app.container.interfaces import IContainer
from zope.app.container.interfaces import IContainerNamesContainer

class Contents(BrowserView):

    __used_for__ = IContainer

    error = ''
    message = ''
    normalButtons = False
    specialButtons = False
    supportsRename = False

    def listContentInfo(self):
        request = self.request

        if  "container_cancel_button" in request:
            if "type_name" in request:
                del request.form['type_name']
            if "rename_ids" in request and "new_value" in request:
                del request.form['rename_ids']
            if "retitle_id" in request and "new_value" in request:
                del request.form['retitle_id']

            return self._normalListContentsInfo()

        elif "container_rename_button" in request and not request.get("ids"):
            self.error = _("You didn't specify any ids to rename.")
        elif "container_add_button" in request:
            if "single_type_name" in request \
                   and "single_new_value" in request:
                request.form['type_name'] = request['single_type_name']
                request.form['new_value'] = request['single_new_value']
                self.addObject()
            elif 'single_type_name' in request \
                     and 'single_new_value' not in request:
                request.form['type_name'] = request['single_type_name']
                request.form['new_value'] = ""
                self.addObject()
        elif "type_name" in request and "new_value" in request:
            self.addObject()
        elif "rename_ids" in request and "new_value" in request:
            self.renameObjects()
        elif "retitle_id" in request and "new_value" in request:
            self.changeTitle()
        elif "container_cut_button" in request:
            self.cutObjects()
        elif "container_copy_button" in request:
            self.copyObjects()
        elif "container_paste_button" in request:
            self.pasteObjects()
        elif "container_delete_button" in request:
            self.removeObjects()
        else:
            return self._normalListContentsInfo()

        if self.error:
            return self._normalListContentsInfo()

        status = request.response.getStatus()
        if status not in (302, 303):
            # Only redirect if nothing else has
            request.response.redirect(request.URL)
        return ()

    def normalListContentInfo(self):
        return self._normalListContentsInfo()

    def _normalListContentsInfo(self):
        request = self.request

        self.specialButtons = (
                 'type_name' in request or
                 'rename_ids' in request or
                 ('container_rename_button' in request
                  and request.get("ids")) or
                 'retitle_id' in request
                 )
        self.normalButtons = not self.specialButtons

        info = map(self._extractContentInfo, self.context.items())

        self.supportsCut = info
        self.supportsCopy = info
        self.supportsDelete = info
        self.supportsPaste = self.pasteable()
        self.supportsRename = (
            self.supportsCut and
            not IContainerNamesContainer.providedBy(self.context)
            )

        return info


    def _extractContentInfo(self, item):
        request = self.request


        rename_ids = {}
        if "container_rename_button" in request:
            for rename_id in request.get('ids', ()):
                rename_ids[rename_id] = rename_id
        elif "rename_ids" in request:
            for rename_id in request.get('rename_ids', ()):
                rename_ids[rename_id] = rename_id


        retitle_id = request.get('retitle_id')

        id, obj = item
        info = {}
        info['id'] = info['cb_id'] = id
        info['object'] = obj

        info['url'] = id
        info['rename'] = rename_ids.get(id)
        info['retitle'] = id == retitle_id


        zmi_icon = zapi.queryView(obj, 'zmi_icon', self.request)
        if zmi_icon is None:
            info['icon'] = None
        else:
            info['icon'] = zmi_icon()

        dc = IZopeDublinCore(obj, None)
        if dc is not None:
            info['retitleable'] = checkPermission(
                'zope.app.dublincore.change', dc) and id != retitle_id
            info['plaintitle'] = 0

            title = self.safe_getattr(dc, 'title', None)
            if title:
                info['title'] = title

            formatter = self.request.locale.dates.getFormatter(
                'dateTime', 'short')

            created = self.safe_getattr(dc, 'created', None)
            if created is not None:
                info['created'] = formatter.format(created)

            modified = self.safe_getattr(dc, 'modified', None)
            if modified is not None:
                info['modified'] = formatter.format(modified)
        else:
            info['retitleable'] = 0
            info['plaintitle'] = 1


        sized_adapter = ISized(obj, None)
        if sized_adapter is not None:
            info['size'] = sized_adapter
        return info

    def safe_getattr(self, obj, attr, default):
        """Attempts to read the attr, returning default if Unauthorized."""
        try:
            return getattr(obj, attr, default)
        except Unauthorized:
            return default

    def renameObjects(self):
        """Given a sequence of tuples of old, new ids we rename"""
        request = self.request
        ids = request.get("rename_ids")
        newids = request.get("new_value")

        for oldid, newid in map(None, ids, newids):
            if newid != oldid:
                rename(self.context, oldid, newid)

    def changeTitle(self):
        """Given a sequence of tuples of old, new ids we rename"""
        request = self.request
        id = request.get("retitle_id")
        new = request.get("new_value")

        item = self.context[id]
        dc = IDCDescriptiveProperties(item)
        dc.title = new

    def addObject(self):
        request = self.request
        if IContainerNamesContainer.providedBy(self.context):
            new = ""
        else:
            new = request["new_value"]

        adding = zapi.queryView(self.context, "+", request)
        if adding is None:
            adding = BasicAdding(self.context, request)
        else:
            # Set up context so that the adding can build a url
            # if the type name names a view.
            # Note that we can't so this for the "adding is None" case
            # above, because there is no "+" view.
            adding.__parent__ = self.context
            adding.__name__ = '+'
             
        adding.action(request['type_name'], new)

    def removeObjects(self):
        """Remove objects specified in a list of object ids"""
        request = self.request
        ids = request.get('ids')
        if not ids:
            self.error = _("You didn't specify any ids to remove.")
            return

        container = self.context
        for id in ids:
            del container[id]

    def copyObjects(self):
        """Copy objects specified in a list of object ids"""
        request = self.request
        ids = request.get('ids')
        if not ids:
            self.error = _("You didn't specify any ids to copy.")
            return

        container_path = zapi.getPath(self.context)

        user = self.request.principal
        annotationsvc = zapi.getService('PrincipalAnnotation')
        annotations = annotationsvc.getAnnotations(user)
        clipboard = IPrincipalClipboard(annotations)
        clipboard.clearContents()
        items = []
        for id in ids:
            items.append(zapi.joinPath(container_path, id))
        clipboard.addItems('copy', items)

    def cutObjects(self):
        """move objects specified in a list of object ids"""
        request = self.request
        ids = request.get('ids')
        if not ids:
            self.error = _("You didn't specify any ids to cut.")
            return

        container_path = zapi.getPath(self.context)

        user = self.request.principal
        annotationsvc = zapi.getService('PrincipalAnnotation')
        annotations = annotationsvc.getAnnotations(user)
        clipboard = IPrincipalClipboard(annotations)
        clipboard.clearContents()
        items = []
        for id in ids:
            items.append(zapi.joinPath(container_path, id))
        clipboard.addItems('cut', items)


    def pasteable(self):
        """Decide if there is anything to paste
        """
        target = self.context
        user = self.request.principal
        annotationsvc = zapi.getService('PrincipalAnnotation')
        annotations = annotationsvc.getAnnotations(user)
        clipboard = IPrincipalClipboard(annotations)
        items = clipboard.getContents()
        for item in items:
            try:
                obj = zapi.traverse(target, item['target'])
            except TraversalError:
                pass
            else:
                if item['action'] == 'cut':
                    mover = IObjectMover(obj)
                    if not mover.moveableTo(target):
                        return False
                elif item['action'] == 'copy':
                    copier = IObjectCopier(obj)
                    if not copier.copyableTo(target):
                        return False
                else:
                    raise

        return True


    def pasteObjects(self):
        """Paste ojects in the user clipboard to the container
        """
        target = self.context
        user = self.request.principal
        annotationsvc = zapi.getService('PrincipalAnnotation')
        annotations = annotationsvc.getAnnotations(user)
        clipboard = IPrincipalClipboard(annotations)
        items = clipboard.getContents()
        moved = False
        for item in items:
            try:
                obj = zapi.traverse(target, item['target'])
            except TraversalError:
                pass
            else:
                if item['action'] == 'cut':
                    mover = IObjectMover(obj)
                    mover.moveTo(target)
                    moved = True
                elif item['action'] == 'copy':
                    copier = IObjectCopier(obj)
                    copier.copyTo(target)
                else:
                    raise

        if moved:
            # Clear the clipboard if we do a move, but not if we only do a copy
            clipboard.clearContents()


    def hasClipboardContents(self):
        """ interogates the `PrinicipalAnnotation` to see if
           clipboard contents exist """

        if not self.supportsPaste:
            return False

        user = self.request.principal

        annotationsvc = zapi.getService('PrincipalAnnotation')
        annotations = annotationsvc.getAnnotations(user)

        # touch at least one item to in clipboard confirm contents
        clipboard = IPrincipalClipboard(annotations)
        items = clipboard.getContents()
        for item in items:
            try:
                zapi.traverse(self.context, item['target'])
            except TraversalError:
                pass
            else:
                return True

        return False

    contents = ViewPageTemplateFile('contents.pt')
    contentsMacros = contents

    _index = ViewPageTemplateFile('index.pt')

    def index(self):
        if 'index.html' in self.context:
            self.request.response.redirect('index.html')
            return ''

        return self._index()

class JustContents(Contents):
    """Like Contents, but does't delegate to item named index.html"""

    def index(self):
        return self._index()
