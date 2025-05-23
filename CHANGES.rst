=======
CHANGES
=======

5.1 (unreleased)
----------------

- Add support for Python 3.12, 3.13.

- Drop support for Python 3.7, 3.8.


5.0 (2023-02-08)
----------------

- Drop support for Python 2.7, 3.4, 3.5, 3.6.

- Add support for Python 3.7, 3.8, 3.9, 3.10, 3.11.

- Fix deprecation warnings.


4.0.0 (2017-04-24)
------------------

- Added support for PyPy and Python 3.4, 3.5 and 3.6.

3.9.2 (2012-01-23)
------------------

- Replaced an undeclared test dependency on ``zope.app.authentication`` with
  ``zope.password``.

- Removed undeclared test dependency on ``zope.app.folder``.

- Replaced the use of ``zope.app.pagetemplate`` and deprecated
  ``zope.app.publisher`` with ``zope.browserpage`` and ``zope.browsermenu``.


3.9.1 (2010-09-14)
------------------

- Removed a testing dependency on ``zope.app.file``.

- Replaced a testing dependency on ``zope.app.securitypolicy`` with the base
  ``zope.securitypolicy`` distribution.


3.9.0 (2010-08-19)
------------------

- Updated ``ftesting.zcml`` to use the new permission names exported by
  ``zope.dublincore`` 3.7.


3.8.2 (2010-01-08)
------------------

- Fixed tests using a newer zope.publisher that requires zope.login.

3.8.1 (2009-12-26)
------------------

- Fixed test_directive. Some parts of zope.app.publisher were moved
  to zope.browsermenu and zope.browserpage.

- Moved tests/test_view_permissions.py to browser/tests.

- Added undeclared install dependency on ``zope.app.publisher``.

- Test no longer use deprecated ``zope.testing.doctestunit`` but
  python's ``doctest`` instead.


3.8.0 (2009-05-13)
------------------

- Moved ``IAdding`` interface to ``zope.browser.interfaces``, leaving
  BBB imports.

3.7.2 (2009-03-12)
------------------

- Show a "nothing to add" message instead of empty list in the
  adding view, if there's nothing to add.

- Don't show the "Add" menu item if there's nothing to add.

- Adapt to the removal of deprecated interfaces from
  ``zope.component.interfaces``. Now ``IAdding`` inherits from
  ``zope.publisher.interfaces.browser.IBrowserView``.

3.7.1 (2009-02-05)
-------------------

- Updated test to accomodate "Pythonic" exception now raised from
  ``__setitem__`` provided by ``zope.container`` (``KeyError`` instead
  of ``zope.exceptions.UserError``).

3.7.0 (2009-01-31)
------------------

- Remove long-time deprecated ``IContentContainer`` class.

- We now rely on a new package called ``zope.container``, which
  contains the basic implementation of ``zope.container`` and is
  intended to have less dependencies. We have gone through a wide
  range of packages and updated their dependencies to point to
  ``zope.container`` so that they will also have less indirect
  dependencies.

  For backwards compatibility we have left the original modules in
  ``zope.app.container`` in place and have placed imports to make sure
  the symbols exist in their original locations.

3.6.2 (2008-10-21)
------------------

- Fixed bug in ``_zope_app_container_contained.c``.

3.6.1 (2008-10-15)
------------------

- Reimplemented the ``BTreeContainer`` so that it directly accesses the btree
  methods (removed an old #TODO)

- Removed usage of deprecated ``LayerField``.

- Made C code compatible with Python 2.5 on 64bit architectures.

- Fixed bug: Error thrown during ``__setitem__`` for an ordered container
  leaves bad key in order

- Fixed https://bugs.launchpad.net/zope3/+bug/238579,
  https://bugs.launchpad.net/zope3/+bug/163149: Error with unicode
  traversing

- Fixed https://bugs.launchpad.net/zope3/+bug/221025: The Adding menu
  is sorted with translated item by using a collator (better localized
  sorting)

- Fixed https://bugs.launchpad.net/zope3/+bug/227617:
    - prevent the namechooser from failing on '+', '@' and '/'
    - added tests in the namechooser
    - be sure the name chooser returns unicode

- Fixed https://bugs.launchpad.net/zope3/+bug/175388: The setitem's
  size modification is now done in ``setitemf``: setting an existing
  item does not change the size, and the event subscribers should see
  the new size instead of the old size.

3.6.0 (2008-05-06)
------------------

- Added an ``IBTreeContainer`` interface that allows an argument to the
  ``items``, ``keys``, and ``values`` methods with the same semantics as for
  a BTree object.  The extended interface is implemented by the
  ``BTreeContainer`` class.

3.5 (2007-10-11)
----------------

- Updated bootstrap script to current version.

- Store length of ``BTreeContainer`` in its own ``Length`` object for faster
  ``__len__`` implementation of huge containers.

- Send ``IObjectModifiedEvent`` when changing the title through the
  ``@@contents.html`` view.
  This fixes https://bugs.edge.launchpad.net/zope3/+bug/98483.

- Resolve ``ZopeSecurityPolicy`` and ``IRolePermissionManager`` deprecation
  warning.

3.4 (2007-04-22)
----------------

- Initial release as a separate project, corresponds to ``zope.app.container``
  from Zope 3.4.0a1.
