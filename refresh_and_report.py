import argparse

from automation import DEFAULT_RECIPIENT, run_workflow


def main():
    parser = argparse.ArgumentParser(
        description="Sync Strava data, generate reports, and optionally email the dated HTML report."
    )
    parser.add_argument(
        "--no-sync",
        action="store_true",
        help="Generate reports without refreshing Strava data first.",
    )
    parser.add_argument(
        "--no-email",
        action="store_true",
        help="Generate reports without sending email.",
    )
    parser.add_argument(
        "--recipient",
        default=DEFAULT_RECIPIENT,
        help="Email recipient for the HTML report.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Number of recent Strava activities to fetch per athlete.",
    )

    args = parser.parse_args()

    paths = run_workflow(
        sync=not args.no_sync,
        email=not args.no_email,
        recipient=args.recipient,
        limit=args.limit,
    )

    print("\nGenerated files:")
    print(f"Excel: {paths['excel']}")
    print(f"Latest HTML: {paths['html_latest']}")
    print(f"Dated HTML: {paths['html_dated']}")


if __name__ == "__main__":
    main()
