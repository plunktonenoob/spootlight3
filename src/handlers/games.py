from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import random
import logging
import os
from pathlib import Path

# Добавляем путь к корневой директории проекта в PYTHONPATH
import sys
src_path = str(Path(__file__).parent.parent.absolute())
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Теперь импортируем модули
from games.memory_game import MemoryGame
from games.word_builder_game import WordBuilderGame
from games.quiz_game import QuizGame
from data.module1.vocabulary import VOCABULARY

# Инициализация логгера
logger = logging.getLogger(__name__)

GAMES = {
    'quiz': 'Викторина',
    'memory': 'Найди пару',
    'word': 'Составь слово'
}

async def handle_games(update: Update, context):
    query = update.callback_query
    keyboard = []
    
    for game_id, game_name in GAMES.items():
        keyboard.append([
            InlineKeyboardButton(
                f"🎮 {game_name}", 
                callback_data=f"game_{game_id}"
            )
        ])
    
    keyboard.extend([
        [
            InlineKeyboardButton("🏆 Таблица лидеров", callback_data="game_leaderboard"),
            InlineKeyboardButton("🎯 Достижения", callback_data="game_achievements")
        ],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "🎮 Игры\n"
        "Выберите игру:",
        reply_markup=reply_markup
    )

async def start_game(update: Update, context: CallbackContext, game_id: str):
    """Запуск выбранной игры"""
    query = update.callback_query
    await query.answer()
    
    try:
        logger.info(f"Запуск игры с id: {game_id}")

        if game_id == 'memory':
            logger.info("Запуск игры 'Найди пару'")
            await handle_memory_game(update, context)
        elif game_id == 'word':
            logger.info("Запуск игры 'Составь слово'")
            await handle_word_builder_game(update, context)
        elif game_id == 'quiz':
            logger.info("Запуск игры 'Викторина'")
            await handle_quiz_game(update, context)
        else:
            logger.info(f"Игра {game_id} находится в разработке")
            keyboard = [[InlineKeyboardButton("🔙 К играм", callback_data="games")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"🎮 {GAMES[game_id]}\n\n"
                "Эта игра находится в разработке.",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Ошибка при запуске игры {game_id}: {e}")
        await query.message.reply_text(
            "Произошла ошибка при запуске игры. Пожалуйста, попробуйте еще раз."
        )

async def handle_memory_game(update: Update, context: CallbackContext):
    """Обработчик игры 'Найди пару'"""
    query = update.callback_query
    await query.answer()
    
    if 'memory_game' not in context.user_data:
        # Инициализируем новую игру
        game = MemoryGame()
        
        # Получаем случайные пары слов из словаря
        word_pairs = []
        for category in VOCABULARY.values():
            word_pairs.extend([
                {'word': word['word'], 'translation': word['translation']}
                for word in category['words']
            ])
        
        # Выбираем 6 случайных пар
        selected_pairs = random.sample(word_pairs, 6)
        game.initialize_game(selected_pairs)
        context.user_data['memory_game'] = game
    else:
        game = context.user_data['memory_game']
    
    # Формируем клавиатуру с картами
    keyboard = []
    current_row = []
    
    for i, card in enumerate(game.cards):
        if card['is_matched']:
            # Для сопоставленн��х пар показываем ✅
            button_text = "✅"
        elif card['is_flipped']:
            # Для открытых карт показываем значение
            button_text = card['value']
        else:
            # Для закрытых карт показываем 🎴
            button_text = "🎴"
        
        current_row.append(InlineKeyboardButton(
            button_text,
            callback_data=f"memory_flip_{i}"
        ))
        
        # Формируем ряды по 3 кнопки
        if len(current_row) == 3:
            keyboard.append(current_row)
            current_row = []
    
    if current_row:  # Добавляем оставшиеся кнопки
        keyboard.append(current_row)
    
    # Добавляем кнопки управления
    keyboard.append([
        InlineKeyboardButton("🔄 Новая игра", callback_data="memory_new"),
        InlineKeyboardButton("🔙 К играм", callback_data="games")
    ])
    
    game_state = game.get_game_state()
    text = (
        "🎮 Найди пару\n\n"
        "Найдите пары: английское слово и его перевод\n\n"
        f"Очки: {game_state['score']}\n"
        f"Ходы: {game_state['moves']}\n"
        f"Найдено пар: {game_state['matched_pairs']}/{game_state['total_pairs']}"
    )
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def handle_memory_flip(update: Update, context: CallbackContext, card_index: int):
    """Обработчик переворота карты"""
    query = update.callback_query
    await query.answer()
    
    game = context.user_data.get('memory_game')
    if not game:
        await handle_memory_game(update, context)
        return
    
    result = game.flip_card(card_index)
    
    if result['success']:
        # Показываем обновленное состояние игры
        await handle_memory_game(update, context)
        
        if result.get('is_pair_complete'):
            # Если открыты две карты, даем время на их просмотр
            # и затем либо оставляем открытыми (если совпали),
            # либо переворачиваем обратно
            if not result.get('is_match'):
                game.reset_flipped_cards()
                await handle_memory_game(update, context)
            
            if result.get('game_over'):
                # Игра завершена, показываем результаты
                final_score = result['final_score']
                keyboard = [[
                    InlineKeyboardButton("🔄 Новая игра", callback_data="memory_new"),
                    InlineKeyboardButton("🔙 К играм", callback_data="games")
                ]]
                await query.edit_message_text(
                    f"🎮 Игра завершена!\n\n"
                    f"Финальный счет: {final_score}\n"
                    f"Количество ходов: {game.moves}\n\n"
                    "Хотите сыграть еще раз?",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                ) 

async def handle_word_builder_game(update: Update, context: CallbackContext):
    """Обработчик игры 'Составь слово'"""
    query = update.callback_query
    await query.answer()
    
    try:
        logger.info("Запуск игры 'Составь слово'")
        
        if 'word_builder_game' not in context.user_data:
            logger.info("Инициализация новой игры")
            game = WordBuilderGame()
            game.initialize_game()
            context.user_data['word_builder_game'] = game
        else:
            logger.info("Продолжение существующей игры")
            game = context.user_data['word_builder_game']
        
        game_state = game.get_game_state()
        logger.info(f"Текущее состояние игры: {game_state}")
        
        # Формируем клавиатуру с буквами
        keyboard = []
        current_row = []
        
        # Показываем буквы для выбора
        for i, letter in enumerate(game_state['shuffled_letters']):
            if i in game_state['selected_letters']:
                # Уже выбранные буквы показываем серым
                button_text = f"[{letter.upper()}]"
            else:
                button_text = letter.upper()
            
            current_row.append(InlineKeyboardButton(
                button_text,
                callback_data=f"word_select_{i}"
            ))
            
            # Формируем ряды по 4 кнопки
            if len(current_row) == 4:
                keyboard.append(current_row)
                current_row = []
        
        if current_row:  # Добавляем оставшиеся кнопки
            keyboard.append(current_row)
        
        # Добавляем подсказку и управление
        keyboard.extend([
            [InlineKeyboardButton("🔄 Сбросить", callback_data="word_reset")],
            [
                InlineKeyboardButton("🔄 Новая игра", callback_data="word_new"),
                InlineKeyboardButton("🔙 К играм", callback_data="games")
            ]
        ])
        
        # Формируем текст состояния игры
        text = (
            "🎮 Составь слово\n\n"
            f"Составьте слово из {game_state['word_length']} букв\n"
            f"Подсказка: {game_state['translation']}\n\n"
            f"Текущая попытка: {game_state['current_word'].upper() or '...'}\n"
            f"Попытка: {game_state['attempts'] + 1}/{game_state['max_attempts']}\n"
            f"Очки: {game_state['score']}\n"
            f"Собрано слов: {game_state['words_completed']}"
        )
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в игре 'Составь слово': {e}")
        await query.message.reply_text(
            "Произошла ошибка при запуске игры. Пожалуйста, попробуйте еще раз."
        )

async def handle_word_builder_select(update: Update, context: CallbackContext, letter_index: int):
    """Обработчик выбора буквы"""
    query = update.callback_query
    await query.answer()
    
    game = context.user_data.get('word_builder_game')
    if not game:
        await handle_word_builder_game(update, context)
        return
    
    result = game.select_letter(letter_index)
    
    if result['success']:
        if result.get('is_complete'):
            if result['is_correct']:
                # Слово собрано правильно
                await query.answer(
                    f"✅ Правильно! +{result['score']} очков",
                    show_alert=True
                )
            else:
                # Слово собрано неправильно
                await query.answer(
                    f"❌ Неправильно! Осталось попыток: {result['attempts_left']}",
                    show_alert=True
                )
                
                if result.get('game_over'):
                    # Игра окончена
                    keyboard = [[
                        InlineKeyboardButton("🔄 Новая игра", callback_data="word_new"),
                        InlineKeyboardButton("🔙 К играм", callback_data="games")
                    ]]
                    await query.edit_message_text(
                        f"🎮 Игра окончена!\n\n"
                        f"Финальный счет: {result['final_score']}\n"
                        f"Собрано слов: {result['words_completed']}\n\n"
                        "Хотите сыграть еще раз?",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    return
    
    # Показываем обновленное состояние игры
    await handle_word_builder_game(update, context)

async def handle_quiz_game(update: Update, context: CallbackContext):
    """Обработчик игры 'Викторина'"""
    query = update.callback_query
    await query.answer()
    
    try:
        logger.info("Запуск игры 'Викторина'")
        
        if 'quiz_game' not in context.user_data:
            logger.info("Инициализация новой викторины")
            game = QuizGame()
            game.initialize_game()
            context.user_data['quiz_game'] = game
        else:
            logger.info("Продолжение существующей викторины")
            game = context.user_data['quiz_game']
        
        game_state = game.get_game_state()
        logger.info(f"Текущее состояние игры: {game_state}")
        
        if game_state['game_over']:
            # Показываем финальный экран
            keyboard = [[
                InlineKeyboardButton("🔄 Новая игра", callback_data="quiz_new"),
                InlineKeyboardButton("🔙 К играм", callback_data="games")
            ]]
            
            text = (
                "🎮 Викторина завершена!\n\n"
                f"Финальный счет: {game_state['score']}\n"
                f"Правильных ответов: {game_state['score'] // 10} из {game_state['total_questions']}\n\n"
                "Хотите сыграть еще раз?"
            )
        else:
            # Показываем текущий вопрос
            current_question = game_state['current_question']
            
            # Формируем клавиатуру с вариантами ответов
            keyboard = []
            for i, option in enumerate(current_question['options']):
                keyboard.append([
                    InlineKeyboardButton(
                        option,
                        callback_data=f"quiz_answer_{i}"
                    )
                ])
            
            keyboard.append([
                InlineKeyboardButton("🔄 Новая игра", callback_data="quiz_new"),
                InlineKeyboardButton("🔙 К играм", callback_data="games")
            ])
            
            text = (
                "🎮 Викторина\n\n"
                f"Вопрос {game_state['question_number']}/{game_state['total_questions']}\n\n"
                f"{current_question['text']}\n\n"
                f"Очки: {game_state['score']}"
            )
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в игре 'Викторина': {e}")
        await query.message.reply_text(
            "Произошла ошибка при запуске игры. Пожалуйста, попробуйте еще раз."
        )

async def handle_quiz_answer(update: Update, context: CallbackContext, answer_index: int):
    """Обработчик ответа на вопрос викторины"""
    query = update.callback_query
    await query.answer()
    
    game = context.user_data.get('quiz_game')
    if not game:
        await handle_quiz_game(update, context)
        return
    
    result = game.answer_question(answer_index)
    
    if result['success']:
        if result['is_correct']:
            await query.answer("✅ Правильно!", show_alert=True)
        else:
            await query.answer(
                f"❌ Неправильно!\nПравильный ответ: {result['correct_answer']}\n{result['explanation']}",
                show_alert=True
            )
    
    # Показываем следующий вопрос или результаты
    await handle_quiz_game(update, context)