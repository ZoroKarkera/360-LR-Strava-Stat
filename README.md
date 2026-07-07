# 🏃 360 Long Runners - Automated Strava Dashboard

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-success?logo=githubactions)
![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-Enabled-blue?logo=github)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite)
![Status](https://img.shields.io/badge/Status-Production-brightgreen)
![Version](https://img.shields.io/badge/Version-v1.0-orange)

An automated Strava reporting platform that synchronizes club activities, generates interactive dashboards, creates Excel reports, emails members automatically, and publishes reports using GitHub Actions.

</div>

---

# 📖 Overview

360 Long Runners Dashboard is an end-to-end automation platform built for running clubs.

Every day the system:

- Connects to Strava
- Refreshes athlete tokens
- Downloads new activities
- Stores activities in SQLite
- Generates statistics
- Produces an interactive HTML dashboard
- Creates an Excel report
- Emails the report automatically
- Publishes the latest dashboard to GitHub Pages (optional)

The project runs entirely on **GitHub Actions**, making it completely cloud-based and free to operate.

---

# ✨ Features

## 🏃 Strava Integration

- Automatic athlete synchronization
- Automatic OAuth token refresh
- Duplicate activity detection
- Historical activity storage
- Multi-athlete support
- Multi-Strava Application support
- Configurable authorization app

---

## 📊 Reports

- Interactive HTML Dashboard
- Excel Report
- Weekly Heatmaps
- Runner Statistics
- Club Leaderboards
- Historical Dashboard Snapshots

---

## 📧 Automation

- Daily scheduled execution
- Manual execution
- Email reports
- Multiple recipients
- Private distribution using BCC
- Optional GitHub Pages deployment

---

## ☁ Cloud

- GitHub Actions
- GitHub Pages
- GitHub Artifacts
- GitHub Secrets
- Feature branch workflow
- Pull Request based development

---

# 🏗 System Architecture

```text
                    GitHub Actions
             (Scheduled / Manual Run)
                       │
                       ▼
            refresh_and_report.py
                       │
                       ▼
                 automation.py
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
  Refresh Strava              Generate Reports
         │                           │
         ▼                           ▼
 Multiple Strava Apps         HTML + Excel Report
         │                           │
         ▼                           ▼
      SQLite DB               Email + Artifacts
                                       │
                                       ▼
                             GitHub Pages (Optional)
```

---

# 🔄 Complete Project Flow

```text
                    Daily Trigger
                  (21:00 IST / Manual)

                          │
                          ▼

             Load Environment Variables

                          │
                          ▼

           Load Multi Strava Configuration

                          │
                          ▼

               Load Athlete Database

                          │
                          ▼

      Determine which Strava App to use
             (per athlete)

                          │
                          ▼

             Refresh OAuth Access Token

                          │
                          ▼

            Download New Activities

                          │
                          ▼

             Store Activities (SQLite)

                          │
                          ▼

              Generate Statistics

                          │
                          ▼

            Generate HTML Dashboard

                          │
                          ▼

             Generate Excel Report

                          │
                          ▼

                Email Reports

                          │
                          ▼

              Upload Artifacts

                          │
                          ▼

         Deploy GitHub Pages (Optional)
```

---

# 📂 Repository Structure

```text
.
├── activity_sync.py
├── auth.py
├── automation.py
├── dashboard.py
├── database.py
├── excel_report.py
├── models.py
├── refresh_and_report.py
├── strava_client.py
├── strava_config.py
├── config.py
├── config/
│   └── strava_apps.yml
├── reports/
├── data/
│   └── club.db
├── .github/
│   └── workflows/
│       └── daily-report.yml
├── requirements.txt
└── README.md
```

---

# 🚀 Multi Strava Application Support

The project supports multiple Strava applications, allowing the system to scale beyond the default athlete limits.

Configuration is maintained in:

```text
config/strava_apps.yml
```

Example:

```yaml
default_authorization_app: app1

apps:

  app1:
    athletes:
      - Chirag
      - Vivek
      - Ralph
      - Vijay

  app2:
    athletes: []
```

The system automatically determines which OAuth credentials should be used for every athlete.

Switching onboarding to another Strava App requires changing only:

```yaml
default_authorization_app: app2
```

No database changes are required.

---

# ⚙ GitHub Actions

The project executes automatically every day.

```text
21:00 IST
```

It can also be started manually.

Manual workflow parameters:

- ✅ Send report to all club members
- ✅ Send report only to administrator
- ✅ Enable / Disable GitHub Pages deployment

---

# 📊 Reports Generated

Every execution generates:

- HTML Dashboard
- Excel Workbook

A dated dashboard snapshot is also archived.

Example:

```text
360_Long_Runners_Dashboard_2026-07-07.html
```

---

# 📧 Email Reports

The generated reports are automatically emailed.

Attachments include:

- HTML Dashboard
- Excel Workbook

Supports:

- Single recipient
- Multiple recipients
- BCC distribution

---

# 🌐 GitHub Pages

Optionally publishes the latest dashboard.

```text
index.html
```

The latest dashboard can be viewed directly from GitHub Pages.

---

# 🗄 Database

SQLite is used for persistent storage.

Stored information:

- Athletes
- OAuth Tokens
- Activities

Duplicate activities are automatically ignored.

---

# 🔐 Configuration

## Environment Variables

```text
CLIENT_ID
CLIENT_SECRET

CLIENT_ID_APP2
CLIENT_SECRET_APP2

REDIRECT_URI

SMTP_HOST
SMTP_PORT
SMTP_USER
SMTP_PASSWORD
SMTP_FROM

EMAIL_RECIPIENTS
```

---

## GitHub Secrets

The same values should be configured as GitHub Secrets.

No credentials are stored inside the repository.

---

# 🛠 Technology Stack

| Component | Technology |
|----------|------------|
| Language | Python 3.11 |
| Web Framework | Flask |
| ORM | SQLAlchemy |
| Database | SQLite |
| Strava API | Stravalib |
| Excel | OpenPyXL |
| Data Analysis | Pandas |
| CI/CD | GitHub Actions |
| Hosting | GitHub Pages |

---

# 🌳 Development Workflow

```text
feature/*
      │
      ▼

Pull Request

      │
      ▼

main

      │
      ▼

Nightly Automation
```

All new functionality is developed in feature branches and merged through Pull Requests to keep the production branch stable.

---

# 💡 Future Roadmap

- Weekly Summary Report
- Monthly Statistics
- Club Records
- Personal Best Detection
- Activity Maps
- Weather Integration
- Pace Trends
- PDF Report Export
- Web-based Athlete Onboarding
- Configuration Validation

---

# 📷 Screenshots

Dashboard

> *(Add dashboard screenshot here)*

Excel Report

> *(Add Excel screenshot here)*

GitHub Actions

> *(Add Actions screenshot here)*

---

# 🤝 Contributing

Contributions, ideas and feature requests are always welcome.

Feel free to fork the repository and submit a Pull Request.

---

# ❤️ Acknowledgements

Built for the **360 Long Runners** community to make club statistics, reporting and motivation fully automated.

---

<div align="center">

### 🏃 Happy Running!

*"If it isn't automated, it isn't finished."*

</div>