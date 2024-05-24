# -*- coding: utf-8 -*-

from collective.taxonomy.interfaces import ITaxonomy
from imio.smartweb.common.utils import translate_vocabulary_term
from plone import api
from Products.Five.browser import BrowserView
from zope.component import getSiteManager

import io
import json
import pandas

# "exceptional_closure",
# "multi_schedule",
ordered_signifiant_columns = [
    "title",
    "title_nl",
    "title_de",
    "title_en",
    "subtitle",
    "subtitle_nl",
    "subtitle_de",
    "subtitle_en",
    "description_nl",
    "description_de",
    "description_en",
    "street",
    "number",
    "zipcode",
    "city",
    "country",
    "country.title",
    "complement",
    "is_geolocated",
    "geolocation.latitude",
    "geolocation.longitude",
    "mails",
    "phones",
    "urls",
    "private_mails",
    "private_phones",
    "private_urls",
    "private_note",
    "vat_number",
    "schedule",
    "schedule.monday.morningstart",
    "schedule.monday.morningend",
    "schedule.monday.afternoonstart",
    "schedule.monday.afternoonend",
    "schedule.monday.comment",
    "schedule.tuesday.morningstart",
    "schedule.tuesday.morningend",
    "schedule.tuesday.afternoonstart",
    "schedule.tuesday.afternoonend",
    "schedule.tuesday.comment",
    "schedule.wednesday.morningstart",
    "schedule.wednesday.morningend",
    "schedule.wednesday.afternoonstart",
    "schedule.wednesday.afternoonend",
    "schedule.wednesday.comment",
    "schedule.thursday.morningstart",
    "schedule.thursday.morningend",
    "schedule.thursday.afternoonstart",
    "schedule.thursday.afternoonend",
    "schedule.thursday.comment",
    "schedule.friday.morningstart",
    "schedule.friday.morningend",
    "schedule.friday.afternoonstart",
    "schedule.friday.afternoonend",
    "schedule.friday.comment",
    "schedule.saturday.morningstart",
    "schedule.saturday.morningend",
    "schedule.saturday.afternoonstart",
    "schedule.saturday.afternoonend",
    "schedule.saturday.comment",
    "schedule.sunday.morningstart",
    "schedule.sunday.morningend",
    "schedule.sunday.afternoonstart",
    "schedule.sunday.afternoonend",
    "schedule.sunday.comment",
    "type",
    "facilities",
    "iam",
    "taxonomy_contact_category",
    "topics",
    "subject",
    "modified",
]


class ExportView(BrowserView):

    def __call__(self):
        self.lang = api.portal.get_current_language()
        datas = self.get_datas()
        items = datas.get("items", None)
        if not items:
            return self.request.response.setStatus(204)
        df = pandas.json_normalize(items)
        dataframe_columns = list(df)
        set1 = set(ordered_signifiant_columns)
        set2 = set(dataframe_columns)
        intersection = set1.intersection(set2)
        columns = sorted(
            intersection, key=lambda x: ordered_signifiant_columns.index(x)
        )
        df = df[columns]

        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False, encoding="utf-8", sep="|")

        self.request.response.setHeader(
            "Content-Disposition", 'attachment; filename="export.csv"'
        )
        self.request.response.setHeader("Content-Type", "text/csv")
        self.request.response.write(csv_buffer.getvalue())
        return self.request.response

    def get_datas(self):
        context_path = "/".join(self.context.getPhysicalPath())
        query = {
            "portal_type": "imio.directory.Contact",
            "path": {"query": context_path, "depth": -1},
            "review_state": ["published", "private"],
        }

        # Executing the query
        brains = api.portal.get_tool("portal_catalog")(query)
        datas = []
        for brain in brains:
            obj = brain.getObject()
            items = {}
            for attribute in ordered_signifiant_columns:
                try:
                    json.dumps(getattr(obj, attribute, None))
                except TypeError:
                    if attribute == "modified":
                        items[attribute] = getattr(obj, attribute)().strftime(
                            "%Y-%m-%d %H:%M:%S.%f"
                        )
                    else:
                        continue
                else:
                    if attribute not in items:
                        items[attribute] = getattr(obj, attribute, None)
                if isinstance(getattr(obj, attribute, None), dict):
                    dict_obj = getattr(obj, attribute, None)
                    for k, v in dict_obj.items():
                        for v, v_value in v.items():
                            items[f"schedule.{k}.{v}"] = v_value
                if (
                    attribute == "geolocation.latitude"
                    or attribute == "geolocation.longitude"
                ):
                    attributes = attribute.split(".")
                    first_attr = getattr(obj, attributes[0], None)
                    items[f"{attributes[0]}.{attributes[1]}"] = (
                        None
                        if first_attr is None
                        else getattr(first_attr, attributes[1], None)
                    )
                if attribute == "taxonomy_contact_category":
                    items["taxonomy_contact_category"] = self.get_taxonomy_label_by_id(
                        obj
                    )
                if attribute == "iam" and getattr(obj, attribute, None) is not None:
                    items["iam"] = self.get_vocabulary_label(
                        "imio.smartweb.vocabulary.IAm", items["iam"]
                    )
                if (
                    attribute == "facilities"
                    and getattr(obj, attribute, None) is not None
                ):
                    items["facilities"] = self.get_vocabulary_label(
                        "imio.directory.vocabulary.Facilities", items["facilities"]
                    )
                if attribute == "topics" and getattr(obj, attribute, None) is not None:
                    items["topics"] = self.get_vocabulary_label(
                        "imio.smartweb.vocabulary.Topics", items["topics"]
                    )
                if attribute == "type" and getattr(obj, attribute, None) is not None:
                    items["type"] = self.get_vocabulary_label(
                        "imio.directory.vocabulary.ContactTypes", items["type"]
                    )
            datas.append(items)
        return {"items": datas, "items_total": len(datas)}

    def get_taxonomy_label_by_id(self, obj):
        sm = getSiteManager()
        utility = sm.queryUtility(
            ITaxonomy, name="collective.taxonomy.contact_category"
        )
        categories = []
        for category in getattr(obj, "taxonomy_contact_category", []) or []:
            categories.append(
                utility.translate(category, context=obj, target_language=self.lang)
            )
        return categories

    def get_vocabulary_label(self, voc, ids):
        ids = [ids] if not isinstance(ids, list) else ids
        labels = []
        for id in ids:
            label = translate_vocabulary_term(voc, id, self.lang)
            labels.append(label)
        return labels
