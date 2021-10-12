# -*- coding: utf-8 -*-

from imio.smartweb.common.config import VOCABULARIES_MAPPING

VOCABULARIES_MAPPING.update(
    {
        "contact_type": "imio.directory.vocabulary.ContactTypes",
        "facilities": "imio.directory.vocabulary.Facilities",
        "taxonomy_contact_category": "collective.taxonomy.contact_category",
    }
)
