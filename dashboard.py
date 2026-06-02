# dashboard.py

import json
import os
from datetime import datetime

ATTENDANCE_FILE = "attendance.json"
ASSIGNMENT_FILE = "assignments.json"
EXAM_FILE = "exams.json"
GPA_FILE = "gpa_records.json"


# ==========================================
# FILE LOADER
# ==========================================

def load_json(filename):

    if os.path.exists(filename):

        with open(filename, "r") as f:

            return json.load(f)

    return {}


# ==========================================
# ATTENDANCE SCORE
# ==========================================

def attendance_score(username):

    data = load_json(
        ATTENDANCE_FILE
    )

    if username not in data:

        return 0

    total_present = 0
    total_absent = 0

    for course in data[username]:

        total_present += (
            data[username][course]["present"]
        )

        total_absent += (
            data[username][course]["absent"]
        )

    total = (
        total_present +
        total_absent
    )

    if total == 0:
        return 0

    return round(
        (total_present / total) * 100,
        2
    )


# ==========================================
# GPA SCORE
# ==========================================

def cgpa_score(username):

    data = load_json(
        GPA_FILE
    )

    if username not in data:

        return 0

    total_points = 0
    total_credits = 0

    for semester in data[
        username
    ]["semesters"]:

        for subject in data[
            username
        ]["semesters"][semester]:

            total_points += (
                subject["credits"]
                *
                subject["grade_point"]
            )

            total_credits += (
                subject["credits"]
            )

    if total_credits == 0:
        return 0

    return round(
        total_points /
        total_credits,
        2
    )


# ==========================================
# ASSIGNMENT COMPLETION
# ==========================================

def assignment_completion(username):

    data = load_json(
        ASSIGNMENT_FILE
    )

    if username not in data:

        return 0

    total = len(
        data[username]
    )

    if total == 0:

        return 0

    completed = 0

    for assignment in data[
        username
    ]:

        if (
            assignment["status"]
            ==
            "Completed"
        ):

            completed += 1

    return round(
        (completed / total) * 100,
        2
    )


# ==========================================
# EXAM READINESS
# ==========================================

def exam_readiness(username):

    attendance = (
        attendance_score(username)
    )

    assignments = (
        assignment_completion(username)
    )

    cgpa = (
        cgpa_score(username)
        * 10
    )

    score = (
        attendance +
        assignments +
        cgpa
    ) / 3

    return round(score, 2)


# ==========================================
# PERFORMANCE LEVEL
# ==========================================

def performance_level(score):

    if score >= 90:
        return "Excellent"

    elif score >= 80:
        return "Very Good"

    elif score >= 70:
        return "Good"

    elif score >= 60:
        return "Average"

    return "Needs Improvement"


# ==========================================
# ASCII BAR CHART
# ==========================================

def draw_bar(label, value):

    bars = int(
        value // 2
    )

    print(
        f"{label:<15}"
        f"{'█' * bars}"
        f" {value}%"
    )


# ==========================================
# ATTENDANCE CHART
# ==========================================

def attendance_chart(username):

    data = load_json(
        ATTENDANCE_FILE
    )

    if username not in data:

        return

    print(
        "\n===== ATTENDANCE CHART ====="
    )

    for course in data[
        username
    ]:

        present = data[
            username
        ][course]["present"]

        absent = data[
            username
        ][course]["absent"]

        total = (
            present + absent
        )

        if total == 0:

            percentage = 0

        else:

            percentage = round(
                (present / total)
                * 100,
                2
            )

        draw_bar(
            course,
            percentage
        )


# ==========================================
# GPA TREND
# ==========================================

def gpa_trend(username):

    data = load_json(
        GPA_FILE
    )

    if username not in data:

        return

    print(
        "\n===== GPA TREND ====="
    )

    for semester in data[
        username
    ]["semesters"]:

        points = 0
        credits = 0

        for subject in data[
            username
        ]["semesters"][semester]:

            points += (

                subject["credits"]
                *
                subject["grade_point"]

            )

            credits += (
                subject["credits"]
            )

        sgpa = 0

        if credits:

            sgpa = round(
                points / credits,
                2
            )

        bars = int(
            sgpa * 3
        )

        print(
            f"{semester:<15}"
            f"{'█' * bars}"
            f" {sgpa}"
        )


# ==========================================
# PRODUCTIVITY SCORE
# ==========================================

def productivity_score(username):

    return round(

        (
            assignment_completion(
                username
            )
            +
            attendance_score(
                username
            )
        ) / 2,

        2
    )


# ==========================================
# DASHBOARD SUMMARY
# ==========================================

def dashboard_summary(username):

    attendance = (
        attendance_score(
            username
        )
    )

    cgpa = (
        cgpa_score(
            username
        )
    )

    assignments = (
        assignment_completion(
            username
        )
    )

    readiness = (
        exam_readiness(
            username
        )
    )

    productivity = (
        productivity_score(
            username
        )
    )

    print(
        "\n===== STUDENT DASHBOARD ====="
    )

    print(
        f"Attendance Score : "
        f"{attendance}%"
    )

    print(
        f"CGPA             : "
        f"{cgpa}"
    )

    print(
        f"Assignments Done : "
        f"{assignments}%"
    )

    print(
        f"Readiness Score  : "
        f"{readiness}"
    )

    print(
        f"Productivity     : "
        f"{productivity}"
    )

    print(
        f"Performance      : "
        f"{performance_level(readiness)}"
    )


# ==========================================
# COMPLETE ANALYTICS
# ==========================================

def full_analytics(username):

    dashboard_summary(
        username
    )

    attendance_chart(
        username
    )

    gpa_trend(
        username
    )


# ==========================================
# MENU
# ==========================================

def dashboard_menu(username):

    while True:

        print(
            "\n===== DASHBOARD ====="
        )

        print(
            "1. Dashboard Summary"
        )

        print(
            "2. Attendance Chart"
        )

        print(
            "3. GPA Trend"
        )

        print(
            "4. Full Analytics"
        )

        print(
            "5. Back"
        )

        choice = input(
            "Choice: "
        )

        if choice == "1":

            dashboard_summary(
                username
            )

        elif choice == "2":

            attendance_chart(
                username
            )

        elif choice == "3":

            gpa_trend(
                username
            )

        elif choice == "4":

            full_analytics(
                username
            )

        elif choice == "5":

            break

        else:

            print(
                "Invalid Choice."
            )


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    dashboard_menu("demo")