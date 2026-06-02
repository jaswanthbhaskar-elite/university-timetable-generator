# reports.py

import json
import csv
import os
from datetime import datetime

ATTENDANCE_FILE = "attendance.json"
ASSIGNMENT_FILE = "assignments.json"
EXAM_FILE = "exams.json"
GPA_FILE = "gpa_records.json"


# ==========================================
# FILE HELPERS
# ==========================================

def load_json(filename):

    if os.path.exists(filename):

        with open(filename, "r") as f:
            return json.load(f)

    return {}


# ==========================================
# ATTENDANCE REPORT
# ==========================================

def attendance_report(username):

    data = load_json(
        ATTENDANCE_FILE
    )

    report = []

    if username not in data:
        return report

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

        percentage = 0

        if total:

            percentage = round(
                (present / total) * 100,
                2
            )

        report.append({

            "course":
                course,

            "present":
                present,

            "absent":
                absent,

            "percentage":
                percentage
        })

    return report


# ==========================================
# GPA REPORT
# ==========================================

def gpa_report(username):

    data = load_json(
        GPA_FILE
    )

    report = []

    if username not in data:
        return report

    for semester in data[
        username
    ]["semesters"]:

        total_points = 0
        total_credits = 0

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

        sgpa = 0

        if total_credits:

            sgpa = round(
                total_points /
                total_credits,
                2
            )

        report.append({

            "semester":
                semester,

            "sgpa":
                sgpa
        })

    return report


# ==========================================
# ASSIGNMENT REPORT
# ==========================================

def assignment_report(username):

    data = load_json(
        ASSIGNMENT_FILE
    )

    report = []

    if username not in data:
        return report

    for assignment in data[
        username
    ]:

        report.append({

            "title":
                assignment["title"],

            "course":
                assignment["course"],

            "status":
                assignment["status"],

            "priority":
                assignment["priority"],

            "due_date":
                assignment["due_date"]
        })

    return report


# ==========================================
# EXAM REPORT
# ==========================================

def exam_report(username):

    data = load_json(
        EXAM_FILE
    )

    report = []

    if username not in data:
        return report

    for exam in data[
        username
    ]:

        report.append({

            "subject":
                exam["subject"],

            "course_code":
                exam["course_code"],

            "exam_date":
                exam["exam_date"],

            "venue":
                exam["venue"]
        })

    return report


# ==========================================
# PRINT ATTENDANCE
# ==========================================

def print_attendance(username):

    report = attendance_report(
        username
    )

    print(
        "\n===== ATTENDANCE REPORT ====="
    )

    for item in report:

        print(

            f"{item['course']} | "
            f"{item['present']} Present | "
            f"{item['absent']} Absent | "
            f"{item['percentage']}%"

        )


# ==========================================
# PRINT GPA
# ==========================================

def print_gpa(username):

    report = gpa_report(
        username
    )

    print(
        "\n===== GPA REPORT ====="
    )

    for item in report:

        print(

            f"{item['semester']} | "
            f"SGPA: {item['sgpa']}"

        )


# ==========================================
# PRINT ASSIGNMENTS
# ==========================================

def print_assignments(username):

    report = assignment_report(
        username
    )

    print(
        "\n===== ASSIGNMENTS ====="
    )

    for item in report:

        print(

            f"{item['title']} | "
            f"{item['status']} | "
            f"{item['due_date']}"

        )


# ==========================================
# PRINT EXAMS
# ==========================================

def print_exams(username):

    report = exam_report(
        username
    )

    print(
        "\n===== EXAMS ====="
    )

    for item in report:

        print(

            f"{item['subject']} | "
            f"{item['exam_date']} | "
            f"{item['venue']}"

        )


# ==========================================
# CSV EXPORT
# ==========================================

def export_csv(
    filename,
    data
):

    if not data:

        print(
            "No Data Available."
        )

        return

    keys = data[0].keys()

    with open(
        filename,
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=keys
        )

        writer.writeheader()

        writer.writerows(
            data
        )

    print(
        f"Exported -> {filename}"
    )


# ==========================================
# EXPORT ATTENDANCE
# ==========================================

def export_attendance_csv(
    username
):

    export_csv(

        f"{username}_attendance.csv",

        attendance_report(
            username
        )
    )


# ==========================================
# EXPORT GPA
# ==========================================

def export_gpa_csv(
    username
):

    export_csv(

        f"{username}_gpa.csv",

        gpa_report(
            username
        )
    )


# ==========================================
# EXPORT ASSIGNMENTS
# ==========================================

def export_assignment_csv(
    username
):

    export_csv(

        f"{username}_assignments.csv",

        assignment_report(
            username
        )
    )


# ==========================================
# EXPORT EXAMS
# ==========================================

def export_exam_csv(
    username
):

    export_csv(

        f"{username}_exams.csv",

        exam_report(
            username
        )
    )


# ==========================================
# FULL STUDENT REPORT
# ==========================================

def generate_full_report(
    username
):

    filename = (
        f"{username}_full_report.txt"
    )

    with open(
        filename,
        "w"
    ) as f:

        f.write(
            "UNIVERSITY REPORT\n"
        )

        f.write(
            "=" * 40 + "\n\n"
        )

        f.write(
            "ATTENDANCE\n"
        )

        for item in attendance_report(
            username
        ):

            f.write(
                str(item) + "\n"
            )

        f.write(
            "\nGPA\n"
        )

        for item in gpa_report(
            username
        ):

            f.write(
                str(item) + "\n"
            )

        f.write(
            "\nASSIGNMENTS\n"
        )

        for item in assignment_report(
            username
        ):

            f.write(
                str(item) + "\n"
            )

        f.write(
            "\nEXAMS\n"
        )

        for item in exam_report(
            username
        ):

            f.write(
                str(item) + "\n"
            )

    print(
        f"Report Saved: {filename}"
    )


# ==========================================
# DASHBOARD SUMMARY
# ==========================================

def dashboard_summary(
    username
):

    attendance = len(
        attendance_report(
            username
        )
    )

    assignments = len(
        assignment_report(
            username
        )
    )

    exams = len(
        exam_report(
            username
        )
    )

    semesters = len(
        gpa_report(
            username
        )
    )

    print(
        "\n===== DASHBOARD ====="
    )

    print(
        f"Courses      : {attendance}"
    )

    print(
        f"Assignments  : {assignments}"
    )

    print(
        f"Exams        : {exams}"
    )

    print(
        f"Semesters    : {semesters}"
    )


# ==========================================
# REPORT MENU
# ==========================================

def reports_menu(username):

    while True:

        print(
            "\n===== REPORTS ====="
        )

        print("1. Attendance Report")
        print("2. GPA Report")
        print("3. Assignment Report")
        print("4. Exam Report")
        print("5. Dashboard")
        print("6. Export Attendance CSV")
        print("7. Export GPA CSV")
        print("8. Export Assignment CSV")
        print("9. Export Exam CSV")
        print("10. Full Report")
        print("11. Back")

        choice = input(
            "Choice: "
        )

        if choice == "1":

            print_attendance(
                username
            )

        elif choice == "2":

            print_gpa(
                username
            )

        elif choice == "3":

            print_assignments(
                username
            )

        elif choice == "4":

            print_exams(
                username
            )

        elif choice == "5":

            dashboard_summary(
                username
            )

        elif choice == "6":

            export_attendance_csv(
                username
            )

        elif choice == "7":

            export_gpa_csv(
                username
            )

        elif choice == "8":

            export_assignment_csv(
                username
            )

        elif choice == "9":

            export_exam_csv(
                username
            )

        elif choice == "10":

            generate_full_report(
                username
            )

        elif choice == "11":

            break

        else:

            print(
                "Invalid Choice."
            )


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    reports_menu("demo")