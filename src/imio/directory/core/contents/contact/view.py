# -*- coding: utf-8 -*-
from plone.app.contenttypes.browser.folder import FolderView
from plone.dexterity.browser.view import DefaultView
from Products.CMFPlone.utils import human_readable_size
from zope.component import queryMultiAdapter


class ContactView(DefaultView, FolderView):
    """imio.dirctory.core.Contact view
    FolderView brings get_thumb_scale_list
    """

    def description(self):
        """Description with html carriage return"""
        description = self.context.description
        description = "<br/>".join(description.split("\r\n"))
        return description

    def get_mime_type_icon(self, file_obj):
        view = queryMultiAdapter((self.context, self.request), name="contenttype_utils")
        return view.getMimeTypeIcon(file_obj.file)

    def human_readable_size(self, file_obj):
        return human_readable_size(file_obj.file.getSize())

    def files(self):
        return self.context.listFolderContents(contentFilter={"portal_type": "File"})

    def images(self):
        return self.context.listFolderContents(contentFilter={"portal_type": "Image"})
