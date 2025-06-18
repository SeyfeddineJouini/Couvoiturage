import React, { useState } from "react";
import "./Inscription.css";
import CryptoJS from "crypto-js";

function Inscription() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    last_name: "",
    first_name: "",
    address: "",
    is_driver: false, // Booléen pour la case à cocher
  });

  const [isSubmitted, setIsSubmitted] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [consentGiven, setConsentGiven] = useState(false); // état pour le consentement
  
  const handleChange = (e) => {
    const { name, value} = e.target;
    setFormData({
      ...formData,
      [name]:  value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!consentGiven) {
      setErrorMessage("Vous devez accepter l'utilisation de vos données personnelles.");
      return;
    }

    try {
      const hashedPassword = CryptoJS.SHA256(formData.password).toString();
      const response = await fetch("http://localhost:5005/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ...formData, password: hashedPassword }),
      });

      const data = await response.json();
      if (response.ok) {
        setIsSubmitted(true);
      } else {
        setErrorMessage(result.message || "Une erreur s'est produite.");
      }
    } catch (error) {
      console.error("An error occurred:", error);
      setErrorMessage("Impossible de contacter le serveur.");
    }
  };

  return (
    <div className="page">
      <h1>Inscription</h1>
      {!isSubmitted ? (
        <form onSubmit={handleSubmit} className="form-container">
          <div className="form-group">
            <label htmlFor="email">Email :</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Mot de passe :</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="last_name">Nom :</label>
            <input
              type="text"
              id="last_name"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="first_name">Prénom :</label>
            <input
              type="text"
              id="first_name"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="address">Adresse :</label>
            <input
              type="text"
              id="address"
              name="address"
              value={formData.address}
              onChange={handleChange}
              required
            />
          </div>
          {/* ✅ Case à cocher RGPD */}
          <div className="form-group">
            <input
              type="checkbox"
              id="consent"
              checked={consentGiven}
              onChange={(e) => setConsentGiven(e.target.checked)}
              required
            />
          <label htmlFor="consent">
            J'accepte que mes données soient utilisées conformément à la{" "}
            <a href="/politiqueconfidentialite"  rel="noopener noreferrer">
              politique de confidentialité
            </a>.
          </label>
          </div>


          <div className="hasAccount">
            Vous avez déjà un compte?
            <br />
            <a href="/connexion">Connectez-vous</a>
          </div>

          {errorMessage && <p className="error-message">{errorMessage}</p>}

          <button type="submit" className="submit-btn">
            Valider les informations
          </button>
        </form>
      ) : (
        <div className="success-message">
          <h2>Inscription réussie !</h2>
        </div>
      )}
    </div>
  );
}

export default Inscription;
