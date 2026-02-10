# -*- coding: utf-8 -*-

from imio.directory.core.contents import IContact
from imio.directory.core.interfaces import IImioDirectoryCoreLayer
from imio.smartweb.common.contact_utils import ContactProperties
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
        contact_prop = ContactProperties(result)
        if contact_prop.is_empty_schedule() is False:
            opening_informations = contact_prop.get_opening_informations()
            result["opening_informations"] = opening_informations
            result["schedule_for_today"] = contact_prop.get_schedule_for_today(
                opening_informations
            )
        schedule = result["schedule"]
        if schedule is None:
            all_values_empty = True
        else:
            all_values_empty = all(
                value == ""
                for day_values in schedule.values()
                for value in day_values.values()
            )
        if all_values_empty is False:
            result["table_date"] = None
            table_date = []
            week_days = contact_prop.get_week_days()
            day_mapping = {
                "weekday_mon_short": "Monday",
                "weekday_tue_short": "Tuesday",
                "weekday_wed_short": "Wednesday",
                "weekday_thu_short": "Thursday",
                "weekday_fri_short": "Friday",
                "weekday_sat_short": "Saturday",
                "weekday_sun_short": "Sunday",
            }
            for a_date in week_days:
                formatted_schedule = contact_prop.formatted_schedule(
                    list(a_date.values())[0]
                )
                day = day_mapping.get([k for k, v in a_date.items()][0])
                dict = {day: formatted_schedule}
                table_date.append(dict)
            result["table_date"] = table_date
        else:
            result["table_date"] = None

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
            if orig_field == "description" and value:
                value = value.replace("**", "")
            summary[orig_field] = json_compatible(value)

        return summary
