# -*- coding: utf-8 -*-

from imio.directory.core.testing import IMIO_DIRECTORY_CORE_FUNCTIONAL_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.zope import Browser

import transaction
import unittest


class TestLocalRoles(unittest.TestCase):

    layer = IMIO_DIRECTORY_CORE_FUNCTIONAL_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="Entity",
        )
        self.contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="Contact",
        )

    def test_local_manager_in_sharing(self):
        transaction.commit()
        browser = Browser(self.layer["app"])
        browser.addHeader(
            "Authorization",
            "Basic %s:%s"
            % (
                TEST_USER_NAME,
                TEST_USER_PASSWORD,
            ),
        )
        browser.open("{}/@@sharing".format(self.entity.absolute_url()))
        content = browser.contents
        self.assertIn("Can manage locally", content)

        browser.open("{}/@@sharing".format(self.contact.absolute_url()))
        content = browser.contents
        self.assertNotIn("Can manage locally", content)
