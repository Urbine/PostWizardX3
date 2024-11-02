import pyclip
from requests.exceptions import ConnectionError, SSLError
import time

from itertools import chain

# Local implementations
import helpers
import content_select
import wordpress_api

db_partner_conn, db_partner_cur, db_partner_name = helpers.get_project_db(parent=True)

videos = helpers.get_from_db(db_partner_cur, '*', 'embeds')
wp_posts_f = helpers.load_json_ctx('wp_posts.json', parent=True)

partners = ['abjav']
partner = partners[0]


# Review the following video:
# 0. 353878
# 0. Uncensored X Personal Shooting]
# 0. <Description>
# 0. https://abjav.tube/video/353878/uncensored-x-personal-shooting4/?campaign_id=1291575419
# 0. 0.9263888888888889
# 0. 0
# 0. 2024-10-04
# 0. Asian,Big Tits,Brunette,Fetish,Hairy,Japanese,JAV Uncensored,MILF,Titty Fucking/Paizuri,Uncensored
# 0. <tags>
# 0. <model>
# 0. <iframe allowfullscreen="" frameborder="0" height="360" mozallowfullscreen="" msallowfullscreen="" oallowfullscreen="" src="https://abjav.tube/embed/353878/?campaign_id=1291575419" webkitallowfullscreen="" width="640"></iframe>
# 0. https://ii.abjav.com/contents/videos_screenshots/353000/353878/480x270/
# 0. 1.jpg
# 0. 1.jpg,2.jpg,3.jpg,4.jpg,5.jpg,6.jpg,7.jpg,8.jpg,9.jpg,10.jpg,11.jpg,12.jpg
# 0. https://vv2.abjav.com/c2/videos/353000/353878/353878_tr.mp4
# 0. abjav-uncensored-x-personal-shooting4-video

def filter_tags(tgs: str, filter_lst: list[str]):
    t_split = tgs.split(',')
    new_set = set({})
    for tg in t_split:
        temp_lst = []
        sublist = tg.split(' ')
        for word in sublist:
            if word not in filter_lst:
                temp_lst.append(word)
            else:
                continue
        new_set.add(' '.join(temp_lst))
    return list(new_set)

def filter_published_embeds(all_videos: list[tuple], wp_posts_f: list[dict]) -> list[tuple]:
    """filter_published does its filtering work based on the published_json function.
    It is based on a similar version from module `content_select`, however, this one is adapted to embedded videos
    and a different db schema.

    This function does not need a lot of explanation, it takes in a list of tuples and iterates over them.
    By unpacking one of its core values, it carries out the manual classification to generate a new set of
    titles.
    :param all_videos: List[tuple] usually resulting from the SQL database query values.
    :param wp_posts_f: WordPress Post Information case file (previously loaded and ready to process)
    :return: list[tuple] with the new filtered values.
    """
    # This loop gets the items I am interested in.
    not_published: list[tuple] = []
    for elem in all_videos:
        (vid_id, vid_title, *fields) = elem
        if content_select.published_json(vid_title, wp_posts_f):
            continue
        else:
            not_published.append(elem)
    return not_published

print('\n==> Warming up... ┌(◎_◎)┘ ')
content_select.hot_file_sync('wp_posts.json', 'posts_url', parent=True)
wp_base_url = "https://whoresmen.com/wp-json/wp/v2"
videos_uploaded = 0
all_vals: list[tuple[str]] = videos
not_published_yet = filter_published_embeds(all_vals, wp_posts_f)
total_elems = len(not_published_yet)
for num, vid in enumerate(videos):
    id_ = vid[0]
    title = vid[1]
    description = vid[2] if vid[2] != '' else vid[1]
    web_link = vid[3]
    duration = vid[4]
    rating = vid[5]
    date = vid[6]
    categories = vid[7]
    tags = vid[8] if vid[8] != '' else vid[7].lower()
    model = vid[9]
    embed_code = vid[10]
    thumbnail_prefix = vid[11]
    main_thumbnail_name = vid[12]
    thumbnails = vid[13]
    video_trailer = vid[14]
    wp_slug = vid[15]
    print(f"\n{'Review the following video':*^30}")
    print(f"Title: {title}")
    print(f"Description: {description}")
    hs, mins, secs = helpers.get_duration(int(duration))
    print(f"Duration: \nHours: {hs} \nMinutes: {mins} \nSeconds: {secs}")  # From seconds to hours to minutes
    print(f"Rating: {rating}")
    print(f"Date: {date}")
    print(f"Tags: {tags}")
    print(f"Models: {model}")
    print(f"Video Trailer: {video_trailer}")
    print(f"WP Slug: {wp_slug}")
    add_post = input('\nAdd post to WP? -> Y/N/ENTER to review next post: ').lower()
    if add_post == ('y' or 'yes'):
        add_post = True
    elif add_post == ('n' or 'no'):
        pyclip.detect_clipboard()
        pyclip.clear()
        print("\n--> Cleaning thumbnails cache now")
        content_select.clean_file_cache('thumbnails', '.jpg', parent=True)
        print(f'You have created {videos_uploaded} posts in this session!')
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
            print("\n--> Cleaning thumbnails cache now")
            content_select.clean_file_cache('thumbnails', '.jpg', parent=True)
            print(f'You have created {videos_uploaded} posts in this session!')
            break
    if add_post:
        slugs = [f'{wp_slug}', content_select.make_slug(partner, model, title, '')]
        print("\n--> Available slugs:")

        for n, slug in enumerate(slugs, start=1):
            print(f'{n}. -> {slug}')

        match input('\nSelect your slug: '):
            case '1':
                wp_slug = slugs[0]
            case '2':
                wp_slug = slugs[1]
            case _:
                # Parsing slug by default.
                wp_slug = slugs[0]

        print('\n--> Making payload...')
        # Making sure there aren't spaces in tags and exclude the word `asian`
        tag_prep = filter_tags(tags, ['asian', 'japanese'])
        tag_prep.append(partner.lower())
        tag_prep.append('japanese')
        print(tag_prep)
        tag_ints = content_select.get_tag_ids(wp_posts_f, tag_prep)
        all_tags_wp = wordpress_api.tag_id_merger_dict(wp_posts_f)
        tag_check = content_select.identify_missing(all_tags_wp, tag_prep,
                                                    tag_ints, ignore_case=True)
        if tag_check is None:
            # All tags have been found and mapped to their IDs.
            pass
        else:
            # You've hit a snag.
            for tag in tag_check:
                print(f'ATTENTION --> Tag: {tag} not on WordPress.')
                print('--> Copying missing tag to your system clipboard.')
                print("Paste it into the tags field as soon as possible...\n")
                pyclip.detect_clipboard()
                pyclip.copy(tag)

        model_prep = model.split(',')
        # The would-be `models_ints`
        calling_models = content_select.get_model_ids(wp_posts_f, model_prep)
        all_models_wp = wordpress_api.map_wp_class_id(wp_posts_f, 'pornstars', 'pornstars')
        new_models = content_select.identify_missing(all_models_wp, model_prep, calling_models)

        if new_models is None:
            # All model have been found and located.
            pass
        else:
            # There's a new girl in town.
            for girl in new_models:
                print(f'ATTENTION! --> Model: {girl} not on WordPress.')
                print('--> Copying missing model name to your system clipboard.')
                print("Paste it into the Pornstars field as soon as possible...\n")
                pyclip.detect_clipboard()
                pyclip.copy(girl)
        category = [38] if partner == 'abjav' else None # 38 is Japanese Amateur Porn
        payload = content_select.make_payload_simple(wp_slug,
                                                     "draft",
                                                     title,
                                                     description,
                                                     tag_ints,
                                                     calling_models,
                                                     categs=category)
        print("--> Fetching thumbnail...")
        try:
            thumbnail_full = f"{thumbnail_prefix}{main_thumbnail_name}"
            content_select.fetch_thumbnail('thumbnails', wp_slug, thumbnail_full, parent=True)
            print(f"--> Stored thumbnail {wp_slug}.jpg in cache folder ../thumbnails")
            print("--> Uploading thumbnail to WordPress Media...")
            print("--> Adding image attributes on WordPress...")
            img_attrs = content_select.make_img_payload(title, description)
            upload_img = wordpress_api.upload_thumbnail(wp_base_url, ['/media'],
                                                        f"../thumbnails/{wp_slug}.jpg", img_attrs)

            # Sometimes, the function fetch image will fetch an element that is not a thumbnail.
            # upload_thumbnail will report a 500 status code when this is the case.
            if upload_img == 500:
                print("It is possible that this thumbnail is defective. Check the Thumbnail manually.")
                print("--> Proceeding to the next post...\n")
                continue
            else:
                print(f'--> WordPress Media upload status code: {upload_img}')
                print("--> Creating post on WordPress")
                push_post = wordpress_api.wp_post_create(wp_base_url, ['/posts'], payload)
                print(f'--> WordPress status code: {push_post}')
                # Copy important information to the clipboard.
                # Some tag strings end with ';'
                pyclip.detect_clipboard()
                pyclip.copy(embed_code)
                pyclip.copy(title)
                print("--> Check the post and paste all you need from your clipboard.")
                videos_uploaded += 1
        except SSLError:
            pyclip.detect_clipboard()
            pyclip.clear()
            print("* There was a connection error while processing this post... *")
            if input("\nDo you want to continue? Y/N/ENTER to exit: ") == ('y' or 'yes'):
                continue
            else:
                print("\n--> Cleaning thumbnails cache now")
                content_select.clean_file_cache('thumbnails', '.jpg', parent=True)
                print(f'You have created {videos_uploaded} posts in this session!')
                break
        if num < total_elems - 1:
            next_post = input("\nNext post? -> Y/N/ENTER to review next post: ").lower()
            if next_post == ('y' or 'yes'):
                # Clears clipboard after every video.
                pyclip.clear()
                print("\n==> Syncing and caching changes... ε= ᕕ(⎚‿⎚)ᕗ")
                try:
                    sync = content_select.hot_file_sync('wp_posts', 'posts_url', parent=True)
                except ConnectionError:
                    print("Hot File Sync encountered a ConnectionError.")
                    print("Going to next post. I will fetch your changes in a next try.")
                    print("If you want to update again, relaunch the bot.")
                    sync = True
                if sync:
                    not_published_yet = content_select.filter_published(all_vals, wp_posts_f)
                    continue
                else:
                    print("ERROR: WP JSON Sync failed. Look at the files and report this.")
                    content_select.clean_file_cache('thumbnails', '.jpg', parent=True)
            elif next_post == ('n' or 'no'):
                # The terminating parts add this function to avoid tracebacks from pyclip
                pyclip.detect_clipboard()
                pyclip.clear()
                print("\n--> Cleaning thumbnails cache now")
                content_select.clean_file_cache('thumbnails', '.jpg', parent=True)
                print(f'You have created {videos_uploaded} posts in this session!')
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
            print("\n--> Cleaning thumbnails cache now")
            content_select.clean_file_cache('thumbnails', 'jpg', parent=True)
            print(f'You have created {videos_uploaded} posts in this session!')
            print("Waiting for 60 secs to clear the clipboard before you're done with the last post...")
            time.sleep(60)
            pyclip.detect_clipboard()
            pyclip.clear()
            break
    else:
        pyclip.detect_clipboard()
        pyclip.clear()
        print("\nWe have reviewed all posts for this query.")
        print("Try a different SQL query or partner. I am ready when you are. ")
        print("\n--> Cleaning thumbnails cache now")
        content_select.clean_file_cache('thumbnails', '.jpg', parent=True)
        print(f'You have created {videos_uploaded} posts in this session!')
        break
