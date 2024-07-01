# -*- coding: utf-8 -*-

from imio.directory.core.rest.odwb_endpoint import OdwbEndpointGet
from imio.directory.core.utils import get_entity_for_contact
from imio.directory.core.utils import get_entity_uid_for_contact
from imio.smartweb.common.faceted.utils import configure_faceted
from imio.smartweb.common.interfaces import IAddress
from imio.smartweb.common.utils import geocode_object
from imio.smartweb.common.utils import remove_cropping
from plone import api
from plone.api.content import get_state
from Products.DCWorkflow.interfaces import IAfterTransitionEvent
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.lifecycleevent import ObjectRemovedEvent
from zope.lifecycleevent.interfaces import IAttributes

import os
import transaction


def set_default_entity_uid(contact):
    contact.selected_entities = contact.selected_entities or []
    uid = get_entity_uid_for_contact(contact)
    if uid not in contact.selected_entities:
        contact.selected_entities = contact.selected_entities + [uid]
    contact.reindexObject(idxs=["selected_entities"])


def added_entity(obj, event):
    faceted_config_path = "{}/faceted/config/entity.xml".format(
        os.path.dirname(__file__)
    )
    configure_faceted(obj, faceted_config_path)
    request = getRequest()
    request.form = {
        "cid": "entity",
        "faceted.entity.default": obj.UID(),
    }
    handler = getMultiAdapter((obj, request), name="faceted_update_criterion")
    handler.edit(**request.form)


def added_contact(obj, event):
    container_entity = get_entity_for_contact(obj)
    set_uid_of_referrer_entities(obj, container_entity)
    if not obj.is_geolocated:
        # geocode only if the user has not already changed geolocation
        geocode_object(obj)


def modified_contact(obj, event):
    set_default_entity_uid(obj)

    if not hasattr(event, "descriptions") or not event.descriptions:
        return
    for d in event.descriptions:
        if not IAttributes.providedBy(d):
            # we do not have fields change description, but maybe a request
            continue
        if d.interface is IAddress and d.attributes:
            # an address field has been changed
            geocode_object(obj)
        elif "ILeadImageBehavior.image" in d.attributes:
            # we need to remove cropping information of previous image
            remove_cropping(
                obj, "image", ["portrait_affiche", "paysage_affiche", "carre_affiche"]
            )
    if get_state(obj) == "published":
        request = getRequest()
        endpoint = OdwbEndpointGet(obj, request)
        endpoint.reply()


def modified_entity(obj, event):
    mark_current_entity_in_contacts_from_other_entities(obj, event)


def moved_contact(obj, event):
    if event.oldParent == event.newParent and event.oldName != event.newName:
        # item was simply renamed
        return
    if type(event) is ObjectRemovedEvent:
        # We don't have anything to do if event is being removed
        return
    container_entity = get_entity_for_contact(obj)
    set_uid_of_referrer_entities(obj, container_entity)
    if event.oldParent is not None and get_state(obj) == "published":
        request = getRequest()
        endpoint = OdwbEndpointGet(obj, request)
        endpoint.reply()


def removed_entity(obj, event):
    try:
        brains = api.content.find(selected_entities=obj.UID())
    except api.exc.CannotGetPortalError:
        # This happen when we try to remove plone object
        return
    for brain in brains:
        contact = brain.getObject()
        contact.selected_entities = [
            uid for uid in contact.selected_entities if uid != obj.UID()
        ]
        contact.reindexObject(idxs=["selected_entities"])


def removed_contact(obj, event):
    request = getRequest()
    endpoint = OdwbEndpointGet(obj, request)
    endpoint.remove()


def published_contact_transition(obj, event):
    if not IAfterTransitionEvent.providedBy(event):
        return
    if event.new_state.id == "published":
        kwargs = dict(obj=obj)
        transaction.get().addAfterCommitHook(send_to_odwb, kws=kwargs)
    if event.new_state.id == "private" and event.old_state.id != event.new_state.id:
        request = getRequest()
        endpoint = OdwbEndpointGet(obj, request)
        endpoint.remove()


def send_to_odwb(trans, obj=None):
    request = getRequest()
    endpoint = OdwbEndpointGet(obj, request)
    endpoint.reply()


def mark_current_entity_in_contacts_from_other_entities(obj, event):
    changed = False
    entities_to_treat = []
    for d in event.descriptions:
        if not IAttributes.providedBy(d):
            # we do not have fields change description, but maybe a request
            continue
        if "populating_entities" in d.attributes:
            changed = True
            uids_in_current_entity = [
                rf.to_object.UID() for rf in obj.populating_entities
            ]
            old_uids = getattr(obj, "old_populating_entities", [])
            entities_to_treat = set(old_uids) ^ set(uids_in_current_entity)
            break
    if not changed:
        return
    for uid_entity in entities_to_treat:
        entity = api.content.get(UID=uid_entity)
        contact_brains = api.content.find(
            context=entity, portal_type="imio.directory.Contact"
        )
        for brain in contact_brains:
            contact = brain.getObject()
            if uid_entity in uids_in_current_entity:
                contact.selected_entities.append(obj.UID())
                contact._p_changed = 1
            else:
                contact.selected_entities = [
                    item for item in contact.selected_entities if item != obj.UID()
                ]
            contact.reindexObject(idxs=["selected_entities"])
    # Keep a copy of populating_entities
    obj.old_populating_entities = uids_in_current_entity


def set_uid_of_referrer_entities(obj, container_entity):
    obj.selected_entities = [container_entity.UID()]
    rels = api.relation.get(target=container_entity, relationship="populating_entities")
    if not rels:
        obj.reindexObject(idxs=["selected_entities"])
        return
    for rel in rels:
        obj.selected_entities.append(rel.from_object.UID())
        obj._p_changed = 1
    obj.reindexObject(idxs=["selected_entities"])
