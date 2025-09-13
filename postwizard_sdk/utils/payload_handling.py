"""
Payload handling and manipulation utilities

This module contains functions to handle and manipulate payload data for the PostWizard API.

author: Yoham Gabriel Urbine@GitHub
email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Optional, Dict, Union, Callable

from postwizard_sdk.builders import PostInfoPayload, PostMetaPayload
from postwizard_sdk.models import PostMetaKey, PostKey


def transform_payload_value(
    post_instance: Optional[Dict[str, Union[str, int, bool, None]]],
    post_key: Union[PostMetaKey, PostKey],
    match_text: str,
    new_value: str,
    transform_func: Callable[[str], str],
    result_func: Callable[[str, str], str],
) -> Optional[Union[PostInfoPayload, PostMetaPayload]]:
    """
    Transforms a payload key value based on a match text. In other words, it transforms the value by removing the
    match text and applying a transformation function to it, provided that such text contains relevant information
    (e.g. a stream slug).

    The way the transformed value is combined with the new value depends on the result function. Following the same
    logic, the result function is expected to return a string that can be used as a new value for the post instance by
    using the new value and the transformed/extracted value. Resulting payload instances always include the post id.

    :param post_instance: ``Optional[Dict[str, Union[str, int, bool, None]]]`` -> The post instance to transform.
    :param post_key: ``Union[PostMetaKey, PostKey]`` -> The post key to transform.
    :param match_text: ``str`` -> The text to match at the start of the value.
    :param new_value: ``str`` -> The new base value to replace the matched text.
    :param transform_func: ``Callable[[str], str]`` -> The transform function for the matched text.
    :param result_func: ``Callable[[str, str], str]`` -> The result function for the transformed value.
    :return: ``Optional[Union[PostInfoPayload, PostMetaPayload]]`` -> The transformed payload.
    """
    if isinstance(post_key, PostKey):
        payload_builder = PostInfoPayload()
    else:
        payload_builder = PostMetaPayload()

    if post_instance[post_key.value] is None or not post_instance[
        post_key.value
    ].startswith(match_text):
        return None
    transformed_value = transform_func(post_instance[post_key.value])
    post_instance[post_key.value] = result_func(new_value, transformed_value)
    payload_builder.post_id(post_instance[post_key.ID.value])
    payload_builder.add(post_key, post_instance[post_key.value])
    return payload_builder
