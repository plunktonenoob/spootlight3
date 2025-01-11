from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackContext
)

WAITING_NAME = 1

async def start_registration(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    db = context.application.bot_data['db']
    
    # Проверяем, зарегистрирован ли пользователь
    if db.user_exists(user_id):
        # Если пользователь уже зарегистрирован, показываем главное меню
        keyboard = [
            [InlineKeyboardButton("📚 Модули", callback_data="modules"),
             InlineKeyboardButton("📖 Словарь", callback_data="dictionary")],
            [InlineKeyboardButton("📝 Грамматика", callback_data="grammar"),
             InlineKeyboardButton("✏️ Практика", callback_data="practice")],
            [InlineKeyboardButton("🎮 Игры", callback_data="games"),
             InlineKeyboardButton("📊 Прогресс", callback_data="progress")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Добро пожаловать в Spotlight 3 Helper!\n"
            "Выберите раздел для изучения:",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
    else:
        # Если пользователь не зарегистрирован, начинаем регистрацию
        await update.message.reply_text("Давайте познакомимся! Как тебя зовут?")
        return WAITING_NAME

async def process_name(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    first_name = update.message.text
    username = update.effective_user.username
    
    db = context.application.bot_data['db']
    
    try:
        db.add_user(user_id, username, first_name)
        
        # После успешной регистрации показываем главное меню
        keyboard = [
            [InlineKeyboardButton("📚 Модули", callback_data="modules"),
             InlineKeyboardButton("📖 Словарь", callback_data="dictionary")],
            [InlineKeyboardButton("📝 Грамматика", callback_data="grammar"),
             InlineKeyboardButton("✏️ Практика", callback_data="practice")],
            [InlineKeyboardButton("🎮 Игры", callback_data="games"),
             InlineKeyboardButton("📊 Прогресс", callback_data="progress")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Приятно познакомиться, {first_name}!\n"
            "Добро пожаловать в Spotlight 3 Helper!\n"
            "Выберите раздел для изучения:",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
        
    except Exception as e:
        print(f"Ошибка при регистрации: {e}")
        await update.message.reply_text(
            "Произошла ошибка при регистрации. Пожалуйста, попробуйте "
            "снова с помощью команды /start"
        )
        return ConversationHandler.END

def get_registration_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start_registration)],
        states={
            WAITING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_name)]
        },
        fallbacks=[CommandHandler('start', start_registration)]
    )