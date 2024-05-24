# -*- coding: utf-8 -*-

from collective.taxonomy.interfaces import ITaxonomy
from imio.directory.core.contents import IContact
from imio.directory.core.utils import get_entity_uid_for_contact
from imio.smartweb.common.utils import translate_vocabulary_term
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
def description_nl(obj):
    if not obj.description_nl:
        raise AttributeError
    return obj.description_nl


@indexer(IContact)
def description_de(obj):
    if not obj.description_de:
        raise AttributeError
    return obj.description_de


@indexer(IContact)
def description_en(obj):
    if not obj.description_en:
        raise AttributeError
    return obj.description_en


@indexer(IContact)
def container_uid(obj):
    uid = get_entity_uid_for_contact(obj)
    return uid


def get_searchable_text(obj, lang):
    topics = []
    for topic in getattr(obj.aq_base, "topics", []) or []:
        term = translate_vocabulary_term("imio.smartweb.vocabulary.Topics", topic, lang)
        topics.append(term)

    sm = getSiteManager()
    utility = sm.queryUtility(ITaxonomy, name="collective.taxonomy.contact_category")
    categories = []
    for category in getattr(obj.aq_base, "taxonomy_contact_category", []) or []:
        categories.append(
            utility.translate(category, context=obj, target_language=lang)
        )
    subjects = obj.Subject()
    title_field_name = "title"
    description_field_name = "description"
    subtitle_field_name = "subtitle"
    if lang != "fr":
        title_field_name = f"{title_field_name}_{lang}"
        description_field_name = f"{description_field_name}_{lang}"
        subtitle_field_name = f"{subtitle_field_name}_{lang}"

    mails_labels = []
    mails = safe_unicode(getattr(obj, "mails", "")) or ""
    if mails:
        for mail in mails:
            if mail["label"] is not None:
                mails_labels.append(mail["label"])

    phones_labels = []
    phones = safe_unicode(getattr(obj, "phones", "")) or ""
    if phones:
        for phone in phones:
            if phone["label"] is not None:
                phones_labels.append(phone["label"])

    result = " ".join(
        (
            safe_unicode(getattr(obj, title_field_name)) or "",
            safe_unicode(getattr(obj, subtitle_field_name)) or "",
            safe_unicode(getattr(obj, description_field_name)) or "",
            *topics,
            *categories,
            *subjects,
            *mails_labels,
            *phones_labels,
        )
    )
    return _unicode_save_string_concat(result)


@indexer(IContact)
def SearchableText_fr_contact(obj):
    return get_searchable_text(obj, "fr")


@indexer(IContact)
def SearchableText_nl_contact(obj):
    return get_searchable_text(obj, "nl")


@indexer(IContact)
def SearchableText_de_contact(obj):
    return get_searchable_text(obj, "de")


@indexer(IContact)
def SearchableText_en_contact(obj):
    return get_searchable_text(obj, "en")
