Changelog
=========


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
