# -*- coding: utf-8 -*-
from imio.directory.core.taxonomies.utils import add_contact_taxonomy
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide unwanted profiles from site-creation and quickinstaller."""
        return [
            "imio.directory.core:testing",
            "imio.directory.core:uninstall",
        ]


def post_install(context):
    """Post install script"""
    add_contact_taxonomy("category")
    add_contact_taxonomy("topic")


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
