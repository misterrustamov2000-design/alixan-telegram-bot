import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Super Admin ID (Doimiy Bosh Admin)
SUPER_ADMIN_ID = 1215985999

# Admin IDs (comma separated string in .env: "12345678,987654321")
raw_admins = os.getenv("ADMIN_IDS", "1215985999").strip()
ADMIN_IDS = [int(x.strip()) for x in raw_admins.split(",") if x.strip().isdigit()]
if SUPER_ADMIN_ID not in ADMIN_IDS:
    ADMIN_IDS.append(SUPER_ADMIN_ID)

# Mini App URL (e.g. Netlify, Vercel or GitHub Pages)
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://alixan-fast-food.netlify.app/").strip()

# Google Maps link
MAPS_URL = os.getenv("MAPS_URL", "https://maps.app.goo.gl/Fhy5qVkYocFi2C92A?g_st=atm").strip()

# Restaurant defaults
DEFAULT_RESTAURANT_NAME = "ALIXAN FAST FOOD"
DEFAULT_PHONES = [
    "+998910333393",
    "+998904477999",
    "+998996787977"
]
DEFAULT_WORK_HOURS = "Har kuni to'xtovsiz: 10:00 dan 00:00 gacha. Dam olish kunlarisiz xizmatingizdamiz."
DEFAULT_ADDRESS = "Samarqand viloyati, Kattaqo'rg'on shahri, Alisher Navoiy ko'chasi 23-uy. Alixan Fast Food (Cafe) restorani."
DEFAULT_DELIVERY_PRICE = "5 000 so'm (Kattaqo'rg'on shahar ichida)"
DEFAULT_DELIVERY_EXTRA = "* Shahardan tashqarida narx o'zgaradi"

# Coordinates for Kattaqo'rg'on Alixan Fast Food
LOCATION_LATITUDE = float(os.getenv("LOCATION_LATITUDE", "39.897368"))
LOCATION_LONGITUDE = float(os.getenv("LOCATION_LONGITUDE", "66.257523"))

# Paths
DB_PATH = BASE_DIR / "bot_database.sqlite3"
IMAGES_DIR = BASE_DIR / "images"
MENU_DATA_PATH = BASE_DIR / "menu_data.json"
