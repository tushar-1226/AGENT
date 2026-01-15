"""
Test script to generate sample analytics data
"""
import requests
import random
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Sample endpoints to test
endpoints = [
    "/api/status",
    "/api/session/list",
    "/api/projects/list",
    "/api/system/complete",
    "/api/analytics/complete"
]

methods = ["GET", "POST", "PUT", "DELETE"]
actions = ["login", "logout", "create_project", "delete_project", "update_settings", "view_dashboard"]

print("Generating sample analytics data...")

# Generate API call logs
for i in range(50):
    endpoint = random.choice(endpoints)
    method = random.choice(methods)
    status_code = random.choice([200, 200, 200, 201, 400, 404, 500])
    response_time = random.uniform(10, 500)

    data = {
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "response_time": response_time,
        "user_id": random.randint(1, 10),
        "request_size": random.randint(100, 5000),
        "response_size": random.randint(500, 10000)
    }

    try:
        response = requests.post(f"{BASE_URL}/api/analytics/log-api-call", json=data)
        print(f"Logged API call: {endpoint} - Status: {status_code}")
    except Exception as e:
        print(f"Error logging API call: {e}")

    time.sleep(0.1)

# Generate user activity logs
for i in range(30):
    action = random.choice(actions)
    user_id = random.randint(1, 10)

    data = {
        "user_id": user_id,
        "action": action,
        "details": f"User {user_id} performed {action}"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/analytics/log-activity", json=data)
        print(f"Logged activity: {action} by user {user_id}")
    except Exception as e:
        print(f"Error logging activity: {e}")

    time.sleep(0.1)

print("\nSample data generation complete!")
print("Now fetching analytics...")

# Fetch and display analytics
try:
    response = requests.get(f"{BASE_URL}/api/analytics/complete?hours=24")
    analytics = response.json()
    print("\nAnalytics Summary:")
    print(f"Total API Calls: {analytics['api_calls']['total_calls']}")
    print(f"Total Activities: {analytics['user_activity']['total_activities']}")
    print(f"Total Errors: {analytics['errors']['total_errors']}")
except Exception as e:
    print(f"Error fetching analytics: {e}")
