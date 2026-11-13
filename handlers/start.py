from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
import config
from database import add_or_update_user, get_setting, is_admin
from keyboards.default import get_main_keyboard
from keyboards.inline import get_welcome_inline

router = Router(name="start_router")

def get_start_caption(delivery_fee: str, work_hours: str) -> str:
    return (
        "👑 <b>ALIXAN FAST FOOD ga xush kelibsiz!</b>\n\n"
        "Kattaqo'rg'on shahridagi eng mazali va sifatli fast-food maskanining rasmiy botidasiz.\n\n"
        "✨ <b>Bizda har kuni siz uchun:</b>\n"
        "• 🌯 Maxsus tandirda pishirilgan Lavashlar va Donarlar\n"
        "• 🍔 Sersuv kotletli Burgerlar va Chikenlar\n"
        "• 🍗 Qarsildoq KFC va qovurilgan Frikalar\n"
        "• 🍕 Issiqqina va pishloqli Pitsalar\n"
        "• 🌭 To'yimli va betakror Hot-Doglar\n\n"
        f"🛵 <b>Yetkazib berish:</b> {delivery_fee}\n"
        f"<i>{config.DEFAULT_DELIVERY_EXTRA}</i>\n"
        f"⏰ <b>Ish vaqti:</b> {work_hours}\n\n"
        "📞 <b>Buyurtma va aloqa uchun:</b>\n"
        "• +998910333393\n"
        "• +998904477999\n"
        "• +998996787977\n\n"
        f"📍 <b>Manzil:</b> {config.DEFAULT_ADDRESS}\n\n"
        "👇 <b>Buyurtma berish uchun pastdagi «Alixan Menu» tugmasini bosing:</b>"
    )

@router.message(CommandStart())
async def command_start_handler(message: Message):
    user = message.from_user
    user_id = user.id if user else 0
    if user:
        await add_or_update_user(user.id, user.username, user.full_name)

    miniapp_url = await get_setting("mini_app_url", config.MINI_APP_URL)
    delivery_fee = await get_setting("delivery_fee", config.DEFAULT_DELIVERY_PRICE)
    work_hours = await get_setting("work_hours", config.DEFAULT_WORK_HOURS)

    caption = get_start_caption(delivery_fee, work_hours)

    photo_path = config.IMAGES_DIR / "icon_welcome.jpg"
    if not photo_path.exists():
        photo_path = config.IMAGES_DIR / "logo.png"

    is_admin_user = await is_admin(user_id)
    reply_kb = get_main_keyboard(miniapp_url, user_id=user_id, is_admin_user=is_admin_user)
    inline_kb = get_welcome_inline(miniapp_url)

    if photo_path.exists():
        await message.answer_photo(
            photo=FSInputFile(str(photo_path)),
            caption=caption,
            parse_mode="HTML",
            reply_markup=inline_kb
        )
        await message.answer(
            "🍔 <b>Alixan menusini oching va buyurtma bering:</b>",
            parse_mode="HTML",
            reply_markup=reply_kb
        )
    else:
        await message.answer(
            caption,
            parse_mode="HTML",
            reply_markup=inline_kb
        )
        await message.answer(
            "🍔 <b>Alixan menusini oching va buyurtma bering:</b>",
            parse_mode="HTML",
            reply_markup=reply_kb
        )

ADMIN_COMMANDS = {
    "⚙️ Admin Panel", "📊 Statistika", "👥 Kimlar foydalanmoqda", "👥 Foydalanuvchilar",
    "📢 Foydalanuvchilarga xabar", "📢 Xabar yuborish (Broadcast)",
    "👥 Guruhga xabar yuborish", "👑 Adminlar", "⚙️ Sozlamalar & Guruhlar", "⚙️ Sozlamalar",
    "🔙 Asosiy menyuga qaytish", "❌ Bekor qilish", "/admin"
}

@router.message(F.text & ~F.text.in_(ADMIN_COMMANDS))
async def generic_text_handler(message: Message):
    user_id = message.from_user.id if message.from_user else 0
    miniapp_url = await get_setting("mini_app_url", config.MINI_APP_URL)
    is_admin_user = await is_admin(user_id)
    reply_kb = get_main_keyboard(miniapp_url, user_id=user_id, is_admin_user=is_admin_user)
    inline_kb = get_welcome_inline(miniapp_url)

    await message.answer(
        "🍔 <b>Alixan menusini oching va buyurtma bering:</b>",
        parse_mode="HTML",
        reply_markup=inline_kb
    )

@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    await callback.answer()
