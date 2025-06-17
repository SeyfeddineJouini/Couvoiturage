import { motion } from "framer-motion";
import React, { useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import "./Accueil.css"; // Ajout du fichier CSS

function Accueil() {
  const { isAuthenticated } = useContext(AuthContext);

  return (
    <div className="accueil-container">
      {/* Section de bienvenue */}
      <div className="hero">
        <h1>🚗 CoVoitUniv</h1>
        <p className="subtitle">
          Partagez vos trajets et simplifiez vos déplacements universitaires.
        </p>
      </div>

      {/* Boutons de connexion / inscription ou accès aux trajets */}
      <div className="buttons-container">
        {!isAuthenticated ? (
          <>
            <Link to="/inscription" className="btn primary-btn">
              S'inscrire
            </Link>
            <Link to="/connexion" className="btn secondary-btn">
              Connexion
            </Link>
          </>
        ) : (
          <>
            <Link to="/calendrier" className="btn primary-btn">
              Mon emploi du temps
            </Link>
            <Link to="/timeline" className="btn secondary-btn">
              Mes trajets
            </Link>
          </>
        )}
      </div>

      {/* Avantages du covoiturage */}
      <div className="features">
        {!isAuthenticated ? (
          <>
            <h2>Pourquoi choisir CoVoitUniv ?</h2>
            <div className="feature-box">
              {[
                {
                  key: "etape1",
                  content: (
                    <>
                      <h3>💰 Économie</h3>
                      <p>
                        Réduisez vos coûts de transport en partageant les
                        trajets.
                      </p>
                    </>
                  ),
                },
                {
                  key: "etape2",
                  content: (
                    <>
                      <h3>🌍 Écologie</h3>
                      <p>
                        Diminuez votre empreinte carbone en limitant le nombre
                        de voitures.
                      </p>
                    </>
                  ),
                },
                {
                  key: "etape3",
                  content: (
                    <>
                      <h3>🤝 Convivialité</h3>
                      <p>Voyagez ensemble et créez de nouvelles rencontres.</p>
                    </>
                  ),
                },
              ].map((step, index) => (
                <motion.div
                  key={step.key}
                  className="feature"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.6, duration: 0.6 }}
                >
                  {step.content}
                </motion.div>
              ))}
            </div>
          </>
        ) : (
          <>
            <h2>Comment utiliser CoVoitUniv ?</h2>
            <div className="feature-box">
              {[
                {
                  key: "etape1",
                  content: (
                    <>
                      <h3>
                        Étape 1️⃣ L'onglet <br />
                        <Link to="/calendrier">Mon emploi du temps</Link>
                      </h3>
                      <p>
                        Ajoutez vos <u>horaires de présence</u> à l'Université
                        afin d'établir un <u>calendrier personnalisé</u> tout au
                        long de l'année.
                      </p>
                      <p>
                        Il servira de base à notre calculateur pour que vous
                        puissiez arriver à l'heure à l'Université.
                      </p>
                    </>
                  ),
                },
                {
                  key: "etape2",
                  content: (
                    <>
                      <h3>
                        Étape 2️⃣ L'onglet <br />
                        <Link to="/timeline">Mes trajets</Link>
                      </h3>
                      <h4>
                        Après le calendrier sauvegardé, deux possibilités :
                      </h4>
                      <p>
                        - Consultez les <u>trajets proposés</u> par d'autres
                        utilisateurs si vous êtes <u>passager</u>.
                        <br />
                        <strong>ou</strong>
                        <br />- <u>Proposez</u> le vôtre si vous êtes{" "}
                        <u>conducteur</u>.
                      </p>
                    </>
                  ),
                },
                {
                  key: "etape3",
                  content: (
                    <>
                      <h3>Étape 3️⃣</h3>
                      <h3>🚗 Pour les conducteurs :</h3>
                      <p>
                        Choisissez vos futurs passagers afin de permettre une
                        future mise en relation.
                      </p>
                      <h3>🚶‍♂️ Pour les passagers :</h3>
                      <p>
                        Dès qu’un conducteur accepte votre trajet, vous recevrez
                        un e-mail contenant tous les détails nécessaires au bon
                        déroulement du trajet.
                      </p>
                    </>
                  ),
                },
              ].map((step, index) => (
                <motion.div
                  key={step.key}
                  className="feature"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.6, duration: 0.6 }}
                >
                  {step.content}
                </motion.div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default Accueil;
