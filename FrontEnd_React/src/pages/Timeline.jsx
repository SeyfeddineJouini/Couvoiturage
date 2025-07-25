import React, { useEffect, useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import dayjs from "dayjs";
import isoWeek from "dayjs/plugin/isoWeek";
import { useNavigate, Link } from "react-router-dom";

import "./Timeline.css";

dayjs.extend(isoWeek);

function Timeline() {
  const { userId } = useContext(AuthContext);
  const [weekData, setWeekData] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  // Récupère la semaine courante + X semaines suivantes
  const fetchMultipleWeeks = async () => {
    if (!userId) return;

    try {
      const weeksToFetch = 4; // ici, la semaine courante + 3 suivantes
      const currentWeek = dayjs().isoWeek();
      let allDays = [];

      for (let i = 0; i < weeksToFetch; i++) {
        const indexWeek = currentWeek + i;

        try {
          const response = await fetch(
            `http://localhost:5005/getCal/${userId}?indexWeek=${indexWeek}`
          );

          // Si la requête est OK, on concatène les jours
          if (response.ok) {
            const data = await response.json();
            if (data?.calendar?.days) {
              allDays = allDays.concat(data.calendar.days);
            }
          } else {
            // On ignore l'erreur pour cette semaine
            console.warn(`Impossible de récupérer la semaine ${indexWeek}.`);
          }
        } catch (err) {
          // Si la requête plante, on l'ignore également
          console.warn(
            `Erreur lors de la récupération de la semaine ${indexWeek}:`,
            err
          );
        }
      }

      // On met à jour le state avec l'ensemble de tous les jours valides
      setWeekData({ days: allDays });
    } catch (err) {
      console.error("Erreur générale:", err);
      setError("Impossible de contacter le serveur.");
    }
  };

  // Charge les données une première fois au montage / quand userId change
  useEffect(() => {
    fetchMultipleWeeks();
  }, [userId]);

  // Quand on clique pour demander un trajet ou gérer ses passagers
  const handleDayClick = async (passCond, date, mornEve) => {
    if (passCond === "conducteur") {
      return navigate("/InterfaceConducteur", {
        state: { passCond, mornEve, date },
      });
    } else {
      try {
        const response = await fetch(`http://localhost:5005/request_ride`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: userId,
            timeSlot: mornEve,
            day: date,
          }),
        });
        const data = await response.json();

        if (response.ok) {
          alert("Demande de trajet envoyée !");
          // On refait un fetch pour mettre à jour l'interface
          fetchMultipleWeeks();
        } else {
          alert(`Erreur : ${data.error}`);
        }
      } catch (error) {
        console.error("Erreur lors de l'envoi des données :", error);
        alert("Impossible de sauvegarder les modifications.");
      }
    }
  };

  if (!userId) {
    return <p>Veuillez vous connecter pour voir vos trajets.</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  if (!weekData || !weekData.days) {
    return <p>Chargement des trajets...</p>;
  }
// #############################################################################################################################
                              //MES MODIFICATIONS 03 JUILLET 2025
//##############################################################################################################################

const handleViewMatches = async (date, role, timeSlot) => {
  try {
    const response = await fetch(`http://localhost:5005/find_matches`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({user_id: userId, timeSlot: timeSlot, day: date 
        
      }),
    });

    if (response.ok) {
  const data = await response.json();
  const matches = data.possible_passengers || [];

  if (matches.length === 0) {
    alert("Aucun match trouvé.");
  } else {
    const matchList = matches.map((p, index) => {
      const name = `${p.first_name} ${p.last_name}`;
      const email = p.email || "(email non fourni)";
      const from = p.passenger_address || "Adresse inconnue";
      const to = p.passenger_destination || "Destination inconnue";
      const hour = p.passenger_time || "?";
      const role = p.passenger_id ? "Passager" : "Conducteur";
      return `${index + 1}. ${name}  – ${email}\n  `;
    }).join("\n\n");

    alert(`Correspondances trouvées :\n\n${matchList}`);
  }
} else {
      const errorData = await response.json();
      alert(`Erreur : ${errorData.error}`);
    }
  } catch (error) {
    console.error("Erreur lors de la récupération des correspondances :", error);
    alert("Impossible de récupérer les correspondances.");
  }
};

//##############################################################################################################################
  return (
    <div className="timeline-container">
      <h1>Vos trajets (semaines à venir incluses)</h1>
      <h2 style={{ color: "black" }}>
        Cliquer sur un bouton vous permettra d'envoyer une demande de trajets
        aux conducteurs ou de séléctionner vos futurs passagers.
      </h2>
      <ul className="timeline-list">
        {weekData.days.filter((day) => !day.disabled).length === 0 ? (
          <>
            <h2 style={{ color: "black" }}>Aucun Trajet trouvé</h2>
            <p style={{ marginTop: "20px" }}>
              Veuillez accéder à{" "}
              <strong>
                <Link to="/calendrier">Mon emploi du temps</Link>
              </strong>{" "}
              afin de créer votre calendrier et générer des trajets.
            </p>
          </>
        ) : (
          weekData.days
            .filter((day) => !day.disabled)
            .map((day, index) => (
              <li key={index} className="timeline-day">
                <h2 className="timeline-date">
                  {dayjs(day.date).format("dddd DD/MM")}
                </h2>

                <div className="timeline-section">
                  <h3>🕗 Aller</h3>
                  <p>
                    {day.departAller} → {day.destinationAller} à {day.startHour}
                    h
                  </p>
                  <p>Rôle : {day.roleAller}</p>
                  <button
                    onClick={() =>
                      handleDayClick(day.roleAller, day.date, "morning")
                    }
                    className="btn-nav"
                    style={{
                      backgroundColor: day.validatedAller
                        ? "green"
                        : day.roleAller === "conducteur"
                        ? "rgba(43, 82, 241, 0.4)"
                        : "rgba(241, 43, 43, 0.4)",
                      pointerEvents: day.validatedAller ? "none" : "auto",
                      opacity: day.validatedAller ? 0.7 : 1,
                    }}
                  >
                    {day.roleAller === "conducteur"
                      ? "🚗 Choisir mes passagers (Aller)"
                      : "🚶‍♂️ Demander un trajet (Aller)"}
                  </button>
                  <button
                    onClick={() =>
                      handleViewMatches(day.date, day.roleAller, "morning")
                    }
                    className="btn-secondary"
                  style={{ marginLeft: "10px" }}
                  >
                  🔍 Voir les correspondances
                  </button>
                </div>

                <div className="timeline-section">
                  <h3>🌙 Retour</h3>
                  <p>
                    {day.departRetour} → {day.destinationRetour} à {day.endHour}
                    h
                  </p>
                  <p>Rôle : {day.roleRetour}</p>
                  <button
                    onClick={() =>
                      handleDayClick(day.roleRetour, day.date, "evening")
                    }
                    className="btn-nav"
                    style={{
                      backgroundColor: day.validatedRetour
                        ? "green"
                        : day.roleRetour === "conducteur"
                        ? "rgba(43, 82, 241, 0.4)"
                        : "rgba(241, 43, 43, 0.4)",
                      pointerEvents: day.validatedRetour ? "none" : "auto",
                      opacity: day.validatedRetour ? 0.7 : 1,
                    }}
                  >
                    {day.roleRetour === "conducteur"
                      ? "🚗 Choisir mes passagers (Retour)"
                      : "🚶‍♂️ Demander un trajet (Retour)"}
                  </button>
                  <button
                    onClick={() =>
                      handleViewMatches(day.date, day.roleRetour, "evening")
                    }
                    className="btn-secondary"
                  style={{ marginLeft: "10px" }}
                  >
                  🔍 Voir les correspondances
                  </button>
                </div>
              </li>
            ))
        )}
      </ul>
    </div>
  );
}

export default Timeline;
