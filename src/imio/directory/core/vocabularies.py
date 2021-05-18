# -*- coding: utf-8 -*-

from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.i18n.locales import locales
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.component import getUtility


class CountryVocabularyFactory:
    def __call__(self, context=None):
        normalizer = getUtility(IIDNormalizer)
        current_language = api.portal.get_current_language()
        locale = locales.getLocale(current_language)
        localized_country_names = {
            capitalized_code.lower(): translation
            for capitalized_code, translation in locale.displayNames.territories.items()
        }
        terms = [
            SimpleTerm(value=k, token=k, title=v)
            for k, v in sorted(
                localized_country_names.items(),
                key=lambda kv: normalizer.normalize(kv[1]),
            )
            if k != "fallback"
        ]
        return SimpleVocabulary(terms)


CountryVocabulary = CountryVocabularyFactory()


class ContactTypeVocabularyFactory:
    def __call__(self, context=None):
        values = [
            (u"organization", _(u"Organization")),
            (u"service", _(u"Service")),
            (u"position", _(u"Position")),
            (u"matter_mission", _(u"Matter / Mission")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in values]
        return SimpleVocabulary(terms)


ContactTypeVocabulary = ContactTypeVocabularyFactory()


class PhoneTypeVocabularyFactory:
    def __call__(self, context=None):
        """vcard spec : cell, home, work, text, voice, fax, video, pager, textphone"""
        values = [
            (u"cell", _(u"Mobile")),
            (u"home", _(u"Personal phone")),
            (u"work", _(u"Work phone")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in values]
        return SimpleVocabulary(terms)


PhoneTypeVocabulary = PhoneTypeVocabularyFactory()


class MailTypeVocabularyFactory:
    def __call__(self, context=None):
        """vcard spec : home, work"""
        values = [
            (u"home", _(u"Personal email")),
            (u"work", _(u"Work email")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in values]
        return SimpleVocabulary(terms)


MailTypeVocabulary = MailTypeVocabularyFactory()


class SiteTypeVocabularyFactory:
    def __call__(self, context=None):
        values = [
            (u"facebook", _(u"Facebook")),
            (u"twitter", _(u"Twitter")),
            (u"website", _(u"Website")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in values]
        return SimpleVocabulary(terms)


SiteTypeVocabulary = SiteTypeVocabularyFactory()
