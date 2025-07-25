# Suppose this is in email_utils.py or somewhere in your codebase
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

  # Use your Gmail address and password (stored securely or in environment variables)
SENDER_EMAIL = "noreplycovoitbot@gmail.com"
SENDER_PASSWORD = "jrgm luus ckes zbzc"

def send_email_via_gmail(sender_email, sender_password, to_email, subject, body):
    """
    Sends an email using Gmail's SMTP server.
    """
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the plain text body
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")


def send_offer_email(driver, passenger, departure_hour, sender_email, sender_password):
    """
    Envoie deux emails :
    1. Au passager pour lui proposer un trajet.
    2. Au conducteur pour confirmer l'offre avec les infos du passager.
    """

    # Format de l'heure de départ
    if isinstance(departure_hour, int):
        departure_str = f"{departure_hour:02d}:00"
    else:
        try:
            departure_str = departure_hour.strftime("%d/%m/%Y à %H:%M")
        except Exception:
            departure_str = str(departure_hour)

    # --- Email au passager ---
    subject_passenger = "Nouvelle Offre de Covoiturage - Confirmation Requise"
    body_passenger = (
        f"Bonjour {passenger.first_name} {passenger.last_name},\n\n"
        f"{driver.first_name} {driver.last_name} vous propose un trajet en covoiturage.\n"
        f"- Heure de départ : {departure_str}\n"
        f"- Adresse de départ du conducteur : {driver.address}\n"
        f"- Adresse email du conducteur : {driver.email}\n\n"
        f"Connectez-vous à l'application CoVoitUniv pour accepter ou refuser l'offre.\n\n"
        f"L'équipe CoVoitUniv\n"
        f"Contact : supportcovoitbot@gmail.com\n"
    )

    send_email_via_gmail(
        sender_email=sender_email,
        sender_password=sender_password,
        to_email=passenger.email,
        subject=subject_passenger,
        body=body_passenger
    )

    # --- Email au conducteur ---
    subject_driver = "Confirmation de votre Offre de Covoiturage"
    body_driver = (
        f"Bonjour {driver.first_name} {driver.last_name},\n\n"
        f"Vous avez proposé un trajet à {passenger.first_name} {passenger.last_name}.\n"
        f"Détails :\n"
        f"- Heure de départ : {departure_str}\n"
        f"- Adresse du passager : {passenger.address}\n"
        f"- Adresse email du passager : {passenger.email}\n\n"
        f"Merci pour votre contribution à la communauté CoVoitUniv !\n\n"
        f"L'équipe CoVoitUniv\n"
        f"Contact : supportcovoitbot@gmail.com\n"
    )

    send_email_via_gmail(
        sender_email=sender_email,
        sender_password=sender_password,
        to_email=driver.email,
        subject=subject_driver,
        body=body_driver
    )


if __name__ == "__main__":
    class DummyUser:
        def __init__(self, first_name, last_name, address, email):
            self.first_name = first_name
            self.last_name = last_name
            self.address = address
            self.email = "seckalioune107@gmail.com"  # <- ton adresse test

    driver = DummyUser("Jean", "Conducteur", "12 rue des Lilas, Paris", "tonemail@tondomaine.com")
    passenger = DummyUser("Marie", "Passagère", "45 avenue Victor Hugo, Lyon", "tonemail@tondomaine.com")

    send_offer_email(driver, passenger, "08:30", SENDER_EMAIL, SENDER_PASSWORD)
