##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Test the OrderedContainer.


$Id: test_ordered.py,v 1.2 2003/06/23 22:46:15 chrism Exp $
"""

import unittest
from zope.interface import *
from zope.testing.doctestunit import DocTestSuite
from zope.interface import Interface

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(DocTestSuite("zope.app.container.ordered"))

    return suite

if __name__ == '__main__':
    unittest.main()
