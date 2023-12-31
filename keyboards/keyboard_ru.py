from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_RU

# ------- Создаем клавиатуру через ReplyKeyboardBuilder -------

# Создаем кнопки с основнными запросами
button_reg = KeyboardButton(text=LEXICON_RU['reg_b'])
button_search = KeyboardButton(text=LEXICON_RU['search_b'])
button_send_message = KeyboardButton(text=LEXICON_RU['send_b'])



# Инициализируем билдер для клавиатуры с кнопками
reg_search_send_builder = ReplyKeyboardBuilder()
next_builder = ReplyKeyboardBuilder()


# Добавляем кнопки в билдер с аргументом width=3
reg_search_send_builder.row(button_reg, button_search, button_send_message, width=3)


# Создаем клавиатуру с кнопками регистрация отправить сообщение и  найти авто по номеру
reg_search_send_kb: ReplyKeyboardMarkup = reg_search_send_builder.as_markup(
                                            one_time_keyboard=True,
                                            resize_keyboard=True)

