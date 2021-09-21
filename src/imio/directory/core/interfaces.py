# -*- coding: utf-8 -*-

from imio.smartweb.common.interfaces import IImioSmartwebCommonLayer
from plone.theme.interfaces import IDefaultPloneLayer


class IImioDirectoryCoreLayer(IImioSmartwebCommonLayer, IDefaultPloneLayer):
    """Marker interface that defines a browser layer."""
