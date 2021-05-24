# -*- coding: utf-8 -*-

from imio.directory.core.testing import IMIO_DIRECTORY_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from Products.CMFPlone.utils import get_installer

import unittest


class TestSetup(unittest.TestCase):
    """Test that imio.directory.core is properly installed."""

    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])

    def test_product_installed(self):
        """Test if imio.directory.core is installed."""
        self.assertTrue(self.installer.is_product_installed("imio.directory.core"))

    def test_browserlayer(self):
        """Test that IImioDirectoryCoreLayer is registered."""
        from imio.directory.core.interfaces import IImioDirectoryCoreLayer
        from plone.browserlayer import utils

        self.assertIn(IImioDirectoryCoreLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = IMIO_DIRECTORY_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("imio.directory.core")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if imio.directory.core is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("imio.directory.core"))

    def test_browserlayer_removed(self):
        """Test that IImioDirectoryCoreLayer is removed."""
        from imio.directory.core.interfaces import IImioDirectoryCoreLayer
        from plone.browserlayer import utils

        self.assertNotIn(IImioDirectoryCoreLayer, utils.registered_layers())
