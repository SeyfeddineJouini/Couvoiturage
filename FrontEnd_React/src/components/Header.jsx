import React, { useState, useEffect, useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import "./Header.css"; // Ajouter le fichier CSS pour styliser le header

function Header() {
  const { isAuthenticated, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');

  };

  return (

    <header className="header">
      <img src="/Covoit.png" alt="Logo Covoit" className="logo covoit" />
      <nav className="nav">
        <Link to="/" className="nav-link nav-accueil">
          Accueil
        </Link>
        {!isAuthenticated ? (
          <>
            <Link to="/inscription" className="nav-link nav-contact">
              S'inscrire
            </Link>
            <Link to="/connexion" className="nav-link nav-contact">
              Connexion
            </Link>
          </>
        ) : (
          <>
            <Link to="/calendrier" className="nav-link nav-edt">
            Mon EDT
            </Link>
            <Link to="/timeline" className="nav-link">
            Mes trajets
            </Link>

            <button onClick={handleLogout} className="nav-link nav-contact">
              Se déconnecter
            </button>
          </>
        )}
        <Link onClick={handleLogout} to="http://localhost:3000/" className="nav-link nav-contact">
            Bilan Carbonne
        </Link>
      </nav>
      <img src="/USPN.png" alt="Logo USPN" className="logo uspn" />
    </header>
  );
}

export default Header;
