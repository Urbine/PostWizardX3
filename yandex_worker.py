# This file will be gathering information from the Yandex Webmaster API, and it will be
# focused specifically in its keyword and impression analysis capabilities.

import json
import requests

from main import get_client_info, get_token_oauth, import_token_json

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
cred_file = get_client_info()
client_id = cred_file['Yandex']['client_id']
client_secret = cred_file['Yandex']['client_secret']

# Set the callback URI to accept incoming connections.
# python3 -m http.server -b 127.0.0.47 8888
uri_callback = "http://127.0.0.47:8888"

generate_tkn = input("Generate new token? Y/N ")
if generate_tkn.lower() == ("y" or "yes"):
    get_token_oauth(client_id, uri_callback, client_secret,
                    authorization_url, token_url)
else:
    pass

token_json = import_token_json()

base_url = "https://api.webmaster.yandex.net/v4/user/"
headers_auth = {"Authorization": f"OAuth {token_json['access_token']}"}

user_id = json.loads(requests.get(base_url, headers=headers_auth).content)

hosts = json.loads(requests.get(f"{base_url}{user_id['user_id']}/hosts", headers=headers_auth).content)

host_id = hosts['hosts'][0]['host_id']

# GET https://api.webmaster.yandex.net/v4/user/{user-id}/hosts/{host-id}/search-queries/popular
#  ? order_by=<string> (REQUIRED)
#  & [query_indicator=<string>]
#  & [device_type_indicator=<string>]
#  & [date_from=<datetime>]
#  & [date_to=<datetime>]
#  & [offset=<int32>]
#  & [limit=<int32>]

order_by = ["TOTAL_SHOWS", "TOTAL_CLICKS"]
popular_search_qs = (json.loads(requests.get(
    f"{base_url}{user_id['user_id']}/hosts/{host_id}/search-queries/popular?order_by={order_by[1]}",
    headers=headers_auth).content))

print(popular_search_qs)
