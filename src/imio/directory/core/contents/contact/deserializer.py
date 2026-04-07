from collective.schedulefield.schedule import ISchedule
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IFieldDeserializer
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

import json


@implementer(IFieldDeserializer)
@adapter(ISchedule, IDexterityContent, IBrowserRequest)
class ScheduleFieldDeserializer(DefaultFieldDeserializer):
    """Allow non-ASCII characters (e.g. accented) in schedule comments.
    The default DictFieldDeserializer recursively validates inner dict values
    against ASCIILine(), rejecting accented characters. Schedule.validate()
    already skips the 'comment' key, so we use it directly instead."""

    def __call__(self, value):
        if not value:
            return value
        if isinstance(value, str):
            value = json.loads(value)
        self.field.validate(value)
        return value
