# bot.py

import os
import requests
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import asyncio

# Переменные из окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Проверить ОСАГО")],
        [KeyboardButton(text="⚖️ Проверить штрафы")],
        [KeyboardButton(text="⬇️ Скачать ОСАГО")],
        [KeyboardButton(text="📝 Оформить ОСАГО")],
    ],
    resize_keyboard=True
)

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Добро пожаловать в бот страховых услуг!", reply_markup=main_menu)


# --- Функция: Проверка ОСАГО ---
@dp.message(F.text == "🔍 Проверить ОСАГО")
async def prompt_vin(message: Message):
    await message.reply("Введите VIN-номер автомобиля для проверки ОСАГО:")


@dp.message()
async def check_osago(message: Message):
    vin = message.text.strip().upper()

    if len(vin) != 17:
        await message.reply("❗ VIN должен содержать 17 символов.")
        return

    url = f"https://service.api-assist.com/parser/osago_api/?key= {API_KEY}&vin={vin}"
    try:
        response = requests.get(url)
        data = response.json()

        if data.get("result"):
            result = data["result"]
            answer = (
                "✅ Полис ОСАГО найден:\n"
                f"Серия и номер: {result.get('policyNumber', 'Не указано')}\n"
                f"Дата начала действия: {result.get('dateStart', 'Не указано')}\n"
                f"Дата окончания: {result.get('dateEnd', 'Не указано')}\n"
                f"Страховая компания: {result.get('insurerName', 'Не указано')}"
            )
        else:
            answer = "❌ Полис ОСАГО не найден."

    except Exception as e:
        answer = f"⚠ Ошибка при проверке ОСАГО: {e}"

    await message.reply(answer)


# --- Функция: Проверка штрафов ---
@dp.message(F.text == "⚖️ Проверить штрафы")
async def prompt_fines(message: Message):
    await message.reply("Введите госномер (например, С328ОА39) и номер СТС через пробел:")


@dp.message(F.text.contains(" "))
async def check_fines(message: Message):
    text = message.text.strip()
    parts = text.split()

    if len(parts) < 2:
        await message.reply("❗ Неверный формат. Введите госномер и СТС через пробел.")
        return

    reg_number, sts = parts[0], parts[1]
    url = f"https://service.api-assist.com/parser/fines_api/?key= {API_KEY}&regNumber={reg_number}&sts={sts}"

    try:
        response = requests.get(url)
        data = response.json()

        if data.get("fines"):
            answer = "⚖️ Найдены штрафы:\n"
            for fine in data["fines"]:
                answer += (
                    f"\n▫️ Номер постановления: {fine.get('number')}\n"
                    f"▫️ Дата: {fine.get('date')}\n"
                    f"▫️ Сумма: {fine.get('sum')} руб.\n"
                    f"▫️ Описание: {fine.get('description')}\n"
                )
        elif data.get("message"):
            answer = f"ℹ️ {data['message']}"
        else:
            answer = "✅ Штрафов нет"

    except Exception as e:
        answer = f"⚠ Ошибка при проверке штрафов: {e}"

    await message.reply(answer)


# --- Заглушка: Скачать ОСАГО ---
@dp.message(F.text == "⬇️ Скачать ОСАГО")
async def download_osago(message: Message):
    await message.reply("Здесь будет возможность скачать ваш полис ОСАГО в формате PDF.")


# --- Заглушка: Оформить ОСАГО ---
@dp.message(F.text == "📝 Оформить ОСАГО")
async def create_osago(message: Message):
    await message.reply("Перейдите по ссылке ниже, чтобы оформить новый полис ОСАГО:\n🔗 https://example.com/osago-form ")


# Запуск бота
if __name__ == '__main__':
    asyncio.run(dp.start_polling())
