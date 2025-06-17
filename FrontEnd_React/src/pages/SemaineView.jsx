import React, {useContext, useState, useEffect } from "react";
import { Link, useNavigate, UNSAFE_NavigationContext  } from "react-router-dom";
import ToggleSwitch from "./ToggleSwitch";
import "./SemaineView.css";
import dayjs from "dayjs";

function useWarnIfUnsavedChanges(when, message = "Des modifications non sauvegardées seront perdues. Quitter ?") {
  const navigator = useContext(UNSAFE_NavigationContext).navigator;

  useEffect(() => {
    if (!when) return;

    const push = navigator.push;

    navigator.push = (...args) => {
      if (!when) {
        push(...args);
        return;
      }

      const shouldProceed = window.confirm(message);
      if (shouldProceed) {
        navigator.push = push;
        push(...args);
      }
    };


    return () => {
      navigator.push = push;
    };
  }, [when, navigator, message]);
}

function SemaineView({ week, userId, onBack }) {
  const [showAllerInfo, setShowAllerInfo] = useState({});
  const [showRetourInfo, setShowRetourInfo] = useState({});
  const [disabledDays, setDisabledDays] = useState({});

  const [roles, setRoles] = useState(
    week.days.reduce((acc, day) => {
      const dayOfWeek = new Date(day).getDay();
      if (dayOfWeek !== 0 && dayOfWeek !== 6) {
        acc[day] = { aller: "passager", retour: "passager" };
      }
      return acc;
    }, {})
  );
  const [daysHours, setDaysHours] = useState([]);
  const [initialDaysHours, setInitialDaysHours] = useState([]);



  const navigate = useNavigate();

  useEffect(() => {
    const fetchWeekSchedule = async () => {
      try {
        const response = await fetch(
          `http://localhost:5005/getCal/${userId}?indexWeek=${week.weekNumber}`
        );
        const data = await response.json();


        if (data.calendar && data.calendar.days.length > 0) {
          setDaysHours(
            data.calendar.days.map((day) => ({
              date: day.date,
              startHour: day.startHour,
              endHour: day.endHour,
              departAller: normaliserAdresse(day.departAller),
              destinationAller: normaliserAdresse(day.destinationAller),
              departRetour: normaliserAdresse(day.departRetour),
              destinationRetour: normaliserAdresse(day.destinationRetour),
              validatedAller: false,
              validatedRetour: false,


            }))
          );
          setDisabledDays(
            data.calendar.days.reduce((acc, day) => {
              acc[day.date] = !!day.disabled;
              return acc;
            }, {})
          );


          setRoles(
            data.calendar.days.reduce((acc, day) => {
              acc[day.date] = {
                aller: day.roleAller || "passager",
                retour: day.roleRetour || "passager",
              };
              return acc;
            }, {})
          );
          setInitialDaysHours(JSON.stringify(data.calendar.days));
          setInitialRoles(
            JSON.stringify(
              data.calendar.days.reduce((acc, day) => {
                acc[day.date] = {
                  aller: day.roleAller || "passager",
                  retour: day.roleRetour || "passager",
                };
                return acc;
              }, {})
            )
          );
        } else {
          setDaysHours(getDefaultWeekSchedule());
          const defaults = getDefaultWeekSchedule();
          setInitialDaysHours(JSON.stringify(defaults));
          setInitialRoles(
            JSON.stringify(
              defaults.reduce((acc, day) => {
                acc[day.date] = {
                  aller: day.roleAller,
                  retour: day.roleRetour,
                };
                return acc;
              }, {})
            )
          );

        }
      } catch (error) {
        console.error(
          "Erreur lors de la récupération des données de la semaine :",
          error
        );
        setDaysHours(getDefaultWeekSchedule());
      }
      setInitialDaysHours(JSON.stringify(daysHours));
        setInitialRoles(JSON.stringify(roles));
    };
    fetchWeekSchedule();

  }, [week.weekNumber, userId]);
  const handleToggleDisabledDay = (date) => {
    setDisabledDays((prev) => ({
      ...prev,
      [date]: !prev[date], // Inverse l'état "désactivé" de ce jour
    }));

  };
  const handleToggleWeekDisabled = () => {
    const allDisabled = daysHours.every(day => disabledDays[day.date]);
    const updated = {};
    daysHours.forEach(day => {
      updated[day.date] = !allDisabled;
    });
    setDisabledDays(updated);
  };


  const [initialRoles, setInitialRoles] = useState({});



  const normaliserAdresse = (adresse) => {
    if (!adresse) return "Maison";
    if (adresse.includes("74 Rue Marcel Cachin, 93000 Bobigny"))
      return "Bobigny";
    if (adresse.includes("99 Av. Jean Baptiste Clément, 93430 Villetaneuse"))
      return "Villetaneuse";
    if (adresse.includes("Place du 8 Mai 1945, 93200, Saint-Denis"))
      return "Saint-Denis";
    return "Maison";
  };

  const getDefaultWeekSchedule = () => {
    return week.days
      .filter((date) => {
        const dayOfWeek = new Date(date).getDay();
        return dayOfWeek !== 0 && dayOfWeek !== 6;
      })
      .map((date) => ({
        date,
        startHour: 9,
        endHour: 17,
        departAller: "Maison",
        destinationAller: "Villetaneuse",
        departRetour: "Villetaneuse",
        destinationRetour: "Maison",
        roleAller: "passager",
        roleRetour: "passager",
        disabled: false,
        validatedAller: false,
        validatedRetour: false,
      }));
  };

  const handleSaveAndPropagate = async () => {
    await handleSaveWeek();      // Sauvegarde la semaine actuelle
    await handlePropagateSchedule(); // Propage la semaine aux autres semaines vides
  };

  const handlePropagateSchedule = async () => {
    try {
      const response = await fetch("http://localhost:5005/propagateCalendar", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          source_week: week.weekNumber,
        }),
      });

      const result = await response.json();
      if (response.ok) {
        alert("Emploi du temps propagé avec succès !");
      } else {
        alert(`Erreur : ${result.error}`);
      }
    } catch (error) {
      console.error("Erreur lors de la propagation :", error);
      alert("Impossible de propager l'emploi du temps.");
    }
  };



  const handleSaveWeek = async () => {
    try {
      const response = await fetch("http://localhost:5005/saveCal", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          calendar_changes: {
            weekNumber: week.weekNumber,
            days: daysHours.map((day) => ({
              date: day.date,
              startHour: day.startHour,
              endHour: day.endHour,
              departAller: day.departAller,
              destinationAller: day.destinationAller,
              roleAller: roles[day.date]?.aller || "passager",
              departRetour: day.departRetour,
              destinationRetour: day.destinationRetour,
              roleRetour: roles[day.date]?.retour || "passager",
              validatedAller: day.validatedAller || false,
              validatedRetour: day.validatedRetour || false,
              disabled: disabledDays[day.date] || false,


            })),
          },
        }),
      });

      const result = await response.json();
      if (response.ok) {
        alert("Modifications enregistrées avec succès !");
        setInitialDaysHours(JSON.stringify(daysHours));
        setInitialRoles(JSON.stringify(roles));
      } else {
        alert(`Erreur : ${result.error}`);
      }
    } catch (error) {
      console.error("Erreur lors de l'envoi des données :", error);
      alert("Impossible de sauvegarder les modifications.");
    }
  };

  const handleDepartAllerChange = (dayIndex, value) => {
    setDaysHours((prev) => {
      const newDaysHours = [...prev];
      newDaysHours[dayIndex].departAller = value;
      return newDaysHours;
    });
  };

  const handleDestinationAllerChange = (dayIndex, value) => {
    setDaysHours((prev) => {
      const newDaysHours = [...prev];
      newDaysHours[dayIndex].destinationAller = value;
      return newDaysHours;
    });
  };

  const handleDepartRetourChange = (dayIndex, value) => {
    setDaysHours((prev) => {
      const newDaysHours = [...prev];
      newDaysHours[dayIndex].departRetour = value;
      return newDaysHours;
    });
  };

  const handleDestinationRetourChange = (dayIndex, value) => {
    setDaysHours((prev) => {
      const newDaysHours = [...prev];
      newDaysHours[dayIndex].destinationRetour = value;
      return newDaysHours;
    });
  };

  const [dragging, setDragging] = useState(null);

  useEffect(() => {
    const handleGlobalMouseUp = () => setDragging(null);
    document.addEventListener("mouseup", handleGlobalMouseUp);
    return () => document.removeEventListener("mouseup", handleGlobalMouseUp);
  }, []);

  const handleMouseDownOnHandle = (dayIndex, handleType) => {
    setDragging({ dayIndex, handleType });
  };

  const handleMouseEnterHour = (dayIndex, hour) => {
    if (!dragging || dragging.dayIndex !== dayIndex) return;

    setDaysHours((prev) => {
      const newDaysHours = [...prev];
      let dayObj = { ...newDaysHours[dayIndex] };

      if (dragging.handleType === "top") {
        const newStart = Math.min(hour, dayObj.endHour - 1);
        dayObj.startHour = Math.max(newStart, 0);
      } else {
        const newEnd = hour + 1;
        dayObj.endHour = Math.min(Math.max(newEnd, dayObj.startHour + 1), 24);
      }

      newDaysHours[dayIndex] = dayObj;
      return newDaysHours;
    });
  };

  useEffect(() => {
    const handleBeforeUnload = (e) => {
      const hasChanges =
        JSON.stringify(daysHours) !== initialDaysHours ||
        JSON.stringify(roles) !== initialRoles;

      if (hasChanges) {
        e.preventDefault();
        e.returnValue = ""; // Nécessaire pour certains navigateurs
        return "";
      }
    };




    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, [daysHours, roles, initialDaysHours, initialRoles]);

  useWarnIfUnsavedChanges(
    JSON.stringify(daysHours) !== initialDaysHours || JSON.stringify(roles) !== initialRoles
  );

  return (
    <div className="semaine-container">
      <button onClick={onBack} className="btn-back">
        ← Retour au mois
      </button>
      <h2>Semaine {week.weekNumber}</h2>
      <div style={{ marginTop: "20px", display: "flex", justifyContent: "center", gap: "10px" }}>
      <div style={{ marginTop: "20px", display: "flex", justifyContent: "center", gap: "10px" }}>
  <button
    className="btn-save"
    onClick={async () => {
      await handleSaveWeek();
      window.location.href = `/Calendrier?week=${week.weekNumber - 1}`;
    }}
  >
    ← Semaine précédente
  </button>
  <button
    className="btn-save"
    onClick={async () => {
      await handleSaveWeek();
      window.location.href = `/Calendrier?week=${week.weekNumber + 1}`;
    }}
  >
    Semaine suivante →
  </button>
</div>

</div>



<button
   className="btn-save"
   onClick={handleToggleWeekDisabled}
   style={{ marginBottom: "20px" }}
 >
   🔁 Activer / Désactiver toute la semaine
 </button>
      <div className="days-columns">
        {daysHours.map((dayObj, dayIndex) => {
          const { date, startHour, endHour } = dayObj;
          const dayLabel = dayjs(date).format("dddd D MMMM");

          return (

            <div
              key={date.toString()}
              className={`day-column ${disabledDays[date] ? "disabled-day" : ""}`}
              style={{ position: "relative" }}
            >
              <h3>{dayLabel}</h3>
              <button
                onClick={() => handleToggleDisabledDay(date)}
                style={{
                  position: "absolute",
                  top: "5px",
                  right: "5px",
                  backgroundColor: "red",
                  color: "white",
                  border: "none",
                  borderRadius: "50%",
                  width: "22px",
                  height: "22px",
                  fontWeight: "bold",
                  cursor: "pointer",
                  lineHeight: "20px",
                  textAlign: "center",
                  padding: 0,
                  zIndex: 1
                }}
                title={disabledDays[date] ? "Réactiver" : "Désactiver"}
              >
                ×
              </button>



              {!disabledDays[date] && (
              <>
              <div className="day-hours">
                {Array.from({ length: 17 }, (_, i) => {
                  const hour = i + 6; // Heures de 8h à 23h
                  const isHighlighted = hour >= startHour && hour < endHour;
                  const isTopHandle = hour === startHour;
                  const isBottomHandle = hour === endHour - 1;

                  let blockClass = "hour-block";
                  if (isHighlighted) blockClass += " highlight";
                  if (isTopHandle || isBottomHandle) blockClass += " handle";

                  return (
                    <div
                      key={hour}
                      className={blockClass}
                      onMouseDown={() => {
                        if (isTopHandle) {
                          handleMouseDownOnHandle(dayIndex, "top");
                        } else if (isBottomHandle) {
                          handleMouseDownOnHandle(dayIndex, "bottom");
                        }
                      }}
                      onMouseEnter={() => handleMouseEnterHour(dayIndex, hour)}
                    >
                      {hour}h
                    </div>
                  );
                })}
              </div>
              <div className="day-buttons">
                <button
                  className="toggle-button"
                  onClick={() =>
                    setShowAllerInfo((prev) => ({
                      ...prev,
                      [date]: !prev[date],
                    }))
                  }
                >
                  {showAllerInfo[date]
                    ? "Masquer Aller"
                    : "Infos Aller"}
                </button>

                {showAllerInfo[date] && (
                  <div className="aller-info">
                    <label htmlFor="depart-select">Départ Aller</label>
                    <br />
                    <select
                      id="depart-select"
                      value={dayObj.departAller}
                      onChange={(e) =>
                        handleDepartAllerChange(dayIndex, e.target.value)
                      }
                    >
                      <option value="Maison">Adresse Personnelle</option>
                      <option value="Villetaneuse">Villetaneuse</option>
                      <option value="Saint-Denis">Saint-Denis</option>
                      <option value="Bobigny">Bobigny</option>
                    </select>
                    <br />

                    <label htmlFor="retour-select">Destination Aller</label>
                    <br />
                    <select
                      id="retour-select"
                      value={dayObj.destinationAller}
                      onChange={(e) =>
                        handleDestinationAllerChange(dayIndex, e.target.value)
                      }
                    >
                      <option value="Villetaneuse">Villetaneuse</option>
                      <option value="Maison">Adresse Personnelle</option>
                      <option value="Saint-Denis">Saint-Denis</option>
                      <option value="Bobigny">Bobigny</option>
                    </select>
                    <br />

                    <div className="switch-container">
                      <label>Rôle à l'aller :</label>
                      <ToggleSwitch
                        checked={roles[dayObj.date]?.aller === "conducteur"}
                        onChange={() =>
                          setRoles((prevRoles) => ({
                            ...prevRoles,
                            [dayObj.date]: {
                              ...prevRoles[dayObj.date],
                              aller:
                                prevRoles[dayObj.date]?.aller === "conducteur"
                                  ? "passager"
                                  : "conducteur",
                            },
                          }))
                        }
                      />
                      <span className="switch-text">
                        {roles[dayObj.date]?.aller === "conducteur"
                          ? "🚗 Conducteur"
                          : "🧍 Passager"}
                      </span>
                    </div>
                  </div>
                )}

                <button
                  className="toggle-button"
                  onClick={() =>
                    setShowRetourInfo((prev) => ({
                      ...prev,
                      [date]: !prev[date],
                    }))
                  }
                >
                  {showRetourInfo[date]
                    ? "Masquer Retour"
                    : "Infos Retour"}
                </button>

                {showRetourInfo[date] && (
                  <div className="retour-info">
                    <label htmlFor="depart-select-retour">Départ Retour</label>
                    <br />
                    <select
                      id="depart-select-retour"
                      value={dayObj.departRetour}
                      onChange={(e) =>
                        handleDepartRetourChange(dayIndex, e.target.value)
                      }
                    >
                      <option value="Maison">Adresse Personnelle</option>
                      <option value="Villetaneuse">Villetaneuse</option>
                      <option value="Saint-Denis">Saint-Denis</option>
                      <option value="Bobigny">Bobigny</option>
                    </select>
                    <br />

                    <label htmlFor="retour-select-retour">
                      Destination Retour
                    </label>
                    <br />
                    <select
                      id="retour-select-retour"
                      value={dayObj.destinationRetour}
                      onChange={(e) =>
                        handleDestinationRetourChange(dayIndex, e.target.value)
                      }
                    >
                      <option value="Villetaneuse">Villetaneuse</option>
                      <option value="Maison">Adresse Personnelle</option>
                      <option value="Saint-Denis">Saint-Denis</option>
                      <option value="Bobigny">Bobigny</option>
                    </select>
                    <br />

                    <div className="switch-container">
                      <label>Rôle au retour :</label>
                      <ToggleSwitch
                        checked={roles[dayObj.date]?.retour === "conducteur"}
                        onChange={() =>
                          setRoles((prevRoles) => ({
                            ...prevRoles,
                            [dayObj.date]: {
                              ...prevRoles[dayObj.date],
                              retour:
                                prevRoles[dayObj.date]?.retour === "conducteur"
                                  ? "passager"
                                  : "conducteur",
                            },
                          }))
                        }
                      />
                      <span className="switch-text">
                        {roles[dayObj.date]?.retour === "conducteur"
                          ? "🚗 Conducteur"
                          : "🧍 Passager"}
                      </span>
                    </div>
                  </div>
                )}
              </div>
              </>
)}
            </div>
          );
        })}
      </div>

      <button onClick={handleSaveWeek} className="btn-save">
        💾 Sauvegarder
      </button>
      <button onClick={handleSaveAndPropagate} className="btn-save" style={{ marginTop: "10px" }}>
  🔁    Propager la semaine aux autres vides
      </button>

    </div>
  );
}

export default SemaineView;
