# UniSchedule

A fresh Flask timetable management app with admin, faculty, and student support.

## Setup

1. Activate your existing virtual environment:

```powershell
& .\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```
```

3. Run the app:

```powershell
python app.py
```

4. Open the browser:

```text
http://127.0.0.1:5000
```

## Notes

- The app stores its SQLite database in `instance/unischedule.db`.
- A default admin account is available at `/create_admin`.
