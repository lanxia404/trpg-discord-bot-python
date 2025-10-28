import discord
from discord.ext import commands
from core.dice_roller import DiceRoller
from core.coc_roller import CoCRoller
from typing import List, Tuple


# Dice commands
class DiceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="roll", description="D&D 骰子指令 - 擲骰子")
    async def roll(self, interaction: discord.Interaction, expression: str):
        """D&D 骰子指令 - 擲骰子"""
        if not interaction.guild:
            await interaction.response.send_message("此指令只能在伺服器中使用", ephemeral=True)
            return
        
        config = self.bot.config_manager.get_guild_config(interaction.guild.id)
        rules = config.dnd_rules
        
        try:
            results = DiceRoller.roll_multiple_dice(expression, rules)
            
            if len(results) == 1:
                result = results[0]
                rolls_str = " + ".join(map(str, result['rolls']))
                
                if result['modifier'] != 0:
                    total_str = f"({rolls_str}) + {result['modifier']} = {result['total']}"
                else:
                    total_str = f"{rolls_str} = {result['total']}"
                
                crit_info = ""
                if result['is_critical_success']:
                    crit_info = " ✨ 大成功!"
                elif result['is_critical_fail']:
                    crit_info = " 💥 大失敗!"
                
                comparison_info = ""
                if result['comparison_result'] is not None:
                    if result['comparison_result']:
                        comparison_info = "✅ 成功 "
                    else:
                        comparison_info = "❌ 失敗 "
                
                description = f"🎲 D&D 擲骰: {expression} = {total_str}{crit_info}{comparison_info}"
                
                embed = discord.Embed(
                    title="D&D 擲骰結果",
                    description=description,
                    color=0x7289DA
                )
            else:
                description = "🎲 連續擲骰結果:\n"
                for i, result in enumerate(results, 1):
                    rolls_str = " + ".join(map(str, result['rolls']))
                    if result['modifier'] != 0:
                        total_str = f"({rolls_str}) + {result['modifier']} = {result['total']}"
                    else:
                        total_str = f"{rolls_str} = {result['total']}"
                    
                    description += f"{i}. {expression} = {total_str}\n"
                
                embed = discord.Embed(
                    title="D&D 連續擲骰結果",
                    description=description,
                    color=0x7289DA
                )
            
            await interaction.response.send_message(embed=embed)
            
        except ValueError as e:
            embed = discord.Embed(
                title="D&D 擲骰錯誤",
                description=f"錯誤: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="coc", description="CoC 7e 指令")
    @discord.app_commands.describe(
        skill="技能值 (1-100)",
        times="擲骰次數 (1-10) [可選]"
    )
    async def coc(self, interaction: discord.Interaction, skill: discord.app_commands.Range[int, 1, 100], times: discord.app_commands.Range[int, 1, 10] = 1):
        """CoC 7e 指令"""
        if not interaction.guild:
            await interaction.response.send_message("此指令只能在伺服器中使用", ephemeral=True)
            return

        config = self.bot.config_manager.get_guild_config(interaction.guild.id)
        rules = config.coc_rules
        
        results = CoCRoller.roll_coc_multi(skill, times, rules)
        
        # Get author and channel for critical event logging
        author = interaction.user
        channel = interaction.channel
        
        # Collect critical events for logging
        from typing import List, Tuple
        CriticalKind = Tuple[str, str]  # (success/fail, message)
        crit_events: List[CriticalKind] = []
        multiple = len(results) > 1
        
        for i, result in enumerate(results):
            prefix = f"第 {i + 1} 次 " if multiple else ""
            roll_values = str(result['roll'])
            
            if result['is_critical_success']:
                crit_events.append((
                    "success",
                    f"{author.mention} 在 `/coc {skill}` {prefix}擲出 {roll_values}，觸發大成功（頻道：{channel.mention}）"
                ))
            if result['is_critical_fail']:
                crit_events.append((
                    "fail",
                    f"{author.mention} 在 `/coc {skill}` {prefix}擲出 {roll_values}，觸發大失敗（頻道：{channel.mention}）"
                ))

        if len(results) == 1:
            result = results[0]
            success_text = CoCRoller.format_success_level(result['success_level'])
            
            description = (
                f"技能值: {skill}\n"
                f"骰子結果: {result['roll']}\n"
                f"判定結果: {success_text}"
            )
            
            if result['is_critical_success']:
                description += " ✨ 大成功!"
            elif result['is_critical_fail']:
                description += " 💥 大失敗!"
            
            embed = discord.Embed(
                title="CoC 7e 擲骰結果",
                description=description,
                color=0x7289DA
            )
        else:
            description = f"連續擲骰次數: {len(results)}\n技能值: {skill}\n"
            for i, result in enumerate(results, 1):
                success_text = CoCRoller.format_success_level(result['success_level'])
                crit = " ✨" if result['is_critical_success'] else " 💥" if result['is_critical_fail'] else ""
                status = " ✅" if result['comparison_result'] else " ❌" if result['comparison_result'] is False else ""
                description += f"{i}. {result['roll']} → {success_text}{crit}{status}\n"
            
            embed = discord.Embed(
                title="CoC 7e 連續擲骰結果",
                description=description,
                color=0x7289DA
            )
        
        await interaction.response.send_message(embed=embed)
        
        # Log critical events if in a guild
        if interaction.guild:
            await self.log_critical_events(interaction, interaction.guild.id, crit_events)

    async def log_critical_events(self, interaction: discord.Interaction, guild_id: int, events: List[Tuple[str, str]]):
        """Log critical success/fail events to dedicated channels"""
        if not events:
            return

        config = self.bot.config_manager.get_guild_config(guild_id)
        
        for kind, content in events:
            channel_id = None
            title = ""
            colour = 0
            
            if kind == "success":
                channel_id = config.crit_success_channel
                title = "大成功紀錄"
                colour = 0x006400  # DARK_GREEN
            elif kind == "fail":
                channel_id = config.crit_fail_channel
                title = "大失敗紀錄"
                colour = 0x8B0000  # DARK_RED
            
            if channel_id:
                channel = interaction.client.get_channel(channel_id)
                if channel:
                    embed = discord.Embed(
                        title=title,
                        description=content,
                        color=colour
                    )
                    try:
                        await channel.send(embed=embed)
                    except Exception as e:
                        print(f"發送關鍵紀錄失敗: {e}")