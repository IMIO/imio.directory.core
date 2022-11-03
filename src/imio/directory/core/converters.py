# -*- coding: utf-8 -*-

from imio.smartweb.common.rest.utils import get_restapi_query_lang
from plone.restapi.interfaces import IJsonCompatible
from zope.component import adapter
from zope.i18n import translate
from zope.i18nmessageid.message import Message
from zope.interface import implementer


@adapter(Message)
@implementer(IJsonCompatible)
def i18n_message_converter(value):
    lang = get_restapi_query_lang()
    value = translate(value, target_language=lang)
    return value
