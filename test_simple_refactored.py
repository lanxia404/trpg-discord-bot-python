#!/usr/bin/env python3
"""
測試重構後的 TRPG Discord Bot 架構 - 簡化版
"""

def test_refactored_structure():
    """測試重構後的架構是否正常工作"""
    print("測試重構後的 TRPG Discord Bot 架構...")
    
    # 測試各個獨立模組（使用新的目錄結構）
    try:
        from models.config import ConfigManager
        print("✓ Config 模組導入成功")
    except ImportError as e:
        print(f"✗ Config 模組導入失敗: {e}")
        return False
    
    try:
        from models.database import SkillsDB
        print("✓ Database 模組導入成功")
    except ImportError as e:
        print(f"✗ Database 模組導入失敗: {e}")
        return False
    
    try:
        from core.dice_roller import DiceRoller
        print("✓ Dice Roller 模組導入成功")
    except ImportError as e:
        print(f"✗ Dice Roller 模組導入失敗: {e}")
        return False
    
    try:
        from core.coc_roller import CoCRoller
        print("✓ CoC Roller 模組導入成功")
    except ImportError as e:
        print(f"✗ CoC Roller 模組導入失敗: {e}")
        return False
    
    try:
        from utils.bot import TRPGDiscordBot
        print("✓ Bot 模組導入成功")
    except ImportError as e:
        print(f"✗ Bot 模組導入失敗: {e}")
        return False
    
    # 測試功能是否正常工作
    print("\n測試各模組功能...")
    
    # 測試配置管理
    config_manager = ConfigManager("test_refactored_config.json")
    original_devs = config_manager.global_config.developers[:]
    config_manager.global_config.developers = [123456789]
    config_manager.save_config()
    
    # 重新載入確認保存成功
    new_manager = ConfigManager("test_refactored_config.json")
    assert 123456789 in new_manager.global_config.developers
    print("✓ 配置管理功能正常")
    
    # 測試數據庫
    db = SkillsDB("test_refactored_skills.db")
    success = db.add_skill(12345, "重構測試技能", "法術", "高級", "測試效果")
    assert success, "添加技能失敗"
    
    skill = db.find_skill(12345, "重構測試技能")
    assert skill is not None and skill['name'] == "重構測試技能", "查找技能失敗"
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
    if os.path.exists("test_refactored_config.json"):
        os.remove("test_refactored_config.json")
    if os.path.exists("test_refactored_skills.db"):
        os.remove("test_refactored_skills.db")
    
    print("\n✓ 所有重構後的功能測試通過！")
    print("\n重構後的架構優勢:")
    print("- 模組化設計，易於維護")
    print("- 功能分離，降低耦合")
    print("- 清晰的架構，便於擴展")
    print("- 各組件可獨立測試")
    
    return True


if __name__ == "__main__":
    success = test_refactored_structure()
    if success:
        print("\n重構成功！✅")
    else:
        print("\n重構失敗！❌")