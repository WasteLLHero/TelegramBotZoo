from aiogram.utils.keyboard import InlineKeyboardBuilder  
from aiogram.types import InlineKeyboardButton 

start_quiz_keyboard_builder = InlineKeyboardBuilder()

start_quiz_keyboard_builder.add(InlineKeyboardButton(
    text="Запустить викторину!",  
    callback_data="start_quiz"  
))

accept_quiz_keyboard_builder = InlineKeyboardBuilder()

accept_quiz_keyboard_builder.add(InlineKeyboardButton(
    text="Начнем!",  
    callback_data="accept_quiz"  
))
accept_quiz_keyboard_builder.add(InlineKeyboardButton(
    text="Отмена!",  
    callback_data="cancel_quiz"  
))
