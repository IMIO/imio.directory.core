# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from imio.directory.core.testing import IMIO_DIRECTORY_CORE_FUNCTIONAL_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser
import transaction
import unittest


class FormsFunctionalTest(unittest.TestCase):

    layer = IMIO_DIRECTORY_CORE_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_leadimage_caption_field(self):
        entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="Entity",
        )
        self.check_leadimage_caption_field(entity, container=self.portal)
        contact = api.content.create(
            container=entity,
            type="imio.directory.Contact",
            title="Contact",
        )
        self.check_leadimage_caption_field(contact, container=entity)

    def check_leadimage_caption_field(self, obj, container):
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
        browser.open("{}/edit".format(obj.absolute_url()))
        content = browser.contents
        soup = BeautifulSoup(content)
        lead_image_caption_widget = soup.find(
            id="form-widgets-ILeadImageBehavior-image_caption"
        )
        self.assertIsNotNone(lead_image_caption_widget)
        self.assertEqual(len(lead_image_caption_widget), 0)
        self.assertEqual(lead_image_caption_widget["type"], "hidden")

        browser.open("{}/++add++{}".format(container.absolute_url(), obj.portal_type))
        content = browser.contents
        soup = BeautifulSoup(content)
        lead_image_caption_widget = soup.find(
            id="form-widgets-ILeadImageBehavior-image_caption"
        )
        self.assertIsNotNone(lead_image_caption_widget)
        self.assertEqual(len(lead_image_caption_widget), 0)
        self.assertEqual(lead_image_caption_widget["type"], "hidden")
