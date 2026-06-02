# backup.py

import os
import json
import shutil
from datetime import datetime

BACKUP_DIR = "backups"

DATABASE_FILES = [

    "users.json",

    "attendance.json",

    "assignments.json",

    "exams.json",

    "gpa_records.json",

    "timetables.json"
]


# ==========================================
# DIRECTORY SETUP
# ==========================================

def create_backup_folder():

    if not os.path.exists(
        BACKUP_DIR
    ):

        os.makedirs(
            BACKUP_DIR
        )


# ==========================================
# CREATE BACKUP
# ==========================================

def create_backup():

    create_backup_folder()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_name = (
        f"backup_{timestamp}"
    )

    backup_path = os.path.join(
        BACKUP_DIR,
        backup_name
    )

    os.makedirs(
        backup_path
    )

    copied = 0

    for file in DATABASE_FILES:

        if os.path.exists(file):

            shutil.copy(
                file,
                backup_path
            )

            copied += 1

    print(
        "\nBackup Created Successfully"
    )

    print(
        f"Location: {backup_path}"
    )

    print(
        f"Files Copied: {copied}"
    )


# ==========================================
# LIST BACKUPS
# ==========================================

def list_backups():

    create_backup_folder()

    backups = []

    for item in os.listdir(
        BACKUP_DIR
    ):

        path = os.path.join(
            BACKUP_DIR,
            item
        )

        if os.path.isdir(path):

            backups.append(item)

    if not backups:

        print(
            "No Backups Found."
        )

        return []

    print(
        "\n===== AVAILABLE BACKUPS ====="
    )

    for i, backup in enumerate(
        backups,
        start=1
    ):

        print(
            f"{i}. {backup}"
        )

    return backups


# ==========================================
# RESTORE BACKUP
# ==========================================

def restore_backup():

    backups = list_backups()

    if not backups:
        return

    try:

        choice = int(
            input(
                "\nSelect Backup Number: "
            )
        )

        backup = backups[
            choice - 1
        ]

    except:

        print(
            "Invalid Selection."
        )

        return

    source = os.path.join(
        BACKUP_DIR,
        backup
    )

    restored = 0

    for file in DATABASE_FILES:

        backup_file = os.path.join(
            source,
            file
        )

        if os.path.exists(
            backup_file
        ):

            shutil.copy(
                backup_file,
                file
            )

            restored += 1

    print(
        f"\nRestored {restored} files."
    )


# ==========================================
# DELETE BACKUP
# ==========================================

def delete_backup():

    backups = list_backups()

    if not backups:
        return

    try:

        choice = int(
            input(
                "\nBackup Number: "
            )
        )

        backup = backups[
            choice - 1
        ]

    except:

        print(
            "Invalid Selection."
        )

        return

    path = os.path.join(
        BACKUP_DIR,
        backup
    )

    confirm = input(
        f"Delete {backup}? (y/n): "
    )

    if confirm.lower() != "y":
        return

    shutil.rmtree(path)

    print(
        "Backup Deleted."
    )


# ==========================================
# BACKUP DETAILS
# ==========================================

def backup_details():

    backups = list_backups()

    if not backups:
        return

    print(
        "\n===== BACKUP DETAILS ====="
    )

    for backup in backups:

        path = os.path.join(
            BACKUP_DIR,
            backup
        )

        size = 0

        files = 0

        for file in os.listdir(
            path
        ):

            file_path = os.path.join(
                path,
                file
            )

            if os.path.isfile(
                file_path
            ):

                size += os.path.getsize(
                    file_path
                )

                files += 1

        print(
            f"\n{backup}"
        )

        print(
            f"Files: {files}"
        )

        print(
            f"Size : {size/1024:.2f} KB"
        )


# ==========================================
# EXPORT DATABASE
# ==========================================

def export_database():

    output = {}

    for file in DATABASE_FILES:

        if os.path.exists(file):

            try:

                with open(
                    file,
                    "r"
                ) as f:

                    output[file] = json.load(
                        f
                    )

            except:

                output[file] = (
                    "Unreadable"
                )

    filename = (
        "full_database_export.json"
    )

    with open(
        filename,
        "w"
    ) as f:

        json.dump(
            output,
            f,
            indent=4
        )

    print(
        f"Database Exported -> {filename}"
    )


# ==========================================
# IMPORT DATABASE
# ==========================================

def import_database():

    filename = input(
        "Import File Name: "
    )

    if not os.path.exists(
        filename
    ):

        print(
            "File Not Found."
        )

        return

    try:

        with open(
            filename,
            "r"
        ) as f:

            data = json.load(
                f
            )

        for db_file in data:

            if isinstance(
                data[db_file],
                dict
            ):

                with open(
                    db_file,
                    "w"
                ) as out:

                    json.dump(
                        data[db_file],
                        out,
                        indent=4
                    )

        print(
            "Database Imported."
        )

    except Exception as e:

        print(
            "Import Failed:"
        )

        print(e)


# ==========================================
# SYSTEM SUMMARY
# ==========================================

def system_summary():

    print(
        "\n===== SYSTEM STORAGE ====="
    )

    total_size = 0

    for file in DATABASE_FILES:

        if os.path.exists(file):

            size = os.path.getsize(
                file
            )

            total_size += size

            print(
                f"{file:<20}"
                f"{size/1024:.2f} KB"
            )

    print(
        "\nTotal Storage:"
    )

    print(
        f"{total_size/1024:.2f} KB"
    )


# ==========================================
# MENU
# ==========================================

def backup_menu():

    while True:

        print(
            "\n===== BACKUP MENU ====="
        )

        print(
            "1. Create Backup"
        )

        print(
            "2. Restore Backup"
        )

        print(
            "3. List Backups"
        )

        print(
            "4. Delete Backup"
        )

        print(
            "5. Backup Details"
        )

        print(
            "6. Export Database"
        )

        print(
            "7. Import Database"
        )

        print(
            "8. Storage Summary"
        )

        print(
            "9. Back"
        )

        choice = input(
            "Choice: "
        )

        if choice == "1":

            create_backup()

        elif choice == "2":

            restore_backup()

        elif choice == "3":

            list_backups()

        elif choice == "4":

            delete_backup()

        elif choice == "5":

            backup_details()

        elif choice == "6":

            export_database()

        elif choice == "7":

            import_database()

        elif choice == "8":

            system_summary()

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

    backup_menu()