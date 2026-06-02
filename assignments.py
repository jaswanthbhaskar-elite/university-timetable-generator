# assignments.py

import json
import os
from datetime import datetime

ASSIGNMENT_FILE = "assignments.json"

PRIORITIES = [
    "Low",
    "Medium",
    "High"
]


# ==========================================
# FILE OPERATIONS
# ==========================================

def load_assignments():

    if os.path.exists(ASSIGNMENT_FILE):

        with open(ASSIGNMENT_FILE, "r") as f:
            return json.load(f)

    return {}


def save_assignments(data):

    with open(ASSIGNMENT_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ==========================================
# USER SETUP
# ==========================================

def initialize_user(username):

    data = load_assignments()

    if username not in data:

        data[username] = []

        save_assignments(data)

    return data


# ==========================================
# DATE VALIDATION
# ==========================================

def valid_date(date_string):

    try:

        datetime.strptime(
            date_string,
            "%Y-%m-%d"
        )

        return True

    except:

        return False


# ==========================================
# ADD ASSIGNMENT
# ==========================================

def add_assignment(username):

    data = load_assignments()

    initialize_user(username)

    data = load_assignments()

    print("\n===== ADD ASSIGNMENT =====")

    title = input("Title: ").strip()

    course = input(
        "Course Code: "
    ).strip()

    description = input(
        "Description: "
    ).strip()

    while True:

        due_date = input(
            "Due Date (YYYY-MM-DD): "
        ).strip()

        if valid_date(due_date):
            break

        print("Invalid date format.")

    print("\nPriority")

    for i, p in enumerate(
        PRIORITIES,
        start=1
    ):
        print(f"{i}. {p}")

    priority = PRIORITIES[
        int(input("Choice: ")) - 1
    ]

    assignment = {

        "id": len(
            data[username]
        ) + 1,

        "title": title,

        "course": course,

        "description": description,

        "due_date": due_date,

        "priority": priority,

        "status": "Pending",

        "created_at":
            datetime.now()
            .strftime("%Y-%m-%d %H:%M:%S")
    }

    data[username].append(
        assignment
    )

    save_assignments(data)

    print(
        "Assignment added successfully."
    )


# ==========================================
# LIST ASSIGNMENTS
# ==========================================

def list_assignments(username):

    data = load_assignments()

    if (
        username not in data
        or
        not data[username]
    ):

        print("No assignments found.")

        return

    print("\n===== ASSIGNMENTS =====")

    for a in data[username]:

        print(
            f"\nID: {a['id']}"
        )

        print(
            f"Title: {a['title']}"
        )

        print(
            f"Course: {a['course']}"
        )

        print(
            f"Due Date: {a['due_date']}"
        )

        print(
            f"Priority: {a['priority']}"
        )

        print(
            f"Status: {a['status']}"
        )


# ==========================================
# MARK COMPLETE
# ==========================================

def mark_completed(
    username,
    assignment_id
):

    data = load_assignments()

    if username not in data:
        return

    for assignment in data[username]:

        if (
            assignment["id"]
            ==
            assignment_id
        ):

            assignment["status"] = (
                "Completed"
            )

            save_assignments(data)

            print(
                "Assignment completed."
            )

            return

    print(
        "Assignment not found."
    )


# ==========================================
# DELETE ASSIGNMENT
# ==========================================

def delete_assignment(
    username,
    assignment_id
):

    data = load_assignments()

    if username not in data:
        return

    for i, assignment in enumerate(
        data[username]
    ):

        if (
            assignment["id"]
            ==
            assignment_id
        ):

            del data[username][i]

            save_assignments(
                data
            )

            print(
                "Assignment deleted."
            )

            return

    print(
        "Assignment not found."
    )


# ==========================================
# PENDING ASSIGNMENTS
# ==========================================

def pending_assignments(
    username
):

    data = load_assignments()

    if username not in data:
        return

    print(
        "\n===== PENDING ====="
    )

    found = False

    for assignment in data[
        username
    ]:

        if (
            assignment["status"]
            ==
            "Pending"
        ):

            found = True

            print(
                f"{assignment['id']} - "
                f"{assignment['title']} "
                f"({assignment['due_date']})"
            )

    if not found:

        print(
            "No pending assignments."
        )


# ==========================================
# OVERDUE ASSIGNMENTS
# ==========================================

def overdue_assignments(
    username
):

    data = load_assignments()

    if username not in data:
        return

    today = datetime.now().date()

    print(
        "\n===== OVERDUE ====="
    )

    found = False

    for assignment in data[
        username
    ]:

        due = datetime.strptime(
            assignment["due_date"],
            "%Y-%m-%d"
        ).date()

        if (
            due < today
            and
            assignment["status"]
            ==
            "Pending"
        ):

            found = True

            print(
                f"{assignment['title']} "
                f"({assignment['due_date']})"
            )

    if not found:

        print(
            "No overdue assignments."
        )


# ==========================================
# STATISTICS
# ==========================================

def assignment_stats(
    username
):

    data = load_assignments()

    if username not in data:
        return

    total = len(
        data[username]
    )

    completed = 0
    pending = 0

    for assignment in data[
        username
    ]:

        if (
            assignment["status"]
            ==
            "Completed"
        ):

            completed += 1

        else:

            pending += 1

    print(
        "\n===== STATISTICS ====="
    )

    print(
        f"Total      : {total}"
    )

    print(
        f"Completed  : {completed}"
    )

    print(
        f"Pending    : {pending}"
    )

    if total:

        print(
            f"Completion : "
            f"{round((completed/total)*100,2)}%"
        )


# ==========================================
# SEARCH
# ==========================================

def search_assignment(
    username,
    keyword
):

    data = load_assignments()

    if username not in data:
        return

    found = False

    for assignment in data[
        username
    ]:

        if (
            keyword.lower()
            in
            assignment["title"]
            .lower()
        ):

            found = True

            print(
                f"{assignment['id']} - "
                f"{assignment['title']}"
            )

    if not found:

        print(
            "No results found."
        )


# ==========================================
# MENU
# ==========================================

def assignment_menu(
    username
):

    initialize_user(
        username
    )

    while True:

        print(
            "\n===== ASSIGNMENT MENU ====="
        )

        print(
            "1. Add Assignment"
        )

        print(
            "2. View Assignments"
        )

        print(
            "3. Mark Complete"
        )

        print(
            "4. Delete Assignment"
        )

        print(
            "5. Pending Assignments"
        )

        print(
            "6. Overdue Assignments"
        )

        print(
            "7. Statistics"
        )

        print(
            "8. Search"
        )

        print(
            "9. Back"
        )

        choice = input(
            "Choice: "
        )

        if choice == "1":

            add_assignment(
                username
            )

        elif choice == "2":

            list_assignments(
                username
            )

        elif choice == "3":

            aid = int(
                input(
                    "Assignment ID: "
                )
            )

            mark_completed(
                username,
                aid
            )

        elif choice == "4":

            aid = int(
                input(
                    "Assignment ID: "
                )
            )

            delete_assignment(
                username,
                aid
            )

        elif choice == "5":

            pending_assignments(
                username
            )

        elif choice == "6":

            overdue_assignments(
                username
            )

        elif choice == "7":

            assignment_stats(
                username
            )

        elif choice == "8":

            keyword = input(
                "Keyword: "
            )

            search_assignment(
                username,
                keyword
            )

        elif choice == "9":

            break

        else:

            print(
                "Invalid choice."
            )


# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":

    user = "demo"

    assignment_menu(user)