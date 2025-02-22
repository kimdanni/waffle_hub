__version__ = "0.2.12"

import enum
from collections import OrderedDict


class CustomEnumMeta(enum.EnumMeta):
    def __contains__(cls, item):
        if isinstance(item, str):
            return item.upper() in cls._member_names_
        return super().__contains__(item)

    def __upper__(self):
        return self.name.upper()


class BaseEnum(enum.Enum, metaclass=CustomEnumMeta):
    """Base class for Enum

    Example:
        >>> class Color(BaseEnum):
        >>>     RED = 1
        >>>     GREEN = 2
        >>>     BLUE = 3
        >>> Color.RED == "red"
        True
        >>> Color.RED == "RED"
        True
        >>> "red" in DataType
        True
        >>> "RED" in DataType
        True
    """

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name.upper() == other.upper()
        return super().__eq__(other)

    def __ne__(self, other):
        if isinstance(other, str):
            return self.name.upper() != other.upper()
        return super().__ne__(other)

    def __hash__(self):
        return hash(self.name.upper())

    def __str__(self):
        return self.name.upper()

    def __repr__(self):
        return self.name.upper()


class DataType(BaseEnum):
    # TODO: map to same value

    YOLO = enum.auto()
    ULTRALYTICS = enum.auto()

    COCO = enum.auto()

    AUTOCARE_DLT = enum.auto()

    TRANSFORMERS = enum.auto()


class TaskType(BaseEnum):
    CLASSIFICATION = enum.auto()
    OBJECT_DETECTION = enum.auto()
    SEMANTIC_SEGMENTATION = enum.auto()
    INSTANCE_SEGMENTATION = enum.auto()
    KEYPOINT_DETECTION = enum.auto()
    TEXT_RECOGNITION = enum.auto()
    REGRESSION = enum.auto()


class SplitMethod(BaseEnum):
    RANDOM = enum.auto()
    STRATIFIED = enum.auto()


class HPOMethod(BaseEnum):
    RANDOMSAMPLER = "RANDOMSAMPLER"
    GRIDSAMPLER = "GRIDSAMPLER"
    BOHB = "BOHB"
    TPESAMPLER = "TPESAMPLER"


class SearchOption(BaseEnum):
    FAST = "FAST"
    MEDIUM = "MEDIUM"
    LONG = "LONG"


class Objective(BaseEnum):
    MINIMIZE_LOSS = ("MINIMIZE", "LOSS")
    MAXIMIZE_ACCURACY = ("MAXIMIZE", "ACCURACY")


EXPORT_MAP = OrderedDict(
    {
        DataType.YOLO: "ULTRALYTICS",
        DataType.ULTRALYTICS: "ULTRALYTICS",
        DataType.COCO: "COCO",
        DataType.AUTOCARE_DLT: "AUTOCARE_DLT",
        DataType.TRANSFORMERS: "TRANSFORMERS",
    }
)


BACKEND_MAP = OrderedDict(
    {
        DataType.ULTRALYTICS: {
            "import_path": "waffle_hub.hub.adapter.ultralytics",
            "class_name": "UltralyticsHub",
        },
        DataType.AUTOCARE_DLT: {
            "import_path": "waffle_hub.hub.adapter.autocare_dlt",
            "class_name": "AutocareDLTHub",
        },
        DataType.TRANSFORMERS: {
            "import_path": "waffle_hub.hub.adapter.transformers",
            "class_name": "TransformersHub",
        },
    }
)


for key in list(EXPORT_MAP.keys()):
    EXPORT_MAP[str(key).lower()] = EXPORT_MAP[key]
    EXPORT_MAP[str(key).upper()] = EXPORT_MAP[key]


for key in list(BACKEND_MAP.keys()):
    BACKEND_MAP[str(key).lower()] = BACKEND_MAP[key]
    BACKEND_MAP[str(key).upper()] = BACKEND_MAP[key]
