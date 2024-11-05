# Accessing MongerCash to get Hosted Videos and links
import datetime

from bs4 import BeautifulSoup

from common import helpers
from tasks import M_CASH_PASSWD, M_CASH_USERNAME, get_partner_name

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By

import time

# ==== Functions ====

def extract_descriptions(bs4_obj: BeautifulSoup):
    # <td><textarea class="display-link-text" rows="2">description text</textarea></td>
    text_areas = bs4_obj.find_all('textarea',
                                   attrs={'class': 'display-link-text',
                                          'rows': '2'})
    # All descriptions are located in even positions followed by <script>
    # elements in uneven positions. This is the easiest approach, I guess.
    return [txt_area.text for num, txt_area in enumerate(text_areas, start=1)
            if num%2 == 0]

def extract_title(bs4_obj: BeautifulSoup):
    # <td class="tab-column col_0 center-align">video title</td>
    vid_title = bs4_obj.find_all('td',
                              attrs={'class': 'tab-column col_0 center-align'})
    return [title.text for title in vid_title]

def extract_date(bs4_obj: BeautifulSoup):
    # <td class="tab-column col_1 center-align">Sep  4, 2024</td>
    vid_date = bs4_obj.find_all('td',
                              attrs={'class': 'tab-column col_1 center-align'})
    return [date.text for date in vid_date]

def extract_duration(bs4_obj: BeautifulSoup):
    # <td class="tab-column col_2 center-align">4 Min</td>
    vid_duration = bs4_obj.find_all('td',
                              attrs={'class': 'tab-column col_2 center-align'})
    return [duration.text for duration in vid_duration]

# Video thumbnail & source link
# <video class="video_holder_14126 table-video-small" controls="" poster="
# https://xyz.com/ttp/video/video_thumbnail.jpg">
# <source src="https://xyz.com/ttp/video/video_file.mp4" type="video/"/>
# </video>

def extract_source(bs4_obj: BeautifulSoup):
    video_source = bs4_obj.find_all('source')
    return [source.attrs['src'] for source in video_source]

def extract_thumbnail(bs4_obj: BeautifulSoup):
    video_thumb = bs4_obj.find_all('video')
    return [thumb.attrs['poster'].strip('\n\t') for thumb in video_thumb]

def combine_vid_elems(bs4_obj):
    page_vids = zip(extract_title(bs4_obj),
              extract_descriptions(bs4_obj),
              extract_date(bs4_obj),
              extract_source(bs4_obj),
              extract_thumbnail(bs4_obj))
    return [vid_elem_lst for vid_elem_lst in page_vids]

def get_xml_link(bs4_obj: BeautifulSoup):
    a_xml = bs4_obj.find_all('a',
                          attrs = {'title': 'Export as XML'})
    # There is only one link with this 'title attribute'
    return [a.attrs['href'] for a in a_xml][0]

def xml_tag_text(bs4_xml: BeautifulSoup, elem_tag: str):
    title = bs4_xml.find(elem_tag)
    return title.text

def get_page_source_flow(url_: str,
                         c_info: tuple,
                         webdrv: webdriver,
                         partner_hint: str = None) -> tuple[BeautifulSoup, str]:
    # Captures the source outside the context manager.
    source_html = None
    with webdrv as driver:

            # Go to URL
            print(f"Getting options from {url_}")
            print("Please wait...\n")
            driver.get(url_)

            # Find element by its ID
            username_box = driver.find_element(By.ID, 'user')
            pass_box = driver.find_element(By.ID, 'password')

            # Authenticate / Send keys
            username_box.send_keys(c_info[0])
            pass_box.send_keys(c_info[1])
            time.sleep(1)

            # Get Button Class
            button_login = driver.find_element(By.ID, 'head-login')

            # Click on the login Button
            button_login.click()
            time.sleep(3)

            # This assumes that 3 seconds is more than enough to get the options.
            # In testing, this webpage seems to extend the loading time
            # required, which impacts performance.
            driver.execute_script("window.stop();")

            # Partner select
            website_partner = driver.find_element(By.XPATH, '//*[@id="link_site"]')
            website_partner_select = Select(website_partner)
            partner_options = website_partner_select.options

            if partner_hint:
                selection = helpers.match_list_single(partner_hint, partner_options, ignore_case=True)
            else:
                for num, opt in enumerate(partner_options, start=0):
                    print(f'{num}. {opt.text}')

                selection = input("Enter a number and select a partner: ")

            website_partner_select.select_by_index(int(selection))
            partner_name = get_partner_name(partner_options, int(selection))
            time.sleep(1)
            apply_changes_xpath = '/html/body/div[1]/div[2]/form/div/div[2]/div/div/div[6]/div/div/input'
            apply_changes_button = driver.find_element(By.XPATH, apply_changes_xpath)
            apply_changes_button.click()
            time.sleep(1)

            # Refresh the page to avoid loading status crashes in Chrome
            driver.refresh()

            # Increase videos per page before dumping to XML
            vids_per_page = driver.find_element(By.ID, 'page-count-val')

            vid_select = Select(vids_per_page)

            # selected_options = vid_select.options
            # select_by_index seems to work with 0-indexing.
            # for num, opt in enumerate(selected_options, start=0):
            #     print(f'{num}. {opt.text}')
            #
            # selection = input("Enter a number and select an option: ")

            # Selecting `Show All` by default in index 5
            vid_select.select_by_index(5)

            #Locate update button to submit selected option
            update_submit_button = driver.find_element(By.ID, 'pageination-submit')
            update_submit_button.click()
            time.sleep(5)

            source_html = BeautifulSoup(driver.page_source, 'html.parser')

    return source_html, f'{partner_name}photos-{datetime.date.today()}'

M_CASH_HOSTED_URL = 'https://mongercash.com/internal.php?page=adtools&category=3&typeid=23'
M_CASH_SETS_URL = 'https://mongercash.com/internal.php?page=adtools&category=3&typeid=4'

if __name__ == '__main__':
    # ==== Execution space ====
    # Cache folder for downloads
    cache_folder = '../tmp'

    # Initialize the webdriver
    web_driver = helpers.get_webdriver(cache_folder, headless=True)
    web_driver_gecko = helpers.get_webdriver(cache_folder, headless=True, gecko=True)

    # TODO: Use JSON notation to store user credentials
    #  so that no private information is pushed to GitHub. OK
    username = M_CASH_USERNAME
    password = M_CASH_PASSWD

    html_source= get_page_source_flow(M_CASH_SETS_URL,
                                      (username, password), web_driver)

    helpers.write_to_file(html_source[1], 'tmp', 'html', html_source[0], parent=True)


# for num, elem in enumerate(xml_elem_entry, start=1):
#     print(f'{num} - {xml_tag_text(elem, "title")}')


# def get_select_txt(bs4_obj: BeautifulSoup, ID: str):
#     select_elem = bs4_obj.find_all('select',
#                                    attrs = {'id':ID})
#     return [id_elem.attrs for id_elem in select_elem]

# for num, entry in enumerate(entry_elems, start=1) :
#     # <published_date_nice>2024-09-05 00:00:00</published_date_nice>
#     date_process = xml_tag_text(entry, "published_date_nice").split(" ")[0].split("-")
#     date_to_py = datetime.date(int(date_process[0]), int(date_process[1]), int(date_process[2]))
#     print(f'{num} -  {xml_tag_text(entry, "title")}')
#     print(f'{xml_tag_text(entry, "description")}')
#     print(f'{xml_tag_text(entry, "thumbnail")}')
#     print(f'{xml_tag_text(entry, "vid_link")}')
#     print(f'{date_to_py}')
#     print(f'{xml_tag_text(entry, "tracking_url")}')
#     print(f'{xml_tag_text(entry, "tags").split(",")}')
#     print('==============')

# pprint.pprint(xml_vids)
# Relevant elements: 6 7 8 10 21 40 41 42
# <url>https://hosted.mongercash.com/videos/violet2_trailer.mp4</url>
# <thumbnail>https://hosted.mongercash.com/videos/violet2_trailer.jpg</thumbnail>
# <description>Hot Manila MILF gets her porn cherry busted by huge dick stud</description>
# <tags>violet tan,shaved,cumshots,facial,pussy,legs,ass,hardcore,blowjob,pov,doggystyle,cowgirl</tags>
# <vid_link>https://hosted.mongercash.com/videos/violet2_trailer.mp4</vid_link>
# <model>Violet Tan</model>
# <published_date_nice>2024-09-05 00:00:00</published_date_nice>
# <title>Hot MILF Porn</title>
# <tracking_url>join.trikepatrol.com/track/MzAwMTc2NC4xLjIuMy4wLjE0MTMwLjAuMC4w</tracking_url>

# Results
# 14130 ----> # 0
# 5     ----> # 1
# 2     ----> # 2
# 1725508800 ----> # 3
# 0          ----> # 4
# 0          ----> # 5
# https://hosted.mongercash.com/videos/violet2_trailer.mp4 ----> # 6
# https://hosted.mongercash.com/videos/violet2_trailer.jpg ----> # 7
# Hot Manila MILF gets her porn cherry busted by huge dick stud ----> # 8
# 1                                                             ----> # 9
# violet tan,shaved,cumshots,facial,pussy,legs,ass,hardcore,blowjob,pov,doggystyle,cowgirl ----> # 10
# 3         ----> # 11
# 0         ----> # 12
# 0         ----> # 13
# 0         ----> # 14
# 0         ----> # 15
#           ----> # 16
# 3001764   ----> # 17
# 1         ----> # 18
# 2         ----> # 19
#           ----> # 20
# https://hosted.mongercash.com/videos/violet2_trailer.mp4  ----> # 21
# Violet Tan ----> # 22
# ?          ----> # 23
#            ----> # 24
# 5          ----> # 25
# 0          ----> # 26
# 0          ----> # 27
# 0          ----> # 28
# 2          ----> # 29
# 0         ----> # 30
# 0         ----> # 31
# 0         ----> # 32
# 0         ----> # 33
# 0         ----> # 34
# 0         ----> # 35
# 000       ----> # 36
# 0         ----> # 37
# MzAwMTc2NC4xLjAuMC4wLjAuMC4wLjA     ----> # 38
#                                     ----> # 39
# 2024-09-05 00:00:00                 ----> # 40
# Hot MILF Porn                       ----> # 41
# join.trikepatrol.com/track/MzAwMTc2NC4xLjIuMy4wLjE0MTMwLjAuMC4w   ----> # 42
# MzAwMTc2NC4xLjIuMy4wLjE0MTMwLjAuMC4w                              ----> # 43

# ==== XML PARSING ====

# Entry element that contains all the videos
# <entry id="14130:2::1725508800" name="Hot MILF Porn">
# <adtoolid>14130</adtoolid>
# <identid>5</identid>
# <siteid>2</siteid>
# <published_date>1725508800</published_date>
# <networkid>0</networkid>
# <deleted>0</deleted>
# <url>https://hosted.mongercash.com/videos/violet2_trailer.mp4</url>
# <thumbnail>https://hosted.mongercash.com/videos/violet2_trailer.jpg</thumbnail>
# <description>Hot Manila MILF gets her porn cherry busted by huge dick stud</description>
# <type>1</type>
# <tags>violet tan,shaved,cumshots,facial,pussy,legs,ass,hardcore,blowjob,pov,doggystyle,cowgirl</tags>
# <embed/>3
#     <autoplay>0</autoplay>
# <controls>0</controls>
# <loop>0</loop>
# <muted>0</muted>
# <item id="ids">
# <loginid>3001764</loginid>
# <programid>1</programid>
# <siteid>2</siteid>
# </item>
# <vid_link>https://hosted.mongercash.com/videos/violet2_trailer.mp4</vid_link>
# <model>Violet Tan</model>
# <var_divide>?</var_divide>
# <item id="ident_details">
# <override_identifier_id>5</override_identifier_id>
# <loginid>0</loginid>
# <networkid>0</networkid>
# <programid>0</programid>
# <siteid>2</siteid>
# <tourid>0</tourid>
# <optionid>0</optionid>
# <adtoolid>0</adtoolid>
# <subid1>0</subid1>
# <subid2>0</subid2>
# <billerid>0</billerid>
# <countryid>000</countryid>
# <promotionalid>0</promotionalid>
# <encoded>MzAwMTc2NC4xLjAuMC4wLjAuMC4wLjA</encoded>
# </item>
# <published_date_nice>2024-09-05 00:00:00</published_date_nice>
# <title>Hot MILF Porn</title>
# <tracking_url>join.trikepatrol.com/track/MzAwMTc2NC4xLjIuMy4wLjE0MTMwLjAuMC4w</tracking_url>
# <encoded>MzAwMTc2NC4xLjIuMy4wLjE0MTMwLjAuMC4w</encoded>
# </entry>

# ====++++====

# Vid attributes from script element in textarea
# <td><textarea class="display-link-text" rows="2">&lt;script type="text/javascript"
# src="https://mongercash.com/jscript/flowplayer.js"&gt;&lt;/script&gt;&lt;
# div class="video_holder_14105 table-video-small"&gt;&lt;/div&gt;&lt;script&gt;
# flowplayer("div.video_holder_14105", {src:'https://mongercash.com/flash/flowplayer.swf', width: 386, height: 386},
# {playlist: ['https://hosted.mongercash.com/hlb/video/june1_romance_blowjob_fucking_4min.jpg',
# {autoPlay: false,autoBuffering: false,loop: false,
# url: 'https://hosted.mongercash.com/hlb/video/june1_romance_blowjob_fucking_4min.mp4',
# linkUrl: "https://join.helloladyboy.com/track/MzAwMTc2NC4xLjIxLjM1LjAuMTQxMDUuMC4wLjA"}],
# plugins: { controls: {all: false,play: true,scrubber: true,mute: true,fullscreen: true}}})
# \;&lt;/script&gt;</textarea></td>
# </tr>

# Access CSV Dump
# <a href=("internal.php?page=adtools&amp;category=3&amp;typeid=23&amp;default_campaign=0&amp;tourid=0&amp;campaignid=create&amp;"
# "addingTags=Add+a+Traffic+Tag...&amp;programid=1&amp;toggle=0&amp;siteid=30&amp;count=10&amp;view=dump")
# class="linkcode-view" id="dump_0" title="View as a Dump"><img src="nats_images/csv-dump.png"
# class="current-view" alt="View as a Dump" width="16" height="16"></a>

# Link encoding field (encoded by default)
# <select class="filter-select" name="toggle" style="width:150px;">
# <option selected="" value="0">Encoded</option>
# <option value="1">Un-Encoded</option>
# <option value="2">Shortname</option>
# <option value="10">Encoded with HTML</option>
# <option value="11">Un-Encoded with HTML</option>
# <option value="12">Shortname with HTML</option>

# Partner select
# <select class="filter-select" id="link_site" name="siteid" style="width:180px;">
# <option value="-1">All Sites</option>
# <option value="16">Asian Sex Diary - Membership</option>
# <option value="30">Euro Sex Diary - Membership</option>
# <option value="21">Hello Ladyboy - Membership</option>
# <option value="28">Milf Trip - Membership</option>
# <option value="27">Paradise GF's - Membership</option>
# <option value="29">Screw Me Too - Membership</option>
# <option value="14">Totico's - Membership</option>
# <option value="2">Trike Patrol - Membership</option>
# <option value="15">TukTuk Patrol - Membership</option>
# </select>

# Tour select (enabled after a partner selection is place)
# <select class="filter-select" id="tour-options" name="tourid" style="width:180px;">
# <option selected="" value="0">All Tours</option>
# </select>

# Duration type select
# <select class="filter-select-short" id="inline-search-type" name="search[type]">
# <option value="0">All Types</option>
# <option value="1">Trailer</option>
# <option value="2">3 Min</option>
# <option value="3">4 Min</option>
# <option value="4">5 Min</option>
# <option value="5">6 Min</option>
# </select>

# Search button
# <input class="button DisableSubmit" disabled="1" id="inline-search-submit"
# type="submit" value="SEARCH CONTENT"/>

# Search input box
# <input name="search[name]" id="inline-search" placeholder="Search..."
# value="Search..." class="filter-text">

# Time setting filter
# <select class="filter-select-veryshort" id="inline-time_setting" name="time_setting">
# <option value="0">Anytime</option>
# <option value="-1">New</option>
# <option value="3">After</option>
# <option value="2">Before</option>
# <option value="1">On </option>
# </select>

# Apply changes button
# <input type="submit" class="button" id="filter-submit" value="APPLY CHANGES">

# ==== FOOTER ====

# Videos per page
# <select name="count" id="page-count-val">
# <option value="10">10</option>
# <option value="25" selected="">25</option>
# <option value="50">50</option>
# <option value="100">100</option>
# <option value="250">250</option>
# <option value="all">Show All</option>
# </select>

# Update button
# <input type="submit" id="pageination-submit"
# class="button inline-button DisableSubmit"
# disabled="1" value="UPDATE">

# Page wrapper (Nav buttons)
# <div class="page-wrapper">
# <div class="page-text">Page:</div>
# <div class="pagination-button">&lt;</div>
# <div class="current-page">1</div> <div class="active-button">
# <a href="/internal.php?page=adtools&amp;category=3&amp;typeid=23&amp;start=25">2</a></div>
# <div class="active-button"><a href="/internal.php?page=adtools&amp;category=3&amp;typeid=23&amp;start=50">3</a></div>
# <div class="page-text"> ..... </div>
# <div class="active-button three-digits">
# <a href="/internal.php?page=adtools&amp;category=3&amp;typeid=23&amp;start=3275">132</a></div>
# <div class="active-button three-digits">
# <a href="/internal.php?page=adtools&amp;category=3&amp;typeid=23&amp;start=3300">133</a></div>
# <div class="active-button"><a href="/internal.php?page=adtools&amp;category=3&amp;typeid=23&amp;start=25">&gt;</a>
# </div>

# Download XML File
# <a href="internal.php?category=3&amp;typeid=23&amp;default_campaign=0&amp;tourid=0&amp;campaignid=create&amp;
# addingTags=Add+a+Traffic+Tag...&amp;toggle=0&amp;siteid=30&amp;count=all&amp;programid=1&amp;page=dump&amp;
# function=display_adtools&amp;dump_array=adtools&amp;view=xml"
# class="linkcode-view" id="xml_1" target="_blank" title="Export as XML">
# <img src="nats_images/view-as-xml.png" alt="Export as XML" width="16" height="16"></a>