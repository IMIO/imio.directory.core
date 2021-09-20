# -*- coding: utf-8 -*-

from collective.geolocationbehavior.geolocation import IGeolocatable
from imio.directory.core.contents import IContact
from plone.api.portal import get_registry_record
from plone.indexer.decorator import indexer


@indexer(IContact)
def is_geolocated(obj):
    coordinates = IGeolocatable(obj).geolocation
    if not coordinates:
        return False
    longitude = coordinates.longitude
    latitude = coordinates.latitude
    defaut_latitude = get_registry_record("geolocation.default_latitude")
    defaut_longitude = get_registry_record("geolocation.default_longitude")
    return [latitude, longitude] != [defaut_latitude, defaut_longitude]
