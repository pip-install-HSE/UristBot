import logging
import os
import logging
import re

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.contrib.fsm_storage.mongo import MongoStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hlink, hide_link, link
from aiogram.types import InputFile

print(os.getenv)

questions = ['🤟 Профиль', '🔍 Искать статью', '📄 Документ', '✊ Поддержка']
documents = ['Договор по оказанию работ']
contracts = ['Договор по оказанию услуг',
             'Договор подряда', 'Договор поручения']

API_TOKEN = ''

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
# storage = MongoStorage('exchange_mongo')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

id_chat_support = 0


async def soft_state_finish(state: FSMContext):
    fields = ['action']
    data = await state.get_data()
    data = {key: value for key, value in data.items() if key not in fields}
    await state.set_data(data)
    await state.set_state(None)


@dp.message_handler(commands=['Start', 'Help'], state="*")
async def main_menu(
        message: [types.Message, types.CallbackQuery], state: FSMContext,
        message_text='Добро пожаловать в Телеграм-бот для юристов!\n'
                     'Выберите пункт меню:'):
    await soft_state_finish(state)
    await bot.send_message(
        chat_id=message.chat.id,
        text=message_text,
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton('🤟 Профиль')],
                [KeyboardButton('🔍 Искать статью')],
                [KeyboardButton('📄 Документ')],
                [KeyboardButton('✊ Поддержка')]
            ],
            resize_keyboard=True,
            one_time_keyboard=True),
        parse_mode="HTML",
        disable_web_page_preview=True
    )


# Назад если мы нажали назад из  первого шага
# '🤟 Профиль', '🔍 Искать статью', '📄 Документ', '✊ Поддержка'
@dp.callback_query_handler(
    text='◀️ Назад',state=['🤟 Профиль',
                           '🔍 Искать статью','📄 Документ', '✊ Поддержка'])
async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(action=None)
    await callback.message.delete()
    await main_menu(callback.message, state)


# код если нажали Профиль
@dp.message_handler(Text(equals=['🤟 Профиль']), state='*')
async def profile(message: types.Message, state: FSMContext):
    await state.update_data(action=message.text)
    await message.answer(
        text=f'Название компании: <b>Компания</b>\n'
             f'Реквизиты: <b>Реквизиты</b>',
        parse_mode='HTML',
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=elem, callback_data=elem)]
                for elem in ['◀️ Назад']
            ]
        )
    )
    await state.set_state(message.text)


# код если нажали 🔍 Искать статью
@dp.message_handler(Text(equals=['🔍 Искать статью']), state='*')
async def search_article(message: types.Message, state: FSMContext):
    await state.update_data(action=message.text)
    await message.answer(
        text=f'<b>*Раздел находится в разработке*</b>',
        parse_mode='HTML',
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=elem, callback_data=elem)]
                for elem in ['◀️ Назад']
            ]
        )
    )
    await state.set_state(message.text)


# код если нажали 📄 Документ
@dp.message_handler(Text(equals=['📄 Документ']), state='*')
async def select_document(message: types.Message, state: FSMContext):
    await state.update_data(action=message.text)
    await message.answer(
        text=f'Выберите документ:',
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=elem, callback_data=elem)]
                for elem in documents + ['◀️ Назад']
            ]
        ),
    )
    await state.set_state(message.text)


# Назад если выбрали документ
@dp.callback_query_handler(text='◀️ Назад', state=documents)
async def back_to_select_document(
        callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(document=None)
    await callback.message.edit_text(
        text=f'Выберите документ:',
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=elem, callback_data=elem)]
                for elem in documents + ['◀️ Назад']
            ]
        ),
    )
    await state.set_state((await state.get_data())['action'])


# Код если выбрали Документ
@dp.callback_query_handler(text=documents, state=['📄 Документ'])
async def select_contract(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(document=callback.data)

    await callback.message.edit_text(
        text=f'Выберите договор:', parse_mode='HTML',
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=elem, callback_data=elem)]
                for elem in contracts + ['◀️ Назад', '⤴️ Главное меню']
            ]
        ),
    )
    await state.set_state(callback.data)


# Код если выбрались из контракта назад
@dp.callback_query_handler(text='◀️ Назад', state=contracts)
async def back_to_select_contract(callback: types.CallbackQuery,
                                  state: FSMContext):
    await state.update_data(contract=None)

    await callback.message.edit_text(
        text=f'Выберите договор:', parse_mode='HTML',
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=elem, callback_data=elem)]
                for elem in contracts + ['◀️ Назад', '⤴️ Главное меню']
            ]
        ),
    )
    await state.set_state((await state.get_data())['document'])


# Код если выбрали контракт (здесь надо дорабатывать)
@dp.callback_query_handler(text=contracts, state=documents)
async def select_forward(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(contract=callback.data)

    await callback.message.edit_text(
        text=f'<b>*Раздел находится в разработке*</b>', parse_mode='HTML',
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=elem, callback_data=elem)]
                for elem in ['◀️ Назад', '⤴️ Главное меню']
            ]
        ),
    )
    await state.set_state(callback.data)


# Код, если выбрали ✊ Поддержка
@dp.message_handler(Text(equals='✊ Поддержка'), state='*')
async def support(message: types.Message, state: FSMContext):
    await state.update_data(action=message.text)
    await message.answer(
        text='<b>*Раздел находится в разработке*</b>',
        parse_mode='HTML',
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=elem, callback_data=elem)]
                for elem in ['◀️ Назад']
            ]
        ))
    await state.set_state(message.text)


@dp.callback_query_handler(text="⤴️ Главное меню", state="*")
async def enter_NO_back_to_mian_menu(callback: types.CallbackQuery,
                                     state: FSMContext):
    await soft_state_finish(state)
    await callback.message.delete()
    await main_menu(callback.message, state)


#
# @dp.callback_query_handler(text="◀️ Назад", state="📩 Поддержка")
# async def enter_NO_back_to_mian_menu(callback: types.CallbackQuery,
#                                      state: FSMContext):
#     await soft_state_finish(state)
#     await callback.message.delete()
#     await main_menu(callback.message, state)


@dp.message_handler(state='📩 Поддержка')
async def support_message(message: types.Message, state: FSMContext):
    await main_menu(message, state,
                    "Спасибо за обращение! Ответ придет в ближайшее время.")
    user = message.from_user
    await bot.send_message(
        text=f"Имя пользователя: {user.first_name}"
             f" {user.last_name if 'last_name' in user else ''}\n"
             f"username:  @{user.username if 'username' in user else None}\n"
             f"id: {user.id}\n\n"
             f"Текст вопроса: {message.text}",
        chat_id=id_chat_support
    )


@dp.message_handler(lambda message: message.chat.id != message.from_user.id)
async def chats_handler(message: types.Message):
    if message.chat.id == id_chat_support:
        if 'reply_to_message' in message:
            user_id = re.findall(r"id: (\d+)",
                                 message.reply_to_message.text)[0]
            await bot.send_message(
                chat_id=user_id,
                text=f"<b>Ответ от менеджера</b> "
                     + message.from_user.first_name
                + ' ' + message.from_user.last_name + ':' + '\n'
                f"{message.text}",
                parse_mode="HTML"
            )
            await message.reply(
                text='Ответ отправлен',
                reply=True
            )


@dp.callback_query_handler(state='*')
async def any_callback(callback: types.CallbackQuery, state: FSMContext):
    print('No one callback handler')
    print(f"{await state.get_state()=}")
    print(f"{callback.data=}")
    await callback.message.edit_reply_markup(InlineKeyboardMarkup())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
