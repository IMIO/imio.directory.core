# -*- coding: utf-8 -*-

from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.uuid.interfaces import IUUID
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import modified

import unittest


class EntityIntegrationTest(unittest.TestCase):

    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="My Entity",
        )

    def test_breadcrumb(self):
        catalog = api.portal.get_tool("portal_catalog")
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="My Contact",
        )
        uuid = IUUID(contact)
        brain = api.content.find(UID=uuid)[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(indexes.get("breadcrumb"), "My Entity > My Contact")

        sub_contact = api.content.create(
            container=contact,
            type="imio.directory.Contact",
            title="My Sub-Contact",
        )
        uuid = IUUID(sub_contact)
        brain = api.content.find(UID=uuid)[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(
            indexes.get("breadcrumb"), "My Entity > My Contact > My Sub-Contact"
        )

        contact.title = "My New Contact"
        modified(contact, Attributes(IBasic, "IBasic.title"))
        brain = api.content.find(UID=uuid)[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(
            indexes.get("breadcrumb"), "My Entity > My New Contact > My Sub-Contact"
        )

        self.entity.title = "My New Entity"
        modified(self.entity, Attributes(IBasic, "IBasic.title"))
        api.content.move(sub_contact, self.entity)
        brain = api.content.find(UID=uuid)[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertEqual(indexes.get("breadcrumb"), "My New Entity > My Sub-Contact")
