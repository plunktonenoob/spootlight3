from typing import List, Dict, Optional
from database import Database

class GamificationManager:
    def __init__(self, db: Database):
        self.db = db
        self.xp_rewards = {
            'word_learned': 10,
            'exercise_completed': 20,
            'test_completed': 50,
            'achievement_earned': 100,
            'daily_streak': 30,
            'perfect_score': 40
        }
        
        self.level_thresholds = {
            1: 0,
            2: 100,
            3: 250,
            4: 500,
            5: 1000,
            6: 2000,
            7: 3500,
            8: 5000,
            9: 7500,
            10: 10000
        }
        
        self.achievements = {
            'first_word': {
                'id': 1,
                'name': 'Первое слово',
                'description': 'Выучите первое слово',
                'xp_reward': 50
            },
            'word_collector': {
                'id': 2,
                'name': 'Коллекционер слов',
                'description': 'Выучите 50 слов',
                'xp_reward': 200
            },
            'perfect_test': {
                'id': 3,
                'name': 'Отличник',
                'description': 'Получите 100% за т��ст',
                'xp_reward': 150
            },
            'streak_week': {
                'id': 4,
                'name': 'Недельная серия',
                'description': 'Занимайтесь 7 дней подряд',
                'xp_reward': 300
            }
        }
    
    async def award_xp(self, user_id: int, action: str) -> Dict:
        """Начисление опыта за действие"""
        xp = self.xp_rewards.get(action, 0)
        if xp > 0:
            current_xp = await self.db.get_user_xp(user_id)
            new_xp = current_xp + xp
            
            # Проверяем, достиг ли пользователь нового уровня
            current_level = await self.db.get_user_level(user_id)
            new_level = self.calculate_level(new_xp)
            
            await self.db.update_user_xp(user_id, new_xp)
            
            result = {
                'xp_gained': xp,
                'total_xp': new_xp,
                'level_up': new_level > current_level,
                'new_level': new_level if new_level > current_level else None
            }
            
            if result['level_up']:
                await self.db.update_user_level(user_id, new_level)
            
            return result
        return {'xp_gained': 0, 'level_up': False}
    
    def calculate_level(self, xp: int) -> int:
        """Расчет уровня на основе опыта"""
        for level, threshold in sorted(self.level_thresholds.items(), reverse=True):
            if xp >= threshold:
                return level
        return 1
    
    async def check_achievements(self, user_id: int) -> List[Dict]:
        """Проверка и начисление достижений"""
        user_stats = await self.db.get_user_statistics(user_id)
        earned_achievements = []
        
        # Проверяем каждое достижение
        if user_stats['words_learned'] == 1:
            earned_achievements.append(
                await self.award_achievement(user_id, 'first_word')
            )
        
        if user_stats['words_learned'] >= 50:
            earned_achievements.append(
                await self.award_achievement(user_id, 'word_collector')
            )
        
        if user_stats['perfect_tests'] > 0:
            earned_achievements.append(
                await self.award_achievement(user_id, 'perfect_test')
            )
        
        if user_stats['streak_days'] >= 7:
            earned_achievements.append(
                await self.award_achievement(user_id, 'streak_week')
            )
        
        return [a for a in earned_achievements if a is not None]
    
    async def award_achievement(self, user_id: int, achievement_id: str) -> Optional[Dict]:
        """Начисление достижения пользователю"""
        if not await self.db.has_achievement(user_id, achievement_id):
            achievement = self.achievements[achievement_id]
            await self.db.add_achievement(user_id, achievement_id)
            await self.award_xp(user_id, 'achievement_earned')
            return {
                'id': achievement_id,
                'name': achievement['name'],
                'description': achievement['description'],
                'xp_reward': achievement['xp_reward']
            }
        return None
    
    async def update_streak(self, user_id: int) -> Dict:
        """Обновление серии ежедневных занятий"""
        last_activity = await self.db.get_last_activity(user_id)
        current_streak = await self.db.get_streak(user_id)
        
        if self.is_streak_continued(last_activity):
            current_streak += 1
            await self.db.update_streak(user_id, current_streak)
            await self.award_xp(user_id, 'daily_streak')
            return {'streak': current_streak, 'maintained': True}
        else:
            await self.db.update_streak(user_id, 1)
            return {'streak': 1, 'maintained': False} 