from flask import redirect, request
from models import Athlete
from database import db
from strava_client import exchange_code_for_token

import os

CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")


def login():

    url = (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        "&approval_prompt=force"
        "&scope=read,activity:read_all"
    )

    return redirect(url)


def callback():

    code = request.args.get("code")

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

        <p>Your credentials have been stored in the database.</p>

        </body>
    </html>
    """
