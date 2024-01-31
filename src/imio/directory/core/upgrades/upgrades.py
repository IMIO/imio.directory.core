# -*- coding: utf-8 -*-

from collective.geolocationbehavior.geolocation import IGeolocatable
from imio.directory.core.utils import get_entity_uid_for_contact
from imio.smartweb.common.faceted.utils import configure_faceted
from imio.smartweb.common.upgrades import upgrades
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


def reindex_searchable_text(context):
    upgrades.reindex_searchable_text(context)


def add_translations_indexes(context):
    catalog = api.portal.get_tool("portal_catalog")

    new_indexes = ["translated_in_nl", "translated_in_de", "translated_in_en"]
    indexes = catalog.indexes()
    indexables = []
    for new_index in new_indexes:
        if new_index in indexes:
            continue
        catalog.addIndex(new_index, "BooleanIndex")
        indexables.append(new_index)
        logger.info(f"Added BooleanIndex for field {new_index}")
    if len(indexables) > 0:
        logger.info(f"Indexing new indexes {', '.join(indexables)}")
        catalog.manage_reindexIndex(ids=indexables)

    new_metadatas = ["title_fr", "title_nl", "title_de", "title_en"]
    metadatas = list(catalog.schema())
    must_reindex = False
    for new_metadata in new_metadatas:
        if new_metadata in metadatas:
            continue
        catalog.addColumn(new_metadata)
        must_reindex = True
        logger.info(f"Added {new_metadata} metadata")
    if must_reindex:
        logger.info("Reindexing catalog for new metadatas")
        catalog.clearFindAndRebuild()


def add_contact_category_index(context):
    catalog = api.portal.get_tool("portal_catalog")
    indexes = catalog.indexes()
    new_index = "taxonomy_contact_category_for_filtering"
    if new_index in indexes:
        return
    catalog.addIndex(new_index, "KeywordIndex")
    idx = catalog._catalog.getIndex(new_index)
    idx.indexed_attrs = ("taxonomy_contact_category",)
    logger.info(f"Added KeywordIndex {new_index}")
    logger.info(f"Indexing new index {new_index}")
    catalog.manage_reindexIndex(ids=[new_index])


def reindex_catalog(context):
    catalog = api.portal.get_tool("portal_catalog")
    catalog.clearFindAndRebuild()


def remove_searchabletext_fr(context):
    catalog = api.portal.get_tool("portal_catalog")
    catalog.manage_delIndex("SearchableText_fr")


def remove_title_description_fr(context):
    catalog = api.portal.get_tool("portal_catalog")
    catalog.delColumn("title_fr")
    catalog.delColumn("description_fr")


def fix_datagridfields_values(context):
    brains = api.content.find(portal_type="imio.directory.Contact")
    for brain in brains:
        contact = brain.getObject()

        def fix_type(contact, field_name):
            if getattr(contact, field_name) is None:
                return
            fixed = False
            lines = getattr(contact, field_name)
            for line in lines:
                if isinstance(line["type"], tuple) or isinstance(line["type"], list):
                    line["type"] = line["type"][0]
                    fixed = True
            if fixed:
                contact._p_changed = 1
                logger.info(f"Fixed {field_name} types for {contact.absolute_url()}")

        fix_type(contact, "phones")
        fix_type(contact, "mails")
        fix_type(contact, "urls")
        fix_type(contact, "private_phones")
        fix_type(contact, "private_mails")
        fix_type(contact, "private_urls")


def fix_missing_values_for_facilities_lists(context):
    catalog = api.portal.get_tool("portal_catalog")
    with api.env.adopt_user(username="admin"):
        brains = api.content.find(portal_type=["imio.directory.Contact"])
        for brain in brains:
            must_reindex = False
            if brain.facilities is None:
                must_reindex = True
            obj = brain.getObject()
            if hasattr(obj, "facilities") and obj.facilities is None:
                obj.facilities = []
                must_reindex = True
                logger.info(f"Fixed None list for Facilities on {obj.absolute_url()}")
            if must_reindex:
                catalog.catalog_object(obj, idxs=["facilities"])
                logger.info(f"Reindexed Facilities on {obj.absolute_url()}")


def reindex_solr(context):
    portal = api.portal.get()
    maintenance = portal.unrestrictedTraverse("@@solr-maintenance")
    maintenance.clear()
    maintenance.reindex()
