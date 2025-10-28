# TRPG Discord Bot package initialization
from .utils.bot import TRPGDiscordBot
from .models.config import ConfigManager, GlobalConfig, GuildConfig
from .models.database import SkillsDB
from .core.dice_roller import DiceRoller
from .core.coc_roller import CoCRoller

__version__ = "1.0.0"
__author__ = "lanxia404"