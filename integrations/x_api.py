import argparse
import datetime
import os
import requests
import time

# Third-party modules
import pyclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

# Local implementations
import core
from core import x_auth, generate_random_str, get_webdriver
from .url_builder import URLEncode, XScope, XEndpoints
from workflows import clean_outdated


def curl_auth_x(xauth):
    response = requests.post(
        xauth.api_token_url,
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


def x_oauth_pkce(xauth, x_endpoints: XEndpoints):
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


def access_token(code: str, xauth, x_endpoints: XEndpoints):
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


def refresh_token_x(refresh_token: str, xauth, x_endpoints: XEndpoints):
    token_url = x_endpoints.token_url
    credentials = f"{xauth.client_id}:{xauth.client_secret}"
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
    ).json()


def authorise_app_x(xauth, x_endpoints: XEndpoints, headless=True, gecko=False):
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

        get_code = lambda url: url.split("=")[-1]

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
            print("Automatic authorization process failed. Try again with this URL.")
            print(f"Paste the following in a browser (already copied): {url}")
            pyclip.detect_clipboard()
            pyclip.copy(url)
            result = input(
                "After authenticating and authorising, paste the result URL here: "
            )
            token_code = get_code(result.strip())
    return token_code


def load_tokens_local(folder: str) -> tuple[str, str] | None:
    local_files = core.search_files_by_ext("json", folder)
    # In case there are outdated files
    clean_outdated(["token-x"], local_files, folder, silent=True)
    if token_file := core.match_list_single("token-x", local_files, ignore_case=True):
        tokens = core.load_json_ctx(local_files[token_file])
        return tokens["access_token"], tokens["refresh_token"]
    else:
        return None


def refresh_flow_x(xauth, x_endpoints: XEndpoints, folder: str) -> tuple[str, str]:
    tkn_filename = f"token-x-{datetime.date.today()}"
    current_tokens = load_tokens_local(folder)
    core.export_request_json(
        tkn_filename, refresh_token_x(current_tokens[1], xauth, x_endpoints)
    )
    new_tokens = load_tokens_local(folder)
    return new_tokens


def main(*args, **kwargs):
    ch_code = authorise_app_x(*args, **kwargs)
    token_filename = f"token-x-{datetime.date.today()}"
    core.export_request_json(
        token_filename, access_token(ch_code, x_auth(), XEndpoints())
    )
    print(f"Check for file {token_filename}.json in {os.getcwd()}")


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

    arg_s = arg.parse_args()
    main(x_auth(), XEndpoints(), headless=arg_s.headless, gecko=arg_s.gecko)
