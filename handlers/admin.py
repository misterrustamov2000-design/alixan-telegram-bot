import asyncio
import io
import csv
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, BufferedInputFile, ChatMemberUpdated
from aiogram.filters import Command, ChatMemberUpdatedFilter, KICKED, LEFT, RESTRICTED, MEMBER, ADMINISTRATOR
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import config
from database import (
    get_user_stats, get_all_active_users, mark_user_blocked,
    get_setting, set_setting, log_broadcast,
    get_recent_users, get_all_users_export,
    add_or_update_group, remove_group, get_all_active_groups,
    is_admin, get_all_admins, add_admin, remove_admin
)
from keyboards.default import get_admin_keyboard, get_main_keyboard, get_cancel_keyboard
from keyboards.inline import (
    get_broadcast_confirm_inline, get_broadcast_menu_inline,
    get_admins_manage_inline, InlineKeyboardMarkup, InlineKeyboardButton
)

logger = logging.getLogger(__name__)

router = Router(name="admin_router")

class AdminStates(StatesGroup):
    waiting_for_user_broadcast = State()
    waiting_for_user_broadcast_confirm = State()
    waiting_for_group_broadcast = State()
    waiting_for_group_broadcast_confirm = State()
    waiting_for_add_group_id = State()
    waiting_for_new_miniapp_url = State()
    waiting_for_new_delivery_fee = State()
    waiting_for_new_workhours = State()
    waiting_for_new_admin_id = State()

# ==================== BOT GURUHGA QO'SHILGANDA AVTOMATIK BAZAGA YOZISH ====================
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER | ADMINISTRATOR))
async def bot_added_to_group(event: ChatMemberUpdated, bot: Bot):
    chat = event.chat
    if chat.type in ["group", "supergroup", "channel"]:
        await add_or_update_group(chat.id, chat.title or "Nomsiz guruh", chat.username)
        # Notify all admins
        admins = await get_all_admins()
        for adm in admins:
            try:
                await bot.send_message(
                    adm["user_id"],
                    f"🎉 <b>Bot yangi guruhga qo'shildi!</b>\n\n"
                    f"📌 <b>Nomi:</b> {chat.title}\n"
                    f"🆔 <b>Chat ID:</b> <code>{chat.id}</code>\n"
                    f"🔗 <b>Username:</b> @{chat.username or 'yo‘q'}\n\n"
                    f"<i>Endi Admin panel orqali ushbu guruhga bevosita xabar yuborishingiz mumkin!</i>",
                    parse_mode="HTML"
                )
            except Exception:
                pass

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED | LEFT))
async def bot_removed_from_group(event: ChatMemberUpdated):
    chat = event.chat
    await remove_group(chat.id)

# ==================== ADMIN DASHBOARD ====================
@router.message(Command("admin"))
@router.message(F.text == "⚙️ Admin Panel")
async def admin_dashboard(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user else 0
    if not await is_admin(user_id):
        await message.answer(
            f"⛔️ <b>Siz admin emassiz!</b>\n\n"
            f"Sizning Telegram ID raqamingiz: <code>{user_id}</code>\n"
            f"Adminlik huquqini olish uchun ushbu ID raqamni bosh admin orqali botga qo'shing.",
            parse_mode="HTML"
        )
        return

    await state.clear()
    stats = await get_user_stats()
    text = (
        "👑 <b>ALIXAN FAST FOOD — ADMIN BOSHQARUV PANELI</b>\n\n"
        "Xush kelibsiz, administrator! Quyidagi amallardan birini tanlang:\n\n"
        f"👥 <b>Jami mijozlar:</b> {stats['total']} nafar\n"
        f"⚡️ <b>Faol a'zolar:</b> {stats['active_total']} nafar\n"
        f"📅 <b>Bugun qo'shilgan:</b> +{stats['today_joined']} nafar\n"
        f"📢 <b>Ulangan guruhlar:</b> {stats['group_count']} ta\n\n"
        "Kerakli bo'limni tanlang 👇"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_admin_keyboard())

@router.message(F.text == "🔙 Asosiy menyuga qaytish")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id if message.from_user else 0
    miniapp_url = await get_setting("mini_app_url", config.MINI_APP_URL)
    is_adm = await is_admin(user_id)
    await message.answer(
        "Bosh sahifaga qaytdingiz.",
        reply_markup=get_main_keyboard(miniapp_url, user_id=user_id, is_admin_user=is_adm)
    )

# ==================== 1. STATISTIKA ====================
@router.message(F.text == "📊 Statistika")
async def admin_stats_handler(message: Message):
    user_id = message.from_user.id if message.from_user else 0
    if not await is_admin(user_id):
        return

    stats = await get_user_stats()
    miniapp_url = await get_setting("mini_app_url", config.MINI_APP_URL)
    delivery_fee = await get_setting("delivery_fee", config.DEFAULT_DELIVERY_PRICE)
    work_hours = await get_setting("work_hours", config.DEFAULT_WORK_HOURS)

    text = (
        "📊 <b>BOTNING TO'LIQ STATISTIKASI:</b>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {stats['total']} ta\n"
        f"✅ <b>Hozirgi faol a'zolar:</b> {stats['active_total']} ta\n"
        f"📅 <b>Bugun qo'shilganlar:</b> +{stats['today_joined']} ta\n"
        f"📈 <b>Haftalik faol a'zolar:</b> {stats['weekly_active']} ta\n"
        f"🚫 <b>Botni bloklaganlar:</b> {stats['blocked']} ta\n"
        f"📢 <b>Ulangan guruhlar soni:</b> {stats['group_count']} ta\n\n"
        "⚙️ <b>Hozirgi sozlamalar:</b>\n"
        f"• 🛵 Yetkazib berish: <b>{delivery_fee}</b>\n"
        f"• ⏰ Ish vaqti: <b>{work_hours}</b>\n"
        f"• 🌐 Mini App: <code>{miniapp_url}</code>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_admin_keyboard())

# ==================== 2. KIMLAR FOYDALANMOQDA ====================
@router.message(F.text.in_(["👥 Kimlar foydalanmoqda", "👥 Foydalanuvchilar"]))
async def admin_users_list_handler(message: Message):
    user_id = message.from_user.id if message.from_user else 0
    if not await is_admin(user_id):
        return

    recent_users = await get_recent_users(limit=15)
    stats = await get_user_stats()

    text = f"👥 <b>BOTDAN FOYDALANUVCHILAR RO'YXATI</b>\n"
    text += f"<i>Jami: {stats['total']} nafar | Faol: {stats['active_total']} nafar</i>\n\n"
    text += "<b>So'nggi faol foydalanuvchilar:</b>\n\n"

    for i, u in enumerate(recent_users, 1):
        uname = f"@{u['username']}" if u['username'] else "yo'q"
        name = u['full_name'] or "Nomsiz"
        status_icon = "🚫" if u['is_blocked'] else "🟢"
        text += (
            f"{i}. {status_icon} <b>{name}</b> ({uname})\n"
            f"   🆔 ID: <code>{u['user_id']}</code>\n"
            f"   ⚡️ Faollik: <i>{u['last_active']}</i>\n\n"
        )

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📥 Barcha a'zolarni yuklab olish (.csv)", callback_data="export_users_csv")
            ]
        ]
    )

    await message.answer(text, parse_mode="HTML", reply_markup=inline_kb)

@router.callback_query(F.data == "export_users_csv")
async def export_users_csv_callback(callback: CallbackQuery):
    user_id = callback.from_user.id if callback.from_user else 0
    if not await is_admin(user_id):
        await callback.answer("Ruxsat berilmagan!", show_alert=True)
        return

    rows = await get_all_users_export()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["user_id", "username", "full_name", "joined_at", "last_active", "is_blocked"])
    for r in rows:
        writer.writerow(r)

    csv_bytes = output.getvalue().encode("utf-8-sig")
    doc = BufferedInputFile(csv_bytes, filename="alixan_foydalanuvchilar.csv")

    await callback.message.answer_document(
        document=doc,
        caption=f"📁 Jami <b>{len(rows)}</b> nafar foydalanuvchilarning to'liq CSV fayli tayyorlandi.",
        parse_mode="HTML"
    )
    await callback.answer()

# ==================== 3. FOYDALANUVCHILARGA XABAR YUBORISH (BROADCAST) ====================
@router.message(F.text.in_(["📢 Foydalanuvchilarga xabar", "📢 Xabar yuborish (Broadcast)"]))
async def user_broadcast_start(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user else 0
    if not await is_admin(user_id):
        return

    await state.set_state(AdminStates.waiting_for_user_broadcast)
    await message.answer(
        "📢 <b>BARCHA FOYDALANUVCHILARGA XABAR YUBORISH</b>\n\n"
        "Xabaringizni yuboring:\n"
        "• Rasm bilan birga matn (chiroyli reklama posti)\n"
        "• Oddiy matn\n"
        "• Video yoki forward xabar\n\n"
        "💡 <i>Keyingi qadamda xabarni «Alixan Menu» tugmasi bilan yoki oddiy (tugmasiz) yuborishni tanlashingiz mumkin!</i>\n\n"
        "Bekor qilish uchun ❌ Bekor qilish tugmasini bosing.",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )

@router.message(AdminStates.waiting_for_user_broadcast, F.text == "❌ Bekor qilish")
@router.message(AdminStates.waiting_for_group_broadcast, F.text == "❌ Bekor qilish")
async def broadcast_cancel_msg(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Xabar yuborish bekor qilindi.", reply_markup=get_admin_keyboard())

@router.message(AdminStates.waiting_for_user_broadcast)
async def user_broadcast_preview(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(
        broadcast_chat_id=message.chat.id,
        broadcast_message_id=message.message_id,
        target="users"
    )
    await state.set_state(AdminStates.waiting_for_user_broadcast_confirm)

    users = await get_all_active_users()

    await message.answer("👆 <b>Siz yuborgan xabar qabul qilindi. Ko'rinishi:</b>", parse_mode="HTML")
    try:
        await bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
    except Exception as e:
        logger.warning(f"Preview copy failed: {e}")

    await message.answer(
        f"📢 Ushbu xabar barcha <b>{len(users)} nafar</b> faol mijozlarga yuboriladi.\n\n"
        "Qanday shaklda yuborishni xohlaysiz?\n"
        "• <b>🍔 Alixan Menu tugmasi bilan:</b> xabar ostiga mini app menyusi tugmasi qo'shiladi.\n"
        "• <b>✉️ Tugmasiz (oddiy xabar):</b> faqat xabarning o'zi yuboriladi.\n\n"
        "Kerakli usulni tanlang 👇",
        parse_mode="HTML",
        reply_markup=get_broadcast_confirm_inline()
    )

@router.callback_query(AdminStates.waiting_for_user_broadcast_confirm, F.data.in_(["confirm_broadcast_menu", "confirm_broadcast_plain", "confirm_broadcast"]))
async def user_broadcast_execute(callback: CallbackQuery, state: FSMContext, bot: Bot):
    with_menu = (callback.data != "confirm_broadcast_plain")
    data = await state.get_data()
    chat_id = data.get("broadcast_chat_id")
    msg_id = data.get("broadcast_message_id")
    await state.clear()

    await callback.message.edit_text("⏳ <b>Foydalanuvchilarga xabar tarqatilmoqda...</b>", parse_mode="HTML")
    await callback.answer()

    users = await get_all_active_users()
    reply_markup = None
    if with_menu:
        miniapp_url = await get_setting("mini_app_url", config.MINI_APP_URL)
        reply_markup = get_broadcast_menu_inline(miniapp_url)

    sent = 0
    failed = 0

    status_msg = await callback.message.answer(f"Yuborilmoqda: 0 / {len(users)}")

    for i, uid in enumerate(users):
        try:
            await bot.copy_message(
                chat_id=uid,
                from_chat_id=chat_id,
                message_id=msg_id,
                reply_markup=reply_markup
            )
            sent += 1
        except Exception as e:
            failed += 1
            err_str = str(e).lower()
            if "forbidden" in err_str or "blocked" in err_str:
                await mark_user_blocked(uid)

        await asyncio.sleep(0.04)

        if (i + 1) % 30 == 0 or (i + 1) == len(users):
            try:
                await status_msg.edit_text(f"Yuborilmoqda: {i + 1} / {len(users)}")
            except Exception:
                pass

    admin_id = callback.from_user.id if callback.from_user else 0
    await log_broadcast(admin_id, sent, failed, target_type="users")

    tag_info = "🔗 <i>Barcha xabarlar ostiga «Alixan Menu» tugmasi ulandi.</i>" if with_menu else "✉️ <i>Xabarlar oddiy ko'rinishda (tugmasiz) yuborildi.</i>"

    await status_msg.edit_text(
        "🎉 <b>Xabar tarqatish muvaffaqiyatli yakunlandi!</b>\n\n"
        f"✅ <b>Yetib bordi:</b> {sent} ta\n"
        f"❌ <b>Yetib bormadi (bloklagan):</b> {failed} ta\n"
        f"👥 <b>Jami yuborilgan:</b> {len(users)} ta\n"
        f"{tag_info}",
        parse_mode="HTML"
    )
    await callback.message.answer("Admin boshqaruv menyusi:", reply_markup=get_admin_keyboard())

# ==================== 4. GURUHGA XABAR YUBORISH ====================
@router.message(F.text == "👥 Guruhga xabar yuborish")
async def group_broadcast_start(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user else 0
    if not await is_admin(user_id):
        return

    groups = await get_all_active_groups()

    if not groups:
        text = (
            "⚠️ <b>Hozircha botga ulangan guruhlar mavjud emas!</b>\n\n"
            "Botni o'z guruhingizga qo'shish juda oson:\n"
            "1. Telegram guruhingizga @Alixan_cafe_bot ni a'zo qilib qo'shing.\n"
            "2. Botga guruhda <b>Admin</b> huquqini bering.\n"
            "3. Bot guruhni avtomatik tarzda ro'yxatga oladi va siz shu yerdan barcha guruhlaringizga xabar yubora olasiz!\n\n"
            "<i>Shuningdek, quyidagi tugma orqali guruh Chat ID sini qo'lda ham kiritishingiz mumkin.</i>"
        )
        inline_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="➕ Guruh Chat ID sini qo'lda kiritish", callback_data="manual_add_group")]
            ]
        )
        await message.answer(text, parse_mode="HTML", reply_markup=inline_kb)
        return

    group_list_text = "\n".join([f"• <b>{g['title']}</b> (ID: <code>{g['chat_id']}</code>)" for g in groups])
    await state.set_state(AdminStates.waiting_for_group_broadcast)

    await message.answer(
        "📢 <b>GURUHLARGA XABAR YUBORISH</b>\n\n"
        f"Ulangan guruhlar soni: <b>{len(groups)} ta</b>\n"
        f"{group_list_text}\n\n"
        "Guruhlarga chiqarmoqchi bo'lgan xabaringizni yuboring (matn, rasm+matn yoki video):\n\n"
        "💡 <i>Keyingi qadamda xabarni «Alixan Menu» tugmasi bilan yoki oddiy (tugmasiz) yuborishni tanlashingiz mumkin!</i>\n\n"
        "Bekor qilish uchun ❌ Bekor qilish tugmasini bosing.",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )

@router.message(AdminStates.waiting_for_group_broadcast)
async def group_broadcast_preview(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(
        broadcast_chat_id=message.chat.id,
        broadcast_message_id=message.message_id,
        target="groups"
    )
    await state.set_state(AdminStates.waiting_for_group_broadcast_confirm)

    groups = await get_all_active_groups()

    await message.answer("👆 <b>Siz yuborgan xabar qabul qilindi. Guruhlarga ko'rinishi:</b>", parse_mode="HTML")
    try:
        await bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
    except Exception as e:
        logger.warning(f"Preview copy failed: {e}")

    await message.answer(
        f"📢 Ushbu xabar barcha <b>{len(groups)} ta</b> guruhga yuboriladi.\n\n"
        "Qanday shaklda yuborishni xohlaysiz?\n"
        "• <b>🍔 Alixan Menu tugmasi bilan:</b> xabar ostiga mini app menyusi tugmasi qo'shiladi.\n"
        "• <b>✉️ Tugmasiz (oddiy xabar):</b> faqat xabarning o'zi yuboriladi.\n\n"
        "Kerakli usulni tanlang 👇",
        parse_mode="HTML",
        reply_markup=get_broadcast_confirm_inline()
    )

@router.callback_query(AdminStates.waiting_for_group_broadcast_confirm, F.data.in_(["confirm_broadcast_menu", "confirm_broadcast_plain", "confirm_broadcast"]))
async def group_broadcast_execute(callback: CallbackQuery, state: FSMContext, bot: Bot):
    with_menu = (callback.data != "confirm_broadcast_plain")
    data = await state.get_data()
    chat_id = data.get("broadcast_chat_id")
    msg_id = data.get("broadcast_message_id")
    await state.clear()

    await callback.message.edit_text("⏳ <b>Guruhlarga xabar yuborilmoqda...</b>", parse_mode="HTML")
    await callback.answer()

    groups = await get_all_active_groups()
    reply_markup = None
    if with_menu:
        miniapp_url = await get_setting("mini_app_url", config.MINI_APP_URL)
        reply_markup = get_broadcast_menu_inline(miniapp_url)

    sent = 0
    failed = 0

    for g in groups:
        try:
            await bot.copy_message(
                chat_id=g["chat_id"],
                from_chat_id=chat_id,
                message_id=msg_id,
                reply_markup=reply_markup
            )
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    admin_id = callback.from_user.id if callback.from_user else 0
    await log_broadcast(admin_id, sent, failed, target_type="groups")

    tag_info = "🔗 <i>Barcha guruh postlari ostiga «Alixan Menu» tugmasi ulandi.</i>" if with_menu else "✉️ <i>Guruhlarga oddiy ko'rinishda (tugmasiz) yuborildi.</i>"

    await callback.message.answer(
        "🎉 <b>Guruhlarga xabar yuborish yakunlandi!</b>\n\n"
        f"✅ <b>Muvaffaqiyatli yetkazildi:</b> {sent} ta guruhga\n"
        f"❌ <b>Xatolik bo'ldi:</b> {failed} ta guruhda\n"
        f"{tag_info}",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )

@router.callback_query(F.data == "cancel_broadcast")
async def cancel_any_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Xabar yuborish bekor qilindi.")
    await callback.message.answer("Admin boshqaruv menyusi:", reply_markup=get_admin_keyboard())
    await callback.answer()

# ==================== 5. ADMINLAR BOSHQARUVI ====================
@router.message(F.text == "👑 Adminlar")
async def admins_list_handler(message: Message):
    user_id = message.from_user.id if message.from_user else 0
    if not await is_admin(user_id):
        return

    admins = await get_all_admins()
    text = (
        "👑 <b>ALIXAN FAST FOOD — ADMINISTRATORLAR RO'YXATI</b>\n\n"
        "Botni boshqarish huquqiga ega shaxslar:\n\n"
    )
    for i, a in enumerate(admins, 1):
        is_super = a["user_id"] in config.ADMIN_IDS
        role_label = "⭐️ Bosh Admin" if is_super else "🛡 Qo'shimcha Admin"
        name = a["full_name"] or a["username"] or "Nomsiz"
        uname = f"@{a['username']}" if a["username"] else "yo'q"
        text += (
            f"{i}. <b>{name}</b> ({role_label})\n"
            f"   🆔 Telegram ID: <code>{a['user_id']}</code>\n"
            f"   🔗 Username: {uname}\n"
            f"   📅 Qo'shilgan: <i>{a['added_at']}</i>\n\n"
        )

    text += (
        "💡 <i>Har ikkala administrator ham mijozlarga xabarlar, rasmlar yuborishi "
        "va bot statistikasini boshqarishi mumkin.</i>\n\n"
        "Yangi admin qo'shish uchun pastdagi tugmani bosing 👇"
    )

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_admins_manage_inline(admins, user_id, config.ADMIN_IDS)
    )

@router.callback_query(F.data == "admin_add_prompt")
async def admin_add_prompt_callback(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id if callback.from_user else 0
    if not await is_admin(user_id):
        await callback.answer("Ruxsat berilmagan!", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_for_new_admin_id)
    await callback.message.answer(
        "➕ <b>YANGI ADMIN QO'SHISH</b>\n\n"
        "Yangi admin bo'ladigan shaxsning <b>Telegram ID raqamini</b> kiriting:\n"
        "<i>(Masalan: <code>123456789</code>)</i>\n\n"
        "💡 <i>Eslatma: Ikkinchi odam o'zining Telegram ID sini bilish uchun @userinfobot ga /start bosishi mumkin.</i>\n\n"
        "Bekor qilish uchun ❌ Bekor qilish tugmasini bosing.",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_new_admin_id, F.text == "❌ Bekor qilish")
async def cancel_add_admin(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Admin qo'shish bekor qilindi.", reply_markup=get_admin_keyboard())

@router.message(AdminStates.waiting_for_new_admin_id)
async def process_new_admin_id(message: Message, state: FSMContext, bot: Bot):
    raw_text = (message.text or "").strip()
    if not raw_text.isdigit():
        await message.answer(
            "⚠️ <b>Noto'g'ri format!</b>\n"
            "Iltimos, faqat raqamlardan iborat Telegram ID kiriting (masalan: <code>123456789</code>):",
            parse_mode="HTML"
        )
        return

    new_admin_id = int(raw_text)
    if await is_admin(new_admin_id):
        await message.answer("⚠️ Ushbu foydalanuvchi allaqachon adminlar ro'yxatida mavjud!", reply_markup=get_admin_keyboard())
        await state.clear()
        return

    admin_name = "Admin"
    admin_uname = ""
    try:
        chat = await bot.get_chat(new_admin_id)
        admin_name = chat.full_name or chat.first_name or "Admin"
        admin_uname = chat.username or ""
    except Exception:
        pass

    current_admin_id = message.from_user.id if message.from_user else 0
    await add_admin(new_admin_id, username=admin_uname, full_name=admin_name, added_by=current_admin_id)
    await state.clear()

    await message.answer(
        f"✅ <b>Yangi admin muvaffaqiyatli qo'shildi!</b>\n\n"
        f"👤 Nomi: <b>{admin_name}</b>\n"
        f"🆔 ID: <code>{new_admin_id}</code>\n\n"
        f"Endi ushbu shaxs ham botda <code>/admin</code> buyrug'idan va admin panelidan to'liq foydalana oladi!",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )

    try:
        await bot.send_message(
            new_admin_id,
            "🎉 <b>Tabriklaymiz!</b>\n\n"
            "Sizga <b>Alixan Fast Food</b> rasmiy botida administrator huquqi berildi.\n\n"
            "Endi siz /admin buyrug'i orqali admin boshqaruv paneliga kirishingiz, mijozlarga rasm va xabarlar yuborishingiz mumkin!",
            parse_mode="HTML"
        )
    except Exception:
        pass

@router.callback_query(F.data.startswith("admin_remove:"))
async def remove_admin_callback(callback: CallbackQuery):
    caller_id = callback.from_user.id if callback.from_user else 0
    if not await is_admin(caller_id):
        await callback.answer("Ruxsat berilmagan!", show_alert=True)
        return

    target_id = int(callback.data.split(":")[1])
    if target_id in config.ADMIN_IDS:
        await callback.answer("Asosiy bosh adminni o'chirib bo'lmaydi!", show_alert=True)
        return

    ok = await remove_admin(target_id)
    if ok:
        await callback.answer("Admin o'chirildi!", show_alert=True)
        await callback.message.edit_text(
            f"✅ ID: <code>{target_id}</code> bo'lgan adminlik huquqi bekor qilindi.",
            parse_mode="HTML"
        )
    else:
        await callback.answer("O'chirishda xatolik!", show_alert=True)

@router.callback_query(F.data == "admin_close_panel")
async def admin_close_panel_callback(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer("Yopildi")

# ==================== 6. SOZLAMALAR VA GURUHLAR ====================
@router.message(F.text.in_(["⚙️ Sozlamalar & Guruhlar", "⚙️ Sozlamalar"]))
async def admin_settings_handler(message: Message):
    user_id = message.from_user.id if message.from_user else 0
    if not await is_admin(user_id):
        return

    groups = await get_all_active_groups()
    group_txt = f"{len(groups)} ta guruh ulangan" if groups else "Hozircha guruh ulanmagan"
    miniapp_url = await get_setting("mini_app_url", config.MINI_APP_URL)
    delivery_fee = await get_setting("delivery_fee", config.DEFAULT_DELIVERY_PRICE)
    work_hours = await get_setting("work_hours", config.DEFAULT_WORK_HOURS)

    text = (
        "⚙️ <b>BOTNING ASOSIY SOZLAMALARI:</b>\n\n"
        f"1️⃣ <b>Mini App Web Havolasi:</b>\n<code>{miniapp_url}</code>\n\n"
        f"2️⃣ <b>Yetkazib berish narxi:</b>\n{delivery_fee}\n\n"
        f"3️⃣ <b>Ish vaqti:</b>\n{work_hours}\n\n"
        f"4️⃣ <b>Guruhlar:</b>\n{group_txt}\n\n"
        "O'zgartirmoqchi bo'lgan ma'lumotingizni tanlang 👇"
    )

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Yangi guruh qo'shish", callback_data="manual_add_group")],
            [InlineKeyboardButton(text="📋 Guruhlar ro'yxati", callback_data="view_groups_list")],
            [InlineKeyboardButton(text="🛵 Yetkazib berish narxini o'zgartirish", callback_data="setting_edit_delivery")],
            [InlineKeyboardButton(text="⏰ Ish vaqtini o'zgartirish", callback_data="setting_edit_workhours")],
            [InlineKeyboardButton(text="🌐 Mini App URL ni o'zgartirish", callback_data="setting_edit_miniapp")],
            [InlineKeyboardButton(text="🔙 Yopish", callback_data="admin_close_settings")]
        ]
    )
    await message.answer(text, parse_mode="HTML", reply_markup=inline_kb)

@router.callback_query(F.data == "view_groups_list")
async def view_groups_callback(callback: CallbackQuery):
    groups = await get_all_active_groups()
    if not groups:
        await callback.answer("Hozircha guruhlar mavjud emas.", show_alert=True)
        return

    txt = "📋 <b>ULANGAN GURUHLAR RO'YXATI:</b>\n\n"
    for i, g in enumerate(groups, 1):
        txt += f"{i}. <b>{g['title']}</b>\n   ID: <code>{g['chat_id']}</code>\n   Qo'shilgan: <i>{g['added_at']}</i>\n\n"
    await callback.message.answer(txt, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "manual_add_group")
async def manual_add_group_prompt(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_add_group_id)
    await callback.message.answer(
        "➕ <b>Guruh Chat ID sini kiriting:</b>\n\n"
        "Masalan: <code>-1001234567890</code>\n\n"
        "<i>Eslatma: Guruh ID sini bilish uchun @ShowJsonBot yoki @username_to_id_bot ga guruhdan biror xabar forward qilishingiz mumkin. "
        "Yoki eng osoni — botni guruhga admin qilib qo'shsangiz, bot avtomatik ulanadi!</i>\n\n"
        "Bekor qilish uchun /cancel deb yozing.",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_add_group_id)
async def save_manual_group(message: Message, state: FSMContext, bot: Bot):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_admin_keyboard())
        return

    raw_id = (message.text or "").strip()
    try:
        chat_id = int(raw_id)
        chat = await bot.get_chat(chat_id)
        await add_or_update_group(chat.id, chat.title or "Guruh", chat.username)
        await state.clear()
        await message.answer(
            f"✅ <b>Guruh muvaffaqiyatli ulandi!</b>\n\n"
            f"📌 Nomi: <b>{chat.title}</b>\n"
            f"🆔 ID: <code>{chat.id}</code>",
            parse_mode="HTML",
            reply_markup=get_admin_keyboard()
        )
    except Exception as e:
        await message.answer(
            f"⚠️ Guruh topilmadi yoki bot u yerda a'zo emas!\n"
            f"Xatolik: {e}\n\n"
            f"Iltimos, avval botni o'sha guruhga a'zo qiling va qayta urinib ko'ring, yoki /cancel bosing."
        )

@router.callback_query(F.data == "admin_close_settings")
async def close_settings_callback(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer("Yopildi")

@router.callback_query(F.data == "setting_edit_miniapp")
async def edit_miniapp_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_new_miniapp_url)
    await callback.message.answer(
        "🌐 <b>Yangi Mini App URL manzilini yuboring:</b>\n\n"
        "Bekor qilish uchun /cancel deb yozing.",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_new_miniapp_url)
async def save_new_miniapp_url(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_admin_keyboard())
        return

    new_url = (message.text or "").strip()
    if not (new_url.startswith("http://") or new_url.startswith("https://")):
        await message.answer("⚠️ URL manzili http:// yoki https:// bilan boshlanishi kerak. Qaytadan kiriting:")
        return

    await set_setting("mini_app_url", new_url)
    await state.clear()
    await message.answer(f"✅ Mini App URL saqlandi:\n<code>{new_url}</code>", parse_mode="HTML", reply_markup=get_admin_keyboard())

@router.callback_query(F.data == "setting_edit_delivery")
async def edit_delivery_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_new_delivery_fee)
    await callback.message.answer(
        "🛵 <b>Yangi yetkazib berish narxini yozing:</b> (Masalan: <code>5 000 so'm</code>)\n\n"
        "Bekor qilish uchun /cancel deb yozing.",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_new_delivery_fee)
async def save_new_delivery_fee(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_admin_keyboard())
        return

    new_val = (message.text or "").strip()
    await set_setting("delivery_fee", new_val)
    await state.clear()
    await message.answer(f"✅ Yetkazib berish narxi yangilandi: <b>{new_val}</b>", parse_mode="HTML", reply_markup=get_admin_keyboard())

@router.callback_query(F.data == "setting_edit_workhours")
async def edit_workhours_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_new_workhours)
    await callback.message.answer(
        "⏰ <b>Yangi ish vaqtini kiriting:</b> (Masalan: <code>Har kuni to'xtovsiz: 09:00 dan 02:00 gacha</code>)\n\n"
        "Bekor qilish uchun /cancel deb yozing.",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_new_workhours)
async def save_new_workhours(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_admin_keyboard())
        return

    new_val = (message.text or "").strip()
    await set_setting("work_hours", new_val)
    await state.clear()
    await message.answer(f"✅ Ish vaqti yangilandi: <b>{new_val}</b>", parse_mode="HTML", reply_markup=get_admin_keyboard())
