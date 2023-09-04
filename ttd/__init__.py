import discord

from discord.ext import commands
from discord import Intents

class telegram_to_discord(commands.Bot):
    def __init__(self, discord_intents):
        super().__init__(
            command_prefix = '!',
            help_command = None,
            intents = discord_intents
        )

        self.extensions = [
            'ttd.extension.util'
        ]
    
    async def setup_hook(self):
        ...
        
    async def close(self):
        await super().close()