from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)

GRAMMAR_TOPICS = {
    'present': {
        'title': 'Present Simple',
        'description': 'Настоящее простое время',
        'rules': [
            "Используется для описания регулярных действий и фактов",
            "Утвердительная форма для I/You/We/They: глагол без изменений",
            "Утвердительная форма для He/She/It: глагол + s",
            "Отрицательная форма: don't/doesn't + глагол",
            "Вопросительная форма: Do/Does + подлежащее + глагол"
        ],
        'examples': [
            "I play football. - Я играю в футбол.",
            "She plays tennis. - Она играет в теннис.",
            "They don't like pizza. - Они не любят пиццу.",
            "Does he speak English? - Он говорит по-английски?"
        ]
    },
    'have': {
        'title': 'Have/Has got',
        'description': 'Конструкция для описания принадлежности',
        'rules': [
            "I/You/We/They have got - У меня/тебя/нас/их есть",
            "He/She/It has got - У него/неё/этого есть",
            "Отрицание: haven't got / hasn't got",
            "Вопрос: Have/Has + подлежащее + got?"
        ],
        'examples': [
            "I have got a dog. - У меня есть собака.",
            "She has got a cat. - У неё есть кошка.",
            "They haven't got a car. - У них нет машины.",
            "Has he got a brother? - У него есть брат?"
        ]
    },
    'possessive': {
        'title': 'Притяжательные местоимения',
        'description': 'Местоимения, указывающие на принадлежность',
        'rules': [
            "my - мой/моя/моё/мои",
            "your - твой/ваш",
            "his - его",
            "her - её",
            "its - его/её (для предметов)",
            "our - наш",
            "their - их"
        ],
        'examples': [
            "This is my book. - Это моя книга.",
            "Her name is Ann. - Её зовут Анна.",
            "Their house is big. - Их дом большой."
        ]
    },
    'plurals': {
        'title': 'Множественное число',
        'description': 'Образование множественного числа существительных',
        'rules': [
            "Обычно: добавляем -s (cat - cats)",
            "После -s, -ss, -ch, -sh, -x: добавляем -es (box - boxes)",
            "Если оканчивается на согласную + y: y → i + es (baby - babies)",
            "Если оканчивается на гласную + y: просто + s (toy - toys)",
            "Особые случаи: child - children, man - men, woman - women"
        ],
        'examples': [
            "One dog, two dogs - Одна собака, две собаки",
            "One box, two boxes - Одна коробка, две коробки",
            "One baby, two babies - Один малыш, два малыша",
            "One toy, two toys - Одна игрушка, две игрушки"
        ]
    },
    'prepositions': {
        'title': 'Предлоги места',
        'description': 'Предлоги, указывающие на расположение предметов',
        'rules': [
            "in - в, внутри",
            "on - на (поверхности)",
            "under - под",
            "behind - за, позади",
            "in front of - перед",
            "between - между",
            "next to - рядом с"
        ],
        'examples': [
            "The book is in the bag. - Книга в сумке.",
            "The cat is on the table. - Кошка на столе.",
            "The ball is under the chair. - Мяч под стулом.",
            "The tree is behind the house. - Дерево за домом."
        ]
    },
    'this': {
        'title': 'This/That/These/Those',
        'description': 'Указательные местоимения',
        'rules': [
            "this - этот/эта/это (близко)",
            "that - тот/та/то (далеко)",
            "these - эти (множ. число, близко)",
            "those - те (множ. число, далеко)"
        ],
        'examples': [
            "This is my pen. - Это моя ручка.",
            "That is his house. - То его дом.",
            "These are my books. - Эт�� мои книги.",
            "Those are their toys. - То их игрушки."
        ]
    },
    'can': {
        'title': 'Can/Can\'t',
        'description': 'Модальный глагол возможности/способности',
        'rules': [
            "Can - мочь, уметь (утвердительная форма)",
            "Can't/Cannot - не мочь, не уметь (отрицательная форма)",
            "Can...? - мочь, уметь (вопросительная форма)",
            "Не изменяется по лицам и числам"
        ],
        'examples': [
            "I can swim. - Я умею плавать.",
            "He can't fly. - Он не может летать.",
            "Can you dance? - Ты умеешь танцевать?",
            "Yes, I can. / No, I can't. - Да, умею. / Нет, не умею."
        ]
    },
    'imperative': {
        'title': 'Повелительное наклонение',
        'description': 'Команды и просьбы',
        'rules': [
            "Утвердительная форма: глагол в начальной форме",
            "Отрицательная форма: Don't + глагол",
            "Please для вежливой просьбы",
            "Let's для предложения совместного действия"
        ],
        'examples': [
            "Open the door! - Открой дверь!",
            "Don't run! - Не бегай!",
            "Please, help me. - Пожалуйста, помоги мне.",
            "Let's play! - Давай играть!"
        ]
    }
}

async def handle_grammar(update: Update, context):
    """Обработчик для раздела грамматики"""
    query = update.callback_query
    await query.answer()

    try:
        keyboard = []
        # Создаем кнопки для каждой грамматической темы
        for topic_id, topic_data in GRAMMAR_TOPICS.items():
            keyboard.append([
                InlineKeyboardButton(
                    topic_data['title'],
                    callback_data=f"grammar_{topic_id}"  # Используем префикс grammar_
                )
            ])

        keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text(
            "📝 Грамматика\nВыберите тему для изучения:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Ошибка при показе грамматики: {e}")
        await query.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )

async def show_grammar_topic(update: Update, context, topic_id: str):
    """Показывает конкретную грамматическую тему"""
    query = update.callback_query
    await query.answer()

    try:
        topic_data = GRAMMAR_TOPICS.get(topic_id)
        if not topic_data:
            logger.error(f"Тема не найдена: {topic_id}")
            await query.message.edit_text(
                "Тема не найдена.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К темам", callback_data="grammar")
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
            [InlineKeyboardButton("✍️ Упражнения", callback_data=f"grammar_{topic_id}_exercise")],
            [InlineKeyboardButton("🔙 К темам", callback_data="grammar")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(text, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при показе грамматической темы: {e}")
        await query.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )

async def handle_grammar_exercise(update: Update, context, topic_id: str):
    logger.info(f"Показываем упражнение по теме: {topic_id}")
    """Показывает упражнения по грамматической теме"""
    topic_data = GRAMMAR_TOPICS.get(topic_id)
    if not topic_data or 'exercises' not in topic_data:
        return
    
    current_exercise = context.user_data.get('current_exercise', 0)
    exercise = topic_data['exercises'][current_exercise]
    
    text = f"✍️ Упражнение {current_exercise + 1}\n\n"
    text += f"Заполните пропуск:\n{exercise['question']}"
    
    keyboard = [
        [InlineKeyboardButton("🔍 Показать ответ", callback_data=f"grammar_{topic_id}_answer")],
        [InlineKeyboardButton("🔙 К теории", callback_data=f"grammar_{topic_id}")]
    ]
    
    if len(topic_data['exercises']) > 1:
        nav_buttons = []
        if current_exercise > 0:
            nav_buttons.append(
                InlineKeyboardButton("⬅️ Предыдущее", callback_data=f"grammar_{topic_id}_prev")
            )
        if current_exercise < len(topic_data['exercises']) - 1:
            nav_buttons.append(
                InlineKeyboardButton("➡️ Следующее", callback_data=f"grammar_{topic_id}_next")
            )
        keyboard.insert(0, nav_buttons)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(text, reply_markup=reply_markup) 