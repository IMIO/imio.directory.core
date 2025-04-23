from collective.schedulefield.behavior import (
    IMultiScheduledContent as IBaseMultiScheduledContent,
)
from collective.schedulefield.behavior import (
    MultiScheduledContent as BaseMultiScheduledContent,
)
from collective.schedulefield.behavior import MultiScheduleField
from collective.schedulefield.behavior import ScheduleWithTitle
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import provider


class MultiScheduledContent(BaseMultiScheduledContent):
    pass


@provider(IFormFieldProvider)
class IMultiScheduledContent(IBaseMultiScheduledContent):
    """Version personnalisée de l'interface"""

    multi_schedule = MultiScheduleField(
        title=_("Multi Schedule Custom"),
        value_type=ScheduleWithTitle(
            __name__="MultiSchedule",
            schema=IBaseMultiScheduledContent["multi_schedule"].value_type.schema,
            required=False,
        ),
        required=False,
    )
