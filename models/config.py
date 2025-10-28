import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


# Data classes for configuration
@dataclass
class GlobalConfig:
    developers: List[int]
    restart_mode: str
    restart_service: Optional[str]
    global_stream_enabled: bool
    global_stream_channel: Optional[int]

    def __post_init__(self):
        if not hasattr(self, 'developers'):
            self.developers = []
        if not hasattr(self, 'restart_mode'):
            self.restart_mode = "execv"
        if not hasattr(self, 'restart_service'):
            self.restart_service = None
        if not hasattr(self, 'global_stream_enabled'):
            self.global_stream_enabled = False
        if not hasattr(self, 'global_stream_channel'):
            self.global_stream_channel = None


@dataclass
class GuildConfig:
    log_channel: Optional[int]
    stream_mode: str
    stream_throttle: int  # milliseconds
    crit_success_channel: Optional[int]
    crit_fail_channel: Optional[int]
    dnd_rules: Dict[str, Any]
    coc_rules: Dict[str, Any]

    def __post_init__(self):
        if not hasattr(self, 'log_channel'):
            self.log_channel = None
        if not hasattr(self, 'stream_mode'):
            self.stream_mode = "Batch"
        if not hasattr(self, 'stream_throttle'):
            self.stream_throttle = 1000
        if not hasattr(self, 'crit_success_channel'):
            self.crit_success_channel = None
        if not hasattr(self, 'crit_fail_channel'):
            self.crit_fail_channel = None
        if not hasattr(self, 'dnd_rules'):
            self.dnd_rules = {
                'critical_success': 20,
                'critical_fail': 1,
                'max_dice_count': 50,
                'max_dice_sides': 1000
            }
        if not hasattr(self, 'coc_rules'):
            self.coc_rules = {
                'critical_success': 1,
                'critical_fail': 100,
                'skill_divisor_hard': 2,
                'skill_divisor_extreme': 5
            }


# Configuration manager
class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.global_config = GlobalConfig(
            developers=[],
            restart_mode="execv",
            restart_service=None,
            global_stream_enabled=False,
            global_stream_channel=None
        )
        self.guilds = {}
        self.load_config()

    def load_config(self):
        """Load configuration from JSON file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'global' in data and data['global']:
                        global_data = data['global']
                        self.global_config = GlobalConfig(
                            developers=global_data.get('developers', []),
                            restart_mode=global_data.get('restart_mode', 'execv'),
                            restart_service=global_data.get('restart_service'),
                            global_stream_enabled=global_data.get('global_stream_enabled', False),
                            global_stream_channel=global_data.get('global_stream_channel')
                        )
                    if 'guilds' in data and data['guilds']:
                        self.guilds = {}
                        for guild_id, config_data in data['guilds'].items():
                            self.guilds[int(guild_id)] = GuildConfig(
                                log_channel=config_data.get('log_channel'),
                                stream_mode=config_data.get('stream_mode', 'Batch'),
                                stream_throttle=config_data.get('stream_throttle', 1000),
                                crit_success_channel=config_data.get('crit_success_channel'),
                                crit_fail_channel=config_data.get('crit_fail_channel'),
                                dnd_rules=config_data.get('dnd_rules', {
                                    'critical_success': 20,
                                    'critical_fail': 1,
                                    'max_dice_count': 50,
                                    'max_dice_sides': 1000
                                }),
                                coc_rules=config_data.get('coc_rules', {
                                    'critical_success': 1,
                                    'critical_fail': 100,
                                    'skill_divisor_hard': 2,
                                    'skill_divisor_extreme': 5
                                })
                            )
            except Exception as e:
                print(f"Error loading config: {e}")
        else:
            self.save_config()

    def save_config(self):
        """Save configuration to JSON file"""
        try:
            data = {
                'global': asdict(self.global_config),
                'guilds': {str(guild_id): asdict(config) for guild_id, config in self.guilds.items()}
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_guild_config(self, guild_id: int) -> GuildConfig:
        """Get guild-specific configuration"""
        if guild_id not in self.guilds:
            self.guilds[guild_id] = GuildConfig(
                log_channel=None,
                stream_mode="Batch",
                stream_throttle=1000,
                crit_success_channel=None,
                crit_fail_channel=None,
                dnd_rules={
                    'critical_success': 20,
                    'critical_fail': 1,
                    'max_dice_count': 50,
                    'max_dice_sides': 1000
                },
                coc_rules={
                    'critical_success': 1,
                    'critical_fail': 100,
                    'skill_divisor_hard': 2,
                    'skill_divisor_extreme': 5
                }
            )
        return self.guilds[guild_id]

    def set_guild_config(self, guild_id: int, config: GuildConfig):
        """Set guild-specific configuration"""
        self.guilds[guild_id] = config
        self.save_config()

    def is_developer(self, user_id: int) -> bool:
        """Check if user is a developer"""
        return user_id in self.global_config.developers

    def add_developer(self, user_id: int) -> bool:
        """Add user to developer list"""
        if user_id in self.global_config.developers:
            return False
        self.global_config.developers.append(user_id)
        self.save_config()
        return True

    def remove_developer(self, user_id: int) -> bool:
        """Remove user from developer list"""
        if user_id not in self.global_config.developers:
            return False
        self.global_config.developers.remove(user_id)
        self.save_config()
        return True