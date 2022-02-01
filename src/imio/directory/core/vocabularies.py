# -*- coding: utf-8 -*-

from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class ContactTypeVocabularyFactory:
    def __call__(self, context=None):
        values = [
            (
                "organization",
                _(
                    "Organization (administrative service, business, professional, sports club, association, etc.)"
                ),
            ),
            (
                "position",
                _(
                    "Position (mayor, alderman, advisor, director, head of department, etc.)"
                ),
            ),
            ("mission", _("Mission (passports, reception, parking, etc.)")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in values]
        return SimpleVocabulary(terms)


ContactTypeVocabulary = ContactTypeVocabularyFactory()


class PhoneTypeVocabularyFactory:
    def __call__(self, context=None):
        """vcard spec : cell, home, work, text, voice, fax, video, pager, textphone"""
        values = [
            ("fax", _("Fax")),
            ("cell", _("Mobile")),
            ("home", _("Personal phone")),
            ("work", _("Work phone")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in values]
        return SimpleVocabulary(terms)


PhoneTypeVocabulary = PhoneTypeVocabularyFactory()


class MailTypeVocabularyFactory:
    def __call__(self, context=None):
        """vcard spec : home, work"""
        values = [
            ("home", _("Personal email")),
            ("work", _("Work email")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in values]
        return SimpleVocabulary(terms)


MailTypeVocabulary = MailTypeVocabularyFactory()


class SiteTypeVocabularyFactory:
    def __call__(self, context=None):
        values = [
            ("facebook", _("Facebook")),
            ("twitter", _("Twitter")),
            ("website", _("Website")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in values]
        return SimpleVocabulary(terms)


SiteTypeVocabulary = SiteTypeVocabularyFactory()


class FacilitiesVocabularyFactory:
    def __call__(self, context=None):
        values = [
            ("accessibility", _("Accessibility (PMR)")),
            ("defibrillator", _("Defibrillator")),
            ("drinking_water_point", _("Drinking water point")),
            ("useful_numbers", _("Useful numbers")),
            ("public_toilets", _("Public toilets")),
            ("free_wifi", _("Free WIFI")),
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
