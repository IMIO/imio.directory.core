Changelog
=========


1.2.3 (2024-01-09)
------------------

- WEB-4041 : Handle new "carre" scale
  [boulch]

- WEB-4007 : Update contact serializer and use ContactProperties to get well formated schedule
  and help displaying schedule in REACT directory view
  [boulch]


1.2.2 (2023-11-20)
------------------

- WEB-4018 : Add three new terms in facitilites vocabulary
  [boulch]

- Fix missing values for topics / iam lists (causing `None` in REST views filters)
  See https://github.com/collective/collective.solr/issues/366
  [laulaz]


1.2.1 (2023-10-26)
------------------

- Remove logo field from cropping editor
  [laulaz]


1.2 (2023-10-25)
----------------

- WEB-3985 : Use new portrait / paysage scales & logic
  [boulch, laulaz]

- WEB-3985 : Remove old cropping information when image changes
  [boulch, laulaz]


1.1.11 (2023-10-25)
-------------------

- MWEBITTA-21 : Add entities subscribing to share all contacts
  [boulch, laulaz]


1.1.10 (2023-10-09)
-------------------

- WEB-3918 : Add missing DE translations for contact_category taxonomy
  [laulaz]

- Update contact_category taxonomy data to reflect production site data
  [laulaz]


1.1.9 (2023-05-26)
------------------

- Fix condition when facing `Missing.Value` to avoid traceback in serializer
  [laulaz]

- WEB-3918 : Add missing DE translations for contact_category taxonomy
  [laulaz]

- Migrate to Plone 6.0.4
  [boulch]

- Update contact_category taxonomy data to reflect production site data
  [laulaz]


1.1.8 (2023-03-31)
------------------

- WEB-3909 : Add upgrade step to fix wrongly stored datagrid fields values
  [laulaz]


1.1.7 (2023-03-17)
------------------

- Fix non empty fields check after Datagridfield update
  [laulaz]


1.1.6 (2023-03-16)
------------------

- Define non empty fields for choices in contact Datagridfield rows & fix labels
  [laulaz]


1.1.5 (2023-03-15)
------------------

- Fix "required field" errors in empty Datagridfield rows
  [laulaz]


1.1.4 (2023-03-13)
------------------

- Add warning message if images are too small to be cropped
  [laulaz]

- Migrate to Plone 6.0.2
  [boulch]


1.1.3 (2023-02-28)
------------------

- Avoid auto-appending new lines to Datagrid fields when clicked
  [laulaz]

- Fix reindex after cut / copy / paste in some cases
  [laulaz]

- Add DE translations in contact_category taxonomy
  [laulaz]


1.1.2 (2023-02-20)
------------------

- Remove unused title_fr and description_fr metadatas
  [laulaz]

- Remove SearchableText_fr (Solr will use SearchableText for FR)
  [laulaz]


1.1.1 (2023-01-12)
------------------

- Add taxonomy_contact_category_for_filtering index to allow complex queries
  from smartweb directory views
  [laulaz]

- Add new descriptions metadatas and SearchableText indexes for multilingual
  [laulaz]


1.1 (2022-12-20)
----------------

- Update to Plone 6.0.0 final
  [boulch]

- Add eea.faceted.navigable behavior on Entity type
  [laulaz]


1.0 (2022-11-15)
----------------

- Add multilingual features: New fields, vocabularies translations, restapi serializer
  [laulaz]


1.0a7 (2022-10-28)
------------------

- Fix translation
  [boulch]

- WEB-3762 : Reorder contact fields to encourage good completion + add some fields descriptions
  [boulch]


1.0a6 (2022-10-21)
------------------

- WEB-3770 : Force include_items in serializer to True to get files and pictures included in contact
  [boulch]

- Add eea.faceted.navigable behavior on Entity type
  [laulaz]


1.0a5 (2022-08-09)
------------------

- WEB-3726 : Add subjects (keyword) in SearchableText
  [boulch]


1.0a4 (2022-07-14)
------------------

- Update contact_category taxonomy data to reflect production site data
  [laulaz]

- [WEBMIGP5-36] Add new vocabulary terms in imio.directory.vocabulary.SiteTypes (Instagram, Pinterest, Youtube)
  [boulch]

- It's not allowed to put Images or Files in imio.directory.Entity
  [boulch]


1.0a3 (2022-05-03)
------------------

- Use unique urls for images scales to ease caching
  [boulch]

- Use common.interfaces.ILocalManagerAware to mark a locally manageable content
  [boulch]


1.0a2 (2022-02-11)
------------------

- Add more checks / automatic corrections in contacts CSV import
  [laulaz]

- Update buildout to use Plone 6.0.0a3 packages versions
  [boulch]


1.0a1 (2022-01-25)
------------------

- Initial release.
  [boulch]
