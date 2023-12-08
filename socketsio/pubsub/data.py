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

    name: str = None
    time: float = None
    data: Any = None

    NAME: ClassVar[str] = "name"
    TIME: ClassVar[str] = "time"
    DATA: ClassVar[str] = "data"

    @classmethod
    def load(cls, data: dict[str, ...]) -> Self:

        return cls(
            name=data[cls.NAME],
            time=data[cls.TIME],
            data=data[cls.DATA]
        )

    def dump(self) -> dict[str, ...]:

        return {
            self.NAME: self.name,
            self.TIME: self.time,
            self.DATA: self.data
        }

    @classmethod
    def encode(cls, data: dict[str, ...] | Self) -> bytes:

        if isinstance(data, cls):
            data = data.dump()

        return json.dumps(data).encode()

    @classmethod
    def decode(cls, data: bytes) -> dict[str, ...]:

        return json.loads(data.decode())
