# -*- coding: utf-8 -*-
import vobject


def get_vcard(contact):
    vcard = vobject.vCard()

    firstname = contact.firstname or ""
    lastname = contact.lastname or ""
    vcard.add("n")
    vcard.n.value = vobject.vcard.Name(family=lastname, given=firstname)
    vcard.add("fn")
    vcard.fn.value = " ".join([e for e in (firstname, lastname) if e])
    vcard.add("gender")
    vcard.gender.value = contact.gender

    emails = contact.mails
    for email in emails:
        vcard.add("email")
        vcard.email.type_param = email.type
        vcard.email.value = email.mail_address

    phones = contact.phones
    for phone in phones:
        vcard.add("tel")
        vcard.tel.type_param = phone.type
        vcard.tel.value = phone.number

    vcard.add("adr")
    country = contact.country
    region = ""
    zip_code = contact.zipcode
    city = contact.city
    street = contact.street
    number = contact.number
    additional = contact.complement
    vcard.adr.value = vobject.vcard.Address(
        street=street,
        city=city,
        region=region,
        code=zip_code,
        country=country,
        box=number,
        extended=additional,
    )

    return vcard
