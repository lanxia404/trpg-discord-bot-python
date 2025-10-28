import random
from typing import Dict, List, Any


# CoC utilities
class CoCRoller:
    @staticmethod
    def roll_coc(skill_value: int, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Roll for Call of Cthulhu 7th edition"""
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