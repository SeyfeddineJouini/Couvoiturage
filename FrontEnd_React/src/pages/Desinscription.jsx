import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import './Desinscription.css'; 



function Desinscription() {
    
    const { userId, logout } = useContext(AuthContext);
    const navigate = useNavigate();
    
    const handleDeleteAccount = async () => {
    const confirm = window.confirm("Êtes-vous sûr de vouloir vous désinscrire ? Cette action est irréversible.");
    if (!confirm) return;
    
    try {
      const response = await fetch(`http://localhost:5005/api/users/${userId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        logout(); // Déconnecter l'utilisateur
        alert("Votre compte a bien été supprimé.");
        navigate('/'); // Rediriger
      } else {
        alert("Erreur lors de la suppression du compte.");
      }
    } catch (error) {
      alert("Erreur serveur.");
    }
  };


    return (
    <div className="desinscription-page">
      <h1>Se désinscrire</h1>
      <p>Cette action supprimera définitivement votre compte.</p>
      <button className="danger-btn" onClick={handleDeleteAccount}>
        Confirmer la désinscription
      </button>
    </div>
  );
}


export default Desinscription;
