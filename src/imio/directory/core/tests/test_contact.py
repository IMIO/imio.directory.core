# -*- coding: utf-8 -*-

from imio.directory.core.contents import IContact
from imio.directory.core.contents.contact.content import phone_constraint
from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface.exceptions import Invalid
import unittest


class ContactIntegrationTest(unittest.TestCase):

    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.authorized_types_in_contact = ["imio.directory.Contact", "File", "Image"]
        self.unauthorized_types_in_contact = ["Folder", "Page", "Link"]

        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_ct_contact_schema(self):
        fti = queryUtility(IDexterityFTI, name="imio.directory.Contact")
        schema = fti.lookupSchema()
        self.assertEqual(IContact, schema)

    def test_ct_contact_fti(self):
        fti = queryUtility(IDexterityFTI, name="imio.directory.Contact")
        self.assertTrue(fti)

    def test_ct_contact_factory(self):
        fti = queryUtility(IDexterityFTI, name="imio.directory.Contact")
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IContact.providedBy(obj),
            u"IContact not provided by {0}!".format(
                obj,
            ),
        )

    def test_ct_contact_adding(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        contact = api.content.create(
            container=self.portal,
            type="imio.directory.Contact",
            title="contact",
        )
        self.assertTrue(
            IContact.providedBy(contact),
            u"IContact not provided by {0}!".format(
                contact.id,
            ),
        )
        parent = contact.__parent__
        self.assertNotIn("contact", parent.objectIds())
        self.assertIn(contact.UID(), parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=contact)
        self.assertNotIn("contact", parent.objectIds())

    def test_ct_contact_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        fti = queryUtility(IDexterityFTI, name="imio.directory.Contact")
        self.assertTrue(
            fti.global_allow, u"{0} is not globally addable!".format(fti.id)
        )

    def test_ct_contact_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        contact = api.content.create(
            container=self.portal,
            type="imio.directory.Contact",
            title="contact",
        )
        for t in self.unauthorized_types_in_contact:
            with self.assertRaises(InvalidParameterError):
                api.content.create(
                    container=contact,
                    type=t,
                    title="My {}".format(t),
                )
        for t in self.authorized_types_in_contact:
            api.content.create(
                container=contact,
                type=t,
                title="My {}".format(t),
            )

    def test_phone_constraint(self):
        self.assertTrue(phone_constraint("+3256543567"))
        with self.assertRaises(Invalid):
            phone_constraint("+32 56543567")
        with self.assertRaises(Invalid):
            phone_constraint("+3256.543.567")
        with self.assertRaises(Invalid):
            phone_constraint("3256543567")
        with self.assertRaises(Invalid):
            phone_constraint("003256543567")
        with self.assertRaises(Invalid):
            phone_constraint("+3256")

    def test_name_chooser(self):
        contact = api.content.create(
            container=self.portal,
            type="imio.directory.Contact",
            title="contact",
        )
        self.assertEqual(contact.id, contact.UID())

        folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="folder",
        )
        self.assertNotEqual(folder.id, folder.UID())
        self.assertEqual(folder.id, "folder")

    def test_gallery_in_contact_view(self):
        contact = api.content.create(
            container=self.portal,
            type="imio.directory.Contact",
            title="contact",
        )
        view = getMultiAdapter(
            (contact, self.request), name="view"
        )
        view.update()
        self.assertNotIn("contact-gallery", view.render())
        api.content.create(
            container=contact,
            type="Image",
            title="image",
        )
        self.assertIn("contact-gallery", view.render())
