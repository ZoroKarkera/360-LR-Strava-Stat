import html
import os

from models import Activity, Athlete
from statistics import (
    get_current_week_start,
    get_heatmap,
    get_leaderboard,
    get_recent_runs,
    get_report_start_date,
    get_summary,
)


REPORT_DIR = "reports"
HTML_FILE = "360_Long_Runners_Dashboard.html"
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def generate_dashboard(filename=None):
    """Generate a self-contained HTML dashboard and return the saved path."""
    output_path = filename or os.path.join(REPORT_DIR, HTML_FILE)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    report_start = get_report_start_date()
    week_start = get_current_week_start()

    summary = get_summary(start_date=report_start)
    leaderboard = get_leaderboard(start_date=report_start)
    heatmap = get_heatmap(start_date=week_start)
    recent_runs = get_recent_runs(limit=20, start_date=report_start)
    achievements = get_achievements(leaderboard, start_date=report_start)
    date_range = get_date_range_label(report_start)

    html_text = render_dashboard(
        summary=summary,
        leaderboard=leaderboard,
        heatmap=heatmap,
        recent_runs=recent_runs,
        achievements=achievements,
        date_range=date_range,
        week_start=week_start,
    )

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(html_text)

    print(f"HTML generated: {output_path}")
    return output_path


def render_dashboard(
    summary,
    leaderboard,
    heatmap,
    recent_runs,
    achievements,
    date_range,
    week_start,
):
    max_heatmap_value = max(
        [heatmap[runner].get(day, 0) for runner in heatmap for day in DAYS] or [0]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>360 Long Runners Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172033;
      --muted: #627084;
      --line: #d8e0ea;
      --panel: #ffffff;
      --page: #f5f7fb;
      --blue: #1f4e78;
      --blue-soft: #dcebf7;
      --green: #2f855a;
      --green-soft: #dff3e8;
      --gold: #b7791f;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background: var(--page);
      color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}

    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}

    header {{
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 20px;
      padding: 26px 28px;
      background: var(--blue);
      color: white;
      border-radius: 8px;
    }}

    h1, h2, p {{ margin: 0; }}

    h1 {{
      font-size: clamp(28px, 5vw, 44px);
      line-height: 1.05;
      letter-spacing: 0;
    }}

    header p {{
      margin-top: 8px;
      color: #d9e8f5;
      font-size: 15px;
    }}

    .generated {{
      color: #d9e8f5;
      font-size: 13px;
      white-space: nowrap;
    }}

    section {{
      margin-top: 26px;
    }}

    h2 {{
      margin-bottom: 12px;
      font-size: 19px;
      color: var(--blue);
    }}

    .summary {{
      display: grid;
      grid-template-columns: repeat(5, minmax(130px, 1fr));
      gap: 12px;
    }}

    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      min-height: 92px;
    }}

    .card span {{
      display: block;
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
    }}

    .card strong {{
      display: block;
      margin-top: 8px;
      font-size: 25px;
      color: var(--ink);
    }}

    .grid {{
      display: grid;
      grid-template-columns: minmax(280px, 0.8fr) minmax(520px, 1.2fr);
      gap: 22px;
      align-items: start;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      font-size: 14px;
    }}

    th {{
      background: var(--blue);
      color: white;
      font-weight: 700;
      text-align: left;
      padding: 10px 12px;
    }}

    td {{
      border-top: 1px solid var(--line);
      padding: 10px 12px;
      vertical-align: top;
    }}

    tbody tr:nth-child(even) {{
      background: #f8fafc;
    }}

    .number {{
      text-align: right;
      font-variant-numeric: tabular-nums;
    }}

    .heat {{
      text-align: center;
      font-variant-numeric: tabular-nums;
      border-left: 1px solid #edf1f5;
    }}

    .activity {{
      max-width: 320px;
    }}

    .empty {{
      padding: 18px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--muted);
      font-style: italic;
    }}

    @media (max-width: 900px) {{
      header {{
        display: block;
      }}

      .generated {{
        margin-top: 14px;
        white-space: normal;
      }}

      .summary {{
        grid-template-columns: repeat(2, minmax(140px, 1fr));
      }}

      .grid {{
        grid-template-columns: 1fr;
      }}

      .table-wrap {{
        overflow-x: auto;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>360 Long Runners</h1>
        <p>{escape(date_range)}</p>
      </div>
      <div class="generated">Generated from Strava club activity data</div>
    </header>

    <section>
      <h2>Club Summary</h2>
      <div class="summary">
        {summary_cards(summary)}
      </div>
    </section>

    <section class="grid equal">
      <div>
        <h2>Leaderboard Since 01-Jun</h2>
        {leaderboard_table(leaderboard)}
      </div>
      <div>
        <h2>Current Week Heatmap ({escape(week_start.strftime('%d-%b'))})</h2>
        {heatmap_table(heatmap, max_heatmap_value)}
      </div>
    </section>

    <section class="grid">
      <div>
        <h2>Achievements Since 01-Jun</h2>
        {achievements_table(achievements)}
      </div>
      <div>
        <h2>Recent Activities Since 01-Jun</h2>
        {recent_runs_table(recent_runs)}
      </div>
    </section>
  </main>
</body>
</html>
"""


def summary_cards(summary):
    cards = [
        ("Distance", f"{summary['distance']:.1f} km"),
        ("Runs", summary["runs"]),
        ("Members", summary["runners"]),
        ("Elevation", f"{summary['elevation']:.0f} m"),
        ("Avg HR", summary["avg_hr"] or "-"),
    ]

    return "\n".join(
        f'<article class="card"><span>{escape(label)}</span><strong>{escape(value)}</strong></article>'
        for label, value in cards
    )


def leaderboard_table(leaderboard, empty_message="No leaderboard data yet."):
    if not leaderboard:
        return f'<div class="empty">{escape(empty_message)}</div>'

    rows = []
    for rank, runner in enumerate(leaderboard, start=1):
        rows.append(
            "<tr>"
            f"<td>{rank}</td>"
            f"<td>{escape(runner['runner'])}</td>"
            f"<td class=\"number\">{runner['distance']:.1f} km</td>"
            f"<td class=\"number\">{runner['runs']}</td>"
            "</tr>"
        )

    return table(
        ["Rank", "Runner", "Distance", "Runs"],
        rows,
    )


def heatmap_table(heatmap, max_value):
    if not heatmap:
        return '<div class="empty">No heatmap data yet.</div>'

    rows = []
    for runner in sorted(heatmap.keys()):
        total = 0
        cells = [f"<td>{escape(runner)}</td>"]
        for day in DAYS:
            distance = round(heatmap[runner].get(day, 0), 1)
            total += distance
            cells.append(
                f'<td class="heat" style="{heat_style(distance, max_value)}">'
                f"{distance:.1f}</td>"
            )
        cells.append(f'<td class="number">{total:.1f} km</td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")

    return '<div class="table-wrap">' + table(["Runner"] + DAYS + ["Total"], rows) + "</div>"


def achievements_table(achievements):
    if not achievements:
        return '<div class="empty">No achievements yet.</div>'

    rows = [
        "<tr>"
        f"<td>{escape(item['metric'])}</td>"
        f"<td>{escape(item['winner'])}</td>"
        f"<td>{escape(item['value'])}</td>"
        "</tr>"
        for item in achievements
    ]

    return table(["Metric", "Winner", "Value"], rows)


def recent_runs_table(recent_runs):
    if not recent_runs:
        return '<div class="empty">No recent runs yet.</div>'

    rows = []
    for activity in recent_runs:
        rows.append(
            "<tr>"
            f"<td>{escape(activity['date'])}</td>"
            f"<td>{escape(activity['runner'])}</td>"
            f"<td class=\"activity\">{escape(activity['activity'])}</td>"
            f"<td class=\"number\">{activity['distance']:.2f} km</td>"
            f"<td class=\"number\">{escape(activity['pace'])}</td>"
            f"<td class=\"number\">{format_optional(activity['elevation'], 'm')}</td>"
            f"<td class=\"number\">{format_optional(activity['hr'], '')}</td>"
            "</tr>"
        )

    return '<div class="table-wrap">' + table(
        ["Date", "Runner", "Activity", "Distance", "Pace", "Elev", "HR"],
        rows,
    ) + "</div>"


def table(headers, rows):
    header_html = "".join(f"<th>{escape(header)}</th>" for header in headers)
    return (
        "<table>"
        f"<thead><tr>{header_html}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
    )


def get_achievements(leaderboard, start_date=None):
    query = Activity.query
    if start_date is not None:
        query = query.filter(Activity.start_date >= start_date)

    activities = query.order_by(Activity.start_date.desc()).all()
    if not activities:
        return []

    longest_run = max(activities, key=lambda item: item.distance or 0)
    highest_elevation = max(activities, key=lambda item: item.total_elevation_gain or 0)
    hr_activities = [activity for activity in activities if activity.average_heartrate]
    lowest_hr = min(hr_activities, key=lambda item: item.average_heartrate) if hr_activities else None
    most_runs = max(leaderboard, key=lambda item: item["runs"]) if leaderboard else None

    achievements = [
        {
            "metric": "Longest Run",
            "winner": runner_name(longest_run),
            "value": f"{(longest_run.distance or 0) / 1000:.2f} km",
        },
        {
            "metric": "Most Runs",
            "winner": most_runs["runner"] if most_runs else "-",
            "value": f"{most_runs['runs']} runs" if most_runs else "-",
        },
        {
            "metric": "Highest Elevation",
            "winner": runner_name(highest_elevation),
            "value": f"{highest_elevation.total_elevation_gain or 0:.0f} m",
        },
    ]

    if lowest_hr:
        achievements.append(
            {
                "metric": "Lowest Average HR",
                "winner": runner_name(lowest_hr),
                "value": f"{lowest_hr.average_heartrate:.1f} bpm",
            }
        )

    return achievements


def get_date_range_label(report_start):
    last_activity = (
        Activity.query
        .filter(Activity.start_date >= report_start)
        .order_by(Activity.start_date.desc())
        .first()
    )

    start_label = report_start.strftime("%d-%b-%Y")

    if not last_activity:
        return f"{start_label} to today"

    return (
        f"{start_label} to "
        f"{last_activity.start_date.strftime('%d-%b-%Y')}"
    )


def runner_name(activity):
    athlete = Athlete.query.get(activity.athlete_id)
    return athlete.firstname if athlete else "Unknown"


def heat_style(value, max_value):
    if not value or not max_value:
        return "background: #ffffff;"

    intensity = min(value / max_value, 1)
    alpha = 0.18 + (0.62 * intensity)
    return f"background: rgba(47, 133, 90, {alpha:.2f});"


def format_optional(value, suffix):
    if value is None:
        return ""

    if isinstance(value, float):
        text = f"{value:.1f}"
    else:
        text = str(value)

    return f"{text} {suffix}".strip()


def escape(value):
    return html.escape(str(value), quote=True)
