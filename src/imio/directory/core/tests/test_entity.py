# -*- coding: utf-8 -*-

from imio.directory.core.contents import IEntity
from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


class TestEntity(unittest.TestCase):

    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.authorized_types_in_entity = ["imio.directory.Contact", "File", "Image"]
        self.unauthorized_types_in_entity = [
            "imio.directory.Entity",
            "Folder",
            "Page",
            "Link",
        ]

        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_ct_entity_schema(self):
        fti = queryUtility(IDexterityFTI, name="imio.directory.Entity")
        schema = fti.lookupSchema()
        self.assertEqual(IEntity, schema)

    def test_ct_entity_fti(self):
        fti = queryUtility(IDexterityFTI, name="imio.directory.Entity")
        self.assertTrue(fti)

    def test_ct_entity_factory(self):
        fti = queryUtility(IDexterityFTI, name="imio.directory.Entity")
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IEntity.providedBy(obj),
            "IEntity not provided by {0}!".format(
                obj,
            ),
        )

    def test_ct_entity_adding(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="entity",
        )
        self.assertTrue(
            IEntity.providedBy(entity),
            "IEntity not provided by {0}!".format(
                entity.id,
            ),
        )
        parent = entity.__parent__
        self.assertIn("entity", parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=entity)
        self.assertNotIn("entity", parent.objectIds())

    def test_ct_entity_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        fti = queryUtility(IDexterityFTI, name="imio.directory.Entity")
        self.assertTrue(fti.global_allow, "{0} is not globally addable!".format(fti.id))

    def test_ct_entity_filter_content_type(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="entity",
        )
        for t in self.unauthorized_types_in_entity:
            with self.assertRaises(InvalidParameterError):
                api.content.create(
                    container=entity,
                    type=t,
                    title="My {}".format(t),
                )
        for t in self.authorized_types_in_entity:
            api.content.create(
                container=entity,
                type=t,
                title="My {}".format(t),
            )
