# exams.py

import json
import os
from datetime import datetime

EXAM_FILE = "exams.json"


# ==========================================
# FILE OPERATIONS
# ==========================================

def load_exams():

    if os.path.exists(EXAM_FILE):

        with open(EXAM_FILE, "r") as f:
            return json.load(f)

    return {}


def save_exams(data):

    with open(EXAM_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ==========================================
# USER INITIALIZATION
# ==========================================

def initialize_user(username):

    data = load_exams()

    if username not in data:

        data[username] = []

        save_exams(data)

    return data


# ==========================================
# DATE VALIDATION
# ==========================================

def valid_datetime(date_string):

    try:

        datetime.strptime(
            date_string,
            "%Y-%m-%d %H:%M"
        )

        return True

    except:

        return False


# ==========================================
# CONFLICT DETECTION
# ==========================================

def check_exam_conflict(
    exams,
    exam_date
):

    for exam in exams:

        if (
            exam["exam_date"]
            ==
            exam_date
        ):
            return True

    return False


# ==========================================
# ADD EXAM
# ==========================================

def add_exam(username):

    initialize_user(username)

    data = load_exams()

    print("\n===== ADD EXAM =====")

    subject = input(
        "Subject Name: "
    )

    course_code = input(
        "Course Code: "
    )

    venue = input(
        "Venue/Hall: "
    )

    seat_no = input(
        "Seat Number: "
    )

    while True:

        exam_date = input(
            "Date & Time (YYYY-MM-DD HH:MM): "
        )

        if valid_datetime(
            exam_date
        ):
            break

        print(
            "Invalid format."
        )

    if check_exam_conflict(
        data[username],
        exam_date
    ):

        print(
            "⚠ Conflict Detected!"
        )

        confirm = input(
            "Continue? (y/n): "
        )

        if confirm.lower() != "y":
            return

    exam = {

        "id":
            len(data[username]) + 1,

        "subject":
            subject,

        "course_code":
            course_code,

        "venue":
            venue,

        "seat_no":
            seat_no,

        "exam_date":
            exam_date
    }

    data[username].append(
        exam
    )

    save_exams(data)

    print(
        "Exam Added Successfully."
    )


# ==========================================
# LIST EXAMS
# ==========================================

def list_exams(username):

    data = load_exams()

    if (
        username not in data
        or
        not data[username]
    ):

        print(
            "No Exams Found."
        )

        return

    print(
        "\n===== EXAMS ====="
    )

    for exam in data[
        username
    ]:

        print(
            f"\nID: {exam['id']}"
        )

        print(
            f"Subject: {exam['subject']}"
        )

        print(
            f"Code: {exam['course_code']}"
        )

        print(
            f"Date: {exam['exam_date']}"
        )

        print(
            f"Venue: {exam['venue']}"
        )

        print(
            f"Seat No: {exam['seat_no']}"
        )


# ==========================================
# DELETE EXAM
# ==========================================

def delete_exam(
    username,
    exam_id
):

    data = load_exams()

    if username not in data:
        return

    for i, exam in enumerate(
        data[username]
    ):

        if exam["id"] == exam_id:

            del data[username][i]

            save_exams(data)

            print(
                "Exam Deleted."
            )

            return

    print(
        "Exam Not Found."
    )


# ==========================================
# EDIT EXAM
# ==========================================

def edit_exam(
    username,
    exam_id
):

    data = load_exams()

    if username not in data:
        return

    for exam in data[
        username
    ]:

        if exam["id"] == exam_id:

            print(
                "Leave Blank To Keep Old Value"
            )

            subject = input(
                "Subject: "
            )

            venue = input(
                "Venue: "
            )

            seat = input(
                "Seat No: "
            )

            if subject:
                exam["subject"] = subject

            if venue:
                exam["venue"] = venue

            if seat:
                exam["seat_no"] = seat

            save_exams(data)

            print(
                "Updated Successfully."
            )

            return

    print(
        "Exam Not Found."
    )


# ==========================================
# COUNTDOWN
# ==========================================

def exam_countdown(
    username
):

    data = load_exams()

    if username not in data:
        return

    now = datetime.now()

    print(
        "\n===== COUNTDOWN ====="
    )

    for exam in data[
        username
    ]:

        exam_time = datetime.strptime(
            exam["exam_date"],
            "%Y-%m-%d %H:%M"
        )

        diff = exam_time - now

        if diff.total_seconds() > 0:

            days = diff.days

            hours = (
                diff.seconds // 3600
            )

            print(
                f"{exam['subject']}: "
                f"{days} days "
                f"{hours} hrs left"
            )


# ==========================================
# UPCOMING EXAMS
# ==========================================

def upcoming_exams(
    username
):

    data = load_exams()

    if username not in data:
        return

    today = datetime.now()

    print(
        "\n===== UPCOMING ====="
    )

    for exam in data[
        username
    ]:

        exam_time = datetime.strptime(
            exam["exam_date"],
            "%Y-%m-%d %H:%M"
        )

        if exam_time >= today:

            print(
                f"{exam['subject']} "
                f"-> "
                f"{exam['exam_date']}"
            )


# ==========================================
# SEARCH EXAM
# ==========================================

def search_exam(
    username,
    keyword
):

    data = load_exams()

    if username not in data:
        return

    found = False

    for exam in data[
        username
    ]:

        if (
            keyword.lower()
            in
            exam["subject"]
            .lower()
        ):

            found = True

            print(
                f"{exam['subject']} "
                f"({exam['course_code']})"
            )

    if not found:

        print(
            "No Exams Found."
        )


# ==========================================
# HALL TICKET VIEW
# ==========================================

def hall_ticket(
    username
):

    data = load_exams()

    if username not in data:
        return

    print(
        "\n===== HALL TICKET ====="
    )

    for exam in data[
        username
    ]:

        print(
            f"{exam['subject']} | "
            f"{exam['venue']} | "
            f"Seat: {exam['seat_no']}"
        )


# ==========================================
# STATISTICS
# ==========================================

def exam_statistics(
    username
):

    data = load_exams()

    if username not in data:
        return

    total = len(
        data[username]
    )

    future = 0

    past = 0

    now = datetime.now()

    for exam in data[
        username
    ]:

        exam_time = datetime.strptime(
            exam["exam_date"],
            "%Y-%m-%d %H:%M"
        )

        if exam_time > now:
            future += 1
        else:
            past += 1

    print(
        "\n===== EXAM STATS ====="
    )

    print(
        f"Total Exams : {total}"
    )

    print(
        f"Upcoming    : {future}"
    )

    print(
        f"Completed   : {past}"
    )


# ==========================================
# MENU
# ==========================================

def exam_menu(username):

    initialize_user(
        username
    )

    while True:

        print(
            "\n===== EXAM MENU ====="
        )

        print("1. Add Exam")
        print("2. View Exams")
        print("3. Edit Exam")
        print("4. Delete Exam")
        print("5. Upcoming Exams")
        print("6. Countdown")
        print("7. Hall Ticket")
        print("8. Search")
        print("9. Statistics")
        print("10. Back")

        choice = input(
            "Choice: "
        )

        if choice == "1":

            add_exam(username)

        elif choice == "2":

            list_exams(username)

        elif choice == "3":

            exam_id = int(
                input(
                    "Exam ID: "
                )
            )

            edit_exam(
                username,
                exam_id
            )

        elif choice == "4":

            exam_id = int(
                input(
                    "Exam ID: "
                )
            )

            delete_exam(
                username,
                exam_id
            )

        elif choice == "5":

            upcoming_exams(
                username
            )

        elif choice == "6":

            exam_countdown(
                username
            )

        elif choice == "7":

            hall_ticket(
                username
            )

        elif choice == "8":

            keyword = input(
                "Keyword: "
            )

            search_exam(
                username,
                keyword
            )

        elif choice == "9":

            exam_statistics(
                username
            )

        elif choice == "10":

            break

        else:

            print(
                "Invalid Choice."
            )


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    exam_menu("demo")