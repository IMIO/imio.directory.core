# -*- coding: utf-8 -*-

from DateTime import DateTime
from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from imio.directory.core.upgrades.upgrades import (
    fix_liege_contacts_language_and_effective,
)
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest import mock

import unittest


class TestUpgrades(unittest.TestCase):
    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # /liege entity with contacts imported from Plone4 (no language, no
        # effective date), including a nested sub-contact.
        self.liege = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            id="liege",
            title="Liège",
        )
        self.contact = api.content.create(
            container=self.liege,
            type="imio.directory.Contact",
            title="8tea5",
        )
        self.contact.language = ""
        self.contact.reindexObject()
        self.subcontact = api.content.create(
            container=self.contact,
            type="imio.directory.Contact",
            title="Sub contact",
        )
        self.subcontact.language = ""
        self.subcontact.reindexObject()

        # A /liege contact that already has a language and an effective date:
        # the upgrade must leave both untouched.
        self.already_ok = api.content.create(
            container=self.liege,
            type="imio.directory.Contact",
            title="Already ok",
        )
        self.already_ok.setLanguage("fr")
        self.existing_effective = api.content.create(
            container=self.liege,
            type="imio.directory.Contact",
            title="Has effective",
        )
        self.existing_effective.setEffectiveDate("2020/01/01")
        self.existing_effective.reindexObject()
        self.preserved_effective = self.existing_effective.effective_date

        # A contact outside /liege: must stay out of scope.
        self.amay = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            id="amay",
            title="Amay",
        )
        self.other_contact = api.content.create(
            container=self.amay,
            type="imio.directory.Contact",
            title="Abbaye de Flône",
        )
        self.other_contact.language = ""
        self.other_contact.reindexObject()

    def test_fix_liege_contacts_language_and_effective(self):
        with mock.patch(
            "imio.directory.core.upgrades.upgrades.reindex_solr"
        ) as patched_reindex_solr:
            fix_liege_contacts_language_and_effective(self.portal)

        # Language set to "fr" on every /liege contact, including nested ones
        self.assertEqual(self.contact.language, "fr")
        self.assertEqual(self.subcontact.language, "fr")
        # ... and observable through the catalog Language index
        brains = api.content.find(
            context=self.liege, portal_type="imio.directory.Contact", Language="fr"
        )
        self.assertEqual(len(brains), 4)

        # Effective date set to 2026/06/01 08:00:00 when it was missing
        expected = DateTime("2026/06/01 08:00:00")
        self.assertEqual(self.contact.effective_date, expected)
        self.assertEqual(self.subcontact.effective_date, expected)

        # A contact that already had an effective date keeps its original value
        self.assertEqual(
            self.existing_effective.effective_date, self.preserved_effective
        )

        # The contact outside /liege is left untouched
        self.assertEqual(self.other_contact.language, "")
        self.assertIsNone(self.other_contact.effective_date)

        # The SolR reindex is triggered once at the end
        patched_reindex_solr.assert_called_once()
