# -*- coding: utf-8 -*-

from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from imio.directory.core.tests.utils import make_named_image
from imio.smartweb.common.interfaces import ICropping
from plone import api
from plone.app.imagecropping.interfaces import IImageCroppingUtils
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.namedfile.file import NamedBlobImage
from zope.component import getMultiAdapter

import unittest


class TestCropping(unittest.TestCase):
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
        self.contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="Contact",
        )

    def test_cropping_adapter(self):
        adapter = ICropping(self.contact, alternate=None)
        self.assertIsNotNone(adapter)
        self.assertEqual(
            adapter.get_scales("image", self.request),
            ["portrait_affiche", "paysage_affiche", "carre_affiche"],
        )
        self.assertEqual(adapter.get_scales("logo", self.request), [])

    def test_uncroppable_fields(self):
        self.contact.logo = NamedBlobImage(**make_named_image())
        self.contact.image = NamedBlobImage(**make_named_image())
        adapter = IImageCroppingUtils(self.contact, alternate=None)
        self.assertIsNotNone(adapter)
        self.assertEqual(len(list(adapter._image_field_values())), 1)
        self.assertEqual(adapter.image_field_names(), ["image"])

    def test_cropping_view(self):
        self.contact.logo = NamedBlobImage(**make_named_image())
        self.contact.image = NamedBlobImage(**make_named_image())
        cropping_view = getMultiAdapter(
            (self.contact, self.request), name="croppingeditor"
        )
        self.assertEqual(len(list(cropping_view._scales("logo"))), 0)
        self.assertEqual(len(list(cropping_view._scales("image"))), 3)
        self.assertNotIn("Logo", cropping_view())
        self.assertIn("Lead Image", cropping_view())
