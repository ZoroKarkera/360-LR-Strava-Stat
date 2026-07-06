from models import Activity
from database import db
from strava_client import get_recent_activities


SUPPORTED_TYPES = {
    "Run",
    "TrailRun",
}


def sync_recent_activities(athlete, limit=30):

    print(f"\nSyncing activities for {athlete.firstname}...\n")

    activities = get_recent_activities(
        athlete.access_token,
        limit=limit,
    )

    imported = 0
    skipped = 0

    for activity in activities:

        activity_type = str(activity.type)

        if activity_type not in SUPPORTED_TYPES:
            skipped += 1
            continue

        exists = Activity.query.get(activity.id)

        if exists:
            continue

        db_activity = Activity(
            activity_id=activity.id,
            athlete_id=athlete.athlete_id,

            name=activity.name,
            activity_type=activity_type,

            start_date=activity.start_date,
            timezone=str(activity.timezone),

            distance=float(activity.distance),

            moving_time=int(activity.moving_time.total_seconds()),
            elapsed_time=int(activity.elapsed_time.total_seconds()),

            total_elevation_gain=float(activity.total_elevation_gain),

            average_speed=float(activity.average_speed)
            if activity.average_speed
            else None,

            max_speed=float(activity.max_speed)
            if activity.max_speed
            else None,

            average_heartrate=activity.average_heartrate,
            max_heartrate=activity.max_heartrate,

            average_cadence=activity.average_cadence,

            average_watts=activity.average_watts,
            max_watts=activity.max_watts,

            kilojoules=activity.kilojoules,

            trainer=activity.trainer,
            commute=activity.commute,
        )

        db.session.add(db_activity)

        imported += 1

    db.session.commit()

    print(f"Imported : {imported}")
    print(f"Skipped  : {skipped}")
