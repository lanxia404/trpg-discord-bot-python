import os
import logging
import discord
from discord.ext import commands
from models.config import ConfigManager
from models.database import SkillsDB

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('trpg_bot')
logger.setLevel(logging.INFO)


# Bot class
class TRPGDiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # Required to read message content
        intents.guilds = True
        
        super().__init__(command_prefix="!", intents=intents)
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.skills_db = SkillsDB()
        
    async def setup_hook(self):
        """Setup hook for the bot"""
        # Add cogs
        from cogs.dice_commands import DiceCommands
        from cogs.skill_commands import SkillCommands
        from cogs.log_commands import LogCommands
        from cogs.admin_commands import AdminCommands
        from cogs.help_commands import HelpCommands
        
        await self.add_cog(DiceCommands(self))
        await self.add_cog(SkillCommands(self))
        await self.add_cog(LogCommands(self))
        await self.add_cog(AdminCommands(self))
        await self.add_cog(HelpCommands(self))
        
        # Synchronize slash commands with Discord
        await self.tree.sync()
        
        logger.info("Bot setup complete")
    
    async def on_ready(self):
        """Event when bot is ready"""
        logger.info(f"{self.user} has logged in!")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        logger.info(f" Serving {len(self.users)} users")