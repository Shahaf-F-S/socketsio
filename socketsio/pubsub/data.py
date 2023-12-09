# data.py

import json
from typing import Any, Self, ClassVar, Iterable
from dataclasses import dataclass

from represent import represent

__all__ = [
    "Data",
    "chain_names",
    "unchain_names"
]

def chain_names(names: Iterable[str], separator: str = ".") -> str:
    """
    Chains togather names with a separator to fore one name.

    :param names: The names to join.
    :param separator: The separator to join names with.

    :return: The chained names.
    """

    chain = separator.join(names)

    if chain.count(separator) >= len(list(names)):
        raise ValueError(
            f"Separator must not appear in any "
            f"of the given names: {', '.join(names)}"
        )

    return chain

def unchain_names(chain: str, separator: str = ".") -> list[str]:
    """
    Unchains the given chain of names.

    :param chain: The chained names.
    :param separator: The separator to split the chain with.

    :return: The names in the chain.
    """

    return chain.split(separator)

@represent
@dataclass(repr=False)
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
