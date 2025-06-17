// MoisView.jsx
import React, { useState } from "react";
import SemaineView from "./SemaineView";
import "./MoisView.css";

function MoisView({ year, monthData,userId, onBack }) {
  const [selectedWeek, setSelectedWeek] = useState(null);
  const { monthName, weeks } = monthData;


  if (selectedWeek) {
    return (
      <SemaineView
        week={selectedWeek}
        userId={userId}
        onBack={() => setSelectedWeek(null)}
      />
    );
  }
  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('fr-FR', { month: 'long', day: 'numeric' });
  }

  const today = new Date().toISOString().split("T")[0];
  return (
    <div>
        <button className="BackButton" onClick={onBack}>← Retour à l'année</button>
        <h2>{monthName} {year}</h2>
        <div className="weeks-grid">
          {weeks.map((week) => (
            <button
            key={week.weekNumber}
            className={`week-button ${week.days.some(day => day.toISOString().split("T")[0] === today) ? "current-week" : ""}`}
            onClick={() => setSelectedWeek(week)}
          >
            Semaine du {formatDate(week.days[0])} au {formatDate(week.days[6])}
          </button>

          ))}
        </div>

    </div>
  );
}

export default MoisView;
