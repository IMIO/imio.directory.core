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
    if contact.gender:
        vcard.add("gender")
        vcard.gender.value = contact.gender
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
    addr = {
        "number": contact.number or "",
        "street": contact.street or "",
        "additional": contact.complement or "",
        "zipcode": str(contact.zipcode or ""),
        "city": contact.city or "",
        "region": "",
        "country": contact.country or "",
    }

    if any(addr.values()):
        vcard.add("adr")
        vcard.adr.value = vobject.vcard.Address(
            street=addr.get("street"),
            city=addr.get("city"),
            region=addr.get("region"),
            code=addr.get("zipcode"),
            country=addr.get("country"),
            box=addr.get("number"),
            extended=addr.get("additional"),
        )

    return vcard
