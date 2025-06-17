import React, { useEffect, useState, useContext } from "react";
import L from "leaflet";
import "leaflet-routing-machine";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { useLocation } from "react-router-dom";
import "./ConducteurMap.css";
import "../leaflet-routing-machine/leaflet-routing-machine.css";
import "../leaflet/leaflet.css";
//import markerIcon from 'leaflet/dist/images/marker-icon.png';
//import markerIconRetina from 'leaflet/dist/images/marker-icon-2x.png';
import markerStartIconRetina from "../leaflet/images/marker-icon-2x-green.png";
import markerEndIconRetina from "../leaflet/images/marker-icon-2x-pink.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import startIcon from "../leaflet/images/marker-icon-green.png";
import endIcon from "../leaflet/images/marker-icon-pink.png";

const InterfaceConducteur = () => {
  const { userId } = useContext(AuthContext);
  const [passagers, setPassagers] = useState([]);
  const [map, setMap] = useState(null);
  const location = useLocation();
  const [markers, setMarkers] = useState({});
  const [conducteurMarker, setConducteurMarker] = useState(null);
  const [destinationMarker, setDestinationMarker] = useState(null);
  const [layerGroup, setLayerGroup] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);


  const startMarkerIcon = L.icon({
    iconUrl: startIcon,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [0, -41],
    shadowUrl: markerShadow,
    shadowSize: [41, 41],
    shadowAnchor: [12, 41],
    iconRetinaUrl: markerStartIconRetina,
  });

  const endMarkerIcon = L.icon({
    iconUrl: endIcon,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [0, -41],
    shadowUrl: markerShadow,
    shadowSize: [41, 41],
    shadowAnchor: [12, 41],
    iconRetinaUrl: markerEndIconRetina,
  });

  const createLetterIcon = (letter) => {
    return L.divIcon({
      className: "custom-letter-icon",
      html: `<div class="letter-marker">${letter}</div>`,
      iconSize: [30, 42],
      iconAnchor: [15, 42],
      popupAnchor: [0, -35],
    });
  };

  const { passCond, date, mornEve } = location.state || {}; // Récupérer les données passées
  //fix bug des icones
  /*delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
        iconRetinaUrl: markerIconRetina,
        iconUrl: markerIcon,
        shadowUrl: markerShadow
    });*/

  const [userData, setUserData] = useState(null);

  useEffect(() => {
    const newMap = L.map("map").setView([48.8566, 2.3522], 10);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(newMap);
    setMap(newMap);

    // Récupération des données utilisateur
    if (userId) {
      fetch(`http://localhost:5005/user/${userId}`)
        .then((response) => response.json())
        .then((data) => {
          setUserData(data);
        })
        .catch((error) =>
          console.error(
            "Erreur lors de la récupération des données utilisateur:",
            error
          )
        );
    }
    const newLayerGroup = L.layerGroup().addTo(newMap);
    setLayerGroup(newLayerGroup);
    setMap(newMap);

    return () => newMap.remove();
  }, [userId]);
  useEffect(() => {
    if (map && conducteurMarker && destinationMarker) {
      afficherTrajet(map);
    }
  }, [map, conducteurMarker, destinationMarker, markers]);

  useEffect(() => {
    Object.values(markers).forEach((marker) => {
      if (!marker._map) {
        map.removeLayer(marker);
      }
    });
  }, [markers]);

  const afficherTrajet = (map, routesData) => {
    if (!map) {
      console.error("Carte non disponible.");
      return;
    }

    const waypoints = [];

    // Ajouter le point de départ du conducteur
    if (conducteurMarker) {
      waypoints.push(conducteurMarker.getLatLng());
    }

    // Ajouter les passagers cochés comme waypoints intermédiaires
    const passagersCoches = Object.values(markers).map((marker) =>
      marker.getLatLng()
    );
    waypoints.push(...passagersCoches);

    // Ajouter la destination finale
    if (destinationMarker) {
      waypoints.push(destinationMarker.getLatLng());
    }

    // Vérifier s'il y a au moins un trajet conducteur → destination
    if (waypoints.length < 2) {
      console.error("Impossible d'afficher un itinéraire.");
      return;
    }

    // Supprimer l'ancien itinéraire s'il existe
    if (map.routeLayer) {
      map.removeControl(map.routeLayer);
      map.routeLayer = null;
    }

    // Ajouter l'itinéraire sur la carte
    map.routeLayer = L.Routing.control({
      waypoints,
      lineOptions: { styles: [{ color: "blue", weight: 5 }] },
      createMarker: function (i, waypoint, n) {
        if (i === 0)
          return L.marker(waypoint.latLng, { icon: startMarkerIcon }).bindPopup(
            "Départ Conducteur"
          );
        if (i === n - 1)
          return L.marker(waypoint.latLng, { icon: endMarkerIcon }).bindPopup(
            "Destination Finale"
          );

        // Convertir l'index en lettre (A, B, C, ...)
        const letter = String.fromCharCode(65 + i - 1); // i-1 car 0 = départ
        const letterIcon = createLetterIcon(letter);
        return L.marker(waypoint.latLng, { icon: letterIcon }).bindPopup(
          `Passager ${letter}`
        );
      },
      routeWhileDragging: false,
      draggableWaypoints: false,
      addWaypoints: false,
      autoRoute: true,
    }).addTo(map);
    document.querySelector(".leaflet-routing-container")?.remove();
  };

  const fetchPassagers = async () => {
    if (!userId || !map) return;

    setIsLoading(true); // Début

    try {
      const response = await fetch(`http://localhost:5005/find_passengers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, timeSlot: mornEve, day: date }),
      });

      const data = await response.json();
      console.log("Passagers récupérés :", data);

      if (!data.possible_passengers || data.possible_passengers.length === 0) {
        console.log("Aucun passager trouvé.");
        return;
      }

      setPassagers(data.possible_passengers);

      const firstPassenger = data.possible_passengers[0];
      if (!firstPassenger?.routes?.driver_to_passenger) {
        console.error("firstPassenger ou ses routes sont invalides.");
        return;
      }

      const driverCoords =
        firstPassenger.routes.driver_to_passenger.geometry[0];
      const destinationCoords =
        firstPassenger.routes.passenger_to_destination.geometry[1];

      if (driverCoords && !conducteurMarker) {
        const driverMarker = L.marker([driverCoords[0], driverCoords[1]], {
          icon: startMarkerIcon,
        })
          .addTo(map)
          .bindPopup("Conducteur");
        setConducteurMarker(driverMarker);
      }

      if (destinationCoords && !destinationMarker) {
        const destMarker = L.marker(
          [destinationCoords[0], destinationCoords[1]],
          {
            icon: endMarkerIcon,
          }
        )
          .addTo(map)
          .bindPopup("Destination Finale");
        setDestinationMarker(destMarker);
      }
    } catch (error) {
      console.error("Erreur lors de la récupération des passagers:", error);
    } finally {
      setIsLoading(false); // ✅ FIN NORMALE OU AVEC ERREUR
    }
  };

  const toggleMarker = (passager) => {
    if (!layerGroup || !map) return;

    const passengerId = passager.passenger_id;
    const passengerCoords = passager.routes.driver_to_passenger.geometry[1];

    setMarkers((prevMarkers) => {
      const newMarkers = { ...prevMarkers };

      if (newMarkers[passengerId]) {
        console.log(`🗑 Suppression du marqueur du passager ${passengerId}`);
        layerGroup.removeLayer(newMarkers[passengerId]); // Suppression du marqueur
        delete newMarkers[passengerId];
      } else {
        console.log(`➕ Ajout du marqueur du passager ${passengerId}`);

        const letter = String.fromCharCode(
          65 + Object.keys(prevMarkers).length
        ); // ou une autre logique
        const marker = L.marker([passengerCoords[0], passengerCoords[1]], {
          icon: createLetterIcon(letter),
        }).bindPopup(
          `${passager.first_name} ${passager.last_name} - ${passager.address}`
        );

        layerGroup.addLayer(marker); // Ajout dans le LayerGroup
        newMarkers[passengerId] = marker;
        // Ajuster la vue pour englober tous les marqueurs et le trajet
        const allMarkers = Object.values(newMarkers).map((marker) =>
          marker.getLatLng()
        );

        // Ajouter le conducteur et la destination s'ils existent
        if (conducteurMarker) allMarkers.push(conducteurMarker.getLatLng());
        if (destinationMarker) allMarkers.push(destinationMarker.getLatLng());

        if (allMarkers.length > 1) {
          const bounds = L.latLngBounds(allMarkers);
          map.fitBounds(bounds, { padding: [50, 50] }); // Ajuster le zoom
        }
      }

      return newMarkers; // Met à jour l'état des marqueurs
    });
  };

  const handleSendOffers = async () => {
    if (!userId) {
      console.error("Utilisateur non identifié.");
      return;
    }

    const selectedPassengers = Object.keys(markers);
    if (selectedPassengers.length === 0) {
      alert("Aucun passager sélectionné !");
      return;
    }

    try {
      for (const passengerId of selectedPassengers) {
        const passenger = passagers.find((p) => p.passenger_id === passengerId);
        if (!passenger) continue;

        const response = await fetch("http://localhost:5005/offerPassenger", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            driver_id: userId,
            ride_request_id: passenger.ride_request_id,
          }),
        });

        const data = await response.json();
        if (!response.ok) {
          console.error(`Erreur pour le passager ${passengerId}:`, data.error);
        } else {
          console.log(`Offre envoyée au passager ${passengerId}.`);
        }
      }
      alert("Les utliisateurs sélectionnés ont été contactés.");
    } catch (error) {
      console.error("Erreur lors de l'envoi des offres :", error);
    } finally {
      setIsLoading(false);
    }
  };
  useEffect(() => {
    if (map && userId && layerGroup) {
      fetchPassagers();
    }
  }, [map, userId, layerGroup]);

  const formatDuration = (minutes) => {
    if (!minutes) return "";
    /*arrondir minutes*/
    minutes = Math.round(minutes);
    return `+${minutes} min`;
  };

  return (
    <div
      className="conducteur-map-container"
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        width: "100%",
      }}
    >
      {/* Date centrée au-dessus */}
      <h2 style={{ textAlign: "center", marginBottom: "20px" }}>
        Trajet du{" "}
        {new Date(date).toLocaleDateString("fr-FR", {
          weekday: "long",
          day: "numeric",
          month: "long",
          year: "numeric",
        })}
      </h2>

      {/* Conteneur avec carte à gauche et passagers à droite */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          width: "100%",
          gap: "20px",
        }}
      >
        {/* Carte à gauche */}
        <div id="map" style={{ width: "70%", height: "750px" }}></div>

        {/* Liste des passagers à droite */}
        <div
          id="options-passagers"
          style={{
            width: "30%",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <h2>Passagers Disponibles</h2>
          {date && (
            <p
              style={{
                marginBottom: "10px",
                padding: "10px",
                borderRadius: "5px",
                fontWeight: "bold",
                color: "white",
                backgroundColor: "#927e6e",
              }}
            >
              Pour le{" "}
              {new Date(date).toLocaleDateString("fr-FR", {
                weekday: "long",
                day: "numeric",
                month: "long",
                year: "numeric",
              })}
            </p>
          )}

          <button onClick={fetchPassagers}>Charger les passagers</button>
          <div
            id="passagers-list"
            style={{
              marginTop: "10px",
              width: "100%",
              textAlign: "center",
              color: "white",
            }}
          >
            {isLoading ? (
              <div className="loader"> </div>
            ) : passagers.length > 0 ? (
              passagers.map((passager) => (
                <div
                  key={passager.passenger_id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    width: "80%",
                    color: "white",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "flex-start",
                    }}
                  >
                    <p style={{ margin: 0 }}>
                      {passager.first_name} {passager.last_name}
                    </p>
                    <span style={{ fontSize: "0.9em", color: "#f5deb3" }}>
                      {formatDuration(
                        (passager.passengers_duration - passager.normal_duration)
                      )}
                    </span>
                  </div>
                  <input
                    type="checkbox"
                    onChange={() => toggleMarker(passager)}
                  />
                </div>
              ))
            ) : (
              <p>Aucun passager trouvé.</p>
            )}
          </div>
        </div>
      </div>
      <button
        onClick={handleSendOffers}
        style={{
          marginTop: "20px",
          padding: "10px",
          backgroundColor: "blue",
          color: "white",
          border: "none",
          cursor: "pointer",
        }}
      >
        Envoyer les offres aux passagers sélectionnés
      </button>
    </div>
  );
};

function ConducteurMap() {
  return (
    <div>
      <InterfaceConducteur />
    </div>
  );
}

export default ConducteurMap;
