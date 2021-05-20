# -*- coding: utf-8 -*-

from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
import unittest


class TestVocabularies(unittest.TestCase):

    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_countries(self):
        factory = getUtility(IVocabularyFactory, "imio.directory.vocabulary.Countries")
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 240)

    def test_contact_types(self):
        factory = getUtility(
            IVocabularyFactory, "imio.directory.vocabulary.ContactTypes"
        )
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 4)

    def test_phone_types(self):
        factory = getUtility(IVocabularyFactory, "imio.directory.vocabulary.PhoneTypes")
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 3)

    def test_mail_types(self):
        factory = getUtility(IVocabularyFactory, "imio.directory.vocabulary.MailTypes")
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 2)

    def test_site_types(self):
        factory = getUtility(IVocabularyFactory, "imio.directory.vocabulary.SiteTypes")
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 3)

    def test_cities_types(self):
        factory = getUtility(IVocabularyFactory, "imio.directory.vocabulary.Cities")
        vocabulary = factory()
        self.assertEqual(len(vocabulary), 898)
