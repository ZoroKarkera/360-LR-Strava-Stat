from stravalib.client import Client
import requests
import time

from settings.strava_config import get_authorization_credentials


TOKEN_URL = "https://www.strava.com/oauth/token"
REQUEST_TIMEOUT_SECONDS = 30
MAX_TOKEN_RETRIES = 4


def post_strava_token(data):
    last_error = None

    for attempt in range(1, MAX_TOKEN_RETRIES + 1):
        try:
            response = requests.post(
                TOKEN_URL,
                data=data,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )

            # Retry transient server/network gateway errors.
            if response.status_code in {429, 500, 502, 503, 504} and attempt < MAX_TOKEN_RETRIES:
                wait_seconds = 2 ** (attempt - 1)
                print(
                    f"Strava token request failed with {response.status_code}. "
                    f"Retrying in {wait_seconds}s (attempt {attempt}/{MAX_TOKEN_RETRIES})..."
                )
                time.sleep(wait_seconds)
                continue

            return response

        except requests.exceptions.RequestException as error:
            last_error = error

            if attempt == MAX_TOKEN_RETRIES:
                break

            wait_seconds = 2 ** (attempt - 1)
            print(
                "Network error during Strava token request: "
                f"{error}. Retrying in {wait_seconds}s "
                f"(attempt {attempt}/{MAX_TOKEN_RETRIES})..."
            )
            time.sleep(wait_seconds)

    raise Exception(
        "Failed to reach Strava token endpoint after retries. "
        f"Last error: {last_error}"
    )


def exchange_code_for_token(code):
    app_name, credentials = get_authorization_credentials()

    print(f"Authorizing new athlete using {app_name}...")

    response = post_strava_token(
        {
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
        }
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()


def refresh_access_token(
    refresh_token,
    client_id,
    client_secret,
):
    response = post_strava_token(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()


def get_recent_activities(access_token, limit=30):
    client = Client()
    client.access_token = access_token
    return list(client.get_activities(limit=limit))