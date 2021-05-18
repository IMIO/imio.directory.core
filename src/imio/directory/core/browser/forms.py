# -*- coding: utf-8 -*-

from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm
from plone.z3cform import layout
from z3c.form.interfaces import HIDDEN_MODE


class CustomAddForm(DefaultAddForm):
    css_class = "tabbed-form-with-toggle"
    enable_form_tabbing = False

    def updateFields(self):
        super(CustomAddForm, self).updateFields()
        if "ILeadImageBehavior.image_caption" in self.fields:
            # We don't use leadimage caption anywhere
            self.fields["ILeadImageBehavior.image_caption"].mode = HIDDEN_MODE


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
