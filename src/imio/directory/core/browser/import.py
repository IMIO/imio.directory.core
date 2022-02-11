# -*- coding: utf-8 -*-

from collective.geolocationbehavior.geolocation import IGeolocatable
from imio.directory.core.config import PHONE_RE
from imio.directory.core.config import URL_RE
from imio.smartweb.common.utils import geocode_object
from imio.smartweb.common.utils import get_vocabulary
from imio.smartweb.locales import SmartwebMessageFactory as _
from io import StringIO
from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.namedfile.field import NamedFile
from Products.CMFPlone.PloneTool import EMAIL_RE
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form.form import Form
from z3c.form.interfaces import NOT_CHANGED
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import Interface

import csv
import logging
import re

logger = logging.getLogger("imio.directory.core")


def convert_empty_val(value):
    """Ensure empty values are all None"""
    if value in ["---", ""]:
        # --- is used as blank field in sheet template listbox
        return None
    return str(value).strip()


def cleanup(lst):
    """Remove duplicates and empty values from list"""
    lst = list(set(lst))
    lst = [val for val in lst if convert_empty_val(val)]
    return lst


def is_in_vocab(voc_name, value):
    """Check if value is in specified vocabulary"""
    voc = get_vocabulary(voc_name)
    terms_token = [term.token for term in voc]
    return value in terms_token


def validate_type(value):
    if not value:
        return
    elif not is_in_vocab("imio.directory.vocabulary.ContactTypes", value):
        return _("Chosen contact type '${val}' doesn't exist.", mapping={"val": value})


def validate_country(value):
    if not value:
        return
    elif not is_in_vocab("imio.smartweb.vocabulary.Countries", value):
        return _(
            "Chosen country '${val}' doesn't exist (good format sample: be, fr).",
            mapping={"val": value},
        )


def validate_phone(value, value_type):
    errors = []
    if re.match(PHONE_RE, value) is None:
        msg = _(
            "Bad phone format '${val}' (good format sample: +32444556677).",
            mapping={"val": value},
        )
        errors.append(msg)

    if not is_in_vocab("imio.directory.vocabulary.PhoneTypes", value_type):
        msg = _(
            "Chosen phone type '${val}' doesn't exist.",
            mapping={"val": value_type},
        )
        errors.append(msg)
    return errors


def validate_mail(value, value_type):
    errors = []
    if re.match(EMAIL_RE, value) is None:
        msg = _(
            "Bad mail format '${val}' (good format sample: noreply@imio.be).",
            mapping={"val": value},
        )
        errors.append(msg)

    if not is_in_vocab("imio.directory.vocabulary.MailTypes", value_type):
        msg = _(
            "Chosen mail type '${val}' doesn't exist.",
            mapping={"val": value_type},
        )
        errors.append(msg)
    return errors


def validate_url(value, value_type):
    errors = []
    if re.match(URL_RE, value) is None:
        msg = _(
            "Bad URL format '${val}' (good format sample: https://www.imio.be).",
            mapping={"val": value},
        )
        errors.append(msg)

    if not is_in_vocab("imio.directory.vocabulary.SiteTypes", value_type):
        msg = _(
            "Chosen URL type '${val}' doesn't exist.",
            mapping={"val": value_type},
        )
        errors.append(msg)
    return errors


class ContactRow(object):
    def __init__(self, contact_row):
        self.contact_type = convert_empty_val(contact_row[0])
        self.title = convert_empty_val(contact_row[1])
        self.subtitle = convert_empty_val(contact_row[2])
        self.description = convert_empty_val(contact_row[3])
        self.street = convert_empty_val(contact_row[4])
        self.number = convert_empty_val(contact_row[5])
        self.complement = convert_empty_val(contact_row[6])
        self.zipcode = convert_empty_val(contact_row[7])
        self.city = convert_empty_val(contact_row[8])
        self.country = convert_empty_val(contact_row[9])
        self.vat_number = convert_empty_val(contact_row[10])
        self.latitude = convert_empty_val(contact_row[11])
        self.longitude = convert_empty_val(contact_row[12])
        self.phones = [
            {
                "label": contact_row[13],
                "type": contact_row[14],
                "number": contact_row[15],
            },
            {
                "label": contact_row[16],
                "type": contact_row[17],
                "number": contact_row[18],
            },
            {
                "label": contact_row[19],
                "type": contact_row[20],
                "number": contact_row[21],
            },
        ]
        self.phones = [p for p in self.phones if convert_empty_val(p.get("number"))]
        for phone in self.phones:
            phone["number"] = phone["number"].replace(" ", "")
            if not phone["number"].startswith("+"):
                # add '+' in phone number if missing
                phone["number"] = f"+{phone['number']}"
        self.mails = [
            {
                "label": contact_row[22],
                "type": contact_row[23],
                "mail_address": contact_row[24],
            },
            {
                "label": contact_row[25],
                "type": contact_row[26],
                "mail_address": contact_row[27],
            },
            {
                "label": contact_row[28],
                "type": contact_row[29],
                "mail_address": contact_row[30],
            },
        ]
        self.mails = [m for m in self.mails if convert_empty_val(m.get("mail_address"))]
        for mail in self.mails:
            mail["mail_address"] = mail["mail_address"].strip()
        self.urls = [
            {"type": contact_row[31], "url": contact_row[32]},
            {"type": contact_row[33], "url": contact_row[34]},
            {"type": contact_row[35], "url": contact_row[36]},
        ]
        self.urls = [u for u in self.urls if convert_empty_val(u.get("url"))]
        for url in self.urls:
            url["url"] = url["url"].strip()
            if not url["url"].startswith("http"):
                # add 'https://' in website url if missing
                url["url"] = f"https://{url['url']}"
        self.topics = cleanup([contact_row[37], contact_row[38], contact_row[39]])
        # XXX categories are not inserted yet
        self.categories = cleanup([contact_row[40], contact_row[41], contact_row[42]])
        self.facilities = cleanup([contact_row[43], contact_row[44], contact_row[45]])
        self.iam = cleanup([contact_row[46], contact_row[47], contact_row[48]])

    def validate(self):
        errors = []
        if self.contact_type is None:
            errors.append(_("Contact type is missing."))
        else:
            errors.append(validate_type(self.contact_type))

        if self.title is None:
            errors.append(_("Contact title is missing."))

        if self.zipcode is not None and not self.zipcode.isdigit():
            errors.append(
                _("Zipcode '${val}' is not a number.", mapping={"val": self.zipcode})
            )

        errors.append(validate_country(self.country))

        for phone in self.phones:
            errors += validate_phone(phone.get("number"), phone.get("type"))

        for mail in self.mails:
            errors += validate_mail(mail.get("mail_address"), mail.get("type"))

        for url in self.urls:
            errors += validate_url(url.get("url"), url.get("type"))

        for topic in self.topics:
            if not is_in_vocab("imio.smartweb.vocabulary.Topics", topic):
                errors.append(
                    _("Chosen topic '${val}' doesn't exist.", mapping={"val": topic})
                )

        for facility in self.facilities:
            if not is_in_vocab("imio.directory.vocabulary.Facilities", facility):
                errors.append(
                    _(
                        "Chosen facility '${val}' doesn't exist.",
                        mapping={"val": facility},
                    )
                )

        for iam in self.iam:
            if not is_in_vocab("imio.smartweb.vocabulary.IAm", iam):
                errors.append(
                    _("Chosen i am term '${val}' doesn't exist.", mapping={"val": iam})
                )

        errors = [e for e in errors if e]
        return errors


class ContactsImporter(object):
    contact_rows = []

    def __init__(self, data):
        self.contact_rows = []
        reader = csv.reader(
            StringIO(data.decode("utf-8")),
            delimiter=";",
            dialect="excel",
            quotechar='"',
        )
        # Skip csv header row
        next(reader)
        for row in reader:
            contact_row = ContactRow(row)
            self.contact_rows.append(contact_row)

    def validate(self):
        errors = {}
        for index, contact_row in enumerate(self.contact_rows, start=1):
            row_errors = contact_row.validate()
            if row_errors:
                errors[index] = [translate(r, context=getRequest()) for r in row_errors]
        return errors

    def create_contact(self, contact_row, container):
        contact = api.content.create(
            container=container,
            type="imio.directory.Contact",
            title=contact_row.title,
        )
        contact.type = contact_row.contact_type
        contact.subtitle = contact_row.subtitle
        contact.description = contact_row.description
        contact.street = contact_row.street
        contact.number = contact_row.number
        contact.complement = contact_row.complement
        if contact_row.zipcode:
            contact.zipcode = int(contact_row.zipcode.strip())
        contact.city = contact_row.city
        contact.country = contact_row.country
        contact.vat_number = contact_row.vat_number
        if contact_row.latitude and contact_row.longitude:
            IGeolocatable(contact).geolocation = Geolocation(
                latitude=contact_row.latitude, longitude=contact_row.longitude
            )
        contact.phones = contact_row.phones
        contact.mails = contact_row.mails
        contact.urls = contact_row.urls
        contact.topics = contact_row.topics
        contact.facilities = contact_row.facilities
        contact.iam = contact_row.iam
        geocode_object(contact)
        contact.reindexObject()

    def create_contacts(self, container):
        for contact_row in self.contact_rows:
            self.create_contact(contact_row, container)
        return len(self.contact_rows)


class IImportCSVFormSchema(Interface):
    csv_file = NamedFile(title=_("CSV file"))


class ImportContactForm(AutoExtensibleForm, Form):
    label = _("Import contacts")
    schema = IImportCSVFormSchema
    template = ViewPageTemplateFile("import.pt")
    ignoreContext = True

    @button.buttonAndHandler(_("Import"), name="import")
    def action_import(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        csv_file = data["csv_file"]
        if csv_file is NOT_CHANGED:
            # avoid traceback or double treatment
            return

        importer = ContactsImporter(csv_file.data)

        # validate contacts values
        errors = importer.validate()
        if errors:
            self.status = self.formErrorsMessage
            self.errors_details = errors
        else:
            # import contacts
            number = importer.create_contacts(self.context)
            self.status = _(
                "Imported ${number} contacts successfully !", mapping={"number": number}
            )
