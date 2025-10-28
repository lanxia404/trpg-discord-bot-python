import discord
from discord.ext import commands
from typing import Optional


# Define choices for log actions
# Log commands
class LogCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="log-stream", description="控制日誌串流開關")
    @discord.app_commands.describe(
        state="on 或 off",
        channel="要設定的日誌頻道 (開啟時必須)"
    )
    @discord.app_commands.choices(state=[
        discord.app_commands.Choice(name="on", value="on"),
        discord.app_commands.Choice(name="off", value="off")
    ])
    async def log_stream(self, interaction: discord.Interaction, 
                         state: discord.app_commands.Choice[str],
                         channel: Optional[discord.TextChannel] = None):
        """控制日誌串流開關"""
        if not interaction.guild:
            await interaction.response.send_message("此指令只能在伺服器中使用", ephemeral=True)
            return
        
        # Validate state
        valid_states = ["on", "off"]
        if state.value not in valid_states:
            await interaction.response.send_message("狀態必須是 'on' 或 'off' 之一", ephemeral=True)
            return
        
        if state.value == "on" and not channel:
            await interaction.response.send_message("請提供要啟用串流的文字頻道", ephemeral=True)
            return
        
        config = self.bot.config_manager.get_guild_config(interaction.guild.id)
        if state.value == "on":
            config.log_channel = channel.id
            self.bot.config_manager.set_guild_config(interaction.guild.id, config)
            await interaction.response.send_message(f"日誌串流已開啟，使用頻道: {channel.mention}")
        else:
            config.log_channel = None
            self.bot.config_manager.set_guild_config(interaction.guild.id, config)
            await interaction.response.send_message("日誌串流已關閉")

    @discord.app_commands.command(name="log-stream-mode", description="設定日誌串流模式")
    @discord.app_commands.describe(
        mode="live 或 batch"
    )
    @discord.app_commands.choices(mode=[
        discord.app_commands.Choice(name="live", value="live"),
        discord.app_commands.Choice(name="batch", value="batch")
    ])
    async def log_stream_mode(self, interaction: discord.Interaction, 
                              mode: discord.app_commands.Choice[str]):
        """設定日誌串流模式"""
        if not interaction.guild:
            await interaction.response.send_message("此指令只能在伺服器中使用", ephemeral=True)
            return
        
        # Validate mode
        valid_modes = ["live", "batch"]
        if mode.value not in valid_modes:
            await interaction.response.send_message("模式必須是 'live' 或 'batch' 之一", ephemeral=True)
            return
        
        config = self.bot.config_manager.get_guild_config(interaction.guild.id)
        config.stream_mode = mode.value
        self.bot.config_manager.set_guild_config(interaction.guild.id, config)
        await interaction.response.send_message(f"串流模式已設定為: {mode.value}")

    @discord.app_commands.command(name="crit", description="設定大成功/大失敗紀錄頻道")
    @discord.app_commands.describe(
        kind="success 或 fail",
        channel="要設定的頻道 (留空則清除設定)"
    )
    @discord.app_commands.choices(kind=[
        discord.app_commands.Choice(name="success", value="success"),
        discord.app_commands.Choice(name="fail", value="fail")
    ])
    async def crit(self, interaction: discord.Interaction, 
                   kind: discord.app_commands.Choice[str],
                   channel: Optional[discord.TextChannel] = None):
        """設定大成功/大失敗紀錄頻道"""
        if not interaction.guild:
            embed = discord.Embed(
                color=0xFF0000,
                description="此指令僅能在伺服器中使用"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate kind
        valid_kinds = ["success", "fail"]
        if kind.value not in valid_kinds:
            await interaction.response.send_message("類型必須是 'success' 或 'fail' 之一", ephemeral=True)
            return
        
        config = self.bot.config_manager.get_guild_config(interaction.guild.id)
        
        if kind.value == "success":
            config.crit_success_channel = channel.id if channel else None
            label = "大成功"
        else:
            config.crit_fail_channel = channel.id if channel else None
            label = "大失敗"
        
        self.bot.config_manager.set_guild_config(interaction.guild.id, config)
        
        if channel:
            description = f"已設定{label}紀錄頻道為 {channel.mention}"
        else:
            description = f"已清除{label}紀錄頻道設定"
        
        embed = discord.Embed(
            title="紀錄頻道已更新",
            description=description,
            color=0x7289DA
        )
        await interaction.response.send_message(embed=embed)