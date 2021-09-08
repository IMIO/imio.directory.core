# -*- coding: utf-8 -*-

from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class ContactTypeVocabularyFactory:
    def __call__(self, context=None):
        values = [
            (
                u"organization",
                _(
                    u"Organization (administrative service, business, professional, sports club, association, etc.)"
                ),
            ),
            (
                u"position",
                _(
                    u"Position (mayor, alderman, advisor, director, head of department, etc.)"
                ),
            ),
            (u"mission", _(u"Mission (passports, reception, parking, etc.)")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in values]
        return SimpleVocabulary(terms)


ContactTypeVocabulary = ContactTypeVocabularyFactory()


class PhoneTypeVocabularyFactory:
    def __call__(self, context=None):
        """vcard spec : cell, home, work, text, voice, fax, video, pager, textphone"""
        values = [
            (u"fax", _(u"Fax")),
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


class FacilitiesVocabularyFactory:
    def __call__(self, context=None):
        values = [
            (u"accessibility", _(u"Accessibility (PMR)")),
            (u"defibrillator", _(u"Defibrillator")),
            (u"drinking_water_point", _(u"Drinking water point")),
            (u"useful_numbers", _(u"Useful numbers")),
            (u"public_toilets", _(u"Public toilets")),
            (u"free_wifi", _(u"Free WIFI")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in values]
        return SimpleVocabulary(terms)


FacilitiesVocabulary = FacilitiesVocabularyFactory()


class EntitiesUIDsVocabularyFactory:
    def __call__(self, context=None):
        portal = api.portal.get()
        brains = api.content.find(
            context=portal,
            portal_type="imio.directory.Entity",
            sort_on="sortable_title",
        )
        terms = [SimpleTerm(value=b.UID, token=b.UID, title=b.Title) for b in brains]
        return SimpleVocabulary(terms)


EntitiesUIDsVocabulary = EntitiesUIDsVocabularyFactory()
