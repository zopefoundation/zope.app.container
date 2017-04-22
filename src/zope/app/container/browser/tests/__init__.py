#

import unittest

from webtest import TestApp

from zope import component

from zope.security.interfaces import ForbiddenAttribute
from zope.security.proxy import Proxy
from zope.security.checker import Checker, CheckerPublic

def provideAdapter(required, provided, factory):
    gsm = component.getGlobalSiteManager()
    gsm.registerAdapter(factory, [required], provided, event=False)


class BrowserTestCase(unittest.TestCase):

    def getRootFolder(self):
        return self.layer.getRootFolder()

    def setUp(self):
        super(BrowserTestCase, self).setUp()
        self._testapp = TestApp(self.layer.make_wsgi_app())
        # Typically this would be done by zope.app.principalannotation's
        # bootstrap.zcml but we don't have a dep on that.
        from zope.principalannotation.utility import PrincipalAnnotationUtility
        from zope.principalannotation.interfaces import IPrincipalAnnotationUtility
        component.getGlobalSiteManager().registerUtility(PrincipalAnnotationUtility(),
                                                         IPrincipalAnnotationUtility)

        # Temporarily check for and workaround (if needed) the issue with
        # security checkers of BTreeItems on PyPy.
        # https://github.com/zopefoundation/zope.security/issues/20
        import BTrees
        tree = BTrees.OOBTree.OOBTree()
        tree['a'] = 42

        checker = Checker({'items': CheckerPublic})
        proxy = Proxy(tree, checker)
        items = proxy.items()
        try:
            list(items)
        except ForbiddenAttribute:
            checker = Checker({'__iter__': CheckerPublic})
            import BTrees._base
            BTrees._base._TreeItems.__Security_checker__ = checker
            self.addCleanup(lambda: delattr(BTrees._base._TreeItems, '__Security_checker__'))

    def publish(self, path, basic=None, form=None):
        if basic:
            self._testapp.authorization = ('Basic', tuple(basic.split(':')))
        else:
            self._testapp.authorization = None
        env = {'wsgi.handleErrors': False}
        if form:
            response = self._testapp.post(path, params=form, extra_environ=env)
        else:
            response = self._testapp.get(path, extra_environ=env)
        return response
