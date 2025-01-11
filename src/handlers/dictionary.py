from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.media_manager import MediaManager
import logging
from gtts import gTTS
import os
import tempfile

logger = logging.getLogger(__name__)

WORD_CATEGORIES = {
    'family': {
        'title': 'Семья',
        'words': [
            {
                'word': 'mother',
                'transcription': 'ˈmʌðər',
                'translation': 'мама',
                'example': 'This is my mother.',
                'module_id': 1
            },
            {
                'word': 'father',
                'transcription': 'ˈfɑːðər',
                'translation': 'папа',
                'example': 'My father is tall.',
                'module_id': 1
            },
            {
                'word': 'sister',
                'transcription': 'ˈsɪstər',
                'translation': 'сестра',
                'example': 'I have a sister.',
                'module_id': 1
            },
            {
                'word': 'brother',
                'transcription': 'ˈbrʌðər',
                'translation': 'брат',
                'example': 'My brother plays football.',
                'module_id': 1
            },
            {
                'word': 'grandmother',
                'transcription': 'ˈɡrænˌmʌðər',
                'translation': 'бабушка',
                'example': 'My grandmother bakes cookies.',
                'module_id': 1
            },
            {
                'word': 'grandfather',
                'transcription': 'ˈɡrænˌfɑːðər',
                'translation': 'дедушка',
                'example': 'My grandfather tells stories.',
                'module_id': 1
            },
            {
                'word': 'parents',
                'transcription': 'ˈpeərənts',
                'translation': 'родители',
                'example': 'My parents work hard.',
                'module_id': 1
            },
            {
                'word': 'family',
                'transcription': 'ˈfæmɪli',
                'translation': 'семья',
                'example': 'I love my family.',
                'module_id': 1
            },
            {
                'word': 'aunt',
                'transcription': 'ɑːnt',
                'translation': 'тётя',
                'example': 'My aunt lives in London.',
                'module_id': 1
            },
            {
                'word': 'uncle',
                'transcription': 'ˈʌŋkl',
                'translation': 'дядя',
                'example': 'My uncle has a car.',
                'module_id': 1
            },
            {
                'word': 'cousin',
                'transcription': 'ˈkʌzn',
                'translation': 'двоюродный брат/сестра',
                'example': 'My cousin is 10 years old.',
                'module_id': 1
            }
        ]
    },
    'toys': {
        'title': 'Игрушки',
        'words': [
            {
                'word': 'ball',
                'transcription': 'bɔːl',
                'translation': 'мяч',
                'example': 'I have a red ball.',
                'module_id': 2
            },
            {
                'word': 'doll',
                'transcription': 'dɒl',
                'translation': 'кукла',
                'example': 'This is my favorite doll.',
                'module_id': 2
            },
            {
                'word': 'car',
                'transcription': 'kɑːr',
                'translation': 'машинка',
                'example': 'The car is blue.',
                'module_id': 2
            },
            {
                'word': 'teddy bear',
                'transcription': 'ˈtedi beər',
                'translation': 'плюшевый мишка',
                'example': 'I sleep with my teddy bear.',
                'module_id': 2
            },
            {
                'word': 'robot',
                'transcription': 'ˈrəʊbɒt',
                'translation': 'робот',
                'example': 'My robot can walk.',
                'module_id': 2
            },
            {
                'word': 'blocks',
                'transcription': 'blɒks',
                'translation': 'кубики',
                'example': 'I build towers with blocks.',
                'module_id': 2
            },
            {
                'word': 'puzzle',
                'transcription': 'ˈpʌzl',
                'translation': 'пазл',
                'example': 'This puzzle has 100 pieces.',
                'module_id': 2
            },
            {
                'word': 'game',
                'transcription': 'ɡeɪm',
                'translation': 'игра',
                'example': "Let's play a game!",
                'module_id': 2
            },
            {
                'word': 'train',
                'transcription': 'treɪn',
                'translation': 'поезд (игрушечный)',
                'example': 'The train goes choo-choo!',
                'module_id': 2
            },
            {
                'word': 'plane',
                'transcription': 'pleɪn',
                'translation': 'самолёт (игрушечный)',
                'example': 'My plane can fly high.',
                'module_id': 2
            }
        ]
    },
    'animals': {
        'title': 'Животные',
        'words': [
            {
                'word': 'cat',
                'transcription': 'kæt',
                'translation': 'кошка',
                'example': 'The cat is black.',
                'module_id': 3
            },
            {
                'word': 'dog',
                'transcription': 'dɒɡ',
                'translation': 'собака',
                'example': 'I have a big dog.',
                'module_id': 3
            },
            {
                'word': 'bird',
                'transcription': 'bɜːd',
                'translation': 'птица',
                'example': 'The bird can fly.',
                'module_id': 3
            },
            {
                'word': 'fish',
                'transcription': 'fɪʃ',
                'translation': 'рыба',
                'example': 'The fish swims in water.',
                'module_id': 3
            },
            {
                'word': 'rabbit',
                'transcription': 'ˈræbɪt',
                'translation': 'кролик',
                'example': 'The rabbit likes carrots.',
                'module_id': 3
            },
            {
                'word': 'hamster',
                'transcription': 'ˈhæmstər',
                'translation': 'хомяк',
                'example': 'My hamster is small.',
                'module_id': 3
            },
            {
                'word': 'parrot',
                'transcription': 'ˈpærət',
                'translation': 'попугай',
                'example': 'The parrot can talk.',
                'module_id': 3
            },
            {
                'word': 'mouse',
                'transcription': 'maʊs',
                'translation': 'мышь',
                'example': 'The mouse likes cheese.',
                'module_id': 3
            }
        ]
    },
    'colors': {
        'title': 'Цвета',
        'words': [
            {
                'word': 'red',
                'transcription': 'red',
                'translation': 'красный',
                'example': 'The apple is red.',
                'module_id': 2
            },
            {
                'word': 'blue',
                'transcription': 'bluː',
                'translation': 'синий',
                'example': 'The sky is blue.',
                'module_id': 2
            },
            {
                'word': 'green',
                'transcription': 'ɡriːn',
                'translation': 'зелёный',
                'example': 'I like green trees.',
                'module_id': 2
            },
            {
                'word': 'yellow',
                'transcription': 'ˈjeləʊ',
                'translation': 'жёлтый',
                'example': 'The sun is yellow.',
                'module_id': 2
            },
            {
                'word': 'black',
                'transcription': 'blæk',
                'translation': 'чёрный',
                'example': 'My cat is black.',
                'module_id': 2
            },
            {
                'word': 'white',
                'transcription': 'waɪt',
                'translation': 'белый',
                'example': 'Snow is white.',
                'module_id': 2
            },
            {
                'word': 'brown',
                'transcription': 'braʊn',
                'translation': 'коричневый',
                'example': 'I have brown hair.',
                'module_id': 2
            },
            {
                'word': 'pink',
                'transcription': 'pɪŋk',
                'translation': 'розовый',
                'example': 'Her dress is pink.',
                'module_id': 2
            },
            {
                'word': 'orange',
                'transcription': 'ˈɒrɪndʒ',
                'translation': 'оранжевый',
                'example': 'The orange is orange.',
                'module_id': 2
            },
            {
                'word': 'purple',
                'transcription': 'ˈpɜːpl',
                'translation': 'фиолетовый',
                'example': 'I like purple flowers.',
                'module_id': 2
            }
        ]
    },
    'numbers': {
        'title': 'Числа',
        'words': [
            {
                'word': 'one',
                'transcription': 'wʌn',
                'translation': 'один',
                'example': 'I have one brother.',
                'module_id': 1
            },
            {
                'word': 'two',
                'transcription': 'tuː',
                'translation': 'два',
                'example': 'I have two sisters.',
                'module_id': 1
            },
            {
                'word': 'three',
                'transcription': 'θriː',
                'translation': 'три',
                'example': 'There are three books.',
                'module_id': 1
            },
            {
                'word': 'four',
                'transcription': 'fɔːr',
                'translation': 'четыре',
                'example': 'I have four pencils.',
                'module_id': 1
            },
            {
                'word': 'five',
                'transcription': 'faɪv',
                'translation': 'пять',
                'example': 'Five dogs are playing.',
                'module_id': 1
            },
            {
                'word': 'six',
                'transcription': 'sɪks',
                'translation': 'шесть',
                'example': 'I am six years old.',
                'module_id': 1
            },
            {
                'word': 'seven',
                'transcription': 'ˈsevn',
                'translation': 'семь',
                'example': 'Seven days in a week.',
                'module_id': 1
            },
            {
                'word': 'eight',
                'transcription': 'eɪt',
                'translation': 'восемь',
                'example': 'I have eight toys.',
                'module_id': 1
            },
            {
                'word': 'nine',
                'transcription': 'naɪn',
                'translation': 'девять',
                'example': 'Nine cats are sleeping.',
                'module_id': 1
            },
            {
                'word': 'ten',
                'transcription': 'ten',
                'translation': 'десять',
                'example': 'Ten birds in the tree.',
                'module_id': 1
            }
        ]
    },
    'house': {
        'title': 'Дом',
        'words': [
            {
                'word': 'room',
                'transcription': 'ruːm',
                'translation': 'комната',
                'example': 'This is my room.',
                'module_id': 4
            },
            {
                'word': 'door',
                'transcription': 'dɔːr',
                'translation': 'дверь',
                'example': 'The door is open.',
                'module_id': 4
            },
            {
                'word': 'window',
                'transcription': 'ˈwɪndəʊ',
                'translation': 'окно',
                'example': 'Close the window, please.',
                'module_id': 4
            },
            {
                'word': 'bed',
                'transcription': 'bed',
                'translation': 'кровать',
                'example': 'I sleep in my bed.',
                'module_id': 4
            },
            {
                'word': 'table',
                'transcription': 'ˈteɪbl',
                'translation': 'стол',
                'example': 'The book is on the table.',
                'module_id': 4
            },
            {
                'word': 'chair',
                'transcription': 'tʃeər',
                'translation': 'стул',
                'example': 'Sit on the chair.',
                'module_id': 4
            },
            {
                'word': 'kitchen',
                'transcription': 'ˈkɪtʃɪn',
                'translation': 'кухня',
                'example': 'Mom is in the kitchen.',
                'module_id': 4
            },
            {
                'word': 'bathroom',
                'transcription': 'ˈbɑːθruːm',
                'translation': 'ванная',
                'example': 'The bathroom is clean.',
                'module_id': 4
            },
            {
                'word': 'floor',
                'transcription': 'flɔːr',
                'translation': 'пол',
                'example': 'The toy is on the floor.',
                'module_id': 4
            },
            {
                'word': 'wall',
                'transcription': 'wɔːl',
                'translation': 'стена',
                'example': 'The picture is on the wall.',
                'module_id': 4
            }
        ]
    }
}

def get_word_data(category_id: str, word_index: int = 0):
    """Получение данных о слове по категории и индексу"""
    category = WORD_CATEGORIES.get(category_id)
    if category and 'words' in category and word_index < len(category['words']):
        return category['words'][word_index]
    return None

def get_category_words_count(category_id: str) -> int:
    """Получение количества слов в атегории"""
    category = WORD_CATEGORIES.get(category_id)
    if category and 'words' in category:
        return len(category['words'])
    return 0

async def handle_dictionary(update: Update, context):
    """Обработчик для общего словаря"""
    query = update.callback_query
    await query.answer()

    try:
        keyboard = []
        # Создаем кнопки для каждой категории
        for category_id, category_data in WORD_CATEGORIES.items():
            keyboard.append([
                InlineKeyboardButton(
                    category_data['title'],
                    callback_data=f"dictionary_{category_id}"  # Используем формат dictionary_category_id
                )
            ])

        keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text(
            "📚 Словарь\nВыберите категорию слов:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Ошибка при показе словаря: {e}")
        await query.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )

async def show_word_card(update: Update, context, category_id: str, word_index: int = 0):
    """Показывает карточку слова"""
    query = update.callback_query
    await query.answer()

    try:
        word_data = get_word_data(category_id, word_index)
        if not word_data:
            await query.message.edit_text(
                "Слово не найдено.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К словарю", callback_data="dictionary")
                ]])
            )
            return

        keyboard = []
        # Кнопки навигации
        nav_buttons = []
        if word_index > 0:
            nav_buttons.append(
                InlineKeyboardButton(
                    "⬅️ Предыдущее", 
                    callback_data=f"dictionary_{category_id}_prev_{word_index}"
                )
            )
        total_words = get_category_words_count(category_id)
        if word_index < total_words - 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    "➡️ Следующее", 
                    callback_data=f"dictionary_{category_id}_next_{word_index}"
                )
            )
        if nav_buttons:
            keyboard.append(nav_buttons)

        # Кнопка произношения
        keyboard.append([
            InlineKeyboardButton(
                "🔊 Произношение", 
                callback_data=f"dictionary_{category_id}_audio_{word_index}"
            )
        ])

        # Кнопки возврата
        keyboard.extend([
            [InlineKeyboardButton("🔙 К категориям", callback_data="dictionary")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ])

        text = (
            f"📝 Слово: {word_data['word']}\n"
            f"🔊 Транскрипция: [{word_data['transcription']}]\n"
            f"🔤 Перевод: {word_data['translation']}\n"
            f"📋 Пример: {word_data['example']}\n\n"
            f"Слово {word_index + 1} из {total_words}"
        )

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(text, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при показе слова: {e}")
        await query.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )

async def get_word_audio(word: str) -> str:
    """Генерирует аудио файл для слова и возвращает путь к нему"""
    try:
        tts = gTTS(text=word, lang='en')
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_path = fp.name
            tts.save(temp_path)
            return temp_path
    except Exception as e:
        logger.error(f"Ошибка при создании аудио для слова {word}: {e}")
        return None