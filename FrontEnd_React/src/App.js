import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Header from "./components/Header";
import Footer from "./components/Footer";
import Accueil from "./pages/Accueil";
import Inscription from "./pages/Inscription";
import Connexion from "./pages/Connexion";
import PolitiqueConfidentialite from "./pages/Politiqueconfidentialite";
import ConducteurMap from "./pages/ConducteurMap";
import { AuthProvider } from "./context/AuthContext";
import Timeline from "./pages/Timeline";

import Calendrier from "./pages/Calendrier";
import "./App.css";

function App() {

  return (
    <AuthProvider>
    <Router>
      <div className="App">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Accueil />} />
            <Route path="/inscription" element={<Inscription />} />
            <Route path ="/connexion" element={<Connexion />} />
            <Route path ="/politiqueconfidentialite" element={<PolitiqueConfidentialite />} />
            <Route path="/InterfaceConducteur" element={<ConducteurMap />} />
            <Route path="/Calendrier" element={<Calendrier />} />
            <Route path="/timeline" element={<Timeline />} />

          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
    </AuthProvider>
  );
}

export default App;
