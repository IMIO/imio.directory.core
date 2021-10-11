# -*- coding: utf-8 -*-

from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.vocabularies.types import BAD_TYPES
from zope.component import queryMultiAdapter

import unittest


class TestDescription(unittest.TestCase):

    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests"""
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_description(self):
        portal_types = api.portal.get_tool("portal_types")
        bad_types = BAD_TYPES + ["Discussion Item"]
        all_types = [t for t in portal_types.listContentTypes() if t not in bad_types]
        for pt in all_types:
            container = self.portal
            if pt == "imio.directory.Contact":
                entity = api.content.create(
                    title="My entity",
                    container=self.portal,
                    type="imio.directory.Entity",
                )
                container = entity
            content_type = api.content.create(
                title="My {}".format(pt), container=container, type=pt
            )
            content_type.description = "My *description* is wonderfull with *bold* and \r\n carriage return \r\n"
            view = queryMultiAdapter((content_type, self.request), name="description")
            self.assertEqual(
                view.description(),
                "My <strong>description</strong> is wonderfull with <strong>bold</strong> and <br/> carriage return <br/>",
            )
