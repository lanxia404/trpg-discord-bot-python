import random
import re
from typing import Dict, List, Optional, Tuple, Any


# Dice rolling utilities
class DiceRoller:
    @staticmethod
    def parse_dice_expr(expr: str, rules: Dict[str, Any]) -> Tuple[int, int, int, Optional[Tuple[str, int]]]:
        """
        Parse a dice expression like "2d6+1" or "d20>=15"
        Returns: (count, sides, modifier, comparison)
        """
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
        return random.randint(1, sides)

    @staticmethod
    def roll_dice(count: int, sides: int, modifier: int, comparison: Optional[Tuple[str, int]] = None) -> Dict[str, Any]:
        """Roll multiple dice and return results"""
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