# -*- coding: utf-8 -*-

from imio.smartweb.common.browser.forms import CustomAddForm
from imio.smartweb.common.browser.forms import CustomEditForm
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from plone.dexterity.browser.add import DefaultAddView
from plone.z3cform import layout
from zope.i18n import translate


class ContactCustomAddForm(CustomAddForm):
    portal_type = "imio.directory.Contact"

    def updateWidgets(self):
        super(ContactCustomAddForm, self).updateWidgets()
        if "IGeolocatable.geolocation" in self.widgets:
            self.widgets["IGeolocatable.geolocation"].description = _(
                "The geolocation is generated on the basis of the address during contact save. "
                "It is possible to change the pointer manually if it is not correctly positioned."
            )


class ContactCustomAddView(DefaultAddView):
    form = ContactCustomAddForm


class ContactCustomEditForm(CustomEditForm):
    def updateWidgets(self):
        super(ContactCustomEditForm, self).updateWidgets()
        if "IGeolocatable.geolocation" in self.widgets:
            self.widgets["IGeolocatable.geolocation"].description = _(
                "The geolocation is generated on the basis of the address during contact save. "
                "It is possible to change the pointer manually if it is not correctly positioned."
            )
        if "ILeadImageBehavior.image" in self.widgets:
            language = api.portal.get_current_language()
            desc = self.widgets["ILeadImageBehavior.image"].description
            desc = translate(desc, target_language=language)
            prepend_desc = _("Example : Photo of a person or organization building")
            prepend_desc = translate(prepend_desc, target_language=language)
            self.widgets[
                "ILeadImageBehavior.image"
            ].description = f"{prepend_desc}. {desc}"


ContactCustomEditView = layout.wrap_form(ContactCustomEditForm)
