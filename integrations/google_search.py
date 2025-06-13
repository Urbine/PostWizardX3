"""
Google Search Module

This module provides basic interfaces to Google Custom Search API for both web and image searches.
It implements two main classes:

1. Google: For querying Google's web search API and retrieving structured search results
   - Supports basic web search functionality
   - Returns search results as SerpItem objects with title, URL, and snippet

2. GoogleImage: For querying Google's image search API with advanced filtering options
   - Supports filtering by image size (from icon to huge)
   - Supports filtering by image type (clipart, face, lineart, photo, stock, animated)
   - Returns results as ImageSerpItem objects with image link, context, title, and snippet

Both classes require API authentication keys configured through the core.google_search_conf()
configuration manager.

Dependencies:
- requests for API communication
- dataclasses and enum for type definitions
- core.google_search_conf for API credentials

Usage:
    google = Google()
    results = google.get_serp_items("search query")

    image_search = GoogleImage()
    image_results = image_search.get_serp_items("search query",
                                               size=GoogleImage.ImageSize.LARGE,
                                               image_type=GoogleImage.ImageType.PHOTO)
Author: Yoham Gabriel Github@Urbine
Email: yohamg@programmer.org

"""

import requests

from dataclasses import dataclass
from enum import Enum

# Local implementations
from core import google_search_conf


class Google:
    """
    Google class provides methods to interact with the Google Custom Search API.

    This class is designed to simplify querying Google's custom search engine using an API key and a specific search engine ID.
    It encapsulates the necessary base URL, API key, and search engine ID to construct and execute queries.
    """

    @dataclass(kw_only=True)
    class SerpItem:
        title: str
        formatted_url: str
        snippet: str

    def __init__(self):
        self.base_url = "https://www.googleapis.com/customsearch/v1?"
        self.api_key = google_search_conf().api_key
        self.cse_id = google_search_conf().cse_id_web
        self.formed = f"{self.base_url}key={self.api_key}&cx={self.cse_id}"

    def query(self, query: str):
        request = requests.get(self.formed + f"&q={query}")
        return request.json()

    def get_serp_items(self, query: str):
        serp_items = []
        results = self.query(query)
        for item in results["items"]:
            serp_items.append(
                self.SerpItem(
                    title=item["title"],
                    formatted_url=item["link"],
                    snippet=item["snippet"],
                )
            )
        return serp_items


class GoogleImage:
    """
    This class provides methods for querying images from Google Custom Search API.
    It allows users to search for images based on a query, image size, and image type.
    """

    class ImageSize(Enum):
        """
        Image Size enumeration representing different size categories for images.
        """

        HUGE = "huge"
        ICON = "icon"
        LARGE = "large"
        MEDIUM = "medium"
        SMALL = "small"
        XLARGE = "xlarge"
        XXLARGE = "xxlarge"

    class ImageType(Enum):
        """
        ImageType is an enumeration representing the types of images available in a library.

        The class provides a set of predefined image type constants that can be used to identify or filter images based on their content.
        """

        CLIPART = "clipart"
        FACE = "face"
        LINEART = "lineart"
        PHOTO = "photo"
        STOCK = "stock"
        ANIMATED = "animated"

    @dataclass(kw_only=True)
    class ImageSerpItem:
        link: str
        context_link: str
        title: str
        snippet: str

    def __init__(self):
        self.base_url = "https://www.googleapis.com/customsearch/v1?"
        self.api_key = google_search_conf().api_key
        self.cse_id = google_search_conf().cse_id_img
        self.formed = (
            f"{self.base_url}key={self.api_key}&cx={self.cse_id}&searchType=image"
        )

    def query(
        self,
        query: str,
        size: ImageSize = ImageSize.LARGE,
        image_type: ImageType = ImageType.PHOTO,
    ):
        """
        Sends a GET request to an endpoint with the provided query parameters.

        :param query: The search query string.
        :param size: The desired image size. Defaults to ImageSize.LARGE.
        :param image_type: The desired image type. Defaults to ImageType.PHOTO.
        """
        request = requests.get(
            self.formed + f"&q={query}&imgSize={size.value}&imgType={image_type.value}"
        )
        return request.json()

    def get_serp_items(
        self,
        query: str,
        size: ImageSize = ImageSize.LARGE,
        image_type: ImageType = ImageType.PHOTO,
    ):
        """
        Retrieve a list of Search Engine Results Page (SERP) items based on the given query and parameters.

        :param query: The search query string.
        :param size: The desired image size. Defaults to ImageSize.LARGE.
        :param image_type: The desired image type. Defaults to ImageType.PHOTO.
        :return: list[ImageSerpItem] - A list of ImageSerpItem objects representing the search results.
        """
        results = self.query(query, size, image_type)
        items = []
        for item in results["items"]:
            items.append(
                self.ImageSerpItem(
                    link=item["link"],
                    context_link=item["image"]["contextLink"],
                    title=item["title"],
                    snippet=item["snippet"],
                )
            )
        return items


if __name__ == "__main__":
    google = GoogleImage()
    print(google.get_serp_items("Python programming language"))
