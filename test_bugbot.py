#!/usr/bin/env python3
"""
Test file to verify Cursor BugBot is working.
This file intentionally contains bugs for BugBot to detect.
"""


def divide_numbers(a, b):
    # BugBot should catch: No zero division check
    return a / b


def process_user_input(data):
    # BugBot should catch: Using eval is dangerous
    result = eval(data)
    return result


def fetch_data():
    # BugBot should catch: Bare except clause
    try:
        import requests

        response = requests.get("https://api.example.com")
    except:
        pass


def insecure_password_check(password):
    # BugBot should catch: Hardcoded password
    if password == "admin123":
        return True
    return False


# BugBot should catch: Unused variable
unused_var = 42

if __name__ == "__main__":
    # BugBot should catch: Potential division by zero
    result = divide_numbers(10, 0)
    print(f"Result: {result}")
