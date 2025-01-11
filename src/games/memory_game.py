from typing import List, Dict, Optional
import random

class MemoryGame:
    def __init__(self):
        self.cards: List[Dict] = []
        self.flipped_cards: List[int] = []  # Индексы открытых карт
        self.matched_pairs: List[int] = []  # Индексы сопоставленных пар
        self.score: int = 0
        self.moves: int = 0
        self.game_over: bool = False
        
    def initialize_game(self, word_pairs: List[Dict[str, str]]) -> None:
        """Инициализация игры с парами слов"""
        self.cards = []
        self.flipped_cards = []
        self.matched_pairs = []
        self.score = 0
        self.moves = 0
        self.game_over = False
        
        # Создаем карты из пар слов
        for i, pair in enumerate(word_pairs):
            # Добавляем английское слово
            self.cards.append({
                'id': i * 2,
                'type': 'en',
                'value': pair['word'],
                'translation': pair['translation'],
                'is_flipped': False,
                'is_matched': False
            })
            # Добавляем перевод
            self.cards.append({
                'id': i * 2 + 1,
                'type': 'ru',
                'value': pair['translation'],
                'translation': pair['word'],
                'is_flipped': False,
                'is_matched': False
            })
        
        # Перемешиваем карты
        random.shuffle(self.cards)
    
    def flip_card(self, card_index: int) -> Dict:
        """Переворачивает карту и проверяет совпадения"""
        if card_index >= len(self.cards) or self.cards[card_index]['is_matched']:
            return {'success': False, 'message': 'Недопустимый ход'}
        
        if len(self.flipped_cards) >= 2:
            # Сначала переворачиваем предыдущие карты обратно, если они не совпали
            self.reset_flipped_cards()
        
        if card_index in self.flipped_cards:
            return {'success': False, 'message': 'Карта уже открыта'}
        
        self.cards[card_index]['is_flipped'] = True
        self.flipped_cards.append(card_index)
        
        result = {
            'success': True,
            'card': self.cards[card_index],
            'is_pair_complete': False,
            'is_match': False
        }
        
        # Если открыты две карты, проверяем совпадение
        if len(self.flipped_cards) == 2:
            self.moves += 1
            card1 = self.cards[self.flipped_cards[0]]
            card2 = self.cards[self.flipped_cards[1]]
            
            # Проверяем, образуют ли карты пару
            is_match = (
                (card1['type'] == 'en' and card2['type'] == 'ru' and 
                 card1['value'] == card2['translation']) or
                (card1['type'] == 'ru' and card2['type'] == 'en' and 
                 card1['translation'] == card2['value'])
            )
            
            if is_match:
                self.score += 10
                card1['is_matched'] = True
                card2['is_matched'] = True
                self.matched_pairs.extend(self.flipped_cards)
                result['is_match'] = True
                
                # Очищаем список открытых карт после нахождения пары
                self.flipped_cards = []
                
                # Проверяем, закончена ли игра
                if len(self.matched_pairs) == len(self.cards):
                    self.game_over = True
                    result['game_over'] = True
                    result['final_score'] = self.calculate_final_score()
            
            result['is_pair_complete'] = True
        
        return result
    
    def reset_flipped_cards(self) -> None:
        """Переворачивает карты обратно"""
        for index in self.flipped_cards:
            if not self.cards[index]['is_matched']:
                self.cards[index]['is_flipped'] = False
        self.flipped_cards = []  # Очищаем список открытых карт
    
    def calculate_final_score(self) -> int:
        """Рассчитывает финальный счет на основе ходов и времени"""
        base_score = self.score
        moves_penalty = max(0, (self.moves - len(self.cards)) * 2)
        return max(0, base_score - moves_penalty)
    
    def get_game_state(self) -> Dict:
        """Возвращает текущее состояние игры"""
        return {
            'cards': self.cards,
            'score': self.score,
            'moves': self.moves,
            'game_over': self.game_over,
            'matched_pairs': len(self.matched_pairs) // 2,
            'total_pairs': len(self.cards) // 2
        } 