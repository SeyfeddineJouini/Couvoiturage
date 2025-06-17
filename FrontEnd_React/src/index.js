import React from "react";
import ReactDOM from "react-dom";
import App from "./App"; // Le composant principal de l'application

// Rendu de l'application dans la div avec l'id "root"
ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById("root") // Cible le conteneur dans public/index.html
);
