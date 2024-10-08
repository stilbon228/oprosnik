from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove, KeyboardButtonPollType, PollAnswer)

BOT_TOKEN = '6716269950:AAFtw0N75Rz9Ce4l0Xk7k__fN7b77ZXu1iQ'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Создаем кнопки
btn_1 = KeyboardButton(text='Создать опрос')
btn_2 = KeyboardButton(text='Создать викторину')

# Создаем объект клавиатуры
keyboard = ReplyKeyboardMarkup(
    keyboard=[[btn_1, btn_2]],
    resize_keyboard=True,
    input_field_placeholder='Тапай'
)

quiz_state = {}

@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text='Создать опрос или викторину?',
        reply_markup=keyboard
    )

# Обработчик для создания опроса
@dp.message(F.text == 'Создать опрос')
async def create_poll(message: Message):
    questions = [
        ("Когда вы родились?", ["вчера", "сегодня", "2005"]),
        ("что кушал?", ["пиво", "рыбку", "ПИвко"]),
        ("ЗОЖ?", ["да", "нет"])
    ]

    for question, options in questions:
        await message.answer_poll(
            question=question,
            options=options,
            is_anonymous=False
        )

# Обработчик для создания викторины
@dp.message(F.text == 'Создать викторину')
async def create_quiz(message: Message):
    questions = [
        ("В каком году?", ["да", "2003", "нет"], 1),
        ("Сколько стоит Пиво?", ["100руб", "200руб", "300руб"], 0),
        ("Sin p/2", ["ШО?", ":)", "ага"], 0),
    ]

    user_id = message.from_user.id
    quiz_state[user_id] = {
        'current_question': 0,
        'correct_answers': 0,
        'questions': questions,
        'user_answers': []  # Список для хранения ответов пользователя
    }

    await ask_question(user_id)

async def ask_question(user_id):
    questions = quiz_state[user_id]['questions']
    current_question = quiz_state[user_id]['current_question']

    if current_question < len(questions):
        question, options, correct_index = questions[current_question]
        await bot.send_poll(
            chat_id=user_id,
            question=question,
            options=options,
            is_anonymous=False,
            type='quiz',
            correct_option_id=correct_index
        )
    else:
        # Завершение викторины
        correct_answers = quiz_state[user_id]['correct_answers']
        user_answers = quiz_state[user_id]['user_answers']
        questions = quiz_state[user_id]['questions']

        result_message = f"Вы ответили правильно на {correct_answers} из {len(questions)} вопросов.\n\n"
        for i, (question, options, correct_index) in enumerate(questions):
            user_answer = options[user_answers[i]]
            correct_answer = options[correct_index]
            result_message += f"Вопрос: {question}\n"
            result_message += f"Ваш ответ: {user_answer}\n"
            result_message += f"Правильный ответ: {correct_answer}\n\n"

        await bot.send_message(
            chat_id=user_id,
            text=result_message
        )
        del quiz_state[user_id]

@dp.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer):
    user_id = poll_answer.user.id
    if user_id in quiz_state:
        current_question = quiz_state[user_id]['current_question']
        questions = quiz_state[user_id]['questions']

        if poll_answer.option_ids[0] == questions[current_question][2]:
            quiz_state[user_id]['correct_answers'] += 1

        quiz_state[user_id]['user_answers'].append(poll_answer.option_ids[0])
        quiz_state[user_id]['current_question'] += 1
        await ask_question(user_id)

if __name__ == '__main__':
    dp.run_polling(bot)