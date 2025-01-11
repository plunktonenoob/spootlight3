EXERCISES = {
    'vocabulary': {
        'title': 'Упражнения на словарный запас',
        'exercises': [
            {
                'type': 'choice',
                'question': 'Выберите правильный перевод слова "pencil"',
                'options': ['ручка', 'карандаш', 'линейка', 'ластик'],
                'correct': 1,
                'explanation': 'Pencil - это карандаш'
            },
            {
                'type': 'match',
                'question': 'Соедините слова с их переводом',
                'pairs': [
                    ('book', 'книга'),
                    ('desk', 'парта'),
                    ('pen', 'ручка'),
                    ('ruler', 'линейка')
                ]
            },
            {
                'type': 'fill',
                'question': 'Заполните пропуск: "I need a _____ to write."',
                'correct': 'pen',
                'explanation': 'Pen (ручка) используется для письма'
            }
        ]
    },
    'grammar': {
        'title': 'Грамматические упражнения',
        'exercises': [
            {
                'type': 'choice',
                'question': 'Выберите правильный артикль: "This is ___ book."',
                'options': ['a', 'an', 'the', '-'],
                'correct': 0,
                'explanation': 'Перед словом book используется артикль "a", так как слово начинается с согласной'
            },
            {
                'type': 'fill',
                'question': 'Заполните пропуск, используя have/has: "She _____ a pencil."',
                'correct': 'has',
                'explanation': 'С местоимением she используется форма has'
            },
            {
                'type': 'choice',
                'question': 'Выберите правильную форму множественного числа: "Two _____"',
                'options': ['child', 'childs', 'children', 'childrens'],
                'correct': 2,
                'explanation': 'Children - правильная форма множественного числа слова child'
            }
        ]
    },
    'mixed': {
        'title': 'Смешанные упражнения',
        'exercises': [
            {
                'type': 'fill',
                'question': 'Составьте предложение: "book / This / my / is"',
                'correct': 'This is my book',
                'explanation': 'Правильный порядок слов: This is my book (Это моя книга)'
            },
            {
                'type': 'choice',
                'question': 'Выберите правильный ответ: "Is this your pen?" "___"',
                'options': ['Yes, it is', 'Yes, this is', 'Yes, that is', 'Yes, it does'],
                'correct': 0,
                'explanation': 'Краткий ответ на вопрос с to be: Yes, it is'
            },
            {
                'type': 'match',
                'question': 'Соедините вопросы и ответы',
                'pairs': [
                    ('What is this?', 'It is a book'),
                    ('Is it a pen?', 'Yes, it is'),
                    ('Are they pencils?', 'No, they are not'),
                    ('How many books?', 'Three books')
                ]
            }
        ]
    }
}

# Грамматические упражнения по конкретным темам
GRAMMAR_EXERCISES = {
    'present_simple': {
        'title': 'Present Simple',
        'exercises': [
            {
                'type': 'choice',
                'question': 'Выберите правильную форму: "She _____ English."',
                'options': ['study', 'studies', 'studying', 'studied'],
                'correct': 1,
                'explanation': 'В Present Simple с she используется окончание -es/s'
            },
            {
                'type': 'fill',
                'question': 'Заполните пропуск: "I _____ to school every day." (go)',
                'correct': 'go',
                'explanation': 'С I используется базовая форма глагола go'
            }
        ]
    },
    'have_has': {
        'title': 'Have/Has',
        'exercises': [
            {
                'type': 'choice',
                'question': 'Выберите правильный вариант: "Tom _____ a new pen."',
                'options': ['have', 'has', 'having', 'to have'],
                'correct': 1,
                'explanation': 'С единственным числом 3-го лица (he/she/it) используется has'
            },
            {
                'type': 'fill',
                'question': 'Заполните пропуск: "We _____ many books."',
                'correct': 'have',
                'explanation': 'С we используется форма have'
            }
        ]
    }
} 