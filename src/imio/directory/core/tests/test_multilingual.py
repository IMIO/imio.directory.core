# -*- coding: utf-8 -*-

from imio.directory.core.interfaces import IImioDirectoryCoreLayer
from imio.directory.core.testing import IMIO_DIRECTORY_CORE_FUNCTIONAL_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import transaction
import unittest


class TestMultilingual(unittest.TestCase):

    layer = IMIO_DIRECTORY_CORE_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="Entity",
        )

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
        metadatas = catalog.getMetadataForRID(brain.getRID())
        self.assertEqual(contact.title, metadatas.get("title_fr"))
        self.assertEqual(contact.title_nl, metadatas.get("title_nl"))
        self.assertEqual(contact.title_de, metadatas.get("title_de"))
        self.assertEqual(contact.title_en, metadatas.get("title_en"))

        contact.title_en = None
        contact.reindexObject()
        transaction.commit()
        catalog = api.portal.get_tool("portal_catalog")
        brain = api.content.find(UID=contact.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertNotIn("several", indexes.get("SearchableText"))

    def test_contact_serializer(self):
        alsoProvides(self.request, IImioDirectoryCoreLayer)
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="Mon contact",
        )
        contact.title_en = "My contact"
        contact.title_nl = "Mijn contactpersoon"
        contact.description = "Ma **description**"
        contact.description_en = "My **description**"
        contact.description_nl = "Mijn **beschrijving**"
        contact.subtitle = "Ma fonction"
        contact.subtitle_en = "My function"
        contact.subtitle_nl = "Mijn positie"
        serializer = getMultiAdapter((contact, self.request), ISerializeToJson)
        json = serializer()
        self.assertEqual(json["title"], "Mon contact")
        self.assertEqual(json["description"], "Ma **description**")
        self.assertEqual(json["title_fr"], "Mon contact")
        self.assertEqual(json["description_fr"], "Ma **description**")

        catalog = api.portal.get_tool("portal_catalog")
        brain = catalog(UID=contact.UID())[0]
        serializer = getMultiAdapter((brain, self.request), ISerializeToJsonSummary)
        json_summary = serializer()
        self.assertEqual(json_summary["title"], "Mon contact")
        self.assertEqual(json_summary["description"], "Ma description")

        self.request.form["translated_in_nl"] = True
        serializer = getMultiAdapter((contact, self.request), ISerializeToJson)
        json = serializer()
        self.assertEqual(json["title"], "Mijn contactpersoon")
        self.assertEqual(json["description"], "Mijn **beschrijving**")
        self.assertEqual(json["subtitle"], "Mijn positie")
        self.assertEqual(json["title_fr"], "Mon contact")
        self.assertEqual(json["description_fr"], "Ma **description**")
        self.assertEqual(json["subtitle_fr"], "Ma fonction")

        brain = catalog(UID=contact.UID())[0]
        serializer = getMultiAdapter((brain, self.request), ISerializeToJsonSummary)
        json_summary = serializer()
        self.assertEqual(json_summary["title"], "Mijn contactpersoon")
        self.assertEqual(json_summary["description"], "Mijn beschrijving")
