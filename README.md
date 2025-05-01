# Mudhaker-Smart-Scheduler

📖 Smart IoT Event & Prayer Reminder System

Prototype for Smart Scheduler Project (7th Boeing Engineering Student Competition)
-------------------------------------------------------------------------------

📚 Overview

This project is a working prototype for a larger smart scheduler system idea, presented at the Boeing Engineering Student Competition at Alfaisal University.

It uses a Raspberry Pi to automate buzzer and light notifications based on:
	•	Google Calendar events (for scheduled tasks and activities)
	•	Daily prayer times (fetched via Aladhan API)

The system demonstrates a practical IoT assistant that helps users manage both daily schedules and prayer duties — setting the foundation for a future AI-enhanced, fully intelligent scheduling assistant.

The system operates completely automated through Python scripts and cron jobs, requiring no user intervention once deployed.
-------------------------------------------------------------------------------

🧠 System Logic

The system consists of two major modules: Calendar Reminders and Prayer Reminders.
-------------------------------------------------------------------------------

📅 Calendar Reminders (Google Calendar Integration)
	1.	Google Apps Script Webhook
	  •	A lightweight script hosted in Google Apps Script.
	  •	Fetches all calendar events scheduled within the next 24 hours.
	  •	Serves events in JSON format via a public URL endpoint.
	2.	Calendar Fetcher Script (calendar_fetcher.py)
	  •	Scheduled daily using cron.
	  •	Connects to the Google Apps Script URL.
	  •	Parses today’s events and saves them into a local file: calendar_events.json.
	3.	Calendar Action Script (calendar_action.py)
	  •	Continuously monitors calendar_events.json.
   
	•	5 minutes before an event:
	  •	If the event is AM (12:00 AM – 11:59 AM):
      🔔 Activates both buzzer and relay-controlled light.
	  •	If the event is PM:
      🔔 Plays a short buzzer beep only.
	•	Allows users to manually turn off buzzer/light via buttons or by typing "off" into the terminal.  
 -------------------------------------------------------------------------------

🕌 Prayer Reminders (Aladhan API Integration):
	1.	Prayer Fetcher Script (prayer_fetcher.py)
	  •	Runs daily using cron.
	  •	Fetches Riyadh prayer times from the Aladhan API.
	  •	Saves today’s timings into a local file: prayer_times.json.
	2.	Prayer Action Script (prayer_action.py)
	  •	Continuously monitors prayer_times.json.
   
	•	5 minutes before a prayer time:
	  •	If it’s Fajr:
      🔔 Activates both buzzer and relay-controlled light.
	  •	For other prayers:
      🔔 Plays a short buzzer beep only.
	•	Supports manual shutdown via buttons or "off" command.
 -------------------------------------------------------------------------------

🛠️ Hardware Setup:
	•	Raspberry Pi (any model with GPIO support)
	•	Relay module (connected to GPIO pin 4) — to control light
	•	Buzzer (connected to GPIO pin 17) — for sound alerts
	•	Two Push Buttons:
	•	Button 1 on GPIO 23 → stop buzzer
	•	Button 2 on GPIO 24 → stop light
	•	Pull-up resistors (enabled via GPIO.PUD_UP configuration)
  -------------------------------------------------------------------------------

⚙️ Software Setup:
	•	Python 3 installed with:
	•	requests
	•	RPi.GPIO
	•	Crontab for automated scheduling
	•	Google Calendar account and a Google Apps Script deployment
	•	Internet connection for API access
 -------------------------------------------------------------------------------

🚨 Reliability Features:
	•	Lock files to prevent duplicate script instances
	•	Button debounce to prevent false button readings
	•	Minimum activation duration to avoid unintended shutdown
	•	Network retry logic if API requests fail
	•	Graceful GPIO cleanup when scripts exit
	•	Manual override (physical buttons and terminal input)
  -------------------------------------------------------------------------------

📈 Future Extensions:
This project is the first prototype toward a much broader AI-driven smart scheduler:
	•	Health App Integration:
Track sleep/wake cycles and auto-schedule events accordingly.
	•	Location-based Triggers:
Adjust reminders if the user is away from home.
	•	Smart Environment Control:
Automatically adjust lights, temperature (A/C), and audio for different types of events.
	•	AI Event Analysis:
Predict best study/work/prayer times based on past behavior patterns.
	•	Fully Context-Aware Assistant:
Integrate Google Services, Health data, and Weather for smart decision-making.




