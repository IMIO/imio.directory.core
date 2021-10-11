# -*- coding: utf-8 -*-

from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobImage
from zope.component import getMultiAdapter

import os
import unittest


def image(filename):
    file_path = os.path.join(os.path.dirname(__file__), filename)
    return NamedBlobImage(data=open(file_path, "rb").read(), filename=file_path)


class TestUtils(unittest.TestCase):

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

    def test_export_to_vcard(self):
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="contact",
        )
        contact.street = "My street"
        contact.number = "1"
        contact.zipcode = 5000
        contact.country = "be"
        view = getMultiAdapter((contact, self.request), name="utils")
        self.assertTrue(view.can_export_contact_to_vcard())
        self.assertEqual(
            str(view.export_contact_to_vcard()),
            "BEGIN:VCARD\r\nVERSION:3.0\r\nADR:1;;My street;;;5000;Belgium\r\nFN:contact\r\nEND:VCARD\r\n",
        )
        contact.phones = [{"label": "label", "type": "cell", "number": "+32496111111"}]
        contact.mails = [
            {"label": "label", "type": "home", "mail_address": "test@imio.be"}
        ]
        self.assertEqual(
            str(view.export_contact_to_vcard()),
            "BEGIN:VCARD\r\nVERSION:3.0\r\nADR:1;;My street;;;5000;Belgium\r\nEMAIL;TYPE=home:test@imio.be\r\nFN:contact\r\nTEL;TYPE=cell:+32496111111\r\nEND:VCARD\r\n",
        )
        contact.urls = [{"type": "website", "url": "https://www.imio.be"}]
        self.assertEqual(
            str(view.export_contact_to_vcard()),
            "BEGIN:VCARD\r\nVERSION:3.0\r\nADR:1;;My street;;;5000;Belgium\r\nEMAIL;TYPE=home:test@imio.be\r\nFN:contact\r\nTEL;TYPE=cell:+32496111111\r\nURL;TYPE=website:https://www.imio.be\r\nEND:VCARD\r\n",
        )
        contact.logo = image("resources/logo.png")
        self.assertIn(
            "PHOTO;ENCODING=B;TYPE=IMAGE/JPEG:", view.export_contact_to_vcard()
        )

        view = getMultiAdapter((self.portal, self.request), name="utils")
        self.assertFalse(view.can_export_contact_to_vcard())
        self.assertIsNone(view.export_contact_to_vcard())

        view = getMultiAdapter((self.entity, self.request), name="utils")
        self.assertFalse(view.can_export_contact_to_vcard())
        self.assertIsNone(view.export_contact_to_vcard())
