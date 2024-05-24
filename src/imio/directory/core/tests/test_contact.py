# -*- coding: utf-8 -*-

from imio.directory.core.contents import IContact
from imio.directory.core.contents.contact.content import phone_constraint
from imio.directory.core.interfaces import IImioDirectoryCoreLayer
from imio.directory.core.testing import IMIO_DIRECTORY_CORE_FUNCTIONAL_TESTING
from imio.directory.core.tests.utils import make_named_image
from imio.smartweb.common.utils import geocode_object
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.contenttypes.behaviors.leadimage import ILeadImageBehavior
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.app.imagecropping import PAI_STORAGE_KEY
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.dexterity.interfaces import IDexterityFTI
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.restapi.testing import RelativeSession
from plone.testing.zope import Browser
from unittest import mock
from z3c.relationfield import RelationValue
from z3c.relationfield.interfaces import IRelationList
from zope.annotation.interfaces import IAnnotations
from zope.component import createObject
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.interface.exceptions import Invalid
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import modified

import geopy
import transaction
import unittest


class TestContact(unittest.TestCase):
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
            "IContact not provided by {0}!".format(
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
            "IContact not provided by {0}!".format(
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
        self.assertFalse(fti.global_allow, "{0} is globally addable!".format(fti.id))

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
        file_obj.file = NamedBlobFile(data="file data", filename="file.txt")
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

        contact.schedule = {
            "friday": {
                "afternoonend": "17:30",
                "afternoonstart": "13:00",
                "comment": "uniquement sur rdv",
                "morningend": "12:30",
                "morningstart": "09:00",
            },
            "monday": {
                "afternoonend": "15:15",
                "afternoonstart": "13:00",
                "comment": "uniquement sur rdv",
                "morningend": "12:30",
                "morningstart": "09:00",
            },
            "saturday": {
                "afternoonend": "",
                "afternoonstart": "",
                "comment": "",
                "morningend": "",
                "morningstart": "",
            },
            "sunday": {
                "afternoonend": "",
                "afternoonstart": "",
                "comment": "",
                "morningend": "",
                "morningstart": "",
            },
            "thursday": {
                "afternoonend": "18:30",
                "afternoonstart": "13:00",
                "comment": "uniquement sur rdv",
                "morningend": "12:30",
                "morningstart": "09:00",
            },
            "tuesday": {
                "afternoonend": "15:15",
                "afternoonstart": "13:00",
                "comment": "uniquement sur rdv",
                "morningend": "12:30",
                "morningstart": "09:00",
            },
            "wednesday": {
                "afternoonend": "18:30",
                "afternoonstart": "13:00",
                "comment": "uniquement sur rdv",
                "morningend": "12:30",
                "morningstart": "09:00",
            },
        }

        transaction.commit()
        response = self.api_session.get(contact.absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

        results = response.json()
        self.assertEqual(
            results["items_total"],
            len(results["items"]),
            "items_total property should match actual item count.",
        )

    def test_subscriber_to_select_current_entity(self):
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="My contact",
        )
        self.assertEqual(contact.selected_entities, [self.entity.UID()])

    def test_geolocation(self):
        attr = {"geocode.return_value": mock.Mock(latitude=1, longitude=2)}
        geopy.geocoders.Nominatim = mock.Mock(return_value=mock.Mock(**attr))
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="contact",
        )
        self.assertFalse(contact.is_geolocated)
        contact.geolocation = Geolocation(0, 0)
        contact.street = "My beautiful street"
        geocode_object(contact)
        self.assertTrue(contact.is_geolocated)
        self.assertEqual(contact.geolocation.latitude, 1)
        self.assertEqual(contact.geolocation.longitude, 2)

    def test_subcontacts_in_contact_view(self):
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="contact",
        )
        view = getMultiAdapter((contact, self.request), name="view")
        view.update()
        self.assertNotIn("contact1", view.render())
        self.assertNotIn("contact2", view.render())
        for cpt_contact in [1, 2]:
            subcontact = api.content.create(
                container=contact,
                type="imio.directory.Contact",
                title="contact{}".format(cpt_contact),
            )
            subcontact.type = "organization"
            subcontact.reindexObject()
        view = getMultiAdapter((contact, self.request), name="view")
        view.update()
        self.assertIn("contact1", view.render())
        self.assertIn("contact2", view.render())

    def test_sharing(self):
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="contact",
        )
        transaction.commit()
        browser = Browser(self.layer["app"])
        browser.handleErrors = False
        browser.addHeader(
            "Authorization",
            "Basic %s:%s"
            % (
                TEST_USER_NAME,
                TEST_USER_PASSWORD,
            ),
        )
        browser.open("{}/@@sharing".format(contact.absolute_url()))
        checkbox = browser.getControl(name="entries.role_Reader:records")
        checkbox.value = True
        # be sure there is no traceback when sharing (subscriber related)
        browser.getControl(name="form.button.Save").click()

    def test_js_bundles(self):
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="contact",
        )
        alsoProvides(self.request, IImioDirectoryCoreLayer)
        getMultiAdapter((contact, self.request), name="view")()
        bundles = getattr(self.request, "enabled_bundles", [])
        self.assertEqual(len(bundles), 0)
        api.content.create(
            container=contact,
            type="Image",
            title="Image",
        )
        getMultiAdapter((contact, self.request), name="view")()
        bundles = getattr(self.request, "enabled_bundles", [])
        self.assertEqual(len(bundles), 2)
        self.assertListEqual(bundles, ["spotlightjs", "flexbin"])

    def test_referrer_entities(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        intids = getUtility(IIntIds)
        entity2 = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            id="entity2",
        )
        contact2 = api.content.create(
            container=entity2,
            type="imio.directory.Contact",
            id="contact2",
        )
        setattr(
            self.entity, "populating_entities", [RelationValue(intids.getId(entity2))]
        )
        modified(self.entity, Attributes(IRelationList, "populating_entities"))
        self.assertIn(self.entity.UID(), contact2.selected_entities)

        # if we create a contact in an entity that is referred in another entity
        # then, referrer entity UID is in contact.selected_entities list.
        contact2b = api.content.create(
            container=entity2,
            type="imio.directory.Contact",
            id="contact2b",
        )
        self.assertIn(entity2.UID(), contact2b.selected_entities)

    def test_automaticaly_readd_container_entity_uid(self):
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            id="contact",
        )
        self.assertIn(self.entity.UID(), contact.selected_entities)
        contact.selected_entities = []
        contact.reindexObject()
        modified(contact)
        self.assertIn(self.entity.UID(), contact.selected_entities)

    def test_removing_old_cropping(self):
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            id="contact",
        )
        contact.image = NamedBlobImage(**make_named_image())
        view = contact.restrictedTraverse("@@crop-image")
        view._crop(fieldname="image", scale="portrait_affiche", box=(1, 1, 200, 200))
        annotation = IAnnotations(contact).get(PAI_STORAGE_KEY)
        self.assertEqual(annotation, {"image_portrait_affiche": (1, 1, 200, 200)})

        modified(contact, Attributes(IBasic, "IBasic.title"))
        annotation = IAnnotations(contact).get(PAI_STORAGE_KEY)
        self.assertEqual(annotation, {"image_portrait_affiche": (1, 1, 200, 200)})

        modified(contact, Attributes(ILeadImageBehavior, "ILeadImageBehavior.image"))
        annotation = IAnnotations(contact).get(PAI_STORAGE_KEY)
        self.assertEqual(annotation, {})
