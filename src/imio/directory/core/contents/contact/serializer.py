# -*- coding: utf-8 -*-

from imio.directory.core.contents import IContact
from imio.directory.core.interfaces import IImioDirectoryCoreLayer
from imio.smartweb.common.rest.utils import get_restapi_query_lang
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from plone.restapi.serializer.summary import DefaultJSONSummarySerializer
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IContact, IImioDirectoryCoreLayer)
class SerializeContactToJson(SerializeFolderToJson):
    def __call__(self, version=None, include_items=True):
        result = super(SerializeContactToJson, self).__call__(
            version, include_items=True
        )
        version = "current" if version is None else version
        obj = self.getVersion(version)

        query = self.request.form
        lang = get_restapi_query_lang(query)
        if lang and lang != "fr":
            result["title"] = getattr(obj, f"title_{lang}")
            result["subtitle"] = getattr(obj, f"subtitle_{lang}")
            result["description"] = getattr(obj, f"description_{lang}")

        # maybe not necessary :
        result["title_fr"] = obj.title
        result["subtitle_fr"] = obj.subtitle
        result["description_fr"] = obj.description

        result["is_geolocated"] = obj.is_geolocated
        return result


@implementer(ISerializeToJsonSummary)
@adapter(Interface, IImioDirectoryCoreLayer)
class ContactJSONSummarySerializer(DefaultJSONSummarySerializer):
    def __call__(self):
        summary = super(ContactJSONSummarySerializer, self).__call__()

        query = self.request.form
        lang = get_restapi_query_lang(query)
        if lang == "fr":
            # nothing to go, fr is the default language
            return summary

        obj = IContentListingObject(self.context)
        for orig_field in ["title", "description"]:
            field = f"{orig_field}_{lang}"
            accessor = self.field_accessors.get(field, field)
            value = getattr(obj, accessor, None)
            try:
                if callable(value):
                    value = value()
            except WorkflowException:
                summary[orig_field] = None
                continue
            if orig_field == "description" and value is not None:
                value = value.replace("**", "")
            summary[orig_field] = json_compatible(value)

        return summary
