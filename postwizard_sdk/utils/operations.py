"""
PostWizard API Utilities - Common Operations
This module contains utility functions for interacting with the PostWizard API.

author: Yoham Gabriel Urbine@GitHub
email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
from json import JSONDecodeError
from typing import Dict, List, Union

# Third-party imports
import requests

# Local imports
from postwizard_sdk.builders.api_url_builder import APIUrlBuilder
from postwizard_sdk.builders import PostMetaNestedPayload, PostInfoNestedPayload
from postwizard_sdk.builders.interfaces import NestedPayloadBuilder
from postwizard_sdk.builders.taxonomy_builder import TaxonomyNestedPayload
from postwizard_sdk.models import PostType
from postwizard_sdk.utils.auth import PostWizardAuth


def update_post_meta(
    payload: PostMetaNestedPayload,
    post_id: int,
    auto_thumb: bool = False,
    retries: int = 5,
    timeout: int = 1,
) -> int:
    """
    Updates the meta fields of a post.
    This function sends a POST request to the PostWizard API to update the metadata of a post.

    :param payload: ``PostMetaPayload`` -> The payload containing the metadata to update.
    :param post_id: ``int`` -> The ID of the post to update.
    :param auto_thumb: ``bool`` -> Whether to allow PostWizard to locate the thumbnail in the server and link it to the post.
    :param retries: ``int`` -> Number of retries to attempt before giving up.
    :param timeout: ``int`` -> Timeout in seconds for the request.
    :return: ``int`` -> The HTTP status code of the response.
    """
    api_addr = APIUrlBuilder().posts_meta(
        post_id, auto_thumb=auto_thumb, retries=retries, timeout=timeout
    )
    token_headers = PostWizardAuth.bearer_auth_flow()
    request_info = requests.post(
        api_addr.build(), headers=token_headers, json=dict(payload.build())
    )
    return request_info.status_code


def update_post_bypass(payload: PostInfoNestedPayload, post_id: int) -> int:
    """
    Updates the fields of a post.
    This function sends a POST request to the PostWizard API to update the details of a post.
    This function bypasses the WordPress API and uses the PostWizard API directly on the server database.

    :param payload: ``PostInfoPayload`` -> The payload containing the metadata to update.
    :param post_id: ``int`` -> The ID of the post to update.
    :return: ``int`` -> The HTTP status code of the response.
    """
    api_addr = APIUrlBuilder().posts(post_id)
    token_headers = PostWizardAuth.bearer_auth_flow()
    request_info = requests.post(
        api_addr.build(), headers=token_headers, json=payload.build()
    )
    return request_info.status_code


def get_all_payload(
    api_addr: APIUrlBuilder,
) -> List[Dict[str, Union[str, int, bool, None]]]:
    """
    Retrieves all post metadata from the PostWizard API.
    This function sends a GET request to the PostWizard API to retrieve all post metadata.
    :param api_addr: ``APIUrlBuilder`` -> The API URL builder object.
    :return: ``List[Dict[str, Union[str, int, bool, None]]]`` -> List of dictionaries containing post metadata.
    """
    token_headers = PostWizardAuth.bearer_auth_flow()
    request_info = requests.get(api_addr.build(), headers=token_headers)
    return request_info.json()


def get_all_post_meta() -> List[Dict[str, Union[str, int, bool, None]]]:
    """
    Retrieves all post metadata from the PostWizard API.
    This function sends a GET request to the PostWizard API to retrieve all post metadata.

    :return: ``List[Dict[str, Union[Optional[str, int, bool]]]]`` -> List of dictionaries containing post metadata.
    """
    api_addr = APIUrlBuilder().post_meta_dump()
    return get_all_payload(api_addr)


def get_all_post_by_type(
    post_type: PostType,
) -> List[Dict[str, Union[str, int, bool, None]]]:
    api_addr = APIUrlBuilder().posts_dump_by_type(post_type)
    return get_all_payload(api_addr)


def send_batch_payload(
    api_addr: APIUrlBuilder, payloads: List[NestedPayloadBuilder]
) -> Dict[str, Union[str, int, List[int]]]:
    """
    Sends a batch of payloads to the PostWizard API.
    This function sends a POST request to the PostWizard API to update the metadata of multiple posts.

    :param api_addr: ``APIUrlBuilder`` -> The API URL builder object.
    :param payloads: ``List[PayloadBuilder]`` -> The list of payloads to send.
    :return: ``Dict[str, Union[str, int, List[int]]]`` -> The response from the PostWizard API.
    """
    token_headers = PostWizardAuth.bearer_auth_flow()
    payload = [dict(builder.build()) for builder in payloads if builder is not None]
    request_info = requests.post(api_addr.build(), headers=token_headers, json=payload)
    return request_info.json()


def send_meta_batch_job(
    payload: List[PostMetaNestedPayload],
) -> Dict[str, Union[str, int, List[int]]]:
    """
    Specialised method that sends a batch of metadata updates to the PostWizard API.

    :param payload: ``List[PostMetaPayload]`` -> The list of payloads containing the metadata to update.
    :return: ``Dict[str, Union[str, int, List[int]]]`` -> The response from the PostWizard API.
    """
    api_addr = APIUrlBuilder().post_meta_batch()
    return send_batch_payload(api_addr, payload)


def send_post_batch_job(
    payload: List[PostInfoNestedPayload],
) -> Dict[str, Union[str, int, List[int]]]:
    """
    Specialised method that sends a batch of post updates to the PostWizard API.

    :param payload: ``List[PostInfoPayload]`` -> The list of payloads containing the post information to update.
    :return: ``Dict[str, Union[str, int, List[int]]]`` -> The response from the PostWizard API.
    """
    api_addr = APIUrlBuilder().post_batch()
    return send_batch_payload(api_addr, payload)


def add_taxonomy(
    payload: TaxonomyNestedPayload, post_id: int = 0, link: bool = False
) -> int:
    """
    Adds a taxonomy to a post.
    This function sends a POST request to the PostWizard API to add a taxonomy to a post.

    If the taxonomy exists, PostWizard will look for it and return the term id;
    otherwise, it will create a new taxonomy and also return the term id.
    If the request is not successful, it returns ``-1``.

    :param payload: ``TaxonomyPayload`` -> The payload containing the taxonomy to add.
    :param post_id: ``int`` -> The ID of the post to add the taxonomy to.
    :param link: ``bool`` -> Whether to link the taxonomy to the post.
    :return: ``int`` -> The term id of the taxonomy
    """
    if link:
        api_addr = APIUrlBuilder().taxonomies_link(post_id)
    else:
        api_addr = APIUrlBuilder().taxonomies_add()
    token_headers = PostWizardAuth.bearer_auth_flow()
    request_info = requests.post(
        api_addr.build(), headers=token_headers, json=payload.build_to_dict()
    )
    try:
        logging.info(f"PostWizard Server Result: {request_info.json()}")
        if request_info.status_code == 200 or request_info.status_code == 201:
            request_json = request_info.json()
            return request_json["data"][0]["term_id"]
        return -1
    except JSONDecodeError as json_error:
        logging.error(
            f"Raised {json_error!r} while decoding JSON response: Status code {request_info.status_code}"
        )


def taxonomy_unlink(post_id: int) -> int:
    """
    Unlinks a taxonomy from a post.
    This function sends a POST request to the PostWizard API to unlink a taxonomy from a post.
    It can be used to unlink a taxonomy from the WordPress site or, if a post is added, to unlink the taxonomy from the post.

    :param post_id: ``int`` -> The ID of the post to unlink the taxonomy from.
    :return: ``int`` -> The HTTP status code of the response.
    """
    api_addr = APIUrlBuilder().taxonomies_unlink(post_id)
    token_headers = PostWizardAuth.bearer_auth_flow()
    request_info = requests.post(api_addr.build(), headers=token_headers)
    return request_info.status_code


def remove_taxonomy(
    payload: TaxonomyNestedPayload,
) -> Dict[str, Union[str, int, bool, None, List[Dict[str, Union[str, int]]]]]:
    """
    Removes a taxonomy from a post.
    This function sends a POST request to the PostWizard API to remove a taxonomy from a post.
    It can be used to remove a taxonomy from the WordPress site or, if a post is added, to remove the taxonomy from the post.

    :param payload: ``TaxonomyPayload`` -> The payload containing the taxonomy to remove.
    :return: ``Dict[str, Union[str, int, bool, None, List[Dict[str, Union[str, int]]]]]`` -> The response from the PostWizard API.
    """
    api_addr = APIUrlBuilder().taxonomies_remove()
    token_headers = PostWizardAuth.bearer_auth_flow()
    request_info = requests.delete(
        api_addr.build(), headers=token_headers, json=payload.build_to_dict()
    )
    return request_info.json()
