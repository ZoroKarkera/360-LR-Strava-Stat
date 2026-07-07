from flask import redirect, request

from database import db
from models import Athlete
from strava_client import exchange_code_for_token
from settings.strava_config import get_authorization_credentials

import os

REDIRECT_URI = os.getenv("REDIRECT_URI")


def login():

    app_name, credentials = get_authorization_credentials()

    print(f"Authorizing new athlete using {app_name}...")

    url = (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={credentials['client_id']}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        "&approval_prompt=force"
        "&scope=read,activity:read_all"
    )

    return redirect(url)


def callback():

    code = request.args.get("code")

    # Determine which Strava App is currently being used
    app_name, _ = get_authorization_credentials()

    token = exchange_code_for_token(code)

    athlete_json = token["athlete"]

    athlete = Athlete.query.filter_by(
        athlete_id=athlete_json["id"]
    ).first()

    if athlete is None:
        athlete = Athlete(
            athlete_id=athlete_json["id"]
        )

    athlete.firstname = athlete_json["firstname"]
    athlete.lastname = athlete_json["lastname"]

    athlete.access_token = token["access_token"]
    athlete.refresh_token = token["refresh_token"]
    athlete.expires_at = token["expires_at"]

    db.session.add(athlete)
    db.session.commit()

    return f"""
    <html>
        <body style="font-family:Arial;padding:40px">

        <h2>✅ Welcome {athlete.firstname}!</h2>

        <p>Your account has been connected successfully.</p>

        <p><b>Athlete ID:</b> {athlete.athlete_id}</p>

        <p><b>Authorized using:</b> {app_name}</p>

        <p>Your credentials have been stored in the database.</p>

        <hr>

        <h3>Next Step</h3>

        <p>Add <b>{athlete.firstname}</b> to the appropriate application in:</p>

        <pre>settings/strava_apps.yml</pre>

        </body>
    </html>
    """
