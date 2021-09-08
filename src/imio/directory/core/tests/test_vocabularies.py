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
        self.assertEqual(len(vocabulary), 3)

    def test_facilities(self):
        factory = getUtility(IVocabularyFactory, "imio.directory.vocabulary.Facilities")
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 6)

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
