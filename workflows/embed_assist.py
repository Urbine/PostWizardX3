"""
Video embedding assistant.
Embed_assist works with the result of different integrations, which retrieve metadata from a remote content partner.
However, it is a specialized version of ``workflows.content_select`` and it deals with less structured data.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

# Std Library
import os
import pyclip
from requests.exceptions import ConnectionError, SSLError
import readline
import sys
import time


# Local implementations
from core import helpers
import workflows.content_select as cs
from core.config_mgr import (embed_assist_conf,
                             wp_auth)

from integrations import wordpress_api, WPEndpoints
from ml_engine import classify_title, classify_description


def filter_tags(tgs: str, filter_lst: list[str]) -> list[str]:
    """ Remove redundant words found in tags and return a clear list of unique filtered tags.

    :param tgs: ``list[str]`` tags to be filtered
    :param filter_lst: ``list[str]`` lookup list of words to be removed
    :return: ``list[str]``
    """
    t_split = tgs.split(",")
    new_set = set({})
    for tg in t_split:
        temp_lst = []
        sublist = tg.split(" ")
        for word in sublist:
            if word not in filter_lst:
                temp_lst.append(word)
            else:
                continue
        new_set.add(" ".join(temp_lst))
    return list(new_set)


def filter_published_embeds(
        wp_posts_f: list[dict[str, ...]], videos: list[tuple[str, ...]]
) -> list[tuple[str, ...]]:
    """filter_published does its filtering work based on the published_json function.
    It is based on a similar version from module `content_select`, however, this one is adapted to embedded videos
    and a different db schema.

    This function does not need a lot of explanation, it takes in a list of tuples and iterates over them.
    By unpacking one of its core values, it carries out the manual classification to generate a new set of
    titles.

    :param videos: ``list[tuple[str, ...]]`` usually resulting from the SQL database query values.
    :param wp_posts_f: ``list[dict[str, ...]]`` WordPress Post Information case file (previously loaded and ready to process)
    :return: ``list[tuple[str, ...]]`` with the new filtered values.
    """
    # This loop gets the items I am interested in.
    post_titles: list[str] = wordpress_api.get_post_titles_local(
        wp_posts_f, yoast=True)

    not_published: list[tuple] = []
    for elem in videos:
        vid_id, vid_title, *fields = elem
        if vid_title in post_titles:
            continue
        else:
            not_published.append(elem)
    return not_published


def embedding_pilot(
        embed_ast_conf = embed_assist_conf(),
        wp_auth = wp_auth(),
        wp_endpoints: WPEndpoints = WPEndpoints,
        parent: bool = False,
) -> None:
    """
    Assist the user in video embedding from the information originated from local
    implementations of Japanese adult content providers in the ``integrations`` package.

    :param embed_ast_conf: ``EmbedAssistConf`` Object with configuration info for this bot.
    :param wp_auth: ``WPAuth`` object that contains configuration of your site.
    :param wp_endpoints: ``WPEndpoints`` object with the integration endpoints for WordPress.
    :param parent: ``bool`` defines whether internal folder references relative to the child directory.
    :return: ``None``
    """
    print("\n==> Warming up... ┌(◎_◎)┘ ")
    cs.hot_file_sync(bot_config=embed_ast_conf)
    wp_posts_f = helpers.load_json_ctx(embed_ast_conf.wp_json_posts)
    partner_list = embed_ast_conf.partners.split(',')
    os.system('clear')
    db_conn, cur_dump, db_dump_name, partner_indx = cs.content_select_db_match(
        partner_list, embed_ast_conf.content_hint
    )
    wp_base_url = wp_auth.api_base_url
    videos_uploaded: int = 0
    partner = partner_list[partner_indx]
    cs.select_guard(db_dump_name, partner)
    all_vals: list[tuple[str]] = helpers.fetch_data_sql(
        embed_ast_conf.sql_query, cur_dump)
    not_published_yet = filter_published_embeds(wp_posts_f, all_vals)
    total_elems = len(not_published_yet)
    for num, vid in enumerate(not_published_yet):
        id_ = vid[0]
        title = vid[1]
        duration = vid[2]
        date = vid[3]
        categories = vid[4]
        rating = vid[5]
        main_thumbnail_name = vid[6]
        embed_code = vid[7]
        web_link = vid[8]
        wp_slug = vid[9]
        print(f"\n{'Review the following video':*^30}\n")
        print(f"ID: {id_}")
        print(f"Title: {title}")
        print(f"Web Link: {web_link}")
        hs, mins, secs = helpers.get_duration(int(duration))
        print(
            f"Duration: \nHours: {hs} \nMinutes: {mins} \nSeconds: {secs}"
        )  # From seconds to hours to minutes
        print(f"Rating: {rating}")
        print(f"Date: {date}")
        print(f"Tags: {categories}")
        print(f"WP Slug: {wp_slug}")
        add_post = input(
            "\nAdd post to WP? -> Y/N/ENTER to review next post: ").lower()
        if add_post == ("y" or "yes"):
            add_post = True
        elif add_post == ("n" or "no"):
            pyclip.detect_clipboard()
            pyclip.clear()
            print(f"You have created {videos_uploaded} posts in this session!")
            break
        else:
            if num < total_elems - 1:
                pyclip.detect_clipboard()
                pyclip.clear()
                continue
            else:
                pyclip.detect_clipboard()
                pyclip.clear()
                print("\nWe have reviewed all posts for this query.")
                print("Try a different SQL query or partner. I am ready when you are. ")
                print(
                    f"You have created {videos_uploaded} posts in this session!")
                break
        if add_post:
            slugs = [
                f"{wp_slug}",
                cs.make_slug(
                    partner,
                    None,
                    title,
                    "video"),
                cs.make_slug(
                    partner,
                    None,
                    title,
                    "video",
                    reverse=True)
            ]
            print("\n--> Available slugs:")

            for n, slug in enumerate(slugs, start=1):
                print(f"{n}. -> {slug}")
            print("Select 4 to enter a custom slug.")

            match input("\nSelect your slug: "):
                case "1":
                    wp_slug = slugs[0]
                case "2":
                    wp_slug = slugs[1]
                case "3":
                    wp_slug = slugs[2]
                case "4":
                    pyclip.copy(slugs[0])
                    print("Enter your slug now: ")
                    wp_slug = sys.stdin.readline().strip('\n')
                case _:
                    # Parsing slug by default.
                    wp_slug = slugs[0]

            # Making sure there aren't spaces in tags and exclude the word
            # `asian` and `japanese` from tags since I want to make the more general.
            tag_prep = filter_tags(categories, ["asian", "japanese"])
            # Default tag per partner
            if partner == 'abjav' or partner == 'vjav':
                tag_prep.append('japanese')
            elif partner == 'Desi Tube':
                tag_prep.append('indian')
            else:
                pass
            tag_ints = cs.get_tag_ids(wp_posts_f, tag_prep, 'tags')
            all_tags_wp = wordpress_api.tag_id_merger_dict(wp_posts_f)
            tag_check = cs.identify_missing(
                all_tags_wp, tag_prep, tag_ints, ignore_case=True
            )

            if tag_check is None:
                # All tags have been found and mapped to their IDs.
                pass
            else:
                # You've hit a snag.
                for tag in tag_check:
                    if tag != '' or tag is None:
                        print(f"ATTENTION --> Tag: {tag} not on WordPress.")
                        print("--> Copying missing tag to your system clipboard.")
                        print("Paste it into the tags field as soon as possible...\n")
                        pyclip.detect_clipboard()
                        pyclip.copy(tag)
                    else:
                        pass

            class_title = classify_title(title)
            class_tags = classify_description(categories)
            class_title.union(class_tags)
            consolidate_categs = list(class_title)

            print(" \n** I think these categories are appropriate: **\n")
            for num, categ in enumerate(consolidate_categs, start=1):
                print(f"{num}. {categ}")

            match input("\nEnter the category number or type in to look for another category in the site: "):
                case _ as option:
                    try:
                        sel_categ = consolidate_categs[int(option) - 1]
                    except (ValueError or IndexError):
                        sel_categ = option

            categ_ids = cs.get_tag_ids(
                wp_posts_f, [sel_categ], preset="categories")
            if not sel_categ:
                # 38 is Japanese Amateur Porn
                # 40 is Indian Amateur Porn
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

            print("\n--> Making payload...")
            payload = cs.make_payload_simple(
                wp_slug,
                wp_auth.default_status,
                title,
                title,
                tag_ints,
                categs=category,
            )
            print("--> Fetching thumbnail...")
            try:
                thumbnail_full = main_thumbnail_name
                cs.fetch_thumbnail(
                    embed_ast_conf.thumbnail_dir, wp_slug, thumbnail_full)
                print(
                    f"--> Stored thumbnail {wp_slug}.jpg in cache folder ../thumbnails")
                print("--> Uploading thumbnail to WordPress Media...")
                print("--> Adding image attributes on WordPress...")
                img_attrs = cs.make_img_payload(title, title)
                is_parent = helpers.is_parent_dir_required(parent=parent)
                upload_img = wordpress_api.upload_thumbnail(
                    wp_base_url, [
                        "/media"], f"{is_parent}{embed_ast_conf.thumbnail_dir}/{wp_slug}.jpg", img_attrs
                )

                # Sometimes, the function fetch image will fetch an element that is not a thumbnail.
                # upload_thumbnail will report a 500 status code when this is the
                # case.
                if upload_img == 500:
                    print(
                        "It is possible that this thumbnail is defective. Check the Thumbnail manually."
                    )
                    print("--> Proceeding to the next post...\n")
                    continue
                elif upload_img == (200 or 201):
                    os.remove(
                        f"{is_parent}{embed_ast_conf.thumbnail_dir}/{wp_slug}.jpg")
                else:
                    pass

                print(
                    f"--> WordPress Media upload status code: {upload_img}")
                print("--> Creating post on WordPress")
                push_post = wordpress_api.wp_post_create(
                    [wp_endpoints.posts], payload)
                print(f"--> WordPress status code: {push_post}")
                # Copy important information to the clipboard.
                # Some tag strings end with ';'
                pyclip.detect_clipboard()
                pyclip.copy(embed_code)
                pyclip.copy(title)
                print(
                    "--> Check the post and paste all you need from your clipboard.")
                videos_uploaded += 1
            except SSLError:
                pyclip.detect_clipboard()
                pyclip.clear()
                print("* There was a connection error while processing this post... *")
                if input("\nDo you want to continue? Y/N/ENTER to exit: ") == (
                        "y" or "yes"
                ):
                    continue
                else:
                    print(
                        f"You have created {videos_uploaded} posts in this session!")
                    break
            if num < total_elems - 1:
                next_post = input(
                    "\nNext post? -> Y/N/ENTER to review next post: ").lower()
                if next_post == ("y" or "yes"):
                    # Clears clipboard after every video.
                    pyclip.clear()
                    print("\n==> Syncing and caching changes... ε= ᕕ(⎚‿⎚)ᕗ")
                    try:
                        sync = cs.hot_file_sync(bot_config=embed_ast_conf)
                    except ConnectionError:
                        print("Hot File Sync encountered a ConnectionError.")
                        print(
                            "Going to next post. I will fetch your changes in a next try."
                        )
                        print("If you want to update again, relaunch the bot.")
                        sync = True
                    if sync:
                        continue
                    else:
                        print(
                            """ERROR: WP JSON Sync failed. Look at the files.
                            Maybe you have to rollback your WordPress cache.
                            Run: python3 -m integrations.wordpress_api --posts""")
                elif next_post == ("n" or "no"):
                    # The terminating parts add this function to avoid tracebacks
                    # from pyclip
                    pyclip.detect_clipboard()
                    pyclip.clear()
                    print(
                        f"You have created {videos_uploaded} posts in this session!")
                    break
                else:
                    pyclip.detect_clipboard()
                    pyclip.clear()
                    continue
            else:
                # Since we ran out of elements the script will end after adding it to WP
                # So that it doesn't clear the clipboard automatically.
                print("\nWe have reviewed all posts for this query.")
                print("Try a different query and run me again.")
                print(
                    f"You have created {videos_uploaded} posts in this session!")
                print(
                    "Waiting for 60 secs to clear the clipboard before you're done with the last post..."
                )
                time.sleep(60)
                pyclip.detect_clipboard()
                pyclip.clear()
                break
        else:
            pyclip.detect_clipboard()
            pyclip.clear()
            print("\nWe have reviewed all posts for this query.")
            print("Try a different SQL query or partner. I am ready when you are. ")
            print(f"You have created {videos_uploaded} posts in this session!")
            break


if __name__ == '__main__':
    embedding_pilot()
