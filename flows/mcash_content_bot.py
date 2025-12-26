# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
MCash Content Bot for WordPress Content Management

A comprehensive CLI tool for managing and automating the creation of WordPress posts
for MongerCash affiliate partner offers. This bot integrates video processing, content
classification, and WordPress publishing into a streamlined workflow.

Key Features:
- Automated WordPress post creation and management
- Video content processing and classification
- Thumbnail management and asset handling
- Interactive console interface with progress tracking
- Support for content filtering and synchronization

The bot implements the ContentBotFlow interface and provides methods for:
- Content selection and database matching
- Asset management and parsing
- WordPress synchronization
- Session management and error handling

Dependencies:
- postwizard_sdk (PostWizardREST client SDK): For WordPress taxonomy management and metadata injection
- workflows.interfaces.ContentBotFlow: Base interface for bot operations
- core.config.config_factories: Configuration management

Example:
    >>> from flows.mcash_content_bot import MCashContentBot
    >>> bot = MCashContentBot()
    >>> bot.run()  # Start interactive session

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import re
from typing import List, Dict

from workflows.interfaces import ContentBotFlow
from core.config.config_factories import mcash_content_bot_conf_factory


class MCashContentBot(ContentBotFlow):
    def __init__(self, load_assets: bool = True, parent: bool = False):
        super().__init__(mcash_content_bot_conf_factory(), parent=parent)
        self._load_assets = load_assets
        self._models = None
        self._models_prep = None
        self._model_ints = None
        self._tracking_link = None
        self._source_url = None
        self._video_duration = None
        self._date = None
        self.__title = None
        self.__description = None
        self.__thumbnail_link = None
        self.__db_slug = None
        self.__tags_str = None

    def _init_run(self):
        try:
            self._console_setup()
            self._logging_setup()

            with self._console.status(
                f"[{self._action_style}] Initializing components... [blink]┌(◎_◎)┘[/blink] [/{self._action_style}]\n",
                spinner="bouncingBall",
            ):
                self._refresh_token_setup()
                self._wp_setup()
            self._do_wp_sync()
            self._do_content_select_db_match()
            self._select_guardian()
            self._run_query()
            self._filter_published()
            self._thumbnails_dir_setup()
            if self._load_assets:
                self._parse_assets()
            self.clean_console()
            self._session_start_print()
        except KeyboardInterrupt:
            logging.critical("KeyboardInterrupt exception detected")
            logging.info("Cleaning clipboard and temporary directories. Quitting...")
            print("Goodbye! ಠ‿↼")
            # When ``exit`` is called, temp dirs will be automatically cleaned.
            logging.shutdown()
            exit(0)

    @property
    def _title(self):
        return self.__title

    @_title.setter
    def _title(self, title: str):
        self.__title = title

    @property
    def _description(self):
        return self.__description

    @_description.setter
    def _description(self, description: str):
        self.__description = description

    @property
    def _thumbnail_link(self):
        return self.__thumbnail_link

    @_thumbnail_link.setter
    def _thumbnail_link(self, thumbnail_link: str):
        self.__thumbnail_link = thumbnail_link

    @property
    def _tags_str(self):
        return self.__tags_str

    @_tags_str.setter
    def _tags_str(self, tags_str: str):
        self.__tags_str = tags_str

    @property
    def _db_slug(self):
        return self.__db_slug

    @_db_slug.setter
    def _db_slug(self, db_slug: str):
        self._db_slug = db_slug

    def _build_slugs(self) -> List[str]:
        from workflows.builders import WorkflowSlugBuilder

        slug_builder = WorkflowSlugBuilder()
        slugs = [
            f"{self._db_slug}-video",
            slug_builder.title(self._title).build(),
            slug_builder.title(self._title).model(self._models).build(),
            slug_builder.title(self._title)
            .model(self._models)
            .partner(self._partner)
            .build(),
            slug_builder.partner(self._partner)
            .model(self._models)
            .title(self._title)
            .build(),
            slug_builder.model(self._models)
            .partner(self._partner)
            .title(self._title)
            .build(),
            slug_builder.title(self._title)
            .model(self._models)
            .content_type("video")
            .build(),
            slug_builder.model(self._models)
            .title(self._title)
            .content_type("video")
            .build(),
        ]
        return slugs

    def _build_payload(self) -> Dict[str, str | int]:
        from workflows.builders import WorkflowPostPayloadBuilder
        from workflows.utils.strings import mask_mcash_tracking_link

        payload = WorkflowPostPayloadBuilder().payload_factory_mcash(
            self._wp_slug,
            self._general_config.default_status,
            self._title,
            self._description,
            mask_mcash_tracking_link(self._tracking_link, "https://join.yoursite.com"),
            self._get_random_asset(),
            # Not the partner name, but a phrase that will be used in the post content payload.
            "Enjoy free porn now",
            self._tag_ints,
            self._model_ints,
            categs=self._categ_ints,
        )
        return payload

    def _build_wp_thumb_payload(self):
        from workflows.builders import WorkflowMediaPayload

        img_attrs = WorkflowMediaPayload().payload_factory(
            self._title, self._description
        )
        return img_attrs

    def _build_post_meta_payload(self):
        from postwizard_sdk.builders import PostMetaNestedPayload
        from postwizard_sdk.models import (
            Ethnicity,
            HairColor,
            Orientation,
            Production,
            ToggleField,
        )
        from workflows.utils.strings import transform_mcash_hosted_link

        digits = re.compile(r"\d+")
        target_video_base_url = "https://video.yoursite.com/stream/"
        post_meta_builder = (
            PostMetaNestedPayload()
            .ethnicity(Ethnicity.ASIAN)
            .production(Production.PROFESSIONAL)
            .orientation(Orientation.STRAIGHT)
            .video_url(
                f"{target_video_base_url}{transform_mcash_hosted_link(self._source_url)}"
            )
            .hd(ToggleField.ON)
            .hair_color(HairColor.BLACK)
            .minutes(int(digits.findall(self._video_duration)[0]))
        )
        return post_meta_builder

    def _prepare_models(self) -> List[str]:
        try:
            self._model_prep = [
                model.strip() for model in re.split(r"(?=\W)\S", self._models) if model
            ]
        except AttributeError:
            self._model_prep = []
        return self._model_prep

    def _find_models(self):
        from workflows.utils.checkers import model_checker

        self._model_ints = model_checker(
            self._site, self._prepare_models(), add_missing=True
        )

    def _main_loop(self) -> None:
        for num, vid in enumerate(self._ready_posts):
            self._iter_session_print()
            logging.info(f"Displaying on iteration {self._iter_num} data: {vid}")
            (title, *fields) = vid
            self.__title = title
            self.__description = fields[0]
            self._models = fields[1]
            self.__tags_str = fields[2]
            self._date = fields[3]
            self._video_duration = fields[4]
            self._source_url = fields[5]
            self.__thumbnail_link = fields[6]
            self._tracking_link = fields[7]
            self.__db_slug = fields[8]

            style_fields = self._default_style
            self._console.print(title, style=style_fields)
            self._console.print(self._description, style=style_fields)
            self._console.print(f"Duration: {self._video_duration}", style=style_fields)
            self._console.print(f"Tags: {self._tags_str}", style=style_fields)
            self._console.print(f"Models: {self._models}", style=style_fields)
            self._console.print(f"Date: {self._date}", style=style_fields)
            self._console.print(
                f"Thumbnail URL: {self._thumbnail_link}", style=style_fields
            )
            self._console.print(f"Source URL: {self._source_url}", style=style_fields)

            if self._loop_state_check():
                # In rare occasions, the ``tags`` is None and the real tags are placed in the ``models`` variable
                # this special handling prevents crashes
                if not self._tags_str:
                    self.__tags_str, self._models = self._models, self.__tags_str

                self._find_models()
                self._flow_start()


if __name__ == "__main__":
    MCashContentBot().run()
