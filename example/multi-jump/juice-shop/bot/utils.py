import asyncio
import io
import json
import zipfile
from enum import Enum
from typing import TYPE_CHECKING, Annotated, Any, Mapping, Sequence, TypeVar

from loguru import logger
from pydantic import BeforeValidator
from typing_extensions import TypeAliasType

from config import settings


class AutoStrEnum(str, Enum):
    """
    StrEnum where auto() returns the field name.
    See https://docs.python.org/3.9/library/enum.html#using-automatic-values
    """

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list
    ) -> str:
        return name


T = TypeVar("T")


def is_json_serializeable(data: Any) -> "JSONType":
    json.dumps(data)
    return data


if TYPE_CHECKING:
    JSONType = (
        Mapping[str, "JSONType"]
        | Sequence["JSONType"]
        | str
        | int
        | float
        | bool
        | None
    )
else:
    JSONType = Annotated[
        TypeAliasType(
            "JSONType",
            (
                Mapping[str, "JSONType"]
                | Sequence["JSONType"]
                | str
                | int
                | float
                | bool
                | None
            ),
        ),
        BeforeValidator(is_json_serializeable),
    ]

NotNoneJSONType = Mapping[str, JSONType] | Sequence[JSONType] | str | int | float | bool


async def empty_coro() -> None:
    return


async def sleep(time: float) -> None:
    if settings.debug:
        await asyncio.sleep(1)
        return
    logger.info(f"Sleep {time}s")
    await asyncio.sleep(time)


def create_zip_with_text_content(text_content: str) -> bytes:
    # 创建一个内存中的字节流对象
    mem_zip = io.BytesIO()

    # 创建一个ZipFile对象，指定模式为写入
    with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # 添加一个名为example.txt的文件到压缩包中
        zf.writestr("example.txt", text_content)

    # 获取内存中的压缩包内容
    mem_zip.seek(0)
    zip_data = mem_zip.read()

    return zip_data
