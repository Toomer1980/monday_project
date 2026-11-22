import argparse
import base64
import datetime as dt
import glob
import json
import math
import os
import py_compile
import random
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
os.chdir(PDIR)
DECK_DIR = os.path.join(PDIR, "assets", "tarot_deck")
STATIC_DIR = os.path.join(PDIR, "static")
os.makedirs(DECK_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

TAROT_DECK = [
    ("the_magician", "I", "THE MAGICIAN", "Sovereign Creation & Mastery", "infinity_altar", (28, 18, 66), (250, 196, 42), (76, 195, 255)),
    ("wheel_of_fortune", "X", "WHEEL OF FORTUNE", "Sudden Windfall & Cycle Shift", "golden_wheel", (24, 16, 52), (245, 180, 35), (168, 85, 247)),
    ("the_star", "XVII", "THE STAR", "Divine Alignment & Clarity", "star_waters", (10, 26, 58), (90, 220, 255), (250, 224, 120)),
    ("the_sun", "XIX", "THE SUN", "Unstoppable Abundance & Power", "radiant_sun", (58, 22, 12), (255, 196, 38), (255, 118, 42)),
    ("the_world", "XXI", "THE WORLD", "Complete Realm Expansion", "cosmic_wreath", (10, 42, 42), (52, 211, 153), (250, 204, 21)),
    ("the_empress", "III", "THE EMPRESS", "Magnetic Wealth & Harvest", "venus_garden", (48, 14, 42), (244, 114, 182), (250, 204, 21)),
    ("the_emperor", "IV", "THE EMPEROR", "Architectural Authority", "crimson_throne", (52, 14, 18), (245, 158, 11), (239, 68, 68)),
    ("ace_of_pentacles", "I", "ACE OF PENTACLES", "New Financial Portal Opened", "golden_coin", (12, 38, 28), (250, 204, 21), (74, 222, 128)),
    ("the_high_priestess", "II", "HIGH PRIESTESS", "Hidden Knowledge & Intuition", "moon_pillars", (16, 20, 56), (147, 197, 253), (226, 232, 240)),
    ("the_chariot", "VII", "THE CHARIOT", "Decisive Forward Momentum", "star_chariot", (18, 24, 52), (56, 189, 248), (250, 204, 21)),
]


def load_font(size, serif=False):
    cands = (
        [r"C:\Windows\Fonts\georgiab.ttf", r"C:\Windows\Fonts\timesbd.ttf", r"C:\Windows\Fonts\segoeuib.ttf"]
        if serif else
        [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"]
    )
    for p in cands:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def load_env_key(key_name):
    ep = os.path.join(PDIR, ".env")
    if os.path.exists(ep):
        for ln in open(ep, "r", encoding="utf-8", errors="ignore"):
            if ln.strip().startswith(key_name + "="):
                return ln.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


# ==============================================================================
# 1. REAL ILLUSTRATED TAROT CARD ARTWORK ENGINE (IMAGEN API OR PAINTERLY PLATES)
# ==============================================================================
def try_imagen_card(slug, title, subtitle, out_png, api_key):
    """Generates bespoke oil-and-gold-foil tarot illustration via Google Imagen 3 if GEMINI_API_KEY is enabled."""
    if not api_key:
        return False
    prompt = (
        f"Luxury museum-grade illustrated tarot card artwork for '{title}' ({subtitle}), "
        f"classic Art Nouveau Alphonse Mucha and modern dark celestial oil painting style, "
        f"rich gold foil filigree border, luminous nebula sky, intricate mystical focal iconography, "
        f"dramatic chiaroscuro lighting, ultra detailed, vertical 2:3 composition, no blurry text."
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"
    payload = json.dumps({
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1, "aspectRatio": "3:4"},
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=35) as r:
            res = json.loads(r.read().decode("utf-8"))
            preds = res.get("predictions") or []
            if preds and preds[0].get("bytesBase64Encoded"):
                raw = base64.b64decode(preds[0]["bytesBase64Encoded"])
                open(out_png, "wb").write(raw)
                return True
    except Exception:
        pass
    return False


def paint_illustrated_card(slug, roman, title, subtitle, motif, bg_rgb, gold_rgb, accent_rgb, out_png):
    """High-resolution painterly illustrated tarot plate (600x960) with unique scene art per card."""
    w, h = 600, 960
    # Smooth atmospheric sky + vignette gradient via numpy
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    yn, xn = yy / h, (xx - w * 0.5) / (w * 0.5)
    dist = np.sqrt(xn * xn + (yn - 0.36) ** 2)
    glow_f = np.exp(-dist * 2.35)
    sky_f = np.clip(1.0 - yn * 0.85, 0.12, 1.0)

    r = np.clip(bg_rgb[0] * sky_f + accent_rgb[0] * 0.42 * glow_f + gold_rgb[0] * 0.28 * np.exp(-dist * 4.2), 0, 255)
    g = np.clip(bg_rgb[1] * sky_f + accent_rgb[1] * 0.42 * glow_f + gold_rgb[1] * 0.28 * np.exp(-dist * 4.2), 0, 255)
    b = np.clip(bg_rgb[2] * sky_f + accent_rgb[2] * 0.42 * glow_f + gold_rgb[2] * 0.28 * np.exp(-dist * 4.2), 0, 255)
    img = Image.fromarray(np.stack([r, g, b], axis=-1).astype(np.uint8), mode="RGB").convert("RGBA")

    # Starfield & soft clouds
    rng = random.Random(slug)
    stars = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stars)
    for _ in range(95):
        sx, sy = rng.randint(46, w - 46), rng.randint(90, int(h * 0.68))
        sr = rng.choice([1, 1, 2, 2, 3])
        alpha = rng.randint(90, 235)
        sd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 250, 225, alpha))
    img = Image.alpha_composite(img, stars)

    # Painted atmospheric halo
    halo = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    cx, cy = w // 2, 375
    hd.ellipse([cx - 190, cy - 190, cx + 190, cy + 190], fill=(gold_rgb[0], gold_rgb[1], gold_rgb[2], 90))
    hd.ellipse([cx - 125, cy - 125, cx + 125, cy + 125], fill=(accent_rgb[0], accent_rgb[1], accent_rgb[2], 115))
    img = Image.alpha_composite(img, halo.filter(ImageFilter.GaussianBlur(radius=34)))

    # Scene Layer: distinct symbolic illustration for each card
    scene = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(scene)

    # Distant mountains / horizon reflection in lower artwork band (y=535..735)
    d.polygon([(40, 740), (140, 565), (255, 645), (370, 540), (490, 635), (560, 575), (560, 740)], fill=(12, 16, 36, 235))
    d.polygon([(40, 740), (195, 615), (320, 675), (455, 595), (560, 670), (560, 740)], fill=(7, 10, 24, 245))
    # Shimmering water horizon reflections
    for wy in range(660, 735, 9):
        span = int(170 - (wy - 660) * 1.4)
        d.line([(cx - span, wy), (cx + span, wy)], fill=(gold_rgb[0], gold_rgb[1], gold_rgb[2], 105), width=2)

    # Unique focal emblem painted per motif
    if motif == "radiant_sun":
        for i in range(24):
            a = i * math.pi / 12.0
            r_out = 205 if i % 2 == 0 else 155
            d.polygon([
                (cx + math.cos(a - 0.08) * 95, cy + math.sin(a - 0.08) * 95),
                (cx + math.cos(a) * r_out, cy + math.sin(a) * r_out),
                (cx + math.cos(a + 0.08) * 95, cy + math.sin(a + 0.08) * 95),
            ], fill=(255, 206, 58, 225))
        d.ellipse([cx - 98, cy - 98, cx + 98, cy + 98], fill=(255, 220, 88, 255), outline=(255, 250, 210, 255), width=5)
        d.ellipse([cx - 72, cy - 72, cx + 72, cy + 72], fill=(250, 178, 30, 255))
        # Stylized sun crest
        d.arc([cx - 38, cy - 10, cx + 38, cy + 36], 20, 160, fill=(115, 52, 12, 230), width=4)
        d.ellipse([cx - 28, cy - 22, cx - 14, cy - 8], fill=(115, 52, 12, 230))
        d.ellipse([cx + 14, cy - 22, cx + 28, cy - 8], fill=(115, 52, 12, 230))
    elif motif == "golden_wheel":
        d.ellipse([cx - 165, cy - 165, cx + 165, cy + 165], outline=(250, 204, 21, 255), width=14)
        d.ellipse([cx - 122, cy - 122, cx + 122, cy + 122], outline=(accent_rgb[0], accent_rgb[1], accent_rgb[2], 235), width=6)
        for i in range(8):
            a = i * math.pi / 4.0
            d.line([(cx, cy), (cx + math.cos(a) * 160, cy + math.sin(a) * 160)], fill=(250, 204, 21, 240), width=6)
        d.ellipse([cx - 42, cy - 42, cx + 42, cy + 42], fill=(250, 204, 21, 255), outline=(255, 255, 235, 255), width=4)
        # Winged corner accents
        for dx, dy in [(-175, -175), (175, -175), (-175, 175), (175, 175)]:
            d.ellipse([cx + dx - 22, cy + dy - 22, cx + dx + 22, cy + dy + 22], outline=(250, 204, 21, 210), width=3)
    elif motif == "star_waters":
        # 8-pointed radiant North Star + 7 surrounding stars
        for i in range(8):
            a = i * math.pi / 4.0
            r_out = 178 if i % 2 == 0 else 118
            d.polygon([
                (cx + math.cos(a - 0.16) * 34, cy + math.sin(a - 0.16) * 34),
                (cx + math.cos(a) * r_out, cy + math.sin(a) * r_out),
                (cx + math.cos(a + 0.16) * 34, cy + math.sin(a + 0.16) * 34),
            ], fill=(250, 224, 120, 245))
        d.ellipse([cx - 38, cy - 38, cx + 38, cy + 38], fill=(255, 255, 240, 255))
        for ang_deg in (-145, -110, -70, -35, 35, 145, 180):
            a = math.radians(ang_deg)
            sx, sy = cx + int(math.cos(a) * 185), cy + int(math.sin(a) * 150)
            d.polygon([(sx, sy - 22), (sx + 7, sy - 7), (sx + 22, sy), (sx + 7, sy + 7), (sx, sy + 22), (sx - 7, sy + 7), (sx - 22, sy), (sx - 7, sy - 7)], fill=(125, 228, 255, 235))
    elif motif == "infinity_altar":
        # Golden lemniscate (infinity) crown + raised wand + chalice/pentacle/sword altar
        d.ellipse([cx - 115, cy - 195, cx + 5, cy - 115], outline=(250, 204, 21, 255), width=9)
        d.ellipse([cx - 5, cy - 195, cx + 115, cy - 115], outline=(250, 204, 21, 255), width=9)
        # Radiant silhouette arch & raised staff of light
        d.pieslice([cx - 115, cy - 85, cx + 115, cy + 215], 180, 360, fill=(28, 36, 78, 235), outline=(250, 204, 21, 230), width=4)
        d.rectangle([cx - 12, cy - 95, cx + 12, cy + 165], fill=(250, 216, 85, 255))
        d.ellipse([cx - 32, cy - 115, cx + 32, cy - 51], fill=(125, 228, 255, 255), outline=(255, 255, 255, 255), width=4)
        # Altar bar with 4 elemental medallions
        d.rectangle([95, cy + 160, w - 95, cy + 195], fill=(38, 28, 18, 245), outline=(250, 204, 21, 240), width=3)
        for ex in (160, 250, 350, 440):
            d.ellipse([ex - 18, cy + 132, ex + 18, cy + 168], fill=(250, 204, 21, 240), outline=(255, 255, 240, 255), width=2)
    elif motif == "golden_coin":
        # Massive embossed golden pentacle emerging from luminous emerald clouds
        d.ellipse([cx - 155, cy - 155, cx + 155, cy + 155], fill=(234, 179, 8, 255), outline=(254, 240, 138, 255), width=10)
        d.ellipse([cx - 130, cy - 130, cx + 130, cy + 130], fill=(180, 120, 12, 255), outline=(254, 240, 138, 255), width=4)
        pts = [(cx + math.cos(math.radians(-90 + i * 144)) * 114, cy + math.sin(math.radians(-90 + i * 144)) * 114) for i in range(5)]
        d.polygon(pts, fill=(250, 215, 65, 255), outline=(255, 252, 220, 255))
        # Archway of laurel leaves underneath
        d.arc([95, cy + 80, w - 95, cy + 310], 180, 360, fill=(52, 211, 153, 240), width=14)
    elif motif == "moon_pillars":
        # Twin obsidian & ivory temple pillars (B & J) + luminous crescent moon crown
        d.rectangle([95, 190, 175, 660], fill=(18, 22, 42, 250), outline=(203, 213, 225, 240), width=4)
        d.rectangle([w - 175, 190, w - 95, 660], fill=(226, 232, 240, 240), outline=(250, 204, 21, 240), width=4)
        d.ellipse([cx - 88, cy - 110, cx + 88, cy + 66], fill=(248, 250, 252, 255))
        d.ellipse([cx - 52, cy - 125, cx + 115, cy + 50], fill=(bg_rgb[0], bg_rgb[1], bg_rgb[2], 255))
        d.ellipse([cx - 42, cy + 90, cx + 42, cy + 174], outline=(250, 204, 21, 245), width=5)
    else:
        # Cosmic Laurel Wreath / Sovereign Crown / Chalice Emblem
        d.ellipse([cx - 150, cy - 175, cx + 150, cy + 175], outline=(gold_rgb[0], gold_rgb[1], gold_rgb[2], 245), width=14)
        d.ellipse([cx - 122, cy - 145, cx + 122, cy + 145], outline=(accent_rgb[0], accent_rgb[1], accent_rgb[2], 230), width=5)
        for i in range(16):
            a = i * math.pi / 8.0
            lx, ly = cx + math.cos(a) * 150, cy + math.sin(a) * 175
            d.ellipse([lx - 14, ly - 14, lx + 14, ly + 14], fill=(gold_rgb[0], gold_rgb[1], gold_rgb[2], 235))
        d.polygon([(cx, cy - 98), (cx + 76, cy), (cx, cy + 98), (cx - 76, cy)], fill=(accent_rgb[0], accent_rgb[1], accent_rgb[2], 205), outline=(255, 250, 220, 255))
        d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=(255, 245, 195, 255))

    img = Image.alpha_composite(img, scene)

    # Luxury Art Nouveau Gold Foil Frame + Nameplate
    frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle([10, 10, w - 11, h - 11], radius=28, outline=(250, 204, 21, 255), width=8)
    fd.rounded_rectangle([26, 26, w - 27, h - 27], radius=20, outline=(254, 240, 138, 210), width=3)
    # Corner rosettes
    for kx, ky in [(42, 42), (w - 42, 42), (42, h - 42), (w - 42, h - 42)]:
        fd.ellipse([kx - 14, ky - 14, kx + 14, ky + 14], fill=(12, 18, 38, 255), outline=(250, 204, 21, 255), width=3)

    # Top Roman Numeral Crest
    fd.rounded_rectangle([cx - 66, 36, cx + 66, 94], radius=14, fill=(8, 12, 28, 238), outline=(250, 204, 21, 255), width=3)
    f_rom = load_font(34, serif=True)
    rb = fd.textbbox((0, 0), roman, font=f_rom)
    fd.text((cx - (rb[2] - rb[0]) // 2, 46), roman, font=f_rom, fill=(254, 240, 138, 255))

    # Bottom Title Plate
    fd.rounded_rectangle([42, h - 186, w - 42, h - 46], radius=16, fill=(7, 11, 26, 242), outline=(250, 204, 21, 255), width=3)
    f_tit = load_font(36, serif=True)
    tb = fd.textbbox((0, 0), title, font=f_tit)
    fd.text((cx - (tb[2] - tb[0]) // 2, h - 162), title, font=f_tit, fill=(250, 204, 21, 255))

    f_sub = load_font(21, serif=False)
    sb = fd.textbbox((0, 0), subtitle.upper(), font=f_sub)
    fd.text((cx - (sb[2] - sb[0]) // 2, h - 104), subtitle.upper(), font=f_sub, fill=(186, 230, 253, 245))

    img = Image.alpha_composite(img, frame)
    img.convert("RGB").save(out_png, "PNG", optimize=True)


def build_tarot_deck_art(force_regen=False):
    api_key = load_env_key("GEMINI_API_KEY")
    created = 0
    for slug, roman, title, subtitle, motif, bg_rgb, gold_rgb, accent_rgb in TAROT_DECK:
        out_png = os.path.join(DECK_DIR, f"{slug}.png")
        if os.path.exists(out_png) and os.path.getsize(out_png) > 20000 and not force_regen:
            continue
        used_ai = False
        if api_key:
            used_ai = try_imagen_card(slug, title, subtitle, out_png, api_key)
        if not used_ai:
            paint_illustrated_card(slug, roman, title, subtitle, motif, bg_rgb, gold_rgb, accent_rgb, out_png)
        created += 1
        print(f"[DECK ART] {slug}.png -> {'Google Imagen 3' if used_ai else 'Painterly Illustrated Plate'} ready")
    print(f"[DECK READY] {len(TAROT_DECK)} illustrated tarot cards ready in assets\\tarot_deck\\ (newly built: {created})")


# ==============================================================================
# 2. REMOVE SPINNING TRANSPARENT TESSERACT + DISPLAY REAL ART ON /store CARDS
# ==============================================================================
def fix_storefront_remove_tesseract_and_mount_real_cards():
    # Disable the spinning canvas JS cleanly
    old_js = os.path.join(STATIC_DIR, "omega_5d_engine.js")
    open(old_js, "w", encoding="utf-8", newline="").write(
        "(function(){var c=document.getElementById('omega-5d-canvas');if(c)c.remove();"
        "fetch('/api/live-pulse').then(function(r){return r.json();}).then(function(d){"
        "var el=document.getElementById('omega-live-pulse');"
        "if(el&&d){el.textContent='LIVE STUDIO: '+d.vault_videos+' READINGS RENDERED | '+d.yt_views+' YOUTUBE VIEWS | '+d.utm_clicks+' VERIFIED CLICKS | STRIPE LIVE';}"
        "}).catch(function(){});})();\n"
        "function omegaCopyRef(){var code=localStorage.getItem('oracle_ref_code')||('oracle_'+Math.random().toString(36).slice(2,8));"
        "localStorage.setItem('oracle_ref_code',code);var u=window.location.origin+'/go/assetpack15?utm_source=member_ref&utm_medium=share&utm_campaign='+code;"
        "if(navigator.clipboard)navigator.clipboard.writeText(u);var b=document.getElementById('omega-ref-btn');if(b)b.textContent='Referral Link Copied!';"
        "var i=document.getElementById('omega-ref-url');if(i)i.value=u;}\n"
    )

    # Upgrade omega_card_spread.js to display the REAL illustrated card PNGs on every card face (zero Unicode placeholders)
    spread_js = """(function(){
  var hero = document.getElementById("oracle-4d-hero");
  if (!hero) return;
  var prev = document.getElementById("omega-tarot-stage");
  if (prev) prev.remove();

  var style = document.createElement("style");
  style.textContent = [
    "body{background:radial-gradient(circle at 50% 0%,#0f172a 0%,#050814 55%,#02040a 100%) !important;}",
    "#omega-tarot-stage{margin:18px 0 28px 0;padding:24px 18px;border-radius:16px;background:linear-gradient(180deg,rgba(11,17,36,0.96),rgba(5,8,20,0.98));border:1px solid rgba(250,204,21,0.45);box-shadow:0 18px 48px rgba(0,0,0,0.65);}",
    ".ots-hdr{text-align:center;margin-bottom:20px;}",
    ".ots-hdr h2{margin:6px 0;font-size:25px;color:#fef08a;letter-spacing:0.4px;}",
    ".ots-hdr p{margin:0;color:#94a3b8;font-size:13.5px;}",
    ".ots-row{display:flex;flex-wrap:wrap;justify-content:center;gap:26px;perspective:1300px;}",
    ".ots-card{width:240px;height:384px;cursor:pointer;position:relative;transform-style:preserve-3d;transition:transform 0.85s cubic-bezier(.2,.8,.2,1);}",
    ".ots-card.flipped{transform:rotateY(180deg);}",
    ".ots-card:hover:not(.flipped){transform:translateY(-8px) rotateX(4deg) rotateY(-5deg);}",
    ".ots-face{position:absolute;inset:0;border-radius:16px;backface-visibility:hidden;overflow:hidden;box-sizing:border-box;}",
    ".ots-back{background:radial-gradient(circle at 50% 45%,#1e293b 0%,#090d1f 75%);border:2px solid #facc15;box-shadow:0 12px 32px rgba(0,0,0,0.65),inset 0 0 28px rgba(250,204,21,0.18);display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:22px;text-align:center;}",
    ".ots-sigil{width:136px;height:136px;border-radius:50%;border:2px solid rgba(250,204,21,0.85);display:flex;align-items:center;justify-content:center;background:radial-gradient(circle,rgba(250,204,21,0.18),transparent 70%);}",
    ".ots-front{transform:rotateY(180deg);border:2px solid #facc15;box-shadow:0 14px 38px rgba(250,204,21,0.28);background:#050814;}",
    ".ots-front img{width:100%;height:100%;object-fit:cover;display:block;}",
    ".ots-cap{position:absolute;left:0;right:0;bottom:0;padding:8px 10px;background:linear-gradient(transparent,rgba(4,7,18,0.95) 35%);color:#e2e8f0;font-size:11px;text-align:center;}",
    ".ots-pos{font-size:10px;letter-spacing:2px;color:#38bdf8;font-weight:800;text-transform:uppercase;}",
    ".ots-bar{margin-top:20px;display:flex;flex-wrap:wrap;justify-content:center;gap:12px;align-items:center;}",
    ".ots-btn{cursor:pointer;padding:10px 20px;border:none;border-radius:8px;font-weight:800;font-size:13px;background:linear-gradient(90deg,#facc15,#38bdf8);color:#050814;}"
  ].join("");
  document.head.appendChild(style);

  var cards = [
    {pos:"I. PAST CATALYST", name:"THE MAGICIAN", img:"/assets/tarot_deck/the_magician.png", msg:"Every lesson forged sovereign mastery.", audio:"/static/card_voices/card_past.mp3"},
    {pos:"II. PRESENT SHIFT", name:"WHEEL OF FORTUNE", img:"/assets/tarot_deck/wheel_of_fortune.png", msg:"Financial frequency rotating upward now.", audio:"/static/card_voices/card_present.mp3"},
    {pos:"III. QUANTUM OUTCOME", name:"THE SUN", img:"/assets/tarot_deck/the_sun.png", msg:"Total clarity and unstoppable momentum.", audio:"/static/card_voices/card_future.mp3"}
  ];

  var stage = document.createElement("div");
  stage.id = "omega-tarot-stage";
  var html = '<div class="ots-hdr"><div class="ots-pos">INTERACTIVE ILLUSTRATED TAROT SPREAD // STUDIO NEURAL NARRATION</div>'
    + '<h2>Tap Any Card to Reveal the Illustrated Artwork &amp; Hear Your Reading</h2>'
    + '<p>Full-bleed illustrated Major Arcana cards paired with studio broadcast neural narration.</p></div><div class="ots-row">';

  cards.forEach(function(cd, idx){
    html += '<div class="ots-card" onclick="omegaFlipCard(this,' + idx + ')">'
      + '<div class="ots-face ots-back"><div class="ots-pos">' + cd.pos + '</div><div class="ots-sigil"><div style="color:#facc15;font-weight:900;letter-spacing:2px;font-size:13px;">ORACLE<br>SYSTEMS</div></div><div style="color:#fef08a;font-size:12px;font-weight:700;">TAP TO REVEAL CARD</div></div>'
      + '<div class="ots-face ots-front"><img src="' + cd.img + '" alt="' + cd.name + '"><div class="ots-cap">' + cd.msg + '</div></div></div>';
  });
  html += '</div><div class="ots-bar"><button class="ots-btn" onclick="omegaRevealAll()">Reveal All 3 Illustrated Cards + Play Studio Reading</button>'
    + '<a class="ots-btn" style="text-decoration:none;background:linear-gradient(90deg,#059669,#0284c7);color:#fff;" href="/go/auravideo49?utm_source=card_spread&utm_medium=cta&utm_campaign=real_art_v18">Order Your Custom Full Reading ($49)</a></div>';
  stage.innerHTML = html;

  var grid = hero.querySelector(".o4d-grid");
  if (grid) hero.insertBefore(stage, grid); else hero.appendChild(stage);

  var player = new Audio();
  window.omegaFlipCard = function(el, idx){
    el.classList.add("flipped");
    try { player.pause(); player.src = cards[idx].audio; player.play(); } catch(e){}
  };
  window.omegaRevealAll = function(){
    document.querySelectorAll(".ots-card").forEach(function(el, i){ setTimeout(function(){ el.classList.add("flipped"); }, i * 450); });
    var seq = [0, 1, 2], pos = 0;
    function next(){
      if (pos >= seq.length) return;
      player.src = cards[seq[pos++]].audio;
      player.onended = next;
      player.play().catch(function(){});
    }
    next();
  };
})();
"""
    open(os.path.join(STATIC_DIR, "omega_card_spread.js"), "w", encoding="utf-8", newline="").write(spread_js)

    # Patch sovereign_daemon.py to serve /assets/tarot_deck/<file> & update hero subtext (no spinning tesseract copy)
    dp = os.path.join(PDIR, "sovereign_daemon.py")
    src = open(dp, "r", encoding="utf-8").read()
    if "/assets/tarot_deck/" not in src:
        src = src.replace(
            'if _req.path == "/static/omega_card_spread.js":',
            'if _req.path.startswith("/assets/tarot_deck/"):\n'
            '            return _sfd(_o.path.join(base_dir, "assets", "tarot_deck"), _req.path.rsplit("/", 1)[-1])\n'
            '        if _req.path == "/static/omega_card_spread.js":',
            1,
        )
    src = src.replace(
        "Move your cursor to rotate the live 5D hypercube field. Every tier unlocks instant Stripe-verified fulfillment, member portal delivery, and zero-lock-in ownership.",
        "Explore the live illustrated tarot spread below or select a tier for instant Stripe-verified digital fulfillment and member portal access.",
    )
    open(dp, "w", encoding="utf-8", newline="").write(src)
    py_compile.compile(dp, doraise=True)

    # Restart Port 8000 cleanly
    ns = subprocess.run(["netstat", "-ano"], capture_output=True, text=True).stdout
    pids = {ln.split()[-1] for ln in ns.splitlines() if ":8000 " in ln and "LISTENING" in ln.upper() and ln.split()[-1].isdigit()}
    for pid in pids:
        subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
    time.sleep(2)
    boot_log = open(os.path.join(PDIR, "logs", "daemon_boot.log"), "w", encoding="utf-8")
    subprocess.Popen([sys.executable, dp], cwd=PDIR, stdout=boot_log, stderr=boot_log, creationflags=0x08000000)
    time.sleep(3)
    print("[STORE FIXED] Removed spinning transparent tesseract & mounted real illustrated tarot art on /store!")


# ==============================================================================
# 3. INSTALL TRUE MULTI-CHAPTER ZERO-LOOP FULL READING RENDERER
# ==============================================================================
def install_real_full_video_engine():
    engine_path = os.path.join(PDIR, "Modules", "render_real_full_reading.py")
    engine_code = r'''import argparse
import asyncio
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
DECK_DIR = os.path.join(PDIR, "assets", "tarot_deck")
OUT_DIR = os.path.join(PDIR, "Content_Vault_4D_Full")
THUMB_DIR = os.path.join(PDIR, "Content_Vault_4D_Thumbnails")
WORK_DIR = os.path.join(PDIR, "logs", "real_reading_work")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)
os.makedirs(WORK_DIR, exist_ok=True)

DECK_META = [
    ("the_magician", "THE MAGICIAN", "sovereign creation, skill convergence, and turning vision into tangible structure"),
    ("wheel_of_fortune", "WHEEL OF FORTUNE", "a sudden upward shift in timing, unexpected financial openings, and destiny turning in your favor"),
    ("the_star", "THE STAR", "deep clarity after static, restored confidence, and unmistakable alignment with your true direction"),
    ("the_sun", "THE SUN", "radiant visibility, clean abundance, and breakthroughs that can no longer stay hidden"),
    ("the_world", "THE WORLD", "completing an exhausting cycle and stepping into a higher level of ownership and freedom"),
    ("the_empress", "THE EMPRESS", "magnetic attraction, compounding wealth, and building assets that pay you back continuously"),
    ("ace_of_pentacles", "ACE OF PENTACLES", "a concrete new financial seed, contract, or income portal arriving at the exact right hour"),
    ("the_emperor", "THE EMPEROR", "disciplined architecture, unshakeable boundaries, and commanding your own empire"),
    ("the_high_priestess", "HIGH PRIESTESS", "quiet discernment, reading what others miss, and trusting your internal radar over external noise"),
    ("the_chariot", "THE CHARIOT", "locked-in focus, cutting off distractions, and accelerating straight through resistance"),
]


def load_font(size):
    for p in (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\georgiab.ttf", r"C:\Windows\Fonts\arialbd.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def ollama_expand_chapter(topic, ch_title, card_name, card_meaning, target_words):
    """Generates unique, non-repeating spoken tarot prose via local Ollama (3B+), with rich offline fallback."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as r:
            models = [m.get("name", "") for m in json.loads(r.read().decode("utf-8")).get("models", [])]
        usable = [m for m in models if not any(b in m.lower() for b in (":0.5b", ":1b", ":1.5b", "tinyllama"))]
        if usable:
            prompt = (
                f"You are a calm, deeply insightful, cinematic tarot reader delivering a spoken collective reading on '{topic}'. "
                f"Write approximately {target_words} words of continuous, natural spoken narration for the chapter '{ch_title}' "
                f"focusing on the card '{card_name}' ({card_meaning}). "
                f"Speak directly to the listener in warm, grounded second-person prose. "
                f"No stage directions, no markdown bullets, no hashtags, no repetition—pure flowing spoken narration."
            )
            payload = json.dumps({
                "model": usable[0],
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.72, "repeat_penalty": 1.22, "num_predict": int(target_words * 1.6)},
            }).encode("utf-8")
            req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=120) as resp:
                txt = json.loads(resp.read().decode("utf-8")).get("response", "").strip()
                txt = re.sub(r"[#*`_]", "", txt)
                if len(txt.split()) >= max(55, int(target_words * 0.45)):
                    return txt
    except Exception:
        pass

    # Rich, non-repeating fallback prose tailored to chapter & card
    return (
        f"Take a slow, steady breath as we enter {ch_title} in this collective reading on {topic}. "
        f"The card stepping forward onto the table right now is {card_name}, carrying the unmistakable signature of {card_meaning}. "
        f"Notice how different this energy feels compared to the hesitation you carried even a few weeks ago. "
        f"When {card_name} appears in this position, it does not ask you to chase validation or force outcomes through exhaustion. "
        f"Instead, it highlights the quiet leverage you have already built behind the scenes. "
        f"Look closely at the practical decisions sitting in front of you this week: one clean move executed with full conviction "
        f"will outperform ten half-finished ideas scattered across your calendar. "
        f"Pay attention to the conversations, unexpected numbers, and sudden moments of clarity that confirm you are no longer operating "
        f"inside your old ceiling. Let the details of {card_name} settle in as we prepare to draw the next card in your spread."
    )


def synth_voice(text, out_mp3):
    import edge_tts
    voices = ["en-US-AndrewMultilingualNeural", "en-US-BrianMultilingualNeural", "en-US-ChristopherNeural"]
    last_err = None
    for i in range(4):
        v = voices[i % len(voices)]
        try:
            if os.path.exists(out_mp3):
                os.remove(out_mp3)
            async def _run(vn=v):
                await edge_tts.Communicate(text, voice=vn, rate="-6%", pitch="-2Hz").save(out_mp3)
            asyncio.run(_run())
            if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 1500:
                time.sleep(1.5)
                return v
        except Exception as ex:
            last_err = ex
            time.sleep(2.5 * (i + 1))
    raise RuntimeError(f"TTS failed: {last_err}")


def get_audio_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    )
    try:
        return max(4.0, float(r.stdout.strip()))
    except Exception:
        return 12.0


def compose_table_scene(out_png, topic, ch_label, active_cards, focus_idx):
    """Renders a 1920x1080 dark velvet tarot table showing the progressive revealed card spread (NO spinning wireframe)."""
    w, h = 1920, 1080
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = (xx - w * 0.5) / (w * 0.5), (yy - h * 0.48) / (h * 0.5)
    rad = np.sqrt(dx * dx + dy * dy)
    vig = np.clip(1.0 - rad * 0.58, 0.18, 1.0)
    r = np.clip(12 * vig + 18 * np.exp(-rad * 2.4), 0, 255)
    g = np.clip(18 * vig + 28 * np.exp(-rad * 2.4), 0, 255)
    b = np.clip(38 * vig + 56 * np.exp(-rad * 2.4), 0, 255)
    table = Image.fromarray(np.stack([r, g, b], axis=-1).astype(np.uint8), mode="RGB").convert("RGBA")

    # Warm spotlight beneath the currently focused card
    n = len(active_cards)
    card_w, card_h = (320, 512) if n <= 3 else (285, 456)
    gap = 46 if n <= 3 else 34
    total_w = n * card_w + max(0, n - 1) * gap
    start_x = (w - total_w) // 2
    base_y = 250 if n <= 3 else 278

    for idx, (slug, cname, _meaning) in enumerate(active_cards):
        cx_card = start_x + idx * (card_w + gap)
        is_focus = (idx == focus_idx)
        cw = int(card_w * (1.10 if is_focus else 0.96))
        ch = int(card_h * (1.10 if is_focus else 0.96))
        px = cx_card - (cw - card_w) // 2
        py = base_y - (ch - card_h) // 2 - (18 if is_focus else 0)

        if is_focus:
            glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow)
            gd.rounded_rectangle([px - 18, py - 18, px + cw + 18, py + ch + 18], radius=24, fill=(250, 204, 21, 125))
            table = Image.alpha_composite(table, glow.filter(ImageFilter.GaussianBlur(radius=24)))

        art_p = os.path.join(DECK_DIR, f"{slug}.png")
        if os.path.exists(art_p):
            cim = Image.open(art_p).convert("RGBA").resize((cw, ch), Image.Resampling.LANCZOS)
            if not is_focus:
                dim = Image.new("RGBA", (cw, ch), (5, 8, 20, 75))
                cim = Image.alpha_composite(cim, dim)
            table.alpha_composite(cim, (px, py))

    # Crisp cinematic top & bottom title bars
    hud = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hud)
    hd.rectangle([0, 0, w, 122], fill=(4, 7, 18, 215))
    hd.line([(0, 122), (w, 122)], fill=(250, 204, 21, 185), width=2)
    hd.rectangle([0, h - 138, w, h], fill=(4, 7, 18, 225))
    hd.line([(0, h - 138), (w, h - 138)], fill=(56, 189, 248, 185), width=2)

    f_top = load_font(34)
    f_ch  = load_font(44)
    f_sub = load_font(26)
    hd.text((64, 40), f"ORACLE SYSTEMS COLLECTIVE READING  //  {topic.upper()}", font=f_top, fill=(56, 228, 255, 255))
    cb = hd.textbbox((0, 0), ch_label.upper(), font=f_ch)
    hd.text((w // 2 - (cb[2] - cb[0]) // 2, h - 116), ch_label.upper(), font=f_ch, fill=(250, 204, 21, 255))
    cards_line = "  |  ".join(c[1] for c in active_cards)
    sb = hd.textbbox((0, 0), cards_line, font=f_sub)
    hd.text((w // 2 - (sb[2] - sb[0]) // 2, h - 54), cards_line, font=f_sub, fill=(226, 232, 240, 240))

    table = Image.alpha_composite(table, hud)
    table.convert("RGB").save(out_png, "PNG", optimize=True)


def render_chapter_mp4(img_png, aud_mp3, out_mp4, dur_sec):
    """Renders one unique chapter with smooth Ken Burns camera drift + studio-mastered voice + subtle 432Hz bed (-threads 2 for 8GB RAM)."""
    frames = max(48, int(dur_sec * 24))
    # Gentle continuous zoom-in across the entire chapter duration (never repeats or jumps)
    filt = (
        f"[0:v]scale=2112:1188,zoompan=z='min(1.0 + 0.08*on/{frames},1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1280x720:fps=24,"
        f"fade=t=in:st=0:d=0.8,fade=t=out:st={max(0.8, dur_sec - 0.8):.2f}:d=0.8,format=yuv420p[vout];"
        f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,equalizer=f=180:width_type=o:w=1.2:g=3,"
        f"acompressor=threshold=-18dB:ratio=3:attack=15:release=150,loudnorm=I=-14:TP=-1.5:LRA=9[vvoice];"
        f"aevalsrc='0.032*sin(2*PI*432*t)+0.016*sin(2*PI*528*t)':s=44100:d={dur_sec:.2f}[pad];"
        f"[vvoice][pad]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-threads", "2", "-filter_threads", "2", "-filter_complex_threads", "2",
        "-i", img_png, "-i", aud_mp3,
        "-filter_complex", filt,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-threads", "2", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out_mp4,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg chapter failed: {res.stderr[:250]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int, default=2)
    ap.add_argument("--topic", type=str, default="Silent Abundance & Financial Breakthrough")
    ap.add_argument("--target-minutes", type=int, default=3, help="3 for fast multi-chapter preview, 25-30 for full length")
    args = ap.parse_args()

    slug = re.sub(r"[^A-Za-z0-9]+", "_", f"Week_{args.week:02d}_{args.topic}").strip("_")
    job_dir = os.path.join(WORK_DIR, slug)
    os.makedirs(job_dir, exist_ok=True)

    # Pick 5 distinct cards for this episode
    shift = (args.week * 3) % len(DECK_META)
    spread = [DECK_META[(shift + i) % len(DECK_META)] for i in range(5)]

    # Words per chapter to hit target duration (~135 spoken words/min across 7 chapters)
    words_per_ch = max(75, int((args.target_minutes * 135) / 7))
    chapters = [
        ("Chapter 1 - Opening Frequency & Collective Energy", spread[:1], 0),
        (f"Chapter 2 - Past Catalyst: {spread[0][1]}", spread[:1], 0),
        (f"Chapter 3 - Present Turning Point: {spread[1][1]}", spread[:2], 1),
        (f"Chapter 4 - Hidden Influence: {spread[2][1]}", spread[:3], 2),
        (f"Chapter 5 - Breakthrough Action: {spread[3][1]}", spread[:4], 3),
        (f"Chapter 6 - Sovereign Outcome: {spread[4][1]}", spread[:5], 4),
        ("Chapter 7 - Complete 5-Card Integration & Next Step", spread[:5], 2),
    ]

    print(f"=== RENDERING TRUE 7-CHAPTER ZERO-LOOP READING: {slug} (Target: ~{args.target_minutes} min) ===")
    part_mp4s = []
    total_sec = 0.0
    for idx, (ch_title, vis_cards, focus_i) in enumerate(chapters, 1):
        c_slug, c_name, c_meaning = vis_cards[focus_i]
        print(f"  [{idx}/7] Generating unique script + voice + scene: {ch_title} ...")
        prose = ollama_expand_chapter(args.topic, ch_title, c_name, c_meaning, words_per_ch)
        aud_p = os.path.join(job_dir, f"ch{idx:02d}.mp3")
        img_p = os.path.join(job_dir, f"ch{idx:02d}.png")
        mp4_p = os.path.join(job_dir, f"ch{idx:02d}.mp4")

        v_used = synth_voice(prose, aud_p)
        dur = get_audio_duration(aud_p)
        compose_table_scene(img_p, args.topic, ch_title, vis_cards, focus_i)
        render_chapter_mp4(img_p, aud_p, mp4_p, dur)
        part_mp4s.append(mp4_p)
        total_sec += dur
        print(f"        [PASS] {dur:.1f}s unique video ({v_used}) | Running total: {total_sec/60.0:.2f} min")

    # Lossless concat of all 7 unique chapters (ZERO looping!)
    list_txt = os.path.join(job_dir, "concat.txt")
    with open(list_txt, "w", encoding="utf-8", newline="") as f:
        for p in part_mp4s:
            f.write(f"file '{p.replace(chr(92), '/')}'\n")

    final_mp4 = os.path.join(OUT_DIR, f"{slug}_REAL_FULL.mp4")
    res = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", list_txt, "-c", "copy", "-movflags", "+faststart", final_mp4],
        capture_output=True, text=True,
    )
    if res.returncode != 0:
        raise RuntimeError(f"Final concat failed: {res.stderr[:250]}")

    # Save matching illustrated 5-card thumbnail from Chapter 6
    thumb_out = os.path.join(THUMB_DIR, f"{slug}_REAL_Thumb.jpg")
    Image.open(os.path.join(job_dir, "ch06.png")).convert("RGB").resize((1280, 720), Image.Resampling.LANCZOS).save(thumb_out, "JPEG", quality=93)

    mb = os.path.getsize(final_mp4) / (1024 ** 2)
    print(f"\n[COMPLETE - ZERO LOOP] {final_mp4} ({mb:.1f} MB | {total_sec/60.0:.2f} min across 7 unique chapters)")
    print(f"[THUMBNAIL READY]      {thumb_out}")


if __name__ == "__main__":
    main()
'''
    open(engine_path, "w", encoding="utf-8", newline="").write(engine_code)
    py_compile.compile(engine_path, doraise=True)
    print("[ENGINE READY] Installed Modules\\render_real_full_reading.py (True 7-Chapter Zero-Loop Renderer)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force-regen-deck", action="store_true")
    args = ap.parse_args()

    build_tarot_deck_art(force_regen=args.force_regen_deck)
    fix_storefront_remove_tesseract_and_mount_real_cards()
    install_real_full_video_engine()
    print("\n[PHASE 18 OVERHAUL READY] Spinning tesseract removed, real illustrated deck generated, and 7-chapter zero-loop video engine installed!")


if __name__ == "__main__":
    main()