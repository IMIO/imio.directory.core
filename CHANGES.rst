Changelog
=========


1.2.20 (2025-06-25)
-------------------

- WEB-4278 : Create translated (de) contact categories vocabulary for e-guichet (citizen project)
  [boulch]

- WEB-4278 : Create translated (de) factilities vocabulary for e-guichet (citizen project)
  [boulch]

- WEB-4278 : Create translated (de) contact types vocabulary for e-guichet (citizen project)
  [boulch]


1.2.19 (2025-05-06)
-------------------

- Upgrade dev environment to Plone 6.1-latest
  [remdub]

- Add tests for Plone 6.1-latest and add Python 3.13
  [remdub]


1.2.18 (2025-01-29)
-------------------

- Update Python classifiers to be compatible with Python 3.12
  [remdub]

- Migrate to Plone 6.0.14
  [boulch]


1.2.17 (2025-01-07)
-------------------

- WEB-4153 : Add a new cacheRuleset to use with our custom rest endpoints
  [remdub]


1.2.16 (2024-08-05)
-------------------

- WEB-4027 : Add "Linkedin" as a new type of site term
  [boulch]

- WEB-4088 : Fix missing include package .rest. we couldn't directly call @odwb endpoints.
  [boulch]


1.2.15 (2024-07-01)
-------------------

- WEB-4088 : Add after commit hook to reduce bad image upload to odwb because of the transaction speed
  New contact hasn't time to go from private to published state ?!
  [boulch]


1.2.14 (2024-06-28)
-------------------

- WEB-4088 : Rename some fields to match with odwb dataset
  [boulch]

- GHA tests on Python 3.8 3.9 and 3.10
  [remdub]

1.2.13 (2024-06-06)
-------------------

- Geocode contact only if longitude and latitude are empty on csv import
  [laulaz, remdub]


1.2.12 (2024-05-27)
-------------------

- Fix upgrade step
  [boulch]


1.2.11 (2024-05-27)
-------------------

- WEB-4088 : Add some odwb endpoints (for contacts , for entities)
  Cover use case for sending data in odwb for a staging environment
  [boulch]

- Fix Topics in SearchableText translated indexes
  [laulaz]


1.2.10 (2024-04-10)
-------------------

- WEB-4095 : Use "|" separator instead of "," when exporting contacts to csv file
  [boulch]


1.2.9 (2024-02-27)
------------------

- WEB-4072, WEB-4073 : Enable solr.fields behavior on some content types
  [remdub]

- WEB-4006 : Exclude some content types from search results
  [remdub]


1.2.8 (2024-02-12)
------------------

- MWEBRCHA-14 : Add view to export contacts to csv file
  [boulch]


1.2.7 (2024-02-02)
------------------

- SUP-34841 : Fix contact serializer when contact hasn't schedule
  [boulch]


1.2.6 (2024-01-31)
------------------

- WEB-4006 : Also reindex solr on SearchableText upgrade step
  [remdub]


1.2.5 (2024-01-31)
------------------

- WEB-4006 : Add mail and phone labels in SearchableText
  [remdub]


1.2.4 (2024-01-17)
------------------

- WEB-4052 : If all values in schedule are "" then we set "table_date" to None
  [boulch]


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
