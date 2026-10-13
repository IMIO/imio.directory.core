# -*- coding: utf-8 -*-

from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.row import DictRow
from imio.smartweb.common.interfaces import ILocalManagerAware
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import schema
from plone.app.vocabularies.catalog import CatalogSource
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope.interface import implementer
from zope.interface import Interface


class ILocalCategoryRowSchema(Interface):

    fr = schema.TextLine(
        title=_("French"),
        required=True,
    )

    nl = schema.TextLine(
        title=_("Dutch"),
        required=False,
    )

    de = schema.TextLine(
        title=_("Deutsch"),
        required=False,
    )

    en = schema.TextLine(
        title=_("English"),
        required=False,
    )


class IEntity(model.Schema):
    """Marker interface and Dexterity Python Schema for Entity"""

    directives.widget(zip_codes=SelectFieldWidget)
    zip_codes = schema.List(
        title=_("Zip codes and cities"),
        description=_("Choose zip codes for this entity"),
        value_type=schema.Choice(vocabulary="imio.smartweb.vocabulary.Cities"),
    )

    model.fieldset("categorization", fields=["local_categories"])
    local_categories = schema.List(
        title=_("Specific contact categories"),
        description=_(
            "List of contact categories values available for this entity (one per line)"
        ),
        value_type=DictRow(title="Value", schema=ILocalCategoryRowSchema),
        required=False,
    )
    directives.widget(
        "local_categories", DataGridFieldFactory, allow_reorder=True, auto_append=False
    )

    populating_entities = RelationList(
        title=_("Populating entities"),
        description=_(
            "Entities that automatically populates this Entity with their contacts."
        ),
        value_type=RelationChoice(
            title="Items selection",
            source=CatalogSource(),
        ),
        default=[],
        required=False,
    )
    directives.widget(
        "populating_entities",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "selectableTypes": ["imio.directory.Entity"],
            "favorites": [],
        },
    )


@implementer(IEntity, ILocalManagerAware)
class Entity(Container):
    """Entity content type"""
