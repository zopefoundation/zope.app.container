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
"""'containerView' directive test
"""
import doctest
import pprint
import re
from io import StringIO

from zope.component.interface import provideInterface
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest


atre = re.compile(' at [0-9a-fA-Fx]+')


class Context:
    info = ''

    def __init__(self):
        self.actions = []

    def action(self, discriminator, callable, args):
        if discriminator is None:
            if callable is provideInterface:
                self.actions.append((callable, args[1]))  # name is args[0]
        else:
            self.actions.append(discriminator)
        self.info = 'info'

    def __repr__(self):
        stream = StringIO()
        pprinter = pprint.PrettyPrinter(stream=stream, width=60)
        pprinter.pprint(self.actions)
        r = stream.getvalue()
        return (''.join(atre.split(r))).strip()


class Iface(Interface):
    pass


class ITestLayer(IBrowserRequest):
    pass


def test_containerViews():
    """
    >>> from zope.browsermenu.metaconfigure import menus
    >>> from zope.interface.interface import InterfaceClass
    >>> from zope.app.container.browser.metaconfigure import containerViews
    >>> zmi_views = InterfaceClass('zmi_views', __module__='zope.app.menus')
    >>> menus.zmi_views = zmi_views
    >>> zmi_actions = InterfaceClass('zmi_actions', __module__='zope.app.menus')
    >>> menus.zmi_actions = zmi_actions

    >>> context = Context()
    >>> containerViews(context, for_=Iface, contents='zope.ManageContent',
    ...                add='zope.ManageContent', index='zope.View')
    >>> context
    [('adapter',
      (<InterfaceClass zope.app.container.browser.tests.test_directive.Iface>,
       <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>),
      <InterfaceClass zope.app.menus.zmi_views>,
      'Contents'),
     (<function provideInterface>,
      <InterfaceClass zope.app.menus.zmi_views>),
     (<function provideInterface>,
      <InterfaceClass zope.app.container.browser.tests.test_directive.Iface>),
     (<function provideInterface>,
      <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>),
     (<function provideInterface>,
      <InterfaceClass zope.app.container.browser.tests.test_directive.Iface>),
     ('view',
      (<InterfaceClass zope.app.container.browser.tests.test_directive.Iface>,
       <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>),
      'contents.html',
      <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>),
     (<function provideInterface>,
      <InterfaceClass zope.app.container.browser.tests.test_directive.Iface>),
     ('view',
      (<InterfaceClass zope.app.container.browser.tests.test_directive.Iface>,
       <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>),
      'index.html',
      <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>),
     ('adapter',
      (<InterfaceClass zope.app.container.browser.tests.test_directive.Iface>,
       <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>),
      <InterfaceClass zope.app.menus.zmi_actions>,
      'Add'),
     (<function provideInterface>,
      <InterfaceClass zope.app.menus.zmi_actions>),
     (<function provideInterface>,
      <InterfaceClass zope.app.container.browser.tests.test_directive.Iface>),
     (<function provideInterface>,
      <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>),
     (<function provideInterface>,
      <InterfaceClass zope.app.container.browser.tests.test_directive.Iface>),
     (<function provideInterface>,
      <InterfaceClass zope.interface.Interface>),
     ('view',
      (<InterfaceClass zope.app.container.browser.tests.test_directive.Iface>,
       <InterfaceClass zope.publisher.interfaces.browser.IDefaultBrowserLayer>),
      '+',
      <InterfaceClass zope.interface.Interface>)]
    """  # noqa: E501 line too long


def test_containerViews_layer():
    """
    >>> from zope.browsermenu.metaconfigure import menus
    >>> from zope.interface.interface import InterfaceClass
    >>> from zope.app.container.browser.metaconfigure import containerViews
    >>> zmi_views = InterfaceClass('zmi_views', __module__='zope.app.menus')
    >>> menus.zmi_views = zmi_views
    >>> zmi_actions = InterfaceClass('zmi_actions', __module__='zope.app.menus')
    >>> menus.zmi_actions = zmi_actions

    >>> context = Context()
    >>> containerViews(context, for_=Iface, contents='zope.ManageContent',
    ...                add='zope.ManageContent', index='zope.View', layer=ITestLayer)
    >>> context
    [('adapter',
      (<InterfaceClass zope.app.container.browser.tests.test_directive.Iface>,
       <InterfaceClass zope.app.container.browser.tests.test_directive.ITestLayer>),
      <InterfaceClass zope.app.menus.zmi_views>,
      'Contents'),
     (<function provideInterface>,
      <InterfaceClass zope.app.menus.zmi_views>),
     (<function provideInterface>,
      <InterfaceClass zope.app.container.browser.tests.test_directive.Iface>),
     (<function provideInterface>,
      <InterfaceClass zope.app.container.browser.tests.test_directive.ITestLayer>),
     (<function provideInterface>,
      <InterfaceClass zope.app.container.browser.tests.test_directive.Iface>),
     ('view',
      (<InterfaceClass zope.app.container.browser.tests.test_directive.Iface>,
       <InterfaceClass zope.app.container.browser.tests.test_directive.ITestLayer>),
      'contents.html',
      <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>),
     (<function provideInterface>,
      <InterfaceClass zope.app.container.browser.tests.test_directive.Iface>),
     ('view',
      (<InterfaceClass zope.app.container.browser.tests.test_directive.Iface>,
       <InterfaceClass zope.app.container.browser.tests.test_directive.ITestLayer>),
      'index.html',
      <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>),
     ('adapter',
      (<InterfaceClass zope.app.container.browser.tests.test_directive.Iface>,
       <InterfaceClass zope.app.container.browser.tests.test_directive.ITestLayer>),
      <InterfaceClass zope.app.menus.zmi_actions>,
      'Add'),
     (<function provideInterface>,
      <InterfaceClass zope.app.menus.zmi_actions>),
     (<function provideInterface>,
      <InterfaceClass zope.app.container.browser.tests.test_directive.Iface>),
     (<function provideInterface>,
      <InterfaceClass zope.app.container.browser.tests.test_directive.ITestLayer>),
     (<function provideInterface>,
      <InterfaceClass zope.app.container.browser.tests.test_directive.Iface>),
     (<function provideInterface>,
      <InterfaceClass zope.interface.Interface>),
     ('view',
      (<InterfaceClass zope.app.container.browser.tests.test_directive.Iface>,
       <InterfaceClass zope.app.container.browser.tests.test_directive.ITestLayer>),
      '+',
      <InterfaceClass zope.interface.Interface>)]
    """  # noqa: E501 line too long


def test_suite():
    return doctest.DocTestSuite()
