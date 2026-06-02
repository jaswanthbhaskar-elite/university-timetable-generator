# attendance.py

import json
import os

ATTENDANCE_FILE = "attendance.json"

MIN_ATTENDANCE = 75


# ==========================================
# FILE OPERATIONS
# ==========================================

def load_attendance():

    if os.path.exists(ATTENDANCE_FILE):

        with open(ATTENDANCE_FILE, "r") as f:
            return json.load(f)

    return {}


def save_attendance(data):

    with open(ATTENDANCE_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ==========================================
# USER INITIALIZATION
# ==========================================

def initialize_user(username):

    data = load_attendance()

    if username not in data:

        data[username] = {}

        save_attendance(data)

    return data


# ==========================================
# COURSE INITIALIZATION
# ==========================================

def initialize_course(username, course_code):

    data = load_attendance()

    if username not in data:
        initialize_user(username)
        data = load_attendance()

    if course_code not in data[username]:

        data[username][course_code] = {
            "present": 0,
            "absent": 0
        }

        save_attendance(data)


# ==========================================
# MARK PRESENT
# ==========================================

def mark_present(username, course_code):

    initialize_course(username, course_code)

    data = load_attendance()

    data[username][course_code]["present"] += 1

    save_attendance(data)

    print("Attendance marked PRESENT.")


# ==========================================
# MARK ABSENT
# ==========================================

def mark_absent(username, course_code):

    initialize_course(username, course_code)

    data = load_attendance()

    data[username][course_code]["absent"] += 1

    save_attendance(data)

    print("Attendance marked ABSENT.")


# ==========================================
# CALCULATE PERCENTAGE
# ==========================================

def attendance_percentage(username, course_code):

    data = load_attendance()

    if (
        username not in data
        or
        course_code not in data[username]
    ):
        return 0

    present = data[username][course_code]["present"]
    absent = data[username][course_code]["absent"]

    total = present + absent

    if total == 0:
        return 0

    return round((present / total) * 100, 2)


# ==========================================
# COURSE REPORT
# ==========================================

def course_report(username, course_code):

    data = load_attendance()

    if (
        username not in data
        or
        course_code not in data[username]
    ):
        print("No attendance data found.")
        return

    present = data[username][course_code]["present"]
    absent = data[username][course_code]["absent"]

    total = present + absent

    percentage = attendance_percentage(
        username,
        course_code
    )

    print("\n===== COURSE REPORT =====")

    print(f"Course     : {course_code}")
    print(f"Present    : {present}")
    print(f"Absent     : {absent}")
    print(f"Total      : {total}")
    print(f"Percentage : {percentage}%")

    if percentage < MIN_ATTENDANCE:
        print("⚠ WARNING: Attendance below 75%")

    print()


# ==========================================
# ALL COURSES REPORT
# ==========================================

def all_courses_report(username):

    data = load_attendance()

    if username not in data:

        print("No attendance records.")
        return

    print("\n===== ATTENDANCE REPORT =====")

    print(
        f"{'Course':<15}"
        f"{'Present':<10}"
        f"{'Absent':<10}"
        f"{'Percent':<10}"
    )

    print("-" * 50)

    for course_code in data[username]:

        present = data[username][course_code]["present"]

        absent = data[username][course_code]["absent"]

        percentage = attendance_percentage(
            username,
            course_code
        )

        print(
            f"{course_code:<15}"
            f"{present:<10}"
            f"{absent:<10}"
            f"{str(percentage)+'%':<10}"
        )


# ==========================================
# LOW ATTENDANCE COURSES
# ==========================================

def low_attendance_courses(username):

    data = load_attendance()

    if username not in data:
        return []

    low = []

    for course in data[username]:

        percentage = attendance_percentage(
            username,
            course
        )

        if percentage < MIN_ATTENDANCE:

            low.append(
                (
                    course,
                    percentage
                )
            )

    return low


# ==========================================
# OVERALL ATTENDANCE
# ==========================================

def overall_attendance(username):

    data = load_attendance()

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

    total = total_present + total_absent

    if total == 0:
        return 0

    return round(
        (total_present / total) * 100,
        2
    )


# ==========================================
# RESET COURSE ATTENDANCE
# ==========================================

def reset_course(username, course_code):

    data = load_attendance()

    if (
        username not in data
        or
        course_code not in data[username]
    ):
        print("Course not found.")
        return

    data[username][course_code] = {
        "present": 0,
        "absent": 0
    }

    save_attendance(data)

    print("Attendance reset successfully.")


# ==========================================
# DELETE COURSE RECORD
# ==========================================

def delete_course(username, course_code):

    data = load_attendance()

    if (
        username not in data
        or
        course_code not in data[username]
    ):
        print("Course not found.")
        return

    del data[username][course_code]

    save_attendance(data)

    print("Attendance record deleted.")


# ==========================================
# MENU
# ==========================================

def attendance_menu(username):

    while True:

        print("\n===== ATTENDANCE MENU =====")

        print("1. Mark Present")
        print("2. Mark Absent")
        print("3. Course Report")
        print("4. All Courses Report")
        print("5. Low Attendance")
        print("6. Overall Attendance")
        print("7. Reset Course")
        print("8. Delete Course")
        print("9. Back")

        choice = input("Choice: ")

        if choice == "1":

            code = input("Course Code: ")

            mark_present(
                username,
                code
            )

        elif choice == "2":

            code = input("Course Code: ")

            mark_absent(
                username,
                code
            )

        elif choice == "3":

            code = input("Course Code: ")

            course_report(
                username,
                code
            )

        elif choice == "4":

            all_courses_report(
                username
            )

        elif choice == "5":

            low = low_attendance_courses(
                username
            )

            if not low:

                print("No low attendance courses.")

            else:

                print("\nLow Attendance Courses:")

                for course, pct in low:

                    print(
                        f"{course} -> {pct}%"
                    )

        elif choice == "6":

            print(
                f"\nOverall Attendance: "
                f"{overall_attendance(username)}%"
            )

        elif choice == "7":

            code = input("Course Code: ")

            reset_course(
                username,
                code
            )

        elif choice == "8":

            code = input("Course Code: ")

            delete_course(
                username,
                code
            )

        elif choice == "9":
            break

        else:
            print("Invalid choice.")


# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":

    user = "demo"

    initialize_user(user)

    attendance_menu(user)