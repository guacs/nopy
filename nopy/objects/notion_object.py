from __future__ import annotations

from dataclasses import InitVar
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from typing import Any
from typing import Optional
from typing import Type

from nopy.enums import ObjectTypes

if TYPE_CHECKING:
    from nopy.client import NotionClient


@dataclass
class BaseObject:
    """A representation of the base object from which all other objects
    inherit from.

    This is the base class for Notion objects such as databases and NOT for
    properties and such.

    Attributes:
        id: The id of the Notion object.
        type (ObjectType): The type of the Notion object.
    """

    id: str = ""
    client: InitVar[Optional["NotionClient"]] = None

    def __post_init__(self, client: Optional["NotionClient"]):

        self._type = ObjectTypes.UNSUPPORTED
        self._client = client

    @property
    def type(self):
        return self._type

    def serialize(self) -> dict[str, Any]:
        raise NotImplementedError("to be implemented by subclass")

    @classmethod
    def from_dict(cls: Type[BaseObject], args: dict[str, Any]) -> BaseObject:
        raise NotImplementedError("to be implemented by subclass")


@dataclass
class NotionObject(BaseObject):

    created_time: Optional[datetime] = None
    last_edited_time: Optional[datetime] = None
    archived: bool = False
    created_by: Any = None
    last_edited_by: Any = None
    parent: Any = None