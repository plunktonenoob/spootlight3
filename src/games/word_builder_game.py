from typing import List, Dict, Optional
import random
from data.module1.vocabulary import VOCABULARY

class WordBuilderGame:
    def __init__(self):
        self.current_word: Dict = {}  # Текущее слово с его данными
        self.shuffled_letters: List[str] = []  # Перемешанные буквы
        self.selected_letters: List[int] = []  # Индексы выбранных букв
        self.score: int = 0
        self.attempts: int = 0
        self.max_attempts: int = 3
        self.game_over: bool = False
        self.words_completed: int = 0
        
    def initialize_game(self) -> None:
        """Инициализация новой игры"""
        self.score = 0
        self.attempts = 0
        self.game_over = False
        self.words_completed = 0
        self.selected_letters = []
        self._set_new_word()
    
    def _set_new_word(self) -> None:
        """Выбирает новое случайное слово"""
        # Собираем все слова из словаря
        all_words = []
        for category in VOCABULARY.values():
            all_words.extend([
                {
                    'word': word['word'],
                    'translation': word['translation'],
                    'transcription': word['transcription']
                }
                for word in category['words']
                if len(word['word']) >= 3  # Только слова от 3 букв
            ])
        
        # Выбираем случайное слово
        self.current_word = random.choice(all_words)
        # Перемешиваем буквы
        self.shuffled_letters = list(self.current_word['word'].lower())
        random.shuffle(self.shuffled_letters)
        self.selected_letters = []
    
    def select_letter(self, index: int) -> Dict:
        """Выбор буквы игроком"""
        if self.game_over or index >= len(self.shuffled_letters):
            return {
                'success': False,
                'message': 'Недопустимый ход'
            }
        
        if index in self.selected_letters:
            return {
                'success': False,
                'message': 'Буква уже выбрана'
            }
        
        self.selected_letters.append(index)
        current_word = self._get_current_attempt()
        
        result = {
            'success': True,
            'current_word': current_word,
            'is_complete': False,
            'is_correct': False
        }
        
        # Проверяем, собрано ли слово полностью
        if len(current_word) == len(self.current_word['word']):
            self.attempts += 1
            
            # Проверяем правильность слова
            if current_word.lower() == self.current_word['word'].lower():
                self.score += self._calculate_word_score()
                self.words_completed += 1
                result.update({
                    'is_complete': True,
                    'is_correct': True,
                    'word_data': self.current_word,
                    'score': self.score
                })
                self._set_new_word()
            else:
                # Неправильное слово
                self.selected_letters = []
                result.update({
                    'is_complete': True,
                    'is_correct': False,
                    'attempts_left': self.max_attempts - self.attempts
                })
                
                # Проверяем, закончились ли попытки
                if self.attempts >= self.max_attempts:
                    self.game_over = True
                    result['game_over'] = True
                    result['final_score'] = self.score
                    result['words_completed'] = self.words_completed
        
        return result
    
    def _get_current_attempt(self) -> str:
        """Возвращает текущую попытку составления слова"""
        return ''.join(self.shuffled_letters[i] for i in self.selected_letters)
    
    def _calculate_word_score(self) -> int:
        """Рассчитывает очки за собранное слово"""
        word_length = len(self.current_word['word'])
        base_score = word_length * 10
        attempts_bonus = (self.max_attempts - self.attempts + 1) * 5
        return base_score + attempts_bonus
    
    def get_game_state(self) -> Dict:
        """Возвращает текущее состояние игры"""
        return {
            'score': self.score,
            'attempts': self.attempts,
            'max_attempts': self.max_attempts,
            'current_word': self._get_current_attempt(),
            'shuffled_letters': self.shuffled_letters,
            'selected_letters': self.selected_letters,
            'translation': self.current_word.get('translation', ''),
            'transcription': self.current_word.get('transcription', ''),
            'word_length': len(self.current_word['word']),
            'words_completed': self.words_completed,
            'game_over': self.game_over
        } 