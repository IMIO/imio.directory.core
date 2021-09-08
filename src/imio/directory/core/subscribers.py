# -*- coding: utf-8 -*-

from imio.directory.core.utils import get_entity_uid_for_contact
from imio.smartweb.common.faceted.utils import configure_faceted
from plone import api
from plone.app.dexterity.behaviors.metadata import IBasic
import os


def reindex_breadcrumb(obj, event):
    if not hasattr(event, "descriptions") or not event.descriptions:
        return

    for d in event.descriptions:
        if d.interface is not IBasic:
            continue
        if "IBasic.title" in d.attributes:
            brains = api.content.find(context=obj)
            for brain in brains:
                content = brain.getObject()
                content.reindexObject(idxs=["breadcrumb"])
            return


def set_default_entity_uid(contact):
    uid = get_entity_uid_for_contact(contact)
    if contact.selected_entities is None:
        contact.selected_entities = [uid]
        contact.reindexObject()
    elif uid not in contact.selected_entities:
        contact.selected_entities = contact.selected_entities + [uid]
        contact.reindexObject()


def added_entity(obj, event):
    faceted_config_path = "{}/faceted/config/entity.xml".format(
        os.path.dirname(__file__)
    )
    configure_faceted(obj, faceted_config_path)


def modified_entity(obj, event):
    reindex_breadcrumb(obj, event)


def added_contact(obj, event):
    set_default_entity_uid(obj)


def modified_contact(obj, event):
    set_default_entity_uid(obj)
    reindex_breadcrumb(obj, event)
