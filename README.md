# Mudhaker-Smart-Scheduler

📖 **Smart IoT Event & Prayer Reminder System**  
*Prototype for Smart Scheduler Project (7th Boeing Engineering Student Competition)*

---

## 📚 Overview

This project is a **working prototype** for a larger smart scheduler system idea, presented at the **Boeing Engineering Student Competition** at **Alfaisal University**.

It uses a **Raspberry Pi** to automate **buzzer and light notifications** based on:
- **Google Calendar events** (for scheduled tasks and activities)
- **Daily prayer times** (fetched via Aladhan API)

The system demonstrates a practical IoT assistant that helps users manage both **daily schedules** and **prayer duties** — setting the foundation for a **future AI-enhanced intelligent scheduling assistant**.

It operates **fully automated** through Python scripts and cron jobs, requiring no manual intervention once deployed.

---

## 🧠 System Logic

The system consists of two main modules:
- 📅 **Calendar Reminders**
- 🕌 **Prayer Reminders**

---

## 📅 Calendar Reminders (Google Calendar Integration)

### 1. Google Apps Script Webhook
- A lightweight script hosted in Google Apps Script.
- Fetches all calendar events scheduled within the next 24 hours.
- Serves events in JSON format via a public URL endpoint.

### 2. Calendar Fetcher Script (`calendar_fetcher.py`)
- Runs daily via cron.
- Connects to the Google Apps Script URL.
- Parses today’s events and saves them into `calendar_events.json`.

### 3. Calendar Action Script (`calendar_action.py`)
- Continuously monitors `calendar_events.json`.

**5 minutes before an event:**
- If the event is **AM (12:00 AM – 11:59 AM)**:  
  🔔 Activates both **buzzer** and **relay-controlled light**.
- If the event is **PM**:  
  🔔 Plays a **short buzzer beep** only.

Supports **manual shutdown** via buttons or by typing `"off"` in the terminal.

---

## 🕌 Prayer Reminders (Aladhan API Integration)

### 1. Prayer Fetcher Script (`prayer_fetcher.py`)
- Runs daily via cron.
- Fetches **Riyadh prayer times** from Aladhan API.
- Saves the timings into `prayer_times.json`.

### 2. Prayer Action Script (`prayer_action.py`)
- Continuously monitors `prayer_times.json`.

**5 minutes before each prayer:**
- If it's **Fajr**:  
  🔔 Activates both **buzzer** and **light**.
- For other prayers:  
  🔔 Plays a **short buzzer beep** only.

Supports **manual shutdown** via physical buttons or `"off"` command.

---

## 🛠️ Hardware Setup

- Raspberry Pi (any model with GPIO support)
- Relay module (GPIO 4) — for light control
- Buzzer (GPIO 17) — for sound alerts
- Two Push Buttons:
  - Button 1 (GPIO 23) → stop buzzer
  - Button 2 (GPIO 24) → stop light
- Pull-up resistors enabled using `GPIO.PUD_UP`

---

## ⚙️ Software Setup

- Python 3 with:
  - `requests`
  - `RPi.GPIO`
- Cron for scheduling
- Google Calendar + Google Apps Script
- Internet connection for API requests

---

## 📸 System Showcase

### 🏆 Boeing Engineering Expo Poster
![Boeing Poster](https://github.com/user-attachments/assets/a6fdd0bd-6e05-421a-913c-16d03d0af0df)


### 🔧 Real-life Prototype Setup
![prototype_setup](https://github.com/user-attachments/assets/6d4a44e3-ff60-412f-85ce-bb0afda23f18)


---

## 🚨 Reliability Features

- 🔒 Lock files prevent duplicate script execution
- 🧼 GPIO cleanup on exit
- 🧠 Manual override using physical buttons or "off" input
- 🔁 Retry logic for network/API issues
- 🧩 Event de-duplication using unique IDs
- 🕹️ Button debounce logic for reliable input

---

## 📈 Future Extensions

This prototype is part of a larger vision of an AI-driven smart assistant that can:

- 🧠 **Integrate with health apps**  
  Detect sleep cycles and optimize scheduling.

- 📍 **Use location-based triggers**  
  Only take action when the user is home.

- 💡 **Control smart environments**  
  Automatically adjust lights, A/C, or audio before an event.

- 📊 **Use AI for event prediction**  
  Recommend optimal timing based on historical habits.

- ☁️ **Become context-aware**  
  Integrate Google, weather, and health data for intelligent decision making.

---
