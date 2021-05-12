# -*- coding: utf-8 -*-

from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter

import unittest


class UtilsIntegrationTest(unittest.TestCase):

    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_exort_to_vcard(self):
        contact = api.content.create(
            container=self.portal,
            type="imio.directory.Contact",
            title="contact",
        )
        contact.street = "My street"
        contact.number = "1"
        contact.zipcode = 5000
        view = getMultiAdapter((contact, self.request), name="utils")
        self.assertTrue(view.can_export_contact_to_vcard())
        self.assertEqual(
            str(view.export_contact_to_vcard()),
            "BEGIN:VCARD\r\nVERSION:3.0\r\nADR:1;;My street;;;5000;\r\nFN:contact\r\nEND:VCARD\r\n",
        )
        contact.gender = "M"
        contact.phones = [{"label": "label", "type": "cell", "number": "+32496111111"}]
        contact.mails = [
            {"label": "label", "type": "home", "mail_address": "test@imio.be"}
        ]
        self.assertEqual(
            str(view.export_contact_to_vcard()),
            "BEGIN:VCARD\r\nVERSION:3.0\r\nADR:1;;My street;;;5000;\r\nEMAIL;TYPE=home:test@imio.be\r\nFN:contact\r\nGENDER:M\r\nTEL;TYPE=cell:+32496111111\r\nEND:VCARD\r\n",
        )
        contact.urls = [
            {"type": "website", "url": "https://www.imio.be"}
        ]
        self.assertEqual(
            str(view.export_contact_to_vcard()),
            "BEGIN:VCARD\r\nVERSION:3.0\r\nADR:1;;My street;;;5000;\r\nEMAIL;TYPE=home:test@imio.be\r\nFN:contact\r\nGENDER:M\r\nTEL;TYPE=cell:+32496111111\r\nURL;TYPE=website:https://www.imio.be\r\nEND:VCARD\r\n",
        )

        view = getMultiAdapter((self.portal, self.request), name="utils")
        self.assertFalse(view.can_export_contact_to_vcard())
        self.assertIsNone(view.export_contact_to_vcard())
