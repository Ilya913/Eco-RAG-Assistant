import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from src.config import cfg
from src.rag import rag_service 

logging.basicConfig(level=logging.INFO)

bot = Bot(token=cfg.BOT_TOKEN)
dp = Dispatcher()

class BotState(StatesGroup):
    generating = State()

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    await message.answer(
        "🌿 **Привет! Я твой цифровой помощник по Экологии.**\n\n"
        "Я прочитал все загруженные лекции и методички. "
        "Готов помочь тебе с определениями, понятиями и теорией.\n\n"
        "⚠️ **Важно:** Я не запоминаю контекст беседы. Пожалуйста, задавай полные вопросы.\n"
        "**Примеры вопросов:**\n"
        "🔹 *Что такое популяция?*\n"
        "🔹 *Кем был предложен термин биоценоз?*",
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(BotState.generating)
async def anti_spam_handler(message: types.Message):
    await message.reply("⏳ Подожди, я еще думаю над прошлым вопросом... Не торопи меня.")

@dp.message(F.text)
async def handle_question(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    question = message.text

    await state.set_state(BotState.generating)
    
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        logging.info(f"User {user_id} asked: {question}")
        
        response = await rag_service.get_answer(question)
        
        await message.answer(response)
        
    except Exception as e:
        logging.error(f"Error processing question: {e}")
        await message.answer("😔 Произошла ошибка. Попробуй позже.")
        
    finally:
        await state.clear()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())