"""
Video embedding assistant.
Embed_assist works with the result of different integrations, which retrieve metadata from a remote content partner.
However, it is a specialized version of ``workflows.content_select`` and it deals with less structured data.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import logging
import os
import re
import sqlite3
import tempfile
import time

from re import Pattern
from dataclasses import dataclass, fields
from sqlite3 import OperationalError
from typing import TypeVar, Any, Generic, Optional

# Third-party modules
import pyclip
from requests.exceptions import SSLError, ConnectionError

# Local implementations
from core import helpers, embed_assist_conf, wp_auth, clean_filename, InvalidDB
from integrations import wordpress_api, WPEndpoints
from ml_engine import classify_title, classify_description, classify_tags
import workflows.content_select as cs

T = TypeVar("T")


class EmbedsMultiSchema(Generic[T]):
    """
    Complementary class dealing with dynamic SQL schema reading for content databases.

    EmbedsMultiSchema provides an interface to the main control flow of the bot that allows
    for direct index probing based on the present schema. This improvement will make it easier
    for the user to implement further functionality and behaviour based on specific fields.
    """

    @dataclass(frozen=True)
    class SchemaRegEx:
        """
        Immutable dataclass containing compiled RegEx patterns for class methods.
        """

        pat_slug: Pattern[str] = re.compile(r"slug", re.IGNORECASE)
        pat_embed: Pattern[str] = re.compile(r"embeds?", re.IGNORECASE)
        pat_thumbnail: Pattern[str] = re.compile(r"thumb(nail)?", re.IGNORECASE)
        pat_categories: Pattern[str] = re.compile(r"categor(ies)?", re.IGNORECASE)
        pat_rating: Pattern[str] = re.compile(r"ratings?", re.IGNORECASE)
        pat_title: Pattern[str] = re.compile(r"title", re.IGNORECASE)
        pat_link: Pattern[str] = re.compile(r"links?", re.IGNORECASE)
        pat_date: Pattern[str] = re.compile(r"date", re.IGNORECASE)
        pat_id: Pattern[str] = re.compile(r"id", re.IGNORECASE)
        pat_duration: Pattern[str] = re.compile(r"duration", re.IGNORECASE)
        pat_prnstars: Pattern[str] = re.compile(r"pornstars?", re.IGNORECASE)
        pat_models: Pattern[str] = re.compile(r"models?", re.IGNORECASE)
        pat_resolution: Pattern[str] = re.compile("resolution", re.IGNORECASE)
        pat_tags: Pattern[str] = re.compile(r"tags?", re.IGNORECASE)
        pat_likes: Pattern[str] = re.compile(r"likes?", re.IGNORECASE)
        pat_url: Pattern[str] = re.compile(r"urls?", re.IGNORECASE)
        pat_description: Pattern[str] = re.compile(r"description", re.IGNORECASE)
        pat_studio: Pattern[str] = re.compile(r"studios?", re.IGNORECASE)
        pat_trailer: Pattern[str] = re.compile(r"trailers?", re.IGNORECASE)
        pat_orientation: Pattern[str] = re.compile(r"orientation", re.IGNORECASE)

        def __iter__(self):
            for field in fields(self):
                yield getattr(self, field.name)

    @staticmethod
    def get_schema(db_cur: sqlite3) -> tuple[str, list[tuple[int, str]]]:
        """
        Get a tuple with the table and its field names.

        :param db_cur: ``sqlite3`` - Active database cursor
        :return: tuple('tablename', [(indx, 'fieldname'), ...])
        """
        query = "SELECT sql FROM sqlite_master"
        try:
            schema: list[tuple[int | str, ...]] = helpers.fetch_data_sql(query, db_cur)
            fst_table, *others = schema

            if others:
                logging.warning(
                    "Detected db with more than one table, fetching the first one by default."
                )

            table_name: str = fst_table[0].split(" ")[2].split("(")[0]
            query: str = "PRAGMA table_info({})".format(table_name)
            schema = helpers.fetch_data_sql(query, db_cur)
            fields_ord = list(map(lambda lstpl: lstpl[0:2], schema))

            return table_name, fields_ord

        except OperationalError:
            logging.critical(
                "db file was not found. Raising InvalidDB exception and quitting..."
            )
            raise InvalidDB

    def __init__(self, db_cur: sqlite3):
        """Initialisation logic for ``EmbedsMultiSchema`` instances.
            Supports data field handling that can carry out error handling without
            explicit logic in the main control flow or functionality using this class.
        :param db_cur: Active database cursor
        """
        schema = EmbedsMultiSchema.get_schema(db_cur)
        self.table_name: str = schema[0]
        self.__fields_indx = schema[1]
        self.__fields: list[Any] = list(map(lambda tpl: tpl[1], self.__fields_indx))
        self.field_count: int = len(self.__fields)
        self.__data: Optional[T] = None

    def load_data_instance(self, data_instance: T) -> None:
        """
        Setter for the private field ``data_instance``.
        :param data_instance: ``T`` - Generic type that ideally can handle __getitem__
        :return: ``None``
        """
        self.__data = data_instance
        return None

    def get_data_instance(self) -> Optional[T]:
        """Retrieve a copy of the data stored in the private field ``self.__data``

        :return: ``T`` | None - Generic Type
        """
        return self.__data

    def get_fields(self, keep_indx: bool = False) -> list[tuple[int, str]] | list[str]:
        """Get the actual database field names or a data structure (tuple) including
            its indexes.

        :param keep_indx: ``bool`` - Flag that, activated, retrieves indexes and column names in a tuple.
        :return:
        """
        if keep_indx:
            return self.__fields_indx
        else:
            return self.__fields

    def __safe_retrieve(self, re_pattern: Pattern[str]) -> Optional[T]:
        """Getter for the private fields ``self.__fields`` and ``self.__data``.
            Typically used in iterations where data access could result in exceptions that could
            cause undesired crashes.

        :param re_pattern: ``Pattern[str]`` - Regular Expression pattern (from local dataclass ``SchemaRegEx``)
        :return: ``T`` | None - Generic type object
        """
        match = helpers.match_list_single(re_pattern, self.__fields)
        if self.__data:
            try:
                return self.__data[match]
            except (IndexError, TypeError):
                return None
        else:
            return match

    def get_slug(self) -> Optional[str | int]:
        """Slug getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``slug`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_slug
        return self.__safe_retrieve(re_pattern)

    def get_embed(self) -> Optional[str | int]:
        """Embed getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``embed`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_embed
        return self.__safe_retrieve(re_pattern)

    def get_thumbnail(self) -> Optional[str | int]:
        """Thumbnail getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``thumbnail`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_thumbnail
        return self.__safe_retrieve(re_pattern)

    def get_categories(self) -> Optional[str | int]:
        """Categories getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``categories`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_categories
        return self.__safe_retrieve(re_pattern)

    def get_rating(self) -> Optional[str | int]:
        """Rating getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``rating`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_rating
        return self.__safe_retrieve(re_pattern)

    def get_title(self) -> Optional[str | int]:
        """Title getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``title`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_title
        return self.__safe_retrieve(re_pattern)

    def get_link(self) -> Optional[str | int]:
        """Link getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``link`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_link
        return self.__safe_retrieve(re_pattern)

    def get_date(self) -> Optional[str | int]:
        """Date getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``date`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_date
        return self.__safe_retrieve(re_pattern)

    def get_id(self) -> Optional[str | int]:
        """ID getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``id`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_id
        return self.__safe_retrieve(re_pattern)

    def get_duration(self) -> Optional[str | int]:
        """Duration getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``Duration`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_duration
        return self.__safe_retrieve(re_pattern)

    def get_pornstars(self) -> Optional[str | int]:
        """Pornstars getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``pornstars`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_prnstars
        return self.__safe_retrieve(re_pattern)

    def get_models(self) -> Optional[str | int]:
        """Models getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``models`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_models
        return self.__safe_retrieve(re_pattern)

    def get_resolution(self) -> Optional[str | int]:
        """Resolution getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``resolution`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_resolution
        return self.__safe_retrieve(re_pattern)

    def get_tags(self) -> Optional[str | int]:
        """Tags getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``tags`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_tags
        return self.__safe_retrieve(re_pattern)

    def get_likes(self) -> Optional[str | int]:
        """Likes getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``likes`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_likes
        return self.__safe_retrieve(re_pattern)

    def get_url(self) -> Optional[str | int]:
        """URL getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``url`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_url
        return self.__safe_retrieve(re_pattern)

    def get_description(self) -> Optional[str | int]:
        """Description getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``description`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_description
        return self.__safe_retrieve(re_pattern)

    def get_studio(self) -> Optional[str | int]:
        """Studio getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``studio`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_studio
        return self.__safe_retrieve(re_pattern)

    def get_trailer(self) -> Optional[str | int]:
        """Trailer getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``trailer`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_trailer
        return self.__safe_retrieve(re_pattern)

    def get_orientation(self) -> Optional[str | int]:
        """Orientation getter/reader from the matched fields in the data structure in an instance of
            ``EmbedsMultiSchema``

        :return: ``Optional[str | int]`` - Data from ``self.__data`` located in the ``orientation`` index.
        """
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_orientation
        return self.__safe_retrieve(re_pattern)


def filter_tags(
    tgs: str, filter_lst: Optional[list[str]] = None
) -> Optional[list[str]]:
    """Remove redundant words found in tags and return a clear list of unique filtered tags.

    :param tgs: ``list[str]`` tags to be filtered
    :param filter_lst: ``list[str]`` lookup list of words to be removed
    :return: ``list[str]``
    """
    if tgs is None:
        return None

    no_sp_chars = lambda w: "".join(re.findall(r"\w+", w))

    # Split with a whitespace separator is not necessary at this point:
    t_split = tgs.split(spl if (spl := helpers.split_char(tgs)) != " " else "-1")

    new_set = set({})
    for tg in t_split:
        temp_lst = []
        sublist = tg.split(" ")
        for word in sublist:
            if filter_lst is None:
                temp_lst.append(no_sp_chars(word))
            elif word not in filter_lst:
                temp_lst.append(no_sp_chars(word))
            elif temp_lst:
                continue
        new_set.add(" ".join(temp_lst))
    return list(new_set)


def filter_published_embeds(
    wp_posts_f: list[dict[...]], videos: list[tuple[str, ...]], db_cur: sqlite3
) -> list[tuple[str, ...]]:
    """filter_published does its filtering work based on the published_json function.
    It is based on a similar version from module `content_select`, however, this one is adapted to embedded videos
    and a different db schema.

    This function does not need a lot of explanation, it takes in a list of tuples and iterates over them.
    By unpacking one of its core values, it carries out the manual classification to generate a new set of
    titles.

    :param videos: ``list[tuple[str, ...]]`` usually resulting from the SQL database query values.
    :param wp_posts_f: ``list[dict[str, ...]]`` WordPress Post Information case file (previously loaded and ready to process)
    :param db_cur: ``sqlite3`` - Active database cursor
    :return: ``list[tuple[str, ...]]`` with the new filtered values.
    """
    db_interface = EmbedsMultiSchema(db_cur)
    post_titles: list[str] = wordpress_api.get_post_titles_local(wp_posts_f, yoast=True)

    not_published: list[tuple] = []
    for elem in videos:
        db_interface.load_data_instance(elem)
        vid_title = db_interface.get_title()
        if vid_title in post_titles:
            continue
        else:
            not_published.append(elem)
    return not_published


def embedding_pilot(
    embed_ast_conf=embed_assist_conf(),
    wpauths=wp_auth(),
    wp_endpoints: WPEndpoints = WPEndpoints,
) -> None:
    """
    Assist the user in video embedding from the information originated from local
    implementations of Japanese adult content providers in the ``integrations`` package.

    :param embed_ast_conf: ``EmbedAssistConf`` Object with configuration info for this bot.
    :param wpauths: ``WPAuth`` object that contains configuration of your site.
    :param wp_endpoints: ``WPEndpoints`` object with the integration endpoints for WordPress.
    :return: ``None``
    """
    time_start = time.time()

    console, partner, not_published, wp_posts_f, thumbnails_dir, cur_dump = (
        cs.pilot_warm_up(embed_ast_conf, wpauths)
    )

    db_interface = EmbedsMultiSchema(cur_dump)
    videos_uploaded: int = 0

    # You can keep on getting posts until this variable is equal to one.
    total_elems: int = len(not_published)
    logging.info(f"Detected {total_elems} to be published for {partner}")

    helpers.clean_console()

    # Styles
    user_default = cs.ConsoleStyle.TEXT_STYLE_DEFAULT.value
    user_default_bold = cs.ConsoleStyle.TEXT_STYLE_DEFAULT_BOLD.value
    user_attention = cs.ConsoleStyle.TEXT_STYLE_ATTENTION.value
    user_warning = cs.ConsoleStyle.TEXT_STYLE_WARN.value
    user_prompt = cs.ConsoleStyle.TEXT_STYLE_PROMPT.value
    user_special_prompt = cs.ConsoleStyle.TEXT_STYLE_SPECIAL_PROMPT.value

    cs.iter_session_print(console, total_elems, partner)
    time.sleep(2)
    for num, vid in enumerate(not_published):
        db_interface.load_data_instance(vid)
        logging.info(f"Displaying on iteration {num} data: {vid}")

        helpers.clean_console()

        cs.iter_session_print(console, videos_uploaded)

        for field in db_interface.get_fields(keep_indx=True):
            num, fld = field
            if re.match(db_interface.SchemaRegEx.pat_duration, fld):
                hs, mins, secs = helpers.get_duration(int(db_interface.get_duration()))
                console.print(
                    f"{num + 1}. Duration: \n\tHours: [bold red]{hs}[/bold red] \n\tMinutes: [bold red]{mins}[/bold red] \n\tSeconds: [bold red]{secs}[/bold red]",
                    style=user_default_bold,
                )  # From seconds to hours to minutes
            else:
                console.print(
                    f"{num + 1}. {fld.title()}: {vid[num]}", style=user_default
                )

        add_post = console.input(
            f"[{user_prompt}]\nAdd post to WP? -> Y/N/ENTER to review next post: [/{user_prompt}]\n"
        ).lower()
        if add_post == ("y" or "yes"):
            logging.info(f"User accepted video element {num} for processing")
            add_post = True
        elif add_post == ("n" or "no"):
            logging.info("User declined further activity with the bot")
            thumbnails_dir.cleanup()
            time_end = time.time()
            h, mins, secs = helpers.get_duration(time_end - time_start)
            cs.terminate_loop_logging(
                console,
                num,
                total_elems,
                videos_uploaded,
                (h, mins, secs),
                exhausted=False,
            )
        else:
            if num < total_elems - 1:
                logging.info(
                    f"Moving forward - ENTER action detected. State: num={num} total_elems={total_elems}"
                )
                pyclip.detect_clipboard()
                pyclip.clear()
                continue
            else:
                logging.info(
                    f"List exhausted. State: num={num} total_elems={total_elems}"
                )
                thumbnails_dir.cleanup()
                time_end = time.time()
                h, mins, secs = helpers.get_duration(time_end - time_start)
                cs.terminate_loop_logging(
                    console,
                    num,
                    total_elems,
                    videos_uploaded,
                    (h, mins, secs),
                    exhausted=True,
                )
        if add_post:
            models = (
                girl
                if (girl := db_interface.get_models())
                else db_interface.get_pornstars()
            )

            slugs = [
                f"{slug}" if (slug := db_interface.get_slug()) else "",
                cs.make_slug(
                    partner, models, (title := db_interface.get_title()), "video"
                ),
                cs.make_slug(partner, models, title, "video", reverse=True),
                cs.make_slug(
                    partner, models, title, "video", studio=db_interface.get_studio()
                ),
                cs.make_slug(
                    partner,
                    models,
                    title,
                    "video",
                    studio=db_interface.get_studio(),
                    partner_out=True,
                ),
                cs.make_slug(
                    partner,
                    None,
                    title,
                    "video",
                    studio=db_interface.get_studio(),
                    partner_out=True,
                ),
            ]

            clean_slugs = list(filter(lambda sl: sl != "", slugs))

            wp_slug = cs.slug_getter(console, clean_slugs)

            logging.info(f"WP Slug - Selected: {wp_slug}")

            # Making sure there aren't spaces in tags and exclude the word
            # `asian` and `japanese` from tags since I want to make them more general.
            tag_prep = filter_tags(
                categories
                if (categories := db_interface.get_categories())
                else db_interface.get_tags(),
                ["asian", "japanese"],
            )
            # Default tag per partner
            if partner == "abjav" or partner == "vjav":
                tag_prep.append("japanese")
            elif partner == "Desi Tube":
                tag_prep.append("indian")

            tag_ints = cs.tag_checker_print(console, wp_posts_f, tag_prep)

            models_field = (
                pornstars
                if (pornstars := db_interface.get_pornstars())
                else db_interface.get_models()
            )

            if models_field:
                models_prep = filter_tags(models_field)
                model_ints: Optional[list[int]] = cs.model_checker(
                    wp_posts_f, models_prep
                )
            else:
                model_ints = None

            # Video category NaiveBayes/MaxEnt Classifiers
            categ_ids = cs.pick_classifier(
                console,
                wp_posts_f,
                db_interface.get_title(),
                db_interface.get_description(),
                db_interface.get_tags(),
            )
            category = categ_ids

            console.print("\n--> Making payload...", style=user_default_bold)
            payload = cs.make_payload_simple(
                wp_slug,
                wpauths.default_status,
                title,
                db_interface.get_description(),
                tag_ints,
                model_int_lst=model_ints,
                categs=category,
            )
            logging.info(f"Generated payload: {payload}")

            console.print("--> Fetching thumbnail...", style=user_default_bold)

            pic_format = (
                embed_ast_conf.pic_format
                if embed_ast_conf.imagick
                else embed_ast_conf.pic_fallback
            )
            thumbnail = clean_filename(wp_slug, pic_format)
            logging.info(f"Thumbnail name: {thumbnail}")

            try:
                cs.fetch_thumbnail(
                    thumbnails_dir.name,
                    wp_slug,
                    db_interface.get_thumbnail(),
                )
                console.print(
                    f"--> Stored thumbnail {thumbnail} in cache folder {os.path.relpath(thumbnails_dir.name)}",
                    style=user_default_bold,
                )
                console.print(
                    "--> Uploading thumbnail to WordPress Media...",
                    style=user_default_bold,
                )
                console.print(
                    "--> Adding image attributes on WordPress...",
                    style=user_default_bold,
                )
                img_attrs = cs.make_img_payload(title, db_interface.get_description())
                logging.info(f"Image Attrs: {img_attrs}")
                upload_img = wordpress_api.upload_thumbnail(
                    wpauths.api_base_url,
                    [wp_endpoints.media],
                    f"{os.path.join(thumbnails_dir.name, thumbnail)}",
                    img_attrs,
                )

                # Sometimes, the function fetch image will fetch an element that is not a thumbnail.
                # upload_thumbnail will report a 500 status code when this is the case.
                # More information in integrations.wordpress_api.upload_thumbnail docs
                if upload_img == 500:
                    logging.warning("Defective thumbnail - Bot abandoned current flow.")
                    console.print(
                        "It is possible that this thumbnail is defective. Check the Thumbnail manually.",
                        style=user_warning,
                    )
                    console.print(
                        "--> Proceeding to the next post...\n", style=user_default_bold
                    )
                    continue
                elif upload_img == (200 or 201):
                    os.remove(
                        removed_img := f"{os.path.join(thumbnails_dir.name, thumbnail)}"
                    )
                    logging.info(f"Uploaded and removed: {removed_img}")

                console.print(
                    f"--> WordPress Media upload status code: {upload_img}",
                    style=user_default_bold,
                )
                console.print("--> Creating post on WordPress", style=user_default_bold)

                push_post = wordpress_api.wp_post_create([wp_endpoints.posts], payload)
                logging.info(f"WordPress post push status: {push_post}")
                console.print(
                    f"--> WordPress status code: {push_post}", style=user_default_bold
                )

                pyclip.detect_clipboard()
                pyclip.copy(db_interface.get_embed())
                pyclip.copy(title)
                console.print(
                    "--> Check the post and paste all you need from your clipboard.",
                    style=user_default_bold,
                )
                cs.social_sharing_controller(
                    console, db_interface.get_description(), wp_slug, embed_ast_conf
                )
                videos_uploaded += 1
            except (SSLError, ConnectionError) as e:
                logging.warning(f"Caught exception {e!r} - Prompting user")
                pyclip.detect_clipboard()
                pyclip.clear()
                console.print(
                    "* There was a connection error while processing this post. Check the logs for details. *",
                    style=user_warning,
                )
                is_published = (
                    True if wp_slug == os.environ.get("LATEST_POST") else False
                )
                console.print(
                    f"Post {wp_slug} was {'' if is_published else 'NOT'} published!",
                    style=user_warning,
                )
                if console.input(
                    f"\n[{user_prompt}] Do you want to continue? Y/ENTER to exit: [{user_prompt}]"
                ) == ("y" or "yes"):
                    logging.info(f"User accepted to continue after catching {e!r}")

                    if is_published:
                        videos_uploaded += 1

                    continue
                else:
                    logging.info(f"User declined after catching {e!r}")

                    if is_published:
                        videos_uploaded += 1

                    console.print(
                        f"You have created {videos_uploaded} posts in this session!",
                        style=user_attention,
                    )
                    cur_dump.close()
                    thumbnails_dir.cleanup()
                    time_end = time.time()
                    h, mins, secs = helpers.get_duration(time_end - time_start)
                    cs.terminate_loop_logging(
                        console,
                        num,
                        total_elems,
                        videos_uploaded,
                        (h, mins, secs),
                        exhausted=False,
                    )
                    logging.shutdown()
                    break
            if num < total_elems - 1:
                next_post = console.input(
                    f"[{user_prompt}]\nNext post? -> N/ENTER to review next post: [/{user_prompt}]\n"
                ).lower()
                if next_post == ("n" or "no"):
                    logging.info("User declined further activity with the bot")
                    cur_dump.close()
                    thumbnails_dir.cleanup()
                    time_end = time.time()
                    h, mins, secs = helpers.get_duration(time_end - time_start)
                    cs.terminate_loop_logging(
                        console,
                        num,
                        total_elems,
                        videos_uploaded,
                        (h, mins, secs),
                        exhausted=False,
                    )
                else:
                    logging.info(
                        "User accepted to continue after successful post creation."
                    )
                    pyclip.detect_clipboard()
                    pyclip.clear()
            else:
                cur_dump.close()
                thumbnails_dir.cleanup()
                time_end = time.time()
                h, mins, secs = helpers.get_duration(time_end - time_start)
                cs.terminate_loop_logging(
                    console,
                    num,
                    total_elems,
                    videos_uploaded,
                    (h, mins, secs),
                    exhausted=True,
                )
        else:
            cur_dump.close()
            thumbnails_dir.cleanup()
            time_end = time.time()
            h, mins, secs = helpers.get_duration(time_end - time_start)
            cs.terminate_loop_logging(
                console,
                num,
                total_elems,
                videos_uploaded,
                (h, mins, secs),
                exhausted=True,
            )


def main():
    try:
        if os.name == "posix":
            import readline

        embedding_pilot()
    except KeyboardInterrupt:
        logging.critical("KeyboardInterrupt exception detected")
        logging.info("Cleaning clipboard and temporary directories. Quitting...")
        print("Goodbye! ಠ‿↼")
        pyclip.detect_clipboard()
        pyclip.clear()
        logging.shutdown()
        # When quit is called, temp dirs will be automatically cleaned.
        quit()


if __name__ == "__main__":
    main()
