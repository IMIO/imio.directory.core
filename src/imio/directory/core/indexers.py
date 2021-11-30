# -*- coding: utf-8 -*-

from collective.taxonomy.interfaces import ITaxonomy
from imio.directory.core.contents import IContact
from imio.directory.core.utils import get_entity_uid_for_contact
from imio.smartweb.common.utils import translate_vocabulary_term
from plone import api
from plone.app.contenttypes.indexers import _unicode_save_string_concat
from plone.indexer import indexer
from Products.CMFPlone.utils import safe_unicode
from zope.component import getSiteManager


@indexer(IContact)
def container_uid(obj):
    uid = get_entity_uid_for_contact(obj)
    return uid


@indexer(IContact)
def SearchableText_contact(obj):
    topics = []
    for topic in getattr(obj.aq_base, "topics", []) or []:
        topics.append(
            translate_vocabulary_term("imio.smartweb.vocabulary.Topics", topic)
        )

    sm = getSiteManager()
    utility = sm.queryUtility(ITaxonomy, name="collective.taxonomy.contact_category")
    current_lang = api.portal.get_current_language()[:2]
    categories = []
    for category in getattr(obj.aq_base, "taxonomy_contact_category", []) or []:
        categories.append(
            utility.translate(category, context=obj, target_language=current_lang)
        )

    result = " ".join(
        (
            safe_unicode(obj.title) or "",
            safe_unicode(obj.subtitle) or "",
            safe_unicode(obj.description) or "",
            *topics,
            *categories,
        )
    )
    return _unicode_save_string_concat(result)
