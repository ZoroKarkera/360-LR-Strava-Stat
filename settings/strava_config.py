from dotenv import load_dotenv

load_dotenv()
import os
from pathlib import Path

import yaml


CONFIG_FILE = Path(__file__).parent / "strava_apps.yml"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


CONFIG = load_config()


STRAVA_APPS = {
    "app1": {
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
    },
    "app2": {
        "client_id": os.getenv("CLIENT_ID_APP2"),
        "client_secret": os.getenv("CLIENT_SECRET_APP2"),
    },
    "app3": {
        "client_id": os.getenv("CLIENT_ID_APP3"),
        "client_secret": os.getenv("CLIENT_SECRET_APP3"),
    },
}


def normalize_athlete_name(name):
    # Normalize user-provided names to avoid config mismatches from case/spacing.
    return " ".join(str(name or "").split()).casefold()


def get_app_for_athlete(firstname):
    target = normalize_athlete_name(firstname)

    for app_name, app in CONFIG["apps"].items():
        athletes = app.get("athletes", [])
        normalized_athletes = {
            normalize_athlete_name(athlete)
            for athlete in athletes
        }

        if target in normalized_athletes:
            return app_name

    cleaned = " ".join(str(firstname or "").split())
    raise ValueError(
        f"Athlete '{cleaned}' not found in config/strava_apps.yml"
    )


def get_credentials(firstname):
    app = get_app_for_athlete(firstname)

    credentials = STRAVA_APPS.get(app)

    if not credentials:
        raise ValueError(f"Unknown Strava app '{app}'")

    return app, credentials

def get_authorization_credentials():

    override = os.getenv("AUTHORIZATION_APP_OVERRIDE")

    if override:
        app_name = override
        print(f"Using authorization app override: {app_name}")
    else:
        app_name = CONFIG["default_authorization_app"]
        print(f"Using default authorization app: {app_name}")

    credentials = STRAVA_APPS.get(app_name)

    if credentials is None:
        available = ", ".join(STRAVA_APPS.keys())

        raise ValueError(
            f"Unknown Strava app '{app_name}'. "
            f"Available apps: {available}"
        )

    return app_name, credentials