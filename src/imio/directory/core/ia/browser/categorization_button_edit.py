# -*- coding: utf-8 -*-
from imio.smartweb.common.ia.browser.categorization_button_edit import (
    IACategorizeEditForm as BaseIACategorizeEditForm,
)
from plone.z3cform import layout
from z3c.form.interfaces import HIDDEN_MODE


class IACategorizeEditForm(BaseIACategorizeEditForm):
    """Vue edit custom, avec bouton 'Catégoriser' injecté en haut de 'categorization'."""

    def update(self):
        super(IACategorizeEditForm, self).update()


PageEditView = layout.wrap_form(IACategorizeEditForm)
