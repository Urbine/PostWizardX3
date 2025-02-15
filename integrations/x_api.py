"""
X Social integration for the content management bots.
As of now, this integration is capable of interacting with the bots in the ``workflows``
package and configuration files within the ``core`` package.
This integration includes a single endpoint for retrieving and posting tweets for now.

As you will see, this implementation makes a heavy use of cURL (Command URL) models to
explain the basis of functions dealing with authentication, communication, as well as certain
design decisions that I came up with in favour of simplicity.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import argparse
import logging
import os
import time

from typing import Any

# Third-party modules
import pyclip
import requests
from requests import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

# Local implementations
import core
from core import (
    get_webdriver,
    generate_random_str,
    RefreshTokenError,
    x_auth,
    AccessTokenRetrivalError,
)

from core.config_mgr import XAuth  # Imported for type annotations.
from .url_builder import URLEncode, XScope, XEndpoints
from workflows import clean_outdated


def curl_auth_x(xauth: XAuth, x_endpoints: XEndpoints) -> str:
    """Authenticate by using an app-only approach. This function is just a model of
    how the X API docs demonstrated a bearer token generation.
    The cURL approach is the following:

    ``curl -u "$API_KEY:$API_SECRET_KEY" --data 'grant_type=client_credentials' 'https://api.x.com/oauth2/token'``

    **Please note that this function is not used in this application since the implementation of the OAuth2 is not
    app-only but uses Proof Key for Code Exchange (PKCE) and deals with the API as a confidential client for the purposes herein described.**

    :param xauth: ``XAuth`` Factory object with the parsed config with API secrets.
    :param x_endpoints: ``XEndpoints`` dataclass containing the endpoints used in this application.
    :return: ``str`` Access token taken from the ``JSON`` response object.
    """
    response = requests.post(
        x_endpoints.token_url,
        data={"grant_type": "client_credentials"},
        auth=(xauth.api_key, xauth.api_secret),
    )
    return response.json()["access_token"]


def post_x(post_text: str, api_token: str, x_endpoints: XEndpoints) -> Response:
    """Once the token is gathered, I can use this function to push a post to X.
    Here is the cURL way of doing this according to the docs:

    ``curl --request POST --url https://api.x.com/2/tweets --header 'Authorization: Bearer <token>'``
    ``--header 'Content-Type: application/json' --data '{"text": "$MYTEXT"}'``

    :param post_text: ``str`` self-explanatory, any text.
    :param api_token: ``str`` X API Access Token
    :param x_endpoints: ``XEndpoints`` dataclass containing the endpoints used in this application.
    :return: ``Response`` object from the ``Requests`` library.
    """
    post_url = x_endpoints.tweets
    post_data = {"text": f"{post_text}"}
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    return requests.post(post_url, json=post_data, headers=headers)


def x_oauth_pkce(xauth: XAuth, x_endpoints: XEndpoints) -> str:
    """In order to generate a token request, I opted to begin this flow with
    an Authorise URL that prompts the user to log in and authorise my application thereafter.
    This is a one-time only process since this URL contains an offline access scope to refresh the token
    everytime we need to operate with access to the API with a new bearer.

    The resulting URL looks like this:
    ``https://x.com/i/oauth2/authorize?response_type=code&client_id=$CLIENT_ID&``
    ``redirect_uri=$CALLBACK_URL&state=MPTFZwCcjKTXrWZ&code_challenge=challenge&code_challenge_method=plain``
    ``&scope=tweet.write+tweet.read+users.read+offline.access``

    According to the OAuth 2.0 standard, the code challenge could be a Base64-encoded SHA256 hash
    as stated in the docs:
    "For devices that can perform a SHA256 hash, the code challenge is a Base64-URL-encoded string of the
    SHA256 hash of the code verifier. Clients that do not have the ability to perform a SHA256 hash
    are permitted to use the plain code verifier string as the challenge, although that provides
    less security benefits so should really only be used if absolutely necessary."
    **I didn't implement the PKCE entirely for the sake of simplicity, although there are a couple of
    functions in the ``core.helpers`` module that can facilitate base64 encoding and SHA256 hashing.**

    :param xauth: ``XAuth`` Factory object with the parsed config with API secrets.
    :param x_endpoints: ``XEndpoints`` dataclass containing the endpoints used in this application.
    :return: ``str`` Encoded URL to initiate the authorisation flow.
    """
    params = {
        "response_type": "code",
        "client_id": f"{xauth.client_id}",
        "redirect_uri": f"{xauth.uri_callback}",
        "state": f"{generate_random_str(15)}",
        "code_challenge": f"challenge",
        "code_challenge_method": "plain",
        "scope": f"{XScope.WRITE} {XScope.READ} {XScope.USREAD} {XScope.OFFLINE}",
    }
    return requests.get(x_endpoints.authorise_url, params=params).url


def access_token(code: str, xauth: XAuth, x_endpoints: XEndpoints) -> Response:
    """After the user authorises my app, X will generate an authorisation code that makes it
    possible to request the new bearer and refresh tokens (if offline.access has been passed
    through the URL scope parameters).
    The function needs the authorisation code that results from a ``GET`` request
    to the redirect URI address.

    :param code: ``str`` Authorisation code from the redirect URI ``GET`` request.
    :param xauth: ``XAuth`` Factory object with the parsed config with API secrets.
    :param x_endpoints: ``XEndpoints`` dataclass containing the endpoints used in this application.
    :return: ``Any`` More precisely a ``JSON`` object. Requests describes this object as ``Any`` for typing purposes.

    """
    token_url = x_endpoints.token_url
    header = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "code": f"{code}",
        "grant_type": "authorization_code",
        "client_id": f"{xauth.client_id}",
        "redirect_uri": f"{xauth.uri_callback}",
        "code_verifier": f"challenge",
    }
    return requests.post(
        token_url,
        data=data,
        auth=(xauth.client_id, xauth.client_secret),
        headers=header,
    )


def refresh_token_x(
    refresh_token: str, xauth: XAuth, x_endpoints: XEndpoints
) -> Response:
    """Executes the cURL flow to refresh the bearer token by providing a refresh token that
    the authorization flow provided for the ``offline.access`` scope.

    ``POST 'https://api.x.com/2/oauth2/token' --header 'Content-Type: application/x-www-form-urlencoded'``
    ``--header 'Authorization: Basic $CLIENT_ID:$CLIENT_SECRET' (base64-encoded)``
    ``--data-urlencode 'refresh_token=$REFRESH_TOKEN --data-urlencode 'grant_type=refresh_token'``


    :param refresh_token: ``str`` from the response object if ``offline.access`` was specified.
    :param xauth: ``XAuth`` Factory object with the parsed config with API secrets.
    :param x_endpoints: ``XEndpoints`` dataclass containing the endpoints used in this application.
    :return: ``Response`` object with the result of the ``POST`` request.
    """
    token_url = x_endpoints.token_url
    header = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "refresh_token": f"{refresh_token}",
        "grant_type": "refresh_token",
    }
    return requests.post(
        token_url,
        data=data,
        auth=(xauth.client_id, xauth.client_secret),
        headers=header,
    )


def authorise_app_x(
    xauth: XAuth, x_endpoints: XEndpoints, headless=True, gecko=False
) -> str:
    """Attempt to emulate user interaction by using webdriver automation with Selenium.
    This authentication flow includes optional clauses that deal with suspicious activity within X
    and tries to bypass them. However, this has proven ineffective in testing because X somehow detects that
    I am automating the flow and imposes MFA measures. As this code does not have access to the actual email server,
    it is not possible to retrieve any verification codes programmatically.

    **Note: The webdriver uses XPath locations that were tested on both Chrome and Firefox.**

    :param xauth: ``XAuth`` Factory object with the parsed config with API secrets.
    :param x_endpoints: ``XEndpoints`` dataclass containing the endpoints used in this application.
    :param headless: ``bool`` CLI parameter for headless webdriver behaviour.
    :param gecko: ``bool`` CLI parameter for switching the webdriver and use Firefox Gecko instead of Chrome.
    :return: ``str`` Authorization code in case the flow is successful either via automation or error handling.
    """
    webdrv = get_webdriver(".", headless=headless, gecko=gecko)
    with webdrv as driver:
        url = x_oauth_pkce(xauth, x_endpoints)
        driver.get(url)
        time.sleep(4)
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

        username = driver.find_element(
            By.XPATH,
            "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input",
        )
        username.send_keys(xauth.x_username)

        next_btn = driver.find_element(
            By.XPATH,
            "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]/div",
        )
        next_btn.click()
        time.sleep(3)

        try:
            # MFA suspicious activity check.
            mfa_text = driver.find_element(
                By.XPATH,
                "/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input",
            )
            mfa_text.send_keys(xauth.x_email)
            next_btn_2 = driver.find_element(
                By.XPATH,
                "/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/button/div",
            )
            next_btn_2.click()
            time.sleep(5)
        except NoSuchElementException:
            pass

        passw = driver.find_element(
            By.XPATH,
            "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input",
        )
        passw.send_keys(xauth.x_passw)

        login_btn = driver.find_element(
            By.XPATH,
            "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/button/div/span/span",
        )
        login_btn.click()
        time.sleep(5)

        get_code = lambda callback: callback.split("=")[-1]

        # This process is likely to fail due to suspicious activity detected by X.
        try:
            authorise_app_btn = driver.find_element(
                By.XPATH,
                "/html/body/div[1]/div/div/div[2]/main/div/div/div[2]/div/div/div[1]/div[3]/button/div/span/span",
            )
            authorise_app_btn.click()
            time.sleep(2)
            token_code = get_code(driver.current_url)
        except NoSuchElementException:
            driver.close()
            print("Automatic authorization process failed. Try with this URL.")
            print(f"Paste the following in a browser (already copied): {url}")
            pyclip.detect_clipboard()
            pyclip.copy(url)
            result = input(
                "After authenticating and authorising, paste the result URL here: "
            )
            token_code = get_code(result.strip())
    return token_code


def load_tokens_json(folder: str) -> tuple[str, str] | None:
    """Token handling with ``JSON`` objects as the application was being tested.
    As of now, the app does not use local ``JSON`` files to store secrets so this is
    no longer in use. Function ``write_tokens_cinfo()`` replaced this method and uses
    the secrets storage standard of the entire project.

    :param folder: ``str`` Location of your ``JSON`` file containing the tokens.
    :return: ``tuple[str, str]`` (access_token, refresh_token)
    """
    local_files = core.search_files_by_ext("json", folder)
    # In case there are outdated files
    clean_outdated(["token-x"], local_files, folder, silent=True)
    if token_file := core.match_list_single("token-x", local_files, ignore_case=True):
        tokens = core.load_json_ctx(local_files[token_file])
        return tokens["access_token"], tokens["refresh_token"]
    else:
        return None


def write_tokens_cinfo(new_bearer_token: str, new_refresh_token: str) -> None:
    """Write the bearer and refresh tokens within the configuration keys of client_info.ini
    which happens to be the standard in secret handling for this project.

    :param new_bearer_token: ``str`` self-explanatory
    :param new_refresh_token: ``str`` self-explanatory
    :return: ``None`` (Writes in client_info.ini config)
    """
    core.write_config_file(
        "client_info", "core.config", "x_api", "access_token", new_bearer_token
    )
    core.write_config_file(
        "client_info", "core.config", "x_api", "refresh_token", new_refresh_token
    )
    return None


def refresh_flow(xauth: XAuth, x_endpoints: XEndpoints) -> None:
    """Guide the token refresh process and call the relevant functions to
    make the necessary changes (token refresh and config update) to ensure
    that successive authentication flows are satisfactory.
    Thanks to this function users can have a smooth experience while using
    the API endpoints that depend on bearer tokens.

    **Please note that you can't expect to read from client_info.ini (or any other required files)
    during runtime since the application already loads the config before this step and stores a snapshot of it
    in memory and/or compiled files. That is why function refresh_flow() stores the bearer token
    in an environment variable, so that our application can make use of it during runtime.
    Factory functions tied to core.config_mgr authentication dataclasses are immutable and, therefore,
    can't be modified by assignment. This is deliberate and desirable behaviour.**

    :param xauth: ``XAuth`` Factory object with the parsed config with API secrets.
    :param x_endpoints: ``XEndpoints`` dataclass containing the endpoints used in this application.
    :return: ``None``
    """
    refresh_token = xauth.refresh_token
    new_request = refresh_token_x(refresh_token, xauth, x_endpoints)
    status_code = new_request.status_code
    if status_code == 200:
        new_tokens = new_request.json()
        new_refresh_token = new_tokens["refresh_token"]
        new_bearer = new_tokens["access_token"]
        write_tokens_cinfo(new_bearer, new_refresh_token)
        os.environ["X_TOKEN"] = new_bearer
        logging.info('Token refreshed and saved in environment under "X_TOKEN"')
    else:
        logging.critical(f"Raised RefreshTokenError. JSON Response {new_request}")
        raise RefreshTokenError(new_request)
    return None


def main(*args, **kwargs) -> None:
    """
    :param args: ``XEndpoints`` and ``XAuth`` Objects
    :param kwargs: CLI parameters for headless automation and the gecko webdriver
    :return: ``None``
    """
    ch_code = authorise_app_x(*args, **kwargs)
    new_tokens = access_token(ch_code, x_auth(), XEndpoints())
    try:
        write_tokens_cinfo(
            new_tokens.json()["access_token"], new_tokens.json()["refresh_token"]
        )
        print(f"The client_info.ini file has been updated with the new tokens.")
    except KeyError:
        raise AccessTokenRetrivalError(new_tokens)


if __name__ == "__main__":
    print("Configuring the X API Integration for you. Please wait...")

    arg = argparse.ArgumentParser(
        description="X API Integration - App Authorize (First Time)"
    )

    arg.add_argument(
        "--headless",
        action="store_true",
        help="Headless App Authorisation.",
    )

    arg.add_argument(
        "--gecko",
        action="store_true",
        help="Use the Gecko webdriver for the automation.",
    )

    args_cli = arg.parse_args()
    main(x_auth(), XEndpoints(), headless=args_cli.headless, gecko=args_cli.gecko)
