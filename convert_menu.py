import json
import re

js_file = r"C:\Users\Brand\.gemini\antigravity\scratch\alixan-fastfood\assets\data.js"
with open(js_file, "r", encoding="utf-8") as f:
    content = f.read()

# Parse restaurant, categories, products from JS
# In data.js, it's const MENU_DATA = { ... };
# We can extract using node or simple JS evaluation
import subprocess

node_script = f"""
const fs = require('fs');
const content = fs.readFileSync({json.dumps(js_file)}, 'utf8');
eval(content.replace('const MENU_DATA =', 'global.MENU_DATA ='));
console.log(JSON.stringify(global.MENU_DATA, null, 2));
"""

res = subprocess.run(["node", "-e", node_script], capture_output=True, encoding="utf-8", check=True)
data = json.loads(res.stdout)

out_file = r"C:\Users\Brand\.gemini\antigravity\scratch\alixan-telegram-bot\menu_data.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(data.get('categories', []))} categories and {len(data.get('products', []))} products to {out_file}")
