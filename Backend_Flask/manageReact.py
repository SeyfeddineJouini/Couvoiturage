from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify  # type: ignore
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from flask_cors import CORS  # type: ignore
from utils import geocode_address, get_route, replace_placeholders
from models import db, User, RideRequest, DriverOffer, CalendarEntry, convert_iso_string_to_calendar_slots, local_midnight_to_utc_iso
from pingMail import send_offer_email, SENDER_EMAIL, SENDER_PASSWORD
from eralchemy import render_er
import os
import requests
import uuid
import json
import logging
from functools import wraps

# Configuration du logging pour écrire dans un fichier de trace.
logging.basicConfig(
    filename='trace.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

def log_call(func):
    """
    Décorateur pour enregistrer les appels et retours de fonctions dans le fichier trace.log.

    :param func: La fonction à instrumenter.
    :return: La fonction décorée qui logue l'appel et le retour.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"--> Appel: {func.__name__} args: {args} kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logging.info(f"<-- Fin: {func.__name__} return: {result}")
        return result
    return wrapper


# Initialisation de l'application Flask et de SQLAlchemy.
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'
# db.init_app(app)  # Activez cette ligne si vous utilisez SQLAlchemy via init_app.

###############################################################################
# ENDPOINTS POUR GESTION DES UTILISATEURS
###############################################################################

@app.route('/signup', methods=['POST'])
@log_call
def signup():
    """
    Endpoint: /signup
    Méthode: POST

    Description:
        Inscription d'un nouvel utilisateur.
        Valide l'unicité de l'email, effectue le géocodage de l'adresse,
        puis crée un nouvel utilisateur.

    Entrée (JSON):
        - email (str): Adresse e-mail de l'utilisateur.
        - first_name (str): Prénom.
        - last_name (str): Nom.
        - address (str): Adresse postale.
        - password (str): Mot de passe (en clair ou haché en production).
        - is_driver (bool): Indique si l'utilisateur est conducteur.

    Sortie (JSON):
        Un message de succès et l'ID de l'utilisateur nouvellement créé.
    """
    data = request.get_json()
    email = data['email']
    first_name = data['first_name']
    last_name = data['last_name']
    address = data['address']
    password = data['password']
    is_driver = data['is_driver']

    # Vérification de l'unicité de l'email
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Cette adresse e-mail est déjà utilisée.'}), 409

    # Géocodage de l'adresse
    lat, lon = geocode_address(address)
    if not lat or not lon:
        return jsonify({'error': 'Adresse invalide', 'status': 'error'}), 400

    new_user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        address=address,
        password=password,
        is_driver=is_driver
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': 'Inscription réussie !',
        'status': 'success',
        'user_id': new_user.id
    }), 201


@app.route('/login', methods=['POST'])
@log_call
def login():
    """
    Endpoint: /login
    Méthode: POST

    Description:
        Authentifie un utilisateur en vérifiant son email et son mot de passe.

    Entrée (JSON):
        - email (str): Adresse e-mail.
        - password (str): Mot de passe.

    Sortie (JSON):
        - Un token (ici, l'ID de l'utilisateur) en cas de succès, ou un message d'erreur.
    """
    data = request.get_json()
    print("Received data for login:", data)
    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid credentials : no accounts found'}), 401

    if user.password == password:
        token = user.id
        return jsonify({'token': token, 'status': 'success'})
    else:
        return jsonify({'error': 'Invalid credentials : wrong password'}), 401


@app.route('/user/<string:id>', methods=['GET'])
@log_call
def user_info(id):
    """
    Endpoint: /user/<id>
    Méthode: GET

    Description:
        Récupère et retourne les informations de l'utilisateur spécifié.

    Paramètre d'URL:
        - id (str): Identifiant de l'utilisateur.

    Sortie (JSON):
        Détails de l'utilisateur (prénom, nom, adresse, statut de conducteur).
    """
    user = User.query.filter_by(id=id).first()
    if user:
        return jsonify({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'address': user.address,
            'is_driver': user.is_driver
        })
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/passengers/<string:id>', methods=['GET'])
@log_call
def passengers(id):
    """
    Endpoint: /passengers/<id>
    Méthode: GET

    Description:
        Récupère la liste de tous les utilisateurs qui ne sont pas conducteurs, à l'exclusion de l'utilisateur spécifié.

    Paramètre d'URL:
        - id (str): Identifiant de l'utilisateur à exclure.

    Sortie (JSON):
        Liste des passagers (prénom, nom, adresse).
    """
    users = User.query.filter(User.id != id).all()
    passengers_list = []
    for u in users:
        if not u.is_driver:
            passengers_list.append({
                'first_name': u.first_name,
                'last_name': u.last_name,
                'address': u.address
            })
    return jsonify(passengers_list)

###############################################################################
# ENDPOINTS POUR LA SUPRRESSION D'UN UTILISATEUR
###############################################################################

@app.route('/api/users/<string:user_id>', methods=['DELETE'])
@log_call
def delete_user(user_id):
    """
    Endpoint: /api/users/<user_id>
    Méthode: DELETE

    Description:
        Supprime définitivement un utilisateur de la base de données.

    Paramètre d'URL:
        - user_id (str): Identifiant de l'utilisateur.

    Sortie (JSON):
        Message de confirmation ou d'erreur.
    """
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Supprimer les trajets
    RideRequest.query.filter_by(user_id=user_id).delete()

    # Supprimer les calendriers
    CalendarEntry.query.filter_by(user_id=user_id).delete()

    # Supprimer les offres de covoiturage (si applicable)
    DriverOffer.query.filter_by(driver_id=user_id).delete()

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Utilisateur supprimé avec succès'}), 200


###############################################################################
# ENDPOINTS POUR LA GESTION DU CALENDRIER
###############################################################################

@app.route('/saveCal', methods=['POST'])
@log_call
def save_calendar_iso():
    """
    Endpoint: /saveCal
    Méthode: POST

    Description:
        Sauvegarde (ou met à jour) les entrées de calendrier dans la table CalendarEntry.
        Pour chaque jour fourni dans "calendar_changes", le système vérifie s'il existe déjà
        une entrée pour (user_id, year, week_number, day_of_week). Si c'est le cas, il met à jour;
        sinon, il crée une nouvelle entrée.

    Entrée (JSON):
        - user_id (str): Identifiant de l'utilisateur.
        - calendar_changes (dict): Contient "weekNumber" et une liste "days" d'objets avec :
            - date (str, ISO8601)
            - startHour (int)
            - endHour (int)
            - departAller (str)
            - destinationAller (str)
            - departRetour (str)
            - destinationRetour (str)
            - disabled (bool)
            - roleAller (str)
            - roleRetour (str)
            - validatedAller (bool)
            - validatedRetour (bool)

    Sortie (JSON):
        Message de succès.
    """
    data = request.get_json()
    user_id = data.get("user_id")
    calendar_changes = data.get("calendar_changes")

    if not user_id or not calendar_changes:
        return jsonify({"error": "Missing user_id or calendar_changes"}), 400

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    days = calendar_changes.get("days", [])
    for day_obj in days:
        date_str = day_obj.get("date")
        if not date_str:
            continue

        iso_year, iso_week, iso_day = convert_iso_string_to_calendar_slots(date_str)
        print(f"Processing date: {date_str} -> Year: {iso_year}, Week: {iso_week}, Day: {iso_day}", flush=True)

        # placeholders ...

        # -- RECHERCHE D'UNE ENTREE EXISTANTE --
        # Recherche d'une entrée existante
        existing_entry = CalendarEntry.query.filter_by(
            user_id=user_id,
            year=iso_year,
            week_number=iso_week,
            day_of_week=iso_day
        ).first()


        if existing_entry:
            # Mise à jour
            existing_entry.start_hour = day_obj.get("startHour")
            existing_entry.end_hour = day_obj.get("endHour")
            existing_entry.depart_aller = replace_placeholders(day_obj.get("departAller"), user.address)
            existing_entry.destination_aller = replace_placeholders(day_obj.get("destinationAller"), user.address)
            existing_entry.depart_retour = replace_placeholders(day_obj.get("departRetour"), user.address)
            print("disabled", day_obj.get("disabled", False), flush=True)
            existing_entry.disabled = day_obj.get("disabled", False)
            existing_entry.destination_retour = replace_placeholders(day_obj.get("destinationRetour"), user.address)
            existing_entry.role_aller = day_obj.get("roleAller")
            existing_entry.role_retour = day_obj.get("roleRetour")
            existing_entry.validated_aller = day_obj.get("validatedAller", False)
            existing_entry.validated_retour = day_obj.get("validatedRetour", False)

        else:
            # Création
            print("disabled", day_obj.get("disabled", False), flush=True)
            new_entry = CalendarEntry(
                user_id=user_id,
                year=iso_year,
                week_number=iso_week,
                day_of_week=iso_day,
                start_hour=day_obj.get("startHour"),
                end_hour=day_obj.get("endHour"),
                depart_aller=replace_placeholders(day_obj.get("departAller"), user.address),
                destination_aller=replace_placeholders(day_obj.get("destinationAller"), user.address),
                depart_retour=replace_placeholders(day_obj.get("departRetour"), user.address),
                destination_retour=replace_placeholders(day_obj.get("destinationRetour"), user.address),
                disabled=day_obj.get("disabled", False),
                role_aller=day_obj.get("roleAller"),
                role_retour=day_obj.get("roleRetour"),
                validated_aller=day_obj.get("validatedAller", False),
                validated_retour=day_obj.get("validatedRetour", False)
            )
            db.session.add(new_entry)

    db.session.commit()
    return jsonify({"message": "Calendar ISO entries upserted"}), 200


@app.route('/propagateCalendar', methods=['POST'])
@log_call
def deploy_week():
    """
    Anciennement on dupliquait user.calendar[source_week] -> toutes les semaines.
    Maintenant qu'on n'a plus user.calendar, on lit la table CalendarEntry.
    On garde la même signature JSON, mais on change la logique.

    { "user_id": "...", "source_week": 6 }
    On copie toutes les entrées de la semaine 6 vers les semaines 1..52,
    en évitant les doublons (check de non-duplication).
    Endpoint: /propagateCalendar
    Méthode: POST

    Description:
        Duplication de la semaine source (spécifiée par "source_week") dans la table CalendarEntry
        pour toutes les semaines (1 à 52). Avant création d'une nouvelle entrée, on vérifie qu'il n'existe
        pas déjà une entrée pour la même combinaison (user_id, year, week_number, day_of_week) pour éviter la duplication.

    Entrée (JSON):
        - user_id (str)
        - source_week (int)

    Sortie (JSON):
        Un message indiquant le nombre d'entrées créées.
    """
    data = request.get_json()
    user_id = data.get("user_id")
    ref_week_number = data.get("source_week")

    if not user_id or ref_week_number is None:
        return jsonify({"error": "Missing user_id or week_number"}), 400

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Récupérer toutes les entrées de la semaine source
    ref_entries = CalendarEntry.query.filter_by(user_id=user_id, week_number=ref_week_number).all()
    if not ref_entries:
        return jsonify({"error": f"No data found for source_week {ref_week_number}"}), 400

    count_created = 0
    # Copier pour semaines 1..52
    for w_num in range(1, 53):
        for ref_e in ref_entries:
            # Vérifier s'il existe déjà une entrée pour (user_id, year, w_num, day_of_week)
            existing_entry = CalendarEntry.query.filter_by(
                user_id=user_id,
                year=ref_e.year,
                week_number=w_num,
                day_of_week=ref_e.day_of_week
            ).first()

            if existing_entry:
                continue

            # Créer une nouvelle entrée
            e = CalendarEntry(
                user_id=user_id,
                year=ref_e.year,
                week_number=w_num,
                day_of_week=ref_e.day_of_week,
                start_hour=ref_e.start_hour,
                end_hour=ref_e.end_hour,
                depart_aller=ref_e.depart_aller,
                destination_aller=ref_e.destination_aller,
                depart_retour=ref_e.depart_retour,
                destination_retour=ref_e.destination_retour,
                disabled=ref_e.disabled,
                role_aller=ref_e.role_aller,
                role_retour=ref_e.role_retour,
                validated_aller=ref_e.validated_aller,
                validated_retour=ref_e.validated_retour
            )
            db.session.add(e)
            count_created += 1

    db.session.commit()

    return jsonify({
        "message": f"Week {ref_week_number} deployed to all weeks (1..52)",
        "new_calendar_size": count_created
    }), 200


@app.route('/getCal/<string:user_id>', methods=['GET'])
@log_call
def get_calendar(user_id):
    """
    Endpoint: /getCal/<user_id>
    Méthode: GET

    Description:
        Récupère les entrées de calendrier pour un utilisateur donné et une semaine spécifiée (via le paramètre 'indexWeek')
        et reconstruit un objet JSON au format :
        {
          "weekNumber": <indexWeek>,
          "days": [
             {
               "date": "<ISO8601>",  # reconstitué à partir de year, week_number, day_of_week
               "startHour": <int>,
               "endHour": <int>,
               "departAller": <str>,
               "destinationAller": <str>,
               "departRetour": <str>,
               "destinationRetour": <str>,
               "disabled": <bool>,
               "roleAller": <str>,
               "roleRetour": <str>,
               "validatedAller": <bool>,
               "validatedRetour": <bool>
             },
             ...
          ]
        }

    Entrée (query parameter):
        - indexWeek (int)

    Sortie (JSON):
        L'objet calendrier pour la semaine spécifiée, ou null si aucune donnée.
    """
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    index_week_str = request.args.get('indexWeek', default=None, type=str)
    if not index_week_str:
        return jsonify({'error': 'Missing "indexWeek" query parameter'}), 400

    try:
        index_week = int(index_week_str)
    except ValueError:
        return jsonify({'error': '"indexWeek" must be an integer'}), 400

    entries = CalendarEntry.query.filter_by(user_id=user_id, week_number=index_week).all()
    if not entries:
        print(f"No data found for week {index_week}")
        return jsonify({'calendar': None}), 200

    days_list = []
    import datetime
    for e in entries:
        try:
            # Reconstruire la date à partir de (year, week_number, day_of_week) en tenant compte de votre logique
            # Ici on utilise la fonction local_midnight_to_utc_iso qui devrait renvoyer une date ISO (ex: "2025-03-30T22:00:00Z")
            date_str = local_midnight_to_utc_iso(e.year, e.week_number, e.day_of_week)
        except ValueError:
            date_str = None

        print("disabled", e.disabled, flush=True)
        days_list.append({
            "date": date_str,
            "startHour": e.start_hour,
            "endHour": e.end_hour,
            "departAller": e.depart_aller,
            "destinationAller": e.destination_aller,
            "departRetour": e.depart_retour,
            "destinationRetour": e.destination_retour,
            "disabled": e.disabled,
            "roleAller": e.role_aller,
            "roleRetour": e.role_retour,
            "validatedAller": e.validated_aller,
            "validatedRetour": e.validated_retour
        })

    requested_week = {
        "weekNumber": index_week,
        "days": days_list
    }
    return jsonify({'calendar': requested_week}), 200


@app.route('/request_ride', methods=['POST'])
@log_call
def request_ride():
    """
    Endpoint: /request_ride
    Méthode: POST

    Description:
        Crée ou met à jour une demande de trajet (RideRequest) pour un utilisateur pour un jour donné.
        Si une demande existe déjà pour ce jour, elle est mise à jour.
        Les informations (adresse de départ, destination, horaires) sont obtenues depuis CalendarEntry et transformées via replace_placeholders.

    Entrée (JSON):
        - user_id (str)
        - day (str): date au format "YYYY-MM-DD"
        - timeSlot (str): "morning" ou "evening"

    Sortie (JSON):
        Informations sur la demande de trajet créée ou mise à jour.
    """
    data = request.get_json()
    user_id = data.get('user_id')
    day_str = data.get('day')  # ex. "2025-02-03"
    time_slot = data.get('timeSlot')  # "morning" ou "evening"

    if not user_id or not day_str:
        return jsonify({"error": "Missing user_id or day"}), 400

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    iso_year, iso_week, iso_day = convert_iso_string_to_calendar_slots(day_str)
    entry = CalendarEntry.query.filter_by(
        user_id=user_id,
        year=iso_year,
        week_number=iso_week,
        day_of_week=iso_day
    ).first()
    if not entry:
        return jsonify({"error": f"No calendar entry found for day {day_str}"}), 400

    if not time_slot:
        time_slot = "morning"

    start_hour = entry.start_hour or 8
    end_hour = entry.end_hour or 18

    if time_slot == "morning":
        departure_address = replace_placeholders(entry.depart_aller, user_address=user.address)
        destination_address = replace_placeholders(entry.destination_aller, user_address=user.address)
        entry.validated_aller = True
    else:
        departure_address = replace_placeholders(entry.depart_retour, user_address=user.address)
        destination_address = replace_placeholders(entry.destination_retour, user_address=user.address)
        entry.validated_retour = True

    lat, lon = geocode_address(departure_address)
    if not lat or not lon:
        return jsonify({'error': 'Unable to geocode departure address'}), 400

    existing_request = RideRequest.query.filter_by(user_id=user_id, day=day_str,timeslot=time_slot).first()

    if existing_request:
        # Mise à jour de la demande existante
        existing_request.address = departure_address
        existing_request.destination = destination_address
        existing_request.lat = lat
        existing_request.lon = lon
        existing_request.timeslot = time_slot
        existing_request.start_hour = start_hour
        existing_request.end_hour = end_hour
        db.session.commit()

        return jsonify({
            "message": "Ride request updated from calendar data",
            "ride_request_id": existing_request.id,
            "departure": departure_address,
            "destination": destination_address,
            "start_hour": start_hour,
            "end_hour": end_hour
        }), 200
    else:
        # Création d'une nouvelle demande
        new_request = RideRequest(
            user_id=user_id,
            day=day_str,
            address=departure_address,
            destination=destination_address,
            lat=lat,
            lon=lon,
            timeslot=time_slot,
            start_hour=start_hour,
            end_hour=end_hour
        )
        db.session.add(new_request)
        db.session.commit()

        return jsonify({
            "message": "Ride request created from calendar data",
            "ride_request_id": new_request.id,
            "departure": departure_address,
            "destination": destination_address,
            "start_hour": start_hour,
            "end_hour": end_hour
        }), 200
####################################################################################################################################
    # ENDPOINTS POUR LA RECHERCHE DE MATCHS
#####################################################################################################################################
@app.route('/find_matches', methods=['POST'])
@log_call
def find_matches():
    """
    Endpoint: /find_matches
    Méthode: POST

    Description:
        Recherche tous les utilisateurs(conducteurs et passagers) qui ont un trajet similaire.

    Entrée (JSON):
        - user_id (str): L'ID de l'utilisateur qui effectue la recherche.
        - day (str): Date au format "YYYY-MM-DD".
        - time_slot (str): "morning" ou "evening" (optionnel, défaut "morning").

    Sortie (JSON): 
        Une liste des utilisateurs correspondants avec leurs informations de trajet.

    """

    print("Received JSON data:", request.get_json(), flush=True)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    person_id = data.get('user_id')
    day_str = data.get('day')
    time_slot = data.get('time_slot', 'morning')

    if not person_id or not day_str:
        return jsonify({"error": "Missing required parameters ('user_id', 'day')"}), 400

    person = User.query.filter_by(id=person_id).first()
    if not person:
        return jsonify({"error": "Person not found"}), 404
    
    iso_year, iso_week, iso_day = convert_iso_string_to_calendar_slots(day_str)
    entry = CalendarEntry.query.filter_by(
        user_id=person_id,
        year=iso_year,
        week_number=iso_week,
        day_of_week=iso_day
    ).first()

    if not entry:
        print("No calendar data found for that day", flush=True)
        return jsonify({"possible_matches": []}), 200
    
    person_start_hour = entry.start_hour
    person_end_hour = entry.end_hour
    if person_start_hour is None or person_end_hour is None:
        print("Person's start/end hours not found in calendar", flush=True)
        return jsonify({"possible_matches": []}), 200

    if time_slot.lower() == "morning":
        person_destination = replace_placeholders(entry.destination_aller, person.address)
        person_departure = replace_placeholders(entry.depart_aller, person.address)
        person_time = person_start_hour
    else:
        person_destination = replace_placeholders(entry.destination_retour, person.address)
        person_departure = replace_placeholders(entry.depart_retour, person.address)
        person_time = person_end_hour

    person_coords = geocode_address(person_departure)
    if not person_coords:
        return jsonify({"error": "Driver's start address invalid"}), 400

    dest_coords = geocode_address(person_destination)
    if not dest_coords:
        return jsonify({"error": "Driver's destination invalid"}), 400
    

    entries = CalendarEntry.query.filter_by(
    year=iso_year,
    week_number=iso_week,
    day_of_week=iso_day
    ).all()

    potential_matches = []

    for entry in entries:
        if entry.disabled:
            continue

        user = User.query.filter_by(id=entry.user_id).first()

        if time_slot == "morning":
            departure = replace_placeholders(entry.depart_aller, user.address)
            destination = replace_placeholders(entry.destination_aller, user.address)
            time = entry.start_hour
        else:
            departure = replace_placeholders(entry.depart_retour, user.address)
            destination = replace_placeholders(entry.destination_retour, user.address)
            time = entry.end_hour

        if not time or abs(person_time - time) > 0.5:
            continue

        if time_slot == "morning" and destination != person_destination:
            continue
        if time_slot == "evening" and departure != person_departure:
            continue

        # Ajout du match
        potential_matches.append({
            "user_id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": "conducteur" if user.is_driver else "passager",
            "departure": departure,
            "destination": destination,
            "hour": time
    })

    return jsonify({"possible_passengers": potential_matches}), 200
    
#####################################################################################################################################

@app.route('/find_passengers', methods=['POST'])
@log_call
def find_passengers():
    """
    Endpoint: /find_passengers
    Méthode: POST

    Description:
        Recherche des demandes de trajet (RideRequest) potentielles correspondant aux critères d'un conducteur.
        Compare l'heure et les adresses (départ/destination) dans le calendrier des conducteurs et passagers.

    Entrée (JSON):
        - user_id (str): l'ID du conducteur
        - day (str): date ("YYYY-MM-DD")
        - time_slot (str): "morning" ou "evening" (optionnel, défaut "morning")

    Sortie (JSON):
        Une liste de demandes potentielles avec des informations sur le passager et les itinéraires.
    """
    print("Received JSON data:", request.get_json(), flush=True)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    driver_id = data.get('user_id')
    day_str = data.get('day')
    time_slot = data.get('time_slot', 'morning')

    if not driver_id or not day_str:
        return jsonify({"error": "Missing required parameters ('driver_id', 'day')"}), 400

    driver = User.query.filter_by(id=driver_id).first()
    if not driver:
        return jsonify({"error": "Driver not found"}), 404

    iso_year, iso_week, iso_day = convert_iso_string_to_calendar_slots(day_str)
    entry = CalendarEntry.query.filter_by(
        user_id=driver_id,
        year=iso_year,
        week_number=iso_week,
        day_of_week=iso_day
    ).first()
    if not entry:
        print("No calendar data found for that day", flush=True)
        return jsonify({"possible_passengers": []}), 200

    driver_start_hour = entry.start_hour
    driver_end_hour = entry.end_hour
    if driver_start_hour is None or driver_end_hour is None:
        print("Driver's start/end hours not found in calendar", flush=True)
        return jsonify({"possible_passengers": []}), 200

    if time_slot.lower() == "morning":
        driver_destination = replace_placeholders(entry.destination_aller, driver.address)
        driver_departure = replace_placeholders(entry.depart_aller, driver.address)
        driver_time = driver_start_hour
    else:
        driver_destination = replace_placeholders(entry.destination_retour, driver.address)
        driver_departure = replace_placeholders(entry.depart_retour, driver.address)
        driver_time = driver_end_hour

    driver_coords = geocode_address(driver_departure)
    if not driver_coords:
        return jsonify({"error": "Driver's start address invalid"}), 400

    dest_coords = geocode_address(driver_destination)
    if not dest_coords:
        return jsonify({"error": "Driver's destination invalid"}), 400

    ride_requests = RideRequest.query.filter_by(day=day_str, matched_driver_id=None).all()

    time_tolerance = 0.5  # ±30 minutes
    possible_passengers = []

    for request_obj in ride_requests:
        passenger_user = User.query.filter_by(id=request_obj.user_id).first()
        if not passenger_user:
            continue
        if request_obj.timeslot != time_slot:
            continue
        passenger_entry = CalendarEntry.query.filter_by(
            user_id=passenger_user.id,
            year=iso_year,
            week_number=iso_week,
            day_of_week=iso_day
        ).first()
        if not passenger_entry:

        # Selon morning/evening, on va chercher l'adresse de départ/destination et l'heure
            continue

        if passenger_entry.disabled:
            continue
        if time_slot.lower() == "morning":
            passenger_address = replace_placeholders(passenger_entry.depart_aller, passenger_user.address)
            passenger_destination = replace_placeholders(passenger_entry.destination_aller, passenger_user.address)
            passenger_time = passenger_entry.start_hour
            if passenger_destination != driver_destination:
                continue
        else:
            passenger_address = replace_placeholders(passenger_entry.depart_retour, passenger_user.address)
            passenger_destination = replace_placeholders(passenger_entry.destination_retour, passenger_user.address)
            passenger_time = passenger_entry.end_hour
            if passenger_address != driver_departure:
                continue

        if passenger_time is None:
            continue

        if abs(driver_time - passenger_time) > time_tolerance:
            continue

        passenger_coords = geocode_address(passenger_address)
        if not passenger_coords:
            continue

        passenger_dest_coords = geocode_address(passenger_destination)
        if not passenger_dest_coords:
            continue

        route_to_passenger = get_route(driver_coords, passenger_coords, f"Driver->Passenger {request_obj.id}")
        if not route_to_passenger:
            continue

        route_to_destination = get_route(passenger_coords, passenger_dest_coords, "Passenger->Destination")
        if not route_to_destination:
            continue

        total_duration = route_to_passenger["duration"] + route_to_destination["duration"]
        normal_route = get_route(driver_coords, dest_coords, "Driver->Destination")

        if total_duration <= 120:
            possible_passengers.append({
                "ride_request_id": request_obj.id,
                "passenger_id": passenger_user.id,
                "first_name": passenger_user.first_name,
                "last_name": passenger_user.last_name,
                "passenger_address": passenger_address,
                "passenger_destination": passenger_destination,
                "day": request_obj.day,
                "driver_destination": driver_destination,
                "passenger_time": passenger_time,
                "driver_time": driver_time,
                "passengers_duration": total_duration,
                "normal_duration": normal_route["duration"] if normal_route else None,
                "routes": {
                    "driver_to_passenger": {
                        "duration": route_to_passenger["duration"],
                        "distance": route_to_passenger["distance"],
                        "geometry": route_to_passenger["geometry"]
                    },
                    "passenger_to_destination": {
                        "duration": route_to_destination["duration"],
                        "distance": route_to_destination["distance"],
                        "geometry": route_to_destination["geometry"]
                    }
                }
            })


    return jsonify({"possible_passengers": possible_passengers}), 200


@app.route('/offerPassenger', methods=['POST'])
@log_call
def offer_passenger():
    """
    Endpoint: /offerPassenger
    Méthode: POST

    Description:
        Permet à un conducteur d'offrir un trajet à une demande de trajet (RideRequest) existante.
        Vérifie que le conducteur n'offre pas un trajet à lui-même, envoie un email de notification au passager,
        puis crée une entrée dans DriverOffer.

    Entrée (JSON):
        - driver_id (str)
        - ride_request_id (str)
        - departure_hour (int)

    Sortie (JSON):
        Un message de succès avec l'ID de l'offre créée.
    """
    data = request.get_json()
    print("📨 Données reçues :", data)
    driver_id = data.get("driver_id")
    ride_request_id = data.get("ride_request_id")
    departure_hour = data.get("departure_hour")
    if not driver_id or not ride_request_id:
       return jsonify({"error": "Missing driver_id or ride_request_id"}), 400

    driver = User.query.filter_by(id=driver_id).first()
    if not driver or not driver.is_driver:
       return jsonify({"error": "Invalid driver"}), 400

    ride_request = RideRequest.query.filter_by(id=ride_request_id).first()
    if not ride_request:
        return jsonify({"error": "Ride request not found"}), 404

    if ride_request.user_id == driver_id:
        return jsonify({"error": "Cannot offer a ride to oneself"}), 400

    new_offer = DriverOffer(
        driver_id=driver_id,
        ride_request_id=ride_request_id,
        departure_hour=departure_hour,
        status="offered"
    )

    passenger = User.query.filter_by(id=ride_request.user_id).first()
    if passenger and passenger.email:
        send_offer_email(
            driver=driver,
            passenger=passenger,
            departure_hour=departure_hour,
            sender_email=SENDER_EMAIL,
            sender_password=SENDER_PASSWORD
        )

    db.session.add(new_offer)
    db.session.commit()

    return jsonify({"message": "Offer created", "driver_offer_id": new_offer.id}), 200


@app.route('/rideOffers', methods=['POST'])
@log_call
def ride_offers():
    """
    Endpoint: /rideOffers
    Méthode: POST

    Description:
        Récupère toutes les offres de trajet (DriverOffer) associées à une demande de trajet (RideRequest) donnée.

    Entrée (JSON):
        - ride_request_id (str)

    Sortie (JSON):
        Une liste d'offres comprenant l'ID de l'offre, le statut, le nom et l'adresse du conducteur.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    ride_request_id = data.get('ride_request_id')
    if not ride_request_id:
        return jsonify({"error": "Missing 'ride_request_id' in JSON"}), 400

    ride_request = RideRequest.query.filter_by(id=ride_request_id).first()
    if not ride_request:
        return jsonify({"error": "Ride request not found"}), 404

    offers = DriverOffer.query.filter_by(ride_request_id=ride_request_id).all()
    offers_data = []
    for off in offers:
        driver = User.query.filter_by(id=off.driver_id).first()
        if driver:
            offers_data.append({
                "offer_id": off.id,
                "status": off.status,
                "driver_name": f"{driver.first_name} {driver.last_name}",
                "driver_address": driver.address
            })

    return jsonify({"offers": offers_data}), 200


if __name__ == '__main__':
    with app.app_context():
        db.init_app(app)
        db.create_all()
    app.run(debug=True, port = 5005)
