import './Politiqueconfidentialite.css';

function Politiqueconfidentialite() {
  return (
    <div className="politiqueconfidentialite">
      <h1 className="titre">Politique de Confidentialité</h1>
      <h2 className="sous-titre">CoVoitUniv</h2>

      <div className="article">
        <h3>ARTICLE 1 : PRÉAMBULE</h3>
        <p>
          La présente politique de confidentialité a pour but d’informer les utilisateurs du site :
        </p>
        <ul className="liste-confidentialite ">
          <li>
            Sur la manière dont sont collectées leurs données personnelles. Sont considérées comme des données personnelles, toute information permettant d’identifier un utilisateur. A ce titre, il peut s’agir : de ses noms et prénoms, de son âge, de son adresse postale ou email, de sa localisation ou encore de son adresse IP (liste non-exhaustive) ; 
          </li>
          <li>Sur les droits dont ils disposent concernant ces données ;</li>
          <li>
            Sur la personne responsable du traitement des données à caractère personnel collectées ;
          </li>
          <li>Sur les destinataires de ces données personnelles ;</li> 
        </ul>
        
      </div>

      <div className="article">
        <h3>ARTICLE 2 : PRINCIPES RELATIFS À LA COLLECTE</h3>
        <p>
            Conformément à l’article 5 du Règlement européen 2016/679, les données à caractère personnel sont :   
        </p>
        <ul className="liste-confidentialite ">
          <li>Traitées de manière licite, loyale et transparente au regard de la personne concernée  ; </li>
          <li>Collectées pour des finalités déterminées (cf. Article 3.1 des présentes), explicites et légitimes, et ne pas être traitées ultérieurement d'une manière incompatible avec ces finalités ; </li>
          <li>Adéquates, pertinentes et limitées à ce qui est nécessaire au regard des finalités pour lesquelles elles sont traitées ; </li>
          <li>Exactes et tenues à jour;</li>
          <li>Conservées pendant une durée limitée; </li>
          <li>Sécurisées contre tout accès ou perte non autorisé;</li>
        </ul>
      </div>

      <div className="article">
        <h3>ARTICLE 3 : DONNÉES COLLECTÉES</h3>
        <h4>3.1 Données collectées</h4>
        <p>Les données collectées sont les suivantes:</p>
        <ul className="liste-confidentialite ">
          <li>Nom et prénom</li>
          <li>Adresse email</li>
          <li>Numéro de téléphone</li>
          <li>Adresse postale</li>
        </ul>
        <h4>3.2 Mode de collecte</h4>
        <p> Les données personnelles sont collectées directement auprès de l'utilisateur via les formulaires présents sur le site, notamment lors de :</p>
        <ul className="liste-confidentialite ">
            <li>La création d’un compte utilisateur (formulaire d'inscription) ;</li>
            <li>La connexion à l’espace personnel ;</li>
            <li>La soumission de trajets ou de demandes de covoiturage ;</li>
            <li>L’utilisation des services liés à la gestion du profil ou du calendrier de disponibilité.</li>
        </ul>
        <p>
            Aucune donnée n’est collectée de manière automatique sans l’action volontaire de l’utilisateur.
        </p>


        <h4>3.3 Hébergement</h4>
        <p>
        L'application est hébergée localement dans le cadre d'un projet pédagogique. 
        Les données sont stockées dans une base de données locale au format SQLite (.db), non accessible depuis Internet.
        </p>
        


        <h4>3.4 Transmission à des tiers</h4>
        <p>
        Aucune donnée personnelle n’est transmise à un serveur distant ou à un service d’hébergement externe. 
        L’accès à la base est strictement limité aux membres du projet pour le bon fonctionnement et le test de l'application.
        </p>

        
      </div>

      <div className="article">
        <h3>ARTICLE 4 : RESPONSABLE DU TRAITEMENT</h3>
        <p>M. Dutier, gabriel.dutier@univ-paris13.fr </p>

        
      </div>

      <div className="article">
        <h3>ARTICLE 5 : DROITS DE L’UTILISATEUR</h3>
        <ul className="liste-confidentialite ">
          <li>Droit d’accès, de rectification, d’effacement</li>
          <li>Droit à la portabilité</li>
          <li>Droit à la limitation et à l’opposition</li>
          <li>Droit de ne pas faire l’objet d’une décision automatisée</li>
          <li>Droit de définir le sort des données après décès</li>
          <li>Droit de recours auprès de la CNIL</li>
        </ul>
        <p>
          Pour exercer vos droits : gabriel.dutier@univ-paris13.fr. Preuve d’identité requise.
        </p>
      </div>

      <div className="article">
        <h3>ARTICLE 6 : MODIFICATIONS</h3>
        <p>
          L’éditeur peut modifier cette politique à tout moment. Dernière mise à jour : 18/06/2025.
        </p>
      </div>
    </div>
  );
}

export default Politiqueconfidentialite;
