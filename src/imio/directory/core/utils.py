# -*- coding: utf-8 -*-
import base64
import vobject


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
    if contact.logo:
        o = vcard.add("PHOTO;ENCODING=b;TYPE=image/jpeg")
        base64_bytes = base64.b64encode(contact.logo.data)
        o.value = base64_bytes.decode("utf-8")
    return vcard
