import csv
import hashlib
import requests
import json

url_signup = 'http://127.0.0.1:5000/signup'
url_saveCal = 'http://127.0.0.1:5000/saveCal'
users_ids = []
with open('users.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        data_signup = {
            "email": row["email"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "address": row["address"],
            "password": hashlib.sha256(row["password"].encode()).hexdigest(),
            "is_driver" : 0
        }

        response_signup = requests.post(url_signup, json=data_signup)
        calendar_str = row["calendar"].replace("'", "\"")
        try:
            calendar = json.loads(calendar_str)
            calendar["user_id"] = response_signup.json()["user_id"]
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for user {row['email']}: {e}")
            continue

