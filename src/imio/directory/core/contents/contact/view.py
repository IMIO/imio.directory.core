# -*- coding: utf-8 -*-
from plone.app.contenttypes.browser.folder import FolderView
from plone.dexterity.browser.view import DefaultView


class ContactView(DefaultView, FolderView):
    """imio.dirctory.core.Contact view
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
                rows.append(images[i:i + self.GALLERY_IMAGES_NUMBER])
        return rows
