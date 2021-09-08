# -*- coding: utf-8 -*-

from imio.directory.core.utils import get_entity_uid_for_contact
from plone import api

import logging

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
