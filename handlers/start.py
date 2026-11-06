from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
import config
from database import add_or_update_user, get_setting
from keyboards.default import get_main_keyboard
from keyboards.inline import get_welcome_inline, get_contacts_inline, get_location_inline

router = Router(name="start_router")

@router.message(CommandStart())
async def command_start_handler(message: Message):
    user = message.from_user
    if user:
        await add_or_update_user(user.id, user.username, user.full_name)

    # Fetch dynamic settings if customized
    miniapp_url = await get_setting("mini_app_url", config.MINI_APP_URL)
    delivery_fee = await get_setting("delivery_fee", config.DEFAULT_DELIVERY_PRICE)
    work_hours = await get_setting("work_hours", config.DEFAULT_WORK_HOURS)

    caption = (
        "👑 <b>ALIXAN FAST FOOD ga xush kelibsiz!</b>\n\n"
        "Kattaqo'rg'on shahridagi eng mazali va sifatli fast-food maskanining rasmiy botidasiz.\n\n"
        "✨ <b>Bizda har kuni siz uchun:</b>\n"
        "• 🌯 Maxsus tandirda pishirilgan Lavashlar va Donarlar\n"
        "• 🍔 Sersuv kotletli Burgerlar va Chikenlar\n"
        "• 🍗 Qarsildoq KFC va qovurilgan Frikalar\n"
        "• 🍕 Issiqqina va pishloqli Pitsalar\n"
        "• 🌭 To'yimli va betakror Hot-Doglar\n\n"
        f"🛵 <b>Yetkazib berish:</b> {delivery_fee} (shahar bo'ylab)\n"
        f"⏰ <b>Ish vaqti:</b> {work_hours}\n\n"
        "Kerakli bo'limni tanlash uchun pastdagi tugmalardan foydalaning 👇"
    )

    photo_path = config.IMAGES_DIR / "icon_welcome.jpg"
    if not photo_path.exists():
        photo_path = config.IMAGES_DIR / "logo.png"

    reply_kb = get_main_keyboard(miniapp_url, user.id if user else None)
    inline_kb = get_welcome_inline(miniapp_url)

    if photo_path.exists():
        await message.answer_photo(
            photo=FSInputFile(str(photo_path)),
            caption=caption,
            parse_mode="HTML",
            reply_markup=reply_kb
        )
    else:
        await message.answer(
            caption,
            parse_mode="HTML",
            reply_markup=reply_kb
        )

@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    await callback.answer()
