import os
from dotenv import load_dotenv
import sys
import logging

# 添加當前目錄到 sys.path 以確保能正確導入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.bot import TRPGDiscordBot


# Load environment variables
load_dotenv()


# Main function
def main():
    bot_token = os.getenv("DISCORD_TOKEN")
    if not bot_token:
        raise ValueError("預期 DISCORD_TOKEN 環境變數，但找不到!")
    
    # Initialize and run the bot
    bot = TRPGDiscordBot()
    
    # Run the bot
    bot.run(bot_token)


if __name__ == "__main__":
    main()
