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
"""Test the OrderedContainer.

$Id$
"""
import unittest

from zope.testing.doctestunit import DocTestSuite
from zope.interface import Interface
from zope.app.testing import placelesssetup

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(DocTestSuite("zope.app.container.ordered",
                               setUp=placelesssetup.setUp,
                               tearDown=placelesssetup.tearDown))

    return suite

if __name__ == '__main__':
    unittest.main()
