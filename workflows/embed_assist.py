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
import readline  # Imported to enable Standard Input manipulation. Don't remove!
import sqlite3
import tempfile
import time

from re import Pattern
from dataclasses import dataclass, fields
from sqlite3 import OperationalError

# Third-party modules
import pyclip
from requests.exceptions import SSLError, ConnectionError
from rich.console import Console

# Local implementations
from core import helpers, embed_assist_conf, wp_auth, x_auth, clean_filename, InvalidDB
from integrations import wordpress_api, x_api, WPEndpoints, XEndpoints
from ml_engine import classify_title, classify_description
import workflows.content_select as cs


class EmbedsMultiSchema:
    """
    Complementary class dealing with dynamic SQL schema reading for content databases.

    EmbedsMultiSchema provides an interface to the main control flow of the bot that allows
    for direct index probing based on the present schema. This improvement will make it easier to
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
            schema = helpers.fetch_data_sql(query, db_cur)
            fst_table, *others = schema

            if others:
                logging.warning(
                    "Detected db with more than one table, fetching the first one by default."
                )
            else:
                pass

            table_name = fst_table[0].split(" ")[2].split("(")[0]
            query = "PRAGMA table_info({})".format(table_name)
            schema = helpers.fetch_data_sql(query, db_cur)
            fields_ord = list(map(lambda lstpl: lstpl[0:2], schema))

            return table_name, fields_ord

        except OperationalError:
            logging.critical(
                "db file was not found. Raising InvalidDB exception and quitting..."
            )
            raise InvalidDB

    def __init__(self, db_cur: sqlite3):
        schema = self.get_schema(db_cur)
        self.table_name: str = schema[0]
        self.__fields_indx = schema[1]
        self.__fields: list[str] = list(map(lambda tpl: tpl[1], self.__fields_indx))
        self.field_count: int = len(self.__fields)

    def get_fields(self, keep_indx: bool = False):
        if keep_indx:
            return self.__fields_indx
        else:
            return self.__fields

    def get_slug(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_slug
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_embed(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_embed
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_thumbnail(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_thumbnail
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_categories(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_categories
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_rating(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_rating
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_title(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_title
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_link(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_link
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_date(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_date
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_id(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_id
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_duration(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_duration
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_pornstars(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_prnstars
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_models(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_models
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_resolution(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_resolution
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_tags(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_tags
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_likes(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_likes
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_url(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_url
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_description(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_description
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_studio(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_studio
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_trailer(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_trailer
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches

    def get_orientation(self) -> int:
        re_pattern: Pattern[str] = EmbedsMultiSchema.SchemaRegEx.pat_orientation
        matches = helpers.match_list_single(re_pattern, self.__fields)
        return matches


def filter_tags(tgs: str, filter_lst: list[str] | None = None) -> list[str] | None:
    """Remove redundant words found in tags and return a clear list of unique filtered tags.

    :param tgs: ``list[str]`` tags to be filtered
    :param filter_lst: ``list[str]`` lookup list of words to be removed
    :return: ``list[str]``
    """
    if tgs is None:
        return None

    spl_char = (
        lambda tag: chars[1]
        if (chars := re.findall(r"[\W_]+", tag))
        else chars[0]
        if chars
        else " "
    )
    t_split = tgs.split(spl_char(tgs))
    new_set = set({})
    for tg in t_split:
        temp_lst = []
        sublist = tg.split(" ")
        for word in sublist:
            if filter_lst is None:
                temp_lst.append(word)
                continue
            elif word not in filter_lst:
                temp_lst.append(word)
            else:
                continue
        new_set.add(" ".join(temp_lst))
    return list(new_set)


def filter_published_embeds(
    wp_posts_f: list[dict[str, ...]], videos: list[tuple[str, ...]], db_cur: sqlite3
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
        vid_title = elem[db_interface.get_title()]
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

    cs.logging_setup(embed_ast_conf, __file__)
    logging.info(f"Started Session ID: {os.environ.get('SESSION_ID')}")

    console = Console()
    os.system("clear")
    with console.status(
        "[bold green] Warming up... [blink]┌(◎_◎)┘[/blink] [/bold green]\n",
        spinner="aesthetic",
    ):
        cs.hot_file_sync(bot_config=embed_ast_conf)
        x_api.refresh_flow(x_auth(), XEndpoints())

    wp_posts_f = helpers.load_json_ctx(embed_ast_conf.wp_json_posts)
    logging.info(f"Reading WordPress Post cache: {embed_ast_conf.wp_json_posts}")

    partner_list = list(map(lambda p: p.strip(), embed_ast_conf.partners.split(",")))
    os.system("clear")
    logging.info(f"Loading partners variable: {partner_list}")

    db_conn, cur_dump, db_dump_name, partner_indx = cs.content_select_db_match(
        partner_list, embed_ast_conf.content_hint
    )
    db_interface = EmbedsMultiSchema(cur_dump)

    wp_base_url = wpauths.api_base_url
    logging.info(f"Using {wp_base_url} as WordPress API base url")

    videos_uploaded: int = 0
    partner = partner_list[partner_indx]
    logging.info(f"Matched {db_dump_name} for {partner} index {partner_indx}")
    cs.select_guard(db_dump_name, partner)
    logging.info("Select guard cleared...")

    all_vals: list[tuple[str]] = helpers.fetch_data_sql(
        embed_ast_conf.sql_query, cur_dump
    )
    logging.info(f"{len(all_vals)} elements found in database {db_dump_name}")
    not_published_yet = filter_published_embeds(wp_posts_f, all_vals, cur_dump)
    total_elems = len(not_published_yet)
    logging.info(f"Detected {total_elems} to be published")
    os.system("clear")
    # Environment variable set in logging_setup() - content_select.py
    console.print(
        f"Session ID: {os.environ.get('SESSION_ID')}",
        style="bold yellow",
        justify="left",
    )
    console.print(
        f"\nThere are {total_elems} videos to be published...",
        style="bold red",
        justify="center",
    )
    time.sleep(2)
    thumbnails_dir = tempfile.TemporaryDirectory(prefix="thumbs", dir=".")
    logging.info(f"Created {thumbnails_dir.name} for thumbnail temporary storage")
    for num, vid in enumerate(not_published_yet):
        logging.info(f"Displaying on iteration {num} data: {vid}")
        os.system("clear")
        console.print(
            f"Session ID: {os.environ.get('SESSION_ID')}",
            style="bold yellow",
            justify="left",
        )
        console.print(
            f"\n{'Review the following video':*^30}\n",
            style="bold yellow",
            justify="center",
        )

        for field in db_interface.get_fields(keep_indx=True):
            num, fld = field
            if re.match(db_interface.SchemaRegEx.pat_duration, fld):
                hs, mins, secs = helpers.get_duration(int(vid[num]))
                console.print(
                    f"{num + 1}. Duration: \n\tHours: [bold red]{hs}[/bold red] \n\tMinutes: [bold red]{mins}[/bold red] \n\tSeconds: [bold red]{secs}[/bold red]",
                    style="bold green",
                )  # From seconds to hours to minutes
                continue
            else:
                console.print(f"{num + 1}. {fld.title()}: {vid[num]}", style="green")

        add_post = console.input(
            "[bold yellow]\nAdd post to WP? -> Y/N/ENTER to review next post: [/bold yellow]\n"
        ).lower()
        if add_post == ("y" or "yes"):
            logging.info(f"User accepted video element {num} for processing")
            add_post = True
        elif add_post == ("n" or "no"):
            logging.info("User declined further activity with the bot")
            pyclip.detect_clipboard()
            pyclip.clear()
            console.print(
                f"You have created {videos_uploaded} posts in this session!",
                style="bold magenta",
            )
            thumbnails_dir.cleanup()
            time_end = time.time()
            h, mins, secs = helpers.get_duration(time_end - time_start)
            logging.info(
                f"User created {videos_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
            )
            logging.shutdown()
            break
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
                pyclip.detect_clipboard()
                pyclip.clear()
                console.print(
                    "\nWe have reviewed all posts for this query.", style="bold red"
                )
                console.print(
                    "Try a different SQL query or partner. I am ready when you are. ",
                    style="bold red",
                )
                console.print(
                    f"You have created {videos_uploaded} posts in this session!",
                    style="bold magenta",
                )
                thumbnails_dir.cleanup()
                time_end = time.time()
                h, mins, secs = helpers.get_duration(time_end - time_start)
                logging.info(
                    f"User created {videos_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
                )
                logging.info(
                    "Cleaning clipboard and temporary directories. Quitting..."
                )
                logging.shutdown()
                break
        if add_post:
            slugs = [
                f"{slug}" if (slug := db_interface.get_slug()) else "",
                cs.make_slug(
                    partner, None, (title := vid[db_interface.get_title()]), "video"
                ),
                cs.make_slug(partner, None, title, "video", reverse=True),
            ]
            console.print("\n--> Available slugs:", style="bold yellow")

            total_slugs = 1
            for slug in slugs:
                if slug:
                    console.print(f"{total_slugs}. -> {slug}", style="bold green")
                    total_slugs += 1
                else:
                    continue

            real_slug_count = len(list(filter(lambda sl: sl != "", slugs)))
            console.print(
                f"Select {real_slug_count + 1} to enter a custom slug.",
                style="bold yellow",
            )

            slug_sel = console.input(
                "[bold yellow]\n--> Select your slug: [/bold yellow]\n"
            )
            try:
                wp_slug = slugs[int(slug_sel)]
            except (IndexError, ValueError):
                slug_sel = total_slugs + 1
                if int(slug_sel) == (total_slugs + 1):
                    # Parsing slug by default.
                    wp_slug = slugs[0]
                    pyclip.copy(slugs[0])
                    console.print("Enter your slug now: ", style="bold yellow")
                    wp_slug = input()
                    while wp_slug == "" or wp_slug == " " or wp_slug is None:
                        console.print("Enter your slug now: ", style="bold yellow")
                        wp_slug = input()

            logging.info(f"WP Slug - Selected: {wp_slug}")

            # Making sure there aren't spaces in tags and exclude the word
            # `asian` and `japanese` from tags since I want to make them more general.
            tag_prep = filter_tags(
                (categories := vid[db_interface.get_categories()]),
                ["asian", "japanese"],
            )
            # Default tag per partner
            if partner == "abjav" or partner == "vjav":
                tag_prep.append("japanese")
            elif partner == "Desi Tube":
                tag_prep.append("indian")
            else:
                pass
            tag_ints = cs.get_tag_ids(wp_posts_f, tag_prep, "tags")
            all_tags_wp = wordpress_api.tag_id_merger_dict(wp_posts_f)
            tag_check = cs.identify_missing(
                all_tags_wp, tag_prep, tag_ints, ignore_case=True
            )

            if tag_check is None:
                # All tags have been found and mapped to their IDs.
                pass
            else:
                for tag in tag_check:
                    if tag != "" or tag is None:
                        console.print(
                            f"ATTENTION --> Tag: {tag} not on WordPress.",
                            style="bold red",
                        )
                        console.print(
                            "--> Copying missing tag to your system clipboard.",
                            style="bold yellow",
                        )
                        console.print(
                            "Paste it into the tags field as soon as possible...\n",
                            style="bold yellow",
                        )
                        logging.warning(f"Missing tag detected: {tag}")
                        pyclip.detect_clipboard()
                        pyclip.copy(tag)
                    else:
                        pass

            spl_char = (
                lambda tag: chars[1] if (chars := re.findall(r"\W", tag)) else chars[0]
            )
            models_field = (
                pornstars
                if (pornstars := vid[db_interface.get_pornstars()])
                else vid[db_interface.get_models()]
            )
            models_prep = filter_tags(models_field)

            # model_prep = (
            #     [model for model in models_spl]
            #     if models_field is not None
            #     else ["model-not-found"]
            # )

            model_ints: list[int] = cs.model_checker(wp_posts_f, models_prep)

            # Video category NaiveBayes/MaxEnt Classifiers
            class_title = classify_title(title)
            class_tags = classify_description(categories)
            class_title.union(class_tags)
            consolidate_categs = list(class_title)
            logging.info(f"Suggested categories ML: {consolidate_categs}")

            console.print(
                " \n** I think these categories are appropriate: **\n",
                style="bold yellow",
            )
            for numbr, categ in enumerate(consolidate_categs, start=1):
                console.print(f"{numbr}. {categ}", style="bold green")

            match console.input(
                "[bold yellow]\nEnter the category number or type in to look for another category in the site: [/bold yellow]\n"
            ):
                case _ as option:
                    try:
                        sel_categ = consolidate_categs[int(option) - 1]
                        logging.info(f"User selected category: {sel_categ}")
                    except (ValueError, IndexError):
                        sel_categ = option
                        logging.info(f"User typed in category: {option}")

            categ_ids = cs.get_tag_ids(wp_posts_f, [sel_categ], preset="categories")
            if not sel_categ:
                # In this site:
                # 38 is Japanese Amateur Porn
                # 40 is Indian Amateur Porn
                # Category numbers are not equal in all sites.
                match partner:
                    case "abjav":
                        category = [38]
                    case "vjav":
                        category = [38]
                    case "Desi Tube":
                        category = [40]
                    case _:
                        category = None
            else:
                category = categ_ids

            console.print("\n--> Making payload...", style="bold green")
            payload = cs.make_payload_simple(
                wp_slug,
                wpauths.default_status,
                title,
                title,
                tag_ints,
                model_int_lst=model_ints,
                categs=category,
            )
            logging.info(f"Generated payload: {payload}")

            console.print("--> Fetching thumbnail...", style="bold green")
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
                    vid[db_interface.get_thumbnail()],
                )
                console.print(
                    f"--> Stored thumbnail {thumbnail} in cache folder {os.path.relpath(thumbnails_dir.name)}",
                    style="bold green",
                )
                console.print(
                    "--> Uploading thumbnail to WordPress Media...", style="bold green"
                )
                console.print(
                    "--> Adding image attributes on WordPress...", style="bold green"
                )
                img_attrs = cs.make_img_payload(title, title)
                logging.info(f"Image Attrs: {img_attrs}")
                upload_img = wordpress_api.upload_thumbnail(
                    wp_base_url,
                    [wp_endpoints.media],
                    f"{thumbnails_dir.name}/{thumbnail}",
                    img_attrs,
                )

                # Sometimes, the function fetch image will fetch an element that is not a thumbnail.
                # upload_thumbnail will report a 500 status code when this is the
                # case.
                # More information in integrations.wordpress_api.upload_thumbnail docs
                if upload_img == 500:
                    logging.warning(
                        f"Defective thumbnail - Bot abandoned current flow."
                    )
                    console.print(
                        "It is possible that this thumbnail is defective. Check the Thumbnail manually.",
                        style="bold red",
                    )
                    console.print(
                        "--> Proceeding to the next post...\n", style="bold green"
                    )
                    continue
                elif upload_img == (200 or 201):
                    os.remove(removed_img := f"{thumbnails_dir.name}/{thumbnail}")
                    logging.info(f"Uploaded and removed: {removed_img}")
                else:
                    pass

                console.print(
                    f"--> WordPress Media upload status code: {upload_img}",
                    style="bold green",
                )
                console.print("--> Creating post on WordPress", style="bold green")
                push_post = wordpress_api.wp_post_create([wp_endpoints.posts], payload)
                logging.info(f"WordPress post push status: {push_post}")
                console.print(
                    f"--> WordPress status code: {push_post}", style="bold green"
                )
                # Some tag strings end with ';'
                pyclip.detect_clipboard()
                pyclip.copy(vid[db_interface.get_embed()])
                pyclip.copy(title)
                console.print(
                    "--> Check the post and paste all you need from your clipboard.",
                    style="bold green",
                )
                if (
                    embed_ast_conf.x_posting_enabled
                    or embed_ast_conf.telegram_posting_enabled
                ):
                    status_msg = "Checking WP status and preparing for social sharing."
                    with console.status(
                        f"[bold green]{status_msg} [blink]ε= ᕕ(⎚‿⎚)ᕗ[blink] [/bold green]\n",
                        spinner="earth",
                    ):
                        is_published = cs.wp_publish_checker(wp_slug, embed_ast_conf)
                    if is_published:
                        if embed_ast_conf.x_posting_enabled:
                            logging.info("X Posting - Enabled in workflows config")
                            if embed_ast_conf.x_posting_auto:
                                logging.info("X Posting Automatic detected in config")
                                # Environment "LATEST_POST" variable assigned in wp_publish_checker()
                                x_post_create = cs.x_post_creator(
                                    title, os.environ.get("LATEST_POST")
                                )
                            else:
                                post_text = console.input(
                                    "[bold yellow]Enter your additional X post text here or press enter to use default configs: [bold yellow]\n"
                                )
                                logging.info(
                                    f"User entered custom post text: {post_text}"
                                )
                                x_post_create = cs.x_post_creator(
                                    title,
                                    os.environ.get("LATEST_POST"),
                                    post_text=post_text,
                                )

                                # Copy custom post text for the following prompt
                                pyclip.detect_clipboard()
                                pyclip.copy(post_text)

                            if x_post_create == 201:
                                console.print(
                                    "--> Post has been published on WP and shared on X.\n",
                                    style="bold yellow",
                                )
                            else:
                                console.print(
                                    f"--> There was an error while trying to share on X.\n Status: {x_post_create}",
                                    style="bold red",
                                )

                        if embed_ast_conf.telegram_posting_enabled:
                            logging.info(
                                "Telegram Posting - Enabled in workflows config"
                            )
                            if embed_ast_conf.telegram_posting_auto:
                                logging.info(
                                    "Telegram Posting Automatic detected in config"
                                )
                                telegram_msg = cs.telegram_send_message(
                                    title,
                                    os.environ.get("LATEST_POST"),
                                    embed_ast_conf,
                                )
                            else:
                                post_text = console.input(
                                    "[bold yellow]Enter your additional Telegram message here or press enter to use default configs: [bold yellow]\n"
                                )
                                telegram_msg = cs.telegram_send_message(
                                    title,
                                    os.environ.get("LATEST_POST"),
                                    embed_ast_conf,
                                    msg_text=post_text,
                                )

                            if telegram_msg == 200:
                                console.print(
                                    # Env variable assigned in botfather_telegram.send_message()
                                    f"--> Message sent to Telegram {os.environ.get('T_CHAT_ID')}",
                                    style="bold yellow",
                                )
                            else:
                                console.print(
                                    f"--> There was an error while trying to communicate with Telegram.\n Status: {telegram_msg}",
                                    style="bold red",
                                )
                            logging.info(
                                f"Telegram message status code: {telegram_msg}"
                            )
                else:
                    pass
                videos_uploaded += 1
            except (SSLError, ConnectionError) as e:
                logging.warning(f"Caught exception {str(e)} - Prompting user")
                pyclip.detect_clipboard()
                pyclip.clear()
                console.print(
                    "* There was a connection error while processing this post... *",
                    style="bold red",
                )
                if console.input(
                    "\n[bold green] Do you want to continue? Y/ENTER to exit: [bold green]"
                ) == ("y" or "yes"):
                    logging.info(f"User accepted to continue after catching {str(e)}")
                    continue
                else:
                    logging.info(f"User declined after catching {str(e)}")
                    console.print(
                        f"You have created {videos_uploaded} posts in this session!",
                        style="bold yellow",
                    )
                    cur_dump.close()
                    thumbnails_dir.cleanup()
                    time_end = time.time()
                    h, mins, secs = helpers.get_duration(time_end - time_start)
                    logging.info(
                        f"User created {videos_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
                    )
                    logging.info(
                        "Cleaning clipboard and temporary directories. Quitting..."
                    )
                    logging.shutdown()
                    break
            if num < total_elems - 1:
                next_post = console.input(
                    "[bold yellow]\nNext post? -> N/ENTER to review next post: [/bold yellow]\n"
                ).lower()
                if next_post == ("n" or "no"):
                    logging.info("User declined further activity with the bot")
                    # The terminating parts add this function to avoid tracebacks from pyclip
                    pyclip.detect_clipboard()
                    pyclip.clear()
                    console.print(
                        f"You have created {videos_uploaded} posts in this session!",
                        style="bold yellow",
                    )
                    cur_dump.close()
                    thumbnails_dir.cleanup()
                    time_end = time.time()
                    h, mins, secs = helpers.get_duration(time_end - time_start)
                    logging.info(
                        f"User created {videos_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
                    )
                    logging.info(
                        "Cleaning clipboard and temporary directories. Quitting..."
                    )
                    logging.shutdown()
                    break
                else:
                    logging.info(
                        "User accepted to continue after successful post creation."
                    )
                    pyclip.detect_clipboard()
                    pyclip.clear()
                    continue
            else:
                logging.info(
                    f"List exhausted. State: num={num} total_elems={total_elems}"
                )
                console.print(
                    "\nWe have reviewed all posts for this query.", style="bold red"
                )
                console.print(
                    "Try a different query and run me again.", style="bold magenta"
                )
                console.print(
                    f"You have created {videos_uploaded} posts in this session!",
                    style="bold yellow",
                )
                cur_dump.close()
                thumbnails_dir.cleanup()
                time_end = time.time()
                h, mins, secs = helpers.get_duration(time_end - time_start)
                logging.info(
                    f"User created {videos_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
                )
                logging.info(
                    "Cleaning clipboard and temporary directories. Quitting..."
                )
                logging.shutdown()
        else:
            logging.info(f"List exhausted. State: num={num} total_elems={total_elems}")
            pyclip.detect_clipboard()
            pyclip.clear()
            console.print(
                "\nWe have reviewed all posts for this query.", style="bold red"
            )
            console.print(
                "Try a different SQL query or partner. I am ready when you are. ",
                style="bold magenta",
            )
            console.print(
                f"You have created {videos_uploaded} posts in this session!",
                style="bold yellow",
            )
            cur_dump.close()
            thumbnails_dir.cleanup()
            time_end = time.time()
            h, mins, secs = helpers.get_duration(time_end - time_start)
            logging.info(
                f"User created {videos_uploaded} posts in hours: {h} mins: {mins} secs: {secs}"
            )
            logging.info("Cleaning clipboard and temporary directories. Quitting...")
            logging.shutdown()
            break


def main():
    try:
        embedding_pilot()
    except KeyboardInterrupt:
        logging.critical(f"KeyboardInterrupt exception detected")
        logging.info("Cleaning clipboard and temporary directories. Quitting...")
        print("Goodbye! ಠ‿↼")
        pyclip.detect_clipboard()
        pyclip.clear()
        logging.shutdown()
        # When quit is called, temp dirs will be automatically cleaned.
        quit()


if __name__ == "__main__":
    main()
