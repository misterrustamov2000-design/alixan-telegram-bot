from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
import config
from database import get_setting

router = Router(name="about_router")

def get_about_text(work_hours: str, delivery_fee: str) -> str:
    return (
        "👑 <b>ALIXAN FAST FOOD — Sifat va Lazzat Uyg'unligi!</b>\n\n"
        "<i>«Har bir luqmada haqiqiy lazzat!»</i>\n\n"
        "<b>Alixan Fast Food</b> — Kattaqo'rg'on shahrida mijozlarga eng sara, toza va mazali "
        "fast-food taomlarini taqdim etuvchi zamonaviy restoran maskanidir.\n\n"
        "✨ <b>Bizning asosiy ustunliklarimiz:</b>\n"
        "▫️ <b>100% Halol mahsulotlar:</b> Faqat eng yangi va saralangan go'shtlar ishlatiladi.\n"
        "▫️ <b>Maxsus Tandir:</b> Qarsildoq tandir lavashlarimiz maxsus tandirda pishiriladi.\n"
        "▫️ <b>Mualliflik souslari:</b> Har bir taomimizga o'ziga xos ta'm beruvchi original souslar.\n"
        "▫️ <b>Tezkor yetkazib berish:</b> Taomlaringiz sovumasdan, issiq va yangi yetkaziladi.\n\n"
        f"🛵 <b>Yetkazib berish:</b> {delivery_fee}\n"
        f"<i>{config.DEFAULT_DELIVERY_EXTRA}</i>\n"
        f"⏰ <b>Ish tartibi:</b> {work_hours}\n"
        f"📍 <b>Manzil:</b> {config.DEFAULT_ADDRESS}\n\n"
        "Sizga xizmat ko'rsatishdan hamisha mamnunmiz! 😊"
    )

@router.message(F.text.in_(["ℹ️ Biz haqimizda", "/about", "Biz haqimizda"]))
async def about_message_handler(message: Message):
    work_hours = await get_setting("work_hours", config.DEFAULT_WORK_HOURS)
    delivery_fee = await get_setting("delivery_fee", config.DEFAULT_DELIVERY_PRICE)
    text = get_about_text(work_hours, delivery_fee)

    photo_path = config.IMAGES_DIR / "icon_about.jpg"
    if not photo_path.exists():
        photo_path = config.IMAGES_DIR / "logo.png"

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📞 Bog'lanish va buyurtma", callback_data="btn_contacts"),
                InlineKeyboardButton(text="📍 Xaritada manzil", callback_data="btn_location")
            ]
        ]
    )

    if photo_path.exists():
        await message.answer_photo(
            photo=FSInputFile(str(photo_path)),
            caption=text,
            parse_mode="HTML",
            reply_markup=inline_kb
        )
    else:
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=inline_kb
        )
