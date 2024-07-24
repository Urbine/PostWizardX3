# This file will be gathering information from the Yandex Webmaster API, and it will be
# focused specifically in its keyword research capabilities.

import json
import os
import urllib
import requests

# This way OAuthlib won't enforce HTTPS connections.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from main import get_client_info
from requests_oauthlib import OAuth2Session


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

def get_token_yandex(client_id_, uri_callback_, client_secret_) -> None:
    oauth_session = OAuth2Session(client_id_, redirect_uri=uri_callback_, )
    authorization_url, state = oauth_session.authorization_url('https://oauth.yandex.com/authorize?')
    print(f'Please go to {authorization_url} and authorize access.')
    authorization_response = input('Enter the full callback URL: ')
    token = oauth_session.fetch_token(
        'https://oauth.yandex.com/token',
        authorization_response=authorization_response,
        client_secret=client_secret_)
    with open('token.json', 'w', encoding='utf-8') as t:
        json.dump(token, t, ensure_ascii=False, indent=4)
    return print("Token stored in project root. Ready to use!")


def import_token_json() -> json:
    with open('token.json', 'r', encoding='utf-8') as t:
        imp_tokn = json.load(t)
    return imp_tokn


# Gets the application client details from a json file for privacy reasons.
cred_file = get_client_info()
client_id = cred_file['Yandex']['client_id']
client_secret = cred_file['Yandex']['client_secret']

# Set the callback URI to accept incoming connections.
# python3 -m http.server -b 127.0.0.47 8888
uri_callback = "http://127.0.0.47:8888"

generate_tkn = input("Generate new token? Y/N ")
if generate_tkn.lower() == ("y" or "yes"):
    get_token_yandex(client_id, uri_callback, client_secret)
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