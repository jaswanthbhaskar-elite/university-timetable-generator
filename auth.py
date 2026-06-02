# auth.py

import json
import os
import hashlib
from getpass import getpass

USERS_FILE = "users.json"


# ==========================================
# File Operations
# ==========================================

def load_users():
    """Load users from JSON file."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_users(users):
    """Save users to JSON file."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ==========================================
# Password Utilities
# ==========================================

def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed_password):
    return hash_password(password) == hashed_password


# ==========================================
# Validation
# ==========================================

def username_exists(users, username):
    return username in users


def validate_username(username):
    if len(username) < 3:
        return False

    return username.replace("_", "").isalnum()


def validate_password(password):
    if len(password) < 6:
        return False

    return True


# ==========================================
# Registration
# ==========================================

def register():
    users = load_users()

    print("\n========== REGISTER ==========")

    while True:
        username = input("Username: ").strip()

        if not validate_username(username):
            print(
                "Username must be at least 3 characters and contain only letters, numbers, or underscores."
            )
            continue

        if username_exists(users, username):
            print("Username already exists.")
            continue

        break

    while True:
        password = getpass("Password: ")
        confirm = getpass("Confirm Password: ")

        if password != confirm:
            print("Passwords do not match.")
            continue

        if not validate_password(password):
            print("Password must be at least 6 characters.")
            continue

        break

    full_name = input("Full Name: ").strip()
    email = input("Email: ").strip()

    users[username] = {
        "password": hash_password(password),
        "full_name": full_name,
        "email": email,
        "role": "student"
    }

    save_users(users)

    print("\nRegistration Successful!\n")


# ==========================================
# Login
# ==========================================

def login():
    users = load_users()

    print("\n========== LOGIN ==========")

    username = input("Username: ").strip()
    password = getpass("Password: ")

    if username not in users:
        print("User not found.")
        return None

    stored_password = users[username]["password"]

    if verify_password(password, stored_password):
        print(f"\nWelcome, {users[username]['full_name']}!")
        return username

    print("Invalid password.")
    return None


# ==========================================
# Change Password
# ==========================================

def change_password(username):
    users = load_users()

    if username not in users:
        print("User not found.")
        return

    print("\n========== CHANGE PASSWORD ==========")

    current = getpass("Current Password: ")

    if not verify_password(current, users[username]["password"]):
        print("Incorrect current password.")
        return

    while True:
        new_pass = getpass("New Password: ")
        confirm = getpass("Confirm New Password: ")

        if new_pass != confirm:
            print("Passwords do not match.")
            continue

        if not validate_password(new_pass):
            print("Password must be at least 6 characters.")
            continue

        break

    users[username]["password"] = hash_password(new_pass)

    save_users(users)

    print("Password changed successfully.")


# ==========================================
# Delete Account
# ==========================================

def delete_account(username):
    users = load_users()

    if username not in users:
        print("User not found.")
        return False

    confirm = input(
        f"Delete account '{username}'? This cannot be undone (y/n): "
    ).lower()

    if confirm != "y":
        print("Cancelled.")
        return False

    del users[username]

    save_users(users)

    print("Account deleted.")
    return True


# ==========================================
# User Profile
# ==========================================

def view_profile(username):
    users = load_users()

    if username not in users:
        print("User not found.")
        return

    user = users[username]

    print("\n========== PROFILE ==========")
    print(f"Username : {username}")
    print(f"Full Name: {user.get('full_name', '')}")
    print(f"Email    : {user.get('email', '')}")
    print(f"Role     : {user.get('role', 'student')}")
    print("=" * 30)


# ==========================================
# Admin Functions
# ==========================================

def list_users():
    users = load_users()

    if not users:
        print("No users found.")
        return

    print("\n========== USERS ==========")

    for i, username in enumerate(users, start=1):
        user = users[username]

        print(
            f"{i}. "
            f"{username:<15} "
            f"{user.get('full_name',''):<20} "
            f"{user.get('email','')}"
        )


# ==========================================
# Create Default Admin
# ==========================================

def create_default_admin():
    users = load_users()

    if "admin" in users:
        return

    users["admin"] = {
        "password": hash_password("admin123"),
        "full_name": "System Administrator",
        "email": "admin@university.com",
        "role": "admin"
    }

    save_users(users)


# ==========================================
# Testing
# ==========================================

if __name__ == "__main__":

    create_default_admin()

    while True:

        print("\n===== AUTH MENU =====")
        print("1. Register")
        print("2. Login")
        print("3. List Users")
        print("4. Exit")

        choice = input("Choice: ")

        if choice == "1":
            register()

        elif choice == "2":
            login()

        elif choice == "3":
            list_users()

        elif choice == "4":
            break

        else:
            print("Invalid choice.")