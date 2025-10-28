import discord
from discord.ext import commands
from models.database import SkillsDB
from typing import Optional


# View for skill deletion confirmation
class SkillDeleteView(discord.ui.View):
    def __init__(self, bot, guild_id: int, normalized_name: str, author: discord.User):
        super().__init__(timeout=30)
        self.bot = bot
        self.guild_id = guild_id
        self.normalized_name = normalized_name
        self.author = author

    @discord.ui.button(label="確認刪除", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("您無法執行此操作", ephemeral=True)
            return
        
        success = self.bot.skills_db.delete_skill(self.guild_id, self.normalized_name)
        if success:
            summary = f"{self.author.mention} 刪除了技能 `{self.normalized_name}`"
            await interaction.response.edit_message(content=summary, view=None)
        else:
            await interaction.response.edit_message(content="刪除失敗", view=None)

    @discord.ui.button(label="取消", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("您無法執行此操作", ephemeral=True)
            return
        
        await interaction.response.edit_message(content=f"{self.author.mention} 取消刪除操作", view=None)




# Skill commands
class SkillCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="skill", description="技能資料庫指令")
    @discord.app_commands.describe(
        action="操作 add、show 或 delete",
        name="技能名稱",
        skill_type="技能類型 (add 必填)",
        level="技能等級 (add 必填)",
        effect="技能效果 (add 必填)"
    )
    @discord.app_commands.choices(action=[
        discord.app_commands.Choice(name="add", value="add"),
        discord.app_commands.Choice(name="show", value="show"),
        discord.app_commands.Choice(name="delete", value="delete")
    ])
    async def skill(self, interaction: discord.Interaction, 
                    action: discord.app_commands.Choice[str],
                    name: str,
                    skill_type: Optional[str] = None,
                    level: Optional[str] = None,
                    effect: Optional[str] = None):
        """技能資料庫指令"""
        if not interaction.guild:
            embed = discord.Embed(
                color=0xFF0000,
                description="此指令僅能在伺服器中使用"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate action
        valid_actions = ["add", "show", "delete"]
        if action.value not in valid_actions:
            await interaction.response.send_message("操作必須是 'add', 'show' 或 'delete' 之一", ephemeral=True)
            return
        
        if action.value == "add":
            if not skill_type or not skill_type.strip():
                embed = discord.Embed(
                    color=0xFF0000,
                    description="請提供技能類型"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if not level or not level.strip():
                embed = discord.Embed(
                    color=0xFF0000,
                    description="請提供技能等級"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if not effect or not effect.strip():
                embed = discord.Embed(
                    color=0xFF0000,
                    description="請提供技能效果"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Add skill to database
            success = self.bot.skills_db.add_skill(interaction.guild.id, name, skill_type, level, effect)
            if success:
                embed = discord.Embed(
                    title="技能已儲存",
                    color=0x00AA00,
                    description=f"**名稱**: `{name}`\n**類型**: {skill_type}\n**等級**: {level}\n**效果**: {effect}"
                )
            else:
                embed = discord.Embed(
                    title="技能儲存失敗",
                    color=0xFF0000,
                    description="無法儲存技能"
                )
            
            await interaction.response.send_message(embed=embed)
        
        elif action.value == "show":
            skill_data = self.bot.skills_db.find_skill(interaction.guild.id, name)
            
            if skill_data:
                embed = discord.Embed(
                    title=f"技能：<{skill_data['name']}>",
                    color=0x7289DA,
                    description=f"**類型**: {skill_data['skill_type']}\n**等級**: {skill_data['level']}\n**效果**: {skill_data['effect']}"
                )
            else:
                embed = discord.Embed(
                    title=f"技能：<{name}>",
                    color=0xFFA500,
                    description=f"找不到技能 `{name}`"
                )
            
            await interaction.response.send_message(embed=embed)
        
        elif action.value == "delete":
            skill_data = self.bot.skills_db.find_skill(interaction.guild.id, name)
            
            if not skill_data:
                embed = discord.Embed(
                    color=0xFFA500,
                    description=f"找不到此伺服器中的技能 `{name}`，無法刪除"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Create confirmation buttons
            view = SkillDeleteView(self.bot, interaction.guild.id, skill_data['normalized_name'], interaction.user)
            embed = discord.Embed(
                title="確認刪除技能",
                description=(
                    f"目標技能：`{skill_data['name']}`\n"
                    f"類型：{skill_data['skill_type']}\n"
                    f"等級：{skill_data['level']}\n"
                    f"效果：{skill_data['effect']}"
                ),
                color=0x8B0000
            )
            await interaction.response.send_message(embed=embed, view=view)