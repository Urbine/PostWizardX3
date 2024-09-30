import helpers
import wordpress_api

import pprint

def clean_descriptions(desc_lst: list[str]):
    descriptions = desc_lst
    clean_desc = []
    for description in descriptions:
        # Descriptions has a <title> - <description> format.
        dash_out = description.split('-')
        if len(dash_out) >= 2:
            # Sometimes, I could hit a <title-something> - <description>
            # I also want to make sure not to get the call to action after the period.
            if len(dash_out) == 3:
                clean_desc.append(dash_out[2:][0].strip().split('.')[0])
            else:
                clean_desc.append(dash_out[1].split('.')[0])
        else:
            clean_desc.append(description.split('.')[0].strip())
    return clean_desc


# Start by creating our training set
import_wp_cache = helpers.load_json_ctx('wp_posts', parent=True)

titles = wordpress_api.get_post_titles_local(import_wp_cache, yoast=True)
raw_descriptions = wordpress_api.get_post_descriptions(import_wp_cache, yoast=True)
# I want to remove the call to action and focus keyphrase from the description.
# TODO: Pornhub&period;com&comma, &period, &amp; must be stop words.
categories = wordpress_api.get_post_category(import_wp_cache)
train_set = zip(titles, clean_descriptions(raw_descriptions), categories)
pprint.pprint(list(train_set))
