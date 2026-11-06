from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
import config
from database import get_setting
from keyboards.inline import get_location_inline

router = Router(name="location_router")

def get_location_caption(work_hours: str, address: str, delivery_fee: str, maps_url: str) -> str:
    return (
        "📍 <b>MANZIL VA ISH VAQTI — ALIXAN FAST FOOD</b>\n\n"
        f"⏰ <b>Ish Vaqti:</b>\n"
        f"<b>{work_hours}</b>\n"
        "Dam olish kunlarisiz doim xizmatingizdamiz!\n\n"
        f"📍 <b>Restoran Manzili:</b>\n"
        f"{address}\n"
        "<i>Mo'ljal: Alisher Navoiy ko'chasi, 5-maktab yaqinida</i>\n\n"
        f"🛵 <b>Yetkazib berish:</b> {delivery_fee} (Kattaqo'rg'on bo'ylab)\n"
        "📞 <b>Aloqa:</b> <code>+998910333393</code> | <code>+998904477999</code>\n\n"
        f"🗺 <b>Xarita:</b> <a href=\"{maps_url}\">Google Xaritada ko'rish</a>\n\n"
        "<i>Xaritada ochish yoki lokatsiya nuqtasini olish uchun pastdagi tugmani bosing</i> 👇"
    )

@router.message(F.text.in_(["📍 Manzil va Ish vaqti", "/location", "Manzil va Ish vaqti"]))
async def location_message_handler(message: Message):
    work_hours = await get_setting("work_hours", config.DEFAULT_WORK_HOURS)
    address = await get_setting("address", config.DEFAULT_ADDRESS)
    delivery_fee = await get_setting("delivery_fee", config.DEFAULT_DELIVERY_PRICE)
    maps_url = await get_setting("maps_url", config.MAPS_URL)

    caption = get_location_caption(work_hours, address, delivery_fee, maps_url)
    photo_path = config.IMAGES_DIR / "icon_location.jpg"
    if not photo_path.exists():
        photo_path = config.IMAGES_DIR / "logo.png"

    inline_kb = get_location_inline(maps_url)

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

@router.callback_query(F.data == "btn_location")
async def location_callback_handler(callback: CallbackQuery):
    work_hours = await get_setting("work_hours", config.DEFAULT_WORK_HOURS)
    address = await get_setting("address", config.DEFAULT_ADDRESS)
    delivery_fee = await get_setting("delivery_fee", config.DEFAULT_DELIVERY_PRICE)
    maps_url = await get_setting("maps_url", config.MAPS_URL)

    caption = get_location_caption(work_hours, address, delivery_fee, maps_url)
    photo_path = config.IMAGES_DIR / "icon_location.jpg"
    inline_kb = get_location_inline(maps_url)

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
    await callback.answer()

@router.callback_query(F.data == "loc_send_pin")
async def send_location_pin(callback: CallbackQuery):
    await callback.answer("Lokatsiya yuborilmoqda...")
    try:
        await callback.message.answer_venue(
            latitude=config.LOCATION_LATITUDE,
            longitude=config.LOCATION_LONGITUDE,
            title="Alixan Fast Food",
            address="Kattaqo'rg'on shahri, Alisher Navoiy ko'chasi, 5-maktab yaqinida"
        )
    except Exception:
        await callback.message.answer_location(
            latitude=config.LOCATION_LATITUDE,
            longitude=config.LOCATION_LONGITUDE
        )
