#!/usr/bin/env python3
"""
測試重構後的 TRPG Discord Bot 架構
"""

def test_imports():
    """測試所有模組是否可以正確導入"""
    print("測試模組導入...")
    
    try:
        from models.config import GlobalConfig, GuildConfig, ConfigManager
        print("✓ config 模組導入成功")
    except ImportError as e:
        print(f"✗ config 模組導入失敗: {e}")
        return False
        
    try:
        from models.database import SkillsDB
        print("✓ database 模組導入成功")
    except ImportError as e:
        print(f"✗ database 模組導入失敗: {e}")
        return False
        
    try:
        from core.dice_roller import DiceRoller
        print("✓ dice_roller 模組導入成功")
    except ImportError as e:
        print(f"✗ dice_roller 模組導入失敗: {e}")
        return False
        
    try:
        from core.coc_roller import CoCRoller
        print("✓ coc_roller 模組導入成功")
    except ImportError as e:
        print(f"✗ coc_roller 模組導入失敗: {e}")
        return False
        
    try:
        from utils.bot import TRPGDiscordBot
        print("✓ bot 模組導入成功")
    except ImportError as e:
        print(f"✗ bot 模組導入失敗: {e}")
        return False
        
    try:
        from cogs.dice_commands import DiceCommands
        print("✓ dice_commands cog 導入成功")
    except ImportError as e:
        print(f"✗ dice_commands cog 導入失敗: {e}")
        return False
        
    try:
        from cogs.skill_commands import SkillCommands
        print("✓ skill_commands cog 導入成功")
    except ImportError as e:
        print(f"✗ skill_commands cog 導入失敗: {e}")
        return False
        
    try:
        from cogs.log_commands import LogCommands
        print("✓ log_commands cog 導入成功")
    except ImportError as e:
        print(f"✗ log_commands cog 導入失敗: {e}")
        return False
        
    try:
        from cogs.admin_commands import AdminCommands
        print("✓ admin_commands cog 導入成功")
    except ImportError as e:
        print(f"✗ admin_commands cog 導入失敗: {e}")
        return False
        
    try:
        from cogs.help_commands import HelpCommands
        print("✓ help_commands cog 導入成功")
    except ImportError as e:
        print(f"✗ help_commands cog 導入失敗: {e}")
        return False
    
    return True


def test_functionality():
    """測試各個模組的基本功能"""
    print("\n測試基本功能...")
    
    # 測試配置管理
    try:
        from config import ConfigManager
        config_manager = ConfigManager("test_config.json")
        config_manager.global_config.developers = [123456789]
        config_manager.save_config()
        print("✓ 配置管理功能正常")
    except Exception as e:
        print(f"✗ 配置管理功能異常: {e}")
        return False
    
    # 測試數據庫
    try:
        from database import SkillsDB
        db = SkillsDB("test_skills.db")
        success = db.add_skill(12345, "測試技能", "法術", "高級", "測試效果")
        assert success, "添加技能失敗"
        print("✓ 數據庫功能正常")
    except Exception as e:
        print(f"✗ 數據庫功能異常: {e}")
        return False
    
    # 測試骰子功能
    try:
        from dice_roller import DiceRoller
        rules = {
            'critical_success': 20,
            'critical_fail': 1,
            'max_dice_count': 50,
            'max_dice_sides': 1000
        }
        result = DiceRoller.roll_multiple_dice("2d6", rules)
        assert len(result) == 1, "骰子擲骰結果異常"
        print("✓ 骰子功能正常")
    except Exception as e:
        print(f"✗ 骰子功能異常: {e}")
        return False
    
    # 測試CoC功能
    try:
        from coc_roller import CoCRoller
        result = CoCRoller.roll_coc(50, {
            'critical_success': 1,
            'critical_fail': 100,
            'skill_divisor_hard': 2,
            'skill_divisor_extreme': 5
        })
        assert 'roll' in result, "CoC擲骰結果異常"
        print("✓ CoC功能正常")
    except Exception as e:
        print(f"✗ CoC功能異常: {e}")
        return False
    
    return True


def main():
    """主測試函數"""
    print("開始測試重構後的 TRPG Discord Bot 架構...\n")
    
    import_success = test_imports()
    if not import_success:
        print("\n模組導入失敗，停止測試")
        return False
    
    functionality_success = test_functionality()
    if not functionality_success:
        print("\n功能測試失敗")
        return False
    
    print("\n✓ 所有測試通過！重構後的架構運行正常")
    print("\n重構後的模組結構：")
    print("- main.py: 程式入口點")
    print("- bot.py: 機器人類定義")
    print("- config.py: 配置管理相關類別")
    print("- database.py: 數據庫操作類別")
    print("- dice_roller.py: D&D骰子系統")
    print("- coc_roller.py: CoC系統")
    print("- command_cogs/: 指令cog目錄")
    print("  - dice_commands.py: 骰子指令")
    print("  - skill_commands.py: 技能指令")
    print("  - log_commands.py: 日誌指令")
    print("  - admin_commands.py: 管理指令")
    print("  - help_commands.py: 幫助指令")
    
    # 清理測試文件
    import os
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")
    if os.path.exists("test_skills.db"):
        os.remove("test_skills.db")
    
    print("\n✓ 清理完成")


if __name__ == "__main__":
    main()