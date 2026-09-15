import os
import django
import asyncio
import re

# --- 1. НАСТРОЙКА DJANGO ---
# Убедись, что 'myproject.settings' совпадает с названием твоего проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

# --- 2. ИНИЦИАЛИЗАЦИЯ ---
API_TOKEN = '8747793908:AAFw4WKnO9LSeR94ZSvFQzcASFZmxtFp8So'
ADMIN_ID = 370584663  # ID закройщика добавлен

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


class OrderSteps(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_look = State()
    waiting_for_fabric = State()
    measure_1 = State()
    measure_2 = State()
    measure_3 = State()
    measure_4 = State()
    measure_5 = State()
    measure_6 = State()
    waiting_for_address = State()


# --- КЛАВИАТУРЫ ---
def get_main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Начать заказ")], [KeyboardButton(text="Начать заново")]],
        resize_keyboard=True
    )


def get_back_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⬅️ Назад")]], resize_keyboard=True)


def get_phone_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить контакт", request_contact=True)],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )


@sync_to_async
def save_final_order(data, u_id, u_username):
    from mainapp.models import Order
    measures = (f"1:{data.get('m1')}, 2:{data.get('m2')}, 3:{data.get('m3')}, "
                f"4:{data.get('m4')}, 5:{data.get('m5')}, 6:{data.get('m6')}")
    comment = f"Тел: {data.get('phone')}. Образ: {data.get('look')}. Доставка: {data.get('delivery_info')}"
    return Order.objects.create(
        client_name=data.get('name'),
        telegram_id=u_id,
        telegram_username=u_username or "Private",
        selected_fabric=data.get('fabric'),
        measurements_data=measures,
        client_comment=comment
    )


async def send_step(message, img_name, caption, next_state, state: FSMContext):
    photo_path = os.path.join(os.getcwd(), "static", "images", img_name)
    if os.path.exists(photo_path):
        await message.answer_photo(types.FSInputFile(photo_path), caption=caption, reply_markup=get_back_kb())
    else:
        await message.answer(f"⚠️ {caption}", reply_markup=get_back_kb())
    await state.set_state(next_state)


# --- 3. ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
@dp.message(F.text == "Начать заново")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Добро пожаловать в SHOHA KOSTUM. Создадим ваш идеальный костюм.", reply_markup=get_main_kb())


@dp.message(F.text == "Начать заказ")
async def start_order(message: types.Message, state: FSMContext):
    await message.answer("Введите ваше ФИО:", reply_markup=get_back_kb())
    await state.set_state(OrderSteps.waiting_for_name)


@dp.message(OrderSteps.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await cmd_start(message, state)
        return
    await state.update_data(name=message.text)
    await message.answer("Введите номер телефона или нажмите кнопку ниже:", reply_markup=get_phone_kb())
    await state.set_state(OrderSteps.waiting_for_phone)


@dp.message(OrderSteps.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await message.answer("Введите ваше ФИО:", reply_markup=get_back_kb())
        await state.set_state(OrderSteps.waiting_for_name)
        return

    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = re.sub(r'[^\d+]', '', message.text)
        if not (phone.isdigit() or (phone.startswith('+') and phone[1:].isdigit())):
            await message.answer("❌ Ошибка! Введите корректный номер (только цифры):")
            return

    await state.update_data(phone=phone)
    await message.answer("Для какого случая костюм? (Свадьба, Работа, Вечерний выход)", reply_markup=get_back_kb())
    await state.set_state(OrderSteps.waiting_for_look)


@dp.message(OrderSteps.waiting_for_look)
async def process_look(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await message.answer("Введите номер телефона:", reply_markup=get_phone_kb())
        await state.set_state(OrderSteps.waiting_for_phone)
        return
    await state.update_data(look=message.text)
    await message.answer("Какую ткань выбрали? (Или напишите 'Нужен совет')", reply_markup=get_back_kb())
    await state.set_state(OrderSteps.waiting_for_fabric)


@dp.message(OrderSteps.waiting_for_fabric)
async def process_fabric(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await message.answer("Для какого случая костюм?", reply_markup=get_back_kb())
        await state.set_state(OrderSteps.waiting_for_look)
        return

    if "совет" in message.text.lower():
        data = await state.get_data()
        look = data.get('look', '').lower()
        advice = "🤖 **Стилист:** Для вашего случая лучше всего подойдет темно-синяя итальянская Евро-шерсть."
        if "свадьб" in look:
            advice = "🤖 **Стилист:** Для свадьбы рекомендую шерсть вискоза темно-синего и темно-зеленого цвета."
        await message.answer(advice)
        return

    await state.update_data(fabric=message.text)
    await send_step(message, "contact1.jpg", "Шаг 1: Плечи. Введите значение (см):", OrderSteps.measure_1, state)


@dp.message(OrderSteps.measure_1)
async def m1(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await message.answer("Какую ткань выбрали?", reply_markup=get_back_kb())
        await state.set_state(OrderSteps.waiting_for_fabric)
        return
    await state.update_data(m1=message.text)
    await send_step(message, "contact2.jpg", "Шаг 2: Обхват груди. Введите (см):", OrderSteps.measure_2, state)


@dp.message(OrderSteps.measure_2)
async def m2(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await send_step(message, "contact1.jpg", "Шаг 1: Плечи. Введите значение (см):", OrderSteps.measure_1, state)
        return
    await state.update_data(m2=message.text)
    await send_step(message, "contact3.jpg", "Шаг 3: Бицепс. Введите (см):", OrderSteps.measure_3, state)


@dp.message(OrderSteps.measure_3)
async def m3(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await send_step(message, "contact2.jpg", "Шаг 2: Обхват груди. Введите (см):", OrderSteps.measure_2, state)
        return
    await state.update_data(m3=message.text)
    await send_step(message, "contact4.jpg", "Шаг 4: Талия. Введите (см):", OrderSteps.measure_4, state)


@dp.message(OrderSteps.measure_4)
async def m4(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await send_step(message, "contact3.jpg", "Шаг 3: Бицепс. Введите (см):", OrderSteps.measure_3, state)
        return
    await state.update_data(m4=message.text)
    await send_step(message, "contact5.jpg", "Шаг 5: Рукав. Введите (см):", OrderSteps.measure_5, state)


@dp.message(OrderSteps.measure_5)
async def m5(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await send_step(message, "contact4.jpg", "Шаг 4: Талия. Введите (см):", OrderSteps.measure_4, state)
        return
    await state.update_data(m5=message.text)
    await send_step(message, "contact6.jpg", "Шаг 6: Длина. Введите (см):", OrderSteps.measure_6, state)


@dp.message(OrderSteps.measure_6)
async def m6(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await send_step(message, "contact5.jpg", "Шаг 5: Рукав. Введите (см):", OrderSteps.measure_5, state)
        return
    await state.update_data(m6=message.text)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Пункт BTS (Бесплатно)", callback_data="dev_bts")],
        [InlineKeyboardButton(text="🏠 Доставка на дом", callback_data="dev_home")]
    ])
    await message.answer("Мерки приняты! Выберите способ доставки:", reply_markup=kb)


@dp.callback_query(F.data == "dev_bts")
async def bts_info(callback: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Бот BTS 🚀", url="https://t.me/btsrobot")]])
    await callback.message.answer("Найдите адрес в @btsrobot и напишите его сюда текстом:", reply_markup=kb)
    await state.set_state(OrderSteps.waiting_for_address)
    await callback.answer()


@dp.callback_query(F.data == "dev_home")
async def home_info(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите адрес доставки:", reply_markup=get_back_kb())
    await state.set_state(OrderSteps.waiting_for_address)
    await callback.answer()


@dp.message(OrderSteps.waiting_for_address)
async def final(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await m6(message, state)
        return

    await state.update_data(delivery_info=message.text)
    data = await state.get_data()

    # 1. Сохранение в БД
    await save_final_order(data, message.from_user.id, message.from_user.username)

    # 2. Формирование отчета для закройщика
    report = (
        f"👔 **НОВЫЙ ЗАКАЗ!**\n\n"
        f"👤 Клиент: {data.get('name')}\n"
        f"📞 Тел: {data.get('phone')}\n"
        f"🧵 Ткань: {data.get('fabric')}\n"
        f"📍 Адрес: {data.get('delivery_info')}\n\n"
        f"📏 **Мерки:**\n"
        f"Плечи: {data.get('m1')} | Грудь: {data.get('m2')}\n"
        f"Бицепс: {data.get('m3')} | Талия: {data.get('m4')}\n"
        f"Рукав: {data.get('m5')} | Длина: {data.get('m6')}"
    )

    # 3. Отправка уведомления закройщику
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=report, parse_mode="Markdown")
    except Exception as e:
        print(f"Ошибка уведомления: {e}")

    # 4. Ответ клиенту
    await message.answer("✅ **Заказ принят!**\nЗакройщик свяжется с вами в ближайшее время.",
                         reply_markup=get_main_kb())
    await state.clear()


async def main():
    print("Бот SHOHA KOSTUM запущен и готов к работе...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())