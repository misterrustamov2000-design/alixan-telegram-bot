from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
import config
from database import get_setting
from keyboards.inline import get_contacts_inline

router = Router(name="contacts_router")

PHONE_CONTACTS = [
    {
        "phone": "+998910333393",
        "display": "+998 (91) 033-33-93",
        "role": "Operator (Asosiy)"
    },
    {
        "phone": "+998904477999",
        "display": "+998 (90) 447-79-99",
        "role": "Tezkor buyurtma"
    },
    {
        "phone": "+998996787977",
        "display": "+998 (99) 678-79-77",
        "role": "Yetkazib berish xizmati"
    }
]

def get_contacts_caption(delivery_fee: str, work_hours: str) -> str:
    return (
        "📞 <b>TELEFON VA BUYURTMA — ALIXAN FAST FOOD</b>\n\n"
        "Issiq va mazali taomlarni xonadoningiz yoki ishxonangizgacha yetkazib beramiz!\n\n"
        "<b>Qo'ng'iroq qilish uchun raqam ustiga bosing:</b>\n"
        "• 📞 <a href=\"tel:+998910333393\"><b>+998 (91) 033-33-93</b></a> — Operator / Asosiy\n"
        "• 📞 <a href=\"tel:+998904477999\"><b>+998 (90) 447-79-99</b></a> — Tezkor buyurtma\n"
        "• 📞 <a href=\"tel:+998996787977\"><b>+998 (99) 678-79-77</b></a> — Yetkazib berish xizmati\n\n"
        f"🛵 <b>Yetkazib berish narxi:</b> <b>{delivery_fee}</b> (Kattaqo'rg'on shahri bo'ylab)\n"
        f"⏰ <b>Buyurtma qabul qilish:</b> {work_hours}\n\n"
        "👇 <i>Pastdagi har bir kontakt orqali to'g'ridan-to'g'ri qo'ng'iroq qilishingiz mumkin:</i>"
    )

@router.message(F.text.in_(["📞 Telefon raqamlar", "/contacts", "Telefon raqamlar"]))
async def contacts_message_handler(message: Message):
    delivery_fee = await get_setting("delivery_fee", config.DEFAULT_DELIVERY_PRICE)
    work_hours = await get_setting("work_hours", config.DEFAULT_WORK_HOURS)
    caption = get_contacts_caption(delivery_fee, work_hours)

    photo_path = config.IMAGES_DIR / "icon_contacts.jpg"
    if not photo_path.exists():
        photo_path = config.IMAGES_DIR / "logo.png"

    inline_kb = get_contacts_inline(config.DEFAULT_PHONES)

    if photo_path.exists():
        await message.answer_photo(
            photo=FSInputFile(str(photo_path)),
            caption=caption,
            parse_mode="HTML",
            reply_markup=inline_kb
        )
    else:
        await message.answer(
            caption,
            parse_mode="HTML",
            reply_markup=inline_kb
        )

    # Send each contact card separately so user can click and call directly
    for item in PHONE_CONTACTS:
        await message.answer_contact(
            phone_number=item["phone"],
            first_name="Alixan Fast Food",
            last_name=item["role"]
        )

@router.callback_query(F.data == "btn_contacts")
async def contacts_callback_handler(callback: CallbackQuery):
    delivery_fee = await get_setting("delivery_fee", config.DEFAULT_DELIVERY_PRICE)
    work_hours = await get_setting("work_hours", config.DEFAULT_WORK_HOURS)
    caption = get_contacts_caption(delivery_fee, work_hours)

    photo_path = config.IMAGES_DIR / "icon_contacts.jpg"
    if not photo_path.exists():
        photo_path = config.IMAGES_DIR / "logo.png"
    inline_kb = get_contacts_inline(config.DEFAULT_PHONES)

    if photo_path.exists():
        await callback.message.answer_photo(
            photo=FSInputFile(str(photo_path)),
            caption=caption,
            parse_mode="HTML",
            reply_markup=inline_kb
        )
    else:
        await callback.message.answer(
            caption,
            parse_mode="HTML",
            reply_markup=inline_kb
        )

    for item in PHONE_CONTACTS:
        await callback.message.answer_contact(
            phone_number=item["phone"],
            first_name="Alixan Fast Food",
            last_name=item["role"]
        )
    await callback.answer()

@router.message(F.text.in_(["🛵 Yetkazib berish", "/delivery"]))
@router.callback_query(F.data == "btn_delivery_info")
async def delivery_info_handler(event: Message | CallbackQuery):
    delivery_fee = await get_setting("delivery_fee", config.DEFAULT_DELIVERY_PRICE)
    text = (
        "🛵 <b>ALIXAN FAST FOOD YETKAZIB BERISH XIZMATI</b>\n\n"
        f"💰 <b>Yetkazib berish narxi:</b> {delivery_fee} (Kattaqo'rg'on shahri bo'ylab)\n"
        "⚡️ <b>Yetkazish vaqti:</b> 20 - 40 daqiqa\n"
        "⏰ <b>Xizmat vaqti:</b> Har kuni 09:00 dan 02:00 gacha\n\n"
        "📦 <b>Qulayliklar:</b>\n"
        "• Barcha taomlar maxsus termo-sumkalarda, issiq holida keltiriladi\n"
        "• Har bir buyurtmaga salfetka va qulay bir martalik anjomlar qo'shiladi\n"
        "• To'lov turi: Naqd pul yoki Click / Payme orqali\n\n"
        "📞 <b>Buyurtma uchun:</b>\n"
        "• <code>+998910333393</code>\n"
        "• <code>+998904477999</code>\n"
        "• <code>+998996787977</code>"
    )
    inline_kb = get_contacts_inline(config.DEFAULT_PHONES)
    photo_path = config.IMAGES_DIR / "icon_delivery.jpg"
    if not photo_path.exists():
        photo_path = config.IMAGES_DIR / "logo.png"

    if isinstance(event, Message):
        if photo_path.exists():
            await event.answer_photo(
                photo=FSInputFile(str(photo_path)),
                caption=text,
                parse_mode="HTML",
                reply_markup=inline_kb
            )
        else:
            await event.answer(text, parse_mode="HTML", reply_markup=inline_kb)
    else:
        if photo_path.exists():
            await event.message.answer_photo(
                photo=FSInputFile(str(photo_path)),
                caption=text,
                parse_mode="HTML",
                reply_markup=inline_kb
            )
        else:
            await event.message.answer(text, parse_mode="HTML", reply_markup=inline_kb)
        await event.answer()

@router.callback_query(F.data.startswith("call:"))
async def phone_call_callback_handler(callback: CallbackQuery):
    phone = callback.data.split(":")[1]
    role = "Buyurtma"
    for item in PHONE_CONTACTS:
        clean_item = "".join(ch for ch in item["phone"] if ch.isdigit())
        clean_target = "".join(ch for ch in phone if ch.isdigit())
        if clean_item == clean_target:
            role = item["role"]
            break

    await callback.answer(f"📞 Qo'ng'iroq qilish: {phone}")
    try:
        await callback.message.answer_contact(
            phone_number=phone,
            first_name="Alixan Fast Food",
            last_name=role
        )
    except Exception:
        await callback.message.answer(
            f"📞 <b>Qo'ng'iroq qilish:</b> <a href=\"tel:{phone}\">{phone}</a>",
            parse_mode="HTML"
        )
