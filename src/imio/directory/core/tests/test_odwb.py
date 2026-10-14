# -*- coding: utf-8 -*-

from imio.directory.core.rest.odwb_endpoint import OdwbEndpointGet
from imio.directory.core.rest.odwb_endpoint import OdwbEntitiesEndpointGet
from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest.mock import MagicMock
from unittest.mock import patch

import requests
import unittest


class RestFunctionalTest(unittest.TestCase):
    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.entity = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            id="entity",
            title="Entity",
        )

    @patch("requests.post")
    def test_odwb_url_errors(self, mock_post):
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            id="contact",
            title="Contact",
        )
        # OdwbEndpointGet.test_in_staging_or_local = True
        mock_request = MagicMock()

        mock_post.side_effect = requests.exceptions.ConnectionError(
            "ODWB : Connection error occurred"
        )
        endpoint = OdwbEndpointGet(contact, mock_request)
        response = endpoint.reply()["batches"][0]["response"]
        self.assertEqual(response, "ODWB : Connection error occurred")
        mock_post.side_effect = requests.exceptions.Timeout("ODWB : Request timed out")
        endpoint = OdwbEndpointGet(contact, mock_request)
        response = endpoint.reply()["batches"][0]["response"]
        self.assertEqual(response, "ODWB : Request timed out")

        mock_post.side_effect = requests.exceptions.HTTPError(
            "ODWB : HTTP error occurred"
        )
        endpoint = OdwbEndpointGet(contact, mock_request)
        response = endpoint.reply()["batches"][0]["response"]
        self.assertEqual(response, "ODWB : HTTP error occurred")

        mock_post.side_effect = Exception("ODWB : Unexpected error occurred")
        endpoint = OdwbEndpointGet(contact, mock_request)
        response = endpoint.reply()["batches"][0]["response"]
        self.assertEqual(response, "ODWB : Unexpected error occurred")

    @patch("requests.post")
    def test_reply_returns_sending_summary(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, text="")
        endpoint = OdwbEndpointGet(self.entity, self.request)
        self.assertEqual(
            endpoint.reply(),
            {"service": "contacts-en-wallonie", "total": 0, "sent": 0, "batches": []},
        )
        mock_post.assert_not_called()

        for i in range(2):
            contact = api.content.create(
                container=self.entity, type="imio.directory.Contact", title=f"C{i}"
            )
            api.content.transition(contact, "publish")
        endpoint = OdwbEndpointGet(self.entity, self.request)
        self.assertEqual(
            endpoint.reply(),
            {
                "service": "contacts-en-wallonie",
                "total": 2,
                "sent": 2,
                "batches": [{"size": 2, "status_code": 200, "response": ""}],
            },
        )

        mock_post.return_value = MagicMock(status_code=400, text="bad pushkey")
        endpoint = OdwbEndpointGet(self.entity, self.request)
        summary = endpoint.reply()
        self.assertEqual(summary["sent"], 0)
        self.assertEqual(
            summary["batches"],
            [{"size": 2, "status_code": 400, "response": "bad pushkey"}],
        )

    @patch("requests.post")
    def test_get_news_to_send_to_odwb(self, m):
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            id="contact",
            title="Contact",
        )

        entity2 = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            id="entity2",
            title="Entity 2",
        )

        contact2 = api.content.create(
            container=entity2,
            type="imio.directory.Contact",
            id="contact2",
            title="Contact 2",
        )

        api.content.transition(contact, "publish")
        endpoint = OdwbEndpointGet(self.portal, self.request)
        endpoint.reply()
        # 1 (published) contact is returned on self.portal
        self.assertEqual(len(endpoint.__datas__), 1)

        api.content.transition(contact2, "publish")
        endpoint = OdwbEndpointGet(self.portal, self.request)
        endpoint.reply()
        # 2 (published) contacts are returned on self.portal
        self.assertEqual(len(endpoint.__datas__), 2)

        for data in endpoint.__datas__:
            if data.get("geolocation", None) is not None:
                self.assertEqual(data.get("geolocation"), {"lat": 4.5, "lon": 45})
            if data.get("latitude", None) is not None:
                self.assertEqual(data.get("latitude"), 4.5)
            if data.get("longitude", None) is not None:
                self.assertEqual(data.get("longitude"), 45)

        # test endpoint on entity
        endpoint = OdwbEndpointGet(self.entity, self.request)
        endpoint.reply()
        # 1 (published) contact is returned on self.entity
        self.assertEqual(len(endpoint.__datas__), 1)

    @patch("requests.post")
    def test_local_category_sent_to_odwb(self, m):
        self.entity.local_categories = [
            {"fr": "Ma catégorie", "nl": "Mijn categorie", "de": None, "en": None},
        ]
        contact = api.content.create(
            container=self.entity,
            type="imio.directory.Contact",
            id="contact",
            title="Contact",
        )
        endpoint = OdwbEndpointGet(contact, self.request)
        endpoint.reply()
        self.assertIsNone(endpoint.__datas__[0]["local_category_token"])
        self.assertIsNone(endpoint.__datas__[0]["local_category_title"])

        contact.local_category = "Ma catégorie"
        endpoint = OdwbEndpointGet(contact, self.request)
        endpoint.reply()
        self.assertEqual(endpoint.__datas__[0]["local_category_token"], "Ma catégorie")
        self.assertEqual(endpoint.__datas__[0]["local_category_title"], "Ma catégorie")

    @patch("requests.post")
    def test_entities_reply_returns_sending_summary(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, text="")
        api.content.transition(self.entity, "publish")
        endpoint = OdwbEntitiesEndpointGet(self.portal, self.request)
        self.assertEqual(
            endpoint.reply(),
            {
                "service": "entites-des-contacts-en-wallonie",
                "total": 1,
                "sent": 1,
                "batches": [{"size": 1, "status_code": 200, "response": ""}],
            },
        )

        mock_post.side_effect = requests.exceptions.Timeout("too slow")
        endpoint = OdwbEntitiesEndpointGet(self.portal, self.request)
        summary = endpoint.reply()
        self.assertEqual(summary["sent"], 0)
        self.assertEqual(
            summary["batches"],
            [{"size": 1, "status_code": None, "response": "ODWB : Request timed out"}],
        )

    @patch("requests.post")
    def test_get_entities_to_send_to_odwb(self, m):
        entity2 = api.content.create(
            container=self.portal,
            type="imio.directory.Entity",
            id="entity2",
            title="Entity 2",
        )
        # On directory auth source, entities are not automatically published
        api.content.transition(self.entity, "publish")
        api.content.transition(entity2, "publish")
        # OdwbEntitiesEndpointGet.test_in_staging_or_local = True
        endpoint = OdwbEntitiesEndpointGet(self.portal, self.request)
        endpoint.reply()
        self.assertEqual(len(endpoint.__datas__), 2)

        api.content.transition(self.entity, "reject")
        endpoint = OdwbEntitiesEndpointGet(self.portal, self.request)
        endpoint.reply()
        self.assertEqual(len(endpoint.__datas__), 1)
