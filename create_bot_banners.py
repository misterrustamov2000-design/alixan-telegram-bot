import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

IMAGES_DIR = r"C:\Users\Brand\.gemini\antigravity\scratch\alixan-telegram-bot\images"
LOGO_PATH = os.path.join(IMAGES_DIR, "logo.png")

def get_font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Users\Brand\.gemini\antigravity\scratch\alixan-fastfood\assets\Outfit.ttf"
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

def create_card_base(width=1000, height=560, bg_color1=(24, 24, 30), bg_color2=(12, 12, 16)):
    img = Image.new("RGB", (width, height), bg_color1)
    draw = ImageDraw.Draw(img)
    # subtle gradient
    for y in range(height):
        factor = y / height
        r = int(bg_color1[0] * (1 - factor) + bg_color2[0] * factor)
        g = int(bg_color1[1] * (1 - factor) + bg_color2[1] * factor)
        b = int(bg_color1[2] * (1 - factor) + bg_color2[2] * factor)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Outer luxury golden border
    draw.rounded_rectangle([15, 15, width - 15, height - 15], radius=24, outline=(218, 165, 32, 180), width=3)
    draw.rounded_rectangle([22, 22, width - 22, height - 22], radius=18, outline=(180, 130, 20, 80), width=1)
    return img

def create_welcome_banner():
    width, height = 1000, 560
    img = create_card_base(width, height, (26, 22, 20), (14, 12, 11))
    draw = ImageDraw.Draw(img)

    # Paste logo if exists
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            # Resize keeping aspect ratio
            logo.thumbnail((480, 240), Image.Resampling.LANCZOS)
            lw, lh = logo.size
            pos_x = (width - lw) // 2
            pos_y = 60
            img.paste(logo, (pos_x, pos_y), logo)
        except Exception as e:
            print("Logo load error:", e)

    font_title = get_font(38, bold=True)
    font_sub = get_font(22, bold=False)
    font_tag = get_font(18, bold=True)

    # Subtitle text
    text1 = "Kattaqo'rg'ondagi eng mazali Fast-Food maskani"
    bbox1 = draw.textbbox((0, 0), text1, font=font_title)
    tw1 = bbox1[2] - bbox1[0]
    draw.text(((width - tw1) // 2, 330), text1, fill=(255, 235, 190), font=font_title)

    text2 = "Har bir luqmada haqiqiy lazzat! Buyurtma va yetkazib berish xizmati"
    bbox2 = draw.textbbox((0, 0), text2, font=font_sub)
    tw2 = bbox2[2] - bbox2[0]
    draw.text(((width - tw2) // 2, 390), text2, fill=(210, 210, 210), font=font_sub)

    # Badge: Yetkazib berish 5 000 so'm
    badge_text = "🛵 Yetkazib berish: 5 000 so'm  |  ⏰ 09:00 - 02:00"
    bbox_b = draw.textbbox((0, 0), badge_text, font=font_tag)
    bw = bbox_b[2] - bbox_b[0]
    bx = (width - bw) // 2
    by = 450
    draw.rounded_rectangle([bx - 20, by - 8, bx + bw + 20, by + 34], radius=16, fill=(220, 53, 34), outline=(255, 200, 100), width=2)
    draw.text((bx, by), badge_text, fill=(255, 255, 255), font=font_tag)

    out_path = os.path.join(IMAGES_DIR, "banner_welcome.jpg")
    img.save(out_path, quality=95)
    print("Created:", out_path)

def create_about_banner():
    width, height = 1000, 520
    img = create_card_base(width, height, (30, 20, 18), (16, 12, 10))
    draw = ImageDraw.Draw(img)

    # Icon / Title
    font_title = get_font(42, bold=True)
    font_desc = get_font(22, bold=False)
    font_gold = get_font(26, bold=True)

    title = "BIZ HAQIMIZDA"
    bbox_t = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox_t[2] - bbox_t[0]
    draw.text(((width - tw) // 2, 50), title, fill=(245, 197, 66), font=font_title)

    slogan = "👑 ALIXAN FAST FOOD — Sifat va Lazzat Uyg'unligi"
    bbox_s = draw.textbbox((0, 0), slogan, font=font_gold)
    sw = bbox_s[2] - bbox_s[0]
    draw.text(((width - sw) // 2, 120), slogan, fill=(255, 255, 255), font=font_gold)

    draw.line([(width // 2 - 150, 175), (width // 2 + 150, 175)], fill=(218, 165, 32), width=2)

    features = [
        "✨ 100% Halol, toza va oliy toifadagi yangi go'sht mahsulotlari",
        "🔥 Maxsus tandirda yopilgan qarsildoq nonlar va xushbo'y souslar",
        "⚡️ Tezkor tayyorlash va Kattaqo'rg'on shahrida sifatli xizmat",
        "❤️ Mijozlarimiz mehrini qozongan shinam va zamonaviy fast-food"
    ]
    y_pos = 210
    for feat in features:
        bbox_f = draw.textbbox((0, 0), feat, font=font_desc)
        fw = bbox_f[2] - bbox_f[0]
        draw.text(((width - fw) // 2, y_pos), feat, fill=(230, 230, 230), font=font_desc)
        y_pos += 45

    badge = "⭐ Kattaqo'rg'on, Alisher Navoiy ko'chasi, 5-maktab yaqinida"
    bbox_b = draw.textbbox((0, 0), badge, font=get_font(19, bold=True))
    bw = bbox_b[2] - bbox_b[0]
    draw.rounded_rectangle([((width - bw) // 2) - 16, 420, ((width + bw) // 2) + 16, 465], radius=14, fill=(40, 30, 25), outline=(218, 165, 32), width=1)
    draw.text(((width - bw) // 2, 430), badge, fill=(245, 197, 66), font=get_font(19, bold=True))

    out_path = os.path.join(IMAGES_DIR, "banner_about.jpg")
    img.save(out_path, quality=95)
    print("Created:", out_path)

def create_contacts_banner():
    width, height = 1000, 520
    img = create_card_base(width, height, (18, 25, 30), (10, 15, 18))
    draw = ImageDraw.Draw(img)

    font_title = get_font(42, bold=True)
    font_bold = get_font(28, bold=True)
    font_num = get_font(26, bold=True)
    font_sub = get_font(20, bold=False)

    title = "TELEFON VA BUYURTMA"
    bbox_t = draw.textbbox((0, 0), title, font=font_title)
    draw.text(((width - (bbox_t[2] - bbox_t[0])) // 2, 50), title, fill=(66, 185, 245), font=font_title)

    desc = "📞 Bitta qo'ng'iroq orqali issiq taomlarni yetkazib beramiz!"
    bbox_d = draw.textbbox((0, 0), desc, font=font_bold)
    draw.text(((width - (bbox_d[2] - bbox_d[0])) // 2, 120), desc, fill=(255, 255, 255), font=font_bold)

    phones = [
        ("📞 +998 (91) 033-33-93", "Operator / Asosiy raqam"),
        ("📞 +998 (90) 447-79-99", "Tezkor buyurtma"),
        ("📞 +998 (99) 678-79-77", "Yetkazib berish xizmati")
    ]
    card_y = 190
    for num, label in phones:
        cx1, cx2 = 180, width - 180
        draw.rounded_rectangle([cx1, card_y, cx2, card_y + 60], radius=14, fill=(25, 38, 48), outline=(66, 185, 245), width=2)
        draw.text((cx1 + 25, card_y + 14), num, fill=(255, 255, 255), font=font_num)
        
        bbox_l = draw.textbbox((0, 0), label, font=font_sub)
        lw = bbox_l[2] - bbox_l[0]
        draw.text((cx2 - lw - 25, card_y + 18), label, fill=(180, 220, 245), font=font_sub)
        card_y += 75

    delivery_txt = "🛵 Shahar bo'ylab yetkazib berish narxi: 5 000 so'm"
    bbox_del = draw.textbbox((0, 0), delivery_txt, font=get_font(21, bold=True))
    dw = bbox_del[2] - bbox_del[0]
    draw.text(((width - dw) // 2, 440), delivery_txt, fill=(255, 215, 0), font=get_font(21, bold=True))

    out_path = os.path.join(IMAGES_DIR, "banner_contacts.jpg")
    img.save(out_path, quality=95)
    print("Created:", out_path)

def create_menu_banner():
    width, height = 1000, 520
    img = create_card_base(width, height, (32, 22, 15), (18, 12, 8))
    draw = ImageDraw.Draw(img)

    font_title = get_font(44, bold=True)
    font_bold = get_font(26, bold=True)
    font_sub = get_font(22, bold=False)

    title = "TAOMLAR MENYUSI"
    bbox_t = draw.textbbox((0, 0), title, font=font_title)
    draw.text(((width - (bbox_t[2] - bbox_t[0])) // 2, 45), title, fill=(255, 175, 40), font=font_title)

    sub = "ALIXAN FAST FOOD — Lazzatli va sifatli taomlar olami"
    bbox_s = draw.textbbox((0, 0), sub, font=font_bold)
    draw.text(((width - (bbox_s[2] - bbox_s[0])) // 2, 115), sub, fill=(255, 255, 255), font=font_bold)

    cats = [
        "🌯 Tandir Lavashlar", "🍔 Shirin & Sersuv Burgerlar",
        "🥙 Maxsus Donarlar", "🍗 Qarsildoq KFC va Fri",
        "🌭 To'yimli Hot-Doglar", "🍕 Issiqqina Pitsalar",
        "🥪 Chiken & Pocket", "🥤 Salqin Ichimliklar"
    ]
    start_y = 180
    for i in range(0, len(cats), 2):
        c1, c2 = cats[i], cats[i+1]
        draw.rounded_rectangle([100, start_y, 470, start_y + 50], radius=12, fill=(45, 30, 20), outline=(218, 165, 32), width=1)
        draw.text((120, start_y + 11), c1, fill=(240, 240, 240), font=font_sub)

        draw.rounded_rectangle([530, start_y, 900, start_y + 50], radius=12, fill=(45, 30, 20), outline=(218, 165, 32), width=1)
        draw.text((550, start_y + 11), c2, fill=(240, 240, 240), font=font_sub)
        start_y += 65

    btn_text = "📲 Quyidagi 'Mini App Menyuni ochish' tugmasini bosing!"
    bbox_btn = draw.textbbox((0, 0), btn_text, font=get_font(20, bold=True))
    draw.text(((width - (bbox_btn[2] - bbox_btn[0])) // 2, 455), btn_text, fill=(255, 220, 100), font=get_font(20, bold=True))

    out_path = os.path.join(IMAGES_DIR, "banner_menu.jpg")
    img.save(out_path, quality=95)
    print("Created:", out_path)

if __name__ == "__main__":
    create_welcome_banner()
    create_about_banner()
    create_contacts_banner()
    create_menu_banner()
    print("All banners created successfully!")
