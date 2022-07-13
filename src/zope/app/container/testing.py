from zope.app.wsgi.testlayer import BrowserLayer
from zope.component.testing import PlacelessSetup
from zope.container.interfaces import ISimpleReadContainer
from zope.container.testing import setUp as cSetUp
from zope.container.testing import tearDown as cTearDown
from zope.container.traversal import ContainerTraversable
from zope.site.folder import Folder
from zope.site.folder import rootFolder
from zope.testing.cleanup import tearDown as tTearDown
from zope.traversing.interfaces import ITraversable

import zope.app.container


AppContainerLayer = BrowserLayer(
    zope.app.container,
    allowTearDown=True)


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
    root['folder1'] = Folder()
    root['folder1']['folder1_1'] = Folder()
    root['folder1']['folder1_1']['folder1_1_1'] = Folder()
    root['folder1']['folder1_1']['folder1_1_2'] = Folder()
    root['folder1']['folder1_2'] = Folder()
    root['folder1']['folder1_2']['folder1_2_1'] = Folder()
    root['folder2'] = Folder()
    root['folder2']['folder2_1'] = Folder()
    root['folder2']['folder2_1']['folder2_1_1'] = Folder()
    root["\N{CYRILLIC SMALL LETTER PE}"
         "\N{CYRILLIC SMALL LETTER A}"
         "\N{CYRILLIC SMALL LETTER PE}"
         "\N{CYRILLIC SMALL LETTER KA}"
         "\N{CYRILLIC SMALL LETTER A}3"] = Folder()
    root["\N{CYRILLIC SMALL LETTER PE}"
         "\N{CYRILLIC SMALL LETTER A}"
         "\N{CYRILLIC SMALL LETTER PE}"
         "\N{CYRILLIC SMALL LETTER KA}"
         "\N{CYRILLIC SMALL LETTER A}3"][
        "\N{CYRILLIC SMALL LETTER PE}"
        "\N{CYRILLIC SMALL LETTER A}"
        "\N{CYRILLIC SMALL LETTER PE}"
        "\N{CYRILLIC SMALL LETTER KA}"
        "\N{CYRILLIC SMALL LETTER A}3_1"] = Folder()

    return root


def setUpTraversal():
    from zope.traversing.testing import setUp
    setUp()
    zope.component.provideAdapter(ContainerTraversable,
                                  (ISimpleReadContainer,), ITraversable)


class PlacefulSetup(PlacelessSetup):

    def setUp(self):
        super().setUp()
        cSetUp()
        setUpTraversal()

        from zope.security.management import newInteraction
        newInteraction()

    def tearDown(self):
        super().tearDown()
        cTearDown()
        tTearDown()

    def buildFolders(self):
        self.rootFolder = buildSampleFolderTree()
