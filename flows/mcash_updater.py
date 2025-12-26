# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
MCash Content Updater

A command-line utility for synchronizing local content databases with the latest video content
from MongerCash affiliate partner offers. This tool automates the process of fetching, processing,
and updating local content repositories with fresh media assets and metadata.

Key Features:
- Automated content database updates
- Video metadata extraction and processing
- Thumbnail generation and optimization
- Support for selective updates using partner hints
- Headless browser operation support

Main Functionality:
- Scrapes and parses video content from MongerCash
- Updates local SQLite databases with new content
- Handles media downloads and storage
- Provides progress tracking and logging

Dependencies:
- Selenium: For web scraping and content extraction
- SQLite: For local content storage
- Rich: For enhanced console output

Example:
    >>> from flows.mcash_updater import MCashUpdater
    >>> updater = MCashUpdater(img_optimize=True)
    >>> updater.run()  # Start the update process

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import sqlite3
import time
import os
import warnings

from argparse import ArgumentParser
from tempfile import TemporaryDirectory
from typing import Tuple

from rich.console import Console

from core.models.file_system import ApplicationPath
from core.utils.data_access import WebDriverFactory
from core.utils.file_system import (
    exists_ok,
    logging_setup,
    load_from_file,
    remove_if_exists,
)
from core.utils.helpers import get_duration
from core.utils.strings import clean_filename
from workflows.tasks import (
    get_vid_dump_flow,
    get_set_source_flow,
    parse_txt_dump_chain,
    db_generate,
)
from workflows.utils.logging import ConsoleStyle
from workflows.exceptions import DataSourceUpdateError


class MCashUpdater:
    def __init__(self, img_optimize: bool = True):
        self._start_time = time.time()
        self._console = Console()
        self._cli_args = None
        self._img_optimize = img_optimize
        self._temp_dir = TemporaryDirectory(dir=exists_ok(ApplicationPath.TEMPORARY))
        # --- Deferred assignment ---
        self._hints = None

    def cli_arg_updater(self) -> None:
        """
        Process and handle command line arguments for the MongerCash update wizard.
        """

        arg_parser = ArgumentParser(
            description="MongerCash local update wizard arguments"
        )

        arg_parser.add_argument(
            "--hints",
            nargs="+",
            type=str,
            help="This parameter receives a space-separated list of the first word of the partner offers for matching",
        )

        arg_parser.add_argument(
            "--parent",
            action="store_true",
            help="Set if you want the resulting files to be located in the parent dir.",
        )

        arg_parser.add_argument(
            "--gecko",
            action="store_true",
            help="Use the Gecko webdriver for this process.",
        )

        arg_parser.add_argument(
            "--headless", action="store_true", help="Browser headless execution."
        )

        arg_parser.add_argument(
            "--silent", action="store_true", help="Ignore user warnings"
        )

        self._cli_args = arg_parser.parse_args()

    def _logging_setup(self):
        if self._cli_args.silent:
            warnings.filterwarnings("ignore")
        logging_setup("logs", __file__)

    def _get_hints(self):
        self._hints = list(self._cli_args.hints)

    def _print_header(self):
        logging.info(f"Passed in {self._cli_args.__dict__}")
        logging.info(f"Started Session ID: {os.environ.get('SESSION_ID')}\n")
        self._console.print(
            f"Session ID: {os.environ.get('SESSION_ID')}",
            style=ConsoleStyle.TEXT_STYLE_ATTENTION.value,
            justify="left",
        )

        self._console.print(
            "Welcome to the MongerCash local update wizard\n",
            style=ConsoleStyle.TEXT_STYLE_ACTION.value,
            justify="center",
        )

    def _fetch_dump_txt(self, temp_dir, hint) -> Tuple[str, int]:
        webdriver = WebDriverFactory(
            temp_dir.name,
            headless=self._cli_args.headless,
            gecko=self._cli_args.gecko,
            no_imgs=self._img_optimize,
        )
        fetched_filename = get_vid_dump_flow(
            webdriver.get_instance(),
            partner_hint=hint,
            temp_dir_p=temp_dir.name,
        )
        dump_txt_filename = load_from_file(
            fetched_filename, "txt", dirname=temp_dir.name, parent=self._cli_args.parent
        )
        logging.info(f"Loading dump txt {fetched_filename} from {temp_dir.name}")
        retry_offset = 3
        retries = 0
        while len(dump_txt_filename) == 0:
            # If the file is empty, it means that something went wrong with the
            # webdriver.
            logging.warning("The content of the dump file is empty, retrying...")

            time.sleep(retry_offset)
            logging.info(
                f"Dump fetch - Retry number {retries} | Current offset: {retry_offset}"
            )
            retry_offset += 2
            retries += 1

            fetched_filename = get_vid_dump_flow(
                webdriver.get_instance(),
                partner_hint=hint,
                temp_dir_p=temp_dir.name,
            )
            dump_txt_filename = load_from_file(
                fetched_filename,
                "txt",
                dirname=temp_dir.name,
                parent=self._cli_args.parent,
            )

        if len(dump_txt_filename) > 0:
            parsing_result = self._parse_store_vid_dump(temp_dir.name, fetched_filename)
            return parsing_result
        else:
            raise DataSourceUpdateError("Failed to fetch dump file")

    def _fetch_set_source_f(self, temp_dir, hint):
        webdriver = WebDriverFactory(
            temp_dir.name,
            headless=self._cli_args.headless,
            gecko=self._cli_args.gecko,
            no_imgs=self._img_optimize,
        )
        photoset_source = get_set_source_flow(
            webdriver.get_instance(), partner_hint=hint
        )
        retry_offset = 3
        retries = 0
        while len(photoset_source[0]) == 0:
            logging.info(photo_fail := "The source file is empty, retrying...")
            warnings.warn(photo_fail, UserWarning)

            time.sleep(retry_offset)
            retry_offset += 2
            logging.info(
                f"Photo set fetch - Retry number {retries} | Current offset: {retry_offset}"
            )
            retries += 1

            photoset_source = get_set_source_flow(
                webdriver.get_instance(), partner_hint=hint
            )

        if len(photoset_source[0]) > 0:
            return self._parse_store_set_dump(photoset_source)
        else:
            raise DataSourceUpdateError("Failed to fetch photo set source file")

    def _parse_store_vid_dump(self, temp_dir_name: str, filename: str):
        db_name = clean_filename(filename, "db")
        db_path = os.path.join(exists_ok(ApplicationPath.ARTIFACTS), db_name)
        remove_if_exists(db_path)
        db_conn = sqlite3.connect(db_path)
        cursor = db_conn.cursor()
        logging.info(f"Created database {db_name} at {db_path}")
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute(
            """
        CREATE TABLE
            videos(
            title,
            description,
            model,
            tags,
            date,
            duration,
            source_url,
            thumbnail_url,
            tracking_url,
            wp_slug
            )
        """
        )

        parsing_result = parse_txt_dump_chain(
            filename,
            db_name,
            db_conn,
            cursor,
            dirname=temp_dir_name,
            parent=self._cli_args.parent,
        )

        logging.info(
            vid_result
            := f"{parsing_result[1]} video entries have been processed from {filename} and inserted into\n{db_path}\n"
        )
        self._console.print(
            vid_result, style=ConsoleStyle.TEXT_STYLE_ATTENTION.value, justify="left"
        )
        return parsing_result

    def _parse_store_set_dump(self, parsing_result):
        parsing_photos = db_generate(
            parsing_result[0], parsing_result[1], parent=self._cli_args.parent
        )

        logging.info(
            photo_result
            := f"{parsing_photos[1]} photo set entries have been processed and inserted into\n{parsing_photos[0]}\n"
        )
        self._console.print(
            photo_result, style=ConsoleStyle.TEXT_STYLE_ATTENTION.value, justify="left"
        )
        return parsing_photos[1] > 0

    def print_duration(self):
        end_time = time.time()
        hours, mins, secs = get_duration(end_time - self._start_time)
        logging.info(
            time_elapsed := f"Process took: Hours: {hours} Mins: {mins} Secs: {secs}"
        )
        self._console.print(
            time_elapsed, style=ConsoleStyle.TEXT_STYLE_ATTENTION.value, justify="left"
        )
        logging.shutdown()

    def _setup_instance(self):
        self.cli_arg_updater()
        self._logging_setup()
        self._print_header()
        self._get_hints()

    def _vid_dump_flow(self, temp_dir, hint: str):
        parsing_result = self._fetch_dump_txt(temp_dir, hint)
        if parsing_result:
            # Parsed more than 0 entries
            return parsing_result[1] > 0
        return False

    def _photoset_dump_flow(self, temp_dir, hint: str):
        return self._fetch_set_source_f(temp_dir, hint)

    def _process_hint(self, temp_dir, hint):
        if self._vid_dump_flow(temp_dir, hint):
            if self._photoset_dump_flow(temp_dir, hint):
                return True
        return False

    def _flow_start(self):
        success = True
        for hint in self._hints:
            temp = TemporaryDirectory(dir=exists_ok(ApplicationPath.TEMPORARY))
            success &= self._process_hint(temp, hint)
            temp.cleanup()

            if not success:
                raise DataSourceUpdateError(
                    "One or more tasks failed during the update process"
                )

    def run(self):
        self._setup_instance()
        with self._console.status(
            "Updating MongerCash artifacts. Please wait...", spinner="bouncingBall"
        ):
            self._flow_start()
        self.print_duration()


if __name__ == "__main__":
    MCashUpdater().run()
