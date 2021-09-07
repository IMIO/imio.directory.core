# -*- coding: utf-8 -*-

from imio.directory.core.contents import IContact
from imio.directory.core.contents import IEntity
from plone.indexer.decorator import indexer
from Products.CMFPlone.utils import parent


@indexer(IContact)
def breadcrumb(obj):
    container = parent(obj)
    titles = [container.title, obj.title]
    while not IEntity.providedBy(container):
        container = parent(container)
        titles.insert(0, container.title)
    return " > ".join(titles)
