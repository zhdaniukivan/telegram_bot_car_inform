from aiogram.fsm.state import State
from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, StatesGroup
from aiogram.types import Message
from keyboards.keyboard_ru import reg_search_send_kb
from lexicon.lexicon_ru import LEXICON_RU
from aiogram.fsm.storage.redis import RedisStorage, Redis
import requests
from data.config_data import Config, load_config

import asyncio
from data import config_data
from db.car_bot import db
from db import quick_commands as commands

# Создаем обработчик для записи данных в базу данных postgresql
async def db_test():
    await db.set_bind(config_data.POSTGRES_URL)

def replace_and_apper_number(number: str) -> str:
    return number.replace(' ', '').upper()


# Создаем глобальную переменную для передачи данных из одной фукции в другую
id_to_message = None

# Инициализируем Redis
redis = Redis(host='localhost')

storage = RedisStorage(redis=redis)

router = Router()

# Создаем "базу данных" пользователей
user_dict: dict[str, dict[str, str, str]] = {}

class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    fill_name = State()        # Состояние ожидания ввода имени
    fill_car_number = State()         # Состояние ожидания номера машины
    fill_rew = State()      # Состояние ожидания опания машины
    searching_number = State()      # Состояние ожидания номера для поиска
    sent_message = State()      # Состояние вода номера для отправки сообщения
    await_text_message = State()      # Состояние ожидания ввода текста сообщения


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['start'], reply_markup=reg_search_send_kb)


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='/help'), StateFilter(default_state))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['help'], reply_markup=reg_search_send_kb)


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию
@router.message(Command(commands='/cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(text=LEXICON_RU['cansel'])


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@router.message(Command(commands='/cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_RU['cansel_1'], reply_markup=reg_search_send_kb)
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()

# Этот хэндлер срабатывает на регистрацию пользователя
@router.message(F.text == LEXICON_RU['reg_b'], StateFilter(default_state))
async def process_reg(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_RU['reg_1'])
    await state.set_state(FSMFillForm.fill_name)


# Этот хэндлер срабатывает на ввод имени
@router.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha())
async def process_name(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(name=message.text)
    await message.answer(text=LEXICON_RU['reg_2'])
    # Устанавливаем состояние ожидания ввода номера авто
    await state.set_state(FSMFillForm.fill_car_number)


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_name))
async def warning_not_name(message: Message):
    await message.answer(text=LEXICON_RU['name_mistake'])

# Этот хэндлер будет срабатывать, если введен корректный номер авто
# и переводить в состояние описания ато
@router.message(StateFilter(FSMFillForm.fill_car_number))
async def process_fill_number(message: Message, state: FSMContext):
    data = replace_and_apper_number(message.text)
    if len(data) == 8:
        # Cохраняем номер в хранилище по ключу "number"
        await state.update_data(number=data)
        # Устанавливаем состояние ожидания описсааеинеия авто
        await message.answer(text=LEXICON_RU['reg_3'])
        await state.set_state(FSMFillForm.fill_rew)
    else:
        await message.answer(text=LEXICON_RU['mistake_3'])


@router.message(StateFilter(FSMFillForm.fill_rew))
async def process_fill_rew(message: Message, state: FSMContext):
    # Cохраняем описание по ключу "rew"
    # await state.update_data(rew=message.text, id=message.chat.id)
    await db_test()
    await commands.add_number((await state.get_data()).get("name"), (await state.get_data()).get("number"), message.text, message.chat.id)
    # user_dict[(await state.get_data()).get("number")] = await state.get_data()
    # Завершаем машину состояний
    await state.clear()
    # Устанавливаем состояние нейтральное
    await message.answer(text=LEXICON_RU['reg_4'], reply_markup=reg_search_send_kb)


# Этот хэндлер будет срабатывать, если во время ввода описания машины если
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_rew))
async def warning_bad_rew(message: Message):
    await message.answer(
        text=LEXICON_RU['mistake_2'])

# Этот хэндлер будет срабатывать на отправку команды /search_b
# и отправлять в чат данные о пользовелеле либо сообщение об отсутствии данных
@router.message(F.text == LEXICON_RU['search_b'], StateFilter(default_state))
async def process_search_car_by_number(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_RU['send'])
    await state.set_state(FSMFillForm.searching_number)

# Этот хэндлер будет выводить информацио авто по номеру.
@router.message(StateFilter(FSMFillForm.searching_number))
async def process_name(message: Message, state: FSMContext):

    # Отправляем пользователю анкету, если она есть в "базе данных"
    data = replace_and_apper_number(message.text)
    print(data)
    await db_test()
    car_data = await commands.select_car_number(data)
    if car_data is not None:
        print(car_data.name)
        await message.answer(text=f"Мошина с номером {car_data.number} принадлежит {car_data.name} описание машины {car_data.rew}. ")

    # if data in user_dict:
    #     await message.answer(
    #         text=f'Имя: {user_dict[data]["name"]}\n'
    #              f'номер: {user_dict[data]["number"]}\n'
    #              f'описание: {user_dict[data]["rew"]}\n'
    #              f'id: {user_dict[data]["id"]}\n', reply_markup=reg_search_send_kb)
        await state.clear()
    else:
        # Если анкеты пользователя в базе нет - предлагаем заполнить
        await message.answer(text=LEXICON_RU['not_found'])


# Этот хэндлер срабатывает на кнопку отправить сообщение
@router.message(F.text == LEXICON_RU['send_b'], StateFilter(default_state))
async def process_reg(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_RU['send'])
    await state.set_state(FSMFillForm.sent_message)


# Этот хэндлер срабатывает на ввод номера
@router.message(StateFilter(FSMFillForm.sent_message))
async def process_name(message: Message, state: FSMContext):
    global id_to_message
    # находим владельца по номеру:
    data = replace_and_apper_number(message.text)
    if data in user_dict:
        await message.answer(
            text=f'Имя: {user_dict[data]["name"]}\n'
                 f'номер: {user_dict[data]["number"]}\n'
                 f'описание: {user_dict[data]["rew"]}\n'
                 f'id: {user_dict[data]["id"]}\n')
        id_to_message = user_dict[data]["id"]
        await message.answer(text=f'Машина с номером{user_dict[data]["number"]} и описанием'
                                  f' {user_dict[data]["rew"]} найдена, введите сообщение для отправки ее владельцу:')
        # Устанавливаем состояние ожидания ввода сообщения автовладельцу
        await state.set_state(FSMFillForm.await_text_message)
    else:
        await message.answer(text=LEXICON_RU['not_found'], reply_markup=reg_search_send_kb)
        await state.clear()

# получаем доступ к токену для отправки сообщений
config: Config = load_config()

# Этот хэндлер срабатывает на ввод сообщения автовладельцу и пересылает сообщение
@router.message(StateFilter(FSMFillForm.await_text_message))
async def process_send_message(message:Message, state: FSMContext):
    global id_to_message
    if message.text:
        url = f'https://api.telegram.org/bot{config.tg_bot.token}/sendMessage?chat_id={id_to_message}&text={message.text}'
        response = requests.get(url)
        await message.answer(text=LEXICON_RU['message_poisoned'], reply_markup=reg_search_send_kb)
        await state.clear()


