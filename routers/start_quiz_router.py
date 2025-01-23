import asyncio
from urllib.parse import quote_plus
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F
import logging
from decouple import config
from async_requests import ArequestGetJson, ArequestPost
from aiogram.utils.keyboard import InlineKeyboardBuilder  
from aiogram.types import InlineKeyboardButton 
from helpers.simulate_typing import simulate_typing

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuizState(StatesGroup):
    data = State()  # Данные викторины
    answers = State()  # Ответы пользователя

start_quiz_router = Router()

# Функция для создания клавиатуры с вариантами ответа
def generate_options_keyboard(options):
    keyboard_buttons = [InlineKeyboardButton(text=option, callback_data=option) for option in options]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[keyboard_buttons], row_width=2)
    return keyboard

@start_quiz_router.callback_query(F.data == "start_quiz")
async def start_quiz_message(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    typing_task = asyncio.create_task(simulate_typing(callback.message))
    data = await ArequestPost(f"{config('url')}/api/zoo/generate-quiz")

    await state.update_data(quiz_data=data)
    question = data[0]
    options = question["options"]
    keyboard = generate_options_keyboard(options)
    
    msg = await callback.message.edit_text(f"Поехали 🏎️💨, Вопрос #{question['number']}: {question['question']}", reply_markup=keyboard)
    await state.update_data(message_for_edit = msg)
    typing_task.cancel()


@start_quiz_router.callback_query(F.data != "support")
async def handle_answer(callback_query: CallbackQuery, state: FSMContext):
    logger.info(f"callback_query = {callback_query.data}")
    current_data = await state.get_data()
    data = current_data.get("quiz_data", [])
    answers = current_data.get("answers", [])
    question_index = len(answers)

    # Сохраняем ответ в нужном формате
    if question_index < len(data):
        selected_answer = callback_query.data
        question = data[question_index]
        
        # Записываем ответ в нужном формате
        answer = {
            "question": question["question"],
            "answer": selected_answer
        }
        answers.append(answer)
        await state.update_data(answers=answers)

        # Переходим к следующему вопросу
        if question_index + 1 < len(data):
            next_question = data[question_index + 1]
            message_for_edit = current_data["message_for_edit"]
            if message_for_edit:
                msg = await callback_query.message.edit_text(
                    f"Вопрос #{next_question['number']}: {next_question['question']}",
                    reply_markup=generate_options_keyboard(next_question["options"])
                )
            else:
                # Отправляем новый вопрос, если сообщения еще нет для редактирования
                msg = await callback_query.message.answer(
                    f"Вопрос #{next_question['number']}: {next_question['question']}",
                    reply_markup=generate_options_keyboard(next_question["options"])
                )
            await state.update_data(message_for_edit = msg)

            # await callback_query.answer()  # Ответ на запрос
        else:
            # Все вопросы пройдены, показываем результат
            answers_text = "\n".join([f"{ans['question']} - {ans['answer']}" for ans in answers])
            logger.info(f"\n\nanswers full - {answers}\n\n")
            await callback_query.message.edit_text(f"Викторина завершена! Ваши ответы: \n{answers_text}")
            typing_task = asyncio.create_task(simulate_typing(callback_query.message))
            animal_response = await ArequestPost(f"{config('url')}/api/zoo/generate-animal-by-quiz", data={"answers": answers})
            typing_task.cancel()
            logger.info(f"{animal_response}")
            telegramUser = await ArequestGetJson(f"{config('url')}/api/zoo/telegram-user?telegramId={callback_query.from_user.id}")
            logger.info(f"telegramUser - {telegramUser}")
            final_response = {
                "tgId": callback_query.from_user.id,
                "telegramUser": telegramUser['id'],
                "answers": answers,
                "suggested_animal": animal_response["suggested_animal"],
                "reasoning": animal_response["reasoning"],
                "care_recommendations": animal_response["care_recommendations"]
            }
            quiz_result = await ArequestPost(f"{config('url')}/api/zoo/quiz-results/", json=final_response)
            logger.info(f"{quiz_result}")
            photo = await ArequestGetJson(f"https://api.unsplash.com/photos/random?query={animal_response['suggested_animal']}&client_id={config('unsplash_token')}")
            photo_url = photo['urls']['full']
            animal_result = animal_response['suggested_animal']
            habitat = animal_response['reasoning']['habitat_preference']
            activity = animal_response['reasoning']['activity_level']
            diet = animal_response['reasoning']['diet']
            social_life = animal_response['reasoning']['social_preference']

            # Текст и ссылки для шаринга
            share_text = f"Викторина завершена! Ваше животное: {animal_result}. Место обитания: {habitat}, активность: {activity}, питание: {diet}, образ жизни: {social_life}"
            encoded_text = quote_plus(share_text)
            vk_share_url = f"https://vk.com/share.php?url={photo_url}&title={encoded_text}"
            tg_share_url = f"https://t.me/share/url?url={photo_url}&text={encoded_text}"

            # Создание кнопок
            share_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="Поделиться в ВК", url=vk_share_url),
                    InlineKeyboardButton(text="Поделиться в ТГ", url=tg_share_url)
                ]
            ])

            # Отправка фото и сообщения с кнопками
            await callback_query.message.bot.send_photo(
                chat_id=callback_query.message.chat.id,
                photo=photo_url,
                caption=(
                    f"Викторина завершена!\n"
                    f"Наиболее подходящее вам животное: {animal_result}.\n"
                    f"Предпочтительно место для обитания: {habitat},\n"
                    f"уровень активности: {activity},\n"
                    f"предпочитаемая еда: {diet},\n"
                    f"образ жизни: {social_life}"
                ),
                reply_markup=share_keyboard
            )
            # await callback_query.message.answer(f"Викторина завершена!\nНаиболее подходящее вам животное: {animal_response['suggested_animal']}.\nПредпочтительно место для обитания: {animal_response['reasoning']['habitat_preference']},\nуровень активности: {animal_response['reasoning']['activity_level']},\nпредпочитаемая еда: {animal_response['reasoning']['diet']},\nобраз жизни: {animal_response['reasoning']['social_preference']}")
            await callback_query.message.answer(f"Рекомендации по уходу: {animal_response['care_recommendations']['exercise']}, {animal_response['care_recommendations']['diet']}, {animal_response['care_recommendations']['housing']}, {animal_response['care_recommendations']['attention']}, {animal_response['care_recommendations']['grooming']}, {animal_response['care_recommendations']['health']}", reply_markup=InlineKeyboardBuilder().add(InlineKeyboardButton(
                text="Попробовать снова!",  
                callback_data="start_quiz"  
            )).add(InlineKeyboardButton(text="Обратится в поддержку!",  
                callback_data="support")).as_markup())
