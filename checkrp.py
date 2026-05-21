import os
import subprocess
import requests
from datetime import datetime  # <-- Ajouté pour le timestamp

# --- CONFIGURATION AUTOMATIQUE DU LOG ---
_print_original = print
def print(*args, **kwargs):
    """Redéfinition de print pour inclure la date et l'heure locale"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    # On ajoute le timestamp devant le premier élément du print
    if args:
        args = (f"{timestamp} {args[0]}",) + args[1:]
    else:
        args = (timestamp,)
    _print_original(*args, **kwargs)
# ----------------------------------------

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
    texte_securise = texte_message.replace('"', '\\"')
    applescript = f'tell application "Messages" to send "{texte_securise}" to buddy "{MON_IDENTIFIANT_ICLOUD}"'
    
    try:
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

        derniere_ronde = liste_rondes[0]
        num_ircc = str(derniere_ronde.get("drawNumber"))
        
        print(f"-> Ronde détectée sur IRCC : #{num_ircc}")

        ancien_num = None
        if os.path.exists(FICHIER_ETAT):
            with open(FICHIER_ETAT, "r", encoding="utf-8") as f:
                ancien_num = f.read().strip()
        
        print(f"-> Ronde enregistrée dans le fichier texte : #{ancien_num}")

        if ancien_num is None:
            print("ℹ️ Premier lancement : Création du fichier d'initialisation sans envoi d'iMessage.")
            with open(FICHIER_ETAT, "w", encoding="utf-8") as f:
                f.write(num_ircc)
                
        elif num_ircc != ancien_num:
            print("🚨 Nouvelle ronde détectée ! Préparation du message...")
            
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
            
            envoyer_imessage(texte_alerte)
            
            with open(FICHIER_ETAT, "w", encoding="utf-8") as f:
                f.write(num_ircc)
        else:
            print("✅ À jour. Pas de nouvelle ronde depuis la dernière vérification.")

    except Exception as e:
        print(f"Une erreur technique est survenue : {e}")

if __name__ == "__main__":
    verifier_ircc()