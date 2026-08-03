import html
import os
from datetime import timezone, timedelta
from datetime import datetime as dt

from models import Activity, Athlete
from statistics import (
    get_heatmap,
    get_leaderboard,
    get_week_start_for_cw,
    get_recent_runs,
    get_report_start_date,
    get_summary,
    to_utc_naive_from_ist,
)


REPORT_DIR = "reports"
HTML_FILE = "360_Long_Runners_Dashboard.html"
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
IST = timezone(timedelta(hours=5, minutes=30))
FORCE_STANDBY_NOTE_PREVIEW = False


def to_ist(dt_utc):
  return dt_utc.replace(tzinfo=timezone.utc).astimezone(IST)


def should_show_standby_note(week_start=None, now_ist=None):
  if FORCE_STANDBY_NOTE_PREVIEW:
    return True

  now_ist = now_ist or dt.now(IST)
  current_week_start = now_ist.date() - timedelta(days=now_ist.weekday())

  if week_start is not None:
    selected_week_start = week_start.date()
    if selected_week_start < current_week_start:
      return True

  return now_ist.weekday() == 6 and now_ist.hour >= 13


def generate_dashboard(filename=None, target_cw=None):
    """Generate a self-contained HTML dashboard and return the saved path."""
    output_path = filename or os.path.join(REPORT_DIR, HTML_FILE)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    report_start = get_report_start_date()
    week_start = get_week_start_for_cw(target_cw)
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)

    query_start = to_utc_naive_from_ist(report_start)
    week_start_utc = to_utc_naive_from_ist(week_start)
    week_end_utc = to_utc_naive_from_ist(week_end)

    summary = get_summary(start_date=query_start, end_date=week_end_utc)
    leaderboard = get_leaderboard(start_date=query_start, end_date=week_end_utc)
    heatmap = get_heatmap(start_date=week_start_utc, end_date=week_end_utc)
    recent_runs = get_recent_runs(limit=20, start_date=query_start, end_date=week_end_utc)
    achievements = get_achievements(leaderboard, start_date=query_start, end_date=week_end_utc)
    date_range = get_date_range_label(report_start, query_start_date=query_start, end_date=week_end_utc)

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
    achievers = get_achievement_winners(achievements)

    IST = timezone(timedelta(hours=5, minutes=30))
    generated_at = dt.now(IST).strftime("%d %b %Y, %I:%M %p IST")

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
      margin-top: 6px;
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
      grid-template-columns: repeat(4, minmax(130px, 1fr));
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

    .runner-cell {{
      white-space: nowrap;
    }}

    .runner-active .runner-cell {{
      background: #f4fbf6;
    }}

    .runner-idle .runner-cell {{
      background: repeating-linear-gradient(
        135deg,
        #fff2f1 0,
        #fff2f1 6px,
        #ffe5e2 6px,
        #ffe5e2 12px
      );
    }}

    .runner-name-active {{
      color: #1f7a4b;
      font-weight: 700;
    }}

    .runner-name-idle {{
      color: #9f2f2f;
      font-weight: 700;
    }}

    .status-legend {{
      margin-bottom: 8px;
      display: flex;
      gap: 14px;
      flex-wrap: wrap;
      font-size: 12px;
      color: #5b6470;
    }}

    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .legend-swatch {{
      width: 12px;
      height: 12px;
      border-radius: 2px;
      display: inline-block;
      border: 1px solid #8f98a3;
    }}

    .legend-active {{
      background: #2e945c;
    }}

    .legend-idle {{
      background: repeating-linear-gradient(
        135deg,
        #d74f3a 0,
        #d74f3a 4px,
        #ffd5cf 4px,
        #ffd5cf 8px
      );
    }}

    .status-pill {{
      display: inline-block;
      margin-left: 6px;
      padding: 2px 7px;
      border-radius: 999px;
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.2px;
      vertical-align: middle;
    }}

    .status-pill-active {{
      color: #ffffff;
      background: #1f7a4b;
      border: 1px solid #155f39;
    }}

    .status-pill-idle {{
      color: #ffffff;
      background: #a1281f;
      border: 1px solid #7c1e17;
    }}

    .achiever-crown {{
      margin-left: 6px;
      font-size: 12px;
      color: #b7791f;
      vertical-align: middle;
    }}

    .standby-span {{
      text-align: center;
      font-style: italic;
      font-weight: 600;
      color: #6a7280;
      background: #f7f9fc;
      letter-spacing: 0.15px;
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
        <p>Strava data from {escape(date_range)}</p>
        <p class="generated">Last updated: {generated_at}</p>
      </div>
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
        <h2>Week Heatmap ({escape(week_start.strftime('%d-%b'))})</h2>
        {heatmap_table(heatmap, max_heatmap_value, week_start=week_start)}
      </div>
    </section>

    <section class="grid">
      <div>
        <h2>Achievements Since 01-Jun</h2>
        {achievements_table(achievements, achievers)}
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


def heatmap_table(heatmap, max_value, week_start=None):
    if Athlete.query.count() == 0:
        return '<div class="empty">No heatmap data yet.</div>'

    rows = []
    show_standby_note = should_show_standby_note(week_start=week_start)
    
    # Calculate totals first to find top 3
    runner_totals = {}
    athletes = (
        Athlete.query
        .order_by(Athlete.firstname.asc())
        .all()
    )
    
    for athlete in athletes:
        runner = athlete.firstname
        total = 0
        for day in DAYS:
            distance = round(
                heatmap.get(runner, {}).get(day, 0),
                1
            )
            total += distance
        runner_totals[runner] = total
    
    # Get top 3 runners by distance
    top_3 = sorted(runner_totals.items(), key=lambda x: x[1], reverse=True)[:3]
    medals = {name: ["🥇", "🥈", "🥉"][i] for i, (name, _) in enumerate(top_3)}

    for athlete in athletes:
        runner = athlete.firstname
        total = runner_totals[runner]
        distances = []
        cells = []

        for day in DAYS:
            distance = round(
                heatmap.get(runner, {}).get(day, 0),
                1
            )
            distances.append(distance)

        is_zero = total == 0
        runner_label_class = "runner-name-idle" if is_zero else "runner-name-active"
        runner_display = escape(runner)
        if runner in medals:
          runner_display = f"{runner_display} {medals[runner]}"
        runner_label = f'<span class="{runner_label_class}">{runner_display}</span>'
        if total == 0:
            runner_label += '<span class="status-pill status-pill-idle">RUN STRIKE ??</span>'

        if is_zero and show_standby_note:
            cells.append(
                f'<td class="standby-span" colspan="{len(DAYS)}">Running shoes on standby</td>'
            )
        else:
            for distance in distances:
                cells.append(
                    f'<td class="heat" style="{heat_style(distance, max_value)}">'
                    f"{distance:.1f}</td>"
                )

        cells.insert(0, f'<td class="runner-cell">{runner_label}</td>')
        cells.append(f'<td class="number">{total:.1f} km</td>')
        row_class = "runner-idle" if is_zero else "runner-active"
        rows.append(f'<tr class="{row_class}">' + "".join(cells) + "</tr>")

    legend_html = (
        '<div class="status-legend">'
      '<span class="legend-item"><span class="legend-swatch legend-active"></span>Ran this week</span>'
      '<span class="legend-item"><span class="legend-swatch legend-idle"></span>Did not run this week</span>'
        '</div>'
    )

    return (
        '<div class="table-wrap">'
        + legend_html
        + table(["Runner"] + DAYS + ["Total"], rows)
        + "</div>"
    )

def achievements_table(achievements, achievers=None):
    if not achievements:
        return '<div class="empty">No achievements yet.</div>'

    rows = [
        "<tr>"
        f"<td>{escape(item['metric'])}</td>"
        f"<td>{render_runner_name(item['winner'], achievers)}</td>"
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


def get_achievements(leaderboard, start_date=None, end_date=None):
    query = Activity.query
    if start_date is not None:
        query = query.filter(Activity.start_date >= start_date)
    if end_date is not None:
        query = query.filter(Activity.start_date <= end_date)

    activities = query.order_by(Activity.start_date.desc()).all()
    if not activities:
        return []

    longest_run = max(activities, key=lambda item: item.distance or 0)
    highest_elevation = max(activities, key=lambda item: item.total_elevation_gain or 0)
    most_runs = max(leaderboard, key=lambda item: item["runs"]) if leaderboard else None

    def best_effort(target_m, margin_m=None, min_distance_m=None, max_distance_m=None):
      candidates = [
        activity for activity in activities
        if activity.distance and (activity.moving_time or activity.elapsed_time)
        and (margin_m is None or abs(activity.distance - target_m) <= margin_m)
        and (min_distance_m is None or activity.distance >= min_distance_m)
        and (max_distance_m is None or activity.distance <= max_distance_m)
      ]
      if not candidates:
        return None
      return min(
        candidates,
        key=lambda activity: (activity.moving_time or activity.elapsed_time) / (activity.distance / 1000),
      )

    def format_effort_time(activity, target_m):
      effort_seconds = activity.moving_time or activity.elapsed_time
      pace_sec = effort_seconds / (activity.distance / 1000)
      total_sec = int(round(pace_sec * (target_m / 1000)))
      mins, secs = divmod(total_sec, 60)
      hours, mins = divmod(mins, 60)
      if hours:
        return f"{hours}:{mins:02d}:{secs:02d}"
      return f"{mins}:{secs:02d}"

    fastest_5k = best_effort(5000, 500)
    fastest_10k = best_effort(10000, 500)
    fastest_21k = best_effort(21097, min_distance_m=21097, max_distance_m=24000)

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

    if fastest_5k:
        achievements.append({
            "metric": "Fastest 5k",
            "winner": runner_name(fastest_5k),
            "value": format_effort_time(fastest_5k, 5000),
        })
    if fastest_10k:
        achievements.append({
            "metric": "Fastest 10k",
            "winner": runner_name(fastest_10k),
            "value": format_effort_time(fastest_10k, 10000),
        })
    if fastest_21k:
        achievements.append({
            "metric": "Fastest 21k",
            "winner": runner_name(fastest_21k),
            "value": format_effort_time(fastest_21k, 21097),
        })

    return achievements


def get_date_range_label(report_start, query_start_date=None, end_date=None):
    query_start = query_start_date if query_start_date is not None else report_start
    query = Activity.query.filter(Activity.start_date >= query_start)
    if end_date is not None:
        query = query.filter(Activity.start_date <= end_date)

    last_activity = query.order_by(Activity.start_date.desc()).first()
    start_label = report_start.strftime("%d/%b")

    if not last_activity:
        end_label = (
            to_ist(end_date).strftime('%d/%b')
            if end_date is not None
            else dt.now(timezone(timedelta(hours=5, minutes=30))).strftime('%d/%b')
        )
        return f"{start_label} to {end_label}"

    return (
        f"{start_label} to "
        f"{to_ist(last_activity.start_date).strftime('%d/%b')}"
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


def normalize_runner_name(name):
    return " ".join(str(name or "").split()).casefold()


def get_achievement_winners(achievements):
    winners = set()
    for item in achievements or []:
        normalized = normalize_runner_name(item.get("winner"))
        if normalized and normalized not in {"-", "unknown"}:
            winners.add(normalized)
    return winners


def render_runner_name(name, achievers=None):
    safe_name = escape(name)
    if achievers and normalize_runner_name(name) in achievers:
        safe_name += '<span class="achiever-crown" title="Achievement winner">&#x1F3C6;</span>'
    return safe_name


def escape(value):
    return html.escape(str(value), quote=True)
