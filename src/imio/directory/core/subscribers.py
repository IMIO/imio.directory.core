# -*- coding: utf-8 -*-

from imio.directory.core.utils import get_entity_uid_for_contact
from imio.smartweb.common.faceted.utils import configure_faceted
from imio.smartweb.common.interfaces import IAddress
from imio.smartweb.common.utils import geocode_object
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.lifecycleevent.interfaces import IAttributes

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
    request = getRequest()
    request.form = {
        "cid": "entity",
        "faceted.entity.default": obj.UID(),
    }
    handler = getMultiAdapter((obj, request), name="faceted_update_criterion")
    handler.edit(**request.form)


def added_contact(obj, event):
    set_default_entity_uid(obj)
    if not obj.is_geolocated:
        # geocode only if the user has not already changed geolocation
        geocode_object(obj)


def modified_contact(obj, event):
    set_default_entity_uid(obj)

    if not hasattr(event, "descriptions") or not event.descriptions:
        return
    for d in event.descriptions:
        if not IAttributes.providedBy(d):
            # we do not have fields change description, but maybe a request
            continue
        if d.interface is IAddress and d.attributes:
            # an address field has been changed
            geocode_object(obj)
            return
