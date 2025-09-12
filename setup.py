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

"""
import os

from setuptools import setup


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()


version = '6.0'

setup(name='zope.app.container',
      version=version,
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.dev',
      description='Zope Container',
      long_description=(
          read('README.rst')
          + '\n\n' +
          read('CHANGES.rst')
      ),
      keywords="zope3 container",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3.13',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope :: 3',
      ],
      url='http://github.com/zopefoundation/zope.app.container',
      license='ZPL-2.1',
      python_requires='>=3.9',
      extras_require={
          'test': [
              'zope.app.appsetup',
              'zope.app.basicskin >= 4.0',
              'zope.app.content',
              'zope.app.dependable >= 4.0',
              'zope.app.http',
              'zope.app.pagetemplate >= 4.0',
              'zope.app.principalannotation',
              'zope.app.publication',
              'zope.app.publisher',
              'zope.app.security',
              'zope.app.testing',
              'zope.app.wsgi',

              'zope.applicationcontrol',
              'zope.browser',
              'zope.browserresource',
              'zope.copypastemove',
              'zope.login',
              'zope.password',
              'zope.principalannotation',
              'zope.principalregistry',
              'zope.proxy >= 4.2.1',
              'zope.securitypolicy',
              'zope.site',
              'zope.testbrowser>5',
              'zope.testing',
              'zope.testrunner >= 6.4',
          ]},
      install_requires=[
          'setuptools',
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
          'zope.publisher >= 4.3.1',
          'zope.security >= 4.1.0',
          'zope.size',
          'zope.traversing',
      ],
      include_package_data=True,
      zip_safe=False,
      )
