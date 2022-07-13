#

import unittest

from webtest import TestApp
from zope.principalannotation.interfaces import IPrincipalAnnotationUtility
from zope.principalannotation.utility import PrincipalAnnotationUtility

from zope import component


def provideAdapter(required, provided, factory):
    gsm = component.getGlobalSiteManager()
    gsm.registerAdapter(factory, [required], provided, event=False)


class BrowserTestCase(unittest.TestCase):

    def getRootFolder(self):
        return self.layer.getRootFolder()

    def setUp(self):
        super().setUp()
        self._testapp = TestApp(self.layer.make_wsgi_app())
        # Typically this would be done by zope.app.principalannotation's
        # bootstrap.zcml but we don't have a dep on that.
        component.getGlobalSiteManager().registerUtility(
            PrincipalAnnotationUtility(), IPrincipalAnnotationUtility)

    def publish(self, path, basic=None, form=None, headers=None):
        if basic:
            self._testapp.authorization = ('Basic', tuple(basic.split(':')))
        else:
            self._testapp.authorization = None
        env = {'wsgi.handleErrors': False}
        if form:
            response = self._testapp.post(path, params=form,
                                          extra_environ=env, headers=headers)
        else:
            response = self._testapp.get(
                path, extra_environ=env, headers=headers)
        return response
