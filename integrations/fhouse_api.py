"""
FapHouse API Integration for content management.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net

"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import argparse
import datetime
import os
import re
import sqlite3
import tempfile
import urllib.parse
from dataclasses import dataclass

# Local implementations
from core import (
    NoFieldsException,
    access_url_bs4,
    write_to_file,
    remove_if_exists,
    clean_filename,
    parse_client_config,
)
from integrations.url_builder import (
    URLEncode,
)


class FHouseBaseUrl:
    """
    Builder class for the FapHouse API Base URL with campaign name.
    """

    def __init__(self, campaign: str = "") -> None:
        task_conf = parse_client_config("tasks_config", "core.config")
        campaign_utm = "=".join(task_conf["fhouse_api"]["fhouse_camp_utm"].split("."))
        if campaign:
            self.__campaign = campaign
            self.__fhouse_base_url = (
                f"https://fap.cash/content/dump?camp={self.__campaign}&{campaign_utm}"
            )
        else:
            self.__fhouse_base_url = f"https://fap.cash/content/dump?{campaign_utm}"

    def __str__(self) -> str:
        return self.__fhouse_base_url


@dataclass(frozen=True)
class FhouseOptions:
    """
    Builder dataclass for the FapHouse URL options.
    """

    orientation: str = "&forient="
    vid_res: str = "&fres="
    period: str = "&fperiod="
    url_num: str = "&furls="
    thumbs_size: str = "&fthumbs="
    thumb_amount: str = "&ftcnt="
    order_by: str = "&ford="
    likes_more_than: str = "&flikes="
    embed_type: str = "&fembed="
    delimit: str = "&fdelim="
    dmp_format: str = "&fformat="
    owner_source: str = "&fowner="
    trailer_size: str = "&ftsize="


@dataclass(frozen=True)
class FHouseFields:
    """
    Builder dataclass for the FapHouse Dump Fields
    """

    embed = "&emb=on"
    vid_id = "&vid=on"
    vid_url = "&url=on"
    thumbnail = "&thumb=on"
    title = "&title=on"
    description = "&desc=on"
    categs = "&cats=on"
    models = "&pstarts=on"
    studio = "&sname=on"
    orient = "&orient=on"
    duration = "&dur=on"
    embed_dur = "&embdur=on"
    date_publish = "&dt=on"
    likes = "&likes=on"
    trailer = "&trailer=on"
    max_res = "&res=on"

    @property
    def __dict__(self) -> dict[str, str]:
        return {
            "embed": self.embed,
            "vid_id": self.vid_id,
            "vid_url": self.vid_url,
            "thumbnail": self.thumbnail,
            "title": self.title,
            "description": self.description,
            "categs": self.categs,
            "models": self.models,
            "studio": self.studio,
            "orient": self.orient,
            "duration": self.duration,
            "embed_dur": self.embed_dur,
            "date_publish": self.date_publish,
            "likes": self.likes,
            "trailer": self.trailer,
            "max_res": self.max_res,
        }


class FHouseURL:
    """
    Builder class for the first part of FapHouse URL.
    """

    def __init__(
        self,
        orient: str,
        vid_res: str,
        period: str,
        url_num: str,
        thumb_size: str,
        order_by: str,
        embed_type: str,
        own_source: str,
        trailer_size: str,
        dmp_format: str,
        delim: str,
        likes_mth: int,
        thumb_amount: int,
        campaign: str,
    ) -> None:
        f_options = FhouseOptions()
        self.base_url = str(FHouseBaseUrl(campaign=campaign))
        self.orient = f_options.orientation + orient
        self.vid_res = f_options.vid_res + vid_res
        self.period = f_options.period + period
        self.url_num = f_options.url_num + url_num
        self.thumb_size = f_options.thumbs_size + thumb_size
        self.order_by = f_options.order_by + order_by
        self.embed_type = f_options.embed_type + embed_type
        self.own_source = f_options.owner_source + own_source
        self.trailer_size = f_options.trailer_size + trailer_size
        self.dmp_format = f_options.dmp_format + dmp_format
        self.format_str = dmp_format
        self.delim = f_options.delimit + delim
        self.delim_str = delim
        self.likes_mth = f_options.likes_more_than + str(likes_mth)
        self.thumb_amount = f_options.thumb_amount + str(thumb_amount)
        self.__f_house_url = (
            self.base_url
            + self.orient
            + self.vid_res
            + self.period
            + self.url_num
            + self.thumb_size
            + self.order_by
            + self.embed_type
            + self.own_source
            + self.trailer_size
            + self.dmp_format
            + self.delim
            + self.likes_mth
            + self.thumb_amount
        )

    def __str__(self) -> str:
        return self.__f_house_url

    def get_delim(self) -> str:
        """
        Getter method for the encoded separator in the URL.
        :return: ``str``
        """
        return self.delim_str

    def get_dump_format(self) -> str:
        """
        Getter method for the dump format str in the URL.
        :return: ``str``
        """
        return self.format_str


class FHouseFieldStr:
    """
    Builder class for csv/dump columns of the FapHouse URL (second part).
    """

    def __init__(
        self,
        embed: bool = False,
        vid_id: bool = False,
        vid_url: bool = False,
        thumbnail: bool = False,
        title: bool = False,
        description: bool = False,
        categs: bool = False,
        models: bool = False,
        studio: bool = False,
        orient: bool = False,
        duration: bool = False,
        embed_dur: bool = False,
        date_publish: bool = False,
        likes: bool = False,
        trailer: bool = False,
        max_res: bool = False,
    ) -> None:
        fields = FHouseFields().__dict__
        self.provided = {k: v for k, v in locals().items() if v is True}
        self.fields = [fields[f] for f in fields.keys() if f in self.provided]
        if self.fields:
            self.__field_str = "".join(self.fields)
        else:
            raise NoFieldsException

    def __str__(self) -> str:
        """
        Getter method - Dump fields str
        :return: ``str``
        """
        return self.__field_str

    def get_fields(self) -> dict[str, str]:
        """
        Getter method - User/API provided active fields
        :return: ``str``
        """
        return self.provided


def fhouse_parse(
    filename: str, extension: str, dirname: str, sep: str, log_res: bool = False
) -> None:
    """
    Content dump parser for FapHouse API. It takes, ideally, a ``CSV`` file to
    convert it into a SQLite3 database.


    :param filename: ``str`` - Self-explanatory
    :param extension: ``str`` - File extension of the source file, typically ``CSV``
    :param dirname: ``str`` - Directory name
    :param sep: ``str`` - Encoded delimiter, typically accessible via a method in the builder class
    :param log_res: ``bool`` Log the results of the computation - Default ``False``
    :return: ``None``
    """
    c_filename = clean_filename(filename, extension)
    path = os.path.join(os.path.abspath(dirname), c_filename)
    db_name = os.path.join(os.getcwd(), f"{filename}-{datetime.date.today()}.db")
    remove_if_exists(db_name)

    db_conn = sqlite3.connect(db_name)
    db_cur = db_conn.cursor()

    total_entries = 0
    with open(path, "r", encoding="utf-8") as dump_file:
        for line in dump_file.readlines():
            line_spl = lambda ln: ln.split(urllib.parse.unquote(sep))
            integer_type_match = (
                lambda column: f"{column.strip('#')} INTEGER"
                if (
                    re.match("ids?", column.strip("#"), flags=re.IGNORECASE)
                    or re.match("likes?", column.strip("#"), flags=re.IGNORECASE)
                    or re.match("duration", column.strip("#"), flags=re.IGNORECASE)
                )
                else column.strip("#")
            )
            if total_entries == 0:
                pre_schema = ",".join(
                    map(
                        integer_type_match,
                        line_spl(line),
                    )
                )
                db_create_table = "CREATE TABLE embeds({})".format(pre_schema)
                db_cur.execute(db_create_table)
                total_entries += 1
            else:
                line_split = tuple([elem.strip("\n") for elem in line_spl(line)])
                value_calc = f"{'?,' * len(line_split)}".strip(",")
                try:
                    db_cur.execute(
                        f"INSERT INTO embeds values({value_calc})",
                        line_split,
                    )
                    db_conn.commit()
                    total_entries += 1
                except sqlite3.OperationalError:
                    # Invalid entries are ignored.
                    continue

    db_cur.close()
    db_conn.close()

    if log_res:
        print(f"Inserted a total of {total_entries} video entries into {db_name}")

    return None


def main(*args, **kwargs):
    f_house_url = FHouseURL(*args)
    f_house_fields = FHouseFieldStr(**kwargs)
    f_house_full_addr = str(f_house_url) + str(f_house_fields)
    temp_store = tempfile.TemporaryDirectory(prefix="dump", dir=".")
    file_extension = f_house_url.get_dump_format()
    write_to_file(
        (fname := "fap-house-dump"),
        temp_store.name,
        file_extension,
        access_url_bs4(f_house_full_addr),
    )
    fhouse_parse(
        fname, file_extension, temp_store.name, f_house_url.get_delim(), log_res=True
    )
    temp_store.cleanup()
    print("Cleaned temporary folder...")


if __name__ == "__main__":
    args_cli = argparse.ArgumentParser(
        description="FapHouse API implementation for webmaster-seo-tools."
    )

    args_cli.add_argument(
        "--campaign", type=str, default="", help="Add a campaign name for your request."
    )

    args_cli.add_argument(
        "--orientation",
        type=str,
        default="straight",
        help="Select orientations from options: gay, shemale, straight (default)",
    )

    args_cli.add_argument(
        "--resolution",
        type=str,
        default="all",
        help="Select the video resolution from options: hd, uhd, all (default)",
    )

    args_cli.add_argument(
        "--period",
        type=str,
        default="week",
        help="Select period from options: day (last day), week (last 7 days) (default), month (last 30 days), all (all time)",
    )

    args_cli.add_argument(
        "--limit",
        type=str,
        default="all",
        help="URL limit code: c1 (100 vids), c2 (1000 vids), c3 (10 000 vids), c4 (100 000 vids), all (default)",
    )

    args_cli.add_argument(
        "--thumb-size",
        type=str,
        default="original",
        help="""Thumbnail sizes have the following codes:
                Tip: Add the code only with this flag. Options: 
                | mmsmall   -> 240x350
                | msmall    -> 240x150
                | small     -> 320x200
                | ssmall    -> 320x240
                | medium    -> 464x290
                | mmsmall2x -> 480x270
                | msmall2x  -> 480x300
                | ssmall2x  -> 640x480
                | small2x   -> 704x440
                | medium2x  -> 928x580
                | original  -> (default option if none is selected)
              """,
    )

    args_cli.add_argument(
        "--thumb-amount",
        type=int,
        default=1,
        help="Number of thumbnails -> from 1 to 25 (default 1 if none is selected)",
    )

    args_cli.add_argument(
        "--order-by",
        type=str,
        default="like",
        help="Select order: dt (publish date), rate (rating), embduration (embed duration), like (video likes)",
    )

    args_cli.add_argument(
        "--gt-like",
        type=int,
        default=0,
        help="More than x likes - minimum likes accepted in dataset. Default is 0.",
    )

    args_cli.add_argument(
        "--embed-type",
        type=str,
        default="code",
        help="Select embed type either 'code' or 'link'",
    )

    args_cli.add_argument(
        "--delimit",
        type=str,
        default=URLEncode.PIPE,
        help="Encoded delimiter (hex for ASCII 124) for content dump - using 'pipe' default",
    )

    args_cli.add_argument(
        "--format",
        type=str,
        default="csv",
        help="Content dump format - Options: 'csv' (default) or 'xml'",
    )

    args_cli.add_argument(
        "--owner",
        type=str,
        default="all",
        help="Content ownership - Options: 'producer', 'creator' or 'all' (default)",
    )

    args_cli.add_argument(
        "--trailer-size",
        type=str,
        default="small",
        help="Trailer size - Options: 'small' (default) or 'medium'",
    )

    args_cli.add_argument(
        "--no-embed", action="store_false", help="Exclude 'embed' column"
    )
    args_cli.add_argument(
        "--no-vid-id",
        action="store_false",
        help="Exclude 'video id' column",
    )
    args_cli.add_argument(
        "--no-vid-url",
        action="store_false",
        help="Exclude 'video URL' column",
    )
    args_cli.add_argument(
        "--no-thumb",
        action="store_false",
        help="Exclude 'thumbnail' column",
    )
    args_cli.add_argument(
        "--no-title", action="store_false", help="Exclude 'title' column"
    )
    args_cli.add_argument(
        "--no-description",
        action="store_false",
        help="Exclude 'description' column",
    )
    args_cli.add_argument(
        "--no-categs",
        action="store_false",
        help="Exclude 'categories' column",
    )
    args_cli.add_argument(
        "--no-models",
        action="store_false",
        help="Exclude 'pornstars' column",
    )
    args_cli.add_argument(
        "--no-studio",
        action="store_false",
        help="Exclude 'studio' column",
    )
    args_cli.add_argument(
        "--no-orientation",
        action="store_false",
        help="Exclude 'orientation' column",
    )
    args_cli.add_argument(
        "--no-duration",
        action="store_false",
        help="Exclude 'duration' column",
    )
    args_cli.add_argument(
        "--no-embed-dur",
        action="store_false",
        help="Exclude 'embed duration' column",
    )
    args_cli.add_argument(
        "--no-date",
        action="store_false",
        help="Exclude 'published date' column",
    )
    args_cli.add_argument(
        "--no-likes", action="store_false", help="Exclude 'likes' column"
    )
    args_cli.add_argument(
        "--no-trailer",
        action="store_false",
        help="Exclude 'trailer' column",
    )
    args_cli.add_argument(
        "--no-max-res",
        action="store_false",
        help="Exclude 'max resolution' column",
    )

    cli = args_cli.parse_args()

    main(
        cli.orientation,
        cli.resolution,
        cli.period,
        cli.limit,
        cli.thumb_size,
        cli.order_by,
        cli.embed_type,
        cli.owner,
        cli.trailer_size,
        cli.format,
        cli.delimit,
        cli.gt_like,
        cli.thumb_amount,
        cli.campaign,
        vid_id=cli.no_vid_id,
        embed=cli.no_embed,
        vid_url=cli.no_vid_url,
        thumbnail=cli.no_thumb,
        title=cli.no_title,
        description=cli.no_description,
        categs=cli.no_categs,
        models=cli.no_models,
        studio=cli.no_studio,
        duration=cli.no_duration,
        embed_dur=cli.no_embed_dur,
        date_publish=cli.no_date,
        likes=cli.no_likes,
        trailer=cli.no_trailer,
        max_res=cli.no_max_res,
        orient=cli.no_orientation,
    )
