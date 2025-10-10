"""
Payload Builder

This module defines the PayloadBuilder class, which is an abstract base class for
classes that build payloads for API requests or other data to be consumed in JSON format.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from abc import ABC
from enum import Enum
from types import MappingProxyType
from typing import Generic, TypeVar, Dict, Optional, Self, Mapping, Union

K = TypeVar("K", str, Enum)
V = TypeVar("V", bound=Union[str, int, bool])


class PayloadBuilder(ABC, Generic[K, V]):
    def __init__(self):
        """
        Initialize the PayloadBuilder with a blank payload.

        """
        self._payload: Dict[K, Dict[K, V] | V] = {}

    def _plus(self, key: K, value: V) -> Self:
        """
        Add a key-value pair to the payload field and return the builder for chaining.

        :param key: The key to be added to the payload.
        :param value: The value to be associated with the key.
        """
        # normalize key to string when using Enum keys in child classes
        real_key = key.value if hasattr(key, "value") else key

        existing = self._payload.get(real_key)
        # If neither existing nor value are dict-like, just set/overwrite
        if existing is None:
            self._payload[real_key] = value

        return self

    def _nest(self, key: K, nested_key: K, value: V):
        """
        Add a nested key-value pair to the payload field and return the builder for chaining.

        :param key: The key to be added to the payload.
        :param nested_key: The nested key to be added to the payload.
        :param value: The value to be associated with the nested key.
        """
        # normalize key to string when using Enum keys in child classes
        real_key = key.value if hasattr(key, "value") else key
        real_nested_key = (
            nested_key.value if hasattr(nested_key, "value") else nested_key
        )

        existing = self._payload.get(real_key)
        # If neither existing nor value are dict-like, just set/overwrite
        if existing is None:
            self._payload[real_key] = {real_nested_key: value}
        else:
            self._payload[real_key][real_nested_key] = value
        return self

    def build(self) -> Optional[Mapping[K, V]]:
        """
        Return the final payload back to the caller.
        It works as a marker for the end of the payload building process to
        communicate to the caller that the payload is ready to be consumed.

        **The payload is immutable and cannot be modified after it is built.
        Any mutations take place on the internal representation by specialised methods
        defined by the concrete builder class. In case this payload is going to be serialized to JSON,
        it is recommended to cast it to a ``dict`` type to avoid tracebacks in the caller.**

        :return: The built payload.
        """
        if not self._payload:
            return None
        return MappingProxyType(self._payload)

    def build_to_dict(self) -> Optional[Mapping[K, V]]:
        """
        Return the final payload back to the caller as a dictionary.

        :return: The built payload.
        """
        if not self._payload:
            return None
        return dict(self.build())

    def clear(self) -> None:
        """
        Clear the payload and return the builder to its initial state for reuse.

        :return: ``None``
        """
        self._payload = {}
