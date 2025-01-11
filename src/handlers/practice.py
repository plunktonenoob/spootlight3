from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.gamification import GamificationManager

PRACTICE_TYPES = {
    'listening': 'Аудирование',
    'speaking': 'Говорение',
    'writing': 'Письмо',
    'translation': 'Перевод',
    'sentences': 'Составление предложений'
}

async def handle_practice(update: Update, context):
    query = update.callback_query
    keyboard = []
    
    for practice_id, practice_name in PRACTICE_TYPES.items():
        keyboard.append([
            InlineKeyboardButton(
                f"✏️ {practice_name}", 
                callback_data=f"practice_{practice_id}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "🎯 Практика\n"
        "Выберите тип упражнения:",
        reply_markup=reply_markup
    )

async def start_practice_session(update: Update, context, practice_type: str):
    # Получаем задание из базы данных в зависимости от типа практики
    task = get_practice_task(practice_type)
    
    keyboard = [
        [
            InlineKeyboardButton("❌ Пропустить", callback_data="skip_task"),
            InlineKeyboardButton("✅ Проверить", callback_data="check_answer")
        ],
        [InlineKeyboardButton("🔙 К выбору практики", callback_data="practice")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        f"📝 {PRACTICE_TYPES[practice_type]}\n\n"
        f"{task['description']}\n\n"
        "Введите ваш ответ:",
        reply_markup=reply_markup
    )

async def handle_exercise_completion(update: Update, context, score: int):
    user_id = update.effective_user.id
    gamification = GamificationManager(context.bot_data['db'])
    
    # Начисляем опыт за выполнение упражнения
    xp_result = await gamification.award_xp(user_id, 'exercise_completed')
    
    # Если получен идеальный счет, начисляем дополнительный опыт
    if score == 100:
        perfect_result = await gamification.award_xp(user_id, 'perfect_score')
        xp_result['xp_gained'] += perfect_result['xp_gained']
    
    # Проверяем достижения
    new_achievements = await gamification.check_achievements(user_id)
    
    # Формируем сообщение о результатах
    text = f"🎯 Упражнение завершено!\nПолучено очков: {score}/100\n"
    text += f"Получено опыта: +{xp_result['xp_gained']} XP\n"
    
    if xp_result['level_up']:
        text += f"🎉 Поздравляем! Вы достигли уровня {xp_result['new_level']}!\n"
    
    if new_achievements:
        text += "\n🏆 Получены достижения:\n"
        for achievement in new_achievements:
            text += f"- {achievement['name']}: {achievement['description']}\n"
    
    await update.callback_query.edit_message_text(text) 