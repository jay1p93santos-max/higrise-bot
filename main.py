from highrise import BaseBot, Position
from highrise.models import User

# Dictionnaire regroupant les émotes (classiques et récentes)
EMOTES = {
    # Émotes classiques et populaires
    "wave": "emote-wave",
    "dance": "dance-tiktok8",
    "sing": "idle_singing",
    "frog": "emote-frog",
    "pose": "emote-pose1",
    "laugh": "emote-laughing",
    "kiss": "emote-kiss",
    "flex": "emote-flex",
    "sit": "idle-loop-sitfloor",
    
    # Nouvelles et récentes émotes Highrise
    "zero": "emote-energyball",
    "think": "emote-confused",
    "hot": "emote-hot",
    "curtsy": "emote-curtsy",
    "bow": "emote-bow",
    "model": "emote-model",
    "snake": "emote-snake",
    "charge": "emote-charge",
    "wings": "emote-wings",
    "float": "emote-float",
    "teleport": "emote-teleporting",
    "slobber": "emote-slobber",
    "monster": "emote-monster_fail"
}

class Bot(BaseBot):
    async def on_chat(self, user: User, message: str) -> None:
        msg = message.lower().strip()

        # --- 1. TÉLÉPORTATION ---
        # Commande : !tp (Téléporte l'utilisateur à des coordonnées précises)
        if msg == "!tp":
            try:
                # Modifie X=5.0, Y=0.0, Z=5.0 selon tes besoins dans la room
                await self.highrise.teleport(user.id, Position(5.0, 0.0, 5.0))
                await self.highrise.send_whisper(user.id, "Téléportation réussie !")
            except Exception as e:
                print(f"Erreur TP : {e}")

        # --- 2. ÉMOTES PAR COMMANDE (ex: !dance, !wave, !wings) ---
        elif msg.startswith("!"):
            emote_name = msg[1:] # Enlève le "!"
            if emote_name in EMOTES:
                try:
                    await self.highrise.send_emote(EMOTES[emote_name], user.id)
                except Exception as e:
                    print(f"Erreur emote : {e}")

        # --- 3. LISTE DES COMMANDES ---
        elif msg == "!help":
            await self.highrise.chat("Commandes : !tp, !help ou tapez le nom d'une emote (ex: !dance, !wings, !float, !zero, !kiss)")


