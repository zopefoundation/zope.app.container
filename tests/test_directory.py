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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: test_directory.py,v 1.1 2003/02/03 15:08:31 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
import zope.app.container.directory

class Directory:
    pass
 
class Test(TestCase):

    def test_Cloner(self):
        d = Directory()
        d.a = 1
        clone = zope.app.container.directory.Cloner(d)('foo')
        self.assert_(clone != d)
        self.assertEqual(clone.__class__, d.__class__)

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
