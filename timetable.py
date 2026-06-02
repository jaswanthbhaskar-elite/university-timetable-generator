# timetable.py

import json
import os
from collections import defaultdict

TIMETABLE_FILE = "timetables.json"

DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday"
]

TIME_SLOTS = [
    "08:00-09:00",
    "09:00-10:00",
    "10:00-11:00",
    "11:00-12:00",
    "12:00-13:00",
    "13:00-14:00",
    "14:00-15:00",
    "15:00-16:00",
    "16:00-17:00",
    "17:00-18:00"
]


# ==========================================
# FILE OPERATIONS
# ==========================================

def load_data():
    if os.path.exists(TIMETABLE_FILE):
        with open(TIMETABLE_FILE, "r") as f:
            return json.load(f)

    return {}


def save_data(data):
    with open(TIMETABLE_FILE, "w") as f:
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
# SEMESTER MANAGEMENT
# ==========================================

def create_semester(username, semester_name):
    data = load_data()

    if username not in data:
        initialize_user(username)
        data = load_data()

    if semester_name in data[username]["semesters"]:
        print("Semester already exists.")
        return False

    data[username]["semesters"][semester_name] = []

    save_data(data)

    print("Semester created successfully.")
    return True


def delete_semester(username, semester_name):
    data = load_data()

    if semester_name not in data[username]["semesters"]:
        print("Semester not found.")
        return False

    del data[username]["semesters"][semester_name]

    save_data(data)

    print("Semester deleted.")
    return True


def list_semesters(username):
    data = load_data()

    semesters = data[username]["semesters"]

    if not semesters:
        print("\nNo semesters found.\n")
        return

    print("\n===== SEMESTERS =====")

    for i, semester in enumerate(semesters, start=1):
        course_count = len(semesters[semester])

        print(
            f"{i}. {semester} "
            f"({course_count} courses)"
        )


# ==========================================
# CONFLICT DETECTION
# ==========================================

def check_conflict(courses, new_course):

    conflicts = []

    for course in courses:

        if (
            course["day"] == new_course["day"]
            and
            course["time_slot"] == new_course["time_slot"]
        ):
            conflicts.append(course["name"])

    return conflicts


# ==========================================
# COURSE MANAGEMENT
# ==========================================

def add_course(username, semester):

    data = load_data()

    courses = data[username]["semesters"][semester]

    print("\n===== ADD COURSE =====")

    name = input("Course Name: ")
    code = input("Course Code: ")
    credits = input("Credits: ")
    instructor = input("Instructor: ")
    room = input("Room: ")

    print("\nSelect Day:")

    for i, day in enumerate(DAYS, start=1):
        print(f"{i}. {day}")

    day = DAYS[int(input("Choice: ")) - 1]

    print("\nSelect Time Slot:")

    for i, slot in enumerate(TIME_SLOTS, start=1):
        print(f"{i}. {slot}")

    time_slot = TIME_SLOTS[int(input("Choice: ")) - 1]

    course = {
        "name": name,
        "code": code,
        "credits": credits,
        "instructor": instructor,
        "room": room,
        "day": day,
        "time_slot": time_slot
    }

    conflicts = check_conflict(courses, course)

    if conflicts:

        print(
            f"Conflict with: "
            f"{', '.join(conflicts)}"
        )

        confirm = input(
            "Add anyway? (y/n): "
        ).lower()

        if confirm != "y":
            return

    courses.append(course)

    save_data(data)

    print("Course added successfully.")


def remove_course(username, semester):

    data = load_data()

    courses = data[username]["semesters"][semester]

    if not courses:
        print("No courses available.")
        return

    list_courses(username, semester)

    choice = input(
        "Course number to remove: "
    )

    if (
        choice.isdigit()
        and
        1 <= int(choice) <= len(courses)
    ):
        removed = courses.pop(int(choice) - 1)

        save_data(data)

        print(
            f"{removed['name']} removed."
        )


def list_courses(username, semester):

    data = load_data()

    courses = data[username]["semesters"][semester]

    if not courses:
        print("No courses found.")
        return

    print("\n===== COURSES =====")

    for i, c in enumerate(courses, start=1):

        print(
            f"{i}. "
            f"{c['name']} | "
            f"{c['code']} | "
            f"{c['day']} | "
            f"{c['time_slot']}"
        )


# ==========================================
# TIMETABLE GRID
# ==========================================

def display_timetable(username, semester):

    data = load_data()

    courses = data[username]["semesters"][semester]

    if not courses:
        print("No timetable data.")
        return

    grid = defaultdict(dict)

    for c in courses:

        grid[c["time_slot"]][c["day"]] = c["name"]

    print("\n")

    print(f"{'TIME':<15}", end="")

    for day in DAYS:
        print(f"{day:<15}", end="")

    print()

    print("-" * 110)

    for slot in TIME_SLOTS:

        print(f"{slot:<15}", end="")

        for day in DAYS:

            print(
                f"{grid[slot].get(day, ''):<15}",
                end=""
            )

        print()

    print()


# ==========================================
# SEARCH COURSE
# ==========================================

def search_course(username, semester):

    keyword = input(
        "Enter course name/code: "
    ).lower()

    data = load_data()

    courses = data[username]["semesters"][semester]

    found = False

    for c in courses:

        if (
            keyword in c["name"].lower()
            or
            keyword in c["code"].lower()
        ):

            print(
                f"{c['name']} "
                f"({c['code']}) "
                f"{c['day']} "
                f"{c['time_slot']}"
            )

            found = True

    if not found:
        print("No matching course found.")


# ==========================================
# SEMESTER MENU
# ==========================================

def semester_menu(username, semester):

    while True:

        print(f"\n===== {semester} =====")
        print("1. View Timetable")
        print("2. List Courses")
        print("3. Add Course")
        print("4. Remove Course")
        print("5. Search Course")
        print("6. Back")

        choice = input("Choice: ")

        if choice == "1":
            display_timetable(username, semester)

        elif choice == "2":
            list_courses(username, semester)

        elif choice == "3":
            add_course(username, semester)

        elif choice == "4":
            remove_course(username, semester)

        elif choice == "5":
            search_course(username, semester)

        elif choice == "6":
            break


# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":

    user = "demo"

    initialize_user(user)

    while True:

        print("\n===== TIMETABLE MENU =====")
        print("1. Create Semester")
        print("2. List Semesters")
        print("3. Open Semester")
        print("4. Exit")

        choice = input("Choice: ")

        if choice == "1":

            semester = input(
                "Semester Name: "
            )

            create_semester(
                user,
                semester
            )

        elif choice == "2":

            list_semesters(user)

        elif choice == "3":

            semester = input(
                "Semester Name: "
            )

            semester_menu(
                user,
                semester
            )

        elif choice == "4":
            break