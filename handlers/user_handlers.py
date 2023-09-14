from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, StatesGroup
from aiogram.types import Message
from keyboards.keyboard_ru import reg_search_send_kb, next_kb, next_1_kb, reg_finish_kb
from lexicon.lexicon_ru import LEXICON_RU
from aiogram.fsm.storage.redis import RedisStorage, Redis
import requests


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
    fill_rew = State()      # Состояние ожидания ввода машины
    searching_number = State()      # Состояние ожидания ввода машины
    sent_message = State()      # Состояние ожидания ввода машины
    await_text_message = State()      # Состояние ожидания ввода машины


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'], reply_markup=reg_search_send_kb)


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'), StateFilter(default_state))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'], reply_markup=reg_search_send_kb)


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что эта команда работает внутри машины состояний
@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(text='Отменять нечего. Вы вне машины состояний\n\n'
                              'Чтобы перейти к заполнению анкеты - '
                              'отправьте команду /fillform')


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text='Вы вышли из машины состояний\n\n'
                              'Чтобы снова перейти к заполнению анкеты - '
                              'отправьте команду /fillform')
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
    await message.answer(text='Спасибо!\n\nА теперь введите ваш номер авто  как в примере 8682AZ-3')
    # Устанавливаем состояние ожидания ввода номера авто
    await state.set_state(FSMFillForm.fill_car_number)


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_name))
async def warning_not_name(message: Message):
    await message.answer(text='То, что вы отправили не похоже на имя\n\n'
                              'Пожалуйста, введите ваше имя\n\n'
                              'Если вы хотите прервать заполнение анкеты - '
                              'отправьте команду /cancel')

# Этот хэндлер будет срабатывать, если введен корректный номер авто
# и переводить в состояние описания ато
@router.message(StateFilter(FSMFillForm.fill_car_number))
async def process_fill_number(message: Message, state: FSMContext):
    # Cохраняем номер в хранилище по ключу "number"
    await state.update_data(number=message.text)
    # Устанавливаем состояние ожидания выбора пола
    await message.answer(text='Спасибо!\n\nА теперь коротко опишите ваш авто')
    await state.set_state(FSMFillForm.fill_rew)

@router.message(StateFilter(FSMFillForm.fill_rew))
async def process_fill_rew(message: Message, state: FSMContext):
    # Cохраняем описание по ключу "rew"
    await state.update_data(rew=message.text, id=message.chat.id)
    user_dict[(await state.get_data()).get("number")] = await state.get_data()
    print(user_dict)
    # Завершаем машину состояний
    await state.clear()
    # Устанавливаем состояние нейтральное
    await message.answer(text='Спасибо!\n\nА регистрация завершена', reply_markup=reg_search_send_kb)


# Этот хэндлер будет срабатывать, если во время ввода описания машины если
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_rew))
async def warning_not_age(message: Message):
    await message.answer(
        text='Mistake!!!')

# Этот хэндлер будет срабатывать на отправку команды
# и отправлять в чат данные анкеты, либо сообщение об отсутствии данных
@router.message(F.text == LEXICON_RU['search_b'], StateFilter(default_state))
async def process_search_car_by_number(message: Message, state: FSMContext):
    await message.answer(text='введите номер:')
    await state.set_state(FSMFillForm.searching_number)

# Этот хэндлер будет выводить информацио авто по номеру.
@router.message(StateFilter(FSMFillForm.searching_number))
async def process_name(message: Message, state: FSMContext):

    # Отправляем пользователю анкету, если она есть в "базе данных"
    if message.text in user_dict:
        await message.answer(
            text=f'Имя: {user_dict[message.text]["name"]}\n'
                    f'номер: {user_dict[message.text]["number"]}\n'
                    f'описание: {user_dict[message.text]["rew"]}\n'
                    f'описание: {user_dict[message.text]["id"]}\n', reply_markup=reg_search_send_kb)
        await state.clear()
    else:
        # Если анкеты пользователя в базе нет - предлагаем заполнить
        await message.answer(text='Такого номера в базе нет')


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
    if message.text in user_dict:
        await message.answer(
            text=f'Имя: {user_dict[message.text]["name"]}\n'
                    f'номер: {user_dict[message.text]["number"]}\n'
                    f'описание: {user_dict[message.text]["rew"]}\n'
                    f'id: {user_dict[message.text]["id"]}\n')
        id_to_message = user_dict[message.text]["id"]
        await message.answer(text=f'Машина с номером{user_dict[message.text]["number"]} и описанием'
                              f' {user_dict[message.text]["rew"]} найдена, введите сообщение для отправки ее владельцу:')
    # Устанавливаем состояние ожидания ввода texts
        await state.set_state(FSMFillForm.await_text_message)
    else:
        await message.answer(text=f'машины с таким номером в базе нет', reply_markup=reg_search_send_kb)
        await state.clear()


# Этот хэндлер срабатывает на ввод texts
@router.message(StateFilter(FSMFillForm.await_text_message))
async def process_send_message(message:Message, state: FSMContext):
    global id_to_message
    if message.text:
        print(id_to_message)
        print(message.text)
        url = f'https://api.telegram.org/bot5956279665:AAGl1G03Y2uxZmVG6-0afYujfbtuT2ySC1k/sendMessage?chat_id={id_to_message}&text={message.text}'
        response = requests.get(url)
        await message.answer(text=f'Ваше сообщение отправлено!', reply_markup=reg_search_send_kb)
        await state.clear()
