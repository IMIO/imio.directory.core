# -*- coding: utf-8 -*-

from plone import api
from plone.app.contenttypes.browser.folder import FolderView
from plone.dexterity.browser.view import DefaultView
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class ContactView(DefaultView, FolderView):
    """imio.directory.core.Contact view
    FolderView brings get_thumb_scale_list
    """

    GALLERY_IMAGES_NUMBER = 3

    def description(self):
        """Description with html carriage return"""
        description = self.context.description
        description = "<br/>".join(description.split("\r\n"))
        return description

    def files(self):
        return self.context.listFolderContents(contentFilter={"portal_type": "File"})

    def images(self):
        images = self.context.listFolderContents(contentFilter={"portal_type": "Image"})
        rows = []
        for i in range(0, len(images)):
            if i % self.GALLERY_IMAGES_NUMBER == 0:
                rows.append(images[i : i + self.GALLERY_IMAGES_NUMBER])  # NOQA
        return rows

    def sub_contacts(self):
        factory = getUtility(
            IVocabularyFactory, "imio.directory.vocabulary.ContactTypes"
        )
        vocabulary = factory()
        sub_contacts = {}
        for term in vocabulary:
            sub_contacts_for_type = api.content.find(
                context=self.context,
                depth=1,
                portal_type="imio.directory.Contact",
                contact_type=term.value,
                sort_on="sortable_title",
            )
            if sub_contacts_for_type:
                sub_contacts[term.title] = sub_contacts_for_type
        return sub_contacts
