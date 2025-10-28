#!/usr/bin/env python3
"""
測試清理和重新組織後的 TRPG Discord Bot 架構 - 簡化版
"""

def test_new_structure():
    """測試新的目錄結構是否正常工作"""
    print("測試新的目錄結構...")
    
    # 測試從新目錄導入核心組件
    try:
        from utils.bot import TRPGDiscordBot
        print("✓ utils.bot 模組導入成功")
    except ImportError as e:
        print(f"✗ utils.bot 模組導入失敗: {e}")
        return False
    
    try:
        from models.config import ConfigManager, GlobalConfig, GuildConfig
        print("✓ models.config 模組導入成功")
    except ImportError as e:
        print(f"✗ models.config 模組導入失敗: {e}")
        return False
        
    try:
        from models.database import SkillsDB
        print("✓ models.database 模組導入成功")
    except ImportError as e:
        print(f"✗ models.database 模組導入失敗: {e}")
        return False
        
    try:
        from core.dice_roller import DiceRoller
        print("✓ core.dice_roller 模組導入成功")
    except ImportError as e:
        print(f"✗ core.dice_roller 模組導入失敗: {e}")
        return False
        
    try:
        from core.coc_roller import CoCRoller
        print("✓ core.coc_roller 模組導入成功")
    except ImportError as e:
        print(f"✗ core.coc_roller 模組導入失敗: {e}")
        return False

    # 測試功能是否正常
    print("\n測試各模組功能...")
    
    # 測試配置管理
    config_manager = ConfigManager("test_new_structure_config.json")
    config_manager.global_config.developers = [123456789]
    config_manager.save_config()
    
    # 重新載入確認保存成功
    new_manager = ConfigManager("test_new_structure_config.json")
    assert 123456789 in new_manager.global_config.developers
    print("✓ 配置管理功能正常")
    
    # 測試數據庫
    db = SkillsDB("test_new_structure_skills.db")
    success = db.add_skill(12345, "新結構測試技能", "法術", "高級", "測試效果")
    assert success, "添加技能失敗"
    
    skill = db.find_skill(12345, "新結構測試技能")
    assert skill is not None and skill['name'] == "新結構測試技能", "查找技能失敗"
    print("✓ 數據庫功能正常")
    
    # 測試骰子系統
    rules = {
        'critical_success': 20,
        'critical_fail': 1,
        'max_dice_count': 50,
        'max_dice_sides': 1000
    }
    result = DiceRoller.roll_multiple_dice("2d6", rules)
    assert len(result) == 1, "骰子擲骰結果異常"
    assert result[0]['count'] == 2 and result[0]['sides'] == 6, "骰子參數異常"
    print("✓ 骰子系統功能正常")
    
    # 測試CoC系統
    coc_result = CoCRoller.roll_coc(50, {
        'critical_success': 1,
        'critical_fail': 100,
        'skill_divisor_hard': 2,
        'skill_divisor_extreme': 5
    })
    assert 'roll' in coc_result and 'success_level' in coc_result, "CoC擲骰結果異常"
    print("✓ CoC系統功能正常")
    
    # 測試機器人類
    bot = TRPGDiscordBot()
    assert hasattr(bot, 'config_manager'), "機器人缺少配置管理器"
    assert hasattr(bot, 'skills_db'), "機器人缺少技能數據庫"
    print("✓ 機器人類初始化正常")
    
    # 清理測試文件
    import os
    if os.path.exists("test_new_structure_config.json"):
        os.remove("test_new_structure_config.json")
    if os.path.exists("test_new_structure_skills.db"):
        os.remove("test_new_structure_skills.db")
    
    print("\n✓ 所有新結構功能測試通過！")
    print("\n新的目錄結構：")
    print("├── cogs/           # 指令模組")
    print("│   ├── dice_commands.py")
    print("│   ├── skill_commands.py") 
    print("│   ├── log_commands.py")
    print("│   ├── admin_commands.py")
    print("│   └── help_commands.py")
    print("├── core/           # 核心邏輯")
    print("│   ├── dice_roller.py")
    print("│   └── coc_roller.py")
    print("├── models/         # 數據模型")
    print("│   ├── config.py")
    print("│   └── database.py")
    print("├── utils/          # 工具類")
    print("│   └── bot.py")
    print("├── main.py        # 程式入口點")
    print("├── requirements.txt")
    print("└── 測試文件...")
    
    return True


def main():
    success = test_new_structure()
    if success:
        print("\n✓ 目錄結構清理和重組成功！")
        print("\n改進點：")
        print("- 按功能類型組織文件，提高可維護性")
        print("- 清晰的目錄結構，便於理解和擴展")
        print("- 規範的導入路徑，避免循環依賴")
    else:
        print("\n✗ 目錄結構清理失敗！")


if __name__ == "__main__":
    main()