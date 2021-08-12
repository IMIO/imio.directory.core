# -*- coding: utf-8 -*-

from collective.geolocationbehavior.geolocation import IGeolocatable
from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.row import DictRow
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import schema
from plone.app.content.namechooser import NormalizingNameChooser
from plone.autoform import directives
from plone.autoform.directives import read_permission
from plone.autoform.directives import widget
from plone.autoform.directives import write_permission
from plone.dexterity.content import Container
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.model import Fieldset
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.converter import FormatterValidationError
from zope.container.interfaces import INameChooser
from zope.interface import Interface
from zope.interface import implementer

import re


def phone_constraint(value):
    if re.match(r"\+\d{7,15}", value) is None:
        raise FormatterValidationError(_(u"Bad phone format"), value)
    return True


class IPhoneRowSchema(Interface):

    label = schema.TextLine(
        title=_(u"Label (direction, Main number,...)"),
        description=_(u""),
        required=False,
    )

    type = schema.Choice(
        title=_(u"Type"),
        source="imio.directory.vocabulary.PhoneTypes",
        description=_(u""),
        required=True,
    )

    number = schema.TextLine(
        title=_(u"Number (format: +32475010203)"),
        required=True,
        constraint=phone_constraint,
    )


class IMailRowSchema(Interface):

    label = schema.TextLine(
        title=_(u"Label (Secretariat, Manager office, Sales,...)"),
        description=_(u""),
        required=False,
    )

    type = schema.Choice(
        title=_(u"Type"),
        source="imio.directory.vocabulary.MailTypes",
        description=_(u""),
        required=True,
    )

    mail_address = schema.Email(title=_(u"E-mail"), required=True)


class IUrlRowSchema(Interface):

    type = schema.Choice(
        title=_(u"Type"),
        source="imio.directory.vocabulary.SiteTypes",
        description=_(u""),
        required=True,
    )

    url = schema.URI(title=_(u"Url"), required=True)


class IAddress(model.Schema):

    model.fieldset(
        "address",
        label=_(u"Address"),
        fields=["street", "number", "complement", "zipcode", "city", "country"],
    )
    street = schema.TextLine(title=_(u"Street"), required=False)
    number = schema.TextLine(title=_(u"Number"), required=False)
    complement = schema.TextLine(title=_(u"Complement"), required=False)
    zipcode = schema.Int(title=_(u"Zipcode"), required=False)
    city = schema.TextLine(title=_(u"City"), required=False)
    country = schema.Choice(
        title=_(u"Country"),
        source="imio.smartweb.vocabulary.Countries",
        default="be",
        required=False,
    )


# Move geolocation field to our Address fieldset
address_fieldset = Fieldset(
    "address",
    fields=["geolocation"],
)
IGeolocatable.setTaggedValue(FIELDSETS_KEY, [address_fieldset])


class IContactInformations(model.Schema):

    model.fieldset(
        "contact_informations",
        label=_(u"Contact informations"),
        fields=["vat_number", "phones", "mails", "urls"],
    )
    vat_number = schema.TextLine(title=_(u"VAT number"), required=False)
    phones = schema.List(
        title=_(u"Phones"),
        value_type=DictRow(
            title=u"Value",
            schema=IPhoneRowSchema,
        ),
        required=False,
    )
    widget(phones=DataGridFieldFactory)

    mails = schema.List(
        title=_(u"E-mails"),
        value_type=DictRow(
            title=u"Value",
            schema=IMailRowSchema,
        ),
        required=False,
    )
    widget(mails=DataGridFieldFactory)

    urls = schema.List(
        title=_(u"URLs"),
        value_type=DictRow(
            title=u"Value",
            schema=IUrlRowSchema,
        ),
        required=False,
    )
    widget(urls=DataGridFieldFactory)


class IPrivateContactInformations(model.Schema):

    model.fieldset(
        "private_contact_informations",
        label=_(u"Private contact informations"),
        fields=["private_phones", "private_mails", "private_urls", "private_note"],
    )
    private_phones = schema.List(
        title=_(u"Phones"),
        value_type=DictRow(
            title=u"Value",
            schema=IPhoneRowSchema,
        ),
        required=False,
    )
    widget(private_phones=DataGridFieldFactory)

    private_mails = schema.List(
        title=_(u"E-mails"),
        value_type=DictRow(
            title=u"Value",
            schema=IMailRowSchema,
        ),
        required=False,
    )
    widget(private_mails=DataGridFieldFactory)

    private_urls = schema.List(
        title=_(u"URLs"),
        value_type=DictRow(
            title=u"Value",
            schema=IUrlRowSchema,
        ),
        required=False,
    )
    widget(private_urls=DataGridFieldFactory)

    private_note = schema.Text(title=_(u"Internal note"), required=False)

    read_permission(
        private_phones="imio.directory.core.ViewContactPrivateInformations",
        private_mails="imio.directory.core.ViewContactPrivateInformations",
        private_urls="imio.directory.core.ViewContactPrivateInformations",
        private_note="imio.directory.core.ViewContactPrivateInformations",
    )
    write_permission(
        private_phones="imio.directory.core.ModifyContactPrivateInformations",
        private_mails="imio.directory.core.ModifyContactPrivateInformations",
        private_urls="imio.directory.core.ModifyContactPrivateInformations",
        private_note="imio.directory.core.ModifyContactPrivateInformations",
    )


class IContact(IPrivateContactInformations, IContactInformations, IAddress):
    """ """

    directives.order_before(type="IBasic.title")
    directives.widget(type=RadioFieldWidget)
    type = schema.Choice(
        title=_(u"Type"),
        source="imio.directory.vocabulary.ContactTypes",
        required=True,
    )

    directives.order_after(subtitle="IBasic.title")
    subtitle = schema.TextLine(title=_(u"Subtitle"), required=False)

    logo = NamedBlobImage(title=_(u"Logo"), description=_(u""), required=False)


@implementer(IContact)
class Contact(Container):
    """ """


@implementer(INameChooser)
class ContactNameChooser(NormalizingNameChooser):
    def chooseName(self, name, obj):
        if IContact.providedBy(obj):
            return obj.UID()
        return super(ContactNameChooser, self).chooseName(name, obj)
