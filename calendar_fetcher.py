import requests
import json
import time
from datetime import datetime, timedelta
import os
import sys

LOCK_FILE = "/tmp/calendar_fetcher.lock"

if os.path.exists(LOCK_FILE):
    print("❌ Script already running. Exiting.")
    sys.exit()

# Create lock file
with open(LOCK_FILE, "w") as f:
    f.write(str(os.getpid()))



# ==== CONFIG ====
CALENDAR_URL = "https://script.google.com/macros/s/AKfycbzToHBc460atRcFYo1QqhMNzp8KirPGk4iuGY1QFid7Y5f-uUZbvaCtZMfpOvcJjay-/exec"
OUTPUT_FILE = "/home/96a/Desktop/calendar_events.json"
REFRESH_INTERVAL = 30
RIYADH_OFFSET = timedelta(hours=3)

# ==== LOAD SAVED EVENTS ====
def load_saved_events():
    try:
        with open(OUTPUT_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# ==== FETCH EVENTS FROM GOOGLE SCRIPT ====
def fetch_calendar_events():
    try:
        response = requests.get(CALENDAR_URL)
        response.raise_for_status()
        events = response.json()

        now = datetime.utcnow() + RIYADH_OFFSET
        today = now.date()

        valid_events = []

        for e in events:
            try:
                # Convert ISO 8601 Z-time (UTC) to Riyadh local naive datetime
                start_time_utc = datetime.fromisoformat(e["start"].replace("Z", "+00:00"))
                start_time_riyadh = start_time_utc + RIYADH_OFFSET
                start_time_naive = start_time_riyadh.replace(tzinfo=None)

                print(f"🕒 Event: {e['summary']} at {start_time_naive.strftime('%Y-%m-%d %H:%M')} | Now: {now.strftime('%Y-%m-%d %H:%M')}")

                if start_time_naive.date() == today:
                    valid_events.append(e)
                else:
                    print(f"⏩ Skipping: {e['summary']} — Not today")

            except Exception as err:
                print(f"⚠️ Skipping malformed event: {e.get('summary', '?')} - Error: {err}")

        return valid_events

    except Exception as e:
        print("❌ Error fetching calendar events:", e)
        return []

# ==== COMPARE OLD AND NEW ====
def events_are_different(old, new):
    return json.dumps(old, sort_keys=True) != json.dumps(new, sort_keys=True)

# ==== SAVE EVENTS TO FILE ====
def save_events(events):
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(events, f, indent=2)

def main():
    print("📅 Calendar Fetcher Started.")

    try:
        while True:
            print("\n🔄 Checking for new events...")
            current_events = fetch_calendar_events()

            print(f"📄 Writing the following events ({len(current_events)}):")
            for e in current_events:
                print(f"  - {e['summary']} at {e['start']}")
            save_events(current_events)
            print("💾 Events saved to:", OUTPUT_FILE)

            time.sleep(REFRESH_INTERVAL)

    except KeyboardInterrupt:
        print("\n⛔ Interrupted manually.")
    finally:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
        print("🧹 Lock file removed. Exiting.")

if __name__ == "__main__":
    main()
