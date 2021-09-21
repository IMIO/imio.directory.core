# -*- coding: utf-8 -*-

from imio.smartweb.common.browser.forms import CustomAddForm
from imio.smartweb.common.browser.forms import CustomEditForm
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone.dexterity.browser.add import DefaultAddView
from plone.z3cform import layout


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


ContactCustomEditView = layout.wrap_form(ContactCustomEditForm)
