# -*- coding: utf-8 -*-

from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm
from plone.z3cform import layout
from z3c.form.interfaces import HIDDEN_MODE
from plone.autoform.widgets import ParameterizedWidget


class CustomAddForm(DefaultAddForm):
    css_class = "tabbed-form-with-toggle"
    enable_form_tabbing = False

    def updateFields(self):
        super(CustomAddForm, self).updateFields()
        if "ILeadImageBehavior.image_caption" in self.fields:
            # We don't use leadimage caption anywhere
            self.fields["ILeadImageBehavior.image_caption"].mode = HIDDEN_MODE
        for group in self.groups:
            print(group.fields.keys())
            if "number" in group.fields:
                print("OK")
                group.fields["number"].widgetFactory = ParameterizedWidget(
                    None,
                    placeholder=u"ex: Jean",
                )
            if "IPhoneRowSchema.number" in group.fields:
                print("OK 2")
                group.fields[
                    "IPhoneRowSchema.number"
                ].widgetFactory = ParameterizedWidget(
                    None,
                    placeholder=u"ex: Jean",
                )


class CustomAddView(DefaultAddView):
    form = CustomAddForm


class CustomEditForm(DefaultEditForm):
    css_class = "tabbed-form-with-toggle"
    enable_form_tabbing = False

    def updateFields(self):
        super(CustomEditForm, self).updateFields()
        if "ILeadImageBehavior.image_caption" in self.fields:
            # We don't use leadimage caption anywhere
            self.fields["ILeadImageBehavior.image_caption"].mode = HIDDEN_MODE


CustomEditView = layout.wrap_form(CustomEditForm)
