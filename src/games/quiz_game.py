from typing import List, Dict, Optional
import random
from data.module1.vocabulary import VOCABULARY
from data.module1.grammar import GRAMMAR_TOPICS
import logging

logger = logging.getLogger(__name__)

class QuizGame:
    def __init__(self):
        self.current_question: Dict = {}
        self.questions: List[Dict] = []
        self.current_question_index: int = 0
        self.score: int = 0
        self.total_questions: int = 10
        self.game_over: bool = False
        
    def initialize_game(self) -> None:
        """Инициализация новой игры"""
        self.score = 0
        self.current_question_index = 0
        self.game_over = False
        self._generate_questions()
        
    def _generate_questions(self) -> None:
        """Генерация вопросов для викторины"""
        try:
            self.questions = []
            
            # Вопросы на знание слов
            vocabulary_questions = self._generate_vocabulary_questions()
            # Вопросы по грамматике
            grammar_questions = self._generate_grammar_questions()
            
            # Объединяем все вопросы и перемешиваем
            all_questions = []
            
            # Добавляем вопросы, проверяя их корректность
            for q in vocabulary_questions:
                if self._is_valid_question(q):
                    all_questions.append(q)
                    
            for q in grammar_questions:
                if self._is_valid_question(q):
                    all_questions.append(q)
            
            random.shuffle(all_questions)
            
            # Выбираем нужное количество вопросов
            self.questions = all_questions[:self.total_questions]
            if self.questions:
                self.current_question = self.questions[0]
            else:
                # Если вопросов нет, создаем тестовый вопрос
                self.questions = [{
                    'type': 'test',
                    'text': 'Тестовый вопрос',
                    'options': ['A', 'B', 'C', 'D'],
                    'correct': 'A',
                    'explanation': 'Тестовый вопрос'
                }]
                self.current_question = self.questions[0]
        except Exception as e:
            logger.error(f"Ошибка при генерации вопросов: {e}")
            # Создаем тестовый вопрос в случае ошибки
            self.questions = [{
                'type': 'test',
                'text': 'Тестовый вопрос',
                'options': ['A', 'B', 'C', 'D'],
                'correct': 'A',
                'explanation': 'Тестовый вопрос'
            }]
            self.current_question = self.questions[0]
    
    def _generate_vocabulary_questions(self) -> List[Dict]:
        """Генерация вопросов по словарю"""
        questions = []
        
        # Собираем все слова из словаря
        all_words = []
        for category in VOCABULARY.values():
            all_words.extend(category['words'])
        
        # Генерируем вопросы разных типов
        for word in all_words:
            # Вопрос на перевод с английского
            questions.append({
                'type': 'translation',
                'text': f"Как переводится слово '{word['word']}'?",
                'options': self._generate_translation_options(word['translation'], all_words),
                'correct': word['translation'],
                'explanation': f"'{word['word']}' переводится как '{word['translation']}'"
            })
            
            # Вопрос а перевод с русского
            questions.append({
                'type': 'word',
                'text': f"Выберите правильный перевод слова '{word['translation']}':",
                'options': self._generate_word_options(word['word'], all_words),
                'correct': word['word'],
                'explanation': f"'{word['translation']}' на английском будет '{word['word']}'"
            })
        
        return questions
    
    def _generate_grammar_questions(self) -> List[Dict]:
        """Генерация вопросов по грамматике"""
        questions = []
        
        try:
            for topic_id, topic in GRAMMAR_TOPICS.items():
                if not isinstance(topic, dict) or 'rules' not in topic or 'examples' not in topic:
                    logger.warning(f"Пропущена тема {topic_id}: неверный формат данных")
                    continue

                # Создаем вопросы на основе правил
                for rule in topic.get('rules', []):
                    if not isinstance(rule, str) or not rule.strip():
                        continue
                        
                    examples = topic.get('examples', [])
                    if not examples:
                        continue
                        
                    try:
                        options = self._generate_grammar_options(rule, examples)
                        correct = self._get_correct_grammar_answer(rule, examples)
                        
                        if not options or not correct:
                            continue
                            
                        questions.append({
                            'type': 'grammar_rule',
                            'text': self._generate_grammar_question(rule),
                            'options': options,
                            'correct': correct,
                            'explanation': rule
                        })
                    except Exception as e:
                        logger.error(f"Ошибка при создании вопроса для правила '{rule}': {e}")
                        continue
                
                # Создаем вопросы на основе примеров
                for example in topic.get('examples', []):
                    if not isinstance(example, str) or ' - ' not in example:
                        continue
                        
                    try:
                        eng = example.split(' - ')[0]
                        options = self._generate_example_options(example)
                        
                        if not options or eng not in options:
                            continue
                            
                        questions.append({
                            'type': 'grammar_example',
                            'text': self._generate_example_question(example, topic.get('title', 'Грамматика')),
                            'options': options,
                            'correct': eng,
                            'explanation': example
                        })
                    except Exception as e:
                        logger.error(f"Ошибка при создании вопроса для примера '{example}': {e}")
                        continue
                    
        except Exception as e:
            logger.error(f"Ошибка при генерации грамматических вопросов: {e}")
        
        return questions
    
    def _generate_translation_options(self, correct: str, words: List[Dict]) -> List[str]:
        """Генерация вариантов ответов для перевода"""
        options = [correct]
        other_translations = [w['translation'] for w in words if w['translation'] != correct]
        options.extend(random.sample(other_translations, min(3, len(other_translations))))
        random.shuffle(options)
        return options
    
    def _generate_word_options(self, correct: str, words: List[Dict]) -> List[str]:
        """Генерация вариантов английских слов"""
        options = [correct]
        other_words = [w['word'] for w in words if w['word'] != correct]
        options.extend(random.sample(other_words, min(3, len(other_words))))
        random.shuffle(options)
        return options
    
    def _generate_grammar_question(self, rule: str) -> str:
        """Генерация вопроса по грамматическому правилу"""
        return f"Выберите правильный пример для правила: {rule}"
    
    def _generate_grammar_options(self, rule: str, examples: List[str]) -> List[str]:
        """Генерация вариантов ответов для грамматического вопроса"""
        try:
            # Проверяем входные данные
            if not examples:
                return []
            
            # Получаем первый пример как правильный ответ
            first_example = examples[0]
            if ' - ' not in first_example:
                return []
            
            correct = first_example.split(' - ')[0].strip()
            if not correct:
                return []
            
            options = [correct]
            
            # Собираем другие примеры для вариантов
            other_examples = []
            for ex in examples[1:]:
                if ' - ' in ex:
                    eng = ex.split(' - ')[0].strip()
                    if eng and eng != correct:
                        other_examples.append(eng)
            
            # Добавляем дополнительные варианты
            while len(options) < 4 and other_examples:
                option = other_examples.pop(0)
                if option not in options:
                    options.append(option)
            
            # Если вариантов недостаточно, генерируем неправильные
            while len(options) < 4:
                variations = self._generate_wrong_variations(correct)
                for var in variations:
                    if len(options) >= 4:
                        break
                    if var and var not in options:
                        options.append(var)
            
            random.shuffle(options)
            return options
            
        except Exception as e:
            logger.error(f"Ошибка при генерации вариантов ответа: {e}")
            return []
    
    def _get_correct_grammar_answer(self, rule: str, examples: List[str]) -> str:
        """Получение правильного ответа для грамматического вопроса"""
        try:
            return examples[0].split(' - ')[0] if ' - ' in examples[0] else examples[0]
        except:
            return examples[0] if examples else ""
    
    def _generate_example_question(self, example: str, topic: str) -> str:
        """Генерация вопроса на основе примера"""
        try:
            # Проверяем формат примера
            parts = example.split(' - ')
            if len(parts) != 2:
                # Если формат не соответствует ожидаемому, возвращаем общий вопрос
                return f"Выберите правильный вариант ({topic}):"
            
            eng, rus = parts
            return f"Как правильно сказать '{rus}' ({topic})?"
        except Exception as e:
            # В случае ошибки возвращаем общий вопрос
            return f"Выберите правильный вариант ({topic}):"
    
    def _generate_example_options(self, example: str) -> List[str]:
        """енерация вариантов ответов для примера"""
        correct = example.split(' - ')[0]
        # Генерируем неправильные варианты, изменяя правильный ответ
        options = [correct]
        wrong_options = self._generate_wrong_variations(correct)
        options.extend(wrong_options[:3])
        random.shuffle(options)
        return options
    
    def _generate_wrong_variations(self, correct: str) -> List[str]:
        """Генерация неправильных вариантов ответа"""
        variations = []
        try:
            words = correct.split()
            
            # Меняем порядок слов
            if len(words) > 1:
                shuffled = words.copy()
                random.shuffle(shuffled)
                if shuffled != words:
                    variations.append(' '.join(shuffled))
            
            # Добавляем или убираем 's' у глаголов
            if any(word.endswith('s') for word in words):
                variations.append(correct.replace('s ', ' '))
            else:
                variations.append(correct + 's')
            
            # Меняем артикли
            if 'a ' in correct:
                variations.append(correct.replace('a ', 'the '))
            elif 'the ' in correct:
                variations.append(correct.replace('the ', 'a '))
            
            # Добавляем базовые варианты если нужно больше
            if not variations:
                variations.extend([
                    f"not {correct}",
                    f"do {correct}",
                    f"does {correct}",
                    f"is {correct}"
                ])
            
            return [var for var in variations if var != correct]
            
        except Exception as e:
            logger.error(f"Ошибка при генерации вариаций: {e}")
            return [f"Option {i+1}" for i in range(3)]  # Возвращаем базовые варианты
    
    def answer_question(self, answer_index: int) -> Dict:
        """Обработка ответа на вопрос"""
        if self.game_over:
            return {
                'success': False,
                'message': 'Игра завершена'
            }
        
        current_question = self.questions[self.current_question_index]
        is_correct = current_question['options'][answer_index] == current_question['correct']
        
        result = {
            'success': True,
            'is_correct': is_correct,
            'correct_answer': current_question['correct'],
            'explanation': current_question['explanation']
        }
        
        if is_correct:
            self.score += 10
        
        self.current_question_index += 1
        if self.current_question_index >= len(self.questions):
            self.game_over = True
            result['game_over'] = True
            result['final_score'] = self.score
            result['total_questions'] = len(self.questions)
        else:
            self.current_question = self.questions[self.current_question_index]
            
        return result
    
    def get_game_state(self) -> Dict:
        """Возвращает текущее состояние игры"""
        return {
            'score': self.score,
            'current_question': self.current_question,
            'question_number': self.current_question_index + 1,
            'total_questions': len(self.questions),
            'game_over': self.game_over
        } 
    
    def _is_valid_question(self, question: Dict) -> bool:
        """Проверка корректности вопроса"""
        try:
            return all([
                'text' in question,
                'options' in question,
                'correct' in question,
                'explanation' in question,
                len(question['options']) > 0,
                question['correct'] in question['options']
            ])
        except:
            return False 