# -*- coding: utf-8 -*-

from imio.directory.core.contents import IContact
from imio.directory.core.contents import IEntity
from imio.directory.core.utils import get_vcard
from Products.Five.browser import BrowserView


class UtilsView(BrowserView):
    def can_export_contact_to_vcard(self):
        return IContact.providedBy(self.context)

    def export_contact_to_vcard(self):
        if not self.can_export_contact_to_vcard():
            return
        self.request.response.setHeader("Content-type", "text/x-vCard; charset=utf-8")
        content_disposition = "attachment; filename=%s.vcf" % (self.context.id)
        self.request.response.setHeader("Content-Disposition", content_disposition)
        vcard = get_vcard(self.context)
        return vcard.serialize()

    def can_import_contacts(self):
        return IContact.providedBy(self.context) or IEntity.providedBy(self.context)
