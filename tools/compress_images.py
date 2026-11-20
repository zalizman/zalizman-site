"""Komprimera webbbilder för zalizman-site. Kör: python tools/compress_images.py"""
import os
from PIL import Image

IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "site", "images")

# (fil, maxbredd) — produkter/skärmdumpar visas max ~600px på sidan, 2x-retina => 1200-1400
TARGETS = {
    "gaptrader.png": 1200,
    "futuretrader.png": 1200,
    "matrix-indicator.png": 1400,
    "tradecontrol.png": 1200,
    "linehelper.png": 1200,
    "ai-validator.png": 1400,
    "logo.png": 512,
    "dash1.png": 1400,
    "dash2.png": 1400,
    "checks.png": 1400,
    "conf.png": 1400,
    "gap.png": 1400,
    "ai.png": 1400,
    "namnlos.png": 1400,
    "linehelper-chart.png": 1400,
}

total_before = total_after = 0
for name, maxw in TARGETS.items():
    path = os.path.join(IMG_DIR, name)
    if not os.path.exists(path):
        print("saknas:", name)
        continue
    before = os.path.getsize(path)
    img = Image.open(path)
    # logga in bevaras som PNG (skarpa kanter), övriga -> JPEG på vit bakgrund
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        keep_png = name == "logo.png"
    else:
        keep_png = False
    if img.width > maxw:
        h = round(img.height * maxw / img.width)
        img = img.resize((maxw, h), Image.LANCZOS)
    if keep_png:
        out_path = path
        img.save(out_path, "PNG", optimize=True)
    else:
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[-1])
            img = bg
        out_path = path.rsplit(".", 1)[0] + ".jpg"
        img.save(out_path, "JPEG", quality=82, optimize=True, progressive=True)
        if out_path != path:
            os.remove(path)
    after = os.path.getsize(out_path)
    total_before += before
    total_after += after
    print(f"{name}: {before//1024} kB -> {after//1024} kB {'=> ' + os.path.basename(out_path) if out_path != path else ''}")

print(f"\nTOTALT: {total_before//1024} kB -> {total_after//1024} kB")
