from imio.directory.core.contents import IEntity
from imio.directory.core.utils import ENDPOINT_CACHE_KEY
from imio.smartweb.common.utils import get_parent_providing
from imio.smartweb.common.utils import is_log_active
from plone import api
from plone.memoize import ram
from plone.restapi.services.search.get import SearchGet as BaseSearchGet
from plone.uuid.interfaces import IUUID
from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite

import logging
import time

logger = logging.getLogger("imio.news.core")
logger.setLevel(logging.INFO)


def _cachekey(method, self):
    req = self.request
    lang = req.get("LANGUAGE", "")
    IGNORED = {"cache_key", "_", "authenticator"}
    items = tuple(sorted((k, v) for k, v in req.form.items() if k not in IGNORED))
    site = getSite()
    uid = req.form.get("UID", None) or req.form.get("selected_news_folders", None)
    if not uid:
        # global cache
        return (site.getId(), "__global__", lang, items)
    obj = api.content.get(UID=uid)
    if not obj:
        return (site.getId(), "__global__", lang, items)
    entity = get_parent_providing(obj, IEntity)
    if not entity:
        return (site.getId(), "__global__", lang, items)
    entity_uid = IUUID(entity, None)
    ann = IAnnotations(site)
    ann_full_key = f"{ENDPOINT_CACHE_KEY}{entity_uid}"
    gen = ann.get(ann_full_key, 0)
    if is_log_active():
        logger.info(f"ENTITY TITLE ========================> {entity.title}")
        logger.info(f"ANNOTATION CACHE KEY ========================> {ann_full_key}")
    return (site.getId(), entity_uid, gen, items, lang)


class SearchGet(BaseSearchGet):

    @ram.cache(_cachekey)
    def _cached_reply(self):
        # Ce code n’est exécuté QUE sur cache MISS
        self.request.response.setHeader("X-RAM-Cache", "MISS")
        self.request.response.setHeader(
            "X-RAM-Cache-Computed-At", str(int(time.time()))
        )
        if is_log_active():
            logger.info("RAMCACHE MISS key=%r", _cachekey(None, self))
        return super().reply()

    def reply(self):
        # Si c'est un HIT, _cached_reply() ne s'exécute pas -> pas de header
        result = self._cached_reply()
        if not self.request.response.getHeader("X-RAM-Cache"):
            self.request.response.setHeader("X-RAM-Cache", "HIT")
            if is_log_active():
                logger.info("RAMCACHE HIT")
        return result
