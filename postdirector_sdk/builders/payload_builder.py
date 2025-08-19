"""
Payload Builder

This module defines the PayloadBuilder class, which is an abstract base class for
classes that build payloads for API requests or other data to be consumed in JSON format.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from abc import ABC, abstractmethod
from enum import EnumType
from types import MappingProxyType
from typing import Generic, TypeVar, Dict, Optional, Self, Mapping, Union

K = TypeVar("K", str, EnumType)
V = TypeVar("V", bound=Union[str, int, bool])


class PayloadBuilder(ABC, Generic[K, V]):
    def __init__(self):
        """
        Initialize the PayloadBuilder with a blank payload.

        """
        self._payload: Dict[K, V] = {}

    @abstractmethod
    def _plus(self, key: K, value: V) -> Self:
        """
        Add a key-value pair to the payload field and return the builder for chaining.

        :param key: The key to be added to the payload.
        :param value: The value to be associated with the key.
        """
        if key in self._payload:
            self._payload[key].update(value)
        else:
            self._payload[key] = value
        return self

    @abstractmethod
    def build(self) -> Optional[Mapping[K, V]]:
        """
        Build the final payload and return it back to the caller.
        It works as a marker for the end of the payload building process to
        communicate to the caller that the payload is ready to be consumed.

        :return: The built payload.
        """
        if not self._payload:
            return None
        return MappingProxyType(self._payload)

    @abstractmethod
    def clear(self) -> None:
        """
        Clear the payload.

        :return: ``None``
        """
        self._payload = {}
