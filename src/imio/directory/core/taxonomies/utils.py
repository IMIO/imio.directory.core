# -*- coding: utf-8 -*-

from collective.taxonomy.exportimport import TaxonomyImportExportAdapter
from collective.taxonomy.factory import registerTaxonomy
from collective.taxonomy.interfaces import ITaxonomy
from collective.taxonomy.vdex import ImportVdex
from imio.smartweb.locales import SmartwebMessageFactory as _
from lxml.etree import fromstring
from plone import api
from zope.i18n import translate
import os


class SortedTaxonomyImportAdapter(TaxonomyImportExportAdapter):
    """ """

    def importDocument(self, taxonomy, document, clear=False):
        tree = fromstring(document)
        results = ImportVdex(tree, self.IMSVDEX_NS)()

        for language, items in results.items():
            items.sort()
            taxonomy.update(language, items, clear)


def create_taxonomy_object(data_tax, portal):
    taxonomy = registerTaxonomy(
        api.portal.get(),
        name=data_tax["taxonomy"],
        title=data_tax["field_title"],
        description=data_tax["field_description"],
        default_language=data_tax["default_language"],
    )

    adapter = SortedTaxonomyImportAdapter(portal)
    data_path = os.path.join(os.path.dirname(__file__), "datas")
    file_path = os.path.join(data_path, data_tax["filename"])
    data = (open(file_path, "rb").read(),)
    import_file = data[0]
    adapter.importDocument(taxonomy, import_file)

    del data_tax["taxonomy"]
    del data_tax["filename"]
    taxonomy.registerBehavior(**data_tax)


def add_contact_taxonomy(taxonomy_type):
    portal = api.portal.get()
    current_lang = api.portal.get_default_language()[:2]
    data_contact = {
        "taxonomy": "contact_{}".format(taxonomy_type),
        "field_title": translate(
            _("Contact {}".format(taxonomy_type)), target_language=current_lang
        ),
        "field_description": "",
        "default_language": "fr",
        "filename": "contact_{}.xml".format(taxonomy_type),
    }
    sm = portal.getSiteManager()
    utility_page = sm.queryUtility(
        ITaxonomy, name="collective.taxonomy.contact_{}".format(taxonomy_type)
    )
    if not utility_page:
        create_taxonomy_object(data_contact, portal)