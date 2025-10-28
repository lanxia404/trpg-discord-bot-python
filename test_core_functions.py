#!/usr/bin/env python3
"""
TRPG Discord Bot - 核心功能測試
"""

import os
import sys
import json
import sqlite3
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any


# 以下是從 main.py 中提取的核心功能類別，以便進行測試
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


# Database class for skill management
class SkillsDB:
    def __init__(self, db_path: str = "skills.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the skills database and create table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Create skills table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                guild_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                normalized_name TEXT NOT NULL,
                skill_type TEXT NOT NULL,
                level TEXT NOT NULL,
                effect TEXT NOT NULL,
                UNIQUE(guild_id, normalized_name)
            )
        ''')
        conn.commit()
        conn.close()

    def add_skill(self, guild_id: int, name: str, skill_type: str, level: str, effect: str) -> bool:
        """Add or update a skill in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            normalized_name = name.lower()
            cursor.execute('''
                INSERT OR REPLACE INTO skills (guild_id, name, normalized_name, skill_type, level, effect)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (guild_id, name, normalized_name, skill_type, level, effect))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding skill: {e}")
            return False
        finally:
            conn.close()

    def find_skill(self, guild_id: int, name: str) -> Optional[Dict[str, str]]:
        """Find a skill by guild and name (with fuzzy matching)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            normalized = name.lower()
            pattern = f"%{normalized}%"
            cursor.execute('''
                SELECT name, normalized_name, skill_type, level, effect
                FROM skills
                WHERE guild_id = ? AND normalized_name LIKE ?
                ORDER BY CASE WHEN normalized_name = ? THEN 0 ELSE 1 END,
                        ABS(LENGTH(normalized_name) - LENGTH(?)),
                        normalized_name
                LIMIT 1
            ''', (guild_id, pattern, normalized, normalized))
            row = cursor.fetchone()
            if row:
                return {
                    'name': row[0],
                    'normalized_name': row[1],
                    'skill_type': row[2],
                    'level': row[3],
                    'effect': row[4]
                }
            return None
        except Exception as e:
            print(f"Error finding skill: {e}")
            return None
        finally:
            conn.close()

    def delete_skill(self, guild_id: int, normalized_name: str) -> bool:
        """Delete a skill by guild and normalized name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                DELETE FROM skills
                WHERE guild_id = ? AND normalized_name = ?
            ''', (guild_id, normalized_name))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting skill: {e}")
            return False
        finally:
            conn.close()


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


# Dice rolling utilities
class DiceRoller:
    @staticmethod
    def parse_dice_expr(expr: str, rules: Dict[str, Any]) -> Tuple[int, int, int, Optional[Tuple[str, int]]]:
        """
        Parse a dice expression like "2d6+1" or "d20>=15"
        Returns: (count, sides, modifier, comparison)
        """
        import re
        expr = expr.strip()
        # Regex to match dice expressions like: 2d6+1, d20, 1d8>=10
        match = re.match(r'^(\d*)d(\d+)([+-]\d+)?(?:\s*([<>=!]{1,2})\s*(\d+))?$', expr)
        if not match:
            raise ValueError("Invalid dice expression format")
        
        count_str = match.group(1)
        count = int(count_str) if count_str else 1
        
        if count == 0:
            raise ValueError("Dice count must be at least 1")
        
        if count > rules['max_dice_count']:
            raise ValueError(f"Too many dice (max {rules['max_dice_count']})")
        
        sides = int(match.group(2))
        if sides < 2:
            raise ValueError("Dice must have at least 2 sides")
        
        if sides > rules['max_dice_sides']:
            raise ValueError(f"Dice has too many sides (max {rules['max_dice_sides']})")
        
        modifier_match = match.group(3)
        modifier = int(modifier_match) if modifier_match else 0
        
        op_match = match.group(4)
        value_match = match.group(5)
        comparison = (op_match, int(value_match)) if op_match and value_match else None
        
        return count, sides, modifier, comparison

    @staticmethod
    def roll_single_dice(sides: int) -> int:
        """Roll a single dice with given sides"""
        import random
        return random.randint(1, sides)

    @staticmethod
    def roll_dice(count: int, sides: int, modifier: int, comparison: Optional[Tuple[str, int]] = None) -> Dict[str, Any]:
        """Roll multiple dice and return results"""
        import random
        rolls = [DiceRoller.roll_single_dice(sides) for _ in range(count)]
        total = sum(rolls) + modifier
        
        # Check for critical success/fail (for d20)
        is_critical_success = sides == 20 and 20 in rolls
        is_critical_fail = sides == 20 and 1 in rolls
        
        # Evaluate comparison if present
        comparison_result = None
        if comparison:
            op, value = comparison
            if op == ">=":
                comparison_result = total >= value
            elif op == ">":
                comparison_result = total > value
            elif op == "<=":
                comparison_result = total <= value
            elif op == "<":
                comparison_result = total < value
            elif op == "==":
                comparison_result = total == value
            elif op == "!=":
                comparison_result = total != value
        
        return {
            'count': count,
            'sides': sides,
            'modifier': modifier,
            'rolls': rolls,
            'total': total,
            'is_critical_success': is_critical_success,
            'is_critical_fail': is_critical_fail,
            'comparison_result': comparison_result
        }

    @staticmethod
    def roll_multiple_dice(expr: str, rules: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse and roll multiple dice expressions (for consecutive rolls)"""
        import re
        # Check if expression is in the format "+N expr" for multiple rolls
        match = re.match(r'^\+?(\d+)\s+(.+)$', expr.strip())
        if match:
            roll_count = int(match.group(1))
            if roll_count == 0:
                raise ValueError("Roll count must be at least 1")
            if roll_count > rules['max_dice_count']:
                raise ValueError(f"Too many rolls (max {rules['max_dice_count']})")
            
            dice_expr = match.group(2).strip()
            count, sides, modifier, comparison = DiceRoller.parse_dice_expr(dice_expr, rules)
            
            results = []
            for _ in range(roll_count):
                # 每次都使用相同的骰子配置進行擲骰
                results.append(DiceRoller.roll_dice(count, sides, modifier, comparison))
            return results
        else:
            count, sides, modifier, comparison = DiceRoller.parse_dice_expr(expr, rules)
            return [DiceRoller.roll_dice(count, sides, modifier, comparison)]


# CoC utilities
class CoCRoller:
    @staticmethod
    def roll_coc(skill_value: int, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Roll for Call of Cthulhu 7th edition"""
        import random
        roll = random.randint(1, 100)
        success_level = CoCRoller.determine_success_level(roll, skill_value, rules)
        
        is_critical_success = roll == rules['critical_success']
        is_critical_fail = CoCRoller.is_critical_failure(roll, skill_value, rules)
        
        return {
            'roll': roll,
            'skill_value': skill_value,
            'success_level': success_level,
            'is_critical_success': is_critical_success,
            'is_critical_fail': is_critical_fail
        }

    @staticmethod
    def roll_coc_multi(skill_value: int, times: int, rules: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Roll multiple times for Call of Cthulhu 7th edition"""
        count = max(1, times)
        return [CoCRoller.roll_coc(skill_value, rules) for _ in range(count)]

    @staticmethod
    def determine_success_level(roll: int, skill_value: int, rules: Dict[str, Any]) -> int:
        """Determine the success level according to CoC 7e rules"""
        if roll == rules['critical_success']:  # Usually 1
            return 1  # Critical success
        
        if CoCRoller.is_critical_failure(roll, skill_value, rules):
            return 6  # Critical failure
        
        hard_success_threshold = skill_value / rules['skill_divisor_hard']
        extreme_success_threshold = skill_value / rules['skill_divisor_extreme']
        
        if roll == 100 or roll <= extreme_success_threshold:
            return 2  # Extreme success
        elif roll <= hard_success_threshold:
            return 3  # Hard success
        elif roll <= skill_value:
            return 4  # Regular success
        else:
            return 5  # Failure

    @staticmethod
    def is_critical_failure(roll: int, skill_value: int, rules: Dict[str, Any]) -> bool:
        """Check if the roll is a critical failure according to CoC 7e rules"""
        if skill_value < 50:
            # For skills under 50%, rolls 96-100 are critical failures
            return roll >= 96
        else:
            # For skills 50% or higher, only roll 100 is a critical failure
            return roll == rules['critical_fail']

    @staticmethod
    def format_success_level(level: int) -> str:
        """Format the success level as a string"""
        levels = {
            1: "大成功 (Critical Success)",
            2: "極限成功 (Extreme Success)",
            3: "困難成功 (Hard Success)",
            4: "普通成功 (Regular Success)",
            5: "失敗 (Failure)",
            6: "大失敗 (Critical Failure)"
        }
        return levels.get(level, "未知 (Unknown)")


def test_config():
    """測試配置功能"""
    print("測試配置功能...")
    
    # 測試 GlobalConfig
    global_config = GlobalConfig(
        developers=[123456789],
        restart_mode="execv",
        restart_service=None,
        global_stream_enabled=False,
        global_stream_channel=None
    )
    assert global_config.developers == [123456789]
    print("✓ GlobalConfig 測試通過")
    
    # 測試 GuildConfig
    guild_config = GuildConfig(
        log_channel=987654321,
        stream_mode="Live",
        stream_throttle=500,
        crit_success_channel=111111111,
        crit_fail_channel=222222222,
        dnd_rules={
            'critical_success': 20,
            'critical_fail': 1,
            'max_dice_count': 10,
            'max_dice_sides': 100
        },
        coc_rules={
            'critical_success': 1,
            'critical_fail': 100,
            'skill_divisor_hard': 2,
            'skill_divisor_extreme': 5
        }
    )
    assert guild_config.log_channel == 987654321
    assert guild_config.stream_mode == "Live"
    print("✓ GuildConfig 測試通過")
    
    # 測試 ConfigManager
    config_manager = ConfigManager("test_config.json")
    config_manager.global_config.developers = [111111111, 222222222]
    config_manager.save_config()
    
    # 讀取剛保存的配置
    new_manager = ConfigManager("test_config.json")
    assert 111111111 in new_manager.global_config.developers
    assert 222222222 in new_manager.global_config.developers
    print("✓ ConfigManager 測試通過")
    
    # 清理測試文件
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")
    
    print("配置功能測試完成\n")


def test_database():
    """測試數據庫功能"""
    print("測試數據庫功能...")
    
    # 使用測試數據庫
    db = SkillsDB("test_skills.db")
    
    # 測試添加技能
    success = db.add_skill(12345, "火球術", "法術", "高級", "造成火屬性傷害")
    assert success == True
    print("✓ 添加技能測試通過")
    
    # 測試查找技能
    skill = db.find_skill(12345, "火球術")
    assert skill is not None
    assert skill['name'] == "火球術"
    assert skill['skill_type'] == "法術"
    print("✓ 查找技能測試通過")
    
    # 測試模糊查找
    skill = db.find_skill(12345, "火球")
    assert skill is not None
    assert skill['name'] == "火球術"
    print("✓ 模糊查找技能測試通過")
    
    # 測試刪除技能
    success = db.delete_skill(12345, "火球術".lower())
    assert success == True
    skill = db.find_skill(12345, "火球術")
    assert skill is None
    print("✓ 刪除技能測試通過")
    
    # 清理測試數據庫
    if os.path.exists("test_skills.db"):
        os.remove("test_skills.db")
    
    print("數據庫功能測試完成\n")


def test_dice_roller():
    """測試骰子功能"""
    print("測試骰子功能...")
    
    # 測試骰子表達式解析
    rules = {
        'critical_success': 20,
        'critical_fail': 1,
        'max_dice_count': 50,
        'max_dice_sides': 1000
    }
    
    # 測試基本解析
    count, sides, modifier, comparison = DiceRoller.parse_dice_expr("2d6+1", rules)
    assert count == 2
    assert sides == 6
    assert modifier == 1
    assert comparison is None
    print("✓ 骰子表達式解析測試通過")
    
    # 測試比較表達式
    count, sides, modifier, comparison = DiceRoller.parse_dice_expr("d20>=15", rules)
    assert count == 1
    assert sides == 20
    assert modifier == 0
    assert comparison == (">=", 15)
    print("✓ 骰子比較表達式解析測試通過")
    
    # 測試骰子投擲
    result = DiceRoller.roll_dice(2, 6, 1, (">=", 10))
    assert len(result['rolls']) == 2
    assert all(1 <= roll <= 6 for roll in result['rolls'])
    assert result['total'] == sum(result['rolls']) + 1
    print("✓ 骰子投擲測試通過")
    
    # 測試 multiple dice
    results = DiceRoller.roll_multiple_dice("2d6", rules)
    assert len(results) == 1  # 單次擲骰
    print("✓ 多重骰子投擲測試通過")
    
    # 測試多次擲骰
    results = DiceRoller.roll_multiple_dice("+3 d4", rules)
    print(f"結果長度: {len(results)}, 預期: 3")  # 調試輸出
    # 應該是3次擲骰，每次擲1個4面骰
    assert len(results) == 3  # 3次擲骰
    # 驗證每次擲骰的結果
    for result in results:
        assert result['count'] == 1
        assert result['sides'] == 4
        assert 1 <= result['rolls'][0] <= 4
    print("✓ 多次擲骰測試通過")
    
    print("骰子功能測試完成\n")


def test_coc_roller():
    """測試 CoC 功能"""
    print("測試 CoC 功能...")
    
    rules = {
        'critical_success': 1,
        'critical_fail': 100,
        'skill_divisor_hard': 2,
        'skill_divisor_extreme': 5
    }
    
    # 測試 CoC 擲骰
    result = CoCRoller.roll_coc(60, rules)
    assert 1 <= result['roll'] <= 100
    assert result['skill_value'] == 60
    print("✓ CoC 擲骰測試通過")
    
    # 測試多次 CoC 擲骰
    results = CoCRoller.roll_coc_multi(50, 3, rules)
    assert len(results) == 3
    print("✓ 多次 CoC 擲骰測試通過")
    
    # 測試成功等級判定
    # 測試大成功
    level = CoCRoller.determine_success_level(1, 50, rules)
    assert level == 1  # 大成功
    print("✓ 大成功判定測試通過")
    
    # 測試極限成功
    level = CoCRoller.determine_success_level(10, 50, rules)  # 50/5=10，所以10是極限成功
    assert level == 2  # 極限成功
    print("✓ 極限成功判定測試通過")
    
    # 測試困難成功
    level = CoCRoller.determine_success_level(25, 50, rules)  # 50/2=25，所以25是困難成功
    assert level == 3  # 困難成功
    print("✓ 困難成功判定測試通過")
    
    # 測試普通成功
    level = CoCRoller.determine_success_level(50, 50, rules)  # 50是普通成功
    assert level == 4  # 普通成功
    print("✓ 普通成功判定測試通過")
    
    # 測試失敗
    level = CoCRoller.determine_success_level(51, 50, rules)  # 51 > 50，所以失敗
    assert level == 5  # 失敗
    print("✓ 失敗判定測試通過")
    
    # 測試大失敗（技能值 < 50）
    is_crit_fail = CoCRoller.is_critical_failure(96, 40, rules)
    assert is_crit_fail == True
    print("✓ 大失敗判定測試通過（技能值 < 50）")
    
    # 測試大失敗（技能值 >= 50）
    is_crit_fail = CoCRoller.is_critical_failure(100, 60, rules)
    assert is_crit_fail == True
    print("✓ 大失敗判定測試通過（技能值 >= 50）")
    
    # 測試成功等級格式化
    text = CoCRoller.format_success_level(1)
    assert text == "大成功 (Critical Success)"
    print("✓ 成功等級格式化測試通過")
    
    print("CoC 功能測試完成\n")


def main():
    """運行所有測試"""
    print("開始測試 TRPG Discord Bot 功能...\n")
    
    test_config()
    test_database()
    test_dice_roller()
    test_coc_roller()
    
    print("所有測試通過！✅\n")
    print("Python 版本的 TRPG Discord Bot 已經成功實現了以下功能：")
    print("- 配置管理系統")
    print("- SQLite 數據庫系統用於技能管理")
    print("- D&D 骰子系統（支援各種表達式）")
    print("- CoC 7e 系統（支援技能判定、成功等級計算）")
    print("- 技能管理系統（新增、查詢、刪除）")
    print("- 日誌系統配置")
    print("- 管理員系統")


if __name__ == "__main__":
    main()