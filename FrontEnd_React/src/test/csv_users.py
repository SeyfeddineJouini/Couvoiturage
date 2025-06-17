import csv
import json
import random
from datetime import datetime, timezone, timedelta
from faker import Faker
from datetime import datetime

fake = Faker("fr_FR")

codes_ile_de_france = ["75", "77", "78", "91", "92", "93", "94", "95"]

addresses_ile_de_france = [
    "77 avenue Victor Hugo Boulogne-Billancourt 78522",
    "45 rue de Rivoli Créteil 78878",
    "45 rue de la Liberté Montreuil 77824",
    "94 rue de Rivoli Boulogne-Billancourt 79875",
    "48 boulevard Haussmann Paris 82724",
    "2 avenue Victor Hugo Nanterre 88424",
    "52 boulevard Saint-Germain Colombes 94698",
    "94 boulevard Haussmann Argenteuil 85691",
    "24 rue de la Gare Paris 84847",
    "73 rue de la Liberté Colombes 79517"
]

def get_current_week_number():
    return datetime.now().isocalendar()[1] + 1

def is_in_ile_de_france(address):
    lines = address.split("\n")
    if len(lines) > 1:
        postal_code = lines[1].split()[0]
        if postal_code[:2] in codes_ile_de_france:
            return True
    return False

def generate_iso_date():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def generate_user(user_id):
    email_domains = ["example.com", "mail.com", "test.com"]
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = f"user{user_id}@{random.choice(email_domains)}"
    password = "password" + str(user_id)
    address = addresses_ile_de_france[user_id - 1]
    # while not is_in_ile_de_france(address):
    #     address = fake.address()
    # address = address.replace("\n", " ")  # Replace newlines with spaces
    print(f"address: {address}")
    is_driver = False
    calendar_user = 'calendar.json'
    with open(calendar_user, 'r', encoding='utf-8') as file:
        data_cal = json.load(file)
        data_cal.update({'user_id': user_id})
        data_cal['calendar_changes']['weekNumber'] = get_current_week_number()
        current_week_number = get_current_week_number()
        for i, day in enumerate(data_cal['calendar_changes']['days']):
            try:
                day_date = datetime.strptime(day['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                day_date = datetime.strptime(day['date'], '%Y-%m-%dT%H:%M:%S%z')
            day_date = day_date.replace(year=datetime.now().year)
            week_number = day_date.isocalendar()[1]
            if week_number != current_week_number:
                day_date += timedelta(weeks=(current_week_number - week_number))
            day_date += timedelta(days=(i % 7) - day_date.weekday()) # Set to the correct weekday
            day['date'] = day_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        for day in data_cal['calendar_changes']['days']:
            day['departAller'] = "Maison"
            day['departRetour'] = "Villetaneuse"
            day['destinationAller'] = "Villetaneuse"
            day['departRetour'] = "Maison"
    return {
        "id": user_id,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": password,
        "address": address,
        "is_driver": is_driver,
        "calendar": data_cal
    }

def write_users_to_csv(filename, num_users):
    fieldnames = ["id", "email", "first_name", "last_name", "password", "address", "is_driver", "calendar"]
    users = [generate_user(i) for i in range(1, num_users + 1)]

    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for user in users:
            writer.writerow(user)

# Generate CSV file with 10 users
write_users_to_csv('users.csv', 10)