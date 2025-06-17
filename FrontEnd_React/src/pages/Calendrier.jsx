import React, { useState, useContext, useEffect } from "react";
import dayjs from "dayjs";
import isoWeek from "dayjs/plugin/isoWeek";
import isSameOrAfter from "dayjs/plugin/isSameOrAfter";
import isSameOrBefore from "dayjs/plugin/isSameOrBefore";
import { AuthContext } from "../context/AuthContext";
import MoisView from "./MoisView";
import SemaineView from "./SemaineView";
import 'dayjs/locale/fr';
import "./Calendrier.css";
import { useSearchParams } from 'react-router-dom';

import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";

// existing dayjs.locale('fr');
// existing dayjs.extend(isoWeek);
dayjs.extend(utc);
dayjs.extend(timezone);

dayjs.locale('fr');
dayjs.extend(isoWeek);
dayjs.extend(isSameOrAfter);
dayjs.extend(isSameOrBefore);

const YEAR = 2025;

const MONTH_NAMES = [
  "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
  "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
];

function getWeeksInMonth(year, monthIndex) {
  const startOfMonth = dayjs(`${year}-${monthIndex+1}-01`).startOf("month");
  const endOfMonth = startOfMonth.endOf("month");

  let current = startOfMonth.startOf("isoWeek"); // Lundi
  const weeks = [];

  while (current.isSameOrBefore(endOfMonth, "day") || current.isBefore(endOfMonth.startOf("isoWeek"))) {
    const weekNumber = current.isoWeek();
    const days = Array.from({ length: 7 }, (_, i) => current.add(i, "day"));
    weeks.push({ weekNumber, days });
    current = current.add(7, "day");
  }

  return weeks;
}

function Calendrier2025({ }) {
  const { userId } = useContext(AuthContext);
  const [selectedMonth, setSelectedMonth] = useState(null);
  const [selectedWeek, setSelectedWeek] = useState(null);

  const [searchParams] = useSearchParams();
  const queryWeek = searchParams.get("week");  // ex : "16" si ?week=16
  useEffect(() => {
       if (queryWeek) {
         const w = parseInt(queryWeek, 10);
         const paramWeekData = getDaysInIsoWeek(YEAR, w);
         setSelectedWeek(paramWeekData);
       }
      }, [queryWeek]);

  if (!userId) {
    return <p>Veuillez vous connecter.</p>;
  }

  let effectiveToday = dayjs();
  const day = effectiveToday.day(); // 0 = dimanche, 6 = samedi
  if (day === 6) effectiveToday = effectiveToday.add(2, "day");
  else if (day === 0) effectiveToday = effectiveToday.add(1, "day");

  const currentMonthIndex = effectiveToday.month();
  const weeksInMonth = getWeeksInMonth(YEAR, currentMonthIndex);

  const currentWeekData = weeksInMonth.find(week =>
    week.days.some(d => d.isSame(effectiveToday, "day"))
  );


  // ** Si une semaine est sélectionnée, affiche la SemaineView **
  if (selectedWeek) {
    return (
      <SemaineView
        week={selectedWeek}
        userId={userId}
        onBack={() => setSelectedWeek(null)}
      />
    );
  }

  // ** Si un mois est sélectionné, affiche la MoisView **
  if (selectedMonth !== null) {
    const monthName = MONTH_NAMES[selectedMonth];
    const weeks = getWeeksInMonth(YEAR, selectedMonth);
    const monthData = { monthIndex: selectedMonth, monthName, weeks };
    return (
      <MoisView
        year={YEAR}
        monthData={monthData}
        userId={userId}
        onBack={() => setSelectedMonth(null)}
      />
    );
  }

  return (
    <div>
      <div className="info-box">
      <p style={{}}>
        Bienvenue sur votre calendrier personnalisé !<br />
        Ici, vous devez définir vos <strong>horaires de présence</strong> pour chaque jour de la semaine
        ainsi que vos <strong>envies de covoiturage</strong> (en tant que conducteur ou passager).<br />
        Ces informations nous permettront de vous proposer des trajets adaptés avec d'autres utilisateurs. 🚗
        Une fois les informations saisies, rendez vous sur la page "Mes trajets" pour voir vos trajets à venir et envoyer des demandes de covoiturage aux conducteurs. <br />
        <strong>Note :</strong> Si vous ne définissez pas vos horaires de présence, vous ne pourrez pas voir les trajets proposés par d'autres utilisateurs.
      </p></div>

      <h1>Calendrier Année {YEAR}</h1>
      <button
        className="today-button"
        onClick={() => setSelectedWeek(currentWeekData)}
      >
        📅 Aller à aujourd’hui
      </button>

      <div className="months-container">
        {MONTH_NAMES.map((m, i) => (
          <div
            key={i}
            onClick={() => setSelectedMonth(i)}
            id={`month-${i}`}
            className={`month-box ${effectiveToday.month() === i ? "current-month" : ""}`}
          >
            {m}
          </div>
        ))}
      </div>
    </div>
  );
}
function getDaysInIsoWeek(year, isoWeekNumber) {
     const start = dayjs().year(year).isoWeek(isoWeekNumber).startOf('isoWeek');
     const days = Array.from({ length: 7 }, (_, i) => start.add(i, 'day'));
     return { weekNumber: isoWeekNumber, days };
   }

export default Calendrier2025;
