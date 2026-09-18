from highrise import BaseBot, Position
from highrise.models import User

class Bot(BaseBot):
    async def on_start(self, session_metadata):
        print("Bot connecté !")
        await self.highrise.send_whisper(session_metadata.user_id, "Bot allumé ✅")

    async def on_user_join(self, user: User, position: Position):
        print(f"{user.username} a rejoint")
        await self.highrise.chat(f"Bienvenue {user.username} dans la room ! 🎉")

    async def on_chat(self, user: User, message: str):
        if message.lower().startswith("!hello"):
            await self.highrise.chat(f"Hello {user.username} !")

    async def on_whisper(self, user: User, message: str):
        print(f"{user.username} m'a chuchoté: {message}")

from highrise.__main__ import main
if __name__ == "__main__":
    main(Bot)
