from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

def get_welcome_inline(mini_app_url: str) -> InlineKeyboardMarkup:
    has_valid_webapp = (
        mini_app_url
        and mini_app_url.startswith("https://")
        and not "t.me" in mini_app_url
    )
    buttons = []
    if has_valid_webapp:
        buttons.append([
            InlineKeyboardButton(text="🍔 Taomlar Menyusi (Mini App)", web_app=WebAppInfo(url=mini_app_url))
        ])
    else:
        buttons.append([
            InlineKeyboardButton(text="🍔 Taomlar Menyusi", url=mini_app_url)
        ])

    buttons.append([
        InlineKeyboardButton(text="📞 Bog'lanish va buyurtma", callback_data="btn_contacts"),
        InlineKeyboardButton(text="📍 Restoran manzili", callback_data="btn_location")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_contacts_inline(phones: list[str]) -> InlineKeyboardMarkup:
    buttons = []
    for p in phones:
        clean = "".join(ch for ch in p if ch.isdigit() or ch == "+")
        buttons.append([
            InlineKeyboardButton(text=f"📞 {p}", callback_data=f"call:{clean}")
        ])
    
    buttons.append([
        InlineKeyboardButton(text="💬 Telegram orqali aloqa", url="https://t.me/Alixan_cafe_bot")
    ])
    buttons.append([
        InlineKeyboardButton(text="🛵 Yetkazib berish shartlari", callback_data="btn_delivery_info")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_location_inline(maps_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🗺 Google Xaritada ochish", url=maps_url)
            ],
            [
                InlineKeyboardButton(text="📍 Telegramda nuqtani (Lokatsiya) yuborish", callback_data="loc_send_pin")
            ],
            [
                InlineKeyboardButton(text="📞 Buyurtma berish", callback_data="btn_contacts")
            ]
        ]
    )

def get_categories_inline(categories: list[dict], mini_app_url: str) -> InlineKeyboardMarkup:
    buttons = []
    has_valid_webapp = (
        mini_app_url
        and mini_app_url.startswith("https://")
        and not "t.me" in mini_app_url
    )
    if has_valid_webapp:
        buttons.append([
            InlineKeyboardButton(text="🌟 Interaktiv Mini App Menyuni Ochish", web_app=WebAppInfo(url=mini_app_url))
        ])

    row = []
    for cat in categories:
        if cat["id"] == "all":
            continue
        row.append(InlineKeyboardButton(text=f"{cat['icon']} {cat['name']}", callback_data=f"cat:{cat['id']}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton(text="📞 Buyurtma uchun qo'ng'iroq", callback_data="btn_contacts")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_product_nav_inline(cat_id: str, current_idx: int, total_items: int, product_id: str) -> InlineKeyboardMarkup:
    nav_row = []
    if current_idx > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Oldingi", callback_data=f"prod:{cat_id}:{current_idx - 1}"))
    
    nav_row.append(InlineKeyboardButton(text=f"🔢 {current_idx + 1}/{total_items}", callback_data="noop"))
    
    if current_idx < total_items - 1:
        nav_row.append(InlineKeyboardButton(text="Keyingi ▶️", callback_data=f"prod:{cat_id}:{current_idx + 1}"))

    return InlineKeyboardMarkup(
        inline_keyboard=[
            nav_row,
            [
                InlineKeyboardButton(text="📞 Buyurtma berish: (91) 033-33-93", callback_data="call:+998910333393")
            ],
            [
                InlineKeyboardButton(text="📂 Barcha toifalarga qaytish", callback_data="menu_categories")
            ]
        ]
    )

def get_broadcast_confirm_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚀 Ha, hammaga yuborilsin!", callback_data="confirm_broadcast")
            ],
            [
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_broadcast")
            ]
        ]
    )

def get_broadcast_menu_inline(mini_app_url: str) -> InlineKeyboardMarkup:
    has_valid_webapp = (
        mini_app_url
        and mini_app_url.startswith("https://")
        and not "t.me" in mini_app_url
    )
    if has_valid_webapp:
        btn = InlineKeyboardButton(
            text="🍔 Online Menyu (Mini App)",
            web_app=WebAppInfo(url=mini_app_url)
        )
    else:
        btn = InlineKeyboardButton(
            text="🍔 Online Menyu",
            url=mini_app_url
        )
    return InlineKeyboardMarkup(inline_keyboard=[[btn]])

def get_admins_manage_inline(admins: list[dict], current_user_id: int, super_admin_ids: list[int]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="➕ Yangi admin qo'shish", callback_data="admin_add_prompt")]
    ]
    # Add delete buttons for non-superadmin users
    for adm in admins:
        if adm["user_id"] not in super_admin_ids and adm["user_id"] != current_user_id:
            name = adm.get("full_name") or adm.get("username") or f"ID: {adm['user_id']}"
            buttons.append([
                InlineKeyboardButton(text=f"🗑 O'chirish: {name[:20]}", callback_data=f"admin_remove:{adm['user_id']}")
            ])
    buttons.append([InlineKeyboardButton(text="🔙 Yopish", callback_data="admin_close_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
