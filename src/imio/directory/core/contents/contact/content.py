# -*- coding: utf-8 -*-

from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.row import DictRow
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import schema
from plone.app.content.namechooser import NormalizingNameChooser
from plone.autoform.directives import widget
from plone.dexterity.content import Container
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope.container.interfaces import INameChooser
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import Invalid
import re


def phone_constraint(value):
    if re.match(r"\+\d{7,15}", value) is None:
        raise Invalid(_(u"Bad phone format"))
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
        title=_(u"Number"), required=True, constraint=phone_constraint
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


class IContact(model.Schema):
    """ """

    logo = NamedBlobImage(title=_(u"Logo"), description=_(u""), required=False)
    subtitle = schema.TextLine(title=_(u"Subtitle"), required=False)
    type = schema.Choice(
        title=_(u"Type"),
        source="imio.directory.vocabulary.ContactTypes",
        required=False,
    )
    street = schema.TextLine(title=u"Street", required=False)
    number = schema.TextLine(title=u"Number", required=False)
    complement = schema.TextLine(title=u"Complement", required=False)
    zipcode = schema.Int(title=u"Zipcode", required=False)
    city = schema.TextLine(title=u"City", required=False)
    country = schema.Choice(
        title=u"Country",
        source="imio.directory.vocabulary.Countries",
        default="be",
        required=False,
    )

    vat_number = schema.TextLine(title=u"VAT number", required=False)
    phone = schema.TextLine(
        title=_(u"Phone"), required=False, constraint=phone_constraint
    )
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

    hide_description = schema.Bool(
        title=_(u"Hide description"),
        description=_(u"If checked, description will be hidden"),
        required=False,
        default=False,
    )

    hide_phones = schema.Bool(
        title=_(u"Hide phones"),
        description=_(u"If checked, phones will be hidden"),
        required=False,
        default=False,
    )


@implementer(IContact)
class Contact(Container):
    """ """


@implementer(INameChooser)
class ContactNameChooser(NormalizingNameChooser):
    def chooseName(self, name, obj):
        if IContact.providedBy(obj):
            return obj.UID()
        return super(ContactNameChooser, self).chooseName(name, obj)
