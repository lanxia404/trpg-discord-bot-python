import discord
from discord.ext import commands
import logging


class HelpButton(discord.ui.Button):
    def __init__(self, label: str, custom_id: str, description: str):
        super().__init__(label=label, custom_id=custom_id, style=discord.ButtonStyle.secondary)
        self.description = description

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="指令說明",
            description=self.description,
            color=0x77B255
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


# View for help command
class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        
        # Add buttons for different help topics
        self.add_item(HelpButton("D&D 擲骰", "help_roll", 
            "**/roll <骰子表達式>**\n支援 `2d6`、`d20+5`、`1d10>=15`、`+3 d6` 等格式，解析骰數、面數、修正值與比較條件。預設最多 50 次擲骰。"))
        self.add_item(HelpButton("CoC 擲骰", "help_coc", 
            "**/coc <技能值> [次數]**\n技能值 1-100，可設定 1-10 次連續擲骰。自動判斷普通/困難/極限成功、大成功（1）與大失敗（技能<50 時 96-100，否則 100）。"))
        self.add_item(HelpButton("技能指令", "help_skill", 
            "**技能指令**\n`/skill add <名稱> <類型> <等級> <效果>`：新增或更新技能紀錄。\n`/skill show <名稱>`：支援模糊搜尋技能名稱，查詢技能。\n`/skill delete <名稱>`：刪除此伺服器中的技能。"))
        self.add_item(HelpButton("日誌指令", "help_logs", 
            "**日誌相關指令**\n`/log-stream on <頻道>`：啟用串流並綁定頻道。\n`/log-stream off`：關閉串流。\n`/log-stream-mode <live|batch>`：切換即時或批次。\n`/crit <success|fail> [頻道]`：設定大成功/大失敗紀錄頻道，留空則清除設定。"))
        self.add_item(HelpButton("管理指令", "help_admin", 
            "**管理指令（需開發者）**\n`/admin restart`：確認後重新啟動機器人。\n`/admin shutdown`：確認後關閉機器人。\n`/admin dev-add <用戶>` / `/admin dev-remove <用戶>`：維護開發者名單。\n`/admin dev-list`：列出所有已註冊開發者。"))


# Help commands
class HelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="help", description="顯示指令說明")
    async def help(self, interaction: discord.Interaction):
        """顯示指令說明"""
        embed = discord.Embed(
            title="TRPG Discord Bot 指令說明",
            description=(
                "請點擊下方按鈕查看各指令的詳細說明。\n"
                "支援 `/roll`、`/coc`、`/skill add`、`/skill show`、`/log-stream`、`/log-stream-mode`、`/crit`、`/admin`。"
            ),
            color=0x77B255
        )
        
        view = HelpView()
        await interaction.response.send_message(embed=embed, view=view)