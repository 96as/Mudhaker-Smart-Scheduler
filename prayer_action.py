import json
import time
import threading
import RPi.GPIO as GPIO
from datetime import datetime, timedelta
import os
import sys

# ==== CONFIG ====
PRAYER_FILE = "/home/96a/Desktop/prayer_times.json"
CHECK_INTERVAL = 30  # seconds
RELAY_PIN = 4
BUZZER_PIN = 17
BUTTON_BUZZER = 23
BUTTON_RELAY = 24
TRIGGER_OFFSET_MINUTES = 5
LOCK_FILE = "/tmp/prayer_action.lock"

# ==== LOCK CHECK ====
if os.path.exists(LOCK_FILE):
    print("❌ prayer_action.py is already running. Exiting.")
    sys.exit()

with open(LOCK_FILE, "w") as f:
    f.write(str(os.getpid()))

# ==== GPIO SETUP ====
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(BUTTON_BUZZER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_RELAY, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(RELAY_PIN, GPIO.LOW)
GPIO.output(BUZZER_PIN, GPIO.LOW)

relay_on = False
buzzer_on = False
gpio_on = False
triggered = set()

# ==== HELPERS ====

def parse_time(timestr):
    return datetime.strptime(timestr, "%H:%M").replace(
        year=datetime.now().year,
        month=datetime.now().month,
        day=datetime.now().day
    )


def short_buzzer():
    global buzzer_on
    print("🔈 Short buzzer")
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    buzzer_on = True
    time.sleep(0.3)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    buzzer_on = False
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    buzzer_on = True
    time.sleep(0.3)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    buzzer_on = False
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    buzzer_on = True
    time.sleep(0.3)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    buzzer_on = False


def stop_action():
    global gpio_on, buzzer_on, relay_on
    print("🔕 Stopping GPIOs manually")
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    GPIO.output(RELAY_PIN, GPIO.LOW)
    gpio_on = False
    buzzer_on = False
    relay_on = False

def monitor_buttons():
    global gpio_on, buzzer_on, relay_on

    while True:
        if GPIO.input(BUTTON_BUZZER) == GPIO.LOW:
            time.sleep(0.05)  # debounce for 50ms
            if GPIO.input(BUTTON_BUZZER) == GPIO.LOW:
                time.sleep(0.05)  # debounce for 50ms
                if GPIO.input(BUTTON_BUZZER) == GPIO.LOW:
                    print("🔘 Button: BUZZER OFF")
                    GPIO.output(BUZZER_PIN, GPIO.LOW)
                    buzzer_on = False

        if GPIO.input(BUTTON_RELAY) == GPIO.LOW:
            time.sleep(0.05)
            if GPIO.input(BUTTON_RELAY) == GPIO.LOW:
                time.sleep(0.05)
                if GPIO.input(BUTTON_RELAY) == GPIO.LOW:
                    print("🔘 Button: RELAY OFF")
                    GPIO.output(RELAY_PIN, GPIO.LOW)
                    relay_on = False

        if not buzzer_on and not relay_on:
            gpio_on = False

        time.sleep(0.1)

def listen_for_manual_off():
    global gpio_on
    while True:
        cmd = input("Type 'off' to stop GPIOs: \n").strip().lower()
        if cmd == "off" and gpio_on:
            stop_action()

# ==== LOAD PRAYER TIMES ====
def load_prayer_times():
    try:
        with open(PRAYER_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print("⚠️ Could not load prayer times:", e)
        return {}

# ==== START THREADS ====
threading.Thread(target=listen_for_manual_off, daemon=True).start()
threading.Thread(target=monitor_buttons, daemon=True).start()

# ==== MAIN LOOP ====
try:
    print("🕌 Prayer Action Script Running...\n")

    while True:
        now = datetime.now()
        prayers = load_prayer_times()

        if not prayers:
            time.sleep(CHECK_INTERVAL)
            continue

        for name in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
            if name not in prayers:
                continue

            try:
                t = parse_time(prayers[name])
                event_id = name + prayers[name]
                if event_id in triggered:
                    continue

                trigger_time = t - timedelta(minutes=TRIGGER_OFFSET_MINUTES)
                time_diff = (trigger_time - now).total_seconds()

                print(f"🔍 {name}: {t.strftime('%H:%M')} | Trigger At: {trigger_time.strftime('%H:%M')} | Now: {now.strftime('%H:%M')} | Δt: {int(time_diff)}s")

                if 0 <= time_diff <= CHECK_INTERVAL:
                    print(f"🛐 Triggering for {name}")

                    if name == "Fajr":
                        print("🌅 Fajr: buzzer + light")
                        GPIO.output(RELAY_PIN, GPIO.HIGH)
                        GPIO.output(BUZZER_PIN, GPIO.HIGH)
                        relay_on = True
                        buzzer_on = True
                        gpio_on = True
                    else:
                        print(f"📢 {name}: short buzzer only")
                        short_buzzer()

                    triggered.add(event_id)

            except Exception as err:
                print(f"⚠️ Skipped {name}: {err}")

        time.sleep(CHECK_INTERVAL)

except KeyboardInterrupt:
    print("\n⛔ Stopped manually.")
finally:
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    GPIO.output(RELAY_PIN, GPIO.LOW)
    GPIO.cleanup()
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    print("🧹 GPIO cleaned and lock file removed.")
