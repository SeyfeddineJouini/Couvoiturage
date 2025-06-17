import subprocess
import time
import unittest
from datetime import datetime, timezone
import requests
from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import threading
import json

stop_thread = False

users = [
    {
        "email": "user1@example.com",
        "password": "password1",
        "last_name": "Dupont",
        "first_name": "Jean",
        "address": "10 Rue de Rivoli, 75004 Paris"
    },
    {
        "email": "user2@example.com",
        "password": "password2",
        "last_name": "Martin",
        "first_name": "Marie",
        "address": "20 Avenue des Champs-Élysées, 75008 Paris"
    },
    {
        "email": "user3@example.com",
        "password": "password3",
        "last_name": "Bernard",
        "first_name": "Luc",
        "address": "30 Boulevard Saint-Germain, 75005 Paris "
    },
    {
        "email": "user4@example.com",
        "password": "password4",
        "last_name": "Dubois",
        "first_name": "Sophie",
        "address": "40 Rue de la Paix, 75002 Paris"
    },
    {
        "email": "user5@example.com",
        "password": "password5",
        "last_name": "Moreau",
        "first_name": "Pierre",
        "address": "50 Rue du Faubourg Saint-Honoré, 75008 Paris"
    }
]

def generate_iso_date():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def run_command(command):
    while not stop_thread:
        subprocess.run(command, shell=True)
        time.sleep(1)
    print("Thread has been stopped.")

class TestUserCreation(unittest.TestCase):
    def setUp(self):
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.get("http://localhost:3000")
        time.sleep(2)

    def tearDown(self):
        self.driver.quit()

    def test_user_creation_and_login(self):
        driver = self.driver

        inscrire_link = driver.find_element(By.LINK_TEXT, "S'inscrire")
        inscrire_link.click()
        time.sleep(2)

        driver.find_element(By.ID, "email").send_keys("test@exemple.com")
        driver.find_element(By.ID, "password").send_keys("test")
        driver.find_element(By.ID, "last_name").send_keys("Doe")
        driver.find_element(By.ID, "first_name").send_keys("John")
        driver.find_element(By.ID, "address").send_keys("123 Main St")

        is_driver_checkbox = driver.find_element(By.ID, "is_driver")
        if not is_driver_checkbox.is_selected():
            is_driver_checkbox.click()

        driver.find_element(By.CLASS_NAME, "submit-btn").click()

        time.sleep(3)

        success_message = driver.find_element(By.CLASS_NAME, "success-message")
        self.assertTrue(success_message.is_displayed(), "User creation failed or success message not found.")

        time.sleep(3)

        driver.find_element(By.LINK_TEXT, "Connexion").click()
        time.sleep(2)

        driver.find_element(By.ID, "email").send_keys("test@exemple.com")
        driver.find_element(By.ID, "password").send_keys("test")
        driver.find_element(By.CLASS_NAME, "submit-btn").click()

        time.sleep(3)

        element = driver.find_element(By.LINK_TEXT, "Mon EDT")
        assert element.is_displayed(), "Mon EDT not displayed -> login failed."
        self.tearDown()

class TestUserRelation(unittest.TestCase):
    def setUp(self):
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.get("http://localhost:3000")
        time.sleep(2)

    def tearDown(self):
        self.driver.quit()

    def test_user_relation(self):
        url_signup = 'http://127.0.0.1:5005/signup'
        for user in users:
            data_signup = {
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "address": user["address"],
                "password": user["password"],
                "is_driver": 1
            }

            print(data_signup)

            response = requests.post(url_signup, json=data_signup)
            response_data = response.json()
            print('REPONSE DATA', response_data)

            self.assertEqual(response_data["status"], "success", f"User creation failed for {user['email']}")
            self.assertEqual(response_data["message"], "Inscription réussie !", f"Unexpected message for {user['email']}")
            self.assertIn("user_id", response_data, f"user_id not found in response for {user['email']}")
            print(f"User {user['email']} created successfully.")

        url_login = 'http://localhost:5005/login'

        log_user1 = {
            "email": users[0]["email"],
            "password": users[0]["password"]
        }

        request_login = requests.post(url_login, json=log_user1)

        response_login = request_login.json()

        user1_id = response_login.get('token')

        url_cal = 'http://localhost:5005/saveCal'

        calendar_user1 = 'calendar_user1.json'
        with open(calendar_user1, 'r', encoding='utf-8') as file:
            data_cal = json.load(file)

        data_cal.update({'user_id': user1_id})
        for day in data_cal['calendar_changes']['days']:
            day['date'] = generate_iso_date()
            print('date changée', day['date'])


        rep_cal = requests.post(url_cal, json=data_cal)

        # Assert the response message
        assert(rep_cal.json().get('message') == 'Calendar updated successfully')

        calendar_user = 'calendar_rest.json'
        for i in range(1, len(users)):
            log_user = {
                "email": users[i]["email"],
                "password": users[i]["password"]
            }

            request_login = requests.post(url_login, json=log_user)

            response_login = request_login.json()

            user_id = response_login.get('token')

            with open(calendar_user, 'r') as file:
                data_cal_rest = json.load(file)

            data_cal_rest.update({'user_id': user_id})

            rep_cal = requests.post(url_cal, json=data_cal_rest)

            assert(rep_cal.json().get('message') == 'Calendar updated successfully')


if __name__ == "__main__":
    file_path = '../../instance/users.db'

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"{file_path} has been deleted.")
    else:
        print(f"{file_path} does not exist.")

    # Define the commands to be executed
    command1 = "cd ../.. && python3 manageReact.py"
    command2 = "cd ../.. && npm start"

    # Create threads
    thread1 = threading.Thread(target=run_command, args=(command1,))
    thread2 = threading.Thread(target=run_command, args=(command2,))

    thread1.start()
    print("Server is starting...")
    time.sleep(15)
    thread2.start()
    print("React is starting...")
    time.sleep(15)

    unittest.main(exit=False)
    stop_thread = True
    print("Stopping threads...")
    thread1.join()
    thread2.join()