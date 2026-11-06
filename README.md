# 🍔 ALIXAN FAST FOOD — Professional Telegram Bot & Mini App Integratsiyasi

Ushbu loyiha **Alixan Fast Food** (Samarqand viloyati, Kattaqo'rg'on shahri) restorani uchun maxsus ishlab chiqilgan professional va to'liq funksional Telegram bot hisoblanadi.

---

## 🌟 Asosiy Imkoniyatlar va Bo'limlar

1. **👑 Start va Xush Kelibsiz Bosh Sahifasi**:
   - Botga start bosilganda Alixan Fast Food rasmiy logosi va jozibador tabrik xabari keladi.
   - Doimiy zamonaviy menyu klaviaturasi (Reply Keyboard) va tezkor inline tugmalar.

2. **🍔 Taomlar Menyusi (Mini App va Bot ichida)**:
   - **Mini App**: Tugmani bosish orqali to'g'ridan-to'g'ri interaktiv veb-menyu ochiladi.
   - **Bot ichida toifalar**: Hot-Doglar, Tandir Lavash, Burgerlar, Donarlar, KFC va Fri, Chiken, Pitsalar, Salqin Ichimliklar.
   - Har bir taomning fotosurati, narxi, tarkibi va `◀️ Oldingi`, `Keyingi ▶️` tugmalari orqali varaqlash.

3. **ℹ️ Biz Haqimizda**:
   - Maxsus dizayndagi "Biz Haqimizda" banneri.
   - Restoran tarixi, 100% Halol mahsulotlar kafolati, tandir xamirlari va mijozlar mehrini qozongan sifat haqida to'liq ma'lumot.

4. **📞 Telefon Raqamlar va Tezkor Qo'ng'iroq**:
   - Maxsus "Telefon va Buyurtma" banneri.
   - Barcha telefon raqamlar Telegramda bir marta bosish orqali qo'ng'iroq qilish imkoniyati bilan:
     - `+998 (91) 033-33-93` (Operator / Asosiy raqam)
     - `+998 (90) 447-79-99` (Tezkor buyurtma)
     - `+998 (99) 678-79-77` (Yetkazib berish xizmati)
   - Nusxa olish uchun qulay format va Telegram orqali bog'lanish tugmasi.

5. **📍 Manzil va Ish Vaqti**:
   - Siz yuborgan rasmiy info-banner (Ish vaqti, manzil, telefon va xarita).
   - Ish vaqti: **Har kuni to'xtovsiz: 09:00 dan 02:00 gacha** (dam olish kunlarisiz).
   - Manzil: Samarqand viloyati, Kattaqo'rg'on shahri, Alisher Navoiy ko'chasi, 5-maktab yaqinida.
   - Google Xarita havolasi va Telegramning o'zida jonli GPS nuqtani (Venue/Location) tashlash tugmasi!

6. **🛵 Yetkazib Berish Shartlari**:
   - Kattaqo'rg'on shahri bo'ylab yetkazib berish narxi: **5 000 so'm**.
   - Termo-sumkalarda issiq yetkazish va to'lov turlari (Naqd, Click, Payme).

7. **⚙️ Professional Admin Panel (`/admin`)**:
   - **Faqat adminlar uchun**: Boshqalar kira olmaydi (ID orqali xavfsiz himoyalangan).
   - **📊 Statistika**: Jami foydalanuvchilar, bugun qo'shilganlar, haftalik faollar, bloklaganlar.
   - **📢 Reklama va Xabar Yuborish (Broadcast)**:
     - Barcha bot foydalanuvchilariga matn, rasm yoki forward xabarlarni bir zumda tarqatish.
     - Yuborishdan oldin ko'rib chiqish (preview) va tasdiqlash.
     - Anti-flood himoyasi va real-vaqt hisoboti (Yetib bordi: X, Bloklagan: Y).
   - **👥 Foydalanuvchilar Ro'yxati**: Barcha faol foydalanuvchilar ID ro'yxatini yuklab olish.
   - **⚙️ Jonli Sozlamalar**: Mini App URL, Yetkazib berish narxi va Ish vaqtini botning o'zidan o'zgartirish!

8. **✍️ Fikr va Takliflar**:
   - Foydalanuvchilar qoldirgan fikrlar avtomatik tarzda bazaga saqlanadi va adminlarga yetkaziladi.

---

## 🚀 Ishga Tushirish Bo'yicha Qo'llanma

### 1-qadam: Bot Tokenini olish
1. Telegramda [@BotFather](https://t.me/BotFather) ga kiring va `/newbot` buyrug'ini yuboring.
2. Bot nomini (masalan: `Alixan Fast Food`) va username'ini (masalan: `alixan_kafe_bot`) kiriting.
3. BotFather bergan **HTTP API Token**ni nusxalang.

### 2-qadam: `.env` faylini to'ldirish
Loyihadagi `.env` faylini oching va tokenni kiriting:
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=123456789
MINI_APP_URL=https://t.me/alixan_fastfood_bot/app
```
*(Eslatma: O'z Telegram ID raqamingizni bilmasangiz, botni ishga tushirib unga `/admin` deb yozing — bot sizga aynan qaysi ID ni `.env` ga yozish kerakligini aytadi!)*

### 3-qadam: Botni ishga tushirish
Windows tizimida bot papkasida turib:
```powershell
python bot.py
```
yoki to'g'ridan-to'g'ri `run_bot.bat` faylini sichqoncha bilan ikki marta bosing!
