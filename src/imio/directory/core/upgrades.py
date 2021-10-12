# -*- coding: utf-8 -*-

from collective.geolocationbehavior.geolocation import IGeolocatable
from imio.directory.core.utils import get_entity_uid_for_contact
from imio.smartweb.common.faceted.utils import configure_faceted
from imio.smartweb.common.utils import geocode_object
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


def geocode_all_contacts(context):
    default_latitude = api.portal.get_registry_record("geolocation.default_latitude")
    default_longitude = api.portal.get_registry_record("geolocation.default_longitude")
    brains = api.content.find(portal_type="imio.directory.Contact")
    for brain in brains:
        contact = brain.getObject()
        coordinates = IGeolocatable(contact).geolocation
        geocoded = False
        if coordinates is None or not all(
            [coordinates.latitude, coordinates.longitude]
        ):
            # contact has no geolocation, see if we can find one
            geocoded = geocode_object(contact)
            logger.info(f"Contact has no location : {contact.absolute_url()}")
        elif (
            coordinates.latitude == default_latitude
            and coordinates.longitude == default_longitude
        ):
            # contact was automatically geolocated on IMIO (by default)
            geocoded = geocode_object(contact)
            logger.info(f"Contact is located on IMIO : {contact.absolute_url()}")
        if geocoded:
            logger.info(
                f"  --> geocoded on {contact.geolocation.latitude} / {contact.geolocation.longitude}"
            )
