# -*- coding: utf-8 -*-

from imio.directory.core.contents import IContact
from imio.directory.core.utils import get_entity_uid_for_contact
from plone.indexer import indexer


@indexer(IContact)
def container_uid(obj):
    uid = get_entity_uid_for_contact(obj)
    return uid
