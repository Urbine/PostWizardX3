# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
WordPress API integration module for data extraction, caching, and analysis.

This module provides a class-based interface to interact with the WordPress REST API,
enabling retrieval, creation, and management of posts, tags, categories, and media.
It supports local caching of API data, efficient synchronization, and various utilities
for filtering, mapping, and reporting on WordPress site content.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__email__ = "yohamg@programmer.net"

import warnings
from json import JSONDecodeError

import aiohttp
import asyncio
import datetime
import logging
import os
import re
import requests
import threading
import time

from collections import namedtuple, deque
from pathlib import Path
from typing import Optional, List, Any, Dict, Deque, Union

# Third-party modules
import urllib3
from requests.auth import HTTPBasicAuth

# Local implementations
from core.utils.file_system import load_json_ctx, export_request_json, logging_setup
from core.models.file_system import ApplicationPath
from core.utils.strings import clean_filename, match_list_single
from core.utils.helpers import get_duration
from wordpress.exceptions.internal_exceptions import (
    MissingCacheError,
    YoastSEOUnsupported,
    CacheCreationAuthError,
)
from wordpress.models.taxonomies import WPTaxonomyMarker, WPTaxonomyValues
from wordpress.models.endpoints import WPEndpoints
from wordpress.models.wpost import WPost


class WordPress:
    """
    WordPress API handler for data extraction, caching, and analysis.

    This class encapsulates the WordPress REST API integration, enabling retrieval,
    creation, and management of posts, tags, categories, and media. It supports local
    caching of API data, efficient synchronization, and various utilities for filtering,
    mapping, and reporting on WordPress site content.

    Attributes:
        fq_domain_name (str): Fully qualified domain name of the WordPress site.
        username (str): Username for WordPress API authentication.
        app_password (str): Application password for WordPress API authentication.
        cache_path (str | Path): Path to the local cache file.
        cache_dir (str): Directory path for the cache file.
        cache_name (str): Name of the cache file.
        cache_metadata_file (str): Name of the metadata file for the cache file.
        cache_metadata_path (str | Path): Path to the metadata file for the cache file.
        __cache_metadata (dict | list[dict]): Metadata for the cache file.
        cached_pages (int): Number of cached pages.
        total_posts (int): Total number of posts.
        last_updated (str): Date when the cache was last updated.
    """

    def __init__(
        self,
        fq_domain_name: str,
        username: str,
        password: str,
        cache_path: str | Path,
        use_photo_support: bool = False,
        unique_logging_session: bool = True,
    ):
        """
        Initializes the WordPress API handler with authentication and cache configuration.
        If you are using the photo cache, please make sure that the cache filename is different,
        otherwise the existing file will be overwritten. If you manage posts and photo posts
        in the same site, create two instances of WordPress, one for posts and one with photo support.

        :param fq_domain_name: ``str`` -> Fully qualified domain name of the WordPress site.
        :param username: ``str`` -> Username for WordPress API authentication.
        :param password: ``str`` -> Application password for WordPress API authentication.
        :param cache_path: ``str | Path`` -> Path to the local cache file, including the filename.
        :param use_photo_support: ``bool`` -> Flag indicating whether to fetch photo posts. Default is False.
        :param unique_logging_session: ``bool`` -> Flag indicating whether to set up an independent logging session.
        :return: ``None``
        """
        if unique_logging_session:
            logging_setup(ApplicationPath.LOGGING.value, __file__)
        self.session_number = os.environ.get("SESSION_ID")
        self.fq_domain_name = fq_domain_name
        self.api_base_url = f"https://{self.fq_domain_name}/wp-json/wp/v2"
        self.username = username
        self.app_password = password
        self.cache_path = cache_path
        self.use_photo_cache = use_photo_support
        self.cache_dir = os.path.split(self.cache_path)[0]
        self.cache_name = os.path.basename(self.cache_path)
        self.cache_metadata_file = (
            f"{os.path.split(self.cache_path)[1].split('.')[0]}_metadata.json"
        )
        self.cache_metadata_path = self.cache_path if self.cache_path else None
        self.__cache_metadata: Optional[List[dict]] = (
            load_json_ctx(
                Path(self.cache_dir, self.cache_metadata_file), thread_safe=False
            )
            if os.path.exists(self.cache_path)
            else None
        )
        self.cached_pages: Optional[int] = None
        self.total_posts: Optional[int] = None
        self.last_updated: Optional[str] = None
        self.created_posts: List[WPost] = []
        self.cache_page_num = 0
        logging.info(f"Using {self.api_base_url} as WordPress API base url")

        # Set up cache dir, if it does not exist.
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

        if self.__cache_metadata:
            metadata_fields = self.__cache_metadata[0][self.cache_name]
            self.cached_pages: int = metadata_fields["cached_pages"]
            self.total_posts: int = metadata_fields["total_posts"]
            self.last_updated: str = metadata_fields["last_updated"]

        try:
            if os.path.exists(self.cache_path):
                self.cache_data: List[dict] = load_json_ctx(
                    Path(self.cache_path), thread_safe=False, log_err=True
                )
                self.cache_sync()
            else:
                self.create_export_local_cache()
        except requests.ConnectionError:
            if os.path.exists(self.cache_path):
                self.cache_data: List[dict] = load_json_ctx(
                    Path(self.cache_path), thread_safe=False
                )
            else:
                raise MissingCacheError(self.cache_path)

    def curl_wp_self_concat(
        self,
        http: urllib3.PoolManager,
        param_lst: list[str],
    ) -> urllib3.BaseHTTPResponse:
        """
        Makes a GET request to the WordPress API using urllib3 and basic authentication.

        :param http: ``urllib3.PoolManager`` -> HTTP client for requests.
        :param param_lst: ``list[str]`` -> List of URL parameters to append to the endpoint.
        :return: ``urllib3.BaseHTTPResponse`` -> HTTP response object.
        """
        wp_self: str = self.api_base_url
        username_: str = self.username
        app_pass_: str = self.app_password
        headers = urllib3.make_headers(
            keep_alive=True,
            accept_encoding=True,
            basic_auth=f"{username_}:{app_pass_}",
        )
        wp_self: str = wp_self + "".join(param_lst)
        return http.request("GET", wp_self, headers=headers)

    def setup_basic_auth(self):
        """
        Sets up basic authentication boilerplate for the WordPress API to promote code reuse.

        :return: ``tuple[str, HTTPBasicAuth]`` -> A tuple containing the base URL and the HTTPBasicAuth object.
        """
        wp_self: str = self.api_base_url
        username_: str = self.username
        app_pass_: str = self.app_password
        auth_wp = HTTPBasicAuth(username_, app_pass_)
        return wp_self, auth_wp

    def create_local_cache(self, wp_cache_fname: str) -> list[dict]:
        """
        Fetches all posts from the WordPress site and creates a local cache.

        :param wp_cache_fname: ``str`` -> Cache filename to use for storing posts.
        :return: ``list[dict]`` -> List of post dictionaries.
        """
        result_lock = threading.Lock()
        result_deque = deque()

        x_wp_total = 0
        x_wp_totalpages = 0

        def add_result(elem) -> None:
            """
            Appends an element to a shared list while ensuring thread safety using a lock.

            :param elem: ``Any`` -> Element to be appended to the shared list.
            :return: ``None``
            """
            timeout = 30
            try:
                if result_lock.acquire(timeout=timeout):
                    result_deque.append(elem)
                else:
                    print(
                        f"Could not acquire lock in {threading.current_thread()!r} at add_result() within {timeout} seconds."
                    )
            finally:
                result_lock.release()

        end_param_posts = [
            WPEndpoints.POSTS.value
            if not self.use_photo_cache
            else WPEndpoints.PHOTOS.value
        ]
        wp_cache: str = clean_filename(wp_cache_fname, "json")
        print(f"\nCreating WordPress {wp_cache} cache file...\n")

        http = urllib3.PoolManager()
        curl_wp = self.curl_wp_self_concat(http, list(end_param_posts))
        headers = curl_wp.headers
        try:
            x_wp_total += int(headers["x-wp-total"])
            x_wp_totalpages += int(headers["x-wp-totalpages"])
        except KeyError:
            raise CacheCreationAuthError
        end_param_posts.append(WPEndpoints.PAGE.value)

        wp_pages = []
        for page_num in range(1, x_wp_totalpages + 1):
            wp_self: str = self.api_base_url
            wp_pages.append(wp_self + "".join(end_param_posts) + str(page_num))

        semaphore = asyncio.Semaphore(value=5)

        async def async_wp_self_concat(
            session: aiohttp.ClientSession, wp_url: str
        ) -> None:
            """
            Coroutine to fetch a single page of posts from the WordPress API.

            :param session: ``aiohttp.ClientSession`` -> HTTP session for requests.
            :param wp_url: ``str`` -> URL to fetch.
            :return: ``None``
            """
            username_: str = self.username
            app_pass_: str = self.app_password
            auth = aiohttp.BasicAuth(username_, app_pass_)
            headers_aiohttp = {"keep-alive": "True", "accept-encoding": "True"}
            async with semaphore:
                async with session.get(
                    wp_url, auth=auth, headers=headers_aiohttp
                ) as response:
                    if response.status != 400:
                        print(f"--> Fetching page #{wp_url.split('=')[-1]}")

                        res_json = await response.json()
                        for item in res_json:
                            add_result(item)

        async def get_all_posts() -> None:
            """
            Fetches all post pages asynchronously and aggregates results.

            :return: ``None``
            """
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(30),
                connector=aiohttp.TCPConnector(
                    ssl_shutdown_timeout=10.0, force_close=True
                ),
            ) as session:
                pages = [async_wp_self_concat(session, wp_page) for wp_page in wp_pages]
                await asyncio.gather(*pages)

        asyncio.run(get_all_posts())

        # Assumes that no config file exists.
        self.local_cache_config(x_wp_totalpages, x_wp_total)
        print(f"\n{'DONE':=^30}\n")
        return list(result_deque)

    def create_export_local_cache(self) -> None:
        """
        Helper function that creates and exports the WordPress local cache.

        :return: ``None``
        """
        wp_cache = self.create_local_cache(self.cache_name)
        export_request_json(self.cache_name, wp_cache, 1, target_dir=self.cache_dir)
        self.cache_data = wp_cache
        return None

    def update_json_cache(self) -> list[dict]:
        """
        Updates the local WordPress cache file by fetching new posts.

        :return: ``list[dict]`` -> Updated list of post dictionaries.
        :raises core.utils.custom_exceptions.MissingCacheError: If the cache file is missing.
        """
        http = urllib3.PoolManager(
            num_pools=10,
            maxsize=10,
            retries=urllib3.Retry(total=2, backoff_factor=0.5),
        )

        params_posts: list[str] = (
            [WPEndpoints.POSTS.value]
            if not self.use_photo_cache
            else [WPEndpoints.PHOTOS.value]
        )
        x_wp_total = 0
        x_wp_totalpages = 0
        # The loop will add 1 to page num when the first request is successful.
        page_num = self.cached_pages - 2
        result_dict: List[Dict[str, Any]] = self.cache_data
        total_elems = len(result_dict)
        recent_posts: list[dict] = []
        page_num_param: bool = False
        while True:
            curl_json = self.curl_wp_self_concat(http, params_posts)
            if curl_json.status == 400:
                diff = x_wp_total - total_elems
                if diff != 0:
                    add_list = recent_posts[:diff]
                    add_list.reverse()
                    for recent in add_list:
                        result_dict.insert(0, recent)
                self.local_cache_config(page_num, x_wp_total)
                return result_dict
            else:
                page_num += 1
                if not page_num_param:
                    headers = curl_json.headers
                    x_wp_total += int(headers["x-wp-total"])
                    x_wp_totalpages = int(headers["x-wp-totalpages"])  # noqa: F841
                    params_posts.append(WPEndpoints.PAGE.value)
                    params_posts.append(str(page_num))
                    page_num_param = True
                else:
                    params_posts[-1] = str(page_num)
                for item in curl_json.json():
                    if item not in result_dict:
                        recent_posts.append(item)
                    else:
                        continue

    def async_update_json_cache(self) -> List[Dict[str, Any]]:
        """
        Updates the local WordPress cache file by fetching new posts.
        Use update_json_cache instead, this one needs more testing.

        :return: ``list[dict]`` -> Updated list of post dictionaries.
        """
        self.cache_page_num = self.cached_pages - 2
        x_wp_total = 0
        x_wp_totalpages = 0

        http = urllib3.PoolManager(
            num_pools=10,
            maxsize=10,
            retries=urllib3.Retry(total=2, backoff_factor=0.5),
        )
        params_posts: Deque[str] = deque(
            [WPEndpoints.POSTS.value]
            if not self.use_photo_cache
            else [WPEndpoints.PHOTOS.value]
        )
        # Get headers
        curl_json = self.curl_wp_self_concat(http, list(params_posts))
        headers = curl_json.headers
        x_wp_total += int(headers["x-wp-total"])
        x_wp_totalpages = int(headers["x-wp-totalpages"])
        http.clear()

        def generate_params(total_pages):
            params_list = []
            while self.cache_page_num <= total_pages:
                self.cache_page_num += 1
                params_posts.append(str(self.cache_page_num))
                params_list.append("".join(params_posts))
                params_posts.pop()
                if WPEndpoints.PAGE.value not in params_posts:
                    params_posts.append(WPEndpoints.PAGE.value)
            return params_list

        result_dict: List[Dict[str, Any]] = self.cache_data
        total_elems = len(result_dict)
        recent_posts: Deque[dict] = Deque()

        recent_posts_lock = threading.Lock()
        client_semaphore = asyncio.Semaphore(value=5)

        def add_recent_posts(elem):
            try:
                if recent_posts_lock.acquire(timeout=5):
                    recent_posts.append(elem)
            finally:
                recent_posts_lock.release()

        async def get_recent_loop(semaphore, client_session, params_req):
            wp_self: str = self.api_base_url
            username_: str = self.username
            app_pass_: str = self.app_password
            basic_auth = aiohttp.BasicAuth(username_, app_pass_)
            headers_aiohttp = {"keep_alive": "true", "accept_encoding": "true"}
            wp_self: str = wp_self + "".join(params_req)
            async with semaphore:
                async with client_session.get(
                    wp_self, auth=basic_auth, headers=headers_aiohttp
                ) as resp:
                    resp_status = resp.status
                    if resp_status != 400:
                        resp_json = await resp.json()
                        for item in resp_json:
                            if item not in result_dict:
                                add_recent_posts(item)

        async def main():
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(30),
                connector=aiohttp.TCPConnector(
                    ssl_shutdown_timeout=10.0, force_close=True
                ),
                connector_owner=False,
            ) as session:
                tasks = [
                    get_recent_loop(client_semaphore, session, params)
                    for params in generate_params(x_wp_totalpages)
                ]
                await asyncio.gather(*tasks)

        asyncio.run(main())

        diff = x_wp_total - total_elems
        if diff != 0:
            add_list = list(recent_posts)[:diff]
            add_list.reverse()
            for recent in add_list:
                if isinstance(recent, dict):
                    result_dict.insert(0, recent)

        self.local_cache_config(self.cache_page_num, x_wp_total)
        return result_dict

    def local_cache_config(self, wp_curr_page: int, total_posts: int) -> None:
        """
        Creates or updates the local cache configuration file with metadata.

        :param wp_curr_page: ``int`` -> Last cached page number.
        :param total_posts: ``int`` -> Total number of posts.
        :return: ``None``
        """
        wp_cache_metadata_file = self.cache_metadata_file
        path_exists = os.path.exists(
            os.path.join(self.cache_dir, wp_cache_metadata_file)
        )
        create_new = [
            {
                self.cache_name: {
                    "cached_pages": wp_curr_page,
                    "total_posts": total_posts,
                    "last_updated": str(datetime.date.today()),
                }
            }
        ]
        if path_exists:
            existing_file = self.__cache_metadata
            for item in existing_file:
                item.update(
                    {
                        self.cache_name: {
                            "cached_pages": wp_curr_page,
                            "total_posts": total_posts,
                            "last_updated": str(datetime.date.today()),
                        }
                    }
                )
            create_new = existing_file

        self.__cache_metadata = create_new
        metadata_fields = self.__cache_metadata[0][self.cache_name]
        self.cached_pages: int = metadata_fields["cached_pages"]
        self.total_posts: int = metadata_fields["total_posts"]
        self.last_updated: str = metadata_fields["last_updated"]

        export_request_json(
            wp_cache_metadata_file, create_new, target_dir=self.cache_dir
        )
        return None

    def cache_sync(self) -> Optional[bool]:
        """
        Synchronizes the local cache with the WordPress site.

        :raises HotFileSyncIntegrityError: If validation fails.
        :return: ``Optional[bool]`` -> True if sync is successful, otherwise None.
        """
        sync_changes: List[Dict[str, Any]] = self.update_json_cache()
        # Reload config
        if len(sync_changes) == self.total_posts:
            export_request_json(
                self.cache_name, sync_changes, 1, target_dir=self.cache_dir
            )
            self.__cache_metadata = load_json_ctx(
                Path(self.cache_dir, self.cache_metadata_file)
            )
            self.cache_data = load_json_ctx(Path(self.cache_path))

            metadata_fields = self.__cache_metadata[0][self.cache_name]
            self.cached_pages: int = metadata_fields["cached_pages"]
            self.total_posts: int = metadata_fields["total_posts"]
            self.last_updated: str = metadata_fields["last_updated"]

            logging.info(f"Exporting new WordPress cache config: {self.cache_name}")
            logging.info("CacheSync Successful")
            return True
        else:
            logging.critical("CacheSync failed - Rebuilding local cache...")
            self.create_export_local_cache()
        return None

    def post_create(self, payload) -> int:
        """
        Creates a new post on the WordPress site via a POST request.

        :param payload: ``dict`` -> Dictionary containing post information.
        :return: ``int`` -> HTTP status code of the request.
        """
        wp_self, auth_wp = self.setup_basic_auth()
        wp_self: str = (
            wp_self + WPEndpoints.POSTS.value
            if not self.use_photo_cache
            else wp_self + WPEndpoints.PHOTOS.value
        )
        request_info = requests.post(wp_self, json=payload, auth=auth_wp)
        request_json = request_info.json()
        logging.info(f"Post upload result: {request_json}")
        if request_info.status_code != 201:
            logging.critical(
                f"Post upload failed with status code: {request_info.status_code} Reason: {request_info.reason}"
            )
            return request_info.status_code
        self.created_posts.append(
            WPost(
                post_id=request_json["id"],
                title=request_json["title"]["rendered"],
                slug=request_json["slug"],
                content=request_json["content"]["rendered"],
                ptype=request_json["type"],
                author=request_json["author"],
            )
        )
        return request_info.status_code

    def post_delete(self, post_id: int) -> int:
        """
        Deletes a post on the WordPress site via a DELETE request.

        :param post_id: ``int`` -> ID of the post to be deleted.
        :return: ``int`` -> HTTP status code of the request.
        """
        wp_self, auth_wp = self.setup_basic_auth()
        wp_self: str = wp_self + WPEndpoints.POSTS.value + "/" + str(post_id)
        request_info = requests.delete(wp_self, auth=auth_wp)
        return request_info.status_code

    def publish_post(self, post_id: int) -> int:
        """
        Publishes a post on the WordPress site via a POST request.

        :param post_id: ``int`` -> ID of the post to be published.
        :return: ``int`` -> HTTP status code of the request.
        """
        wp_self, auth_wp = self.setup_basic_auth()
        wp_self: str = wp_self + WPEndpoints.POSTS.value + "/" + str(post_id)
        payload = {"status": "publish"}
        request_info = requests.post(wp_self, auth=auth_wp, json=payload)
        return request_info.status_code

    def get_last_post(self) -> Optional[WPost]:
        """
        Returns the last post created on the WordPress site only once,
        then it will be removed from the instance.

        :return: ``WPost`` or ``None`` -> Last post created on the WordPress site.
        """
        try:
            return self.created_posts.pop()
        except IndexError:
            return None

    def tag_create(
        self,
        tag_name: str,
        tag_slug: str,
        description: Optional[str] = None,
        sync_on_add: bool = False,
    ) -> int:
        """
        Adds a new tag to the WordPress site via a POST request.

        :param tag_name: ``str`` -> Name of the new tag.
        :param tag_slug: ``str`` -> Slug for the new tag.
        :param description: ``Optional[str]`` -> Optional description for the tag.
        :param sync_on_add: ``bool`` -> If True, synchronizes the cache after adding.
        :return: ``int`` -> HTTP status code of the request.
        """
        payload_schema = {
            "name": tag_name,
            "slug": tag_slug,
        }
        if description:
            payload_schema["description"] = description
        wp_self, auth_wp = self.setup_basic_auth()
        wp_self: str = wp_self + WPEndpoints.TAGS.value
        status_code = requests.post(
            wp_self, json=payload_schema, auth=auth_wp
        ).status_code
        if status_code == 201 and sync_on_add:
            self.cache_sync()
        return status_code

    def post_polling(self, post_slug: str, retry_offset: int = 5) -> Optional[bool]:
        """Check for the publication a post in real time by using iteration of the Cache Sync
        algorithm. It will detect that you have effectively hit the publish button, so that functionality
        that directly depends on the post being online can take it from there.

        The function assigns environment variable ``"LATEST_POST"`` since objects
        present in this application do not usually work with fully qualified links because it is
        not necessary. This mechanism has also proven effective for manipulating pieces of information during runtime.

        :param post_slug: ``str`` -> self-explanatory
        :param retry_offset: ``int`` -> self-explanatory, defaults to 5
        :return: ``None`` | ``True``
        """
        retries = 0
        start_check = time.time()
        cache_sync = self.cache_sync()
        while cache_sync:
            slugs = self.get_slugs()
            if post_slug in slugs:
                os.environ["LATEST_POST"] = self.get_links()[slugs.index(post_slug)]
                end_check = time.time()
                h, mins, secs = get_duration(end_check - start_check)
                logging.info(
                    f"wordpress_post_polling took -> hours: {h} mins: {mins} secs: {secs} in {retries} retries"
                )
                return True

            time.sleep(retry_offset)

            if retry_offset != 0:
                retry_offset -= 1
            else:
                retry_offset = 5

            retries += 1
            # Safeguard mechanism
            try:
                cache_sync = self.cache_sync()
            except KeyboardInterrupt:
                while not cache_sync:
                    continue
                raise KeyboardInterrupt
        return None

    def upload_image(
        self,
        file_path: str | Path,
        payload: dict[str, str | int],
        return_source_url: bool = False,
    ) -> Union[int, str]:
        """
        Uploads an image as a WordPress media attachment.

        :param file_path: ``str | Path`` -> Path to the image file.
        :param payload: ``dict[str, str | int]`` -> Image attributes (ALT text, description, caption).
        :param return_source_url: ``str`` -> Source URL of the image
        :return: ``int`` -> HTTP status code of the request or ``source_url`` of the attachment file in the server
                    if ``return_source_url`` is set to True.
        """
        wp_self, auth_wp = self.setup_basic_auth()
        # headers = {"Content-Disposition": f"attachment; filename={file_path}"}
        wp_self: str = self.api_base_url + WPEndpoints.MEDIA.value
        with open(file_path, "rb") as thumb:
            request = requests.post(wp_self, files={"file": thumb}, auth=auth_wp)

        status_code = request.status_code
        logging.info(f"WordPress media upload status -> {status_code}")

        try:
            image_json = request.json()
        except JSONDecodeError:
            logging.exception("Failed to decode WordPress media response")
            return status_code

        media_id = image_json.get("id")
        if not media_id:
            logging.error("WordPress upload response missing 'id': %s", image_json)
            return status_code

        upload_request = requests.post(
            wp_self + "/" + str(image_json["id"]),
            json=payload,
            auth=auth_wp,
        )
        if upload_request in (requests.codes.ok, 201):
            return (
                image_json["source_url"]
                if return_source_url
                else upload_request.status_code
            )
        else:
            logging.error("Failed to attach metadata to media: %s", upload_request.text)
            return upload_request.status_code

    def get_tags_num_count(self) -> dict[int, int]:
        """
        Counts the occurrences of tag IDs in the cached posts.

        :return: ``dict[int, int]`` -> Mapping tag ID to occurrence count.
        """
        content = WPTaxonomyValues.TAGS
        tags_nums_count: dict = {}
        for dic in self.cache_data:
            for tag_num in dic[content.value]:
                if tag_num in tags_nums_count.keys():
                    tags_nums_count[tag_num] += 1
                else:
                    tags_nums_count[tag_num] = 1
        return tags_nums_count

    def get_slugs(self) -> list[str]:
        """
        Retrieves all slugs from the cached WordPress posts.

        :return: ``list[str]`` -> List of slugs/permalinks.
        """
        return [elem["slug"] for elem in self.cache_data]

    def get_links(self) -> list[str]:
        """
        Retrieves all post links from the cached WordPress posts.

        :return: ``list[str]`` -> List of post links.
        """
        return [elem["link"] for elem in self.cache_data]

    def map_wp_class_id(
        self, taxonomy_marker: WPTaxonomyMarker, taxonomy_values: WPTaxonomyValues
    ) -> dict[str, int]:
        """
        Maps keywords from the class_list to their numeric IDs.

        :param taxonomy_marker: ``WPTaxonomyMarker`` -> Enum value for the keyword prefix to match.
            A taxonomy marker is a prefix in the class_list (e.g., "tag", "category").
        :param taxonomy_values: ``WPTaxonomyValues`` -> Enum value for the key containing numeric IDs.
            A taxonomy value list is a key in the post dict (e.g., "tags", "categories").
        :return: ``dict[str, int]`` -> Mapping keyword to numeric ID.

        Output sample:
            ``{"Python": 12, "Tutorial": 34}``
        """
        result_dict = {}
        for elem in self.cache_data:
            kw = [
                " ".join(item.split("-")[1:]).title()
                for item in elem["class_list"]
                if re.findall(taxonomy_marker.value, item)
            ]
            model_ids = elem[taxonomy_values.value]
            for item in zip(kw, model_ids):
                (name, wp_id) = item
                if name not in result_dict.keys():
                    result_dict[name] = wp_id
                else:
                    continue
        return result_dict

    def get_from_class_list(
        self, taxonomy_marker: WPTaxonomyMarker, unique_str: bool = False
    ) -> list[str]:
        """
        Gets keywords from a post dictionary that WordPress prefixes with a specific pattern.

        Output sample:
            ``["Python", "Tutorial", "Beginner"]``

        Note:
            If unique_str is True, only unique keywords are returned.

        :param taxonomy_marker: ``WPTaxonomyMarker`` -> Enum class with taxonomy marker values.
            Used to match prefixes in the class_list (e.g., "tag", "category").
        :param unique_str: ``bool`` -> Return unique results.
        :return: ``list[str]`` -> Cleaned keywords.
        """
        double_join = lambda tag: "".join(" ".join(tag).title())  # noqa: E731
        class_list = [
            [
                double_join(cls_lst.split("-")[1:])
                for cls_lst in elem["class_list"]
                if re.match(taxonomy_marker.value, cls_lst)
                if cls_lst is not None
            ]
            for elem in self.cache_data
        ]

        taxonomy_lst = [
            taxonomy if len(item) != 0 else None
            for item in class_list
            for taxonomy in item
        ]
        return (
            taxonomy_lst
            if not unique_str
            else list({taxonomy for taxonomy in taxonomy_lst})
        )

    def get_class_list_id_groups(
        self, taxonomy_marker: WPTaxonomyMarker, tags_key: bool = False
    ) -> dict[str, list[str | int]] | list[dict[str | int, str]]:
        """
        Gets keywords from a post dictionary that WordPress prefixes with a specific pattern.
        Output: ``{post_id: [tag_list]}`` or if ``tag_key`` is ``True``, then ``{tag: [post_id_list]}``

        Output sample (``tags_key=False``):
            ``[{123: ["Python", "Tutorial"]}, {124: ["Beginner"]}]``
        Output sample (``tags_key=True``):
            ``{"Python": [123], "Tutorial": [123], "Beginner": [124]}``

        Note:
            This function can invert the mapping depending on ``tags_key``.

        :param taxonomy_marker: ``WPTaxonomyMarker`` -> Enum class with taxonomy marker values.
            Used to match prefixes in the class_list (e.g., "tag", "category").
        :param tags_key: ``bool`` -> If True, returns a dictionary with the keyword as key and list of ids as value.
        :return: ``dict[str, list[str | int]] | list[dict[str | int, str]]`` -> Grouping keywords and IDs.
        """
        double_join = lambda tag: "".join(" ".join(tag).title())  # noqa: E731
        class_list = [
            {
                elem["id"]: [
                    double_join(cls_lst.split("-")[1:])
                    for cls_lst in elem["class_list"]
                    if re.match(taxonomy_marker.value, cls_lst)
                ]
            }
            for elem in self.cache_data
        ]

        if tags_key:
            tags_site = self.get_tag_count().keys()
            class_list_dict = {kw: [] for kw in tags_site}
            for post in class_list:
                for id_, cls_list in post.items():
                    for cls in cls_list:
                        if cls in class_list_dict.keys():
                            class_list_dict[cls].append(id_)
            class_list = class_list_dict
        return class_list

    def tag_id_merger_dict(self) -> dict[str, int]:
        """
        Returns a dictionary mapping tag names to their IDs.

        Output sample:
            ``{"Python": 12, "Tutorial": 34}``

        :return: ``dict[str, int]`` -> Mapping tag name to tag ID.
        """
        return {
            tag: t_id
            for tag, t_id in zip(
                self.get_tag_count().keys(), self.get_tags_num_count().keys()
            )
        }

    def get_tag_count(self, yoast_support: bool = False) -> dict[str, int]:
        """
        Counts every occurrence of a tag in the entire posts json file.

        Output sample:
            ``{"Python": 5, "Tutorial": 2}``

        Note:
            If yoast_support is True, this uses the Yoast SEO plugin's keywords.
            If the Yoast SEO plugin is not installed or data is missing, a :exc:`core.utils.custom_exceptions.YoastSEOUnsupported` exception is raised.

        :param yoast_support: ``bool`` -> Enable Yoast SEO support for parsing.
        :return: ``dict[str, int]`` -> Mapping tag name to count.
        :raises core.utils.custom_exceptions.YoastSEOUnsupported: If Yoast SEO data is missing.
        """
        tags_count: dict = {}
        if yoast_support:
            for dic in self.cache_data:
                if dic["yoast_head_json"]["schema"]["@graph"][0]["keywords"]:
                    for kw in dic["yoast_head_json"]["schema"]["@graph"][0]["keywords"]:
                        if kw in tags_count.keys():
                            tags_count[kw] = tags_count[kw] + 1
                        else:
                            tags_count[kw] = 1
                else:
                    raise YoastSEOUnsupported
        else:
            tags_count = self.count_wp_class_id(WPTaxonomyMarker.TAG)
        return tags_count

    def tag_id_count_merger(self) -> list:
        """
        Returns a list of NamedTuples with tag title, ID, and count.

        Output sample:
            ``[WP_Tags(title='Python', ID=12, count=5), WP_Tags(title='Tutorial', ID=34, count=2)]``

        :return: ``list`` -> List of NamedTuples (title, ID, count).
        """
        tag_count: dict = self.get_tag_count()
        tag_id_merger = zip(
            tag_count.keys(),
            self.get_tags_num_count().keys(),
            tag_count.values(),
        )
        Tag_ID_Count = namedtuple("WP_Tags", ["title", "ID", "count"])
        result = [
            Tag_ID_Count(title, ids, count) for title, ids, count in tag_id_merger
        ]
        return result

    def get_tag_id_pairs(
        self, yoast_support: bool = False
    ) -> dict[str, list[str | int]]:
        """
        Creates a dictionary mapping tag names to lists of post IDs.

        Output sample:
            ``{"Python": [123, 124], "Tutorial": [123]}``

        Note:
            If yoast_support is True, this uses the Yoast SEO plugin's keywords.

        :param yoast_support: ``bool`` -> Enable Yoast SEO support for parsing.
        :return: ``dict[str, list[str | int]]`` -> Mapping tag name to list of post IDs.
        """
        unique_tags = self.get_tag_count(yoast_support=yoast_support).keys()
        tags_c: dict[str, list[str | int]] = {kw: [] for kw in unique_tags}
        if yoast_support:
            for dic in self.cache_data:
                for kw in unique_tags:
                    if kw in dic["yoast_head_json"]["schema"]["@graph"][0]["keywords"]:
                        tags_c[kw].append(dic["id"])
        else:
            tags_c = self.get_class_list_id_groups(WPTaxonomyMarker.TAG, tags_key=True)
        return tags_c

    def get_post_titles_local(self, yoast_support: bool = False) -> list[str]:
        """
        Gets a list of all post titles from the cache.

        :param yoast_support: ``bool`` -> Enable Yoast SEO support for parsing.
        :return: ``list[str]`` -> List of post titles.
        """
        all_titles = []
        for post in self.cache_data:
            if yoast_support:
                all_titles.append(
                    " ".join(post["yoast_head_json"]["title"].split(" ")[:-2]).strip()
                )
            else:
                all_titles.append(post["title"]["rendered"].strip())
        return all_titles

    def map_posts_by_id(self, include_host_name: bool = False) -> dict[str, int]:
        """
        Maps post ID to a slug or URL.

        :param include_host_name: ``bool`` -> If True, includes the hostname in the URL.
        :return: ``dict[str, str]`` -> Mapping post ID to slug or URL.
        """
        wp_cache_data = self.cache_data
        u_pack = zip(
            [idd["id"] for idd in wp_cache_data], [url["slug"] for url in wp_cache_data]
        )
        if include_host_name:
            return {idd: f"{self.fq_domain_name}/" + url for idd, url in u_pack}
        else:
            return {idd: url for idd, url in u_pack}

    def map_tags_post_urls(
        self, include_host_name: bool = False
    ) -> dict[str, list[str]]:
        """
        Creates a dictionary mapping tag names to lists of post slugs or URLs.

        :param include_host_name: ``bool`` -> If True, includes the hostname in the URLs.
        :return: ``dict[str, list[str]]`` -> Mapping tag name to list of slugs or URLs.
        """
        mapped_ids = self.map_posts_by_id(include_host_name=include_host_name)
        unique_tags = self.get_tag_count().keys()
        tags_c = {kw: [] for kw in unique_tags}
        clean_kw = lambda tag: " ".join(tag.split("-")[1:]).title()  # noqa: E731
        for dic in self.cache_data:
            for kw in dic["class_list"]:
                if (kw := clean_kw(kw)) in tags_c.keys():
                    tags_c[kw].append(mapped_ids[dic["id"]])
        return tags_c

    def map_tags_posts(
        self,
        taxonomy_marker: WPTaxonomyMarker,
        include_host_name: bool = False,
        idd: bool = None,
        yoast_support: bool = False,
    ) -> dict[str, list[str]]:
        """
        Creates a dictionary mapping tag names to lists of post slugs or IDs.

        Output sample (``idd=False``):
            ``{"Python": ["python-intro", "python-advanced"], "Tutorial": ["tutorial-1"]}``
        Output sample (``idd=True``):
            ``{"Python": [123, 124], "Tutorial": [123]}``

        Note:
            If yoast_support is True, this uses the Yoast SEO plugin's keywords.

        :param taxonomy_marker: ``WPTaxonomyMarker`` -> Taxonomy that you want to match with the Tag key.
            Used to match prefixes in the class_list (e.g., "tag", "category").
        :param include_host_name: ``bool`` -> If True, includes the hostname in the URLs.
        :param idd: ``bool | None`` -> If True, returns post IDs instead of slugs.
        :param yoast_support: ``bool`` -> Enable Yoast SEO support for parsing.
        :return: ``dict[str, list[str]]`` -> Mapping tag name to list of slugs or IDs.
        """
        mapped_ids: dict = self.map_posts_by_id(include_host_name=include_host_name)
        unique_tags = self.get_tag_count(yoast_support=yoast_support).keys()
        tags_c: dict = {kw: [] for kw in unique_tags}
        if yoast_support:
            for dic in self.cache_data:
                for kw in dic["yoast_head_json"]["schema"]["@graph"][0]["keywords"]:
                    if kw in tags_c.keys():
                        if idd is True:
                            tags_c[kw].append(dic["id"])
                        else:
                            tags_c[kw].append(mapped_ids[dic["id"]])
        else:
            class_list = self.get_class_list_id_groups(taxonomy_marker, tags_key=True)
            for tag, post_ids in class_list.items():
                for post_id in post_ids:
                    for post in self.cache_data:
                        if post["id"] == post_id:
                            if idd:
                                append_val = post["id"]
                            else:
                                append_val = post["slug"]

                            if tag.title() in tags_c.keys():
                                tags_c[tag.title()].append(append_val)
        return tags_c

    def map_post_id_slug(
        self,
        include_host_name: bool = False,
        yoast_support: bool = False,
    ) -> dict[str, str]:
        """
        Associates post ID with a slug or URL.

        :param include_host_name: ``bool`` -> If True, includes the hostname in the URLs.
        :param yoast_support: ``bool`` -> Enable Yoast SEO support for parsing.
        :return: ``dict[str, str]`` -> Mapping post ID to slug or URL.
        """
        # In the case of KeyError, there is at least one post that hasn't been categorized in WordPress.
        # Check the culprit with the following code if this behaviour is not intended.
        id_list = [id_post["id"] for id_post in self.cache_data]
        if yoast_support:
            post_pack = zip(
                id_list,
                [
                    post["yoast_head_json"]["schema"]["@graph"][1]["url"].split("/")[-2]
                    if not include_host_name
                    else post["yoast_head_json"]["schema"]["@graph"][1]["url"]
                    for post in self.cache_data
                ],
            )
        else:
            post_pack = zip(
                id_list,
                [post["slug"] for post in self.cache_data],
            )

        if include_host_name and not yoast_support:
            return {idd: f"{self.fq_domain_name}/" + url for idd, url in post_pack}
        else:
            return {idd: cat for idd, cat in post_pack}

    def get_post_categories(self) -> list[str]:
        """
        Retrieves the category for each post from the cached data.

        :return: ``list[str]`` -> List of categories.
        """
        categories = self.get_from_class_list(WPTaxonomyMarker.CATEGORY)
        return categories

    def get_post_descriptions(self, yoast_support: bool = False) -> list[str]:
        """
        Extracts post descriptions (excerpts) from the cached data.

        :param yoast_support: ``bool`` -> Enable Yoast SEO support for parsing.
        :return: ``list[str]`` -> List of post descriptions.
        """
        wp_cached_data = self.cache_data
        if yoast_support:
            return [item["yoast_head_json"]["description"] for item in wp_cached_data]
        else:
            return [
                item["excerpt"]["rendered"].strip("\n").strip("<p>").strip("</p>")
                for item in wp_cached_data
            ]

    def map_wp_class_id_many(
        self,
        match_taxonomy_marker: WPTaxonomyMarker,
        compare_taxonomy_marker: WPTaxonomyMarker,
    ) -> dict[str, set[str]]:
        """
        Combine two keys in the class-list key.

        Output sample:
            ``{"Beginner": {"Python", "Tutorial"}, "Advanced": {"Python"}}``

        Note:
            This function creates a mapping between two different taxonomy markers.

        :param match_taxonomy_marker: ``WPTaxonomyMarker`` -> Taxonomy you want to match.
            Used to match prefixes in the class_list (e.g., "tag", "category").
        :param compare_taxonomy_marker: ``WPTaxonomyMarker`` -> Taxonomy you want to map to match_taxonomy_marker matches.
            Used to match another prefix in the class_list.
        :return: ``dict[str, set[str]]`` -> Mapping taxonomy to set of matched values.
        """
        result_dict = {}
        for elem in self.cache_data:
            kw = [
                " ".join(item.split("-")[1:]).title()
                for item in elem["class_list"]
                if re.findall(match_taxonomy_marker.value, item)
            ]

            d_kw = [
                " ".join(item.split("-")[1:]).title()
                for item in elem["class_list"]
                if re.findall(compare_taxonomy_marker.value, item)
            ]

            for item in d_kw:
                if item not in result_dict.keys():
                    result_dict[item] = set(kw)
                else:
                    result_dict[item].union(kw)
        return result_dict

    def count_wp_class_id(self, taxonomy_marker: WPTaxonomyMarker) -> dict[str, int]:
        """
        Parses the cache to locate and count tags or other keywords in the class_list key.

         Output sample:
            ``{"Python": 5, "Tutorial": 2}``

        :param taxonomy_marker: ``WPTaxonomyMarker`` -> Taxonomy you want to match.
            Used to match prefixes in the class_list (e.g., "tag", "category").
        :return: ``dict[str, int]`` -> Mapping taxonomy to count.
        """
        result_dict = {}
        for elem in self.cache_data:
            kw = [
                " ".join(item.split("-")[1:]).title()
                for item in elem["class_list"]
                if re.findall(taxonomy_marker.value, item)
            ]
            for item in kw:
                if item not in result_dict.keys():
                    result_dict[item] = 1
                else:
                    result_dict[item] += 1
        return result_dict

    def count_map_match_taxonomy(
        self,
        match_taxonomy: WPTaxonomyMarker,
        track_taxonomy: WPTaxonomyMarker,
        hint_list: list[str],
    ) -> dict[str, tuple[tuple[int | str]]]:
        """
        This function parses the WordPress cache to locate and count tags or other
        keywords that WordPress includes in the ``['class_list']`` key, here defined as taxonomy markers.
        In case there is a relationship between taxonomy markers, the function takes a tracking word
        (any pattern that is associated with ``match_taxonomy``) to return a tuple with a count of the latter and the flag that
        realise the relationship with ``track_taxonomy`` by using a list of hints (``hint_list``).

        The problem that sustains the existence of this function resides in the need to map the models, video count and partner.
        Both model and partner (elements in the ``['class_list']`` key) are related and; therefore, such connection
        is realised by a list of hints that make sorting and matching easier.

        This function is based on ``map_wp_class_id`` and implements its basic idea (taxonomy marker vs taxonomy value).
        for more information about mechanism of matching, see the docstring for ``map_wp_class_id``

        :param wp_posts_f: list[dict] (wp_posts or wp_photos) previously loaded in the program.
        :param match_word: ``str`` prefix of the keywords that you want to match.
        :param track_match_wrd: ``str`` pattern that will be matched and has a relationship with ``match_word``
        :param hint_list: ``list[str]`` Matching hints that are related to ``track_match_wrd``
        :return: ``dict[str, tuple[int, str]`` {'keyword': (count: int, matching_track_taxonomy: str)}
        """
        result_dict = {}
        for elem in self.cache_data:
            kw = [
                " ".join(item.split("-")[1:]).title()
                for item in elem["class_list"]
                if re.findall(match_taxonomy.value, item)
            ]

            track_kw = [
                " ".join(item.split("-")[1:]).title()
                for item in elem["class_list"]
                if re.findall(track_taxonomy.value, item)
            ]

            post_id = elem["id"]
            for item in kw:
                if item not in result_dict.keys():
                    match = [
                        hint for hint in hint_list if match_list_single(hint, track_kw)
                    ]
                    tr_kw = match[0] if match else False

                    if tr_kw:
                        result_dict[item] = [(1, tr_kw), post_id]
                    else:
                        result_dict[item] = [(1, "AdultNext/TubeCorporate"), post_id]
                else:
                    result_dict[item][0] = (
                        result_dict[item][0][0] + 1,
                        result_dict[item][0][1],
                    )
                    result_dict[item].append(post_id)
        # Packing into tuples makes it easier to process for reporting purposes.
        return {r: tuple(vals) for r, vals in result_dict.items()}

    def map_postsid_category(self, host_name: bool = False) -> dict[str, str]:
        """
        Associates post ``ID`` with a URL. As many functions, it assumes that your *WordPress* installation has
        the *Yoast SEO* plug-in in place.

        :param wp_posts_f: ``list[dict]`` Posts ``JSON``
        :param host_name: ``bool`` add your hostname to the URL in the result list. Default ``False``
        :return: ``dict[str, str]``
        """
        # In the case of KeyError, there is at least one post that hasn't been categorized in WordPress.
        # Check the culprit with the following code if this behaviour is not intended:
        # for url in imported_json:
        #   try:
        #      print(url['yoast_head_json']['schema']['@graph'][0]['articleSection'])
        #   except KeyError:
        #      pprint.pprint(url)

        u_pack = zip(
            [idd["id"] for idd in self.cache_data],
            [
                url["yoast_head_json"]["schema"]["@graph"][0]["articleSection"]
                for url in self.cache_data
            ],
        )
        if host_name is not None:
            return {idd: f"{self.fq_domain_name}/" + url for idd, url in u_pack}
        else:
            return {idd: cat for idd, cat in u_pack}

    def get_post_models(self) -> list[str]:
        """This function is based on the same principle as ``get unique tags``, however, this is a
            domain specific implementation that is no longer in operation and has been replaced by function
            ``get_from_class_list`` and used by reporting modules.

        :param wp_posts_f: ``list[dict]``
        :return: ``list[str]`` of model items joined by a comma individually.
                 This behaviour is desired because some videos have more than one model item associated with it,
                 making it easier for other functions to process these individually and find unique occurrences.
        """
        models = [
            [
                " ".join(cls_lst.split("-")[1:]).title()
                for cls_lst in elem["class_list"]
                if re.match("pornstars", cls_lst)
            ]
            for elem in self.cache_data
        ]
        return [",".join(model) if len(model) != 0 else None for model in models]

    def get_post_category(self) -> Optional[list[str]]:
        """It assumes that each post has only one category, so that's why I am not joining
        them with commas within the return list comprehension.
        This is a domain specific implementation for categories.
        If you have more than one category, you can use the ``get_from_class_list`` with ``'category'``
        as the taxonomy marker.

        :param wp_posts_f: ``list[dict]``
        :return: ``list[str]``
        """
        categories = [
            [
                " ".join(cls_lst.split("-")[1:]).title()
                for cls_lst in elem["class_list"]
                if re.match("category", cls_lst)
            ]
            for elem in self.cache_data
        ]
        try:
            return [category[0] for category in categories]
        except IndexError:
            warnings.warn(
                "WordPress API detected uncategorized posts in the cache. It is recommended that you locate, categorize them and rebuild your cache in case of issues"
            )
            return None


if __name__ == "__main__":
    # This file is not meant to be run directly yet.
    # It is a module that is imported by other modules.
    raise RuntimeError(
        "This file is not meant to be run directly yet. It is a module that is imported by other modules."
    )
