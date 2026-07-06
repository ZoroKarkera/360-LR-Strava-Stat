from pathlib import Path
import shutil
import subprocess


PROJECT_DIR = Path(__file__).resolve().parent
PLIST_NAME = "com.runboard.daily-report.plist"
SOURCE_PLIST = PROJECT_DIR / PLIST_NAME
TARGET_DIR = Path.home() / "Library" / "LaunchAgents"
TARGET_PLIST = TARGET_DIR / PLIST_NAME


def main():
    (PROJECT_DIR / "logs").mkdir(exist_ok=True)
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE_PLIST, TARGET_PLIST)

    subprocess.run(["launchctl", "unload", str(TARGET_PLIST)], check=False)
    subprocess.run(["launchctl", "load", str(TARGET_PLIST)], check=True)

    print(f"Installed daily RunBoard automation: {TARGET_PLIST}")
    print("Schedule: every day at 9:00 PM")


if __name__ == "__main__":
    main()
