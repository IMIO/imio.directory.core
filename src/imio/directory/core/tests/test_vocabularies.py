# -*- coding: utf-8 -*-

from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import unittest


class TestVocabularies(unittest.TestCase):
    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_contact_types(self):
        factory = getUtility(
            IVocabularyFactory, "imio.directory.vocabulary.ContactTypes"
        )
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 3)

    def test_phone_types(self):
        factory = getUtility(IVocabularyFactory, "imio.directory.vocabulary.PhoneTypes")
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 4)

    def test_mail_types(self):
        factory = getUtility(IVocabularyFactory, "imio.directory.vocabulary.MailTypes")
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 2)

    def test_site_types(self):
        factory = getUtility(IVocabularyFactory, "imio.directory.vocabulary.SiteTypes")
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 7)

    def test_facilities(self):
        factory = getUtility(IVocabularyFactory, "imio.directory.vocabulary.Facilities")
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 13)

    def test_entities_UIDs(self):
        entity1 = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="Entity1",
        )
        entity2 = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="Entity2",
        )
        contact1 = api.content.create(
            container=entity1,
            type="imio.directory.Contact",
            title="Contact1",
        )
        factory = getUtility(
            IVocabularyFactory, "imio.directory.vocabulary.EntitiesUIDs"
        )
        vocabulary = factory(contact1)
        self.assertEqual(len(vocabulary), 2)

        vocabulary = factory(self.portal)
        self.assertEqual(len(vocabulary), 2)
        ordered_entities = [a.title for a in vocabulary]
        self.assertEqual(ordered_entities, [entity1.title, entity2.title])
        entity1.title = "Z Change order!"
        entity1.reindexObject()
        vocabulary = factory(self.portal)
        ordered_entities = [a.title for a in vocabulary]
        self.assertEqual(ordered_entities, [entity2.title, entity1.title])

    def test_contact_types_de(self):
        factory = getUtility(
            IVocabularyFactory, "imio.directory.vocabulary.ContactTypesDe"
        )
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 3)
        self.assertEqual(
            vocabulary.getTerm("mission").title,
            "Auftrag (Pässe, Empfang, Parken, etc.)",
        )

    def test_facilities_de(self):
        factory = getUtility(
            IVocabularyFactory, "imio.directory.vocabulary.FacilitiesDe"
        )
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 13)
        self.assertEqual(
            vocabulary.getTerm("drinking_water_point").title, "Trinkwasserstelle"
        )

    def test_contact_categories(self):
        factory = getUtility(
            IVocabularyFactory, "imio.directory.vocabulary.ContactCategories"
        )
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 396)
        self.assertEqual(
            vocabulary.getTerm("cho96vl9ox").title, "␟Commerces et entreprises"
        )

    def test_contact_categories_de(self):
        factory = getUtility(
            IVocabularyFactory, "imio.directory.vocabulary.ContactCategoriesDe"
        )
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 396)
        self.assertEqual(
            vocabulary.getTerm("902qcm27bp").title,
            "␟Andere Akteure des Gesundheitswesens",
        )

    def test_contact_local_categories(self):
        factory = getUtility(
            IVocabularyFactory, "imio.directory.vocabulary.ContactLocalCategories"
        )
        # Site root (ex: @types or @vocabularies from RESTAPI)
        self.assertEqual(len(factory(self.portal)), 0)

        entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="Entity",
        )
        contact = api.content.create(
            container=entity,
            type="imio.directory.Contact",
            title="Contact",
        )
        # Entity without local categories
        self.assertEqual(len(factory(contact)), 0)

        entity.local_categories = [
            {"fr": "Catégorie 1", "nl": "Categorie 1", "de": None, "en": None},
            {"fr": "Catégorie 2", "nl": None, "de": "Kategorie 2", "en": None},
        ]
        # Context can be the entity or a contact inside it
        vocabulary = factory(entity)
        self.assertEqual(len(vocabulary), 2)
        vocabulary = factory(contact)
        self.assertEqual(
            [(t.value, t.title) for t in vocabulary],
            [("Catégorie 1", "Catégorie 1"), ("Catégorie 2", "Catégorie 2")],
        )
        # Translated titles, with fallback on french value
        vocabulary = factory(contact, lang="nl")
        self.assertEqual(
            [(t.value, t.title) for t in vocabulary],
            [("Catégorie 1", "Categorie 1"), ("Catégorie 2", "Catégorie 2")],
        )
        vocabulary = factory(contact, lang="de")
        self.assertEqual(
            [(t.value, t.title) for t in vocabulary],
            [("Catégorie 1", "Catégorie 1"), ("Catégorie 2", "Kategorie 2")],
        )
