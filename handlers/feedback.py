from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import config
from database import save_feedback, get_setting
from keyboards.default import get_main_keyboard, get_cancel_keyboard

router = Router(name="feedback_router")

class FeedbackStates(StatesGroup):
    waiting_for_message = State()

@router.message(F.text.in_(["✍️ Fikr / Taklif", "/feedback", "Fikr"]))
async def feedback_start(message: Message, state: FSMContext):
    await state.set_state(FeedbackStates.waiting_for_message)
    await message.answer(
        "✍️ <b>Alixan Fast Food mijozlar xizmati</b>\n\n"
        "Biz uchun har bir mijozning fikri va taklifi juda muhim! "
        "Taomlarimiz, xizmat ko'rsatish sifati yoki yetkazib berish bo'yicha fikringizni yozib qoldiring.\n\n"
        "<i>Xabaringiz to'g'ridan-to'g'ri restoran rahbariyatiga yetkaziladi.</i>\n\n"
        "Bekor qilish uchun ❌ Bekor qilish tugmasini bosing.",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )

@router.message(FeedbackStates.waiting_for_message, F.text == "❌ Bekor qilish")
async def feedback_cancel(message: Message, state: FSMContext):
    await state.clear()
    miniapp_url = await get_setting("mini_app_url", config.MINI_APP_URL)
    await message.answer(
        "Amal bekor qilindi.",
        reply_markup=get_main_keyboard(miniapp_url, message.from_user.id if message.from_user else None)
    )

@router.message(FeedbackStates.waiting_for_message)
async def feedback_received(message: Message, state: FSMContext, bot: Bot):
    feedback_text = message.text or message.caption or "Rasm yoki media yuborildi"
    user = message.from_user
    user_info = f"@{user.username}" if user and user.username else (user.full_name if user else "Foydalanuvchi")
    user_id = user.id if user else 0

    await save_feedback(user_id, feedback_text)
    await state.clear()

    miniapp_url = await get_setting("mini_app_url", config.MINI_APP_URL)
    await message.answer(
        "✅ <b>Fikringiz uchun katta rahmat!</b>\n\n"
        "Xabaringiz qabul qilindi va mutasaddilarga yetkazildi. "
        "Sizga yanada sifatliroq xizmat ko'rsatishdan doimo xursandmiz!",
        parse_mode="HTML",
        reply_markup=get_main_keyboard(miniapp_url, user_id)
    )

    # Forward or notify admins
    admin_notify = (
        "📩 <b>Yangi mijoz fikri / taklifi!</b>\n\n"
        f"👤 <b>Yuboruvchi:</b> {user_info} (ID: <code>{user_id}</code>)\n"
        f"💬 <b>Xabar:</b>\n{feedback_text}"
    )
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_notify, parse_mode="HTML")
        except Exception:
            pass
