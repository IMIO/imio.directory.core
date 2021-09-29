# -*- coding: utf-8 -*-

from imio.directory.core.utils import get_entity_uid_for_contact
from imio.smartweb.common.faceted.utils import configure_faceted
from plone import api
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest

import logging
import os

logger = logging.getLogger("imio.directory.core")


def add_current_entity_on_contacts(context):
    brains = api.content.find(portal_type="imio.directory.Contact")
    for brain in brains:
        contact = brain.getObject()
        entity_uid = get_entity_uid_for_contact(contact)
        contact.selected_entities = [entity_uid]
        contact.reindexObject(idxs=["selected_entities"])
    logger.info(
        "Finished selected_entities filling for {} contacts".format(len(brains))
    )


def refresh_entities_faceted(context):
    request = getRequest()
    faceted_config_path = "{}/faceted/config/entity.xml".format(
        os.path.dirname(__file__)
    )
    brains = api.content.find(portal_type="imio.directory.Entity")
    for brain in brains:
        obj = brain.getObject()
        configure_faceted(obj, faceted_config_path)
        request.form = {
            "cid": "entity",
            "faceted.entity.default": obj.UID(),
        }
        handler = getMultiAdapter((obj, request), name=u"faceted_update_criterion")
        handler.edit(**request.form)
        logger.info("Faceted refreshed on {}".format(obj.Title()))
