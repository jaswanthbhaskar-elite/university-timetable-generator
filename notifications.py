# notifications.py

from datetime import datetime, timedelta
import json
import os

ATTENDANCE_FILE = "attendance.json"
ASSIGNMENT_FILE = "assignments.json"
EXAM_FILE = "exams.json"


# ==========================================
# FILE LOADERS
# ==========================================

def load_json(filename):

    if os.path.exists(filename):

        with open(filename, "r") as f:
            return json.load(f)

    return {}


# ==========================================
# ATTENDANCE ALERTS
# ==========================================

def attendance_alerts(username):

    data = load_json(
        ATTENDANCE_FILE
    )

    alerts = []

    if username not in data:
        return alerts

    for course in data[username]:

        present = data[username][course]["present"]

        absent = data[username][course]["absent"]

        total = present + absent

        if total == 0:
            continue

        percentage = (
            present / total
        ) * 100

        if percentage < 75:

            alerts.append(
                f"⚠ Attendance Low in "
                f"{course} "
                f"({percentage:.2f}%)"
            )

    return alerts


# ==========================================
# OVERDUE ASSIGNMENTS
# ==========================================

def overdue_assignments(username):

    data = load_json(
        ASSIGNMENT_FILE
    )

    alerts = []

    if username not in data:
        return alerts

    today = datetime.now().date()

    for assignment in data[
        username
    ]:

        due_date = datetime.strptime(
            assignment["due_date"],
            "%Y-%m-%d"
        ).date()

        if (
            assignment["status"]
            == "Pending"
            and
            due_date < today
        ):

            alerts.append(
                f"📌 Overdue Assignment: "
                f"{assignment['title']}"
            )

    return alerts


# ==========================================
# UPCOMING ASSIGNMENTS
# ==========================================

def upcoming_assignments(username):

    data = load_json(
        ASSIGNMENT_FILE
    )

    alerts = []

    if username not in data:
        return alerts

    today = datetime.now().date()

    for assignment in data[
        username
    ]:

        due = datetime.strptime(
            assignment["due_date"],
            "%Y-%m-%d"
        ).date()

        days_left = (
            due - today
        ).days

        if (
            assignment["status"]
            == "Pending"
            and
            0 <= days_left <= 3
        ):

            alerts.append(
                f"📝 Assignment Due Soon: "
                f"{assignment['title']} "
                f"({days_left} day(s))"
            )

    return alerts


# ==========================================
# UPCOMING EXAMS
# ==========================================

def upcoming_exams(username):

    data = load_json(
        EXAM_FILE
    )

    alerts = []

    if username not in data:
        return alerts

    now = datetime.now()

    for exam in data[
        username
    ]:

        exam_time = datetime.strptime(
            exam["exam_date"],
            "%Y-%m-%d %H:%M"
        )

        days = (
            exam_time - now
        ).days

        if 0 <= days <= 7:

            alerts.append(
                f"🎓 Exam Soon: "
                f"{exam['subject']} "
                f"({days} days)"
            )

    return alerts


# ==========================================
# TODAY'S EXAMS
# ==========================================

def todays_exams(username):

    data = load_json(
        EXAM_FILE
    )

    alerts = []

    if username not in data:
        return alerts

    today = datetime.now().date()

    for exam in data[
        username
    ]:

        exam_date = datetime.strptime(
            exam["exam_date"],
            "%Y-%m-%d %H:%M"
        ).date()

        if exam_date == today:

            alerts.append(
                f"🚨 Exam Today: "
                f"{exam['subject']}"
            )

    return alerts


# ==========================================
# DAILY SUMMARY
# ==========================================

def daily_summary(username):

    print(
        "\n===== DAILY SUMMARY ====="
    )

    all_alerts = []

    all_alerts.extend(
        attendance_alerts(
            username
        )
    )

    all_alerts.extend(
        overdue_assignments(
            username
        )
    )

    all_alerts.extend(
        upcoming_assignments(
            username
        )
    )

    all_alerts.extend(
        upcoming_exams(
            username
        )
    )

    all_alerts.extend(
        todays_exams(
            username
        )
    )

    if not all_alerts:

        print(
            "✅ No Notifications"
        )

        return

    for alert in all_alerts:

        print(alert)


# ==========================================
# NOTIFICATION COUNT
# ==========================================

def notification_count(username):

    total = 0

    total += len(
        attendance_alerts(
            username
        )
    )

    total += len(
        overdue_assignments(
            username
        )
    )

    total += len(
        upcoming_assignments(
            username
        )
    )

    total += len(
        upcoming_exams(
            username
        )
    )

    total += len(
        todays_exams(
            username
        )
    )

    return total


# ==========================================
# ALL NOTIFICATIONS
# ==========================================

def all_notifications(username):

    notifications = []

    notifications.extend(
        attendance_alerts(
            username
        )
    )

    notifications.extend(
        overdue_assignments(
            username
        )
    )

    notifications.extend(
        upcoming_assignments(
            username
        )
    )

    notifications.extend(
        upcoming_exams(
            username
        )
    )

    notifications.extend(
        todays_exams(
            username
        )
    )

    return notifications


# ==========================================
# MENU
# ==========================================

def notification_menu(username):

    while True:

        print(
            "\n===== NOTIFICATIONS ====="
        )

        print(
            "1. View Notifications"
        )

        print(
            "2. Notification Count"
        )

        print(
            "3. Daily Summary"
        )

        print(
            "4. Back"
        )

        choice = input(
            "Choice: "
        )

        if choice == "1":

            alerts = all_notifications(
                username
            )

            if not alerts:

                print(
                    "No Notifications."
                )

            else:

                for alert in alerts:
                    print(alert)

        elif choice == "2":

            print(
                f"Total Notifications: "
                f"{notification_count(username)}"
            )

        elif choice == "3":

            daily_summary(
                username
            )

        elif choice == "4":

            break

        else:

            print(
                "Invalid Choice."
            )


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    notification_menu("demo")