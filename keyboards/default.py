from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from config import ADMIN_IDS

def get_main_keyboard(mini_app_url: str, user_id: int | None = None) -> ReplyKeyboardMarkup:
    # Telegram only allows WebAppInfo for external https domains (not t.me)
    has_valid_webapp = (
        mini_app_url
        and mini_app_url.startswith("https://")
        and not mini_app_url.startswith("https://t.me")
        and not "t.me/" in mini_app_url
    )
    
    if has_valid_webapp:
        menu_btn = KeyboardButton(text="🍔 Taomlar Menyusi (Mini App)", web_app=WebAppInfo(url=mini_app_url))
    else:
        menu_btn = KeyboardButton(text="🍔 Taomlar Menyusi")

    keyboard = [
        [menu_btn],
        [
            KeyboardButton(text="📋 Botda Menyu"),
            KeyboardButton(text="ℹ️ Biz haqimizda")
        ],
        [
            KeyboardButton(text="📞 Telefon raqamlar"),
            KeyboardButton(text="📍 Manzil va Ish vaqti")
        ],
        [
            KeyboardButton(text="🛵 Yetkazib berish"),
            KeyboardButton(text="✍️ Fikr / Taklif")
        ]
    ]

    # If user is in ADMIN_IDS, show Admin button
    if user_id and user_id in ADMIN_IDS:
        keyboard.append([KeyboardButton(text="⚙️ Admin Panel")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Kerakli bo'limni tanlang..."
    )

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text="📊 Statistika"),
            KeyboardButton(text="👥 Kimlar foydalanmoqda")
        ],
        [
            KeyboardButton(text="📢 Foydalanuvchilarga xabar"),
            KeyboardButton(text="👥 Guruhga xabar yuborish")
        ],
        [
            KeyboardButton(text="⚙️ Sozlamalar & Guruhlar"),
            KeyboardButton(text="🔙 Asosiy menyuga qaytish")
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Admin amalini tanlang..."
    )

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
