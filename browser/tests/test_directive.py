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
"""'containerView' directive test

$Id$
"""
import re
import pprint
import cStringIO

import unittest
from zope.interface import Interface
from zope.testing.doctestunit import DocTestSuite
from zope.app.container.browser.metaconfigure import containerViews

atre = re.compile(' at [0-9a-fA-Fx]+')

class Context(object):
    actions = ()
    
    def action(self, discriminator, callable, args):
        self.actions += ((discriminator, callable, args), )
        self.info = 'info'

    def __repr__(self):
        stream = cStringIO.StringIO()
        pprinter = pprint.PrettyPrinter(stream=stream, width=60)
        pprinter.pprint(self.actions)
        r = stream.getvalue()
        return (''.join(atre.split(r))).strip()

class I(Interface):
    pass

def test_containerViews():
    """
    >>> context = Context()
    >>> containerViews(context, for_=I, contents='zope.ManageContent',
    ...                add='zope.ManageContent', index='zope.View')
    >>> context
    ((('browser:menuItem',
       'zmi_views',
       <InterfaceClass zope.app.container.browser.tests.test_directive.I>,
       u'Contents'),
      <bound method GlobalBrowserMenuService.menuItem of <zope.app.publisher.browser.globalbrowsermenuservice.GlobalBrowserMenuService object>>,
      ('zmi_views',
       <InterfaceClass zope.app.container.browser.tests.test_directive.I>,
       '@@contents.html',
       u'Contents',
       '',
       None,
       'zope.ManageContent',
       None)),
     (None,
      <function provideInterface>,
      ('',
       <InterfaceClass zope.app.container.browser.tests.test_directive.I>)),
     (('view',
       <InterfaceClass zope.app.container.browser.tests.test_directive.I>,
       'contents.html',
       <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>,
       'default'),
      <function handler>,
      ('Presentation',
       'provideAdapter',
       <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>,
       <class 'zope.app.publisher.browser.viewmeta.Contents'>,
       'contents.html',
       [<InterfaceClass zope.app.container.browser.tests.test_directive.I>],
       <InterfaceClass zope.interface.Interface>,
       'default',
       'info')),
     (None,
      <function provideInterface>,
      ('',
       <InterfaceClass zope.app.container.browser.tests.test_directive.I>)),
     (('view',
       <InterfaceClass zope.app.container.browser.tests.test_directive.I>,
       'index.html',
       <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>,
       'default'),
      <function handler>,
      ('Presentation',
       'provideAdapter',
       <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>,
       <class 'zope.app.publisher.browser.viewmeta.Contents'>,
       'index.html',
       [<InterfaceClass zope.app.container.browser.tests.test_directive.I>],
       <InterfaceClass zope.interface.Interface>,
       'default',
       'info')),
     (('browser:menuItem',
       'zmi_actions',
       <InterfaceClass zope.app.container.browser.tests.test_directive.I>,
       u'Add'),
      <bound method GlobalBrowserMenuService.menuItem of <zope.app.publisher.browser.globalbrowsermenuservice.GlobalBrowserMenuService object>>,
      ('zmi_actions',
       <InterfaceClass zope.app.container.browser.tests.test_directive.I>,
       '@@+',
       u'Add',
       '',
       None,
       'zope.ManageContent',
       None)),
     (None,
      <function provideInterface>,
      ('',
       <InterfaceClass zope.app.container.browser.tests.test_directive.I>)),
     (None,
      <function provideInterface>,
      ('', <InterfaceClass zope.interface.Interface>)),
     (('view',
       <InterfaceClass zope.app.container.browser.tests.test_directive.I>,
       '+',
       <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>,
       'default',
       <InterfaceClass zope.interface.Interface>),
      <function handler>,
      ('Presentation',
       'provideAdapter',
       <InterfaceClass zope.publisher.interfaces.browser.IBrowserRequest>,
       <class 'zope.app.publisher.browser.viewmeta.+'>,
       '+',
       [<InterfaceClass zope.app.container.browser.tests.test_directive.I>],
       <InterfaceClass zope.interface.Interface>,
       'default',
       'info')))
    """
    
       
def test_suite():
    return unittest.TestSuite((
        DocTestSuite(),
        ))

if __name__ == '__main__':
    unittest.main()
