from stravalib.client import Client
from datetime import datetime
import os
import requests

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def exchange_code_for_token(code):

    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        },
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()


def refresh_access_token(refresh_token):

    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
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

    activities = client.get_activities(limit=limit)

    return list(activities)
