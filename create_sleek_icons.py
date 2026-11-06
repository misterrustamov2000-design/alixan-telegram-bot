import os
import math
from PIL import Image, ImageDraw, ImageFilter

IMAGES_DIR = r"C:\Users\Brand\.gemini\antigravity\scratch\alixan-telegram-bot\images"
os.makedirs(IMAGES_DIR, exist_ok=True)

W, H = 800, 480

def create_base_canvas(color_center=(35, 30, 25), color_edge=(15, 12, 10)):
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(canvas)
    cx, cy = W // 2, H // 2
    max_radius = math.hypot(cx, cy)
    for y in range(H):
        for x in range(0, W, 2):
            dist = math.hypot(x - cx, y - cy) / max_radius
            r = int(color_center[0] * (1 - dist) + color_edge[0] * dist)
            g = int(color_center[1] * (1 - dist) + color_edge[1] * dist)
            b = int(color_center[2] * (1 - dist) + color_edge[2] * dist)
            draw.line([(x, y), (x + 1, y)], fill=(r, g, b, 255))
    return canvas

def add_glow_and_circle(img, center_color=(255, 180, 50), outer_color=(200, 140, 20)):
    cx, cy = W // 2, H // 2
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    
    # Soft background glow
    gdraw.ellipse([cx - 160, cy - 160, cx + 160, cy + 160], fill=(center_color[0], center_color[1], center_color[2], 40))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    img.alpha_composite(glow)

    # Clean circle container
    draw = ImageDraw.Draw(img)
    r = 130
    draw.ellipse([cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8], outline=(outer_color[0], outer_color[1], outer_color[2], 100), width=3)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(22, 20, 26, 230), outline=(center_color[0], center_color[1], center_color[2], 255), width=4)
    return img

def draw_phone_icon():
    img = create_base_canvas(color_center=(20, 35, 45), color_edge=(10, 15, 20))
    img = add_glow_and_circle(img, center_color=(50, 180, 255), outer_color=(20, 120, 200))
    
    # Draw high quality sleek telephone receiver
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # Draw modern 3D phone handset in the center
    # Left earpiece, bridge, right mouthpiece
    phone_color = (255, 255, 255)
    accent_color = (50, 200, 255)
    
    # Angled handset (approx 35 degrees)
    # Using smooth poly / shapes
    # Left ear round
    draw.rounded_rectangle([cx - 75, cy - 65, cx - 35, cy - 15], radius=15, fill=accent_color)
    draw.rounded_rectangle([cx - 70, cy - 60, cx - 40, cy - 20], radius=10, fill=phone_color)

    # Right mouth round
    draw.rounded_rectangle([cx + 35, cy + 15, cx + 75, cy + 65], radius=15, fill=accent_color)
    draw.rounded_rectangle([cx + 40, cy + 20, cx + 70, cy + 60], radius=10, fill=phone_color)

    # Connecting handle bar
    draw.polygon([
        (cx - 50, cy - 25), (cx - 30, cy - 40),
        (cx + 40, cy + 25), (cx + 25, cy + 45)
    ], fill=accent_color)
    draw.polygon([
        (cx - 45, cy - 23), (cx - 32, cy - 35),
        (cx + 35, cy + 23), (cx + 25, cy + 38)
    ], fill=phone_color)

    # Sound wave rings to the top right
    for rad, width in [(35, 4), (55, 4), (75, 3)]:
        bbox = [cx + 10, cy - 90 - (rad - 35), cx + 10 + rad * 2, cy - 90 + rad]
        draw.arc(bbox, start=270, end=360, fill=(70, 210, 255, 220), width=width)

    out = img.convert("RGB")
    out.save(os.path.join(IMAGES_DIR, "icon_contacts.jpg"), quality=95)
    print("Created icon_contacts.jpg")

def draw_about_icon():
    img = create_base_canvas(color_center=(40, 30, 20), color_edge=(15, 12, 10))
    img = add_glow_and_circle(img, center_color=(255, 200, 50), outer_color=(200, 150, 20))
    
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # Draw royal golden crown (symbolizing Alixan logo)
    gold = (255, 210, 60)
    gold_dark = (210, 160, 20)
    white = (255, 255, 255)

    # Crown base
    draw.rounded_rectangle([cx - 65, cy + 30, cx + 65, cy + 48], radius=8, fill=gold_dark)
    draw.rounded_rectangle([cx - 62, cy + 32, cx + 62, cy + 45], radius=6, fill=gold)

    # Crown spikes (5 points)
    points = [
        (cx - 60, cy + 30),
        (cx - 65, cy - 30),  # left peak
        (cx - 30, cy + 5),   # inner left dip
        (cx, cy - 55),       # center highest peak
        (cx + 30, cy + 5),   # inner right dip
        (cx + 65, cy - 30),  # right peak
        (cx + 60, cy + 30)
    ]
    draw.polygon(points, fill=gold)

    # Golden jewels / pearls on peaks
    for px, py in [(cx - 65, cy - 30), (cx, cy - 55), (cx + 65, cy - 30)]:
        draw.ellipse([px - 10, py - 10, px + 10, py + 10], fill=gold_dark)
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=white)

    # Inner stars
    draw.ellipse([cx - 30, cy + 38, cx - 22, cy + 44], fill=white)
    draw.ellipse([cx - 4, cy + 38, cx + 4, cy + 44], fill=white)
    draw.ellipse([cx + 22, cy + 38, cx + 30, cy + 44], fill=white)

    out = img.convert("RGB")
    out.save(os.path.join(IMAGES_DIR, "icon_about.jpg"), quality=95)
    print("Created icon_about.jpg")

def draw_location_icon():
    img = create_base_canvas(color_center=(35, 20, 25), color_edge=(15, 10, 12))
    img = add_glow_and_circle(img, center_color=(255, 80, 80), outer_color=(200, 50, 50))
    
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2 - 10

    # Draw vibrant 3D Map Pin
    red = (235, 55, 55)
    red_dark = (180, 30, 30)
    white = (255, 255, 255)

    # Pin point shadow on floor
    draw.ellipse([cx - 35, cy + 85, cx + 35, cy + 105], fill=(10, 8, 8, 160))

    # Pin head circle
    r = 55
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=red_dark)
    draw.ellipse([cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3], fill=red)

    # Pin bottom triangle tip
    draw.polygon([
        (cx - 42, cy + 15),
        (cx + 42, cy + 15),
        (cx, cy + 90)
    ], fill=red)

    # Inner white hole
    draw.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=(22, 20, 26))
    draw.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=white)

    out = img.convert("RGB")
    out.save(os.path.join(IMAGES_DIR, "icon_location.jpg"), quality=95)
    print("Created icon_location.jpg")

def draw_menu_icon():
    img = create_base_canvas(color_center=(40, 25, 15), color_edge=(18, 10, 8))
    img = add_glow_and_circle(img, center_color=(255, 160, 40), outer_color=(210, 120, 20))
    
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # Draw delicious 3D Burger icon
    bun_color = (230, 150, 60)
    patty_color = (110, 60, 35)
    cheese_color = (255, 200, 30)
    salad_color = (80, 180, 50)
    tomato_color = (220, 50, 40)

    # Bottom bun
    draw.rounded_rectangle([cx - 65, cy + 30, cx + 65, cy + 55], radius=12, fill=bun_color)

    # Patty
    draw.rounded_rectangle([cx - 70, cy + 12, cx + 70, cy + 30], radius=8, fill=patty_color)

    # Cheese melting
    draw.polygon([
        (cx - 68, cy + 10), (cx + 68, cy + 10),
        (cx + 40, cy + 22), (cx - 20, cy + 10), (cx - 50, cy + 24)
    ], fill=cheese_color)

    # Tomato layer
    draw.rounded_rectangle([cx - 65, cy - 5, cx + 65, cy + 10], radius=6, fill=tomato_color)

    # Salad wavy layer
    draw.rounded_rectangle([cx - 70, cy - 18, cx + 70, cy - 4], radius=6, fill=salad_color)

    # Top bun (dome)
    draw.pieslice([cx - 72, cy - 70, cx + 72, cy + 10], start=180, end=360, fill=bun_color)

    # Sesame seeds on top
    for sx, sy in [(-40, -40), (-15, -55), (10, -50), (35, -38), (-20, -30), (15, -28)]:
        draw.ellipse([cx + sx - 3, cy + sy - 2, cx + sx + 3, cy + sy + 2], fill=(255, 240, 200))

    out = img.convert("RGB")
    out.save(os.path.join(IMAGES_DIR, "icon_menu.jpg"), quality=95)
    print("Created icon_menu.jpg")

def create_clean_logo_banner():
    # Centered logo with pure elegance and soft lighting, zero noisy duplicate text!
    img = create_base_canvas(color_center=(30, 24, 20), color_edge=(12, 10, 8))
    logo_path = os.path.join(IMAGES_DIR, "logo.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo.thumbnail((420, 240), Image.Resampling.LANCZOS)
        lw, lh = logo.size
        cx, cy = (W - lw) // 2, (H - lh) // 2

        # Soft glow behind logo
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        gdraw.ellipse([cx - 40, cy - 20, cx + lw + 40, cy + lh + 20], fill=(255, 200, 100, 50))
        glow = glow.filter(ImageFilter.GaussianBlur(35))
        img.alpha_composite(glow)

        img.paste(logo, (cx, cy), logo)

    out = img.convert("RGB")
    out.save(os.path.join(IMAGES_DIR, "icon_welcome.jpg"), quality=95)
    print("Created icon_welcome.jpg")

if __name__ == "__main__":
    draw_phone_icon()
    draw_about_icon()
    draw_location_icon()
    draw_menu_icon()
    create_clean_logo_banner()
    print("All sleek icons generated successfully!")
