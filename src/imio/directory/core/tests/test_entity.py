# -*- coding: utf-8 -*-

from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from imio.directory.core.contents import IEntity
from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from z3c.relationfield import RelationValue
from z3c.relationfield.interfaces import IRelationList
from zope.component import createObject
from zope.component import getUtility
from zope.component import queryUtility
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import modified

import unittest


class TestEntity(unittest.TestCase):
    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.authorized_types_in_entity = ["imio.directory.Contact"]
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

        self.assertTrue(IFacetedNavigable.providedBy(entity))

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

    def test_populating_entities(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            id="entity",
        )
        entity2 = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            id="entity2",
        )
        entity3 = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            id="entity3",
        )
        contact = api.content.create(
            container=entity,
            type="imio.directory.Contact",
            id="contact",
        )
        contact2 = api.content.create(
            container=entity2,
            type="imio.directory.Contact",
            id="contact2",
        )
        contact3 = api.content.create(
            container=entity3,
            type="imio.directory.Contact",
            id="contact3",
        )

        # Add new entity + subscription to existing entity.
        intids = getUtility(IIntIds)

        entity4 = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            id="entity4",
        )
        entity4.populating_entities = [RelationValue(intids.getId(entity))]
        modified(entity4, Attributes(IRelationList, "populating_entities"))
        self.assertIn(entity4.UID(), contact.selected_entities)
        api.content.delete(entity4)

        # Link entity2 (all these contacts) to our object "entity".
        api.relation.create(
            source=entity, target=entity2, relationship="populating_entities"
        )
        modified(entity, Attributes(IRelationList, "populating_entities"))
        # So entity.uid() can be find on contact2
        self.assertIn(entity.UID(), contact2.selected_entities)

        moving_contact = api.content.create(
            container=entity2,
            type="imio.directory.Contact",
            id="moving_contact",
        )
        self.assertIn(entity.UID(), moving_contact.selected_entities)
        # We move a contact from one entity to another
        api.content.move(moving_contact, entity3)
        self.assertNotIn(entity.UID(), moving_contact.selected_entities)

        # Clear linking entities out of our object "entity".
        api.relation.delete(source=entity, relationship="populating_entities")
        modified(entity, Attributes(IRelationList, "populating_entities"))
        # So entity.uid() can not be find on contact2
        self.assertNotIn(entity.UID(), contact2.selected_entities)

        # First, link entity2 and entity3 to entity
        api.relation.create(
            source=entity, target=entity2, relationship="populating_entities"
        )
        api.relation.create(
            source=entity, target=entity3, relationship="populating_entities"
        )
        modified(entity, Attributes(IRelationList, "populating_entities"))
        # Assert link is OK
        self.assertIn(entity.UID(), contact2.selected_entities)
        self.assertIn(entity.UID(), contact3.selected_entities)

        # Next, we delete entity so we remove this entity.UID() out of contacts.
        api.content.delete(entity)
        self.assertNotIn(entity.UID(), contact2.selected_entities)
        self.assertNotIn(entity.UID(), contact3.selected_entities)
