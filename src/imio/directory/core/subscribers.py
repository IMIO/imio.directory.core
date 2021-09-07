# -*- coding: utf-8 -*-

from imio.smartweb.common.faceted.utils import configure_faceted
from plone import api
from plone.app.dexterity.behaviors.metadata import IBasic
import os


def added_entity(obj, event):
    faceted_config_path = "{}/faceted/config/entity.xml".format(
        os.path.dirname(__file__)
    )
    configure_faceted(obj, faceted_config_path)


def modified_content(obj, event):
    if not hasattr(event, "descriptions") or not event.descriptions:
        return

    for d in event.descriptions:
        if d.interface is not IBasic:
            continue
        if "IBasic.title" in d.attributes:
            brains = api.content.find(context=obj)
            for brain in brains:
                content = brain.getObject()
                content.reindexObject(idxs=["breadcrumb"])
            return
