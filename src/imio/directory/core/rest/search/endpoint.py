from imio.directory.core.utils import ENDPOINT_CACHE_KEY
from imio.smartweb.common.utils import is_log_active
from plone.memoize import ram
from plone.restapi.search.handler import SearchHandler
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.services.search.get import SearchGet as BaseSearchGet
from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite

import logging
import time

logger = logging.getLogger("imio.directory.core")
logger.setLevel(logging.INFO)


def _norm(v):
    if isinstance(v, (list, tuple)):
        return tuple(v)
    return v


def _first(value):
    if isinstance(value, (list, tuple)):
        return value[0] if value else None
    return value


def _items_from_req(req, ignored=frozenset({"cache_key", "_", "authenticator"})):
    items = tuple(
        sorted((k, _norm(v)) for k, v in req.form.items() if k not in ignored)
    )
    return items


def _query_from_req(req, pop_keys=()):
    # IMPORTANT: copy() => keep req.form intact for cache
    query = req.form.copy()
    for k in pop_keys:
        query.pop(k, None)
    st = query.get("SearchableText")
    prefix_param = query.pop("prefix_search", None)
    enable_prefix = True
    if isinstance(prefix_param, str):
        lowered = prefix_param.strip().lower()
        if lowered in {"0", "false", "no"}:
            enable_prefix = False
    st = query.get("SearchableText")
    if enable_prefix and isinstance(st, str) and st and not st.endswith("*"):
        query["SearchableText"] = f"{st}*"
    return unflatten_dotted_dict(query)


def _cachekey_by_entity_uid(method, self, entity_uid_key):
    req = self.request
    lang = req.get("LANGUAGE", "") or req.cookies.get("I18N_LANGUAGE", "")
    site = getSite()
    type_key = self.__class__.__name__
    entity_uid = _first(req.form.get(entity_uid_key))
    items = _items_from_req(req)

    if not entity_uid:
        return (site.getId(), type_key, "__no_entity__", items, lang)
    ann = IAnnotations(site)
    gen = ann.get(f"{ENDPOINT_CACHE_KEY}{entity_uid}", 0)
    return (site.getId(), type_key, entity_uid, gen, items, lang)


def _cachekey_entity(method, self):
    return _cachekey_by_entity_uid(method, self, "UID")


def _cachekey_contact(method, self):
    return _cachekey_by_entity_uid(method, self, "entity_uid")


class SearchGet(BaseSearchGet):
    # These params should not go to catalog
    POP_FROM_QUERY = ("entity_uid", "u", "batch_size")

    def _search(self):
        query = _query_from_req(self.request, pop_keys=self.POP_FROM_QUERY)
        return SearchHandler(self.context, self.request).search(query)

    def reply(self):
        # same as BaseSearchGet but filtered
        return self._search()


class CachedSearchMixin:
    CACHEKEY = None  # function
    REQUIRED_PARAM = None  # "UID" or "entity_uid"

    @ram.cache(lambda method, self: self.CACHEKEY(method, self))
    def _cached_reply(self):
        self.request.response.setHeader("X-RAM-Cache", "MISS")
        self.request.response.setHeader(
            "X-RAM-Cache-Computed-At", str(int(time.time()))
        )
        if is_log_active():
            logger.info("RAMCACHE MISS key=%r", self.CACHEKEY(None, self))
        return self._search()

    def reply(self):
        if self.REQUIRED_PARAM and _first(self.request.form.get(self.REQUIRED_PARAM)):
            result = self._cached_reply()
            if not self.request.response.getHeader("X-RAM-Cache"):
                self.request.response.setHeader("X-RAM-Cache", "HIT")
                if is_log_active():
                    logger.info("RAMCACHE HIT")
            return result
        return self._search()


class SearchEntity(CachedSearchMixin, SearchGet):
    CACHEKEY = staticmethod(_cachekey_entity)
    REQUIRED_PARAM = "UID"


class SearchContact(CachedSearchMixin, SearchGet):
    CACHEKEY = staticmethod(_cachekey_contact)
    REQUIRED_PARAM = "entity_uid"
