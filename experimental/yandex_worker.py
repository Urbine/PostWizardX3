# This file will be gathering information from the Yandex Webmaster API, and it will be
# focused specifically in its keyword and impression analysis capabilities.

from common import helpers
import requests

from common.config_mgr import YANDEX_INFO

#  oauth2 = "https://oauth.yandex.com/authorize?response_type=code"
#  & client_id=<app ID>
# [& device_id=<device ID>]
# [& device_name=<device name>]
# [& redirect_uri=<redirect URL>]
# [& login_hint=<username or email>]
# [& scope=<requested required rhttps://api.webmaster.yandex.net/v4/userights>]
# [& optional_scope=<requested optional rights>]
# [& force_confirm=yes]
# [& state=<arbitrary string>]

#
authorization_url = "https://oauth.yandex.com/authorize?"
token_url = "https://oauth.yandex.com/authorize?"

# Gets the application client details from a json file for privacy reasons.
client_id = YANDEX_INFO.client_id
client_secret = YANDEX_INFO.client_secret

# Set the callback URI to accept incoming connections.
# python3 -m http.server -b 127.0.0.47 8888
uri_callback = "http://127.0.0.47:8888"

generate_tkn = input("Generate new token? Y/N ")
if generate_tkn.lower() == ("y" or "yes"):
    helpers.export_request_json(
        "token",
        helpers.get_token_oauth(
            client_id, uri_callback, client_secret, authorization_url, token_url
        ),
        4,
        parent=True,
    )
else:
    pass

token_json = helpers.load_json_ctx("token")

base_url = "https://api.webmaster.yandex.net/v4/user/"
headers_auth = {"Authorization": f"OAuth {token_json['access_token']}"}

user_id = requests.get(base_url, headers=headers_auth).json()

hosts = requests.get(
    f"{base_url}{user_id['user_id']}/hosts", headers=headers_auth
).json()

host_id = hosts["hosts"][0]["host_id"]

# Getting information about popular search queries
# GET https://api.webmaster.yandex.net/v4/user/{user-id}/hosts/{host-id}/search-queries/popular
#  ? order_by=<string> (REQUIRED)
#  & [query_indicator=<string>]
#  & [device_type_indicator=<string>]
#  & [date_from=<datetime>]
#  & [date_to=<datetime>]
#  & [offset=<int32>]
#  & [limit=<int32>]

# Getting general statistics for all search queries
# GET https://api.webmaster.yandex.net/v4/user/{user-id}/hosts/{host-id}/search-queries/all/history
#  ? [query_indicator=<string>]
#  & [device_type_indicator=<string>]
#  & [date_from=<datetime>]
#  & [date_to=<datetime>]

# Getting general statistics for a search query
# GET https://api.webmaster.yandex.net/v4/user/{user-id}/hosts/{host-id}/search-queries/{query-id}/history
#  ? [query_indicator=<string>]
#  & [device_type_indicator=<string>]
#  & [date_from=<datetime>]
#  & [date_to=<datetime>]


# Query sorting order (ApiQueryOrderField)
# and Query indicators (ApiQueryIndicator)
api_qu_ind: dict = {
    "t_shows": "TOTAL_SHOWS",
    "t_clicks": "TOTAL_CLICKS",
    "a_show_pos": "AVG_SHOW_POSITION",
    "a_click_pos": "AVG_CLICK_POSITION",
}

# Device type indicators (ApiDeviceTypeIndicator)
dev_type_ind: dict = {
    "all": "ALL",
    "pcs": "DESKTOP",
    "ph_tab": "MOBILE_AND_TABLET",
    "mob": "MOBILE",
    "tabs": "TABLET",
}

order_by = [api_qu_ind["t_shows"], api_qu_ind["t_clicks"]]
popular_search_qs = requests.get(
    f"{base_url}{user_id['user_id']}/hosts/{host_id}/search-queries/popular?order_by={order_by[1]}",
    headers=headers_auth,
).json()

print(popular_search_qs)
