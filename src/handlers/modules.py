from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from typing import List
import logging
from data.module1.vocabulary import VOCABULARY
from data.module1.grammar import GRAMMAR_TOPICS
from data.module1.exercises import GRAMMAR_EXERCISES
from gtts import gTTS
import os
import tempfile

logger = logging.getLogger(__name__)

async def handle_modules(update: Update, context):
    """Обработчик для раздела модулей"""
    query = update.callback_query
    await query.answer()

    try:
        keyboard = [
            [InlineKeyboardButton("Module 1: School Days", callback_data="module_1"),
             InlineKeyboardButton("Module 2: Family Moments", callback_data="module_2")],
            [InlineKeyboardButton("Module 3: All the Things I Like", callback_data="module_3"),
             InlineKeyboardButton("Module 4: Come in and Play!", callback_data="module_4")],
            [InlineKeyboardButton("Module 5: Furry Friends", callback_data="module_5"),
             InlineKeyboardButton("Module 6: Home Sweet Home", callback_data="module_6")],
            [InlineKeyboardButton("Module 7: A Day Off", callback_data="module_7"),
             InlineKeyboardButton("Module 8: Day by Day", callback_data="module_8")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text(
            "Выберите модуль для изучения:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Ошибка при показе модулей: {e}")
        await query.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )

async def handle_module_callback(update: Update, context: CallbackContext, callback_parts: List[str]):
    """Обработка callback'ов для модулей"""
    try:
        logger.info(f"Получены части callback: {callback_parts}")
        
        if len(callback_parts) >= 3:
            module_id = int(callback_parts[1])
            action = callback_parts[2]

            if action == "grammar":
                if len(callback_parts) == 3:
                    await handle_module_grammar(update, context, module_id)
                elif len(callback_parts) >= 4:
                    topic_parts = callback_parts[3:]
                    if 'exercise' in topic_parts:
                        exercise_index = topic_parts.index('exercise')
                        topic_id = '_'.join(topic_parts[:exercise_index])
                        await handle_grammar_exercise(update, context, module_id, topic_id)
                    else:
                        topic_id = '_'.join(topic_parts)
                        await handle_grammar_topic(update, context, module_id, topic_id)

            elif action == "vocab":
                if len(callback_parts) == 3:
                    await handle_module_vocabulary(update, context, module_id)
                else:
                    category_parts = callback_parts[3:]
                    if any(action in category_parts for action in ['prev', 'next', 'audio']):
                        action_index = next(i for i, part in enumerate(category_parts) 
                                         if part in ['prev', 'next', 'audio'])
                        category_id = '_'.join(category_parts[:action_index])
                        word_index = int(category_parts[-1])
                        await handle_module_vocabulary_category(
                            update, context, module_id, category_id, word_index
                        )
                    else:
                        category_id = '_'.join(category_parts)
                        await handle_module_vocabulary_category(
                            update, context, module_id, category_id
                        )

        elif len(callback_parts) >= 2:
            module_id = int(callback_parts[1])
            await handle_specific_module(update, context, module_id)

    except Exception as e:
        logger.error(f"Ошибка в handle_module_callback: {e}")
        if "Message is not modified" not in str(e):
            raise

async def handle_grammar_topic(update: Update, context: CallbackContext, module_id: int, topic_id: str):
    """Показывает конкретную грамматическую тему"""
    query = update.callback_query
    await query.answer()

    try:
        # Выбираем грамматику в зависимости от модуля
        if module_id == 1:
            from data.module1.grammar import GRAMMAR_TOPICS
        elif module_id == 2:
            from data.module2.grammar import GRAMMAR_TOPICS
        elif module_id == 3:
            from data.module3.grammar import GRAMMAR_TOPICS
        elif module_id == 4:
            from data.module4.grammar import GRAMMAR_TOPICS
        elif module_id == 5:  # Добавляем поддержку пятого модуля
            from data.module5.grammar import GRAMMAR_TOPICS
        elif module_id == 6:  # Добавляем поддержку шестого модуля
            from data.module6.grammar import GRAMMAR_TOPICS
        elif module_id == 7:  # Добавляем поддержку седьмого модуля
            from data.module7.grammar import GRAMMAR_TOPICS
        elif module_id == 8:  # Добавляем поддержку восьмого модуля
            from data.module8.grammar import GRAMMAR_TOPICS
        else:
            await query.message.edit_text(
                "Грамматика для этого модуля находится в разработке.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К модулю", callback_data=f"module_{module_id}")
                ]])
            )
            return
        
        logger.info(f"Запрошена тема: {topic_id}")
        logger.info(f"Доступные темы: {list(GRAMMAR_TOPICS.keys())}")
        
        # Нормализуем topic_id
        normalized_topic_id = topic_id.lower().replace(' ', '_')
        logger.info(f"Нормализованный topic_id: {normalized_topic_id}")
        
        # Расширенный маппинг тем
        topic_mapping = {
            'present': 'present_simple',
            'present_simple': 'present_simple',
            'have': 'have_has',
            'have_has': 'have_has',
            'have_has_got': 'have_has',
            'possessive': 'possessive',
            'plural': 'plural',
            'prepositions': 'prepositions',
            # Добавляем маппинг для тем второго модуля
            'articles': 'articles',
            'there_is': 'there_is',
            'adjectives': 'adjectives',
            'possessive_s': 'possessive_s',
            'like_dislike': 'like_dislike',
            'present_continuous': 'present_continuous',
            'food_drinks': 'food_drinks',
            'would_like': 'would_like',
            'some_any': 'some_any',
            'can_ability': 'can_ability',
            'prepositions_time': 'prepositions_time',
            'lets': 'lets',
            'imperatives': 'imperatives',
            'must': 'must',
            'have_got': 'have_got',
            'can_animals': 'can_animals',
            'this_that_animals': 'this_that_animals',
            'adjectives_animals': 'adjectives_animals',
            'numbers_20_50': 'numbers_20_50',
            'there_is_are': 'there_is_are',
            'prepositions_place': 'prepositions_place',
            'plural_house': 'plural_house',
            'possessive_house': 'possessive_house',
            'how_many': 'how_many',
            'present_simple_daily': 'present_simple_daily',
            'adverbs_frequency': 'adverbs_frequency',
            'daily_routine': 'daily_routine',
            'time_expressions': 'time_expressions',
            'what_time': 'what_time',
            # Добавим альтернативные написания для надежности
            'present_simple': 'present_simple_daily',
            'adverbs': 'adverbs_frequency',
            'routine': 'daily_routine',
            'time': 'time_expressions'
        }
        
        actual_topic_id = topic_mapping.get(normalized_topic_id, normalized_topic_id)
        logger.info(f"Итоговый topic_id: {actual_topic_id}")
            
        topic_data = GRAMMAR_TOPICS.get(actual_topic_id)
        if not topic_data:
            logger.error(f"Тема не найдена: {actual_topic_id}")
            await query.message.edit_text(
                "Тема не найдена.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К темам", callback_data=f"module_{module_id}_grammar")
                ]])
            )
            return

        text = f"📝 {topic_data['title']}\n\n"
        text += f"ℹ️ {topic_data['description']}\n\n"
        
        text += "📚 Правила:\n"
        for rule in topic_data['rules']:
            text += f"• {rule}\n"
        
        text += "\n✏️ Примеры:\n"
        for example in topic_data['examples']:
            text += f"• {example}\n"

        keyboard = [
            [InlineKeyboardButton("✍️ Упражнения", callback_data=f"module_{module_id}_grammar_{actual_topic_id}_exercise")],
            [InlineKeyboardButton("🔙 К темам", callback_data=f"module_{module_id}_grammar")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(text, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при показе грамматической темы: {e}")
        raise

async def handle_grammar_exercise(update: Update, context: CallbackContext, module_id: int, topic_id: str):
    """Обработчик упражнений по грамматике"""
    query = update.callback_query
    await query.answer()

    try:
        if module_id == 1:
            exercises = GRAMMAR_EXERCISES.get(topic_id)
            if not exercises:
                await query.message.edit_text(
                    "Упражнения для этой темы пока не доступны.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("◀️ К теме", callback_data=f"module_{module_id}_grammar_{topic_id}")
                    ]])
                )
                return

            # Получаем текущий номер упражнения из контекста или начинаем с первого
            exercise_num = context.user_data.get(f'grammar_exercise_{topic_id}', 0)
            if exercise_num >= len(exercises['exercises']):
                exercise_num = 0

            exercise = exercises['exercises'][exercise_num]
            
            # Формируем текст упражнения
            text = f"✍️ Упражнение {exercise_num + 1}/{len(exercises['exercises'])}\n\n"
            text += f"📝 {exercise['question']}\n\n"

            keyboard = []
            if exercise['type'] == 'choice':
                # Для упражнений с выбором ответа
                for i, option in enumerate(exercise['options']):
                    keyboard.append([
                        InlineKeyboardButton(
                            option,
                            callback_data=f"module_{module_id}_grammar_{topic_id}_answer_{exercise_num}_{i}"
                        )
                    ])
            else:
                # Для упражнений с вводом текста
                text += "✏️ Введите ваш ответ в чат"
                context.user_data['expecting_answer'] = {
                    'module': module_id,
                    'topic': topic_id,
                    'exercise': exercise_num
                }

            # Добавляем навигационные кнопки
            keyboard.extend([
                [InlineKeyboardButton("◀️ К теме", callback_data=f"module_{module_id}_grammar_{topic_id}")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(text, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при показе упражнения: {e}")
        await query.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )

async def handle_grammar_exercise_answer(update: Update, context: CallbackContext, module_id: int, topic_id: str, exercise_num: int, answer: str):
    """Обработчик ответов на упражнения"""
    query = update.callback_query
    await query.answer()

    try:
        exercise = GRAMMAR_EXERCISES[topic_id]['exercises'][exercise_num]
        is_correct = False

        if exercise['type'] == 'choice':
            is_correct = int(answer) == exercise['correct']
        else:
            is_correct = answer.lower().strip() == exercise['correct'].lower().strip()

        # Показываем результат
        text = "✅ Правильно!\n\n" if is_correct else "❌ Неправильно.\n\n"
        text += f"💡 {exercise['explanation']}"

        keyboard = [
            [InlineKeyboardButton("➡️ Следующее упражнение", 
                callback_data=f"module_{module_id}_grammar_{topic_id}_exercise_{exercise_num + 1}")],
            [InlineKeyboardButton("◀️ К теме", callback_data=f"module_{module_id}_grammar_{topic_id}")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(text, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при обработке ответа: {e}")
        await query.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )

async def handle_module_vocabulary_category(update: Update, context: CallbackContext, module_id: int, category_id: str, word_index: int = 0):
    """Показывает слова из выбранной категории"""
    query = update.callback_query
    await query.answer()

    try:
        # Выбираем словарь в зависимости от модуля
        if module_id == 1:
            from data.module1.vocabulary import VOCABULARY
            # Маппинг для первого модуля
            category_mapping = {
                'classroom': 'classroom_objects',
                'language': 'classroom_language',
                'classroom_language': 'classroom_language',
                'classroom_objects': 'classroom_objects',
                'school_subjects': 'school_subjects',
                'numbers': 'numbers'
            }
        elif module_id == 2:
            from data.module2.vocabulary import VOCABULARY
            # Маппинг для второго модуля
            category_mapping = {
                'family': 'family_members',
                'family_members': 'family_members',
                'appearance': 'appearance',
                'activities': 'family_activities',
                'family_activities': 'family_activities',
                'home': 'home'
            }
        elif module_id == 3:
            from data.module3.vocabulary import VOCABULARY
            # Маппинг для третьего модуля
            category_mapping = {
                'food': 'food_drinks',
                'food_drinks': 'food_drinks',
                'meals': 'meals',
                'likes': 'likes_dislikes',
                'likes_dislikes': 'likes_dislikes',
                'food_types': 'food_types',
                'types': 'food_types'
            }
        elif module_id == 4:
            from data.module4.vocabulary import VOCABULARY
            # Маппинг для четвертого модуля
            category_mapping = {
                'toys': 'toys',
                'games': 'games',
                'playground': 'playground',
                'actions': 'actions',
                'play': 'actions',
                'game': 'games'
            }
        elif module_id == 5:
            from data.module5.vocabulary import VOCABULARY
            # Маппинг для пятого модуля
            category_mapping = {
                'pets': 'pets',
                'wild': 'wild_animals',
                'wild_animals': 'wild_animals',
                'body': 'animal_body',
                'animal_body': 'animal_body',
                'actions': 'animal_actions',
                'animal_actions': 'animal_actions',
                'habitats': 'animal_habitats',
                'animal_habitats': 'animal_habitats'
            }
        elif module_id == 6:
            from data.module6.vocabulary import VOCABULARY
            # Маппинг для шестого модуля
            category_mapping = {
                'rooms': 'rooms',
                'furniture': 'furniture',
                'items': 'household_items',
                'household': 'household_items',
                'household_items': 'household_items',
                'appliances': 'appliances',
                'prepositions': 'prepositions',
                'place': 'prepositions'
            }
        elif module_id == 7:
            from data.module7.vocabulary import VOCABULARY
            # Маппинг для седьмого модуля
            category_mapping = {
                'leisure': 'leisure',
                'activities': 'activities',
                'weekend': 'weekend',
                'sports': 'sports',
                'entertainment': 'entertainment',
                'hobby': 'activities',
                'free': 'weekend',
                'free_time': 'weekend',
                'sport': 'sports',
                'fun': 'entertainment'
            }
        elif module_id == 8:
            from data.module8.vocabulary import VOCABULARY
            # Маппинг для восьмого модуля
            category_mapping = {
                'routine': 'daily_routine',
                'daily_routine': 'daily_routine',
                'time': 'time_words',
                'time_words': 'time_words',
                'activities': 'daily_activities',
                'daily_activities': 'daily_activities',
                'frequency': 'frequency',
                'periods': 'time_periods',
                'time_periods': 'time_periods',
                'day': 'time_periods'
            }
        else:
            await query.message.edit_text(
                "Словарь для этого модуля находится в разработке.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("◀️ К модулю", callback_data=f"module_{module_id}")
                ]])
            )
            return
            
        logger.info(f"Запрошена категория: {category_id}")
        logger.info(f"Доступные категории: {list(VOCABULARY.keys())}")
        
        # Получаем правильный идентификатор категории
        actual_category_id = category_mapping.get(category_id, category_id)
        logger.info(f"Преобразованный category_id: {actual_category_id}")
        
        category = VOCABULARY.get(actual_category_id)
        if not category:
            logger.error(f"Категория не найдена: {actual_category_id}")
            await query.message.edit_text(
                "Категория не найдена.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("◀️ К словарю", callback_data=f"module_{module_id}_vocab")
                ]])
            )
            return

        words = category['words']
        total_words = len(words)

        # Проверяем и корректируем индекс слова
        if 'next' in query.data:
            word_index += 1
        elif 'prev' in query.data:
            word_index -= 1

        # Проверяем границы индекса
        if word_index < 0:
            word_index = 0
        if word_index >= total_words:
            word_index = total_words - 1

        word_data = words[word_index]
        keyboard = []

        # Кнопки навигации
        nav_buttons = []
        if word_index > 0:
            nav_buttons.append(
                InlineKeyboardButton(
                    "⬅️ Предыдущее", 
                    callback_data=f"module_{module_id}_vocab_{actual_category_id}_prev_{word_index}"
                )
            )
        if word_index < total_words - 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    "➡️ Следующее", 
                    callback_data=f"module_{module_id}_vocab_{actual_category_id}_next_{word_index}"
                )
            )
        if nav_buttons:
            keyboard.append(nav_buttons)

        # Кнопка произношения
        keyboard.append([
            InlineKeyboardButton(
                "🔊 Произношение", 
                callback_data=f"module_{module_id}_vocab_{actual_category_id}_audio_{word_index}"
            )
        ])

        # Кнопки навигации по меню
        keyboard.extend([
            [InlineKeyboardButton("◀️ К категориям", callback_data=f"module_{module_id}_vocab")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ])

        text = (
            f"📝 Слово: {word_data['word']}\n"
            f"🔊 Транскрипция: [{word_data['transcription']}]\n"
            f"🔤 Перевод: {word_data['translation']}\n"
            f"📋 Пример: {word_data['example']}\n\n"
            f"Слово {word_index + 1} из {total_words}"
        )

        try:
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(text, reply_markup=reply_markup)
        except Exception as e:
            if "Message is not modified" not in str(e):
                raise

        if 'audio' in query.data:
            # Генерируем и отправляем аудио
            audio_path = await get_word_audio(word_data['word'])
            if audio_path:
                try:
                    with open(audio_path, 'rb') as audio_file:
                        await query.message.reply_voice(audio_file)
                    os.remove(audio_path)  # Удаляем временный файл
                except Exception as e:
                    logger.error(f"Ошибка при отправке аудио: {e}")
                    await query.answer("Ошибка воспроизведения")
            else:
                await query.answer("Не удалось создать аудио")
            return

    except Exception as e:
        logger.error(f"Ошибка при показе слова: {e}")
        await query.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )

async def handle_specific_module(update: Update, context: CallbackContext, module_id: int):
    """Обработчик для конкретного модуля"""
    query = update.callback_query
    await query.answer()

    try:
        keyboard = [
            [
                InlineKeyboardButton("📚 Словарь", callback_data=f"module_{module_id}_vocab"),
                InlineKeyboardButton("📝 Грамматика", callback_data=f"module_{module_id}_grammar")
            ],
            [InlineKeyboardButton("🔙 К модулям", callback_data="modules")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            f"📚 Модуль {module_id}\n\n"
            "Выберите раздел для изучения:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Ошибка при показе модуля {module_id}: {e}")
        await query.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )

async def handle_module_vocabulary(update: Update, context: CallbackContext, module_id: int):
    """Обработчик для раздела словаря конкретного модуля"""
    query = update.callback_query
    await query.answer()

    try:
        # Выбираем словарь в зависимости от модуля
        if module_id == 1:
            from data.module1.vocabulary import VOCABULARY
        elif module_id == 2:
            from data.module2.vocabulary import VOCABULARY
        elif module_id == 3:
            from data.module3.vocabulary import VOCABULARY
        elif module_id == 4:
            from data.module4.vocabulary import VOCABULARY
        elif module_id == 5:
            from data.module5.vocabulary import VOCABULARY
        elif module_id == 6:
            from data.module6.vocabulary import VOCABULARY
        elif module_id == 7:
            from data.module7.vocabulary import VOCABULARY
        elif module_id == 8:
            from data.module8.vocabulary import VOCABULARY
        else:
            await query.message.edit_text(
                "Словарь для этого модуля находится в разработке.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К модулю", callback_data=f"module_{module_id}")
                ]])
            )
            return

        keyboard = []
        # Создаем кнопки для каждой категории в словаре
        for category_id, category_data in VOCABULARY.items():
            keyboard.append([
                InlineKeyboardButton(
                    category_data['title'],
                    callback_data=f"module_{module_id}_vocab_{category_id}"
                )
            ])

        # Добавляем кнопки навигации
        keyboard.extend([
            [InlineKeyboardButton("🔙 К модулю", callback_data=f"module_{module_id}")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            f"📚 Словарь модуля {module_id}\n\n"
            "Выберите категорию слов:",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Ошибка при показе словаря модуля {module_id}: {e}")
        await query.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )

async def handle_module_grammar(update: Update, context: CallbackContext, module_id: int):
    """Обработчик для раздела грамматики конкретного модуля"""
    query = update.callback_query
    await query.answer()

    try:
        # Выбираем грамматику в зависимости от модуля
        if module_id == 1:
            from data.module1.grammar import GRAMMAR_TOPICS
        elif module_id == 2:
            from data.module2.grammar import GRAMMAR_TOPICS
        elif module_id == 3:
            from data.module3.grammar import GRAMMAR_TOPICS
        elif module_id == 4:
            from data.module4.grammar import GRAMMAR_TOPICS
        elif module_id == 5:
            from data.module5.grammar import GRAMMAR_TOPICS
        elif module_id == 6:
            from data.module6.grammar import GRAMMAR_TOPICS
        elif module_id == 7:
            from data.module7.grammar import GRAMMAR_TOPICS
        elif module_id == 8:
            from data.module8.grammar import GRAMMAR_TOPICS
        else:
            await query.message.edit_text(
                "Грамматика для этого модуля находится в разработке.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К модулю", callback_data=f"module_{module_id}")
                ]])
            )
            return

        keyboard = []
        # Создаем кнопки для каждой грамматической темы
        for topic_id, topic_data in GRAMMAR_TOPICS.items():
            keyboard.append([
                InlineKeyboardButton(
                    topic_data['title'],
                    callback_data=f"module_{module_id}_grammar_{topic_id}"
                )
            ])

        # Добавляем кнопки навигации
        keyboard.extend([
            [InlineKeyboardButton("🔙 К модулю", callback_data=f"module_{module_id}")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            f"📝 Грамматика модуля {module_id}\n\n"
            "Выберите тему для изучения:",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Ошибка при показе грамматики модуля {module_id}: {e}")
        await query.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )

async def handle_module_exercises(update: Update, context: CallbackContext, module_id: int):
    """Обработчик для раздела упражнений конкретного модуля"""
    query = update.callback_query
    await query.answer()

    try:
        # Выбираем упражнения в зависимости от модуля
        if module_id == 1:
            from data.module1.exercises import EXERCISES
            
            keyboard = []
            # Создаем кнопки для каждого типа упражнений
            for exercise_type, exercise_data in EXERCISES.items():
                keyboard.append([
                    InlineKeyboardButton(
                        exercise_data['title'],
                        callback_data=f"module_{module_id}_exercise_{exercise_type}_0"  # Добавляем индекс 0
                    )
                ])

            # Добавляем кнопки навигации
            keyboard.extend([
                [InlineKeyboardButton("🔙 К модулю", callback_data=f"module_{module_id}")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(
                "✍️ Упражнения модуля 'School Days'\n\n"
                "Выберите тип упражнений:",
                reply_markup=reply_markup
            )
        else:
            keyboard = [[InlineKeyboardButton("🔙 К модулю", callback_data=f"module_{module_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(
                "Упражнения для этого модуля находятся в разработке.",
                reply_markup=reply_markup
            )

    except Exception as e:
        logger.error(f"Ошибка при показе упражнений модуля {module_id}: {e}")
        if "Message is not modified" not in str(e):
            await query.message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте еще раз."
            )

async def handle_module_test(update: Update, context: CallbackContext, module_id: int):
    """Обработчик для раздела тестов конкретного модуля"""
    query = update.callback_query
    await query.answer()

    try:
        # Выбираем тесты в зависимости от модуля
        if module_id == 1:
            from data.module1.tests import TESTS
        elif module_id == 2:
            from data.module2.tests import TESTS
        elif module_id == 3:
            from data.module3.tests import TESTS
        elif module_id == 4:
            from data.module4.tests import TESTS
        elif module_id == 5:
            from data.module5.tests import TESTS
        elif module_id == 6:
            from data.module6.tests import TESTS
        elif module_id == 7:
            from data.module7.tests import TESTS
        elif module_id == 8:
            from data.module8.tests import TESTS
        else:
            await query.message.edit_text(
                "Тесты для этого модуля находятся в разработке.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К модулю", callback_data=f"module_{module_id}")
                ]])
            )
            return

        # Получаем текущий вопрос теста из контекста или начинаем с первого
        current_question = context.user_data.get(f'test_question_{module_id}', 0)
        
        if current_question >= len(TESTS):
            # Если все вопросы пройдены, показываем результат
            score = context.user_data.get(f'test_score_{module_id}', 0)
            await query.message.edit_text(
                f"🎉 Тест завершен!\n\n"
                f"Ваш результат: {score}/{len(TESTS)} правильных ответов.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Начать заново", 
                        callback_data=f"module_{module_id}_test_restart"),
                    InlineKeyboardButton("🔙 К модулю", 
                        callback_data=f"module_{module_id}")
                ]])
            )
            return

        # Показываем текущий вопрос
        question_data = TESTS[current_question]
        
        keyboard = []
        # Создаем кнопки с вариантами ответов
        for i, option in enumerate(question_data['options']):
            keyboard.append([
                InlineKeyboardButton(
                    option,
                    callback_data=f"module_{module_id}_test_answer_{current_question}_{i}"
                )
            ])

        # Добавляем кнопки навигации
        keyboard.extend([
            [InlineKeyboardButton("🔙 К модулю", callback_data=f"module_{module_id}")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            f"❓ Вопрос {current_question + 1}/{len(TESTS)}\n\n"
            f"{question_data['question']}",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Ошибка при показе теста модуля {module_id}: {e}")
        await query.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )

async def handle_exercise(update: Update, context: CallbackContext, module_id: int, exercise_type: str, exercise_index: int):
    """Обработчик конкретного упражнения"""
    query = update.callback_query
    await query.answer()

    try:
        if module_id == 1:
            from data.module1.exercises import EXERCISES
            
            exercise_data = EXERCISES[exercise_type]
            exercises = exercise_data['exercises']
            
            if exercise_index >= len(exercises):
                exercise_index = 0
                
            exercise = exercises[exercise_index]
            keyboard = []
            
            # Формируем текст упражнения
            text = f"📝 {exercise_data['title']}\n"
            text += f"Упражнение {exercise_index + 1} из {len(exercises)}\n\n"
            text += f"❓ {exercise['question']}\n\n"
            
            if exercise['type'] == 'choice':
                # Для упражнений с выбором ответа
                for i, option in enumerate(exercise['options']):
                    keyboard.append([
                        InlineKeyboardButton(
                            option,
                            callback_data=f"module_{module_id}_exercise_{exercise_type}_answer_{exercise_index}_{i}"
                        )
                    ])
            elif exercise['type'] == 'match':
                # Для упражнений на сопоставление
                text += "🔄 Соедините пары:\n"
                for pair in exercise['pairs']:
                    text += f"• {pair[0]} - ?\n"
                    
            elif exercise['type'] == 'fill':
                # Для упражнений с заполнением пропусков
                text += "✏️ Введите ответ в чат"
                context.user_data['expecting_answer'] = {
                    'module': module_id,
                    'type': exercise_type,
                    'index': exercise_index
                }
            
            # Добавляем навигационные кнопки
            nav_buttons = []
            if exercise_index > 0:
                nav_buttons.append(
                    InlineKeyboardButton("⬅️ Предыдущее", 
                        callback_data=f"module_{module_id}_exercise_{exercise_type}_{exercise_index-1}")
                )
            if exercise_index < len(exercises) - 1:
                nav_buttons.append(
                    InlineKeyboardButton("➡️ Следующее", 
                        callback_data=f"module_{module_id}_exercise_{exercise_type}_{exercise_index+1}")
                )
            if nav_buttons:
                keyboard.append(nav_buttons)
            
            keyboard.extend([
                [InlineKeyboardButton("🔙 К упражнениям", callback_data=f"module_{module_id}_exercises")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(text, reply_markup=reply_markup)
            
    except Exception as e:
        logger.error(f"Ошибка при показе упражнения: {e}")
        if "Message is not modified" not in str(e):
            await query.message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте еще раз."
            )

async def handle_exercise_answer(update: Update, context: CallbackContext, module_id: int, exercise_type: str, exercise_index: int, answer: str):
    """Обработчик ответов на упражнения"""
    query = update.callback_query
    await query.answer()

    try:
        if module_id == 1:
            from data.module1.exercises import EXERCISES
            
            exercise_data = EXERCISES[exercise_type]
            exercise = exercise_data['exercises'][exercise_index]
            is_correct = False

            if exercise['type'] == 'choice':
                is_correct = int(answer) == exercise['correct']
            elif exercise['type'] == 'fill':
                is_correct = answer.lower().strip() == exercise['correct'].lower().strip()

            # Показываем результат
            text = "✅ Правильно!\n\n" if is_correct else "❌ Неправильно.\n\n"
            text += f"💡 {exercise['explanation']}"

            keyboard = []
            # Добавляем кнопку следующего упражнения, если оно есть
            if exercise_index < len(exercise_data['exercises']) - 1:
                keyboard.append([
                    InlineKeyboardButton(
                        "➡️ Следующее упражнение",
                        callback_data=f"module_{module_id}_exercise_{exercise_type}_{exercise_index + 1}"
                    )
                ])

            keyboard.extend([
                [InlineKeyboardButton("🔙 К упражнениям", callback_data=f"module_{module_id}_exercises")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(text, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при обработке ответа на упражнение: {e}")
        if "Message is not modified" not in str(e):
            await query.message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте еще раз."
            )