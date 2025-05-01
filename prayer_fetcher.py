import requests
import json
import os
from datetime import datetime
import time


# ==== CONFIG ====
CITY = "Riyadh"
COUNTRY = "SA"
API_URL = f"https://api.aladhan.com/v1/timingsByCity?city={CITY}&country={COUNTRY}&method=4"
OUTPUT_FILE = "/home/96a/Desktop/prayer_times.json"
LOCK_FILE = "/tmp/prayer_fetcher.lock"

# ==== LOCK FILE CHECK ====
if os.path.exists(LOCK_FILE):
    print("❌ prayer_fetcher.py is already running. Exiting.")
    exit()

with open(LOCK_FILE, "w") as f:
    f.write(str(os.getpid()))

try:
    print("📿 Fetching prayer times...")

    # to try 3 times fetching from api if 1st fails, it happened once so needed solution
    response = requests.get(API_URL)
    for attempt in range(3):
        try:
            response = requests.get(API_URL, timeout=10)
            break
        except requests.exceptions.RequestException as e:
            print(f"🌐 Attempt {attempt + 1} failed. Retrying in 10s...")
            time.sleep(10)
    else:
        raise SystemExit("❌ Failed to fetch prayer times after 3 attempts.")

    data = response.json()

    if data["code"] != 200:
        raise ValueError("❌ API error")

    timings = data["data"]["timings"]
    today = {
        "date": data["data"]["date"]["gregorian"]["date"],
        "Fajr": timings["Fajr"],
        "Dhuhr": timings["Dhuhr"],
        "Asr": timings["Asr"],
        "Maghrib": timings["Maghrib"],
        "Isha": timings["Isha"]
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(today, f, indent=2)

    print("✅ Prayer times saved to:", OUTPUT_FILE)

finally:
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    print("🧹 Lock file removed.")
