# -*- coding: utf-8 -*-

from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.theme.interfaces import IDefaultPloneLayer


class IImioDirectoryCoreLayer(IDefaultPloneLayer, IPloneFormLayer):
    """Marker interface that defines a browser layer."""
