# -*- coding: utf-8 -*-
from collective.schedulefield.behavior import ScheduledWithTitle
from datetime import datetime
from DateTime import DateTime
from imio.smartweb.common.rest.odwb import OdwbBaseEndpointGet
from imio.smartweb.common.utils import (
    activate_sending_data_to_odwb_for_staging as odwb_staging,
)
from imio.directory.core.contents import IEntity
from imio.directory.core.contents import IContact
from imio.directory.core.utils import get_entity_for_contact
from plone import api
from plone.formwidget.geolocation.geolocation import Geolocation
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

import json
import logging
import requests

logger = logging.getLogger("imio.events.core")


class OdwbEndpointGet(OdwbBaseEndpointGet):
    def __init__(self, context, request):
        imio_service = (
            "contacts-en-wallonie"
            if not odwb_staging()
            else "staging-contacts-en-wallonie"
        )
        pushkey = f"imio.directory.core.odwb_{imio_service}_pushkey"
        super(OdwbEndpointGet, self).__init__(context, request, imio_service, pushkey)

    def reply(self):
        if not super(OdwbEndpointGet, self).available():
            return
        url = f"{self.odwb_api_push_url}/{self.odwb_imio_service}/temps_reel/push/?pushkey={self.odwb_pushkey}"
        self.__datas__ = self.get_contacts()
        batched_lst = [
            self.__datas__[i : i + 1000] for i in range(0, len(self.__datas__), 1000)
        ]
        for elem in batched_lst:
            payload = json.dumps(elem)
            response_text = self.odwb_query(url, payload)
            logger.info(response_text)
        return response_text

    def get_contacts(self):
        lst_contacts = []
        if IPloneSiteRoot.providedBy(self.context) or IEntity.providedBy(self.context):
            brains = api.content.find(
                object_provides=IContact.__identifier__, review_state="published"
            )
            for brain in brains:
                if IEntity.providedBy(self.context):
                    if self.context.UID() not in brain.selected_entities:
                        continue
                contact_obj = brain.getObject()
                contact = Contact(contact_obj)
                lst_contacts.append(json.loads(contact.to_json()))
        elif IContact.providedBy(self.context):
            contact = Contact(self.context)
            lst_contacts.append(json.loads(contact.to_json()))
        return lst_contacts

    def remove(self):
        if not super(OdwbEndpointGet, self).available():
            return
        lst_contacts = []
        if IContact.providedBy(self.context):
            contact = Contact(self.context)
            lst_contacts.append(json.loads(contact.to_json()))
        url = f"{self.odwb_api_push_url}/{self.odwb_imio_service}/temps_reel/delete/?pushkey={self.odwb_pushkey}"
        payload = json.dumps(lst_contacts)
        headers = {"Content-Type": "application/json"}
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.text


class Contact:

    def __init__(self, context):
        # 2126b6ef314a4b3d9712732d5f036afc,
        self.id = context.id
        self.type = context.type  # get an id...
        self.title = context.title
        self.subtitle = context.subtitle
        # [{'label': None, 'type': 'fax', 'number': '+323874325'}]
        self.contact_phones = context.phones
        # [{'label': None, 'type': 'perso', 'mail': 'kamoulox@perdu.com'}]
        self.contact_emails = context.mails
        self.vat_number = context.vat_number
        self.description = context.description
        self.taxonomy_contact_category = context.taxonomy_contact_category
        self.topics = context.topics
        self.facilities = context.facilities
        self.image = f"{context.absolute_url()}/@@images/image/preview"
        self.coordinates = context.geolocation
        self.address_street_name = context.street
        self.address_street_number = context.number
        self.address_postal_code = context.zipcode
        self.address_city = context.city
        self.address_country = context.country
        self.urls = context.urls
        self.schedule = context.schedule
        self.multi_schedule = context.multi_schedule
        entity = get_entity_for_contact(context)
        self.owner_id = entity.UID()
        self.owner_name = entity.Title()
        # DateTime(2024/02/14 13:59:7.829612 GMT+1),
        self.creation_datetime = context.creation_date
        # DateTime(2024/02/14 15:51:52.128648 GMT+1),
        self.modification_datetime = context.modification_date

        # self.street_number_complement = context.complement
        # self.title_de = context.title_de
        # self.title_en = context.title_en
        # self.title_nl = context.title_nl
        # self.subtitle_de = context.subtitle_de
        # self.subtitle_en = context.subtitle_en
        # self.subtitle_nl = context.subtitle_nl
        # self.description_de = context.description_de
        # self.description_en = context.description_en
        # self.description_nl = context.description_nl
        # self.latitude = context.geolocation.latitude if context.geolocation else None
        # self.longitude = context.geolocation.longitude if context.geolocation else None
        # send to odwb?
        # self.private_phones = context.private_phones
        # self.private_mails = context.private_mails
        # self.private_urls = context.private_urls
        # self.private_note = context.private_note
        # ['e578c03fb70e448492ece56495686eae']
        # self.selected_entities = context.selected_entities
        # self.iam = context.iam
        # self.subjects = context.subjects
        # self.language = context.language
        # solr
        # self.searchwords = context.searchwords
        # DateTime(2024/02/14 13:59:00 GMT+1),
        # self.effective_date = context.effective_date

    def to_json(self):
        return json.dumps(self.__dict__, cls=ContactEncoder)


class ContactEncoder(json.JSONEncoder):

    def default(self, attr):
        if isinstance(attr, Geolocation):
            return {
                "lon": attr.longitude,
                "lat": attr.latitude,
            }
        elif isinstance(attr, DateTime):
            iso_datetime = attr.ISO8601()
            return iso_datetime
        elif isinstance(attr, datetime):
            return attr.isoformat()
        elif isinstance(attr, ScheduledWithTitle):
            start_date = None
            end_date = None
            if len(attr.dates) > 0:
                start_date = attr.dates[0].start_date.isoformat()
                end_date = attr.dates[0].end_date.isoformat()
            schedule = {
                "title": attr.title,
                "dates": {"start_date": start_date, "end_date": end_date},
                "schedule": attr.schedule,
            }
            return schedule
        else:
            return super().default(attr)


class OdwbEntitiesEndpointGet(OdwbBaseEndpointGet):

    def __init__(self, context, request):
        imio_service = (
            "entites-des-contacts-en-wallonie"
            if not odwb_staging()
            else "staging-entites-des-contacts-en-wallonie"
        )
        pushkey = f"imio.directory.core.odwb_{imio_service}_pushkey"
        super(OdwbEntitiesEndpointGet, self).__init__(
            context, request, imio_service, pushkey
        )

    def reply(self):
        if not super(OdwbEntitiesEndpointGet, self).available():
            return
        lst_entities = []
        brains = api.content.find(
            object_provides=IEntity.__identifier__, review_state="published"
        )
        for brain in brains:
            entity = {}
            entity["UID"] = brain.UID
            entity["id"] = brain.id
            entity["entity_title"] = brain.Title
            lst_entities.append(entity)
        self.__datas__ = lst_entities
        url = f"{self.odwb_api_push_url}/{self.odwb_imio_service}/temps_reel/push/?pushkey={self.odwb_pushkey}"
        payload = json.dumps(self.__datas__)
        headers = {"Content-Type": "application/json"}
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.text
