import argparse
import logging
from tempfile import TemporaryDirectory
from typing import Dict

from automation.flows.mcash_content_bot import MCashContentBot

from core.config.config_factories import (
    mcash_gallery_bot_conf_factory,
    image_config_factory,
)
from core.models.file_system import ApplicationPath
from core.utils.file_system import exists_ok
from core.utils.interfaces import WordFilter


class MCashGalleryBot(MCashContentBot):
    def __init__(
        self, gecko_enabled: bool, headless_browser: bool, parent: bool = False
    ):
        super().__init__(load_assets=False, parent=parent)
        self._bot_config = mcash_gallery_bot_conf_factory()
        self._gecko_enabled = gecko_enabled
        self._headless_browser = headless_browser
        self._date = None
        self._download_url = None
        self._temp_download_dir = TemporaryDirectory(
            prefix="download", dir=exists_ok(ApplicationPath.TEMPORARY)
        )

    def _build_payload(self) -> Dict[str, str | int]:
        from workflows.builders import PhotoPostPayloadBuilder

        self._console.print("\n--> Making payload...", style=self._action_style)
        return PhotoPostPayloadBuilder().photos_payload_factory(
            self._general_config.default_status,
            self._title,
            self._partner,
            self._tag_ints,
            reverse_slug=False,
        )

    def _process_slug(self) -> None:
        self._wp_slug = (
            WordFilter(delimiter="-", stopword_removal=True)
            .add_word(self._title)
            .filter()
        )

    def _fetch_photoset(self):
        from workflows.utils.file_handling import fetch_zip, extract_zip

        fetch_zip(
            self._temp_download_dir.name,
            self._download_url,
            parent=self._parent,
            gecko=self._gecko_enabled,
            headless=self._headless_browser,
        )
        extract_zip(self._temp_download_dir.name, self._thumbnails_dir.name)

    def _upload_photo_set(self):
        from workflows.utils.file_handling import upload_image_set

        if self._title:
            upload_image_set(
                image_config_factory().pic_fallback,
                self._thumbnails_dir.name,
                self._title,
                self._site,
            )

    def _main_flow(self) -> bool:
        self._process_slug()
        self._process_partner_tag()
        self._tag_checker(add_missing=True, photo_tags=True)
        self._fetch_photoset()
        self._upload_photo_set()
        self._wp_post_create()
        return self._add_post_prompt(next_post=True)

    def _main_loop(self) -> None:
        for num, photo in enumerate(self._ready_posts):
            (title, *fields) = photo
            logging.info(f"Displaying on iteration {num} data: {photo}")
            self._title = title
            self._date: str = fields[0]
            self._download_url: str = fields[1]

            self.clean_console()

            self._iter_session_print()

            self._console.print(title, style=self._default_style)
            self._console.print(f"Date: {self._date}", style=self._default_style)
            self._console.print(
                f"Download URL: \n{self._download_url}", style=self._default_style
            )

            if self._loop_state_check():
                self._flow_start()


def cli_args_group():
    arg_parser = argparse.ArgumentParser(
        description="Gallery Select Assistant - Behaviour Tweaks"
    )

    arg_parser.add_argument(
        "--parent",
        action="store_true",
        default=False,
        help="""Define if database and file search happens in the parent directory.
                                                This argument also affects:
                                                1. Thumbnail search
                                                2. HotSync caching
                                                3. Cache cleaning
                                                The default is set to false, so if you execute this file as a module,
                                                you may not want to enable it because this is treated as a package.
                                                If you are experiencing issues with the location of your thumbnails and relative
                                                references, this is a good place to start.""",
    )

    arg_parser.add_argument(
        "--gecko",
        action="store_true",
        help="Use the gecko webdriver for the browser automation steps.",
    )

    arg_parser.add_argument(
        "--relevancy",
        action="store_true",
        help="Activate relevancy algorithm (experimental)",
    )

    arg_parser.add_argument(
        "--headless",
        action="store_true",
        help="Enable headless webdriver execution. Compatibility is experimental with this module.",
    )

    return arg_parser.parse_args()


def main():
    args_cli = cli_args_group()
    # Disabled for now
    # relevancy_on = args_cli.relevancy
    gecko = args_cli.gecko
    parent = args_cli.parent
    MCashGalleryBot(gecko_enabled=gecko, headless_browser=False, parent=parent).run()


if __name__ == "__main__":
    main()
