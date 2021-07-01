# -*- coding: utf-8 -*-

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import imio.directory.core


class ImioDirectoryCoreLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity

        z2.installProduct(app, "plone.restapi")
        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=imio.directory.core)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "imio.directory.core:testing")


IMIO_DIRECTORY_CORE_FIXTURE = ImioDirectoryCoreLayer()


IMIO_DIRECTORY_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(IMIO_DIRECTORY_CORE_FIXTURE,),
    name="ImioDirectoryCoreLayer:IntegrationTesting",
)

IMIO_DIRECTORY_CORE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(
        IMIO_DIRECTORY_CORE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="ImioDirectoryCoreLayer:FunctionalTesting",
)


IMIO_DIRECTORY_CORE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        IMIO_DIRECTORY_CORE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="ImioDirectoryCoreLayer:AcceptanceTesting",
)
