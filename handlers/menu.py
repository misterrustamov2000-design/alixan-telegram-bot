import json
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.filters import Command
import config
from database import get_setting
from keyboards.inline import get_categories_inline, get_product_nav_inline

router = Router(name="menu_router")

# Cache menu data
def load_menu():
    try:
        with open(config.MENU_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Menu load error:", e)
        return {"categories": [], "products": []}

MENU_DATA = load_menu()

def format_price(val: int | float) -> str:
    return f"{int(val):,}".replace(",", " ") + " so'm"

@router.message(F.text.in_(["🍔 Taomlar Menyusi (Mini App)", "Mini App"]))
async def mini_app_button_handler(message: Message):
    miniapp_url = await get_setting("mini_app_url", config.MINI_APP_URL)
    photo_path = config.IMAGES_DIR / "icon_menu.jpg"
    categories = MENU_DATA.get("categories", [])

    text = (
        "🍔 <b>ALIXAN FAST FOOD — INTERAKTIV MINI APP VA MENYU</b>\n\n"
        "Siz taomlarimizni Telegram Mini App ilovasida interaktiv tarzda ko'rishingiz, "
        "har bir taomning rasmlari, narxlari va tarkibi bilan tanishishingiz mumkin!\n\n"
        "Shuningdek, to'g'ridan-to'g'ri ushbu botning o'zida ham toifalar bo'yicha ko'rish imkoniyati mavjud.\n\n"
        "👇 <i>Kerakli toifani yoki Mini App tugmasini bosing:</i>"
    )

    inline_kb = get_categories_inline(categories, miniapp_url)

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

@router.message(F.text.in_(["📋 Botda Menyu", "/menu", "Menyu"]))
@router.callback_query(F.data.in_(["btn_menu_bot", "menu_categories"]))
async def bot_menu_categories_handler(event: Message | CallbackQuery):
    miniapp_url = await get_setting("mini_app_url", config.MINI_APP_URL)
    photo_path = config.IMAGES_DIR / "icon_menu.jpg"
    categories = MENU_DATA.get("categories", [])

    text = (
        "📋 <b>ALIXAN FAST FOOD TAOMLAR TOIFALARI</b>\n\n"
        "Bizning barcha taomlarimiz yangi va 100% halol go'sht mahsulotlaridan tayyorlanadi. "
        "O'zingizga yoqqan toifani tanlang va taomlar bilan tanishing 👇"
    )

    inline_kb = get_categories_inline(categories, miniapp_url)

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
        # If callback from previous message, we can send or edit
        try:
            if photo_path.exists():
                await event.message.answer_photo(
                    photo=FSInputFile(str(photo_path)),
                    caption=text,
                    parse_mode="HTML",
                    reply_markup=inline_kb
                )
            else:
                await event.message.answer(text, parse_mode="HTML", reply_markup=inline_kb)
        except Exception:
            await event.message.answer(text, parse_mode="HTML", reply_markup=inline_kb)
        await event.answer()

@router.callback_query(F.data.startswith("cat:"))
async def category_select_handler(callback: CallbackQuery):
    cat_id = callback.data.split(":")[1]
    products = [p for p in MENU_DATA.get("products", []) if p.get("categoryId") == cat_id]

    if not products:
        await callback.answer("Ushbu toifada taomlar mavjud emas.", show_alert=True)
        return

    await show_product_card(callback, cat_id, 0, products)
    await callback.answer()

@router.callback_query(F.data.startswith("prod:"))
async def product_nav_handler(callback: CallbackQuery):
    parts = callback.data.split(":")
    cat_id = parts[1]
    idx = int(parts[2])

    products = [p for p in MENU_DATA.get("products", []) if p.get("categoryId") == cat_id]
    if not products or idx < 0 or idx >= len(products):
        await callback.answer()
        return

    await show_product_card(callback, cat_id, idx, products, is_edit=True)
    await callback.answer()

async def show_product_card(callback: CallbackQuery, cat_id: str, idx: int, products: list[dict], is_edit: bool = False):
    prod = products[idx]
    total = len(products)

    # Category name
    cat_name = cat_id.capitalize()
    for c in MENU_DATA.get("categories", []):
        if c["id"] == cat_id:
            cat_name = f"{c.get('icon', '')} {c.get('name', '')}"
            break

    caption = (
        f"🏷 <b>Toifa:</b> {cat_name}\n"
        f"👑 <b>{prod.get('name')}</b>\n\n"
        f"📝 <i>{prod.get('desc', 'Tarkibi: yangi va sifatli mahsulotlar')}</i>\n\n"
        f"💰 <b>Narxi:</b> <b>{format_price(prod.get('price', 0))}</b>\n"
        f"🛵 <i>Yetkazib berish: 5 000 so'm (Kattaqo'rg'on)</i>\n\n"
        f"📞 <b>Buyurtma uchun:</b> <code>+998910333393</code>"
    )

    inline_kb = get_product_nav_inline(cat_id, idx, total, prod.get("id", ""))

    img_rel = prod.get("image", "")
    img_name = os.path.basename(img_rel)
    img_file = config.IMAGES_DIR / "menu" / img_name

    if not img_file.exists():
        img_file = config.IMAGES_DIR / "banner_menu.jpg"
        if not img_file.exists():
            img_file = config.IMAGES_DIR / "logo.png"

    if is_edit:
        try:
            if img_file.exists():
                media = InputMediaPhoto(
                    media=FSInputFile(str(img_file)),
                    caption=caption,
                    parse_mode="HTML"
                )
                await callback.message.edit_media(media=media, reply_markup=inline_kb)
            else:
                await callback.message.edit_caption(caption=caption, parse_mode="HTML", reply_markup=inline_kb)
            return
        except Exception:
            pass

    # If new message
    if img_file.exists():
        await callback.message.answer_photo(
            photo=FSInputFile(str(img_file)),
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
