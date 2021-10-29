# -*- coding: utf-8 -*-

from plone import api
from plone.app.contenttypes.browser.folder import FolderView
from plone.dexterity.browser.view import DefaultView
from Products.CMFPlone.resources import add_bundle_on_request
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class ContactView(DefaultView, FolderView):
    """imio.directory.core.Contact view
    FolderView brings get_thumb_scale_list
    """

    def __call__(self):
        images = self.context.listFolderContents(contentFilter={"portal_type": "Image"})
        if len(images) > 0:
            add_bundle_on_request(self.request, "spotlightjs")
            add_bundle_on_request(self.request, "flexbin")
        self.update()
        return self.index()

    def files(self):
        return self.context.listFolderContents(contentFilter={"portal_type": "File"})

    def images(self):
        return self.context.listFolderContents(contentFilter={"portal_type": "Image"})

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
