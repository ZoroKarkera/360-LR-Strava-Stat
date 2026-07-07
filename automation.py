import os
import shutil
import time
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
import smtplib
from config.strava_config import get_credentials

from dotenv import load_dotenv
from flask import Flask

load_dotenv()

from activity_sync import sync_recent_activities
from config import Config
from dashboard import generate_dashboard
from database import db
from excel_report import generate_excel
from models import Athlete
from strava_client import refresh_access_token


PROJECT_DIR = Path(__file__).resolve().parent
REPORT_DIR = PROJECT_DIR / "reports"
DEFAULT_RECIPIENT = "chirukarkera@gmail.com"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


def refresh_data(limit=100):
    athletes = Athlete.query.all()

    if not athletes:
        print("No athletes found. Connect at least one Strava athlete first.")
        return

    for athlete in athletes:
        ensure_fresh_token(athlete)
        sync_recent_activities(athlete, limit=limit)


def ensure_fresh_token(athlete):
    now = int(time.time())

    if athlete.expires_at and athlete.expires_at > now + 300:
        return

    if not athlete.refresh_token:
        print(f"Skipping token refresh for {athlete.firstname}: no refresh token.")
        return

    app_name, credentials = get_credentials(athlete.firstname)
    
    print(
        f"Refreshing Strava token for {athlete.firstname} ({app_name})..."
    )
    
    token = refresh_access_token(
        athlete.refresh_token,
        credentials["client_id"],
        credentials["client_secret"],
    )

    athlete.access_token = token["access_token"]
    athlete.refresh_token = token["refresh_token"]
    athlete.expires_at = token["expires_at"]

    db.session.add(athlete)
    db.session.commit()


def generate_reports():
    REPORT_DIR.mkdir(exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    dated_html = REPORT_DIR / f"360_Long_Runners_Dashboard_{today}.html"

    excel_path = Path(generate_excel())
    latest_html_path = Path(generate_dashboard())
    generate_dashboard(filename=str(dated_html))

    return {
        "excel": PROJECT_DIR / excel_path,
        "html_latest": PROJECT_DIR / latest_html_path,
        "html_dated": dated_html,
    }


def send_report_email(report_paths, recipient=DEFAULT_RECIPIENT):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM", smtp_user)

    if not all([smtp_host, smtp_user, smtp_password, sender]):
        print(
            "Email skipped: SMTP_HOST, SMTP_USER, SMTP_PASSWORD, and SMTP_FROM/SMTP_USER are required."
        )
        return False

    recipients = [r.strip() for r in recipient.split(",") if r.strip()]

    dated_html = report_paths["html_dated"]
    excel_report = report_paths["excel"]

    message = EmailMessage()
    message["Subject"] = (
        f"🏃 360 Long Runners Report - {datetime.now().strftime('%d-%b-%Y')}"
    )
    message["From"] = sender

    # Keep recipients private
    message["To"] = sender
    message["Bcc"] = ", ".join(recipients)

    message.set_content(
        f"""Hey There,

The latest 360 Long Runners report has been generated automatically.

📅 Date: {datetime.now().strftime('%d-%b-%Y')}
📎 Attached:
• HTML Dashboard
• Excel Report

Happy Running! 🏃

Your Chief
"""
    )

    # Attach HTML Dashboard
    message.add_attachment(
        dated_html.read_bytes(),
        maintype="text",
        subtype="html",
        filename=dated_html.name,
    )

    # Attach Excel Report
    message.add_attachment(
        excel_report.read_bytes(),
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=excel_report.name,
    )

    with smtplib.SMTP(smtp_host, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_user, smtp_password)
        smtp.send_message(message)

    print(f"Email sent successfully to {len(recipients)} recipient(s).")

    return True

def run_workflow(sync=True, email=True, recipient=DEFAULT_RECIPIENT, limit=100):
    app = create_app()

    with app.app_context():
        if sync:
            refresh_data(limit=limit)

        report_paths = generate_reports()

    if email:
        send_report_email(report_paths, recipient=recipient)

    return report_paths


def archive_latest_html(report_paths):
    latest_path = report_paths["html_latest"]
    dated_path = report_paths["html_dated"]

    if latest_path != dated_path:
        shutil.copyfile(latest_path, dated_path)
