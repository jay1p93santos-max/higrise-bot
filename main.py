import asyncio
from highrise import BaseBot, Position
from highrise.models import User, SessionMetadata

# --- LISTE DES ÉMOTES ET CONFIGURATIONS ---
EMOTES_LIST = [
    # Danses & TikTok
    "dance-tiktok8", "dance-tiktok2", "dance-tiktok10", "dance-weird", 
    "dance-russian", "dance-shoppingcart", "dance-breakdance", "dance-popart", 
    "dance-hiphop", "dance-shuffle", "dance-spiritual", "dance-smoothwalk", 
    "dance-robot", "dance-floss", "dance-orangejustice",
    # Actions, Poses & Expressions
    "emote-wave", "emote-kiss", "emote-laughing", "emote-frog", 
    "emote-pose5", "emote-pose7", "emote-pose8", "emote-flex", 
    "emote-energyball", "emote-teleporting", "emote-wings", "emote-charge", 
    "emote-monster_fail", "emote-confused", "emote-bow", "emote-model", 
    "emote-slobber", "emote-cute", "emote-yes", "emote-no", "emote-angry", 
    "emote-sleepy", "emote-zombie", "emote-swordfight", "emote-headbang", 
    "emote-hero", "emote-gravity", "emote-fashion", "emote-jet", 
    "emote-boxer", "emote-celebrate", "emote-chug"
]

EMOTES_NUMEROS = {str(i): EMOTES_LIST[i-1] for i in range(1, len(EMOTES_LIST) + 1)}

def get_gold_bar(amount: int) -> str:
    """Valide et renvoie l'identifiant de lingot d'or"""
    valid_amounts = [1, 5, 10, 50, 100, 500, 1000, 5000, 10000]
    if amount in valid_amounts:
        return f"bars_{amount}"
    return None

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.user_loops = {}
        self.vip_users = set()
        
        # --- NOUVELLES VARIABLES ---
        self.owner_username = "_jay10"
        self.moderators = set()
        self.vip_cost = "10"
        self.custom_join_message = ""

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("Bot connecté avec succès !")

    async def on_user_join(self, user: User, position: Position) -> None:
        # Second accueil / Message VIP envoyé en chuchoté
        welcome_msg = f"Bienvenue {user.username} ! Tu veux profiter du VIP ? Envoie un pourboire de {self.vip_cost} pour l'obtenir."
        await self.highrise.send_whisper(user.id, welcome_msg)
        
        # Accueil personnel du propriétaire si défini
        if self.custom_join_message and user.username.lower() == self.owner_username.lower():
            await self.highrise.send_whisper(user.id, self.custom_join_message)

    async def dance_loop(self, user_id: str, emote_id: str):
        try:
            while self.user_loops.get(user_id, False):
                await self.highrise.send_emote(emote_id, user_id)
                await asyncio.sleep(8)
        except Exception as e:
            print(f"Erreur boucle emote : {e}")

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.lower().strip()

        # Vérification des rôles (Propriétaire / Modérateur)
        is_owner = user.username.lower() == self.owner_username.lower()
        is_mod = user.id in self.moderators or is_owner

        # --- 1. ACCORDER L'ACCÈS VIP ---
        if msg.startswith("!vip @"):
            target_username = msg.replace("!vip @", "").strip()
            self.vip_users.add(target_username.lower())
            await self.highrise.send_whisper(user.id, f"⭐ @{target_username} a maintenant accès au VIP !")

        # --- 2. COMMANDE !SETJOIN (Accueil du propriétaire) ---
        elif msg.startswith("!setjoin "):
            if not is_owner:
                await self.highrise.send_whisper(user.id, "Seul le propriétaire peut définir ce message.")
                return
            self.custom_join_message = message[9:].strip()
            await self.highrise.send_whisper(user.id, "Message d'accueil personnel mis à jour avec succès !")

        # --- 3. COMMANDE *VIPCOST (Montant) PERMANENT ---
        elif msg.startswith("*vipcost ") and msg.endswith(" permanent"):
            if not is_mod:
                await self.highrise.send_whisper(user.id, "Réservé aux modérateurs et au propriétaire.")
                return
            parts = message.split()
            if len(parts) >= 2:
                self.vip_cost = parts[1]
                await self.highrise.send_whisper(user.id, f"Le coût du VIP permanent est maintenant fixé à {self.vip_cost}.")

        # --- 4. COMMANDE !ADDMOD (Ajouter un modérateur) ---
        elif msg.startswith("!addmod @"):
            if not is_owner:
                await self.highrise.send_whisper(user.id, "Seul le propriétaire peut ajouter des modérateurs.")
                return
            target_name = msg.replace("!addmod @", "").strip()
            try:
                room_users = (await self.highrise.get_room_users()).content
                found = False
                for room_user, _ in room_users:
                    if room_user.username.lower() == target_name.lower():
                        self.moderators.add(room_user.id)
                        found = True
                        break
                if found:
                    await self.highrise.send_whisper(user.id, f"@{target_name} est désormais modérateur.")
                else:
                    await self.highrise.send_whisper(user.id, f"Utilisateur @{target_name} introuvable dans la pièce.")
            except Exception as e:
                print(f"Erreur addmod : {e}")

        # --- 5. ARRÊT DE L'ÉMOTE ---
        elif msg in ["0", "stop"]:
            self.user_loops[user.id] = False
            try:
                await self.highrise.send_emote("emote-rest", user.id)
            except Exception as e:
                print(f"Erreur arrêt : {e}")

        # --- 6. TÉLÉPORTATION SIMPLIFIÉE ---
        elif msg == "!tp":
            try:
                await self.highrise.teleport(user.id, Position(5.0, 0.0, 5.0))
            except Exception as e:
                print(f"Erreur TP : {e}")

        # --- 7. DÉCLENCHEMENT D'ÉMOTE ---
        elif msg in EMOTES_NUMEROS:
            self.user_loops[user.id] = True
            emote_id = EMOTES_NUMEROS[msg]
            try:
                await self.highrise.send_emote(emote_id, user.id)
            except Exception as e:
                print(f"Erreur emote : {e}")
            asyncio.create_task(self.dance_loop(user.id, emote_id))

        # --- 8. COMMANDE D'AIDE ---
        elif msg == "!help":
            await self.highrise.send_whisper(user.id, "Commandes disponibles : !tp, !help, !setjoin, !addmod, *vipcost ... permanent, 0/stop, et les numéros d'emotes.")

if __name__ == "__main__":
    import asyncio
    from highrise.__main__ import main

    definitions = [
        (Bot(), "6a819ca594613dc3a8816d518c7414777c27170a7b45f45853b0f555e71464b5")
    ]

    asyncio.run(main(definitions))
