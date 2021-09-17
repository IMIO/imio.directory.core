# -*- coding: utf-8 -*-

from imio.directory.core.utils import get_entity_uid_for_contact
from imio.smartweb.common.faceted.utils import configure_faceted

import os


def set_default_entity_uid(contact):
    contact.selected_entities = contact.selected_entities or []
    uid = get_entity_uid_for_contact(contact)
    if uid not in contact.selected_entities:
        contact.selected_entities = contact.selected_entities + [uid]
        contact.reindexObject()


def added_entity(obj, event):
    faceted_config_path = "{}/faceted/config/entity.xml".format(
        os.path.dirname(__file__)
    )
    configure_faceted(obj, faceted_config_path)


def added_contact(obj, event):
    set_default_entity_uid(obj)


def modified_contact(obj, event):
    set_default_entity_uid(obj)
