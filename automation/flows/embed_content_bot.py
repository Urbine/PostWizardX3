import logging
import re
from typing import Dict, List

# Local imports
from core.utils.helpers import get_duration
from core.config.config_factories import vid_embed_bot_conf_factory
from postwizard_sdk.builders import PostMetaNestedPayload
from workflows.interfaces import ContentBotFlow
from workflows.interfaces import EmbedsMultiSchema


class EmbedContentBot(ContentBotFlow):
    def __init__(self):
        super().__init__(vid_embed_bot_conf_factory(), exclude_partner_tag=True)

        self.__db_interface = None
        self.__video_duration = None
        self.__studio = None
        self.__models = None
        self.__title = None
        self.__description = None
        self.__tags_str = None
        self.__thumbnail_link = None
        self.__db_slug = None
        self.__models_prep = None
        self.__model_ints = None
        self.__embed_code = None

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
            self._define_query()
            self._run_query()
            self._filter_embeds()
            self._thumbnails_dir_setup()
            self.__db_interface = EmbedsMultiSchema(self._cursor)
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
    def _title(self, title):
        self.__title = title

    @property
    def _description(self):
        return self.__description

    @_description.setter
    def _description(self, description):
        self.__description = description

    @property
    def _tags_str(self):
        return self.__tags_str

    @_tags_str.setter
    def _tags_str(self, tags_str):
        self.__tags_str = tags_str

    @property
    def _thumbnail_link(self):
        return self.__thumbnail_link

    @_thumbnail_link.setter
    def _thumbnail_link(self, thumbnail_link):
        self.__thumbnail_link = thumbnail_link

    @property
    def _db_slug(self):
        return self.__db_slug

    @_db_slug.setter
    def _db_slug(self, db_slug):
        self.__db_slug = db_slug

    def _build_slugs(self) -> List[str]:
        from workflows.builders import WorkflowSlugBuilder

        slug_builder = WorkflowSlugBuilder()
        slugs = [
            f"{slug}" if (slug := self.__db_slug) else "",
            slug_builder.title(self.__title).build(),
            slug_builder.title(self.__title).model(self.__models).build(),
            slug_builder.title(self.__title).studio(self.__studio).build(),
            slug_builder.title(self.__title)
            .model(self.__models)
            .partner(self._partner)
            .build(),
            slug_builder.title(self.__title)
            .model(self.__models)
            .studio(self.__studio)
            .build(),
            slug_builder.title(self.__title)
            .model(self.__models)
            .partner(self._partner)
            .content_type("video")
            .build(),
            slug_builder.title(self.__title)
            .model(self.__models)
            .studio(self.__studio)
            .content_type("video")
            .build(),
            slug_builder.title(self.__title)
            .model(self.__models)
            .content_type("video")
            .partner(self._partner)
            .build(),
            slug_builder.title(self.__title)
            .model(self.__models)
            .content_type("video")
            .studio(self.__studio)
            .build(),
            slug_builder.partner(self._partner)
            .model(self.__models)
            .title(self.__title)
            .content_type("video")
            .studio(self.__studio)
            .build(),
            slug_builder.model(self.__models)
            .title(self.__title)
            .studio(self.__studio)
            .build(),
        ]
        return list(dict.fromkeys([slug for slug in slugs if slug]))

    def _build_payload(self) -> Dict[str, str | int]:
        from workflows.builders import WorkflowPostPayloadBuilder

        payload = WorkflowPostPayloadBuilder().payload_factory_simple(
            self._wp_slug,
            self._general_config.default_status,
            self.__title,
            self.__description,
            self._tag_ints,
            model_int_lst=self.__model_ints,
            categs=self._categ_ints,
        )
        return payload

    def _prepare_models(self) -> None:
        models_field = self.__models
        if models_field:
            self.__models_prep = re.split(r"(?=\W)\S", models_field)

    def _find_models(self) -> None:
        from workflows.utils.checkers import model_checker

        if self.__models_prep:
            self.__model_ints = model_checker(
                self._site, self.__models_prep, add_missing=True
            )

    def _build_wp_thumb_payload(self) -> Dict[str, str]:
        from workflows.builders import WorkflowMediaPayload

        img_attrs = WorkflowMediaPayload().payload_factory(
            self.__title, self.__description
        )
        return img_attrs

    def _build_post_meta_payload(self) -> PostMetaNestedPayload:
        from postwizard_sdk.models import (
            Ethnicity,
            ToggleField,
            Orientation,
            HairColor,
            Production,
        )
        from workflows.utils.strings import transform_partner_iframe

        transformed_iframe = transform_partner_iframe(
            self.__embed_code, "https://video.whoresmen.com"
        )
        h, mins, secs = get_duration(int(self.__video_duration))
        post_meta_payload = (
            PostMetaNestedPayload()
            .ethnicity(
                Ethnicity.INDIAN
                if self._partner.startswith("Desi")
                else Ethnicity.ASIAN
            )
            .hd(ToggleField.ON)
            .orientation(Orientation.STRAIGHT)
            .production(Production.PROFESSIONAL)
            .hair_color(HairColor.BLACK)
            .embed_code(transformed_iframe)
            .hours(int(h))
            .minutes(int(mins))
            .seconds(int(secs))
        )
        return post_meta_payload

    def _populate_internal_state(self) -> None:
        self.__title = self.__db_interface.get_title()
        self.__description = self.__db_interface.get_description()
        self.__embed_code = self.__db_interface.get_embed()
        self.__video_duration = self.__db_interface.get_duration()
        self.__studio = self.__db_interface.get_studio()
        self.__db_slug = f"{slug}" if (slug := self.__db_interface.get_slug()) else ""
        self.__thumbnail_link = self.__db_interface.get_thumbnail()
        self.__models = (
            girl
            if (girl := self.__db_interface.get_pornstars())
            else self.__db_interface.get_models()
        )
        self.__tags_str = (
            categories
            if (categories := self.__db_interface.get_categories())
            else self.__db_interface.get_tags()
        )

    def _main_loop(self) -> None:
        for num, vid in enumerate(self._ready_posts):
            self.clean_console()
            self._iter_session_print()
            self.__db_interface.load_data_instance(vid)
            logging.info(f"Displaying on iteration {self._iter_num} data: {vid}")

            for field in self.__db_interface.get_fields(keep_indx=True):
                num, fld = field
                if re.match(self.__db_interface.SchemaRegEx.pat_duration, fld):
                    hs, mins, secs = get_duration(
                        int(self.__db_interface.get_duration())
                    )
                    self._console.print(
                        f"{num + 1}. Duration: \n\tHours: [bold red]{hs}[/bold red] \n\tMinutes: [bold red]{mins}[/bold red] \n\tSeconds: [bold red]{secs}[/bold red]",
                        style=self._default_style,
                    )  # From seconds to hours to minutes
                else:
                    self._console.print(
                        f"{num}. {fld.title()}: {vid[num]}", style=self._default_style
                    )

            if self._loop_state_check():
                self._populate_internal_state()
                self._prepare_models()
                self._find_models()
                self._flow_start()


if __name__ == "__main__":
    EmbedContentBot().run()
