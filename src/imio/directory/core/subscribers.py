# -*- coding: utf-8 -*-

from imio.smartweb.common.faceted.utils import configure_faceted
import os


def added_entity(obj, event):
    faceted_config_path = "{}/faceted/config/entity.xml".format(
        os.path.dirname(__file__)
    )
    configure_faceted(obj, faceted_config_path)
