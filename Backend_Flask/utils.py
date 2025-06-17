"""
Module de fonctions utilitaires pour la gestion du géocodage, du calcul d'itinéraire,
et du remplacement de placeholders dans le projet.
"""

from models import AddressCache, db
import polyline
import requests 
import logging

def geocode_address(address):
    """
    Effectue le géocodage d'une adresse en utilisant l'API adresse.data.gouv.fr, 
    avec mise en cache pour accélérer les calculs.

    Cette fonction vérifie d'abord si l'adresse est présente dans le cache (table AddressCache).
    Si c'est le cas, les coordonnées mises en cache sont retournées.
    Sinon, une requête est effectuée vers l'API, les coordonnées (latitude et longitude)
    sont extraites, arrondies à 6 décimales, enregistrées dans le cache, puis retournées.

    :param address: (str) Adresse à géocoder.
    :return: (tuple) (lat, lon) si le géocodage est réussi, sinon (None, None).
    """
    # Vérifier le cache
    cached_entry = AddressCache.query.filter_by(address=address).first()
    if cached_entry:
        return (cached_entry.lat, cached_entry.lon)
    
    # Si l'adresse n'est pas en cache, appeler l'API
    url = f'https://api-adresse.data.gouv.fr/search/?q={address}&limit=1'
    response = requests.get(url)
    
    # Vérifier que la réponse HTTP est 200
    if response.status_code == 200:
        data = response.json()
        if data and "features" in data and len(data["features"]) > 0:
            coords = data["features"][0]["geometry"]["coordinates"]
            lat = coords[1]
            lon = coords[0]
            
            # Vérifier que les coordonnées sont présentes
            if lat is not None and lon is not None:
                try:
                    lat = float(lat)
                    lon = float(lon)
                    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                        lat = round(lat, 6)
                        lon = round(lon, 6)
                        # Enregistrer les coordonnées dans le cache
                        new_entry = AddressCache(address=address, lat=lat, lon=lon)
                        db.session.add(new_entry)
                        db.session.commit()
                        return lat, lon
                    else:
                        raise ValueError("Les coordonnées ne sont pas valides")
                except ValueError as e:
                    print(f"Erreur de conversion des coordonnées : {e}")
                    return None, None
            else:
                print("Les coordonnées de géolocalisation sont manquantes.")
                return None, None
        else:
            print("Aucune donnée retournée pour l'adresse.")
            return None, None
    else:
        print(f"Erreur lors de la récupération des données : {response.status_code}")
        return None, None


def get_route(start_coords, end_coords, label):
    """
    Calcule un itinéraire entre deux points en utilisant le service OSRM.

    Cette fonction envoie une requête à l'API OSRM pour obtenir l'itinéraire
    entre les coordonnées de départ et d'arrivée. Elle renvoie un dictionnaire contenant :
    - Le label donné,
    - La distance (en km),
    - La durée (en minutes),
    - Une géométrie simplifiée sous forme de liste de coordonnées.

    :param start_coords: (tuple) Coordonnées de départ sous la forme (lat, lon).
    :param end_coords: (tuple) Coordonnées d'arrivée sous la forme (lat, lon).
    :param label: (str) Label pour identifier cet itinéraire.
    :return: (dict) Dictionnaire avec "label", "distance", "duration" et "geometry",
             ou None si l'itinéraire n'est pas trouvé.
    """
    response = requests.get(
        f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}",
        params={"overview": "full"}
    )
    data = response.json()
    if "routes" in data and data["routes"]:
        route = data["routes"][0]
        # Ici, on construit une géométrie simplifiée contenant juste les coordonnées de départ et d'arrivée.
        coords_list = [start_coords, end_coords]
        return {
            "label": label,
            "distance": route["distance"] / 1000,  # Convertir en km
            "duration": route["duration"] / 60,    # Convertir en minutes
            "geometry": coords_list
        }
    return None


def replace_placeholders(obj, user_address):
    """
    Parcourt récursivement 'obj' (peut être un dict, une liste ou une chaîne)
    et remplace certains mots-clés par des adresses complètes.

    Notamment, si le mot "Maison" est rencontré, il sera remplacé par 'user_address'.
    D'autres remplacements prédéfinis sont appliqués (Villetaneuse, Bobigny, Saint-Denis).

    :param obj: (dict, list, str, ou autre) Objet à traiter.
    :param user_address: (str) Adresse de l'utilisateur à utiliser pour le remplacement.
    :return: L'objet mis à jour avec les remplacements effectués.
    """
    replacements = {
        "Villetaneuse": "99 Av. Jean Baptiste Clément, 93430 Villetaneuse",
        "Bobigny": "74 Rue Marcel Cachin, 93000 Bobigny",
        "Saint-Denis": "Place du 8 Mai 1945, 93200, Saint-Denis",
        "Maison": user_address  # Remplace "Maison" par l'adresse de l'utilisateur
    }

    if isinstance(obj, dict):
        # Traiter récursivement chaque clé/valeur
        for key, value in obj.items():
            obj[key] = replace_placeholders(value, user_address)
        return obj

    elif isinstance(obj, list):
        # Traiter récursivement chaque élément de la liste
        for i in range(len(obj)):
            obj[i] = replace_placeholders(obj[i], user_address)
        return obj

    elif isinstance(obj, str):
        # Effectuer les remplacements pour chaque mot-clé
        for placeholder, full_address in replacements.items():
            obj = obj.replace(placeholder, full_address)
        return obj

    else:
        # Pour les types int, float, bool ou None, retourner directement l'objet
        return obj
