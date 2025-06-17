"""
Module de définition des modèles de base de données et des fonctions utilitaires
pour la gestion du calendrier et des requêtes de covoiturage.
"""

from flask_sqlalchemy import SQLAlchemy
import uuid
import datetime
from dateutil.parser import parse
import pytz

# Initialisation de l'instance SQLAlchemy
db = SQLAlchemy()


class AddressCache(db.Model):
    """
    Modèle représentant le cache d'adresses géocodées pour éviter de répéter des requêtes de géocodage.
    
    Attributs :
        - id (int) : Clé primaire, autoincrémentée.
        - address (str) : Adresse unique.
        - lat (float) : Latitude.
        - lon (float) : Longitude.
    """
    __tablename__ = "address_cache"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.String(255), unique=True, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<AddressCache {self.address} lat={self.lat} lon={self.lon}>"


class User(db.Model):
    """
    Modèle représentant un utilisateur.

    Attributs :
        - id (str) : Identifiant UUID de l'utilisateur.
        - email (str) : Adresse e-mail unique.
        - first_name (str) : Prénom.
        - last_name (str) : Nom.
        - password (str) : Mot de passe (en clair ou haché).
        - address (str) : Adresse de l'utilisateur.
        - is_driver (bool) : Indique si l'utilisateur est conducteur.
        - calendar (str) : Texte de calendrier (optionnel).
    """
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Plain-text or hashed
    address = db.Column(db.String(200), nullable=False)
    is_driver = db.Column(db.Boolean, default=False)
    calendar = db.Column(db.Text, nullable=True)


class RideRequest(db.Model):
    """
    Modèle représentant une demande de covoiturage.

    Attributs :
        - id (str) : Identifiant UUID de la demande.
        - user_id (str) : Référence à l'utilisateur (passager).
        - day (str) : Date de la demande (ex: "2025-02-03").
        - address (str) : Adresse de départ.
        - destination (str) : Adresse de destination.
        - lat (float) : Latitude de l'adresse de départ.
        - lon (float) : Longitude de l'adresse de départ.
        - start_hour (int) : Heure de début (ex: 9).
        - end_hour (int) : Heure de fin (ex: 17).
        - matched_driver_id (str) : Identifiant du conducteur ayant accepté la demande (optionnel).
    """
    __tablename__ = "ride_request"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    day = db.Column(db.String(20), nullable=False)  # e.g. "2025-02-03" or "monday"
    address = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    lat = db.Column(db.Float, nullable=True)
    lon = db.Column(db.Float, nullable=True)
    start_hour = db.Column(db.Integer, nullable=False)
    end_hour = db.Column(db.Integer, nullable=False)
    timeslot = db.Column(db.String(50), nullable=True)  # e.g. "9-17"
    matched_driver_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f"<RideRequest {self.id} day={self.day} user={self.user_id}>"


class DriverOffer(db.Model):
    """
    Modèle représentant une offre de covoiturage proposée par un conducteur
    en réponse à une demande de trajet.

    Attributs :
        - id (str) : Identifiant UUID de l'offre.
        - driver_id (str) : Référence à l'utilisateur conducteur.
        - ride_request_id (str) : Référence à la demande de trajet.
        - status (str) : Statut de l'offre (ex: "offered", "accepted", "declined").
        - departure_hour (int) : Heure de départ proposée.
    """
    __tablename__ = "driver_offer"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    driver_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    ride_request_id = db.Column(db.String(36), db.ForeignKey('ride_request.id'), nullable=False)
    status = db.Column(db.String(20), default="offered")
    departure_hour = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<DriverOffer {self.id} driver={self.driver_id} request={self.ride_request_id} status={self.status}>"


class CalendarEntry(db.Model):
    """
    Modèle représentant une entrée dans le calendrier d'un utilisateur.

    Chaque entrée correspond à un jour (défini par l'année, le numéro de semaine ISO et le jour ISO)
    et contient des informations sur les horaires, adresses de départ/destination, et le rôle (conducteur ou passager).

    Attributs :
        - id (str) : Identifiant UUID de l'entrée.
        - user_id (str) : Référence à l'utilisateur.
        - year (int) : Année (ex: 2025).
        - week_number (int) : Numéro de semaine ISO (1..53).
        - day_of_week (int) : Jour de la semaine ISO (1 = lundi, 7 = dimanche).
        - start_hour (int) : Heure de début (optionnel).
        - end_hour (int) : Heure de fin (optionnel).
        - depart_aller (str) : Adresse de départ pour l'aller.
        - destination_aller (str) : Adresse de destination pour l'aller.
        - depart_retour (str) : Adresse de départ pour le retour.
        - destination_retour (str) : Adresse de destination pour le retour.
        - disabled (bool) : Indique si l'entrée est désactivée.
        - role_aller (str) : Rôle à l'aller (par exemple, "passager" ou "conducteur").
        - role_retour (str) : Rôle au retour.
        - validated_aller (bool) : Indique si l'entrée a été validée pour l'aller.
        - validated_retour (bool) : Indique si l'entrée a été validée pour le retour.
    """
    __tablename__ = 'calendar_entry'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_hour = db.Column(db.Integer, nullable=True)
    end_hour = db.Column(db.Integer, nullable=True)
    depart_aller = db.Column(db.String(200), nullable=True)
    destination_aller = db.Column(db.String(200), nullable=True)
    depart_retour = db.Column(db.String(200), nullable=True)
    destination_retour = db.Column(db.String(200), nullable=True)
    disabled = db.Column(db.Boolean, default=False)
    role_aller = db.Column(db.String(50), nullable=True)
    role_retour = db.Column(db.String(50), nullable=True)
    validated_aller = db.Column(db.Boolean, default=False)
    validated_retour = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return (f"<CalendarEntry {self.id} user={self.user_id} "
                f"year={self.year} week={self.week_number} day={self.day_of_week}>")


def to_real_date(year, week_number, day_of_week):
    """
    Convertit les valeurs ISO (year, week_number, day_of_week) en une date réelle.

    :param year: Année (int)
    :param week_number: Numéro de semaine ISO (int)
    :param day_of_week: Jour de la semaine ISO (int, 1 = lundi, 7 = dimanche)
    :return: Date (datetime.date)
    """
    return datetime.date.fromisocalendar(year, week_number, day_of_week)


def convert_iso_string_to_calendar_slots(date_str):
    """
    Convertit une chaîne ISO8601 (ex: "2025-03-30T22:00:00Z") en un tuple (year, week_number, day_of_week)
    en interprétant l'heure donnée comme étant en UTC, puis en la convertissant en heure locale ("Europe/Paris").
    Cela permet de gérer correctement les décalages horaires et les changements d'heure (DST).

    :param date_str: Chaîne de date au format ISO8601.
    :return: Tuple (year, week_number, day_of_week)
    """
    dt_utc = parse(date_str)
    if dt_utc.tzinfo is None:
        # Si aucun offset n'est spécifié, on considère la date comme UTC
        dt_utc = dt_utc.replace(tzinfo=pytz.utc)

    local_zone = pytz.timezone("Europe/Paris")
    dt_local = dt_utc.astimezone(local_zone)
    iso_year, iso_week, iso_day = dt_local.isocalendar()
    return iso_year, iso_week, iso_day


def local_midnight_to_utc_iso(year, week, day_of_week):
    """
    Reconstruit la date correspondant à minuit local pour les paramètres donnés (year, week, day_of_week)
    en utilisant la zone "Europe/Paris", puis la convertit en heure UTC sous forme d'une chaîne ISO8601.

    Par exemple, si minuit local en "Europe/Paris" est à 00:00 et que le décalage est de +2,
    la fonction renverra une chaîne avec "T22:00:00Z" correspondant au jour précédent en UTC.

    :param year: Année (int)
    :param week: Numéro de semaine ISO (int)
    :param day_of_week: Jour de la semaine ISO (int, 1 = lundi, 7 = dimanche)
    :return: Chaîne ISO8601 (str) représentant l'heure UTC.
    """
    real_date = datetime.date.fromisocalendar(year, week, day_of_week)
    # Création d'un datetime naïf pour minuit local (00:00:00)
    naive_local_dt = datetime.datetime(real_date.year, real_date.month, real_date.day, 0, 0, 0)
    local_zone = pytz.timezone("Europe/Paris")
    local_dt = local_zone.localize(naive_local_dt, is_dst=None)
    # Conversion de l'heure locale en UTC
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt.isoformat().replace("+00:00", "Z")
