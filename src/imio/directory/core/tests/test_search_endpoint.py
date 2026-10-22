# -*- coding: utf-8 -*-
"""RAM cache, Last-Modified and BAN of the @search endpoint, for the
contacts of one entity (selected_entities parameter, as sent by
imio.smartweb.core)."""

from contextlib import contextmanager
from datetime import datetime
from datetime import timezone
from imio.directory.core.rest.search.endpoint import _cachekey
from imio.directory.core.rest.search.endpoint import _entity_uid
from imio.directory.core.rest.search.endpoint import SearchGet
from imio.directory.core.subscribers import removed_contact
from imio.directory.core.testing import IMIO_DIRECTORY_CORE_FUNCTIONAL_TESTING
from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from imio.directory.core.utils import ENDPOINT_CACHE_KEY
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.restapi.services.search.get import SearchGet as BaseSearchGet
from unittest.mock import MagicMock
from unittest.mock import patch
from z3c.caching.interfaces import ILastModified
from z3c.relationfield import RelationValue
from z3c.relationfield.interfaces import IRelationList
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.component.hooks import setSite
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import modified

import os
import transaction
import unittest


def make_request(form, language="fr"):
    request = MagicMock()
    request.form = form.copy()
    request.get.return_value = language
    request.cookies = {}
    headers = {}
    request.response.setHeader.side_effect = lambda k, v: headers.__setitem__(k, v)
    request.response.getHeader.side_effect = headers.get
    return request


def make_service(context, form, language="fr"):
    service = object.__new__(SearchGet)
    service.context = context
    service.request = make_request(form, language)
    return service


def bump_generation(portal, entity_uid):
    ann = IAnnotations(portal)
    key = f"{ENDPOINT_CACHE_KEY}{entity_uid}"
    ann[key] = ann.get(key, 0) + 1


class TestEntityUid(unittest.TestCase):
    def test_one_entity(self):
        self.assertEqual(_entity_uid(make_request({"selected_entities": "a"})), "a")
        self.assertEqual(_entity_uid(make_request({"selected_entities": ["a"]})), "a")

    def test_not_exactly_one_entity(self):
        self.assertIsNone(_entity_uid(make_request({})))
        self.assertIsNone(_entity_uid(make_request({"selected_entities": ""})))
        self.assertIsNone(_entity_uid(make_request({"selected_entities": []})))
        self.assertIsNone(_entity_uid(make_request({"selected_entities": ["a", "b"]})))


class TestCacheKey(unittest.TestCase):
    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setSite(self.portal)
        self.entity_uid = "entity-uid"

    def key(self, form, language="fr"):
        return _cachekey(None, make_service(self.portal, form, language))

    def test_key_follows_the_generation_of_the_entity(self):
        form = {"selected_entities": self.entity_uid}
        key = self.key(form)
        self.assertIn(self.entity_uid, key)
        self.assertEqual(key, self.key(form))
        bump_generation(self.portal, self.entity_uid)
        self.assertNotEqual(key, self.key(form))

    def test_key_depends_on_params_and_language(self):
        form = {"selected_entities": self.entity_uid, "b_size": "10"}
        self.assertNotEqual(self.key(form), self.key({**form, "b_size": "20"}))
        self.assertNotEqual(self.key(form), self.key(form, language="nl"))

    def test_volatile_params_are_ignored(self):
        form = {"selected_entities": self.entity_uid}
        self.assertEqual(self.key(form), self.key({**form, "cache_key": "x", "_": 1}))


class TestRAMCache(unittest.TestCase):
    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setSite(self.portal)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        # a new entity for each test: the RAM cache is not cleared between tests
        self.entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="Entity",
        )
        logout()

    def cache_header(self, form):
        service = make_service(self.portal, form)
        with patch.object(BaseSearchGet, "reply", return_value={"items": []}):
            service.reply()
        return service.request.response.getHeader("X-RAM-Cache")

    def test_miss_hit_and_miss_after_invalidation(self):
        form = {"selected_entities": self.entity.UID()}
        self.assertEqual(self.cache_header(form), "MISS")
        self.assertEqual(self.cache_header(form), "HIT")
        bump_generation(self.portal, self.entity.UID())
        self.assertEqual(self.cache_header(form), "MISS")

    def test_no_cache_without_exactly_one_entity(self):
        self.assertIsNone(self.cache_header({}))
        self.assertIsNone(self.cache_header({"UID": self.entity.UID()}))
        self.assertIsNone(
            self.cache_header({"selected_entities": [self.entity.UID(), "other"]})
        )

    def test_no_cache_when_authenticated(self):
        # the results depend on the user: they must not be shared with others
        login(self.portal, TEST_USER_NAME)
        self.assertIsNone(self.cache_header({"selected_entities": self.entity.UID()}))

    def test_no_cache_when_disabled_in_registry(self):
        api.portal.set_registry_record(
            "imio.directory.core.search_cache_enabled", False
        )
        self.assertIsNone(self.cache_header({"selected_entities": self.entity.UID()}))


class TestInvalidation(unittest.TestCase):
    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="Entity",
        )

    def generation(self, entity=None):
        entity = entity or self.entity
        return IAnnotations(self.portal).get(f"{ENDPOINT_CACHE_KEY}{entity.UID()}", 0)

    def create_contact(self, container=None):
        return api.content.create(
            container=container or self.entity,
            type="imio.directory.Contact",
            title="Contact",
        )

    def test_add_contact(self):
        before = self.generation()
        self.create_contact()
        self.assertGreater(self.generation(), before)

    def test_modify_contact(self):
        contact = self.create_contact()
        before = self.generation()
        modified(contact)
        self.assertGreater(self.generation(), before)

    def test_transition_contact(self):
        contact = self.create_contact()
        before = self.generation()
        with patch("imio.directory.core.subscribers.send_to_odwb"):
            api.content.transition(contact, "publish")
        self.assertGreater(self.generation(), before)

    def test_remove_contact(self):
        contact = self.create_contact()
        before = self.generation()
        api.content.delete(contact)
        self.assertGreater(self.generation(), before)

    def test_remove_contact_without_portal(self):
        # when the Plone site is removed, there is no portal any more
        contact = self.create_contact()
        with patch(
            "plone.api.portal.get", side_effect=api.exc.CannotGetPortalError
        ), patch("imio.directory.core.subscribers.OdwbEndpointGet") as odwb:
            removed_contact(contact, None)
        odwb.assert_not_called()

    def create_entity(self, title, populating_entities=()):
        intids = getUtility(IIntIds)
        return api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title=title,
            populating_entities=[
                RelationValue(intids.getId(entity)) for entity in populating_entities
            ],
        )

    def test_move_contact_invalidates_old_and_new_entities(self):
        # after the move, the contact is also shown in third_entity, which is
        # populated by new_entity
        contact = self.create_contact()
        new_entity = self.create_entity("New entity")
        third_entity = self.create_entity("Third entity", [new_entity])
        entities = (self.entity, new_entity, third_entity)
        before = [self.generation(entity) for entity in entities]
        api.content.move(contact, new_entity)
        for entity, generation in zip(entities, before):
            self.assertGreater(self.generation(entity), generation)

    def test_contact_invalidates_entities_it_populates(self):
        # a contact of self.entity is also shown in other_entity
        other_entity = self.create_entity("Other entity", [self.entity])
        before = self.generation(other_entity)
        contact = self.create_contact()
        self.assertIn(other_entity.UID(), contact.selected_entities)
        self.assertGreater(self.generation(other_entity), before)

        before = self.generation(other_entity)
        modified(contact)
        self.assertGreater(self.generation(other_entity), before)

    def test_change_populating_entities(self):
        # the contacts of other_entity are now shown in self.entity
        other_entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="Other entity",
        )
        self.create_contact(other_entity)
        before = self.generation()
        intids = getUtility(IIntIds)
        self.entity.populating_entities = [RelationValue(intids.getId(other_entity))]
        modified(self.entity, Attributes(IRelationList, "populating_entities"))
        self.assertGreater(self.generation(), before)


class TestSearchLastModified(unittest.TestCase):
    """The Last-Modified header and the ETag of @search come from
    ILastModified. They must change when the contacts of the entity change,
    else Varnish revalidates its cached results with a 304 forever."""

    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setSite(self.portal)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="Entity",
        )

    def last_modified(self, form):
        return ILastModified(make_service(self.portal, form))()

    def test_last_modified_follows_the_contacts_of_the_entity(self):
        form = {"selected_entities": self.entity.UID()}
        before = datetime.now(timezone.utc).replace(microsecond=0)
        api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="Contact",
        )
        last_modified = self.last_modified(form)
        self.assertGreaterEqual(last_modified, before)
        self.assertEqual(last_modified, self.last_modified(form))
        # the site modification date (old behaviour) is never used
        self.assertNotEqual(last_modified, self.portal.modified().asdatetime())

    def test_last_modified_is_now_when_unknown(self):
        # without one entity, or for an entity that never changed, we cannot
        # tell when the results changed: no 304 may be sent
        before = datetime.now(timezone.utc)
        self.assertGreaterEqual(self.last_modified({}), before)
        self.assertGreaterEqual(self.last_modified({"UID": "a"}), before)
        self.assertGreaterEqual(
            self.last_modified({"selected_entities": "unknown"}), before
        )


class TestBanSearchEndpoint(unittest.TestCase):
    """After the commit of a change in the contacts, the search results are
    removed from Varnish (BAN), so the clients get the new results at once."""

    layer = IMIO_DIRECTORY_CORE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            title="Entity",
        )
        transaction.commit()

    @contextmanager
    def mocked_ban(self):
        with patch.dict(os.environ, {"CACHING_SERVERS": "varnish:6081"}), patch(
            "imio.smartweb.common.caching.requests.request"
        ) as mocked:
            yield mocked

    def add_two_contacts(self):
        for title in ("Contact 1", "Contact 2"):
            api.content.create(
                container=self.entity,
                type="imio.directory.Contact",
                title=title,
            )

    def test_ban_after_commit(self):
        with self.mocked_ban() as ban:
            self.add_two_contacts()
            self.assertEqual(ban.call_args_list, [])
            transaction.commit()
        # one BAN, even with many changes in the transaction
        self.assertEqual(
            [call.args[:2] for call in ban.call_args_list],
            [("BAN", "http://varnish:6081/@search")],
        )

    def test_no_ban_when_transaction_is_aborted(self):
        with self.mocked_ban() as ban:
            self.add_two_contacts()
            transaction.abort()
        self.assertEqual(ban.call_args_list, [])

    def test_failed_ban_does_not_stop_odwb(self):
        # the BAN and the ODWB sending are independent after commit hooks
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            title="Contact",
        )
        transaction.commit()
        with self.mocked_ban() as ban, patch(
            "imio.directory.core.subscribers.OdwbEndpointGet"
        ) as odwb:
            ban.side_effect = RuntimeError("Varnish is down")
            api.content.transition(contact, "publish")
            transaction.commit()
            self.assertTrue(ban.called)
            odwb.return_value.reply.assert_called_once()

            ban.reset_mock()
            api.content.delete(contact)
            transaction.commit()
            self.assertTrue(ban.called)
            odwb.return_value.remove.assert_called_once()
