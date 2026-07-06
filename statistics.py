from collections import defaultdict
from datetime import datetime, time, timedelta

from models import Activity, Athlete


REPORT_START_MONTH = 6
REPORT_START_DAY = 1


def get_report_start_date(reference_date=None):
    reference_date = reference_date or datetime.now()
    return datetime.combine(
        reference_date.replace(
            month=REPORT_START_MONTH,
            day=REPORT_START_DAY,
        ).date(),
        time.min,
    )


def get_current_week_start(reference_date=None):
    reference_date = reference_date or datetime.now()
    week_start = reference_date.date() - timedelta(days=reference_date.weekday())
    return datetime.combine(week_start, time.min)


def get_summary(start_date=None, end_date=None):
    activities = get_activities(start_date=start_date, end_date=end_date)

    hr_values = [
        activity.average_heartrate
        for activity in activities
        if activity.average_heartrate
    ]

    return {
        "runners": Athlete.query.count(),
        "runs": len(activities),
        "distance": round(sum((a.distance or 0) for a in activities) / 1000, 1),
        "elevation": round(sum((a.total_elevation_gain or 0) for a in activities)),
        "avg_hr": round(sum(hr_values) / len(hr_values), 1) if hr_values else 0,
    }


def get_leaderboard(start_date=None, end_date=None):
    leaderboard = []

    for athlete in Athlete.query.all():
        activities = get_activities(
            athlete_id=athlete.athlete_id,
            start_date=start_date,
            end_date=end_date,
        )

        distance = sum((a.distance or 0) for a in activities) / 1000

        if not activities:
            continue

        leaderboard.append(
            {
                "runner": athlete.firstname,
                "distance": round(distance, 1),
                "runs": len(activities),
            }
        )

    leaderboard.sort(key=lambda item: (item["distance"], item["runs"]), reverse=True)

    return leaderboard


def get_weekly_leaderboard(reference_date=None):
    return get_leaderboard(start_date=get_current_week_start(reference_date))


def get_recent_runs(limit=20, start_date=None, end_date=None):
    rows = []

    query = filtered_activity_query(start_date=start_date, end_date=end_date)

    activities = query.order_by(Activity.start_date.desc()).limit(limit).all()

    for activity in activities:
        athlete = Athlete.query.get(activity.athlete_id)
        pace = ""

        if activity.distance and activity.moving_time:
            pace_sec = activity.moving_time / (activity.distance / 1000)
            mins = int(pace_sec // 60)
            secs = int(pace_sec % 60)
            pace = f"{mins}:{secs:02d}"

        rows.append(
            {
                "date": activity.start_date.strftime("%d-%b"),
                "runner": athlete.firstname if athlete else "Unknown",
                "activity": activity.name,
                "distance": round((activity.distance or 0) / 1000, 2),
                "pace": pace,
                "elevation": activity.total_elevation_gain,
                "hr": activity.average_heartrate,
            }
        )

    return rows


def get_heatmap(start_date=None, end_date=None):
    heatmap = defaultdict(lambda: defaultdict(float))

    activities = get_activities(start_date=start_date, end_date=end_date)

    for activity in activities:
        athlete = Athlete.query.get(activity.athlete_id)
        runner = athlete.firstname if athlete else "Unknown"
        day = activity.start_date.strftime("%a")
        heatmap[runner][day] += (activity.distance or 0) / 1000

    return heatmap


def get_activities(athlete_id=None, start_date=None, end_date=None):
    query = filtered_activity_query(
        athlete_id=athlete_id,
        start_date=start_date,
        end_date=end_date,
    )
    return query.order_by(Activity.start_date.desc()).all()


def filtered_activity_query(athlete_id=None, start_date=None, end_date=None):
    start_date = start_date or get_report_start_date()
    query = Activity.query

    if athlete_id is not None:
        query = query.filter(Activity.athlete_id == athlete_id)

    if start_date is not None:
        query = query.filter(Activity.start_date >= start_date)

    if end_date is not None:
        query = query.filter(Activity.start_date <= end_date)

    return query
