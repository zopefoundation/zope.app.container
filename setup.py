##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Setup for zope.app.container package

$Id$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.container',
      version='3.9.2',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Zope Container',
      long_description=(
          read('README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 container",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://cheeseshop.python.org/pypi/zope.app.container',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],

      extras_require=dict(test=['zope.app.testing',
                                'zope.app.zcmlfiles',
                                'zope.login',
                                'zope.password',
                                'zope.securitypolicy',
                                'zope.schema',
                                'zope.site',
                                ]),
      install_requires=['setuptools',
                        'zope.browser',
                        'zope.browsermenu',
                        'zope.browserpage',
                        'zope.component',
                        'zope.container',
                        'zope.copypastemove',
                        'zope.dublincore >= 3.7',
                        'zope.event',
                        'zope.exceptions',
                        'zope.i18n',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.lifecycleevent',
                        'zope.location',
                        'zope.publisher >= 3.12',
                        'zope.security',
                        'zope.size',
                        'zope.traversing',
                        ],
      include_package_data = True,
      zip_safe = False,
      )

