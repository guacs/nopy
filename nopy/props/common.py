from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Any
from typing import Optional
from typing import Type
from zoneinfo import ZoneInfo

from nopy.enums import Colors
from nopy.enums import FileTypes
from nopy.enums import MentionTypes
from nopy.enums import RichTextTypes
from nopy.props.base import BaseProperty


@dataclass
class Annotations(BaseProperty):
    """A representation of the annotations.

    Attributes:
        bold: Mark the text as bold.
        italic: Make the text italic.
        strikethrough: Strikethrough the text.
        underline: Underline the text.
        code: Mark the text as code.
        color: Change the color of the code.
    """

    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: Colors = Colors.DEFAULT

    @classmethod
    def from_dict(cls: Type[Annotations], args: dict[str, Any]) -> Annotations:

        new_args: dict[str, Any] = args.copy()
        new_args["color"] = Colors[new_args["color"].upper()]
        return Annotations(**new_args)


@dataclass
class Date(BaseProperty):
    """A representation of a date in Notion.

    Attributes:
        start: The start date and time.
        end: The end date and time, if any.
        time_zone: The time zone, if any.
    """

    start: datetime
    end: Optional[datetime] = None
    time_zone: Optional[ZoneInfo] = None

    @classmethod
    def from_dict(cls: Type[Date], args: dict[str, Any]) -> Date:

        start = datetime.fromisoformat(args["start"])
        end = None
        time_zone = None
        if end_str := args["end"]:
            end = datetime.fromisoformat(end_str)
        if tz := args["time_zone"]:
            time_zone = ZoneInfo(tz)

        return Date(start, end, time_zone)


@dataclass
class Link(BaseProperty):
    """A representation of a link object.

    Attributes:
        url: The URL.
    """

    url: str

    @classmethod
    def from_dict(cls: Type[Link], args: dict[str, Any]) -> Link:
        return Link(args["url"])


@dataclass
class RichText(BaseProperty):
    """A represenation of a rich text property.

    Attributes:
        plain_text: The plain text without any annotations/styling.
        href: The URL to the link, if any.
        annotations: The annotations/styles applied on this text.
        type (RichTextTypes):
            The type of rich text which will always be
            `RichText.UNSUPPORTED`.
    """

    plain_text: str = ""
    href: str = ""
    annotations: Optional[Annotations] = field(default_factory=Annotations)

    def __post_init__(self):

        self._type: RichTextTypes = RichTextTypes.UNSUPPORTED

    @property
    def type(self) -> RichTextTypes:
        return self._type

    @classmethod
    def from_dict(cls: Type[BaseProperty], args: dict[str, Any]) -> BaseProperty:

        try:
            rich_text_type = RichTextTypes[args["type"].upper()]
        except KeyError:
            rich_text_type = RichTextTypes.UNSUPPORTED

        if rich_text_type == RichTextTypes.TEXT:
            return Text.from_dict(args)
        if rich_text_type == RichTextTypes.MENTION:
            return Mention.from_dict(args)
        if rich_text_type == RichTextTypes.EQUATION:
            return Equation.from_dict(args)

        base = _rich_text_base_args(args)
        return RichText(**base)


@dataclass
class Text(RichText):
    """A represenation of a text type of rich text.

    Attributes:
        plain_text: The plain text without any annotations/styling.
        href: The URL to the link, if any.
        annotations: The annotations/styles applied on this text.
        link: The link within the text, if any.
        type (RichTextTypes):
            The type of rich text which will always be
            `RichText.UNSUPPORTED`.
    """

    link: Optional[Link] = None

    def __post_init__(self):

        self._type = RichTextTypes.TEXT

    @classmethod
    def from_dict(cls: Type[Text], args: dict[str, Any]) -> Text:

        new_args = _rich_text_base_args(args)
        link = args[RichTextTypes.TEXT.value].get("link", None)
        if link:
            new_args["link"] = Link.from_dict(link)
        return Text(**new_args)


@dataclass
class Mention(RichText):
    """A represenation of a mention type of rich text.

    Attributes:
        plain_text: The plain text without any annotations/styling.
        mention_type:
            The type of the mention. Available attributes depend on this
            type.
        id: The id of the mention, if any.
        date: The date mentioned, if any.
        url: The URL mentioned, if any.
        href: The URL to the link, if any.
        annotations: The annotations/styles applied on this text.
        type (RichTextTypes):
            The type of rich text which will always be
            `RichText.UNSUPPORTED`.
    """

    mention_type: MentionTypes = MentionTypes.UNSUPPORTED
    id: str = ""
    date: Optional[Date] = None
    url: Optional[str] = None

    def __post_init__(self):

        self._type = RichTextTypes.MENTION

    @classmethod
    def from_dict(cls: Type[Mention], args: dict[str, Any]) -> Mention:

        new_args: dict[str, Any] = _rich_text_base_args(args)
        try:
            mention_type = MentionTypes[args["mention"]["type"].upper()]
        except KeyError:
            mention_type = MentionTypes.UNSUPPORTED
            new_args["mention_type"] = mention_type
            return Mention(**new_args)

        new_args["mention_type"] = mention_type
        mention_details = args[RichTextTypes.MENTION.value]
        if mention_type == MentionTypes.DATE:
            new_args["date"] = Date.from_dict(mention_details["date"])
        elif mention_type == MentionTypes.LINK_PREVIEW:
            new_args["url"] = mention_details["url"]
        elif mention_type in (MentionTypes.DATABASE, MentionTypes.PAGE):
            new_args["id"] = mention_details[mention_type.value]["id"]

        return Mention(**new_args)


@dataclass
class Equation(RichText):
    """A represenation of an equation type of rich text.

    Attributes:
        plain_text: The plain text without any annotations/styling.
        expression: The mathematical expression as a LaTeX string.
        href: The URL to the link, if any.
        annotations: The annotations/styles applied on this text.
        type (RichTextTypes):
            The type of rich text which will always be
            `RichText.UNSUPPORTED`.
    """

    expression: str = ""

    def __post_init__(self):

        self._type = RichTextTypes.EQUATION

    @classmethod
    def from_dict(cls: Type[Equation], args: dict[str, Any]) -> Equation:

        new_args = _rich_text_base_args(args)
        new_args["expression"] = args[RichTextTypes.EQUATION.value]["expression"]
        return Equation(**new_args)


@dataclass
class File(BaseProperty):
    """A representation of a File object.

    Attributes:
        url: The url of the file.
        type (FileTypes): The 'type' of file.
        expiry_time:
            The date on which the file will expire from Notion.
            NOTE: Only files hosted by Notion will have an `expiry_time`.
            That is, the `type` should be `FileType.FILE`.
    """

    url: str = ""
    expiry_time: Optional[datetime] = None
    type: FileTypes = FileTypes.EXTERNAL

    @classmethod
    def from_dict(cls: Type[File], args: dict[str, Any]) -> File:

        file_type = FileTypes[args["type"].upper()]
        file_details = args[file_type.value]

        new_args: dict[str, Any] = {
            "url": file_details["url"],
            "type": file_type,
        }

        # Only files hosted by Notion have expiry dates
        if file_type == FileTypes.FILE:
            new_args["expiry_time"] = datetime.fromisoformat(
                file_details["expiry_time"]
            )

        return File(**new_args)


@dataclass
class Option(BaseProperty):
    """A representation of an Option.

    This can be used in the options for Select and Multi-Select
    properties.

    Attributes:
        name: Name of the option.
        id: Id of the option.
        color: The color associated with the option.
    """

    name: str
    id: str = ""
    color: Colors = Colors.DEFAULT

    @classmethod
    def from_dict(cls: Type[Option], args: dict[str, Any]) -> Option:
        args["color"] = Colors[args["color"].upper()]
        return Option(**args)


@dataclass
class StatusGroup(BaseProperty):
    """A representation of a Status Group.

    Attributes:
        name: Name of the group.
        id: Id of the group.
        color: Color associated with the group.
        option_ids: The list of option ids associated with the group.
    """

    name: str
    id: str = ""
    color: Colors = Colors.DEFAULT
    option_ids: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls: Type[StatusGroup], args: dict[str, Any]) -> StatusGroup:

        args["color"] = Colors[args["color"].upper()]

        return StatusGroup(**args)


@dataclass
class Emoji(BaseProperty):
    """A representation of the Emoji object.

    Attributes:
        emoji: The emoji as a Unicode string.
    """

    emoji: str

    @classmethod
    def from_dict(cls: Type[Emoji], args: dict[str, Any]) -> Emoji:
        return Emoji(args["emoji"])


# ----- Helper functions for `from_dict` -----
def _rich_text_base_args(args: dict[str, Any]) -> dict[str, Any]:

    return {
        "plain_text": args["plain_text"],
        "href": args["href"],
        "annotations": Annotations.from_dict(args["annotations"]),
    }
