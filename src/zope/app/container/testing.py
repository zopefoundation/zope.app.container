from zope.component.testing import PlacelessSetup

from zope.container.testing import setUp as cSetUp, tearDown as cTearDown

try:
    from zope.testing.cleanup import tearDown as tTearDown
except ImportError:
    def tTearDown():
        pass

from zope.traversing.api import traverse

from zope.app.wsgi.testlayer import BrowserLayer

import zope.app.container

AppContainerLayer = BrowserLayer(
    zope.app.container,
    allowTearDown=True)

from zope.site.folder import Folder, rootFolder
def buildSampleFolderTree():
    # set up a reasonably complex folder structure
    #
    #     ____________ rootFolder ______________________________
    #    /                                    \                 \
    # folder1 __________________            folder2           folder3
    #   |                       \             |                 |
    # folder1_1 ____           folder1_2    folder2_1         folder3_1
    #   |           \            |            |
    # folder1_1_1 folder1_1_2  folder1_2_1  folder2_1_1

    root = rootFolder()
    root[u'folder1'] = Folder()
    root[u'folder1'][u'folder1_1'] = Folder()
    root[u'folder1'][u'folder1_1'][u'folder1_1_1'] = Folder()
    root[u'folder1'][u'folder1_1'][u'folder1_1_2'] = Folder()
    root[u'folder1'][u'folder1_2'] = Folder()
    root[u'folder1'][u'folder1_2'][u'folder1_2_1'] = Folder()
    root[u'folder2'] = Folder()
    root[u'folder2'][u'folder2_1'] = Folder()
    root[u'folder2'][u'folder2_1'][u'folder2_1_1'] = Folder()
    root[u"\N{CYRILLIC SMALL LETTER PE}"
         u"\N{CYRILLIC SMALL LETTER A}"
         u"\N{CYRILLIC SMALL LETTER PE}"
         u"\N{CYRILLIC SMALL LETTER KA}"
         u"\N{CYRILLIC SMALL LETTER A}3"] = Folder()
    root[u"\N{CYRILLIC SMALL LETTER PE}"
         u"\N{CYRILLIC SMALL LETTER A}"
         u"\N{CYRILLIC SMALL LETTER PE}"
         u"\N{CYRILLIC SMALL LETTER KA}"
         u"\N{CYRILLIC SMALL LETTER A}3"][
         u"\N{CYRILLIC SMALL LETTER PE}"
         u"\N{CYRILLIC SMALL LETTER A}"
         u"\N{CYRILLIC SMALL LETTER PE}"
         u"\N{CYRILLIC SMALL LETTER KA}"
         u"\N{CYRILLIC SMALL LETTER A}3_1"] = Folder()

    return root

from zope.traversing.interfaces import ITraversable
from zope.container.interfaces import ISimpleReadContainer
from zope.container.traversal import ContainerTraversable
def setUpTraversal():
    from zope.traversing.testing import setUp
    setUp()
    zope.component.provideAdapter(ContainerTraversable,
                                  (ISimpleReadContainer,), ITraversable)


class Place(object):

    def __init__(self, path):
        self.path = path

    def __get__(self, inst, cls=None):
        if inst is None:
            return self

        try:
            # Use __dict__ directly to avoid infinite recursion
            root = inst.__dict__['rootFolder']
        except KeyError:
            root = inst.rootFolder = buildSampleFolderTree()

        return traverse(root, self.path)


class PlacefulSetup(PlacelessSetup):

    # Places :)
    rootFolder  = Place(u'')

    folder1     = Place(u'folder1')
    folder1_1   = Place(u'folder1/folder1_1')
    folder1_1_1 = Place(u'folder1/folder1_1/folder1_1_1')
    folder1_1_2 = Place(u'folder1/folder1_2/folder1_1_2')
    folder1_2   = Place(u'folder1/folder1_2')
    folder1_2_1 = Place(u'folder1/folder1_2/folder1_2_1')

    folder2     = Place(u'folder2')
    folder2_1   = Place(u'folder2/folder2_1')
    folder2_1_1 = Place(u'folder2/folder2_1/folder2_1_1')

    folder3     = Place(u"\N{CYRILLIC SMALL LETTER PE}"
                        u"\N{CYRILLIC SMALL LETTER A}"
                        u"\N{CYRILLIC SMALL LETTER PE}"
                        u"\N{CYRILLIC SMALL LETTER KA}"
                        u"\N{CYRILLIC SMALL LETTER A}3")
    folder3_1   = Place(u"\N{CYRILLIC SMALL LETTER PE}"
                        u"\N{CYRILLIC SMALL LETTER A}"
                        u"\N{CYRILLIC SMALL LETTER PE}"
                        u"\N{CYRILLIC SMALL LETTER KA}"
                        u"\N{CYRILLIC SMALL LETTER A}3/"
                        u"\N{CYRILLIC SMALL LETTER PE}"
                        u"\N{CYRILLIC SMALL LETTER A}"
                        u"\N{CYRILLIC SMALL LETTER PE}"
                        u"\N{CYRILLIC SMALL LETTER KA}"
                        u"\N{CYRILLIC SMALL LETTER A}3_1")

    def setUp(self, folders=False, site=False):
        super(PlacefulSetup, self).setUp()
        cSetUp()
        setUpTraversal()
        if folders or site:
            return self.buildFolders(site)

        from zope.security.management import newInteraction
        newInteraction()

    def tearDown(self):
        super(PlacefulSetup, self).tearDown()
        cTearDown()
        tTearDown()

    def buildFolders(self, site=False):
        self.rootFolder = buildSampleFolderTree()
        if site:
            return self.makeSite()

    def makeSite(self, path='/'):
        folder = traverse(self.rootFolder, path)
        return setup.createSiteManager(folder, True)

    def createRootFolder(self):
        self.rootFolder = zope.site.folder.rootFolder()
