import os
from pathlib import Path

import yaml


CONFIG_FILE = Path(__file__).parent / "config" / "strava_apps.yml"


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
}


def get_app_for_athlete(firstname):
    for app_name, app in CONFIG["apps"].items():
        if firstname in app["athletes"]:
            return app_name

    raise ValueError(
        f"Athlete '{firstname}' not found in config/strava_apps.yml"
    )


def get_credentials(firstname):
    app = get_app_for_athlete(firstname)

    credentials = STRAVA_APPS.get(app)

    if not credentials:
        raise ValueError(f"Unknown Strava app '{app}'")

    return app, credentials