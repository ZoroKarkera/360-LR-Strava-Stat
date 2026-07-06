# RunBoard Automation

## Manual refresh

Sync latest Strava activities, generate Excel, generate latest HTML, generate dated HTML, and send email:

```bash
/Users/chirag/StravaClub/.venv/bin/python /Users/chirag/StravaClub/refresh_and_report.py
```

Generate reports without email:

```bash
/Users/chirag/StravaClub/.venv/bin/python /Users/chirag/StravaClub/refresh_and_report.py --no-email
```

Generate reports without syncing Strava first:

```bash
/Users/chirag/StravaClub/.venv/bin/python /Users/chirag/StravaClub/refresh_and_report.py --no-sync
```

## Daily schedule

The macOS LaunchAgent is installed at:

```text
/Users/chirag/Library/LaunchAgents/com.runboard.daily-report.plist
```

It runs every day at 9:00 PM and writes logs to:

```text
/Users/chirag/StravaClub/logs/daily_report.out.log
/Users/chirag/StravaClub/logs/daily_report.err.log
```

## Email setup

Add SMTP settings to `/Users/chirag/StravaClub/.env`.

For Gmail, use an app password, not your normal Gmail password:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_FROM=your_email@gmail.com
```

Reports are sent to `chirukarkera@gmail.com` by default.
