import os
import subprocess
import requests

# 1. CONFIGURATION
# Mettez votre courriel iCloud ou votre numéro de téléphone (ex: "+1514XXXXXXX")

MON_IDENTIFIANT_ICLOUD = os.environ.get("MON_TELEPHONE")

URL_JSON = "https://www.canada.ca/content/dam/ircc/documents/json/ee_rounds_123_fr.json"
FICHIER_ETAT = "derniere_ronde.txt"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

def envoyer_imessage(texte_message):
    """Commande au Mac d'envoyer un iMessage via AppleScript"""
    # Échappement simple des guillemets pour éviter de casser la commande Bash
    texte_securise = texte_message.replace('"', '\\"')
    applescript = f'tell application "Messages" to send "{texte_securise}" to buddy "{MON_IDENTIFIANT_ICLOUD}"'
    
    try:
        # Python exécute la commande AppleScript directement sur le Mac
        subprocess.run(["osascript", "-e", applescript], check=True)
        print("💬 iMessage envoyé avec succès !")
    except subprocess.CalledProcessError as e:
        print(f"❌ Échec de l'envoi de l'iMessage. Vérifiez que l'app Messages est configurée. Erreur : {e}")

def verifier_ircc():
    print("Vérification des données d'IRCC...")
    try:
        reponse = requests.get(URL_JSON, headers=HEADERS)
        if reponse.status_code != 200:
            print(f"Erreur d'accès à IRCC : {reponse.status_code}")
            return

        donnees = reponse.json()
        liste_rondes = donnees.get("rounds", [])
        
        if not liste_rondes:
            print("Aucune ronde trouvée dans le fichier JSON d'IRCC.")
            return

        # Extraction de la dernière ronde en ligne (index 0)
        derniere_ronde = liste_rondes[0]
        num_ircc = str(derniere_ronde.get("drawNumber"))
        
        print(f"-> Ronde détectée sur IRCC : #{num_ircc}")

        # Lecture de l'historique local
        ancien_num = None
        if os.path.exists(FICHIER_ETAT):
            with open(FICHIER_ETAT, "r", encoding="utf-8") as f:
                ancien_num = f.read().strip()
        
        print(f"-> Ronde enregistrée dans le fichier texte : #{ancien_num}")

        # Comparaison logique
        if ancien_num is None:
            print("ℹ️ Premier lancement : Création du fichier d'initialisation sans envoi d'iMessage.")
            with open(FICHIER_ETAT, "w", encoding="utf-8") as f:
                f.write(num_ircc)
                
        elif num_ircc != ancien_num:
            print("🚨 Nouvelle ronde détectée ! Préparation du message...")
            
            # Récupération des détails de la ronde pour construire le texte
            date = derniere_ronde.get("drawDateFull")
            nom = derniere_ronde.get("drawName")
            places = derniere_ronde.get("drawSize")
            score = derniere_ronde.get("drawCRS")
            
            texte_alerte = (
                f"🇨🇦 Nouvelle ronde Entrée Express !\n\n"
                f"La ronde #{num_ircc} a été publiée.\n"
                f"• Type : {nom}\n"
                f"• Date : {date}\n"
                f"• Invitations envoyées : {places}\n"
                f"• Score minimum requis : {score}"
            )
            
            # Envoi de la notification
            envoyer_imessage(texte_alerte)
            
            # Sauvegarde de l'état pour bloquer les doublons au prochain coup
            with open(FICHIER_ETAT, "w", encoding="utf-8") as f:
                f.write(num_ircc)
        else:
            print("✅ À jour. Pas de nouvelle ronde depuis la dernière vérification.")

    except Exception as e:
        print(f"Une erreur technique est survenue : {e}")

if __name__ == "__main__":
    verifier_ircc()