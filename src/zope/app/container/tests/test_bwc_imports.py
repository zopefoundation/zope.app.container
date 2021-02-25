##############################################################################
#
# Copyright (c) 2017 Zope Foundation and Contributors.
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

import unittest


class TestImports(unittest.TestCase):

    def test_traversal_import(self):
        import zope.app.container.traversal as m
        self.assertIn('ContainerTraverser', m.__dict__)

    def test_size_import(self):
        import zope.app.container.size as m
        self.assertIn('ContainerSized', m.__dict__)

    def test_ordered_import(self):
        import zope.app.container.ordered as m
        self.assertIn('OrderedContainer', m.__dict__)

    def test_btree_import(self):
        import zope.app.container.btree as m
        self.assertIn('BTreeContainer', m.__dict__)

    def test_container_import(self):
        import zope.app.container.dependency as m
        self.assertIn('CheckDependency', m.__dict__)

    def test_directory_import(self):
        import zope.app.container.directory as m
        self.assertIn('Cloner', m.__dict__)

    def test_find_import(self):
        import zope.app.container.find as m
        self.assertIn('FindAdapter', m.__dict__)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
