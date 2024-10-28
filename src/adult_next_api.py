import datetime
import sqlite3

# Local implementations
import helpers

# Constants

ABJAV_BASE_URL = 'https://direct.abjav.com'
ABJAV_CAMPAIGN_ID = 1291575419

# Encoded separators for the URL params
PIPE_SEP = '%7C'
COMMA_SEP = '%2C'
SEMICOLON_SEP = '%3B'


# Functions

def construct_api_dump_url(base_url: str,
                           campgn_id: str | int,
                           sort_crit: str,
                           sep: str,
                           days: str | int = '',
                           url_limit: str | int = 999999999) -> str:
    params = '/feeds/?link_args='
    campaign_id = f'campaign_id:{campgn_id}'
    format = "&feed_format=csv&"
    sorting = f'sorting={sort_crit}&'  # rating, popularity, duration, post_date, ID
    limit = f'limit={url_limit}'
    sep_param = f'&csv_separator={sep}&'
    days = f'days={days}&' if days != '' else days

    # Column Fields
    ID_ = 'id'
    title = 'title'
    description = 'description'
    link = 'link'
    duration = 'duration'  # seconds
    rating = 'rating'
    added_time = 'post_date'
    categories = 'categories'
    tags = 'tags'
    model = 'models'
    embed_code = 'embed'
    thumbnail_prefix = 'screenshots_prefix'  # Attaches to main to fetch thumbnail.
    main_thumbnail = 'main_screenshot'  # Thumbnail ID obtained from removing the img extension
    thumbnails = 'screenshots'
    video_thumbnail_url = 'preview_url'

    column_lst = [
        ID_,
        title,
        description,
        link,
        duration,
        rating,
        added_time,
        categories,
        tags,
        model,
        embed_code,
        thumbnail_prefix,
        main_thumbnail,
        thumbnails,
        video_thumbnail_url
    ]

    csv_columns = f'csv_columns={sep.join(column_lst)}'

    return f"{base_url}{params}{campaign_id}{format}{sorting}{days}{limit}{sep_param}{csv_columns}"


def adult_next_dump_parse(filename: str,
                          dirname: str,
                          partner: str,
                          sep: str,
                          parent: bool = False):
    # ID|Title|Description|Website link|Duration|Rating|Publish date, time|Categories|Tags|Models|Embed code|Thumbnail prefix|Main thumbnail|Thumbnails|Preview URL
    if dirname:
        path = f"{dirname}/{helpers.clean_filename(filename, 'csv')}"
    else:
        path = f"{helpers.is_parent_dir_required(parent=parent)}{helpers.clean_filename(filename, 'txt')}"

    db_name = f'{helpers.is_parent_dir_required(parent=parent)}{filename}-{datetime.date.today()}.db'
    db_conn = sqlite3.connect(db_name)
    db_cur = db_conn.cursor()

    db_create_table = """
    CREATE TABLE embeds(id, 
                        title, 
                        description, 
                        web_link, 
                        duration, 
                        rating, 
                        date, 
                        categories, 
                        tags, 
                        models, 
                        embed_code, 
                        thumbnail_prefix, 
                        thumbnail_name, 
                        video_thumbnails, 
                        video_trailer, 
                        wp_slug)
    """
    db_cur.execute(db_create_table)

    total_entries = 0
    with open(path, 'r', encoding='utf-8') as dump_file:
        for line in dump_file.readlines():
            # I don't want to process or count the header of the csv file.
            if total_entries == 0:
                total_entries += 1
                continue
            else:
                line_split = line.split(sep)
                id_ = line_split[0]
                title = line_split[1]
                description = line_split[2]
                website_link = line_split[3]
                duration = line_split[4]
                rating = line_split[5]
                publish_date = line_split[6].split(' ')[0]
                categories = line_split[7]
                tags = line_split[8]
                models = line_split[9]
                embed_code = line_split[10]
                thumbnail_prefix = line_split[11]
                main_thumbnail = line_split[12]
                thumbnails = line_split[13]
                video_trailer = line_split[14].strip('\n')

                # Custom db fields

                # As mentioned in other modules, slugs have to contain the content type
                wp_slug = f"{website_link.split('/')[-2:][0]}-{partner}-video"

                all_values = (id_,
                              title,
                              description,
                              website_link,
                              duration,
                              rating,
                              publish_date,
                              categories,
                              tags,
                              models,
                              embed_code,
                              thumbnail_prefix,
                              main_thumbnail,
                              thumbnails,
                              video_trailer,
                              wp_slug)

                db_cur.execute("INSERT INTO embeds values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", all_values)
                db_conn.commit()
                total_entries += 1

    db_conn.close()
    return f'Inserted a total of {total_entries} video entries into {db_name}'


if __name__ == '__main__':
    main_url = construct_api_dump_url(ABJAV_BASE_URL,
                                      ABJAV_CAMPAIGN_ID,
                                      'popularity',
                                      PIPE_SEP, days=30)

    helpers.write_to_file('abjav-dump',
                          'tmp',
                          'csv',
                          helpers.access_url_bs4(main_url),
                          parent=True)

    partners = ['abjav']

    result = adult_next_dump_parse('abjav-dump', '../tmp',
                          partners[0], '|', parent=True)
    print(result)