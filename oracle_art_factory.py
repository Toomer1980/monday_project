import os, json, math, hashlib, urllib.request, urllib.parse
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw, ImageStat

ROOT = "C:/Users/toome/Desktop/SovereignCore"
ART_DIR = ROOT + "/static/card_art"
UA = "OracleSystemsTarot3D/1.0 (mailto:Toomer1980@gmail.com)"
os.makedirs(ART_DIR, exist_ok=True)

DECK_QUERIES = {
    "the_tower": "lightning strike storm clouds night mountain",
    "the_star": "aurora borealis starry night mountain lake reflection",
    "ace_of_pentacles": "gold coins treasure sunlight",
    "the_sun": "golden sunrise sunbeams dramatic sky clouds",
    "the_magician": "galaxy nebula glowing cosmos space",
    "the_emperor": "grand cathedral golden sunlight architecture",
    "the_high_priestess": "full moon ocean reflection night sky",
    "nine_of_pentacles": "golden vineyard garden sunset estate",
    "ten_of_pentacles": "historic stone castle golden sunset",
    "wheel_of_fortune": "astronomical clock gold gears prague",
    "six_of_wands": "golden sunset mountain summit victory clouds",
    "the_world": "earth from space glowing horizon stars",
    "king_of_pentacles": "gold bullion bars glowing reflection"
}

def make_depth_map(img_path, depth_path):
    im = Image.open(img_path).convert("RGB").resize((512, 768))
    gray = ImageOps.autocontrast(im.convert("L"), cutoff=2)
    edges = gray.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(6))
    base = gray.filter(ImageFilter.GaussianBlur(10))
    W, H = im.size
    out = Image.new("L", (W, H))
    bp, ep, op = base.load(), edges.load(), out.load()
    for y in range(H):
        horiz = (y / float(H)) * 135.0
        ny = (y / float(H) - 0.54) * 1.45
        for x in range(W):
            nx = (x / float(W) - 0.5) * 1.65
            c_pop = max(0.0, 1.0 - math.sqrt(nx*nx + ny*ny) * 0.85) * 85.0
            op[x, y] = int(min(255, max(0, horiz + c_pop + bp[x,y] * 0.25 + ep[x,y] * 0.22)))
    ImageOps.autocontrast(out.filter(ImageFilter.GaussianBlur(8))).save(depth_path)

def render_painterly_fallback(out_jpg, seed_str):
    W, H = 768, 1152
    h = int(hashlib.md5(seed_str.encode()).hexdigest()[:6], 16)
    im = Image.new("RGB", (W, H), (14, 18, 44))
    dr = ImageDraw.Draw(im)
    c_top = (12 + (h % 28), 18 + ((h >> 4) % 35), 55 + ((h >> 8) % 60))
    c_mid = (160 + (h % 80), 95 + ((h >> 4) % 70), 40 + ((h >> 8) % 50))
    for y in range(H):
        k = y / float(H)
        col = tuple(int(c_top[i]*(1-k) + c_mid[i]*k) for i in range(3))
        dr.line([(0, y), (W, y)], fill=col)
    dr.ellipse([W//2-190, 210, W//2+190, 590], fill=(255, 224, 130))
    im = im.filter(ImageFilter.GaussianBlur(28))
    dr = ImageDraw.Draw(im)
    dr.polygon([(0, H), (0, 740), (240, 560), (490, 720), (W, 540), (W, H)], fill=(12, 10, 26))
    im.save(out_jpg, quality=92)

def fetch_photo(query, out_jpg):
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "generator": "search", "gsrnamespace": "6", "gsrlimit": "10",
        "gsrsearch": f"{query} filetype:bitmap", "prop": "imageinfo",
        "iiprop": "url|mime|size", "iiurlwidth": "1024", "format": "json"
    })
    try:
        req = urllib.request.Request(api, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=18) as r:
            pages = json.loads(r.read().decode("utf-8")).get("query", {}).get("pages", {})
        for pg in sorted(pages.values(), key=lambda x: x.get("index", 99)):
            ii = (pg.get("imageinfo") or [{}])[0]
            if ii.get("mime") != "image/jpeg" or ii.get("width", 0) < 500: continue
            dl = ii.get("thumburl") or ii.get("url")
            if not dl: continue
            try:
                with urllib.request.urlopen(urllib.request.Request(dl, headers={"User-Agent": UA}), timeout=18) as dr:
                    raw = dr.read()
                if len(raw) < 25000: continue
                open(out_jpg, "wb").write(raw)
                im = ImageOps.fit(Image.open(out_jpg).convert("RGB"), (768, 1152), method=Image.Resampling.LANCZOS)
                if ImageStat.Stat(im.convert("L")).stddev[0] < 18.0: continue
                ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.18)).enhance(1.16).save(out_jpg, quality=92)
                return True
            except Exception: continue
    except Exception: pass
    return False

def ensure_card_art(card_name):
    slug = "".join(c if c.isalnum() else "_" for c in card_name.lower()).strip("_")
    jpg_p, dep_p = f"{ART_DIR}/{slug}.jpg", f"{ART_DIR}/{slug}_depth.png"
    if not (os.path.exists(jpg_p) and os.path.getsize(jpg_p) > 25000):
        q = DECK_QUERIES.get(slug, f"{card_name} dramatic golden light landscape")
        ok = fetch_photo(q, jpg_p)
        if not ok: render_painterly_fallback(jpg_p, slug)
        print(f"[ART] {slug}.jpg ({os.path.getsize(jpg_p)//1024} KB) -> {'REAL PHOTO' if ok else 'SCENIC FALLBACK'}")
    if not os.path.exists(dep_p): make_depth_map(jpg_p, dep_p)
    return f"/static/card_art/{slug}.jpg", f"/static/card_art/{slug}_depth.png"

if __name__ == "__main__":
    for slug_k in DECK_QUERIES:
        ensure_card_art(slug_k.replace("_", " ").title())
