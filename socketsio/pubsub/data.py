# data.py

import json
from typing import Any, Self, ClassVar
from dataclasses import dataclass

from represent import represent


__all__ = [
    "Data"
]


@dataclass(repr=False)
@represent
class Data:
    """A class to represent a data container message."""

    name: str = None
    time: float = None
    data: Any = None

    NAME: ClassVar[str] = "name"
    TIME: ClassVar[str] = "time"
    DATA: ClassVar[str] = "data"

    @classmethod
    def load(cls, data: dict[str, ...]) -> Self:
        """
        Loads the data into a new data object.

        :param data: The data to load.

        :return: The new data object.
        """

        return cls(
            name=data[cls.NAME],
            time=data[cls.TIME],
            data=data[cls.DATA]
        )

    def dump(self) -> dict[str, ...]:
        """
        Dumps the data of the object.

        :return: The data of the object.
        """

        return {
            self.NAME: self.name,
            self.TIME: self.time,
            self.DATA: self.data
        }

    @classmethod
    def encode(cls, data: dict[str, ...] | Self) -> bytes:
        """
        Encodes the data to bytes of json string.

        :param data: The data to encode.

        :return: The encoded bytes stream.
        """

        if isinstance(data, cls):
            data = data.dump()

        return json.dumps(data).encode()

    @classmethod
    def decode(cls, data: bytes) -> dict[str, ...]:
        """
        Decodes the bytes stream into a json data.

        :param data: The data to decode.

        :return: The json data.
        """

        return json.loads(data.decode())
