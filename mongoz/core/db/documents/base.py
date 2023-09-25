from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Mapping, Type, TypeVar, Union

import bson
import pydantic
from pydantic import BaseModel, ConfigDict
from pydantic_core._pydantic_core import SchemaValidator as SchemaValidator

from mongoz.core.db.documents._internal import DescriptiveMeta
from mongoz.core.db.documents.metaclasses import BaseModelMeta, MetaInfo
from mongoz.core.db.fields.base import MongozField
from mongoz.core.db.fields.core import ObjectId
from mongoz.core.db.querysets.base import QuerySet
from mongoz.core.db.querysets.expressions import Expression
from mongoz.core.signals.signal import Signal
from mongoz.utils.mixins import is_operation_allowed

T = TypeVar("T", bound="MongozBaseModel")

if TYPE_CHECKING:
    from mongoz.core.signals import Broadcaster


class BaseMongoz(BaseModel, metaclass=BaseModelMeta):
    """
    Base of all Mongoz models with the core setup.
    """

    __db_document__: ClassVar[bool] = False

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        json_encoders={bson.ObjectId: str, Signal: str},
        validate_assignment=True,
    )
    meta: ClassVar[MetaInfo] = MetaInfo(None)
    Meta: ClassVar[DescriptiveMeta] = DescriptiveMeta()

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.extract_default_values_from_field()

    def extract_default_values_from_field(self) -> None:
        """
        Populate the defaults of each Mongoz field if any is passed.

        E.g.: DateTime(auto_now=True) will generate the default for automatic
        dates.
        """
        for field_name, field in self.model_fields.items():
            if hasattr(field, "has_default") and field.has_default():
                setattr(self, field_name, field.get_default_value())

    def get_instance_name(self) -> str:
        """
        Returns the name of the class in lowercase.
        """
        return self.__class__.__name__.lower()

    @classmethod
    def query(cls: Type[T], *values: Union[bool, Dict, Expression]) -> QuerySet[T]:
        """Filter query criteria nad blocks abstract class operations"""
        is_operation_allowed(cls)

        filter_by: List[Expression] = []
        if not values:
            return QuerySet(model_class=cls)

        for arg in values:
            assert isinstance(arg, (dict, Expression)), "Invalid argument to Query"
            if isinstance(arg, dict):
                query_expressions = Expression.unpack(arg)
                filter_by.extend(query_expressions)
            else:
                filter_by.append(arg)

        return QuerySet(model_class=cls, filter_by=filter_by)

    @property
    def signals(self) -> "Broadcaster":
        return self.__class__.signals  # type: ignore

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self}>"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.pk})"


class MongozBaseModel(BaseMongoz):
    __mongoz_fields__: ClassVar[Mapping[str, Type["MongozField"]]]
    id: Union[ObjectId, None] = pydantic.Field(alias="_id")
