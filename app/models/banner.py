from .abstract_models import (
    BaseNameField,
    BaseImageDescriptionFields,
    BaseDateTimeFields
)


class Banner(
    BaseNameField,
    BaseImageDescriptionFields,
    BaseDateTimeFields
):
    pass
