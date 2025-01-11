import json
import os
from typing import Dict, Any
import logging
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

# Получаем путь к директории с данными
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = os.path.join(BASE_DIR, "data")
PROGRESS_FILE = os.path.join(DATA_DIR, "user_progress.json")

# Создаем директорию, если её нет
os.makedirs(DATA_DIR, exist_ok=True)

# Создаем пустой файл прогресса, если его нет
if not os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f)

def load_progress() -> Dict[str, Any]:
    """Загружает прогресс всех пользователей из файла"""
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}
    except Exception as e:
        logger.error(f"Ошибка при загрузке прогресса: {e}")
        return {}

def save_progress(progress: Dict[str, Any]) -> None:
    """Сохраняет прогресс всех пользователей в файл"""
    try:
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as file:
            json.dump(progress, file, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка при сохранении прогресса: {e}")

def get_user_progress(user_id: int) -> Dict[str, Any]:
    """Получает прогресс конкретного пользователя"""
    progress = load_progress()
    return progress.get(str(user_id), {})

def update_user_progress(user_id: int, data: Dict[str, Any]) -> None:
    """Обновляет прогресс конкретного пользователя"""
    progress = load_progress()
    if str(user_id) not in progress:
        progress[str(user_id)] = {}
    progress[str(user_id)].update(data)
    save_progress(progress)

def get_user_name(user_id: int) -> str:
    """Получает имя пользователя"""
    try:
        progress = get_user_progress(user_id)
        name = progress.get('name', '')
        logger.info(f"Получено имя {name} для пользователя {user_id}")
        return name
    except Exception as e:
        logger.error(f"Ошибка при получении имени: {e}")
        logger.exception("Полный стек ошибки:")
        return ''

def save_user_name(user_id: int, name: str) -> None:
    """Сохраняет имя пользователя"""
    logger.info(f"Сохранение имени {name} для пользователя {user_id}")
    try:
        update_user_progress(user_id, {'name': name})
        logger.info(f"Имя успешно сохранено")
    except Exception as e:
        logger.error(f"Ошибка при сохранении имени: {e}")
        logger.exception("Полный стек ошибки:")

async def handle_progress(update: Update, context: CallbackContext) -> None:
    """Обработчик для просмотра прогресса пользователя"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_progress = get_user_progress(user_id)
    user_name = user_progress.get('name', 'Пользователь')
    
    # Формируем текст с информацией о прогрессе
    text = f"📊 Прогресс пользователя {user_name}\n\n"
    
    # Добавляем информацию о пройденных модулях
    completed_modules = user_progress.get('completed_modules', [])
    text += "📚 Пройденные модули:\n"
    if completed_modules:
        for module in completed_modules:
            text += f"✅ Модуль {module}\n"
    else:
        text += "Пока нет пройденных модулей\n"
    
    # Добавляем статистику
    stats = user_progress.get('stats', {})
    text += "\n📈 Статистика:\n"
    text += f"• Изучено слов: {stats.get('words_learned', 0)}\n"
    text += f"• Выполнено упражнений: {stats.get('exercises_completed', 0)}\n"
    text += f"• Пройдено тестов: {stats.get('tests_completed', 0)}\n"
    
    # Добавляем кнопку возврата в главное меню
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.message.edit_text(text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Ошибка при показе прогресса: {e}")
        if "Message is not modified" not in str(e):
            await query.message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте еще раз."
            ) 