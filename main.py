import asyncio
from highrise import BaseBot, Position
from highrise.models import User

# --- CONFIGURATION ---
# Coordonnées de téléportation basiques (!tp)
DEFAULT_POSITION = Position(5.0, 0.0, 5.0)

# Coordonnées de la zone VIP (quand un joueur tape "vip") -> Modifiez X, Y, Z selon votre pièce
VIP_POSITION = Position(10.0, 5.0, 10.0)

# Liste des émotes Highrise
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

# Association automatique des chiffres 1 à 350
EMOTES_NUMEROS = {str(i): EMOTES_LIST[(i - 1) % len(EMOTES_LIST)] for i in range(1, 351)}

def get_gold_bar(amount: int) -> str:
    """Valide et renvoie l'identifiant de la barre d'or."""
    valid_amounts = [1, 5, 10, 50, 100, 500, 1000]
    if amount in valid_amounts:
        return f"bars_{amount}"
    return None

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.user_loops = {}
        # Ensemble pour stocker les pseudos des utilisateurs autorisés VIP
        self.vip_users = set()

    async def on_start(self, session_metadata) -> None:
        print("Bot connecté avec 350 émotes, STOP, TIPS, SUMMON & Système VIP !")

    async def dance_loop(self, user_id: str, emote_id: str):
        try:
            while self.user_loops.get(user_id, False):
                await self.highrise.send_emote(emote_id, user_id)
                await asyncio.sleep(8)
        except Exception as e:
            print(f"Erreur boucle emote : {e}")

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.lower().strip()

        # --- 1. ACCORDER L'ACCÈS VIP (!vip @pseudo) ---
        if msg.startswith("!vip @") or (msg.startswith("!vip ") and len(msg.split()) > 1 and msg.split()[1] != "all"):
            target_username = msg.split()[1].replace("@", "").strip().lower()
            self.vip_users.add(target_username)
            await self.highrise.chat(f"⭐ @{target_username} a reçu le statut VIP ! Tapez 'vip' pour aller dans la zone VIP.")

        # --- 2. SE TÉLÉPORTER AU VIP (mot-clé "vip" sans point d'exclamation) ---
        elif msg == "vip":
            if user.username.lower() in self.vip_users:
                try:
                    await self.highrise.teleport(user.id, VIP_POSITION)
                    await self.highrise.send_whisper(user.id, "Bienvenue dans la zone VIP !")
                except Exception as e:
                    print(f"Erreur téléportation VIP : {e}")
            else:
                await self.highrise.send_whisper(user.id, "Vous n'avez pas l'accès VIP.")

        # --- 3. COMMANDE !SUMMON (@pseudo) ---
        elif msg.startswith("!summon "):
            target_username = msg.split()[1].replace("@", "").strip().lower()
            try:
                room_users = (await self.highrise.get_room_users()).content
                target_user = next((u for u, pos in room_users if u.username.lower() == target_username), None)
                caller_pos = next((pos for u, pos in room_users if u.id == user.id), None)

                if target_user and isinstance(caller_pos, Position):
                    await self.highrise.teleport(target_user.id, caller_pos)
                    await self.highrise.chat(f"✨ {target_user.username} a été invoqué(e) auprès de {user.username} !")
                else:
                    await self.highrise.send_whisper(user.id, "Utilisateur introuvable dans la pièce.")
            except Exception as e:
                print(f"Erreur summon : {e}")

        # --- 4. COMMANDE !TIP ALL <MONTANT> ---
        elif msg.startswith("!tip all ") or msg.startswith("!tips all "):
            parts = msg.split()
            if len(parts) >= 3 and parts[2].isdigit():
                amount = int(parts[2])
                bar_type = get_gold_bar(amount)
                
                if not bar_type:
                    await self.highrise.send_whisper(user.id, "Montant invalide. Choisissez parmi : 1, 5, 10, 50, 100, 500, 1000.")
                    return

                try:
                    room_users = (await self.highrise.get_room_users()).content
                    count = 0
                    for room_user, _ in room_users:
                        if room_user.id != self.user_id:
                            await self.highrise.tip_user(room_user.id, bar_type)
                            count += 1
                            await asyncio.sleep(0.5)
                    await self.highrise.chat(f"🎁 Tip envoyé à {count} personnes ({amount} Or chacun) !")
                except Exception as e:
                    print(f"Erreur tip : {e}")

        # --- 5. ARRÊT DE L'ÉMOTE (0 ou stop) ---
        elif msg in ["0", "stop"]:
            self.user_loops[user.id] = False
            try:
                await self.highrise.send_emote("idle-std", user.id)
                await self.highrise.send_whisper(user.id, "Émote arrêtée !")
            except Exception as e:
                print(f"Erreur arrêt : {e}")

        # --- 6. TÉLÉPORTATION SIMPLIFIÉE (!tp) ---
        elif msg == "!tp":
            try:
                await self.highrise.teleport(user.id, DEFAULT_POSITION)
                await self.highrise.send_whisper(user.id, "Téléporté !")
            except Exception as e:
                print(f"Erreur TP : {e}")

        # --- 7. DÉCLENCHEMENT D'ÉMOTE (1 à 350) ---
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
            await self.highrise.chat("Commandes : 1-350 (danser), '0'/'stop' (arrêter), !tp, !vip @user, vip, !summon @user, !tip all <montant>.") 

if __name__ == "__main__":
    import asyncio
    from highrise.__main__ import main
    asyncio.run(main())
