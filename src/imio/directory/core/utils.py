# -*- coding: utf-8 -*-

from imio.directory.core.contents.entity.content import IEntity
from plone import api
from Products.CMFPlone.utils import parent
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import base64
import geopy
import vobject


def get_entity_uid_for_contact(contact):
    obj = contact
    while not IEntity.providedBy(obj):
        obj = parent(obj)
    entity = obj
    return entity.UID()


def geocode_contact(contact):
    street_parts = [
        contact.number and str(contact.number) or "",
        contact.street,
        contact.complement,
    ]
    street = " ".join(filter(None, street_parts))
    entity_parts = [
        contact.zipcode and str(contact.zipcode) or "",
        contact.city,
    ]
    entity = " ".join(filter(None, entity_parts))
    country = translate_vocabulary_term(
        "imio.smartweb.vocabulary.Countries", contact.country
    )
    address = " ".join(filter(None, [street, entity, country]))
    if not address:
        return
    geolocator = geopy.geocoders.Nominatim(user_agent="contact@imio.be", timeout=3)
    location = geolocator.geocode(address)
    if location:
        contact.geolocation.latitude = location.latitude
        contact.geolocation.longitude = location.longitude


def translate_vocabulary_term(vocabulary, term):
    if term is None:
        return ""
    factory = getUtility(IVocabularyFactory, vocabulary)
    vocabulary = factory(api.portal.get())
    term = vocabulary.getTerm(term)
    return term and term.title or ""


def get_vcard(contact):
    vcard = vobject.vCard()

    vcard.add("fn")
    vcard.fn.value = contact.Title()
    emails = contact.mails or []
    for email in emails:
        vcard.add("email")
        vcard.email.type_param = email.get("type")
        vcard.email.value = email.get("mail_address")

    phones = contact.phones or []
    for phone in phones:
        vcard.add("tel")
        vcard.tel.type_param = phone.get("type")
        vcard.tel.value = phone.get("number")

    urls = contact.urls or []
    for url in urls:
        vcard.add("url")
        vcard.url.type_param = url.get("type")
        vcard.url.value = url.get("url")

    addr = {
        "number": contact.number or "",
        "street": contact.street or "",
        "additional": contact.complement or "",
        "zipcode": str(contact.zipcode or ""),
        "city": contact.city or "",
    }
    if any(addr.values()):
        # If any field values (except country) has been filled in, we consider
        # that an address has been encooded
        vcard.add("adr")
        vcard.adr.value = vobject.vcard.Address(
            street=addr.get("street"),
            city=addr.get("city"),
            region="",
            code=addr.get("zipcode"),
            country=translate_vocabulary_term(
                "imio.smartweb.vocabulary.Countries", contact.country
            ),
            box=addr.get("number"),
            extended=addr.get("additional"),
        )
    if contact.logo:
        o = vcard.add("PHOTO;ENCODING=b;TYPE=image/jpeg")
        base64_bytes = base64.b64encode(contact.logo.data)
        o.value = base64_bytes.decode("utf-8")
    return vcard
