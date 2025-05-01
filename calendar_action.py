import json
import time
import threading
import RPi.GPIO as GPIO
from datetime import datetime, timedelta, timezone
import os
import sys

LOCK_FILE = "/tmp/calendar_action.lock"

if os.path.exists(LOCK_FILE):
    print("❌ Script already running. Exiting.")
    sys.exit()

# Create lock file
with open(LOCK_FILE, "w") as f:
    f.write(str(os.getpid()))


with open("/home/96a/Desktop/action_ping.txt", "a") as log:
    log.write("✅ Action script started via cron at " + str(datetime.now()) + "\n")

# ==== CONFIG ====
EVENTS_FILE = "/home/96a/Desktop/calendar_events.json"
CHECK_INTERVAL = 30  # seconds
RELAY_PIN = 4
BUZZER_PIN = 17
BUTTON_BUZZER = 23
BUTTON_RELAY = 24
TRIGGER_OFFSET = 5 * 60  # Trigger 5 minutes before event (in seconds)
RIYADH_OFFSET = timedelta(hours=3)
RIYADH_TZ = timezone(RIYADH_OFFSET)

# ==== GPIO SETUP ====
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(BUTTON_BUZZER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_RELAY, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(RELAY_PIN, GPIO.LOW)
GPIO.output(BUZZER_PIN, GPIO.LOW)

buzzer_on = False
relay_on = False
gpio_on = False
triggered_events = set()

# ==== HELPERS ====

def is_am_time(dt):
    return 0 <= dt.hour < 12  # Treat 00:00–11:59 as AM

def short_buzzer():
    global buzzer_on
    print("🔈 Short buzzer (PM event)")
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    buzzer_on = True
    time.sleep(0.3)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def load_events():
    try:
        with open(EVENTS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print("⚠️ Could not load events:", e)
        return []

def monitor_buttons_continuous():
    global gpio_on

    while True:
        if GPIO.input(BUTTON_BUZZER) == GPIO.LOW:
            print("🔘 Button Pressed: BUZZER OFF")
            GPIO.output(BUZZER_PIN, GPIO.LOW)

        if GPIO.input(BUTTON_RELAY) == GPIO.LOW:
            print("🔘 Button Pressed: RELAY OFF")
            GPIO.output(RELAY_PIN, GPIO.LOW)

        if GPIO.input(BUTTON_BUZZER) == GPIO.LOW or GPIO.input(BUTTON_RELAY) == GPIO.LOW:
            gpio_on = False

        time.sleep(0.1)  # check 10x per second




def stop_action():
    global gpio_on, relay_on, buzzer_on
    print(f"🔕 STOPPING RELAY & BUZZER manually")
    GPIO.output(RELAY_PIN, GPIO.LOW)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    gpio_on = False
    relay_on = False
    buzzer_on = False

# ==== BACKGROUND THREAD TO LISTEN FOR 'off' ====
def listen_for_manual_off():
    while True:
        cmd = input("Type 'off' to stop GPIOs: ").strip().lower()
        if cmd == "off" and gpio_on:
            stop_action()

# ==== MAIN LOOP ====

# Start the listener in the background
threading.Thread(target=listen_for_manual_off, daemon=True).start()
threading.Thread(target=monitor_buttons_continuous, daemon=True).start()


try:
    print("📅 Calendar Event Action Script Running...\n")
    while True:
        now = datetime.now()  # Local time (assumed to be Riyadh)
        events = load_events()

        for event in events:
            try:
                event_id = event["summary"] + event["start"]
                if event_id in triggered_events:
                    continue

                # Convert UTC time to Riyadh local time
                utc_start = datetime.fromisoformat(event["start"].replace("Z", "+00:00"))
                start = utc_start.astimezone(RIYADH_TZ).replace(tzinfo=None)

                # Trigger time = 5 minutes before event
                trigger_time = start - timedelta(seconds=TRIGGER_OFFSET)
                time_diff = (trigger_time - now).total_seconds()

                print(f"🔍 Checking: {event['summary']} | Event Time: {start.strftime('%H:%M')} | Trigger At: {trigger_time.strftime('%H:%M')} | Now: {now.strftime('%H:%M')} | Δt: {int(time_diff)}s")

                if time_diff <= 0:
                    if time_diff > -CHECK_INTERVAL:
                        print(f"✅ Triggering now: {event['summary']}")

                        if is_am_time(start):
                            print("🕗 AM event — turning ON buzzer and light.")
                            GPIO.output(RELAY_PIN, GPIO.HIGH)
                            GPIO.output(BUZZER_PIN, GPIO.HIGH)
                            relay_on = True
                            buzzer_on = True
                            gpio_on = True
                        else:
                            short_buzzer()

                    triggered_events.add(event_id)
                    continue

            except Exception as e:
                print(f"⚠️ Skipped event due to error: {e}")

        time.sleep(CHECK_INTERVAL)

except KeyboardInterrupt:
    print("\n⛔ Stopped manually.")
finally:
    GPIO.output(RELAY_PIN, GPIO.LOW)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    GPIO.cleanup()
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    print("🧹 GPIO cleaned and lock file removed.")
