# -*- coding: utf-8 -*-

from imio.directory.core.utils import ENDPOINT_CACHE_KEY
from imio.smartweb.common.utils import is_log_active
from plone import api
from plone.memoize import ram
from plone.restapi.services.search.get import SearchGet as BaseSearchGet
from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite

import logging
import time

logger = logging.getLogger("imio.directory.core")

IGNORED_PARAMS = frozenset({"cache_key", "_", "authenticator"})


def _norm(value):
    if isinstance(value, (list, tuple)):
        return tuple(value)
    return value


def _entity_uid(request):
    """UID of the entity whose contacts are searched, None if the search is
    not on exactly one entity"""
    uids = request.form.get("selected_entities")
    if isinstance(uids, (list, tuple)):
        uids = uids[0] if len(uids) == 1 else None
    return uids or None


def _cachekey(method, self):
    request = self.request
    lang = request.get("LANGUAGE", "") or request.cookies.get("I18N_LANGUAGE", "")
    site = getSite()
    entity_uid = _entity_uid(request)
    # the generation is incremented when a contact of the entity changes
    gen = IAnnotations(site).get(f"{ENDPOINT_CACHE_KEY}{entity_uid}", 0)
    params = tuple(
        sorted(
            (k, _norm(v)) for k, v in request.form.items() if k not in IGNORED_PARAMS
        )
    )
    return (site.getId(), entity_uid, gen, params, lang)


class SearchGet(BaseSearchGet):
    @ram.cache(_cachekey)
    def _cached_reply(self):
        self.request.response.setHeader("X-RAM-Cache", "MISS")
        self.request.response.setHeader(
            "X-RAM-Cache-Computed-At", str(int(time.time()))
        )
        if is_log_active():
            logger.info("RAMCACHE MISS key=%r", _cachekey(None, self))
        return super(SearchGet, self).reply()

    def _use_cache(self):
        # the results of an authenticated user must not be shared with others
        return (
            api.portal.get_registry_record(
                "imio.directory.core.search_cache_enabled", default=True
            )
            and api.user.is_anonymous()
            and _entity_uid(self.request) is not None
        )

    def reply(self):
        if not self._use_cache():
            return super(SearchGet, self).reply()
        result = self._cached_reply()
        # on a HIT, _cached_reply() is not executed: no header yet
        if not self.request.response.getHeader("X-RAM-Cache"):
            self.request.response.setHeader("X-RAM-Cache", "HIT")
            if is_log_active():
                logger.info("RAMCACHE HIT")
        return result
