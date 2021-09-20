# -*- coding: utf-8 -*-

from collective.geolocationbehavior.geolocation import IGeolocatable
from imio.directory.core.contents import IContact
from imio.directory.core.contents.contact.content import phone_constraint

# from imio.directory.core.tests.utils import get_json
from imio.directory.core.testing import IMIO_DIRECTORY_CORE_FUNCTIONAL_TESTING
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

# from plone.app.testing import TEST_USER_NAME
# from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.dexterity.interfaces import IDexterityFTI
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.namedfile.file import NamedBlobFile

# from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import RelativeSession
from zope.annotation.interfaces import IAnnotations
from zope.component import createObject
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface.exceptions import Invalid

# import json
import transaction
import unittest


class ContactFunctionalTest(unittest.TestCase):

    layer = IMIO_DIRECTORY_CORE_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.authorized_types_in_contact = ["imio.directory.Contact", "File", "Image"]
        self.unauthorized_types_in_contact = ["Folder", "Page", "Link"]

        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        # self.api_session.auth = (TEST_USER_NAME, TEST_USER_PASSWORD)
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="Entity",
        )

    def tearDown(self):
        self.api_session.close()

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
            container=self.entity,
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

    def test_ct_contact_not_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        fti = queryUtility(IDexterityFTI, name="imio.directory.Contact")
        self.assertFalse(fti.global_allow, u"{0} is globally addable!".format(fti.id))

    def test_ct_contact_filter_content_type(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        contact = api.content.create(
            container=self.entity,
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
            container=self.entity,
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
            container=self.entity,
            type="imio.directory.Contact",
            title="contact",
        )
        view = getMultiAdapter((contact, self.request), name="view")
        view.update()
        self.assertNotIn("contact-gallery", view.render())
        api.content.create(
            container=contact,
            type="Image",
            title="image",
        )
        self.assertIn("contact-gallery", view.render())

    def test_files_in_contact_view(self):
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="contact",
        )
        view = getMultiAdapter((contact, self.request), name="view")
        view.update()
        self.assertNotIn("contact-files", view.render())
        file_obj = api.content.create(
            container=contact,
            type="File",
            title="file",
        )
        file_obj.file = NamedBlobFile(data="file data", filename=u"file.txt")
        view = queryMultiAdapter((contact, self.request), name="view")
        view.update()
        self.assertIn("++resource++mimetype.icons/txt.png", view.render())
        self.assertIn("1 KB", view.render())
        self.assertEqual(view.get_thumb_scale_list(), "thumb")
        api.portal.set_registry_record("plone.thumb_scale_listing", "preview")
        annotations = IAnnotations(self.request)
        del annotations["plone.memoize"]
        view = queryMultiAdapter((contact, self.request), name="view")
        self.assertEqual(view.get_thumb_scale_list(), "preview")
        api.portal.set_registry_record("plone.no_thumbs_lists", True)
        annotations = IAnnotations(self.request)
        del annotations["plone.memoize"]
        view = queryMultiAdapter((contact, self.request), name="view")
        self.assertIsNone(view.get_thumb_scale_list())
        view.update()
        self.assertIn("contact-files", view.render())

    def test_overall_response_format(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="contact",
        )
        transaction.commit()
        response = self.api_session.get(contact.absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

        results = response.json()
        self.assertEqual(
            results[u"items_total"],
            len(results[u"items"]),
            "items_total property should match actual item count.",
        )

    def test_subscriber_to_select_current_entity(self):
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="My contact",
        )
        self.assertEqual(contact.selected_entities, [self.entity.UID()])

    def test_indexes(self):
        contact1 = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="Contact1",
        )
        catalog = api.portal.get_tool("portal_catalog")
        brain = api.content.find(UID=contact1.UID())[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertFalse(indexes.get("is_geolocated"))
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
