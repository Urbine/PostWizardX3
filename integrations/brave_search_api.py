"""
Brave Search API wrapper

This module provides a wrapper for the Brave Search API.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import argparse
import datetime
import re

import urllib3

from dataclasses import dataclass, asdict
from typing import Any, Optional
from urllib3 import BaseHTTPResponse

# Local implementations
import core
import core.utils.file_system
import core.utils.strings
from integrations.exceptions.integration_exceptions import (
    BraveAPIValidationError,
    BraveAPIInvalidCountryCode,
    BraveAPIInvalidLanguageCode,
)

from core.utils.secret_handler import SecretHandler
from core.models.secret_model import SecretType


class BraveSearchAPI:
    """
    Brave Search API Wrapper class.
    """

    @dataclass(frozen=True)
    class Mode:
        """
        Immutable dataclass containing vertical mode information for URL construction.
        """

        web: str = "web"
        images: str = "images"
        videos: str = "videos"

    @dataclass(frozen=True)
    class Endpoint:
        """
        Immutable dataclass containing possible endpoints for URL construction.
        Endpoints usually go after the vertical.
        """

        search: str = "search?"

    @dataclass(frozen=True)
    class QParams:
        """
        Immutable dataclass with possible query parameters for URL construction.
        If no query parameters are passed then the api will assume a series of default values.

        Query parameters also have maximum values that must be respected if you want to avoid a validation
        error response from the API.

        1. ``count``: the maximum value of count depends on the mode selected by the user. For example,
        for ``web`` is ``20`` (defaults to maximum), ``images`` allows for ``100`` (defaults to ``50``)
        and ``videos`` accept up to ``50`` elements (defaults to ``20``)

        2. ``offset``: Global maximum of ``9``, defaults to ``0`` which is the first page of results.
        ``offset`` is usually used with ``count`` to retrieve a specific page. Elements may overlap.

        3. ``country`` and ``search_lang``: Default to ``US`` and ``en``, respectively.
        Find the country codes and language codes here: `Country Codes <https://api-dashboard.search.brave.com/app/documentation/video-search/codes#country-codes>`_
        and `Language Codes <https://api-dashboard.search.brave.com/app/documentation/video-search/codes#language-codes>`_

        4. ``query``: "Query can not be empty. Maximum of 400 characters and 50 words in the query."

        5. ``safesearch``: Supports the following - ``off``, ``moderate`` and ``strict``

        6. ``spellcheck``: "Whether to spellcheck provided query.
        If the spellchecker is enabled, the modified query is always used for search.
        The modified query can be found in altered key from the query response model."
        This wrapper provides methods to get ``original`` and ``altered`` queries.

        Text passages in quotation marks are excerpts from the online documentation.
        """

        count: str = "count="
        offset: str = "offset="
        country: str = "country="
        query: str = "q="
        search_lang: str = "search_lang="
        ui_lang: str = "ui_lang="
        spellcheck: str = "spellcheck="
        safesearch: str = "safesearch="

    @dataclass(frozen=True, kw_only=True)
    class WebSERP:
        """
        Immutable class designed as a record for web search engine results.
        """

        title: Optional[str]
        description: Optional[str]
        url: Optional[str]
        hostname: Optional[str]
        age: Optional[str]

    @dataclass(frozen=True, kw_only=True)
    class ImageSERP(WebSERP):
        """
        Immutable class designed as a record for image search results.
        """

        property_url: str
        image_confidence: str
        image_source: str

    @dataclass(frozen=True, kw_only=True)
    class VideoSERP(WebSERP):
        """
        Immutable class designed as a record for video search results.
        """

        thumbnail_url: str
        video_views: str
        video_publisher: str

    def __init__(
        self,
        http: urllib3.PoolManager,
        web: bool = False,
        images: bool = False,
        videos: bool = False,
        count: Optional[int] = None,
        offset: Optional[int] = None,
        safesearch: Optional[str] = None,
        country: Optional[str] = None,
        search_lang: Optional[str] = None,
        ui_lang: Optional[str] = None,
        spellcheck: Optional[bool] = False,
    ) -> None:
        """
        Brave Search API URL constructor. For a detailed overview of parameters, flags and defaults this constructor
        takes in, got to the ``QParams`` dataclass docstring. Defaults to the Web Search vertical.
        Boolean parameters here default to ``False``

        :param http: ``http: urllib3.PoolManager`` - External PoolManager for continuous requests and resource efficiency.
        :param web: ``bool`` - Web Search vertical flag
        :param images: ``bool`` - Image Search vertical flag
        :param videos: ``bool`` - Video Search vertical flag
        :param count:        ``int`` | ``None`` - Result count
        :param offset:       ``int`` | ``None`` - SERP Offset
        :param safesearch:   ``str`` | ``None`` - Safe Search filtering string
        :param country:      ``str`` | ``None`` - Country Code
        :param search_lang:  ``str`` | ``None`` - Language Code
        :param ui_lang:      ``str`` | ``None`` - Market or UI language code
        :param spellcheck:   ``bool`` - Query spellcheck flag
        """
        self.__base_url = "https://api.search.brave.com/res/v1"
        self.endpoint: str = self.Endpoint.search
        self.http = http
        self.__api_key = SecretHandler().get_secret(SecretType.BRAVE_API_KEY)[0].api_key

        if web:
            self.mode: str = self.Mode.web
        elif images:
            self.mode: str = self.Mode.images
        elif videos:
            self.mode: str = self.Mode.videos
        else:
            # Default option
            self.mode: str = self.Mode.web

        if self.mode == self.Mode.images and offset:
            # Image vertical can't take offsets.
            offset = None

        if country:
            country = country.strip().lower()
            if len(country) != 2 and country != "all":
                raise BraveAPIInvalidCountryCode
        elif search_lang:
            search_lang = search_lang.strip().lower()
            if len(search_lang) != 2 and not re.findall("-", search_lang):
                raise BraveAPIInvalidLanguageCode
        elif ui_lang:
            # ui_lang is indeed case-sensitive.
            ui_lang = ui_lang.strip()
            if re.findall("-", ui_lang):
                raise BraveAPIInvalidLanguageCode

        fields = self.QParams.__dict__
        self.fields = [fields[f] for f in fields.keys() if f in locals().keys()]
        prep_params = {
            key: val for key, val in locals().items() if key in fields.keys()
        }
        self.qparams = (
            f"&{'&'.join(fields_lst)}"
            if (
                fields_lst := [
                    f"{fields[key]}{val}"
                    for key, val in prep_params.items()
                    if val is not None
                ]
            )
            else ""
        )
        self.__url = f"{self.__base_url}/{self.mode}/{self.endpoint}"
        self.request: Optional[BaseHTTPResponse] = None

    @property
    def api_base(self) -> str:
        """
        Brave API Base URL property getter.

        :return: ``str``
        """
        return self.__base_url

    @property
    def api_url(self) -> str:
        """
        Brave API Constructed URL property getter.

        :return: ``str``
        """
        return self.__url

    def __key_protect(
        self, dic: dict[str, Any], keys: tuple[str, str] | str
    ) -> Optional[Any]:
        """
        Helper functions that facilitates error handling in iterations using
        lambda expressions. Lambdas in this class access a maximum of two keys.

        :param dic: ``dict[str, Any]``
        :param key: ``tuple[str, str]`` | ``str``
        :return: ``Optional[Any]``
        """
        try:
            if isinstance(keys, str):
                return dic[keys]
            else:
                return dic[keys[0]][keys[1]]
        except KeyError:
            return None

    def send_query(self, query: str, raw_query: bool = False) -> BaseHTTPResponse:
        """
        Send Search query to Brave. Depending on the vertical you selected in object construction,
        results and fields may vary. Results have some elements present in all verticals and most methods
        in this class work with any SERP result.

        :param query: ``str`` provide any string as a search query.
        :param raw_query: ``bool`` - ``raw`` mode flag. Passes an unaltered string to the query parameter.
        :return: ``BaseHTTPResponse``
        """
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.__api_key,
        }

        if not raw_query:
            query_prep = "+".join(query.split()) if re.findall(" ", query) else query
        else:
            query_prep = query

        self.request = self.http.request(
            "GET",
            self.__url + self.QParams.query + query_prep + self.qparams,
            headers=headers,
        )
        return self.request

    def get_json(self) -> Optional[dict[str, Any]]:
        """
        Enables error handling in case there is no BaseHTTPResponse in the ``self.request`` field.
        :return: ``Optional[dict[str, Any]]``
        """
        try:
            request_json = self.request.json()
            if "error" in request_json.keys():
                if request_json["error"]["code"] == "VALIDATION":
                    raise BraveAPIValidationError
            else:
                return request_json
        except AttributeError:
            return self.request

    def get_original_query(self) -> str:
        """
        Get the original query passed on to Brave for debugging purposes.
        This is helpful in case you need to see what Brave received and if it aligns with what you want.

        :return: ``str``
        """
        return self.get_json()["query"]["original"]

    def get_altered_query(self) -> Optional[str]:
        """
        Get the altered query in case that Brave applied spellchecking.
        Note that ``spellchecker`` must be enabled if you use this method; otherwise it just returns none.

        :return: Optional[str]
        """
        return self.__key_protect(self.get_json(), ("query", "altered"))

    def more_results_available(self) -> bool:
        """
        Check if there are more results available. Useful if you want to work with page offsets.

        :return: ``bool``
        """
        return self.__key_protect(self.get_json(), ("query", "more_results_available"))

    def is_navigational(self) -> Optional[bool]:
        """
        Identifies whether the user-provided query is navigational.

        :return: ``bool``
        """
        return self.__key_protect(self.get_json(), ("query", "is_navigational"))

    def is_news_breaking(self) -> Optional[bool]:
        """
        Identifies whether the user-provided query has breaking news articles related to it.

        :return: ``bool``
        """
        return self.__key_protect(self.get_json(), ("query", "is_news_breaking"))

    def get_country(self) -> Optional[str]:
        """
        Get country text from the current search result set.

        :return: ``Optional[str]``
        """
        return self.__key_protect(self.get_json(), ("query", "country"))

    def get_city(self) -> Optional[str]:
        """
        Get city text from the current search result set.

        :return: ``Optional[str]``
        """
        return self.__key_protect(self.get_json(), ("query", "city"))

    def __get_collection(self) -> Optional[dict[str, Any]]:
        """
        Internal helper method which allows for "vertical awareness" in result set getter methods.
        In other words, it identifies where to look for overlapping values and returns the correct collection
        to avoid exceptions and improve usability.

        :return: ``Optional[dict[str, Any]]``
        """
        result_json = self.get_json()
        if result_json:
            if self.mode == self.Mode.web:
                return result_json["web"]["results"]
            else:
                return result_json["results"]
        else:
            return self.request

    def get_search_titles(self) -> Optional[list[str]]:
        """
        Get title tag text from the current search result set.

        :return: ``Optional[list[str]]``
        """
        if collection := self.__get_collection():
            return list(
                map(lambda entry: self.__key_protect(entry, "title"), collection)
            )
        else:
            return self.request

    def get_search_descriptions(self) -> Optional[list[str]]:
        """
        Get meta description text from the current search result set.

        :return: ``Optional[list[str]]``
        """
        if collection := self.__get_collection():
            return list(
                map(lambda entry: self.__key_protect(entry, "description"), collection)
            )
        else:
            return self.request

    def get_search_breadcrumbs(self) -> Optional[list[str]]:
        """
        Get breadcrumbs text from the current search result set.

        :return: ``Optional[list[str]]``
        """
        if collection := self.__get_collection():
            return list(
                map(
                    lambda entry: self.__key_protect(entry, ("meta_url", "path")),
                    collection,
                )
            )
        else:
            return self.request

    def get_search_urls(self) -> Optional[list[str]]:
        """
        Get results URL from the current search result set.

        :return: ``Optional[list[str]]``
        """
        if collection := self.__get_collection():
            return list(map(lambda entry: self.__key_protect(entry, "url"), collection))
        else:
            return self.request

    def get_search_hostname(self):
        """
        Get hostname text from the current search result set.

        :return: ``Optional[list[str]]``
        """
        if collection := self.__get_collection():
            return list(
                map(
                    lambda entry: self.__key_protect(entry, ("meta_url", "hostname")),
                    collection,
                )
            )
        else:
            return self.request

    def get_result_age(self) -> Optional[list[str]]:
        """
        Get ages text from the current search result set.

        :return: ``Optional[list[str]]``
        """
        if collection := self.__get_collection():
            return list(map(lambda entry: self.__key_protect(entry, "age"), collection))
        else:
            return self.request

    def get_image_age(self):
        """
        Get ``page_fetched`` text from the current search result set.

        :return: ``Optional[list[str]]``
        """
        if collection := self.__get_collection():
            try:
                return list(
                    map(
                        lambda entry: self.__key_protect(entry, "page_fetched"),
                        collection,
                    )
                )
            except KeyError:
                return None
        else:
            return self.request

    def get_image_property_url(self) -> Optional[list[str]]:
        """Get the image source URL for permalink analysis.

        :return: ``Optional[list[str]]``
        """
        if collection := self.__get_collection():
            try:
                return list(
                    map(
                        lambda entry: self.__key_protect(entry, ("properties", "url")),
                        collection,
                    )
                )
            except KeyError:
                return None
        else:
            return self.request

    def get_image_confidence(self) -> Optional[list[str]]:
        """
        Get Brave confidence level marker from the current search result set.

        :return: ``Optional[list[str]]``
        """
        if collection := self.__get_collection():
            try:
                return list(
                    map(
                        lambda entry: self.__key_protect(entry, "confidence"),
                        collection,
                    )
                )
            except KeyError:
                return None
        else:
            return self.request

    def get_image_source(self) -> Optional[list[str]]:
        """
        Get image original link from the current search result set.

        :return: ``Optional[list[str]]``
        """
        if collection := self.__get_collection():
            try:
                return list(
                    map(lambda entry: self.__key_protect(entry, "source"), collection)
                )
            except KeyError:
                return None
        else:
            return self.request

    def get_video_thumbnail_url(self) -> Optional[list[str]]:
        """
        Get image source thumbnail from the current search result set.

        :return: ``Optional[list[str]]``
        """
        if collection := self.__get_collection():
            try:
                return list(
                    map(
                        lambda entry: self.__key_protect(
                            entry, ("thumbnail", "original")
                        ),
                        collection,
                    )
                )
            except KeyError:
                return None
        else:
            return self.request

    def get_video_views(self) -> Optional[list[str]]:
        """
        Get view count of videos from the current search result set, if available.

        :return: ``Optional[list[str]]``
        """
        if collection := self.__get_collection():
            try:
                return list(
                    map(
                        lambda entry: self.__key_protect(entry, ("video", "views")),
                        collection,
                    )
                )
            except KeyError:
                return None
        else:
            return self.request

    def get_video_publisher(self) -> Optional[list[str]]:
        """
        Get video publisher from the current search result set, if available.

        :return: ``Optional[list[str]]``
        """
        if collection := self.__get_collection():
            try:
                return list(
                    map(
                        lambda entry: self.__key_protect(entry, ("video", "publisher")),
                        collection,
                    )
                )
            except KeyError:
                return None
        else:
            return self.request

    def webserp_factory_collect(
        self, as_dict: bool = False
    ) -> Optional[list[WebSERP] | dict[str, Any]]:
        if self.mode != self.Mode.web:
            return None
        else:
            titles = self.get_search_titles()
            descriptions = self.get_search_descriptions()
            urls = self.get_search_urls()
            hostnames = self.get_search_hostname()
            age = self.get_result_age()
            aggregate = zip(titles, descriptions, urls, hostnames, age)
            if as_dict:
                return [
                    asdict(
                        self.WebSERP(title=t, description=d, url=u, hostname=h, age=a)
                    )
                    for t, d, u, h, a in aggregate
                ]
            else:
                return [
                    self.WebSERP(title=t, description=d, url=u, hostname=h, age=a)
                    for t, d, u, h, a in aggregate
                ]

    def imgserp_factory_collect(
        self, as_dict: bool = False
    ) -> Optional[list[ImageSERP] | dict[str, Any]]:
        if self.mode != self.Mode.images:
            return None
        else:
            titles = self.get_search_titles()
            descriptions = self.get_search_descriptions()
            urls = self.get_search_urls()
            property_url = self.get_image_property_url()
            image_source = self.get_image_source()
            hostnames = self.get_search_hostname()
            age = self.get_image_age()
            confidence_level = self.get_image_confidence()

            aggregate = zip(
                titles,
                descriptions,
                urls,
                property_url,
                image_source,
                hostnames,
                confidence_level,
                age,
            )
            if as_dict:
                return [
                    asdict(
                        self.ImageSERP(
                            title=t,
                            description=d,
                            url=u,
                            property_url=p,
                            image_source=s,
                            hostname=h,
                            image_confidence=c,
                            age=a,
                        )
                    )
                    for t, d, u, p, s, h, c, a in aggregate
                ]
            else:
                return [
                    self.ImageSERP(
                        title=t,
                        description=d,
                        url=u,
                        property_url=p,
                        image_source=s,
                        hostname=h,
                        image_confidence=c,
                        age=a,
                    )
                    for t, d, u, p, s, h, c, a in aggregate
                ]

    def vidserp_factory_collect(
        self, as_dict: bool = False
    ) -> Optional[list[VideoSERP] | dict[str, Any]]:
        if self.mode != self.Mode.videos:
            return None
        else:
            titles = self.get_search_titles()
            descriptions = self.get_search_descriptions()
            urls = self.get_search_urls()
            hostnames = self.get_search_hostname()
            thumbnail_url = self.get_video_thumbnail_url()
            video_publisher = self.get_video_publisher()
            video_views = self.get_video_views()
            age = self.get_result_age()
            aggregate = zip(
                titles,
                descriptions,
                urls,
                thumbnail_url,
                hostnames,
                video_publisher,
                video_views,
                age,
            )
            if as_dict:
                return [
                    asdict(
                        self.VideoSERP(
                            title=t,
                            description=d,
                            url=u,
                            thumbnail_url=tu,
                            hostname=h,
                            video_publisher=vp,
                            video_views=vv,
                            age=a,
                        )
                    )
                    for t, d, u, tu, h, vp, vv, a in aggregate
                ]
            else:
                return [
                    self.VideoSERP(
                        title=t,
                        description=d,
                        url=u,
                        thumbnail_url=tu,
                        hostname=h,
                        video_publisher=vp,
                        video_views=vv,
                        age=a,
                    )
                    for t, d, u, tu, h, vp, vv, a in aggregate
                ]


def main(*args, **kwargs):
    brave_search = BraveSearchAPI(urllib3.PoolManager(), **kwargs)
    brave_search.send_query(*args)

    if webserp := brave_search.webserp_factory_collect(as_dict=True):
        core.utils.file_system.lst_dict_to_csv(
            webserp, f"brave-web-search-report-{datetime.date.today()}"
        )
    elif imgserp := brave_search.imgserp_factory_collect(as_dict=True):
        core.utils.file_system.lst_dict_to_csv(
            imgserp, f"brave-image-search-report-{datetime.date.today()}"
        )
    elif vidserp := brave_search.vidserp_factory_collect(as_dict=True):
        core.utils.file_system.lst_dict_to_csv(
            vidserp, f"brave-image-search-report-{datetime.date.today()}"
        )


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Brave API Wrapper CLI Interface")

    arg_parser.add_argument(
        "--web", action="store_true", help="Enable Web Search mode."
    )
    arg_parser.add_argument(
        "--images", action="store_true", help="Enable Image Search mode."
    )
    arg_parser.add_argument(
        "--videos", action="store_true", help="Enable Video Search mode."
    )
    arg_parser.add_argument(
        "--spellcheck", action="store_true", help="Let Brave spellcheck your query."
    )
    arg_parser.add_argument(
        "--count", type=int, default=None, help="Provide a result set count."
    )
    arg_parser.add_argument(
        "--offset", type=int, default=None, help="Provide a page offset number."
    )
    arg_parser.add_argument(
        "--country", type=str, default=None, help="Provide a country code for search."
    )
    arg_parser.add_argument(
        "--language", type=str, default=None, help="Provide a language code for search."
    )

    arg_parser.add_argument(
        "--ui_lang",
        type=str,
        default=None,
        help="Provide a ui language/market code for search.",
    )

    arg_parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Provide a search query. This is a required flag.",
    )

    arg_parser.add_argument(
        "--raw-query",
        action="store_true",
        help="Send unprocessed query to Brave Search",
    )

    arg_parser.add_argument(
        "--safesearch",
        type=str,
        default=None,
        help="Provide a safesearch filtering value.",
    )

    args = arg_parser.parse_args()

    main(
        args.query,
        args.raw_query,
        web=args.web,
        images=args.images,
        videos=args.videos,
        count=args.count,
        offset=args.offset,
        safesearch=args.safesearch,
        country=args.country,
        search_lang=args.language,
        ui_lang=args.ui_lang,
        spellcheck=args.spellcheck,
    )
