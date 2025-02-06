"""
X Social integration for the content management bots.
As of now, this integration is capable of interacting with the
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

# Std Library
import argparse
import os
import time

# Third-party modules
import pyclip
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

# Local implementations
import core
from core import x_auth, generate_random_str, get_webdriver, RefreshTokenError
from core.config_mgr import XAuth  # Imported for type annotations.
from .url_builder import URLEncode, XScope, XEndpoints
from workflows import clean_outdated


def curl_auth_x(xauth: XAuth, x_endpoints: XEndpoints):
    response = requests.post(
        x_endpoints.token_url,
        data={"grant_type": "client_credentials"},
        auth=(xauth.api_key, xauth.api_secret),
    )
    return response.json()["access_token"]


def post_x(post_text: str, api_token: str, x_endpoints: XEndpoints):
    post_url = x_endpoints.tweets
    post_data = {"text": f"{post_text}"}
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    return requests.post(post_url, json=post_data, headers=headers)


def x_oauth_pkce(xauth: XAuth, x_endpoints: XEndpoints):
    space = URLEncode.SPACE
    params = {
        "response_type": "code",
        "client_id": f"{xauth.client_id}",
        "redirect_uri": f"{xauth.uri_callback}",
        "state": f"{generate_random_str(15)}",
        "code_challenge": "challenge",
        "code_challenge_method": "plain",
        "scope": f"{XScope.WRITE} {XScope.READ} {XScope.USREAD} {XScope.OFFLINE}",
    }
    return requests.get(x_endpoints.authorise_url, params=params).url


def access_token(code: str, xauth: XAuth, x_endpoints: XEndpoints):
    token_url = x_endpoints.token_url
    header = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "code": f"{code}",
        "grant_type": "authorization_code",
        "client_id": f"{xauth.client_id}",
        "redirect_uri": f"{xauth.uri_callback}",
        "code_verifier": "challenge",
    }
    return requests.post(
        token_url,
        data=data,
        auth=(xauth.client_id, xauth.client_secret),
        headers=header,
    ).json()


def refresh_token_x(refresh_token: str, xauth: XAuth, x_endpoints: XEndpoints):
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


def authorise_app_x(xauth: XAuth, x_endpoints: XEndpoints, headless=True, gecko=False):
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
    local_files = core.search_files_by_ext("json", folder)
    # In case there are outdated files
    clean_outdated(["token-x"], local_files, folder, silent=True)
    if token_file := core.match_list_single("token-x", local_files, ignore_case=True):
        tokens = core.load_json_ctx(local_files[token_file])
        return tokens["access_token"], tokens["refresh_token"]
    else:
        return None


def write_tokens_cinfo(new_bearer_token: str, new_refresh_token: str) -> None:
    core.write_config_file(
        "client_info", "core.config", "x_api", "access_token", new_bearer_token
    )
    core.write_config_file(
        "client_info", "core.config", "x_api", "refresh_token", new_refresh_token
    )
    return None


def refresh_flow(xauth: XAuth, x_endpoints: XEndpoints) -> None:
    refresh_token = xauth.refresh_token
    new_request = refresh_token_x(refresh_token, xauth, x_endpoints)
    status_code = new_request.status_code
    if status_code == 200:
        new_tokens = new_request.json()
        new_refresh_token = new_tokens["refresh_token"]
        new_bearer = new_tokens["access_token"]
        write_tokens_cinfo(new_bearer, new_refresh_token)
        os.environ["X_TOKEN"] = new_bearer
    else:
        raise RefreshTokenError(new_request.reason)
    return None


def main(*args, **kwargs):
    ch_code = authorise_app_x(*args, **kwargs)
    new_tokens = access_token(ch_code, x_auth(), XEndpoints())
    write_tokens_cinfo(new_tokens["access_token"], new_tokens["refresh_token"])
    print(f"The client_info.ini file has been updated with the new tokens.")


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
