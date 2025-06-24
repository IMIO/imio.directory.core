# -*- coding: utf-8 -*-

from collective.taxonomy.interfaces import ITaxonomy
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from zope.component import getSiteManager
from zope.i18n import translate
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


class ContactTypeDeVocabularyFactory:
    def __call__(self, context=None):
        vocabulary = ContactTypeVocabularyFactory()(context)
        translated_terms = [
            SimpleTerm(
                value=term.value,
                token=term.token,
                title=translate(term.title, target_language="de"),
            )
            for term in vocabulary
        ]
        return SimpleVocabulary(translated_terms)


ContactTypeDeVocabulary = ContactTypeDeVocabularyFactory()


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
            ("instagram", _("Instagram")),
            ("linkedin", _("Linkedin")),
            ("pinterest", _("Pinterest")),
            ("twitter", _("Twitter")),
            ("website", _("Website")),
            ("youtube", _("Youtube")),
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
            ("bottle_bubbles", _("Bottle bubbles")),
            ("clothing_bubbles", _("Clothing bubbles")),
            ("container_parks", _("Container parks")),
        ]
        terms = [SimpleTerm(value=t[0], token=t[0], title=t[1]) for t in values]
        return SimpleVocabulary(terms)


FacilitiesVocabulary = FacilitiesVocabularyFactory()


class FacilitiesDeVocabularyFactory:
    def __call__(self, context=None):
        vocabulary = FacilitiesVocabularyFactory()(context)
        translated_terms = [
            SimpleTerm(
                value=term.value,
                token=term.token,
                title=translate(term.title, target_language="de"),
            )
            for term in vocabulary
        ]
        return SimpleVocabulary(translated_terms)


FacilitiesDeVocabulary = FacilitiesDeVocabularyFactory()


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


class ContactCategoriesDeVocabularyFactory:
    def __call__(self, context=None):
        sm = getSiteManager()
        contact_categories_taxo = sm.queryUtility(
            ITaxonomy, name="collective.taxonomy.contact_category"
        )
        categories_voca = contact_categories_taxo.makeVocabulary("de").inv_data
        terms = [
            SimpleTerm(value=k, token=k, title=v) for k, v in categories_voca.items()
        ]
        return SimpleVocabulary(terms)


ContactCategoriesDeVocabulary = ContactCategoriesDeVocabularyFactory()
