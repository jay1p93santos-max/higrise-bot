import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from highrise import BaseBot, Position
from highrise.models import User

# Mini-serveur Web pour garder la connexion Render active
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Highrise actif !")

def run_web_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# Liste des émotes Highrise (servira à remplir automatiquement les 350 numéros)
EMOTES_LIST = [
    # Danses & TikTok
    "dance-tiktok8", "dance-tiktok2", "dance-tiktok10", "dance-pennywise", "dance-macarena",
    "dance-weird", "dance-russian", "dance-shoppingcart", "dance-duckwalk", "dance-handsup",
    "dance-breakdance", "dance-poptart", "dance-hiphop", "dance-voguehand", "dance-creepypuppet",
    "dance-shuffle", "dance-spiritual", "dance-smoothwalk", "dance-singleladies", "dance-samba",
    "dance-robot", "dance-floss", "dance-orangejustice", "dance-gangnam", "dance-kpop",
    
    # Actions, Poses & Expressions
    "emote-wave", "emote-kiss", "emote-laughing", "emote-frog", "emote-pose1", "emote-pose3",
    "emote-pose5", "emote-pose7", "emote-pose8", "emote-flex", "idle-loop-sitfloor", "idle_singing",
    "emote-energyball", "emote-teleporting", "emote-wings", "emote-float", "emote-snake",
    "emote-charge", "emote-monster_fail", "emote-confused", "emote-hot", "emote-curtsy",
    "emote-bow", "emote-model", "emote-slobber", "emote-cute", "emote-snowangel", "emote-sad",
    "emote-yes", "emote-no", "emote-angry", "emote-sleepy", "emote-shy", "emote-clap",
    "emote-zombie", "emote-swordfight", "emote-headbang", "emote-think", "emote-judging",
    "emote-hero", "emote-gravity", "emote-fashion", "emote-jetpack", "emote-ghost",
    "emote-boxer", "emote-celebrate", "emote-chug", "emote-disco", "emote-death",
    
    # Émotes spéciales
    "emote-superpose", "emote-astronaut", "emote-dinosaur", "emote-bunnyhop", "emote-ninja",
    "emote-hearteyes", "emote-fireworks", "emote-magic", "emote-propose", "emote-guitar"
]

# Associe les numéros "1" à "350" aux émotes en bouclant sur la liste
EMOTES_NUMEROS = {str(i): EMOTES_LIST[(i - 1) % len(EMOTES_LIST)] for i in range(1, 351)}

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        # Dictionnaire pour gérer les boucles d'émotes par utilisateur
        self.user_loops = {}

    async def on_start(self, session_metadata) -> None:
        print("Bot connecté avec 350 émotes et fonction STOP !")

    async def dance_loop(self, user_id: str, emote_id: str):
        """Joue l'émote en boucle jusqu'à l'envoi de 'stop' ou '0'."""
        try:
            while self.user_loops.get(user_id, False):
                await self.highrise.send_emote(emote_id, user_id)
                await asyncio.sleep(8)  # Pause entre chaque répétition de la danse
        except Exception as e:
            print(f"Erreur boucle emote : {e}")

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.lower().strip()

        # --- 1. ARRÊTER L'ÉMOTE / LA BOUCLE (0 ou stop) ---
        if msg in ["0", "stop"]:
            # Arrête la boucle infinie si elle était active
            self.user_loops[user.id] = False
            try:
                # Réinitialise la position du joueur pour couper l'émote en cours
                await self.highrise.send_emote("idle-std", user.id)
                await self.highrise.send_whisper(user.id, "Émote arrêtée !")
            except Exception as e:
                print(f"Erreur lors de l'arrêt de l'émote : {e}")

        # --- 2. TÉLÉPORTATION ---
        elif msg == "!tp":
            try:
                await self.highrise.teleport(user.id, Position(5.0, 0.0, 5.0))
                await self.highrise.send_whisper(user.id, "Téléporté !")
            except Exception as e:
                print(f"Erreur TP : {e}")

        # --- 3. DÉCLENCHEMENT D'UNE ÉMOTE (1 à 350) ---
        elif msg in EMOTES_NUMEROS:
            # Stoppe une ancienne boucle s'il y en avait une en cours
            self.user_loops[user.id] = True
            emote_id = EMOTES_NUMEROS[msg]
            
            # Lance l'émote immédiatement
            try:
                await self.highrise.send_emote(emote_id, user.id)
            except Exception as e:
                print(f"Erreur emote : {e}")
                
            # Démarre la répétition en arrière-plan
            asyncio.create_task(self.dance_loop(user.id, emote_id))

        # --- 4. AIDE ---
        elif msg == "!help":
            await self.highrise.chat("Tapez un numéro entre 1 et 350 pour danser. Tapez '0' ou 'stop' pour vous arrêter ! Tapez !tp pour vous téléporter.")
