import sqlite3
import logging
from typing import Dict, List, Optional, Any


# Initialize logging
logger = logging.getLogger('trpg_bot')
logger.setLevel(logging.INFO)


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
            logger.error(f"Error adding skill: {e}")
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
            logger.error(f"Error finding skill: {e}")
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
            logger.error(f"Error deleting skill: {e}")
            return False
        finally:
            conn.close()