import sqlite3
from datetime import datetime
from pathlib import Path

class Database:
    def __init__(self):
        # Создаём директорию для базы данных, если её нет
        db_dir = Path(__file__).parent / 'data'
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Путь к файлу базы данных
        self.db_path = db_dir / 'spotlight_bot.db'
        self.create_tables()
        
    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Сначала удалим старую таблицу если она существует
            cursor.execute('DROP TABLE IF EXISTS users')
            
            # Создаем таблицу пользователей с правильной структурой
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Создаем таблицы для тестов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_questions (
                    id INTEGER PRIMARY KEY,
                    module_id INTEGER,
                    question_text TEXT,
                    FOREIGN KEY (module_id) REFERENCES modules(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_answers (
                    id INTEGER PRIMARY KEY,
                    question_id INTEGER,
                    answer_text TEXT,
                    is_correct BOOLEAN,
                    FOREIGN KEY (question_id) REFERENCES test_questions(id)
                )
            ''')
            
            # Таблица статистики пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_statistics (
                    user_id INTEGER PRIMARY KEY,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    words_learned INTEGER DEFAULT 0,
                    exercises_completed INTEGER DEFAULT 0,
                    streak_days INTEGER DEFAULT 0,
                    last_activity_date DATE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Таблица достижений пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_achievements (
                    user_id INTEGER,
                    achievement_id TEXT,
                    earned_at TIMESTAMP,
                    PRIMARY KEY (user_id, achievement_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            conn.commit()

    def get_module_test_questions(self, module_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Получаем все вопросы для модуля с их ответами
            cursor.execute('''
                SELECT q.id, q.question_text, a.id, a.answer_text, a.is_correct
                FROM test_questions q
                LEFT JOIN test_answers a ON q.id = a.question_id
                WHERE q.module_id = ?
                ORDER BY q.id, a.id
            ''', (module_id,))
            
            rows = cursor.fetchall()
            
            # Форматируем данные в удобную структуру
            questions = {}
            for row in rows:
                q_id, q_text, a_id, a_text, is_correct = row
                
                if q_id not in questions:
                    questions[q_id] = {
                        'id': q_id,
                        'text': q_text,
                        'answers': []
                    }
                
                if a_id is not None:
                    questions[q_id]['answers'].append({
                        'id': a_id,
                        'text': a_text,
                        'is_correct': bool(is_correct)
                    })
            
            return list(questions.values())

    def add_test_question(self, module_id: int, question_text: str, answers: list):
        """
        Добавляет новый вопрос с ответами
        answers должен быть списком кортежей (текст_ответа, правильный_ли)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Добавляем вопрос
            cursor.execute('''
                INSERT INTO test_questions (module_id, question_text)
                VALUES (?, ?)
            ''', (module_id, question_text))
            
            question_id = cursor.lastrowid
            
            # Добавляем ответы
            for answer_text, is_correct in answers:
                cursor.execute('''
                    INSERT INTO test_answers (question_id, answer_text, is_correct)
                    VALUES (?, ?, ?)
                ''', (question_id, answer_text, is_correct))
            
            conn.commit()

    def user_exists(self, user_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
            return cursor.fetchone() is not None

    def add_user(self, user_id: int, username: str = None, first_name: str = None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, username, first_name)
                VALUES (?, ?, ?)
            ''', (user_id, username, first_name))
            conn.commit()

    def get_user(self, user_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            return cursor.fetchone()

    async def get_user_xp(self, user_id: int) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT xp FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0

    def get_user_level(self, user_id: int) -> int:
        cursor = self.conn.cursor()
        cursor.execute('SELECT level FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 1

    def update_user_xp(self, user_id: int, xp: int):
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE users SET points = ? WHERE user_id = ?',
            (xp, user_id)
        )
        self.conn.commit()

    def update_user_level(self, user_id: int, level: int):
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE users SET level = ? WHERE user_id = ?',
            (level, user_id)
        )
        self.conn.commit()

    def has_achievement(self, user_id: int, achievement_id: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT 1 FROM achievements WHERE user_id = ? AND achievement_id = ?',
            (user_id, achievement_id)
        )
        return cursor.fetchone() is not None

    def add_achievement(self, user_id: int, achievement_id: str):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO achievements (user_id, achievement_id, earned_at) VALUES (?, ?, ?)',
            (user_id, achievement_id, datetime.now())
        )
        self.conn.commit()

    def get_streak(self, user_id: int) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT streak_days FROM users WHERE user_id = ?',
            (user_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else 0

    def update_streak(self, user_id: int, streak: int):
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE users SET streak_days = ? WHERE user_id = ?',
            (streak, user_id)
        )
        self.conn.commit()

    def add_sample_test_questions(self):
        """Добавление тестовых вопросов"""
        test_questions = [
            {
                'module_id': 1,
                'question': 'What is the correct form of "to be" in present simple?',
                'answers': [
                    ('I am', True),
                    ('I is', False),
                    ('I are', False),
                    ('I be', False)
                ]
            },
            # Добавьте больше вопросов по необходимости
        ]
        
        for q in test_questions:
            self.add_test_question(q['module_id'], q['question'], q['answers'])

# Скрипт для заполнения базы тестовыми данными
def add_sample_data(db: Database):
    # Пример добавления вопроса для модуля 1
    question = "What is the correct form of 'to be' in present simple?"
    answers = [
        ("I is", False),
        ("I am", True),
        ("I are", False),
        ("I be", False)
    ]
    db.add_test_question(1, question, answers)

# Запустите эту функцию один раз для заполнения базы данных
if __name__ == "__main__":
    db = Database()
    add_sample_data(db)