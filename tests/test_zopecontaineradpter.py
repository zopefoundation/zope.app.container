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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: test_zopecontaineradpter.py,v 1.2 2002/12/25 14:12:47 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.interfaces.container import IAddNotifiable
from zope.app.interfaces.container import IDeleteNotifiable
from zope.app.container.tests.baseizopeitemcontainer \
     import BaseTestIZopeItemContainer, BaseTestIZopeSimpleReadContainer,\
            BaseTestIZopeReadContainer, BaseTestIZopeWriteContainer
from zope.app.traversing import getParent
from zope.proxy.context import ContextWrapper
from zope.app.tests.placelesssetup import PlacelessSetup
class C: pass

class H:
    __implements__ = IAddNotifiable, IDeleteNotifiable
    notified = 0
    def manage_beforeDelete(self, object, container):
        self.notified -= 1


    def manage_afterAdd(self, object, container):
        self.notified += 1

class Test(PlacelessSetup,
           BaseTestIZopeSimpleReadContainer,
           BaseTestIZopeReadContainer,
           BaseTestIZopeWriteContainer,
           TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        from zope.app.container.sample import SampleContainer
        self.__container = SampleContainer()

    def _sampleMapping(self):
        from zope.app.container.zopecontainer \
            import ZopeContainerAdapter
        container = self.__container
        for k, v in self._sampleDict().items():
            container.setObject(k, v)
        return ZopeContainerAdapter(container)

    def _sampleContainer(self):
        return self.__container

    __sample = {'Z': C(), 'O': C(),'P': C()}
    def _sampleDict(self):
        return self.__sample


    def _absentKeys(self):
        return 'zc', 'ny'

    __newItem = {'A': C(), 'B':C()}
    def _sample_newItem(self):
        return self.__newItem

    __newItemHooked = {'B': H(), 'E':H()}
    def _sample_newItemHooked(self):
        return self.__newItemHooked



def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
