from flask import Flask, redirect, request
from dotenv import load_dotenv
import os
from stravalib.client import Client

# Load environment variables
load_dotenv()

CLIENT_ID = int(os.getenv("CLIENT_ID"))
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <html>
        <head>
            <title>RunBoard</title>
        </head>
        <body style="font-family: Arial; padding: 40px;">
            <h1>🏃 RunBoard</h1>

            <p>Welcome to RunBoard.</p>

            <a href="/login">
                <button style="padding:10px 20px;font-size:16px;">
                    Login with Strava
                </button>
            </a>
        </body>
    </html>
    """


@app.route("/login")
def login():

    client = Client()

    authorize_url = client.authorization_url(
        client_id=CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=["read", "activity:read_all"],
        approval_prompt="force"
    )

    return redirect(authorize_url)


@app.route("/callback")
def callback():

    code = request.args.get("code")
    scope = request.args.get("scope")

    return f"""
    <html>
        <head>
            <title>RunBoard</title>
        </head>

        <body style="font-family: Arial; padding:40px;">

            <h2>✅ OAuth Successful</h2>

            <p>RunBoard successfully authenticated with Strava.</p>

            <hr>

            <p><b>Authorization Code</b></p>

            <textarea rows="5" cols="90">{code}</textarea>

            <p><b>Granted Scope</b></p>

            <pre>{scope}</pre>

            <hr>

            <p>Next milestone: Exchange this authorization code for an access token.</p>

        </body>
    </html>
    """


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)