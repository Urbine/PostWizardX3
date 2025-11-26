import logging
import time
import regex as re
from abc import abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, NoReturn

# Third-party imports
from requests.exceptions import SSLError, ConnectionError

# Local imports
from core.models import WorkflowConfigObject
from core.utils.helpers import get_duration
from core.utils.system_shell import clean_console
from postwizard_sdk.builders import PostMetaNestedPayload
from workflows.interfaces import ContentBotRunner
from workflows.utils.logging import iter_session_print, terminate_loop_logging

W_co = TypeVar("W_co", covariant=True, bound=WorkflowConfigObject)


class ContentBotFlow(ContentBotRunner, Generic[W_co]):
    """
    ContentBotRunner class
    """

    def __init__(
        self,
        workflow_config: W_co,
        re_filter: str = r"(?=\W)\S",
        interactive: bool = True,
        auto_cache_sync: bool = False,
        post_required: int = 0,
        exclude_partner_tag=False,
        parent: bool = False,
    ):
        super().__init__(workflow_config, interactive=interactive, parent=parent)

        self._time_start = time.time()
        self._items_uploaded = 0
        self._iter_num = 0
        self._default_re_filter = re_filter
        self._auto_cache_sync = auto_cache_sync
        self._post_add = False
        self._posts_required = 0
        self._exclude_partner_tag = exclude_partner_tag

        if not self._interactive and self._posts_required <= 0:
            from workflows.exceptions import InvalidPostQuantityException

            raise InvalidPostQuantityException(self._posts_required)

        # Deferred assignment
        self._time_end = None
        self._wp_slug = None
        self._tag_prep = None
        self._tag_ints = None
        self._categ_ints = None
        self._thumbnail_name = None
        self._assets = None
        self._wp_last_post = None

    @property
    @abstractmethod
    def _title(self):
        pass

    @property
    @abstractmethod
    def _description(self):
        pass

    @property
    @abstractmethod
    def _tags_str(self):
        pass

    @property
    @abstractmethod
    def _thumbnail_link(self):
        pass

    @property
    @abstractmethod
    def _db_slug(self):
        pass

    def _session_start_print(self) -> None:
        clean_console()
        iter_session_print(self._console, self._total_ready, partner=self._partner)
        time.sleep(3)

    def _increment_iter_num(self) -> int:
        self._iter_num += 1
        return self._iter_num

    def _iter_session_print(self) -> None:
        clean_console()
        iter_session_print(
            self._console, self._items_uploaded, elem_num=self._increment_iter_num()
        )

    def _flow_session_end(self, log_statement: str, exhausted: bool) -> NoReturn:
        logging.info(log_statement)
        self._thumbnails_dir.cleanup()
        self._time_end = time.time()
        h, mins, secs = get_duration(self._time_end - self._time_start)
        try:
            terminate_loop_logging(
                self._console,
                self._iter_num,
                self._total_ready,
                self._items_uploaded,
                (h, mins, secs),
                exhausted,
                interactive=self._interactive,
            )
        except KeyboardInterrupt:
            if self._interactive:
                print("Goodbye! ಠ‿↼")
            logging.critical(
                f"KeyboardInterrupt exception handled -> _session_end_print at {__file__}"
            )
            time.sleep(0.5)
            # When ``exit`` is called, temp dirs will be automatically cleaned.
            exit(0)

    def _parse_assets(self) -> None:
        from workflows.utils.parsing import asset_parser

        self._assets = asset_parser(self._bot_config, self._partner)
        return None

    def _get_random_asset(self) -> Optional[str]:
        import random

        if self._assets is None:
            return None
        return random.choice(self._assets)

    @staticmethod
    def clean_console() -> None:
        from core.utils.system_shell import clean_console

        clean_console()
        return None

    def _add_post_prompt(self, next_post: bool = False) -> bool:
        from rich.prompt import Prompt

        if self._interactive:
            if next_post:
                if (
                    Prompt.ask(
                        f"[{self._prompt_style}]\nNext post? -> N/ENTER to review next post [/{self._prompt_style}]"
                    )
                    == ""
                ):
                    logging.info(
                        "User accepted to continue after successful post creation."
                    )
                    logging.info(
                        "Refreshing WordPress Local Cache and reloading site data to memory..."
                    )
                    clean_console()
                    if self._auto_cache_sync:
                        with self._console.status(
                            f"[{self._action_style}] Refreshing WordPress Local Cache... [blink]┌(◎_◎)┘[/blink] [/{self._action_style}]\n",
                            spinner="bouncingBall",
                        ):
                            self._site.cache_sync()
                    return True
                else:
                    self._flow_session_end(
                        "User declined further activity with the bot", False
                    )
            else:
                prompt_flow = Prompt.ask(
                    f"\n[{self._prompt_style}]Add post to WP? -> Y/N/ENTER to review next post [/{self._prompt_style}]",
                    choices=["y", "n", ""],
                    show_choices=False,
                    case_sensitive=False,
                )
                if prompt_flow == "":
                    # 'Enter' action
                    return False
                elif prompt_flow == "y":
                    logging.info(
                        f"User accepted video element {self._iter_num} for processing"
                    )
                    return True
                else:
                    self._flow_session_end(
                        "User declined further activity with the bot", False
                    )
        else:
            if self._post_add and self._iter_num >= self._posts_required:
                self._flow_session_end(
                    f"Exhausted videos required. Added ({self._iter_num}/{self._posts_required})",
                    False,
                )
            else:
                if self._auto_cache_sync:
                    self._site.cache_sync()
                return True

    def _loop_state_check(self) -> Optional[bool]:
        if self._add_post_prompt():
            return True
        else:
            if self._iter_num < self._total_ready - 1:
                logging.info(
                    f"Moving forward - ENTER action detected. State: Iteration: {self._iter_num} Total: {self._total_ready}"
                )
                return False
            else:
                self._flow_session_end(
                    f"List of available videos has been exhausted: Iteration: ({self._iter_num}) Total: ({self._total_ready})",
                    exhausted=True,
                )
        return None

    @abstractmethod
    def _build_slugs(self) -> List[str]:
        pass

    def _process_slug(self) -> None:
        import random
        from workflows.utils.selectors import SlugGetter

        built_slugs = self._build_slugs()
        if self._interactive:
            slug_getter = SlugGetter(self._console, self._build_slugs())
        else:
            slug_getter = SlugGetter(
                self._console,
                self._build_slugs(),
                interactive=False,
                proposed_slug=random.choice(built_slugs),
            )
        self._wp_slug = slug_getter.get()
        return None

    def _process_partner_tag(self) -> Optional[str]:
        from core.utils.interfaces import WordFilter

        return (
            WordFilter(delimiter="", filter_pattern=r"(?=\W)\S")
            .add_word(self._partner.lower())
            .filter()
        )

    def _process_tags(self) -> None:
        self._tag_prep = [
            tag for tag in re.split(self._default_re_filter, self._tags_str) if tag
        ]
        partner_tag = self._process_partner_tag()
        if partner_tag and not self._exclude_partner_tag:
            self._tag_prep.append(partner_tag)
        return None

    def _tag_checker(self, add_missing: bool = True, photo_tags: bool = False) -> None:
        from workflows.utils.checkers import tag_checker_print

        if self._tag_prep:
            self._tag_ints = tag_checker_print(
                self._console,
                self._site,
                self._tag_prep,
                add_missing=add_missing,
                interactive=self._interactive,
                photo_tags=photo_tags,
            )
        return None

    def _classify_content(self):
        from workflows.utils.selectors import ContentClassifier

        self._categ_ints = ContentClassifier(
            self._console,
            self._site,
            self._title,
            self._description,
            self._tags_str,
            interactive=self._interactive,
            aggregate_all=True,
        ).get()
        return None

    @abstractmethod
    def _build_payload(self) -> Dict[str, str | int]:
        pass

    def _prepare_thumbnail(self):
        from core.config.config_factories import image_config_factory
        from core.utils.strings import clean_filename

        image_config = image_config_factory()
        # Check whether ImageMagick conversion has been enabled in config.
        pic_format = (
            image_config.pic_format
            if image_config.imagick
            else image_config.pic_fallback
        )
        self._thumbnail_name = clean_filename(self._wp_slug, pic_format)
        logging.info(f"Thumbnail name: {self._thumbnail_name}")
        return None

    def _fetch_thumbnail(self) -> bool:
        from workflows.utils.file_handling import fetch_thumbnail

        status_code = fetch_thumbnail(
            self._thumbnails_dir.name, self._wp_slug, self._thumbnail_link
        )
        logging.info(f"Thumbnail fetched: {self._thumbnail_name} Status: {status_code}")
        if status_code != (200 or 201):
            logging.warning(
                f"Defective thumbnail or service unavailable: {self._thumbnail_name} Status: {status_code}"
            )
            return False
        return True

    @abstractmethod
    def _build_wp_thumb_payload(self) -> Dict[str, str]:
        pass

    def _wp_post_create(self) -> bool:
        push_post = lambda: self._site.post_create(self._build_payload())  # noqa: E731
        if self._interactive:
            with self._console.status(
                f"[{self._action_style}] Creating post on WordPress... [blink]┌(◎_◎)┘[/blink] [/{self._action_style}]\n",
                spinner="bouncingBall",
            ):
                upload_result = push_post()
        else:
            upload_result = push_post()

        logging.info(f"WordPress post push status: {upload_result}")
        if upload_result != 201:
            logging.warning(
                f"Defective post or service unavailable: {self._wp_slug} Status: {upload_result}"
            )
            if self._interactive:
                self._console.print(
                    f"[{self._warning_style}] Post creation failed -> Unable to proceed with the workflow safely. Terminating flow... [/{self._warning_style}]"
                )
            time.sleep(4)
            raise ConnectionError
        else:
            if self._interactive:
                self._console.print(
                    f"--> WordPress status code: {upload_result}",
                    style=self._action_style,
                )
                self._console.print(
                    "--> Post published successfully.",
                    style=self._action_style,
                )
        self._items_uploaded += 1
        return True

    def _get_wp_last_post(self):
        if self._wp_last_post is None:
            self._wp_last_post = self._site.get_last_post()
        return self._wp_last_post

    def _wp_post_publish(self) -> None:
        last_post = self._get_wp_last_post()
        self._site.publish_post(last_post.post_id)
        return None

    @abstractmethod
    def _build_post_meta_payload(self) -> PostMetaNestedPayload:
        pass

    def _submit_meta_payload(self) -> bool:
        from postwizard_sdk.utils.auth import PostWizardAuth
        from postwizard_sdk.utils.operations import update_post_meta

        post_meta_payload = self._build_post_meta_payload()
        last_post = self._get_wp_last_post()
        pw_meta_update = update_post_meta(
            post_meta_payload, last_post.post_id, auto_thumb=True
        )
        logging.info(f"Sent payload to PostWizard: {post_meta_payload.build()}")
        retries = 0
        while pw_meta_update != (200 or 201):
            logging.warning(f"Post meta update status: {pw_meta_update}. Retrying...")
            PostWizardAuth.reset_auth()
            pw_meta_update = update_post_meta(post_meta_payload, last_post.post_id)
            if pw_meta_update == (200 or 201):
                logging.info(f"Post meta update status: {pw_meta_update} -> Success!")
                break
            retries += 1
            time.sleep(5)
            if retries == 3:
                logging.warning(
                    f"Post meta update status: {pw_meta_update}. Max retries reached."
                )
                if self._interactive:
                    self._console.print(
                        "* There an error while injecting the post meta fields, likely an authentication issue. Check the session logs for more details...*",
                        style=self._warning_style,
                    )
                    self._console.print(
                        "--> Rolling back and exiting...\n",
                        style=self._warning_style,
                    )
                self._site.post_delete(last_post.post_id)
                return False

        logging.info(f"Post meta update status: {pw_meta_update}")
        post_meta_payload.clear()
        return True

    def _wp_upload_image(self):
        import os

        thumb_payload = self._build_wp_thumb_payload()
        logging.info(f"Image Attrs: {thumb_payload}")
        push_thumb = self._site.upload_image(
            os.path.join(self._thumbnails_dir.name, self._thumbnail_name), thumb_payload
        )
        if push_thumb != (200 or 201):
            logging.warning(
                f"Defective thumbnail or service unavailable: {self._thumbnail_name} Status: {push_thumb}"
            )
            return False
        else:
            if self._interactive:
                self._console.print(
                    f"--> WordPress Media Upload -> Status: {push_thumb}",
                    style=self._action_style,
                )
                self._console.print(
                    "--> Thumbnail uploaded successfully.",
                    style=self._action_style,
                )
        return True

    def _social_sharing(self) -> None:
        from workflows.utils.social import social_sharing_controller

        return social_sharing_controller(
            self._console,
            self._description,
            self._wp_slug,
            self._bot_config,
            self._site,
        )

    def _main_flow(self) -> bool:
        self._process_slug()
        self._process_partner_tag()
        self._process_tags()
        self._tag_checker(add_missing=True)
        self._classify_content()
        self._prepare_thumbnail()
        self._fetch_thumbnail()
        self._wp_upload_image()
        self._wp_post_create()
        self._wp_post_publish()
        self._submit_meta_payload()
        self._social_sharing()
        return self._add_post_prompt(next_post=True)

    def _interactive_flow(self) -> None:
        try:
            import datetime

            next_post = self._main_flow()
            if next_post:
                self._wp_last_post = None
                return
            else:
                self._flow_session_end(
                    f"Session Ended at {datetime.datetime.now()}", exhausted=False
                )
        except (SSLError, ConnectionError) as e:
            logging.warning(f"Caught exception {e!r} - Prompting user")
            this_slug = (
                last_slug.slug
                if hasattr(last_slug := self._wp_last_post, "slug")
                else ""
            )
            is_published = True if self._wp_slug == this_slug else False
            if self._interactive:
                from rich.prompt import Confirm

                self._console.print(
                    "* There was a connection error while processing this post. Check the logs for more details...*",
                    style=self._warning_style,
                )
                self._console.print(
                    f"Post {self._wp_slug if self._wp_slug else ''} was {'' if is_published else 'NOT'} published!",
                    style=self._warning_style,
                )

                if Confirm.ask(
                    f"\n[{self._prompt_style}] Do you want to continue? Y/N to exit: [{self._prompt_style}]"
                ):
                    logging.info(f"User accepted to continue after catching {e!r}")
                    if is_published:
                        self._items_uploaded += 1
                else:
                    self._flow_session_end(
                        f"User refused to continue after catching {e!r}",
                        exhausted=False,
                    )
            else:
                self._flow_session_end(
                    f"Headless flow encountered {e!r} and won't continue",
                    exhausted=False,
                )

    def _flow_start(self):
        if self._interactive:
            self._interactive_flow()

    @abstractmethod
    def _main_loop(self) -> None:
        pass

    def run(self) -> None:
        self._init_run()
        self._main_loop()
