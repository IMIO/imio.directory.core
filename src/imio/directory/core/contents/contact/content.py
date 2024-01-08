# -*- coding: utf-8 -*-

from collective.geolocationbehavior.geolocation import IGeolocatable
from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.row import DictRow
from imio.smartweb.common.adapters import BaseCroppingProvider
from imio.smartweb.common.interfaces import IAddress
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import schema
from plone.app.content.namechooser import NormalizingNameChooser
from plone.app.imagecropping.dx import CroppingUtilsDexterity
from plone.app.imagecropping.interfaces import IImageCroppingUtils
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.autoform.directives import read_permission
from plone.autoform.directives import widget
from plone.autoform.directives import write_permission
from plone.dexterity.content import Container
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImage
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.supermodel import model
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.converter import FormatterValidationError
from zope.component import adapter
from zope.container.interfaces import INameChooser
from zope.interface import Interface
from zope.interface import implementer
from zope.schema.interfaces import RequiredMissing
from zope.schema.interfaces import StopValidation

import re

UNCROPPABLE_FIELDS = ["logo"]


@implementer(IImageCroppingUtils)
@adapter(IImageScaleTraversable)
class DirectoryCroppingUtilsDexterity(CroppingUtilsDexterity):
    def _image_field_values(self):
        """Remove logo field from cropping editor"""
        for fieldname, field in self._all_fields():
            value = getattr(self.context, fieldname, None)
            if (
                value
                and IImage.providedBy(value)
                and fieldname not in UNCROPPABLE_FIELDS
            ):
                yield (fieldname, value)


class ContactCroppingProvider(BaseCroppingProvider):
    def get_scales(self, fieldname, request=None):
        if fieldname == "image":
            # scale used for lead image field
            return [
                "portrait_affiche",
                "paysage_affiche",
                "carre_affiche",
            ]
        return []


def phone_constraint(value):
    if re.match(r"\+\d{7,15}", value) is None:
        raise FormatterValidationError(_("Bad phone format"), value)
    return True


class NonEmptyField:
    def validate(self, value):
        if value:
            return super(NonEmptyField, self).validate(value)
        try:
            raise RequiredMissing
        except StopValidation:
            pass


class NonEmptyChoiceField(NonEmptyField, schema.Choice):
    """Required Choice field for Datagridfield - without buggy required"""


class NonEmptyTextField(NonEmptyField, schema.TextLine):
    """Required Text field for Datagridfield - without buggy required"""


class NonEmptyEmailField(NonEmptyField, schema.Email):
    """Required Email field for Datagridfield - without buggy required"""


class NonEmptyURIField(NonEmptyField, schema.URI):
    """Required URI field for Datagridfield - without buggy required"""


class IPhoneRowSchema(Interface):
    label = schema.TextLine(
        title=_("Label (direction, Main number,...)"),
        description=_(""),
        required=False,
    )

    type = NonEmptyChoiceField(
        title=_("Type"),
        source="imio.directory.vocabulary.PhoneTypes",
        description=_(""),
        required=False,
    )

    number = NonEmptyTextField(
        title=_("Number (format: +32475010203)"),
        required=False,
        constraint=phone_constraint,
    )


class IMailRowSchema(Interface):
    label = schema.TextLine(
        title=_("Label (Secretariat, Manager office, Sales,...)"),
        description=_(""),
        required=False,
    )

    type = NonEmptyChoiceField(
        title=_("Type"),
        source="imio.directory.vocabulary.MailTypes",
        description=_(""),
        required=False,
    )

    mail_address = NonEmptyEmailField(title=_("E-mail"), required=False)


class IUrlRowSchema(Interface):
    type = NonEmptyChoiceField(
        title=_("Type"),
        source="imio.directory.vocabulary.SiteTypes",
        description=_(""),
        required=False,
    )

    url = NonEmptyURIField(title=_("Url"), required=False)


# # Move geolocation field to our Address fieldset
# address_fieldset = Fieldset(
#     "address",
#     fields=["geolocation"],
# )
# IGeolocatable.setTaggedValue(FIELDSETS_KEY, [address_fieldset])


class IContactInformations(model.Schema):
    model.fieldset(
        "contact_informations",
        label=_("Contact informations"),
        fields=["vat_number", "phones", "mails", "urls"],
    )
    vat_number = schema.TextLine(title=_("VAT number"), required=False)
    phones = schema.List(
        title=_("Phones"),
        value_type=DictRow(
            title="Value",
            schema=IPhoneRowSchema,
        ),
        required=False,
    )
    widget("phones", DataGridFieldFactory, allow_reorder=True, auto_append=False)

    mails = schema.List(
        title=_("E-mails"),
        value_type=DictRow(
            title="Value",
            schema=IMailRowSchema,
        ),
        required=False,
    )
    widget("mails", DataGridFieldFactory, allow_reorder=True, auto_append=False)

    urls = schema.List(
        title=_("URLs"),
        value_type=DictRow(
            title="Value",
            schema=IUrlRowSchema,
        ),
        required=False,
    )
    widget("urls", DataGridFieldFactory, allow_reorder=True, auto_append=False)


class IPrivateContactInformations(model.Schema):
    model.fieldset(
        "private_contact_informations",
        label=_("Private contact informations"),
        fields=["private_phones", "private_mails", "private_urls", "private_note"],
    )
    private_phones = schema.List(
        title=_("Phones"),
        value_type=DictRow(
            title="Value",
            schema=IPhoneRowSchema,
        ),
        required=False,
    )
    widget(
        "private_phones", DataGridFieldFactory, allow_reorder=True, auto_append=False
    )

    private_mails = schema.List(
        title=_("E-mails"),
        value_type=DictRow(
            title="Value",
            schema=IMailRowSchema,
        ),
        required=False,
    )
    widget("private_mails", DataGridFieldFactory, allow_reorder=True, auto_append=False)

    private_urls = schema.List(
        title=_("URLs"),
        value_type=DictRow(
            title="Value",
            schema=IUrlRowSchema,
        ),
        required=False,
    )
    widget("private_urls", DataGridFieldFactory, allow_reorder=True, auto_append=False)

    private_note = schema.Text(title=_("Internal note"), required=False)

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


class IDETranslations(model.Schema):
    model.fieldset(
        "de_translations",
        label=_("German translations"),
        fields=["title_de", "subtitle_de", "description_de"],
    )
    title_de = schema.TextLine(
        title=_("Title"),
        description=_(
            "This field is required if the content must be available in this language"
        ),
        required=False,
    )
    subtitle_de = schema.TextLine(title=_("Subtitle"), required=False)
    description_de = schema.Text(title=_("Description"), required=False)


class IENTranslations(model.Schema):
    model.fieldset(
        "en_translations",
        label=_("English translations"),
        fields=["title_en", "subtitle_en", "description_en"],
    )
    title_en = schema.TextLine(
        title=_("Title"),
        description=_(
            "This field is required if the content must be available in this language"
        ),
        required=False,
    )
    subtitle_en = schema.TextLine(title=_("Subtitle"), required=False)
    description_en = schema.Text(title=_("Description"), required=False)


class INLTranslations(model.Schema):
    model.fieldset(
        "nl_translations",
        label=_("Dutch translations"),
        fields=["title_nl", "subtitle_nl", "description_nl"],
    )
    title_nl = schema.TextLine(
        title=_("Title"),
        description=_(
            "This field is required if the content must be available in this language"
        ),
        required=False,
    )
    subtitle_nl = schema.TextLine(title=_("Subtitle"), required=False)
    description_nl = schema.Text(title=_("Description"), required=False)


class ITranslations(IENTranslations, IDETranslations, INLTranslations):
    """ """


class IContact(
    IPrivateContactInformations, IContactInformations, IAddress, ITranslations
):
    """ """

    directives.order_before(type="IBasic.title")
    directives.widget(type=RadioFieldWidget)
    type = schema.Choice(
        title=_("Type"),
        source="imio.directory.vocabulary.ContactTypes",
        required=True,
    )

    directives.order_after(subtitle="IBasic.title")
    subtitle = schema.TextLine(title=_("Subtitle"), required=False)

    directives.order_after(logo="ILeadImageBehavior.image")
    logo = NamedBlobImage(
        title=_("Logo"),
        description=_("Example : shop, service, association logo"),
        required=False,
    )

    model.fieldset("categorization", fields=["selected_entities", "facilities"])
    directives.widget(selected_entities=SelectFieldWidget)
    selected_entities = schema.List(
        title=_("Selected entities"),
        description=_(
            "Select entities where this contact will be displayed. Current entity will always be selected."
        ),
        value_type=schema.Choice(vocabulary="imio.directory.vocabulary.EntitiesUIDs"),
        default=[],
        required=False,
    )

    facilities = schema.List(
        title=_("Facilities"),
        description=_(
            "Important! These categories make it possible to highlight and geolocate certain basic services"
        ),
        value_type=schema.Choice(vocabulary="imio.directory.vocabulary.Facilities"),
        default=[],
        required=False,
    )
    directives.widget(facilities=SelectFieldWidget)

    read_permission(selected_entities="imio.directory.core.AddEntity")
    write_permission(selected_entities="imio.directory.core.AddEntity")


@implementer(IContact)
class Contact(Container):
    """ """

    @property
    def is_geolocated(self):
        coordinates = IGeolocatable(self).geolocation
        if coordinates is None:
            return False
        return all([coordinates.latitude, coordinates.longitude])


@implementer(INameChooser)
class ContactNameChooser(NormalizingNameChooser):
    def chooseName(self, name, obj):
        if IContact.providedBy(obj):
            return obj.UID()
        return super(ContactNameChooser, self).chooseName(name, obj)
