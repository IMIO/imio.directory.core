# -*- coding: utf-8 -*-

from imio.directory.core.contents import IContact
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IContact, Interface)
class SerializeContactToJson(SerializeFolderToJson):
    def __call__(self, version=None, include_items=True):
        result = super(SerializeContactToJson, self).__call__(version, include_items)
        version = "current" if version is None else version
        obj = self.getVersion(version)
        result["is_geolocated"] = obj.is_geolocated
        return result
