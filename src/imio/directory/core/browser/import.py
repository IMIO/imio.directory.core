# -*- coding: utf-8 -*-

from collective.geolocationbehavior.geolocation import IGeolocatable
from imio.smartweb.common.utils import get_vocabulary
from imio.smartweb.locales import SmartwebMessageFactory as _
from io import StringIO
from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.formwidget.geolocation.geolocation import Geolocation
from plone.namedfile.field import NamedFile
from Products.statusmessages.interfaces import IStatusMessage
from urllib.parse import urlparse
from z3c.form import button
from z3c.form.form import Form
from zope.interface import Interface

import csv
import logging
import re

logger = logging.getLogger("imio.directory.core")


class ContactRow(object):
    def __init__(self, row_number, contact_row):
        # keep row values in var to make some validation tests.
        self.row_number = row_number
        self.contact_type = None if contact_row[0] == "" else str(contact_row[0])
        self.title = None if contact_row[1] == "" else str(contact_row[1])
        self.subtitle = contact_row[2]
        self.description = contact_row[3]
        self.street = contact_row[4]
        self.number = str(contact_row[5])
        self.complement = contact_row[6]
        self.zipcode = None if contact_row[7] == "" else str(contact_row[7])
        self.city = contact_row[8]
        self.country = contact_row[9]
        self.vat_number = None if contact_row[10] == "" else str(contact_row[10])
        self.geoloc = Geolocation(
            latitude=str(contact_row[11]), longitude=str(contact_row[12])
        )
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
        # we keep phone if at least label or type or number is completed
        self.phones = [
            phone
            for phone in self.phones
            if phone.get("type") or phone.get("label") or phone.get("number")
        ]
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
        self.mails = [
            mail
            for mail in self.mails
            if mail.get("type") or mail.get("label") or mail.get("mail_address")
        ]
        self.urls = [
            {"type": contact_row[31], "url": contact_row[32]},
            {"type": contact_row[33], "url": contact_row[34]},
            {"type": contact_row[35], "url": contact_row[36]},
        ]
        self.urls = [url for url in self.urls if url.get("type") or url.get("url")]
        # Remove duplicates values
        self.topics = list(set([contact_row[37], contact_row[38], contact_row[39]]))
        # Remove empty values
        self.topics = [topic for topic in self.topics if topic]
        # Remove duplicates values
        self.categories = list(set([contact_row[40], contact_row[41], contact_row[42]]))
        # Remove empty values
        self.categories = [category for category in self.categories if category]
        self.facilities = list(set([contact_row[43], contact_row[44], contact_row[45]]))
        self.facilities = [facility for facility in self.facilities if facility]
        self.iam = list(set([contact_row[46], contact_row[47], contact_row[48]]))
        self.iam = [me for me in self.iam if me]

    def uri_validator(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def check_voc(
        self,
        voc_name,
        contact_row_field,
        err_type_msg,
        err_suffix_msg,
        display_index=True,
    ):
        msg = []
        err_line_trad = _("Line")
        voc = get_vocabulary(voc_name)
        terms_token = [term.token for term in voc]
        for index, item in enumerate(contact_row_field, start=1):
            if item is None or item == "":
                """normally never pass in this test."""
                pass
            if item not in terms_token:
                err_type_msg = err_type_msg
                err_suffix_msg = err_suffix_msg
                msg.append(
                    f"{err_line_trad} {str(self.row_number)}, {err_type_msg}{index if display_index else ''}. {err_suffix_msg}"
                )
        return msg

    def validate(self):
        errors = []
        err_line_trad = _("Line")

        if self.contact_type is None:
            err_suffix_msg = _("you must set a type of contact.")
            errors.append(f"{err_line_trad} {str(self.row_number)}, {err_suffix_msg}")
        else:
            check_contact_type_msg = self.check_voc(
                "imio.directory.vocabulary.ContactTypes",
                [self.contact_type],
                _("Bad type of contact"),
                _("It's seems, this type of contact doesn't exist."),
                display_index=False,
            )
            if check_contact_type_msg:
                errors += check_contact_type_msg

        if self.title is None:
            err_suffix_msg = _("You must set a title to your contact.")
            errors.append(f"{err_line_trad} {str(self.row_number)}, {err_suffix_msg}")

        if self.zipcode is not None and self.zipcode.isdigit() is False:
            err_suffix_msg = _("Zipcode is not a number.")
            errors.append(f"{err_line_trad} {str(self.row_number)}, {err_suffix_msg}")

        if self.country:
            check_country_msg = self.check_voc(
                "imio.smartweb.vocabulary.Countries",
                [self.country],
                _("Bad country"),
                _(
                    "It's seems, this country doesn't exist. (set it with be, fr, nl,...) "
                ),
                display_index=False,
            )
            if check_country_msg:
                errors += check_country_msg

        regex = r"\+\d{7,15}"
        for index, phone in enumerate(self.phones, start=1):
            len_phone = len(phone.get("number"))
            if len_phone > 0 and re.match(regex, phone.get("number")) is None:
                """check phone number format"""
                err_type_msg = _("Bad phone")
                err_suffix_msg = _("Format (Good format sample : +32444556677) !")
                errors.append(
                    f"{err_line_trad} {str(self.row_number)}, {err_type_msg}{index} {err_suffix_msg}"
                )
            # phone.label is not required. So, only verify number and type.
            if (phone.get("number") and not phone.get("type")) or (
                not phone.get("number") and phone.get("type")
            ):
                """check phone number format"""
                err_type_msg = _("Bad phone")
                err_suffix_msg = _("Phone type or phone number not define !")
                errors.append(
                    f"{err_line_trad} {str(self.row_number)}, {err_type_msg}{index} {err_suffix_msg}"
                )
            # bad type of phone
            check_phones_msg = self.check_voc(
                "imio.directory.vocabulary.PhoneTypes",
                [phone.get("type")],
                _("Bad phone type"),
                _("It's seems, this type of phone doesn't exist."),
            )
            if check_phones_msg:
                errors += check_phones_msg

        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        for index, mail in enumerate(self.mails, start=1):
            len_mail = len(mail.get("mail_address"))
            if len_mail > 0 and re.fullmatch(regex, mail.get("mail_address")) is None:
                err_type_msg = _("Bad mail")
                err_suffix_msg = _("format (Good format sample : noreply@imio.be) !")
                errors.append(
                    f"{err_line_trad} {str(self.row_number)}, {err_type_msg}{index} {err_suffix_msg}"
                )
            # mail.label is not required. So, only verify mail_address and type.
            if (mail.get("mail_address") and not mail.get("type")) or (
                not mail.get("mail_address") and mail.get("type")
            ):
                """check phone number format"""
                err_type_msg = _("Bad mail")
                err_suffix_msg = _("Mail type or mail address not define !")
                errors.append(
                    f"{err_line_trad} {str(self.row_number)}, {err_type_msg}{index} {err_suffix_msg}"
                )
            # bad type of mail
            check_mails_msg = self.check_voc(
                "imio.directory.vocabulary.MailTypes",
                [mail.get("type")],
                _("Bad mail type"),
                _("It's seems, this type of mail doesn't exist."),
            )
            if check_mails_msg:
                errors += check_mails_msg

        for index, url in enumerate(self.urls, start=1):
            len_url = len(url.get("url"))
            if len_url > 0 and self.uri_validator(url.get("url")) is False:
                err_type_msg = _("Bad url")
                err_suffix_msg = _(
                    "format (Good format sample : https://www.imio.be, http://test.com,...) !"
                )
                errors.append(
                    f"{err_line_trad} {str(self.row_number)}, {err_type_msg}{index} {err_suffix_msg}"
                )
            # bad type of site
            check_urls_msg = self.check_voc(
                "imio.directory.vocabulary.SiteTypes",
                [url.get("type")],
                _("Bad site type"),
                _("It's seems, this type of site doesn't exist."),
            )
            if check_urls_msg:
                errors += check_urls_msg

        check_topics_msg = self.check_voc(
            "imio.smartweb.vocabulary.Topics",
            self.topics,
            _("Bad topic"),
            _("It's seems, this topic doesn't exist."),
        )
        if check_topics_msg:
            errors += check_topics_msg

        check_facilities_msg = self.check_voc(
            "imio.directory.vocabulary.Facilities",
            self.facilities,
            _("Bad facility"),
            _("It's seems, this facility doesn't exist."),
        )
        if check_facilities_msg:
            errors += check_facilities_msg

        check_iam_msg = self.check_voc(
            "imio.smartweb.vocabulary.IAm",
            self.iam,
            _("Bad iam item"),
            _("It's seems, this iam item doesn't exist."),
        )
        if check_iam_msg:
            errors += check_iam_msg

        return errors


class IImportCSVFormSchema(Interface):
    """Define fields used on the form"""

    csv_file = NamedFile(title=_("CSV file"))


class ImportContactForm(AutoExtensibleForm, Form):
    """ """

    label = _("Import contacts")
    schema = IImportCSVFormSchema  # Form schema
    ignoreContext = True
    contact_rows = []

    def validateCSV(self, data):
        """ """
        reader = csv.reader(
            StringIO(data.decode("utf-8")),
            delimiter=",",
            dialect="excel",
            quotechar='"',
        )

        index = 1
        # I give a temporary index for each cols in csv file
        # colnumber = next(reader)
        # index += 1

        # Pass csv header row.
        next(reader)
        index += 1

        errors = []
        for row in reader:
            # process the data here as needed for the specific case
            contact_row = ContactRow(index, row)
            self.contact_rows.append(contact_row)
            errors += contact_row.validate()
            index += 1

        return errors

    def process(self):
        """ """
        updated = 0
        for contact_row in self.contact_rows:
            self.create_contact(contact_row)
            updated += 1
        return updated

    def create_contact(self, contact_row):
        # use cas : we are in an entity.
        contact = api.content.create(
            container=self.context,
            type="imio.directory.Contact",
            title=contact_row.title,
        )
        contact.type = contact_row.contact_type
        contact.subtitle = contact_row.subtitle
        contact.description = contact_row.description
        contact.street = contact_row.street
        contact.number = contact_row.number
        contact.complement = contact_row.complement
        contact.zipcode = (
            int(contact_row.zipcode.strip()) if contact_row.zipcode else None
        )
        contact.city = contact_row.city
        contact.country = contact_row.country
        contact.vat_number = contact_row.vat_number
        IGeolocatable(contact).geolocation = contact_row.geoloc
        contact.phones = contact_row.phones
        contact.mails = contact_row.mails
        contact.urls = contact_row.urls
        contact.topics = contact_row.topics
        contact.facilities = contact_row.facilities
        contact.iam = contact_row.iam
        return contact.title

    @button.buttonAndHandler(_("Import"), name="import")
    def action_import(self, action):
        data, errors = self.extractData()
        number = None
        if errors:
            self.status = self.formErrorsMessage
            return
        # get datas
        file = data["csv_file"].data

        # Validate
        errors = self.validateCSV(file)
        if errors:
            self.status = "\n".join(errors)
        else:
            # Process
            number = self.process()

        # If everything was ok post success note
        if number is not None:
            # mark only as finished if we get the new object
            IStatusMessage(self.request).addStatusMessage(
                _("Processed: {0}").format(number), "info"
            )
