# -*- coding: utf-8 -*-

from collective.geolocationbehavior.geolocation import IGeolocatable
from imio.directory.core.utils import get_entity_uid_for_contact
from imio.smartweb.common.faceted.utils import configure_faceted
from imio.smartweb.common.utils import translate_vocabulary_term
from plone import api
from plone.formwidget.geolocation.geolocation import Geolocation
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest

import geopy
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
        handler = getMultiAdapter((obj, request), name="faceted_update_criterion")
        handler.edit(**request.form)
        logger.info("Faceted refreshed on {}".format(obj.Title()))


def geocode_all_contacts(context):
    default_latitude = api.portal.get_registry_record("geolocation.default_latitude")
    default_longitude = api.portal.get_registry_record("geolocation.default_longitude")

    # we use OpenCage with a temporary API key for this migration because
    # Nominatim is too limited for bulk use
    geolocator = geopy.geocoders.OpenCage(
        api_key="801c91558c1f4338a62a43561fc961ab", timeout=3
    )

    brains = api.content.find(portal_type="imio.directory.Contact")
    for brain in brains:
        obj = brain.getObject()
        coordinates = IGeolocatable(obj).geolocation
        street_parts = [
            obj.number and str(obj.number) or "",
            obj.street,
            obj.complement,
        ]
        street = " ".join(filter(None, street_parts))
        entity_parts = [
            obj.zipcode and str(obj.zipcode) or "",
            obj.city,
        ]
        entity = " ".join(filter(None, entity_parts))
        country = translate_vocabulary_term(
            "imio.smartweb.vocabulary.Countries", obj.country
        )
        address = " ".join(filter(None, [street, entity, country]))
        if not address:
            # if we have no address, clear geolocation
            if obj.geolocation is not None:
                obj.geolocation = Geolocation("", "")
                obj.reindexObject(idxs=["longitude", "latitude"])
                logger.info(
                    f"Contact has no address : {obj.absolute_url()} --> cleared geolocation"
                )
            continue

        location = None
        if coordinates is None or not all(
            [coordinates.latitude, coordinates.longitude]
        ):
            # contact has no geolocation, see if we can find one
            location = geolocator.geocode(address)
            logger.info(
                f"Contact had no location : {obj.absolute_url()} --> {location.latitude} / {location.longitude}"
            )
        elif (
            coordinates.latitude == default_latitude
            and coordinates.longitude == default_longitude  # NOQA
        ):
            # contact was automatically geolocated on IMIO (by default)
            location = geolocator.geocode(address)
            logger.info(
                f"Contact was located on IMIO : {obj.absolute_url()} --> {location.latitude} / {location.longitude}"
            )
        else:
            # contact already has a geolocation, do nothing
            logger.info(f"Contact already has its location : {obj.absolute_url()}")
            continue

        if location:
            obj.geolocation = Geolocation(
                latitude=location.latitude, longitude=location.longitude
            )
            obj.reindexObject(idxs=["longitude", "latitude"])
