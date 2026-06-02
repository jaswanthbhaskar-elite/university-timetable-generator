# gpa.py

import json
import os
from datetime import datetime

GPA_FILE = "gpa_records.json"

GRADE_POINTS = {
    "O": 10,
    "A+": 9,
    "A": 8,
    "B+": 7,
    "B": 6,
    "C": 5,
    "F": 0
}


# ==========================================
# FILE OPERATIONS
# ==========================================

def load_data():

    if os.path.exists(GPA_FILE):

        with open(GPA_FILE, "r") as f:
            return json.load(f)

    return {}


def save_data(data):

    with open(GPA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ==========================================
# USER INITIALIZATION
# ==========================================

def initialize_user(username):

    data = load_data()

    if username not in data:

        data[username] = {
            "semesters": {}
        }

        save_data(data)

    return data


# ==========================================
# CREATE SEMESTER
# ==========================================

def create_semester(username, semester):

    data = load_data()

    initialize_user(username)

    data = load_data()

    if semester not in data[username]["semesters"]:

        data[username]["semesters"][semester] = []

        save_data(data)

        print("Semester created.")

    else:

        print("Semester already exists.")


# ==========================================
# ADD SUBJECT RESULT
# ==========================================

def add_result(username, semester):

    data = load_data()

    if semester not in data[username]["semesters"]:

        print("Semester not found.")
        return

    print("\n===== ADD RESULT =====")

    subject = input("Subject Name: ")

    course_code = input("Course Code: ")

    credits = int(
        input("Credits: ")
    )

    print("\nAvailable Grades:")

    for grade in GRADE_POINTS:
        print(grade)

    grade = input(
        "Grade: "
    ).upper()

    if grade not in GRADE_POINTS:

        print("Invalid grade.")
        return

    result = {

        "subject": subject,

        "course_code": course_code,

        "credits": credits,

        "grade": grade,

        "grade_point":
            GRADE_POINTS[grade]
    }

    data[username]["semesters"][
        semester
    ].append(result)

    save_data(data)

    print("Result added.")


# ==========================================
# CALCULATE SGPA
# ==========================================

def calculate_sgpa(username, semester):

    data = load_data()

    if semester not in data[username]["semesters"]:
        return 0

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

    if total_credits == 0:
        return 0

    return round(
        total_points /
        total_credits,
        2
    )


# ==========================================
# CALCULATE CGPA
# ==========================================

def calculate_cgpa(username):

    data = load_data()

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
# VIEW SEMESTER RESULTS
# ==========================================

def semester_report(
    username,
    semester
):

    data = load_data()

    if semester not in data[
        username
    ]["semesters"]:

        print("Semester not found.")
        return

    print(
        f"\n===== {semester} ====="
    )

    for subject in data[
        username
    ]["semesters"][semester]:

        print(
            f"{subject['course_code']} | "
            f"{subject['subject']} | "
            f"{subject['credits']} Credits | "
            f"{subject['grade']}"
        )

    print(
        f"\nSGPA : "
        f"{calculate_sgpa(username, semester)}"
    )


# ==========================================
# TRANSCRIPT
# ==========================================

def generate_transcript(
    username
):

    data = load_data()

    print(
        "\n===== TRANSCRIPT ====="
    )

    for semester in data[
        username
    ]["semesters"]:

        print(
            f"\n{semester}"
        )

        print("-" * 30)

        for subject in data[
            username
        ]["semesters"][semester]:

            print(
                f"{subject['course_code']} "
                f"{subject['subject']} "
                f"{subject['grade']}"
            )

        print(
            f"SGPA: "
            f"{calculate_sgpa(username, semester)}"
        )

    print(
        f"\nCGPA: "
        f"{calculate_cgpa(username)}"
    )


# ==========================================
# GRADE STATISTICS
# ==========================================

def grade_statistics(
    username
):

    data = load_data()

    stats = {}

    for semester in data[
        username
    ]["semesters"]:

        for subject in data[
            username
        ]["semesters"][semester]:

            grade = subject["grade"]

            stats[grade] = (
                stats.get(grade, 0)
                + 1
            )

    print(
        "\n===== GRADE STATS ====="
    )

    for grade in sorted(stats):

        print(
            f"{grade}: "
            f"{stats[grade]}"
        )


# ==========================================
# TOP SEMESTER
# ==========================================

def best_semester(
    username
):

    data = load_data()

    best = None
    best_sgpa = -1

    for semester in data[
        username
    ]["semesters"]:

        sgpa = calculate_sgpa(
            username,
            semester
        )

        if sgpa > best_sgpa:

            best_sgpa = sgpa
            best = semester

    if best:

        print(
            f"\nBest Semester: "
            f"{best}"
        )

        print(
            f"SGPA: "
            f"{best_sgpa}"
        )


# ==========================================
# DELETE RESULT
# ==========================================

def delete_result(
    username,
    semester,
    course_code
):

    data = load_data()

    subjects = data[
        username
    ]["semesters"][semester]

    for i, subject in enumerate(
        subjects
    ):

        if (
            subject["course_code"]
            ==
            course_code
        ):

            del subjects[i]

            save_data(data)

            print(
                "Result deleted."
            )

            return

    print(
        "Course not found."
    )


# ==========================================
# GPA MENU
# ==========================================

def gpa_menu(username):

    initialize_user(username)

    while True:

        print(
            "\n===== GPA MENU ====="
        )

        print("1. Create Semester")
        print("2. Add Result")
        print("3. Semester Report")
        print("4. Transcript")
        print("5. CGPA")
        print("6. Grade Statistics")
        print("7. Best Semester")
        print("8. Delete Result")
        print("9. Back")

        choice = input(
            "Choice: "
        )

        if choice == "1":

            sem = input(
                "Semester: "
            )

            create_semester(
                username,
                sem
            )

        elif choice == "2":

            sem = input(
                "Semester: "
            )

            add_result(
                username,
                sem
            )

        elif choice == "3":

            sem = input(
                "Semester: "
            )

            semester_report(
                username,
                sem
            )

        elif choice == "4":

            generate_transcript(
                username
            )

        elif choice == "5":

            print(
                f"\nCGPA: "
                f"{calculate_cgpa(username)}"
            )

        elif choice == "6":

            grade_statistics(
                username
            )

        elif choice == "7":

            best_semester(
                username
            )

        elif choice == "8":

            sem = input(
                "Semester: "
            )

            code = input(
                "Course Code: "
            )

            delete_result(
                username,
                sem,
                code
            )

        elif choice == "9":

            break

        else:

            print(
                "Invalid Choice."
            )


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    gpa_menu("demo")