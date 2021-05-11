# -*- coding: utf-8 -*-

from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.row import DictRow
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import schema
from plone.app.content.namechooser import NormalizingNameChooser
from plone.autoform import directives
from plone.autoform.directives import widget
from plone.dexterity.content import Container
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope.container.interfaces import INameChooser
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import Invalid
import re

CATEGORY_TAXONOMY = "collective.taxonomy.contact_category"
TOPIC_TAXONOMY = "collective.taxonomy.contact_topic"


def phone_constraint(value):
    if re.match(r"\+\d{7,15}", value) is None:
        raise Invalid(_(u"Bad phone format"))
    return True


class IPhoneRowSchema(Interface):

    label = schema.TextLine(
        title=_(u"Label (direction, Main number,...)"),
        description=_(u""),
    )

    type = schema.Choice(
        title=_(u"Type"),
        source="imio.directory.vocabulary.PhoneTypes",
        description=_(u""),
        required=True,
    )
    # , constraint=phone_constraint
    phone = schema.TextLine(
        title=_(u"Phone"), required=True, constraint=phone_constraint
    )


class IMailRowSchema(Interface):

    label = schema.TextLine(
        title=_(u"Label (Professional, personal,...)"),
        description=_(u""),
    )

    mail = schema.Email(title=_(u"E-mail"), required=True)


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
    street = schema.TextLine(title=u"Street")
    number = schema.TextLine(title=u"Number")
    complement = schema.TextLine(title=u"Complement", required=False)
    zipcode = schema.Int(title=u"Zipcode")
    city = schema.TextLine(title=u"City")
    country = schema.Choice(
        title=u"Country", source="imio.directory.vocabulary.Countries"
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

    directives.order_before(category="ICategorization.subjects")
    model.fieldset("categorization", fields=["category", "topics"])
    category = schema.Choice(
        title=_(u"Category"),
        source=CATEGORY_TAXONOMY,
        required=False,
    )

    directives.order_after(topics="category")
    topics = schema.List(
        title=_(u"Topics"),
        value_type=schema.Choice(source=TOPIC_TAXONOMY),
        required=False,
    )


@implementer(IContact)
class Contact(Container):
    """ """

    category_taxonomy = CATEGORY_TAXONOMY
    topic_taxonomy = TOPIC_TAXONOMY


@implementer(INameChooser)
class ContactNameChooser(NormalizingNameChooser):

    def chooseName(self, name, obj):
        if IContact.providedBy(obj):
            return obj.UID()
        return super(ContactNameChooser, self).chooseName(name, obj)
