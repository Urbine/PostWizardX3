"""
URL Builder

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import re
from abc import ABC
from enum import Enum
from typing import Generic, TypeVar, Optional, Self, Union

K = TypeVar("K", str, Enum)
V = TypeVar("V", bound=Union[str, int])


class URLBuilder(ABC, Generic[K, V]):
    def __init__(self, base_url: str):
        """
        Initialize the URLBuilder with a base URL provided by the
        concrete builder class.

        :param base_url: The base URL for the API endpoint.
        """
        self._url: str = base_url.strip("/")

        # Back-up URL in case the builder needs to be reused.
        self._bck_url: str = base_url.strip("/")

    def _plus_path(self, endpoint: K, value: Union[V, K]) -> Self:
        """
        Add an endpoint-value pair to the internal URL field and return the builder for chaining.
        The caller can also provide an integer to be concatenated to the final URL string.

        The leading endpoint parameter has to be an enum defined by the sdk, however, the value parameter
        can be either a string or another enum, so that endpoints can be joined.

        If you need to join an endpoint with the one that follows, you can skip the value by passing an
        empty string, so that there is no trailing slash after it.
        This allows for natural chaining of endpoints.

        :param key: The key to be added to the payload.
        :param value: The value to be associated with the key.
        """
        # normalize key and values to string when using Enum keys in child classes
        real_endpoint = endpoint.value if hasattr(endpoint, "value") else endpoint
        real_value = value.value if hasattr(value, "value") else value
        value_chunk = f"{real_value}" if not real_value else f"/{real_value}"

        self._url += f"/{real_endpoint}{value_chunk}"
        return self

    def _plus_query_param(self, query_param: K, query_value: Union[K, V]) -> Self:
        """
        Add a query parameter to the internal URL field and return the builder for chaining.
        If the URL already has a query parameter, the new one will be appended with an ampersand.

        :param query_param: ``K`` -> The query parameter to be added.
        :param query_value: ``Union[K, V]`` -> The value of the query parameter to be added.
        :return: ``Self`` -> The current builder instance.
        """
        real_query_value = (
            query_value.value if hasattr(query_value, "value") else query_param
        )
        if re.findall(r"[?]+", self._url):
            self._url += f"&{query_param.value}={real_query_value}"
        else:
            self._url += f"?{query_param.value}={real_query_value}"
        return self

    def build(self) -> Optional[str]:
        """
        Return the final payload back to the caller.
        It works as a marker for the end of the payload building process to
        communicate to the caller that the payload is ready to be consumed.

        :return: The built payload.
        """
        return self._url

    def reset(self) -> None:
        """
        Reset the internal URL field to its back-up value and return the builder
        in case of reuse

        :return: ``None``
        """
        self._url = self._bck_url
