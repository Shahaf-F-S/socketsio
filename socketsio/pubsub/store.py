# store.py

import time
from typing import Iterable, Self

from socketsio.pubsub.data import Data


__all__ = [
    "DataStore"
]


class DataStore:
    """A class to contain data lists by keys."""

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
        """
        Inserts the data into the storage.

        :param data: The data object to store.
        """

        queue = self.storage.setdefault(data.name, [])

        queue.append(data)

        if self.limit:
            while len(queue) > self.limit:
                queue.pop(0)

    def insert_all(self, data: Iterable[Data]) -> None:
        """
        Inserts the data into the storage.

        :param data: The data object to store.
        """

        for d in data:
            self.insert(d)

    def is_valid_key(self, key: str) -> bool:
        """
        Checks if a key is a valid key in the storage.

        :param key: The data key.

        :return: The validation value.
        """

        return key not in self.storage

    def validate_key(self, key: str) -> None:
        """
        Checks if a key is a valid key in the storage, otherwise raises an error.

        :param key: The data key.
        """

        if self.is_valid_key(key=key):
            raise KeyError(
                f"Key: '{key}' is not a valid key in storage. "
                f"Valid keys are: {', '.join(self.storage.keys())}"
            )

    def fetch(self, key: str) -> Data:
        """
        Fetches the last data object by the given key.

        :param key: The data key.

        :return: The data object.
        """

        self.validate_key(key=key)

        queue = self.storage[key]

        if len(queue) == 0:
            raise ValueError(
                f"No data is found in storage of key: '{key}'."
            )

        return queue[-1]

    def pop(self, key: str) -> Data:
        """
        Pops the last data object out of the key store and returns the data.

        :param key: The key for the data.

        :return: The data object.
        """

        self.validate_key(key=key)

        queue = self.storage[key]

        if len(queue) == 0:
            raise ValueError(
                f"No data is found in storage of key: '{key}'."
            )

        return queue.pop(-1)

    def remove(self, key: str, adjust: bool = True) -> None:
        """
        Removes the last data object out of the key store.

        :param key: The key for the data.
        :param adjust: The value to adjust for an invalid key.
        """

        try:
            self.pop(key)

        except (KeyError, ValueError) as e:
            if not adjust:
                raise e

    def pop_all(self, keys: Iterable[str], adjust: bool = True) -> dict[str, Data]:
        """
        Pops the last data object out of the key store and returns the data.

        :param keys: The keys for the data.
        :param adjust: The value to adjust for an invalid key.

        :return: The data object.
        """

        data: dict[str, Data] = {}

        for key in keys:
            try:
                data[key] = self.pop(key)

            except (KeyError, ValueError) as e:
                if not adjust:
                    raise e

        return data

    def remove_all(self, keys: Iterable[str], adjust: bool = True) -> None:
        """
        Removes the last data object out of the key store.

        :param keys: The keys for the data.
        :param adjust: The value to adjust for an invalid key.

        :return: The data object.
        """

        self.pop_all(keys=keys, adjust=adjust)

    def fetch_all(
            self,
            keys: Iterable[str],
            adjust: bool = True,
            limit: float = None
    ) -> dict[str, Data]:
        """
        Fetches the last data object by the given key.

        :param keys: The keys for the data.
        :param adjust: The value to adjust for an invalid key.
        :param limit: The time limit for valid data.

        :return: The data object.
        """

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
        """
        Fetches the data queue by the given key.

        :param key: The key for the data.
        :param adjust: The value to adjust for an invalid key.

        :return: The data object.
        """

        try:
            self.validate_key(key=key)

            return self.storage[key].copy()

        except KeyError as e:
            if not adjust:
                raise e

        return []

    def empty(self) -> None:
        """Empties all queues in the storage."""

        for queue in self.storage.values():
            queue.clear()

    def clear(self) -> None:
        """Clears the record of the storage."""

        self.storage.clear()

    def copy(self) -> Self:
        """
        Returns a copy of the storage object.

        :return: A new storage object with the exact same data, in a new structure.
        """

        return DataStore(
            storage={key: values.copy() for key, values in self.storage},
            limit=self.limit
        )