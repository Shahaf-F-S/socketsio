# store.py

import time
from typing import Iterable, Self

from socketsio.pubsub.data import Data


__all__ = [
    "DataStore"
]


class DataStore:

    def __init__(
            self,
            storage: dict[str, list[Data]] = None,
            limit: int = None
    ) -> None:

        if storage is None:
            storage = {}

        self.storage = storage
        self.limit = limit

    def insert(self, data: Data) -> None:

        queue = self.storage.setdefault(data.name, [])

        queue.append(data)

        if self.limit:
            while len(queue) > self.limit:
                queue.pop(0)

    def insert_all(self, data: Iterable[Data]) -> None:

        for d in data:
            self.insert(d)

    def is_valid_key(self, key: str) -> bool:

        return key not in self.storage

    def validate_key(self, key: str) -> None:

        if self.is_valid_key(key=key):
            raise KeyError(
                f"Key: '{key}' is not a valid key in storage. "
                f"Valid keys are: {', '.join(self.storage.keys())}"
            )

    def fetch(self, key: str) -> Data:

        self.validate_key(key=key)

        queue = self.storage[key]

        if len(queue) == 0:
            raise ValueError(
                f"No data is found in storage of key: '{key}'."
            )

        return queue[-1]

    def pop(self, key: str) -> Data:

        self.validate_key(key=key)

        queue = self.storage[key]

        if len(queue) == 0:
            raise ValueError(
                f"No data is found in storage of key: '{key}'."
            )

        return queue.pop(-1)

    def remove(self, key: str, adjust: bool = True) -> None:

        try:
            self.pop(key)

        except (KeyError, ValueError) as e:
            if not adjust:
                raise e

    def pop_all(self, keys: Iterable[str], adjust: bool = True) -> dict[str, Data]:

        data: dict[str, Data] = {}

        for key in keys:
            try:
                data[key] = self.pop(key)

            except (KeyError, ValueError) as e:
                if not adjust:
                    raise e

        return data

    def remove_all(self, keys: Iterable[str], adjust: bool = True) -> None:

        self.pop_all(keys=keys, adjust=adjust)

    def fetch_all(
            self,
            keys: Iterable[str],
            adjust: bool = True,
            limit: float = None
    ) -> dict[str, Data]:

        data: dict[str, Data] = {}

        for key in keys:
            try:
                d = self.fetch(key)

                if not (limit and ((time.time() - d.time) > limit)):
                    data[key] = d

            except (KeyError, ValueError) as e:
                if not adjust:
                    raise e

        return data

    def fetch_queue(self, key: str, adjust: bool = True) -> list[Data]:

        try:
            self.validate_key(key=key)

            return self.storage[key].copy()

        except KeyError as e:
            if not adjust:
                raise e

        return []

    def empty(self) -> None:

        for queue in self.storage.values():
            queue.clear()

    def clear(self) -> None:

        self.storage.clear()

    def copy(self) -> Self:

        return DataStore(
            storage={key: values.copy() for key, values in self.storage},
            limit=self.limit
        )