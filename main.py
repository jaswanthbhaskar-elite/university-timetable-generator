# main.py

from auth import (
    register,
    login,
    change_password,
    delete_account
)

from timetable import semester_menu

from attendance import attendance_menu

from assignments import assignment_menu

from exams import exam_menu

from gpa import gpa_menu

from notifications import notification_menu

from reports import reports_menu

from backup import backup_menu

from dashboard import dashboard_menu


# ==========================================
# STUDENT PANEL
# ==========================================

def student_panel(username):

    while True:

        print(
            "\n================================="
        )

        print(
            f" Welcome {username}"
        )

        print(
            "================================="
        )

        print(
            "1. Timetable"
        )

        print(
            "2. Attendance"
        )

        print(
            "3. Assignments"
        )

        print(
            "4. Exams"
        )

        print(
            "5. GPA / CGPA"
        )

        print(
            "6. Notifications"
        )

        print(
            "7. Reports"
        )

        print(
            "8. Dashboard"
        )

        print(
            "9. Backup"
        )

        print(
            "10. Change Password"
        )

        print(
            "11. Delete Account"
        )

        print(
            "12. Logout"
        )

        choice = input(
            "\nChoice: "
        )

        # -------------------------
        # Timetable
        # -------------------------

        if choice == "1":

            semester_name = input(
                "Semester Name: "
            )

            data = {
                "semesters": {
                    semester_name: []
                }
            }

            semester_menu(
                data,
                semester_name
            )

        # -------------------------
        # Attendance
        # -------------------------

        elif choice == "2":

            attendance_menu(
                username
            )

        # -------------------------
        # Assignments
        # -------------------------

        elif choice == "3":

            assignment_menu(
                username
            )

        # -------------------------
        # Exams
        # -------------------------

        elif choice == "4":

            exam_menu(
                username
            )

        # -------------------------
        # GPA
        # -------------------------

        elif choice == "5":

            gpa_menu(
                username
            )

        # -------------------------
        # Notifications
        # -------------------------

        elif choice == "6":

            notification_menu(
                username
            )

        # -------------------------
        # Reports
        # -------------------------

        elif choice == "7":

            reports_menu(
                username
            )

        # -------------------------
        # Dashboard
        # -------------------------

        elif choice == "8":

            dashboard_menu(
                username
            )

        # -------------------------
        # Backup
        # -------------------------

        elif choice == "9":

            backup_menu()

        # -------------------------
        # Change Password
        # -------------------------

        elif choice == "10":

            change_password(
                username
            )

        # -------------------------
        # Delete Account
        # -------------------------

        elif choice == "11":

            confirm = input(
                "Delete account permanently? (y/n): "
            )

            if confirm.lower() == "y":

                delete_account(
                    username
                )

                print(
                    "Account Deleted."
                )

                break

        # -------------------------
        # Logout
        # -------------------------

        elif choice == "12":

            print(
                "\nLogged Out."
            )

            break

        else:

            print(
                "Invalid Choice."
            )


# ==========================================
# MAIN MENU
# ==========================================

def main():

    while True:

        print(
            "\n================================="
        )

        print(
            " UNIVERSITY MANAGEMENT SYSTEM "
        )

        print(
            "================================="
        )

        print(
            "1. Register"
        )

        print(
            "2. Login"
        )

        print(
            "3. Exit"
        )

        choice = input(
            "\nChoice: "
        )

        # -------------------------
        # REGISTER
        # -------------------------

        if choice == "1":

            register()

        # -------------------------
        # LOGIN
        # -------------------------

        elif choice == "2":

            username = login()

            if username:

                student_panel(
                    username
                )

        # -------------------------
        # EXIT
        # -------------------------

        elif choice == "3":

            print(
                "\nThank You!"
            )

            break

        else:

            print(
                "Invalid Choice."
            )


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":

    main()