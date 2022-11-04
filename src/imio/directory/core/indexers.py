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
def translated_in_nl(obj):
    return bool(obj.title_nl)


@indexer(IContact)
def translated_in_de(obj):
    return bool(obj.title_de)


@indexer(IContact)
def translated_in_en(obj):
    return bool(obj.title_en)


@indexer(IContact)
def title_fr(obj):
    return obj.title


@indexer(IContact)
def title_nl(obj):
    if not obj.title_nl:
        raise AttributeError
    return obj.title_nl


@indexer(IContact)
def title_de(obj):
    if not obj.title_de:
        raise AttributeError
    return obj.title_de


@indexer(IContact)
def title_en(obj):
    if not obj.title_en:
        raise AttributeError
    return obj.title_en


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
    subjects = obj.Subject()
    result = " ".join(
        (
            safe_unicode(obj.title) or "",
            safe_unicode(obj.subtitle) or "",
            safe_unicode(obj.description) or "",
            safe_unicode(obj.title_nl) or "",
            safe_unicode(obj.subtitle_nl) or "",
            safe_unicode(obj.description_nl) or "",
            safe_unicode(obj.title_de) or "",
            safe_unicode(obj.subtitle_de) or "",
            safe_unicode(obj.description_de) or "",
            safe_unicode(obj.title_en) or "",
            safe_unicode(obj.subtitle_en) or "",
            safe_unicode(obj.description_en) or "",
            *topics,
            *categories,
            *subjects,
        )
    )
    return _unicode_save_string_concat(result)
