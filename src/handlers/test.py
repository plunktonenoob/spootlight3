from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)

async def show_test_question(update: Update, context: CallbackContext):
    """Показывает текущий вопрос теста"""
    query = update.callback_query
    await query.answer()
    
    test_data = context.user_data.get('current_test')
    if not test_data:
        await query.message.reply_text("Ошибка: тест не найден")
        return
    
    current_q = test_data['current_question']
    questions = test_data['questions']
    
    if current_q >= len(questions):
        await show_test_results(update, context)
        return
        
    question = questions[current_q]
    
    keyboard = []
    for answer in question['answers']:
        keyboard.append([InlineKeyboardButton(
            answer['text'], 
            callback_data=f"test_answer_{current_q}_{answer['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("❌ Завершить тест", callback_data="test_end")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        # Отправляем новое сообщение вместо редактирования
        await query.message.reply_text(
            f"Вопрос {current_q + 1} из {len(questions)}:\n\n"
            f"{question['text']}",
            reply_markup=reply_markup
        )
        # Удаляем предыдущее сообщение
        await query.message.delete()
    except Exception as e:
        logger.error(f"Ошибка при показе вопроса: {e}")
        await query.message.reply_text(
            "Произошла ошибка при загрузке вопроса. Пожалуйста, попробуйте позже."
        ) 