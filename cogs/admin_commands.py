import discord
import asyncio
from discord.ext import commands
from models.config import ConfigManager
from typing import Optional


# View for admin action confirmation
class AdminConfirmView(discord.ui.View):
    def __init__(self, bot, action: str, author: discord.User):
        super().__init__(timeout=30)
        self.bot = bot
        self.action = action
        self.author = author

    @discord.ui.button(label="確認", style=discord.ButtonStyle.primary)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("您無法執行此操作", ephemeral=True)
            return
        
        await interaction.response.edit_message(content=f"已確認，機器人即將{self.action}……", view=None)
        
        if self.action == "restart":
            # Schedule restart
            asyncio.create_task(self.restart_bot())
        elif self.action == "shutdown":
            # Schedule shutdown
            asyncio.create_task(self.shutdown_bot())

    @discord.ui.button(label="取消", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("您無法執行此操作", ephemeral=True)
            return
        
        await interaction.response.edit_message(content="操作已取消", view=None)

    async def restart_bot(self):
        """Restart the bot (in a real implementation, this would restart the process)"""
        # In a real implementation, this would restart the bot process
        # For now, we'll just log the event
        import logging
        logger = logging.getLogger('trpg_bot')
        logger.info("Restart command received")
        # await self.bot.close()

    async def shutdown_bot(self):
        """Shutdown the bot (in a real implementation, this would shut down the process)"""
        # In a real implementation, this would shut down the bot process
        # For now, we'll just log the event and close the connection
        import logging
        logger = logging.getLogger('trpg_bot')
        logger.info("Shutdown command received")
        await self.bot.close()


# Define choices for admin actions
class AdminAction(discord.app_commands.Choice[str]):
    restart = discord.app_commands.Choice(name="restart", value="restart")
    shutdown = discord.app_commands.Choice(name="shutdown", value="shutdown")
    dev_add = discord.app_commands.Choice(name="dev-add", value="dev-add")
    dev_remove = discord.app_commands.Choice(name="dev-remove", value="dev-remove")
    dev_list = discord.app_commands.Choice(name="dev-list", value="dev-list")

# Admin commands
class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="admin", description="管理指令")
    @discord.app_commands.describe(
        action="操作類型 (restart, shutdown, dev-add, dev-remove, dev-list)",
        user="要操作的用戶 (dev-add 和 dev-remove 時必須)"
    )
    @discord.app_commands.choices(action=[
        discord.app_commands.Choice(name="restart", value="restart"),
        discord.app_commands.Choice(name="shutdown", value="shutdown"),
        discord.app_commands.Choice(name="dev-add", value="dev-add"),
        discord.app_commands.Choice(name="dev-remove", value="dev-remove"),
        discord.app_commands.Choice(name="dev-list", value="dev-list")
    ])
    async def admin(self, interaction: discord.Interaction, 
                    action: discord.app_commands.Choice[str],
                    user: Optional[discord.User] = None):
        """管理指令"""
        # Check if user is a developer
        if not self.bot.config_manager.is_developer(interaction.user.id):
            await interaction.response.send_message("您沒有權限執行此操作！", ephemeral=True)
            return
        
        # Validate action
        valid_actions = ["restart", "shutdown", "dev-add", "dev-remove", "dev-list"]
        if action.value not in valid_actions:
            await interaction.response.send_message("操作必須是 'restart', 'shutdown', 'dev-add', 'dev-remove', 'dev-list' 之一", ephemeral=True)
            return
        
        if action.value == "dev-list":
            developers = self.bot.config_manager.global_config.developers
            if not developers:
                await interaction.response.send_message("目前沒有開發者")
            else:
                dev_list = "開發者列表:\n"
                for dev_id in developers:
                    dev_list += f"<@{dev_id}>\n"
                await interaction.response.send_message(dev_list)
            return
        
        if action.value in ["dev-add", "dev-remove"] and not user:
            await interaction.response.send_message("請指定要操作的用戶！", ephemeral=True)
            return
        
        if action.value == "dev-add":
            if self.bot.config_manager.add_developer(user.id):
                await interaction.response.send_message(f"用戶 {user.mention} 已添加到開發者列表")
            else:
                await interaction.response.send_message(f"用戶 {user.mention} 已經是開發者")
        
        elif action.value == "dev-remove":
            if self.bot.config_manager.remove_developer(user.id):
                await interaction.response.send_message(f"用戶 {user.mention} 已從開發者列表移除")
            else:
                await interaction.response.send_message(f"用戶 {user.mention} 不在開發者列表中")
        
        elif action.value in ["restart", "shutdown"]:
            # Confirmation view for dangerous operations
            view = AdminConfirmView(self.bot, action.value, interaction.user)
            await interaction.response.send_message(f"確認執行{action.value}操作？", view=view, ephemeral=True)