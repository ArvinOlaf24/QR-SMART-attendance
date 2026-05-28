# TrackAS — QR Smart Attendance System (Flask)

TrackAS is a smart attendance system that uses QR codes and geolocation. Lecturers create class schedules and generate QR codes; students scan the code and mark attendance when they are within 20 meters of the lecture venue.

This project was converted from a React + Vite frontend to a **Python Flask** server-rendered application while keeping **Supabase** as the backend database and auth provider.

## Features

- Lecturer registration and login (Supabase Auth)
- Create class schedules with map-based venue selection
- QR code generation for student attendance links
- Geolocation-based attendance (20 m radius)
- View previous classes and export attendance (CSV / Excel)

## Requirements

- Python 3.10+
- A Supabase project with `lecturers` and `classes` tables (same schema as the original app)

## Setup

1. **Clone and enter the project**

   ```bash
   cd QRCode-Smart-Attendance-System-with-Geolocation
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Copy `.env.example` to `.env` and set:

   - `SUPABASE_URL` — your Supabase project URL
   - `SUPABASE_ANON_KEY` — your Supabase anon/public key
   - `APP_URL` — public base URL (e.g. `http://127.0.0.1:5000` for local dev)
   - `SECRET_KEY` — random string for Flask sessions

4. **Run the app**

   ```bash
   python run.py
   ```

   Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Project structure

```
app/
  __init__.py          # Flask app factory
  config.py            # Configuration
  routes/              # Blueprints (auth, classes, attendance, api)
  utils/               # Supabase, distance, QR helpers
templates/             # Jinja2 HTML templates
static/                # CSS, JS, images
run.py                 # Entry point
requirements.txt
```

## Routes

| Path | Description |
|------|-------------|
| `/` | Landing page |
| `/register` | Lecturer registration |
| `/login` | Lecturer login |
| `/class-details` | Lecturer dashboard |
| `/class-schedule` | Create class + QR |
| `/previous-class` | List past classes |
| `/attendance` | Student attendance (from QR link) |
| `/success` | Attendance success page |

Legacy React paths (`/loginLecturer`, `/classSchedule`, etc.) redirect to the Flask routes above.

## Notes

- Student geolocation is checked in the browser and **re-validated on the server** when attendance is submitted.
- Set `APP_URL` to your deployed URL so generated QR codes point to the correct host.
