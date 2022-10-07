# -*- coding: utf-8 -*-

from imio.directory.core.testing import IMIO_DIRECTORY_CORE_FUNCTIONAL_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import RelativeSession
from zope.component import getMultiAdapter

import transaction
import unittest


class TestContact(unittest.TestCase):

    layer = IMIO_DIRECTORY_CORE_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.authorized_types_in_contact = ["imio.directory.Contact", "File", "Image"]
        self.unauthorized_types_in_contact = ["Folder", "Page", "Link"]

        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="Entity",
        )

    def tearDown(self):
        self.api_session.close()

    def test_create_multilingual_contact(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="Mon contact que je vais tester en plusieurs langues",
        )
        catalog = api.portal.get_tool("portal_catalog")
        brain = api.content.find(UID=contact.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertFalse(indexes.get("translated_in_nl"))
        self.assertFalse(indexes.get("translated_in_de"))
        self.assertFalse(indexes.get("translated_in_en"))

        contact.title_en = "My contact that I will test in several languages"
        contact.reindexObject()
        transaction.commit()
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertFalse(indexes.get("translated_in_nl"))
        self.assertFalse(indexes.get("translated_in_de"))
        self.assertTrue(indexes.get("translated_in_en"))

        contact.title_nl = (
            "Mijn contactpersoon die ik in verschillende talen zal testen"
        )
        contact.title_de = "Mein Kontakt, den ich in mehreren Sprachen testen werde"
        contact.reindexObject()
        transaction.commit()
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertTrue(indexes.get("translated_in_nl"))
        self.assertTrue(indexes.get("translated_in_de"))
        self.assertTrue(indexes.get("translated_in_en"))

        view = getMultiAdapter((contact, self.request), name="view")
        view.update()
        self.assertIn(
            "Mon contact que je vais tester en plusieurs langues", view.render()
        )
        self.assertIn("My contact that I will test in several languages", view.render())
        self.assertIn(
            "Mijn contactpersoon die ik in verschillende talen zal testen",
            view.render(),
        )
        self.assertIn(
            "Mein Kontakt, den ich in mehreren Sprachen testen werde", view.render()
        )

        contact.title_en = None
        contact.reindexObject()
        transaction.commit()
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertFalse(indexes.get("translated_in_en"))
        view = getMultiAdapter((contact, self.request), name="view")
        view.update()
        self.assertNotIn(
            "My contact that I will test in several languages", view.render()
        )

    def test_multilingual_searchabletext_contact(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="Mon contact que je vais tester en plusieurs langues",
        )
        contact.title_en = "My contact that I will test in several languages"
        contact.title_nl = (
            "Mijn contactpersoon die ik in verschillende talen zal testen"
        )
        contact.title_de = "Mein Kontakt, den ich in mehreren Sprachen testen werde"
        contact.reindexObject()
        transaction.commit()
        catalog = api.portal.get_tool("portal_catalog")
        brain = api.content.find(UID=contact.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertIn("several", indexes.get("SearchableText"))
        self.assertIn("verschillende", indexes.get("SearchableText"))

        contact.title_en = None
        contact.reindexObject()
        transaction.commit()
        catalog = api.portal.get_tool("portal_catalog")
        brain = api.content.find(UID=contact.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertNotIn("several", indexes.get("SearchableText"))
