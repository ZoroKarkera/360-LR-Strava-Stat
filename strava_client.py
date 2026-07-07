from stravalib.client import Client
import requests

from strava_config import get_authorization_credentials


def exchange_code_for_token(code):
    app_name, credentials = get_authorization_credentials()

    print(f"Authorizing new athlete using {app_name}...")

    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
        },
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()


def refresh_access_token(
    refresh_token,
    client_id,
    client_secret,
):
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()


def get_recent_activities(access_token, limit=30):
    client = Client()
    client.access_token = access_token
    return list(client.get_activities(limit=limit))