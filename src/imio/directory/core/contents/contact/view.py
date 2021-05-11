# -*- coding: utf-8 -*-
from plone.dexterity.browser.view import DefaultView


class ContactView(DefaultView):
    """imio.dirctory.core.Contact view"""

    def images(self):
        return self.context.listFolderContents(contentFilter={"portal_type": "Image"})
