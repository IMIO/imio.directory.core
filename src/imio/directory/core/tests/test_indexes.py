# -*- coding: utf-8 -*-

from collective.geolocationbehavior.geolocation import IGeolocatable
from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.i18n.utility import setLanguageBinding

import unittest


class TestIndexes(unittest.TestCase):
    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

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

    def test_selected_entities_index(self):
        contact1 = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="Contact1",
        )
        catalog = api.portal.get_tool("portal_catalog")
        brain = api.content.find(UID=contact1.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertFalse(indexes.get("is_geolocated"))
        self.assertEqual(indexes.get("container_uid"), self.entity.UID())
        IGeolocatable(contact1).geolocation = Geolocation(
            latitude="4.5", longitude="45"
        )
        contact1.reindexObject(idxs=["is_geolocated"])
        brain = api.content.find(UID=contact1.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertTrue(indexes.get("is_geolocated"))

        contact2 = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="Contact2",
        )
        entity2 = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="Entity2",
        )
        contact1.selected_entities = [self.entity.UID()]
        contact1.reindexObject()
        brains = api.content.find(selected_entities=self.entity.UID())
        lst = [brain.UID for brain in brains]
        self.assertEqual(lst, [contact1.UID(), contact2.UID()])

        contact2.selected_entities = [entity2.UID(), self.entity.UID()]
        contact2.reindexObject()
        brains = api.content.find(selected_entities=entity2.UID())
        lst = [brain.UID for brain in brains]
        self.assertEqual(lst, [contact2.UID()])

        brains = api.content.find(selected_entities=[entity2.UID(), self.entity.UID()])
        lst = [brain.UID for brain in brains]
        self.assertEqual(lst, [contact1.UID(), contact2.UID()])

        contact2.selected_entities = [entity2.UID()]
        contact2.reindexObject()
        brains = api.content.find(selected_entities=[entity2.UID(), self.entity.UID()])
        lst = [brain.UID for brain in brains]
        self.assertEqual(lst, [contact1.UID(), contact2.UID()])

        api.content.move(contact1, entity2)
        brain = api.content.find(UID=contact1.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(indexes.get("container_uid"), entity2.UID())

    def test_searchable_text_index(self):
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="Title",
        )

        # use French (taxonomy is only translated in French)
        self.request["set_language"] = "fr"
        setLanguageBinding(self.request)

        catalog = api.portal.get_tool("portal_catalog")
        brain = api.content.find(UID=contact.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(indexes.get("SearchableText"), ["title"])

        contact.subtitle = "Subtitle"
        contact.description = "Description"
        contact.taxonomy_contact_category = [
            "brog42mktt",  # Auberge de jeunesse
            "hlsm9bijb1",  # Alimentation
        ]
        contact.topics = ["agriculture"]

        contact.mails = [
            {"label": "kamouloxmail", "mail_address": "ka@moulox.be", "type": "home"},
            {"label": None, "mail_address": "ka@moulox2.be", "type": "work"},
            {"label": "kamouloxmail2", "mail_address": "ka@moulox2.be", "type": "work"},
        ]
        contact.phones = [
            {"label": "kamouloxphone", "phone_number": "+3223456789", "type": "home"},
            {"label": "kamouloxphone2", "phone_number": "+3212345678", "type": "work"},
            {"label": None, "phone_number": "+3291234567", "type": "work"},
        ]
        contact.reindexObject()

        brain = api.content.find(UID=contact.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(
            indexes.get("SearchableText"),
            [
                "title",
                "subtitle",
                "description",
                "agriculture",
                "commerces",
                "et",
                "entreprises",
                "hebergement",
                "auberge",
                "de",
                "jeunesse",
                "commerces",
                "et",
                "entreprises",
                "alimentation",
                "kamouloxmail",
                "kamouloxmail2",
                "kamouloxphone",
                "kamouloxphone2",
            ],
        )

        contact2 = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="Title",
        )
        brain = api.content.find(UID=contact2.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(indexes.get("SearchableText"), ["title"])

        contact2.description = "Description"
        contact2.topics = ["agriculture"]
        contact2.taxonomy_contact_category = ["cho96vl9ox"]
        contact2.reindexObject()

        brain = api.content.find(UID=contact2.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(
            indexes.get("SearchableText"),
            [
                "title",
                "description",
                "agriculture",
                "commerces",
                "et",
                "entreprises",
            ],
        )

        contact2.title_de = "Titel"
        contact2.description_de = "Descriptie"
        contact2.reindexObject()

        brain = api.content.find(UID=contact2.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(
            indexes.get("SearchableText_de"),
            [
                "titel",
                "descriptie",
                "landwirtschaft",
                "geschafte",
                "und",
                "unternehmen",
            ],
        )
