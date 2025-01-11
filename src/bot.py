from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    CallbackContext,
    filters
)
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from database import Database
from handlers.registration import get_registration_handler
from handlers.modules import (
    handle_modules, 
    handle_specific_module,
    handle_module_vocabulary,
    handle_module_grammar,
    handle_module_exercises,
    handle_module_test,
    handle_module_vocabulary_category,
    handle_grammar_topic,
    handle_grammar_exercise,
    handle_grammar_exercise_answer,
    handle_module_callback
)
from handlers.dictionary import (
    handle_dictionary, 
    show_word_card, 
    get_word_data,
    get_category_words_count
)
from handlers.grammar import (
    handle_grammar, 
    show_grammar_topic, 
    handle_grammar_exercise
)
from handlers.practice import handle_practice
from handlers.games import handle_games, start_game, handle_memory_game, handle_memory_flip, handle_word_builder_game, handle_word_builder_select, handle_quiz_game, handle_quiz_answer
from handlers.progress import (
    handle_progress, 
    get_user_name, 
    save_user_name,
    get_user_progress,
    update_user_progress
)
import telegram
import logging

# В начале файла добавьте настройку логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем путь к корневой директории проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем переменные окружения из корневой директории
load_dotenv(BASE_DIR / '.env')

# Получаем токен и проверяем его наличие
BOT_TOKEN = os.getenv('BOT_TOKEN')
print(f"Loaded token: {BOT_TOKEN}")  # Временно для отладки
if not BOT_TOKEN:
    raise ValueError("Не найден BOT_TOKEN. Убедитесь, что он указан в файле .env")

class SpotlightBot:
    def __init__(self):
        self.db = Database()
        
    async def start(self, update: Update, context):
        """Обработчик команды /start"""
        user_id = update.effective_user.id
        logger.info(f"Вызван метод start для пользователя {user_id}")
        
        # Создаем клавиатуру главного меню
        main_menu_keyboard = [
            [
                InlineKeyboardButton("📚 Модули", callback_data="modules"),
                InlineKeyboardButton("📖 Словарь", callback_data="dictionary")
            ],
            [
                InlineKeyboardButton("📝 Грамматика", callback_data="grammar"),
                InlineKeyboardButton("🎮 Игры", callback_data="games")
            ],
            [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
        ]
        main_menu_markup = InlineKeyboardMarkup(main_menu_keyboard)
        
        # Проверяем, есть ли уже сохраненное имя пользователя
        saved_name = get_user_name(user_id)
        logger.info(f"Сохраненное имя пользователя: {saved_name}")
        
        if update.callback_query:
            # Если это callback (переход из другого меню), всегда показываем главное меню
            message_text = "🏠 Главное меню\n\n"
            if saved_name:
                message_text = f"👋 {saved_name}, добро пожаловать в главное меню!\n\nВыберите раздел:"
            else:
                message_text += "Выберите раздел:"
            
            logger.info("Обработка callback query в start")
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                text=message_text,
                reply_markup=main_menu_markup
            )
        else:
            # Если это обычное сообщение и нет сохраненного имени
            if not saved_name:
                message_text = ("Привет! 👋 Я бот для изучения английского языка.\n"
                              "Как я могу к вам обращаться?")
                context.user_data['waiting_for_name'] = True
                reply_markup = None
            else:
                message_text = f"👋 {saved_name}, добро пожаловать!\n\nВыберите раздел:"
                reply_markup = main_menu_markup
            
            logger.info("Обработка обычного сообщения в start")
            await update.message.reply_text(
                text=message_text,
                reply_markup=reply_markup
            )

    async def handle_name_input(self, update: Update, context: CallbackContext) -> None:
        """Обработчик ввода имени пользователя"""
        if context.user_data.get('waiting_for_name'):
            user_id = update.effective_user.id
            name = update.message.text
            
            # Сохраняем имя пользователя
            save_user_name(user_id, name)
            
            # Очищаем флаг ожидания имени
            context.user_data.pop('waiting_for_name', None)
            
            keyboard = [
                [InlineKeyboardButton("📚 Модули", callback_data="modules")],
                [InlineKeyboardButton("📊 Мой прогресс", callback_data="progress")],
                [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"Приятно познакомиться, {name}! 😊\n\n"
                "Выберите раздел:",
                reply_markup=reply_markup
            )

    async def handle_callback(self, update: Update, context):
        query = update.callback_query
        callback_data = query.data
        callback_parts = callback_data.split('_')
        callback_type = callback_parts[0]

        logger.info(f"Получен callback: {callback_data}")
        logger.info(f"Части callback: {callback_parts}")
        logger.info(f"Тип callback: {callback_type}")

        try:
            if callback_type == "module":
                await handle_module_callback(update, context, callback_parts)
            elif callback_type == "modules":
                await handle_modules(update, context)
            elif callback_type == "main" or callback_data == "main_menu":
                logger.info("Переход в главное меню")
                await self.start(update, context)
            elif callback_type == "progress":
                await handle_progress(update, context)
            elif callback_type == "dictionary":
                if len(callback_parts) == 1:
                    await handle_dictionary(update, context)
                elif len(callback_parts) >= 2:
                    category_id = callback_parts[1]
                    if len(callback_parts) == 2:
                        # Показываем слова категории с индексом 0
                        await show_word_card(update, context, category_id, 0)
                    elif len(callback_parts) >= 4:
                        action = callback_parts[2]
                        word_index = int(callback_parts[3])
                        if action == "prev":
                            # Предыдущее слово
                            await show_word_card(update, context, category_id, word_index - 1)
                        elif action == "next":
                            # Следующее слово
                            await show_word_card(update, context, category_id, word_index + 1)
                        elif action == "audio":
                            # Воспроизведение аудио
                            word_data = get_word_data(category_id, word_index)
                            if word_data:
                                await query.answer(f"🔊 {word_data['word']}")
            elif callback_type == "dict":
                # Обработка callback'ов для словаря в модулях
                if len(callback_parts) >= 2:
                    category_id = callback_parts[1]
                    if len(callback_parts) == 2:
                        await handle_module_vocabulary_category(update, context, 1, category_id)
                    elif len(callback_parts) >= 4:
                        action = callback_parts[2]
                        word_index = int(callback_parts[3])
                        if action == "prev":
                            await handle_module_vocabulary_category(update, context, 1, category_id, word_index - 1)
                        elif action == "next":
                            await handle_module_vocabulary_category(update, context, 1, category_id, word_index + 1)
                        elif action == "audio":
                            word_data = get_word_data(category_id, word_index)
                            if word_data:
                                await query.answer(f"🔊 {word_data['word']}")
            elif callback_type == "grammar":
                if len(callback_parts) == 1:
                    await handle_grammar(update, context)
                else:
                    topic_id = callback_parts[1]
                    await show_grammar_topic(update, context, topic_id)
            elif callback_type == "practice":
                await handle_practice(update, context)
            elif callback_type == "games":
                await handle_games(update, context)
            elif callback_type == "memory":
                if callback_parts[1] == "new":
                    if 'memory_game' in context.user_data:
                        del context.user_data['memory_game']
                    await handle_memory_game(update, context)
                elif callback_parts[1] == "flip":
                    card_index = int(callback_parts[2])
                    await handle_memory_flip(update, context, card_index)
            elif callback_type == "word":
                if callback_parts[1] == "new":
                    if 'word_builder_game' in context.user_data:
                        del context.user_data['word_builder_game']
                    await handle_word_builder_game(update, context)
                elif callback_parts[1] == "select":
                    letter_index = int(callback_parts[2])
                    await handle_word_builder_select(update, context, letter_index)
                elif callback_parts[1] == "reset":
                    game = context.user_data.get('word_builder_game')
                    if game:
                        game.selected_letters = []
                    await handle_word_builder_game(update, context)
            elif callback_type == "quiz":
                if callback_parts[1] == "new":
                    if 'quiz_game' in context.user_data:
                        del context.user_data['quiz_game']
                    await handle_quiz_game(update, context)
                elif callback_parts[1] == "answer":
                    answer_index = int(callback_parts[2])
                    await handle_quiz_answer(update, context, answer_index)
            elif callback_type == "game":
                if len(callback_parts) >= 2:
                    game_id = callback_parts[1]
                    if game_id == "leaderboard":
                        await query.answer("Таблица лидеров в разработке")
                    elif game_id == "achievements":
                        await query.answer("Достижения в разработке")
                    else:
                        logger.info(f"Запуск игры: {game_id}")
                        await start_game(update, context, game_id)
        except Exception as e:
            logger.error(f"Ошибка при обработке callback: {e}")
            logger.exception("Полный стек ошибки:")  # Добавляем полный стек ошибки
            if "Message is not modified" not in str(e):
                await query.message.reply_text(
                    "Произошла ошибка. Пожалуйста, попробуйте еще раз."
                )

    async def handle_module_callback(self, update: Update, context: CallbackContext, callback_parts: List[str]):
        """Обработка всех callback-ов, связанных с модулями"""
        if len(callback_parts) < 2:
            return
        
        module_id = int(callback_parts[1])
        
        if len(callback_parts) == 2:
            # Показываем содержимое модуля
            await handle_specific_module(update, context, module_id)
        elif len(callback_parts) >= 3:
            # Обрабатываем разделы модуля
            section = callback_parts[2]
            if section == 'vocab':
                await handle_module_vocabulary(update, context, module_id)
            elif section == 'grammar':
                await handle_module_grammar(update, context, module_id)
            elif section == 'exercises':
                await handle_module_exercises(update, context, module_id)
            elif section == 'test':
                await handle_module_test(update, context, module_id)

    async def show_main_menu(self, update: Update, context: CallbackContext):
        keyboard = [
            [InlineKeyboardButton("📚 Модули", callback_data="modules"),
             InlineKeyboardButton("📖 Словарь", callback_data="dictionary")],
            [InlineKeyboardButton("📝 Грамматика", callback_data="grammar"),
             InlineKeyboardButton("🎮 Игры", callback_data="games")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Добро пожаловать в Spotlight 3 Helper!\n"
            "Выберите раздел для изучения:",
            reply_markup=reply_markup
        )

def main() -> None:
    bot = SpotlightBot()
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем базу данных в контекст бота
    application.bot_data['db'] = bot.db
    
    # Добавляем обработчик регистрации
    application.add_handler(get_registration_handler())
    
    # Добавляем обработчик callback-запросов для остальных действий
    application.add_handler(CallbackQueryHandler(bot.handle_callback))
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_name_input))
    
    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main() 