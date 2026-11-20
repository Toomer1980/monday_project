import os, json, math, hashlib, urllib.request, urllib.parse
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageStat

ROOT = "C:/Users/toome/Desktop/SovereignCore"
ART_DIR = ROOT + "/static/card_art"
UA = "OracleSystemsTarot3D/1.0 (mailto:Toomer1980@gmail.com)"
os.makedirs(ART_DIR, exist_ok=True)

QUERIES = {
    "the_tower": "lightning strike castle tower storm night",
    "the_star": "aurora borealis starry night mountain lake reflection",
    "ace_of_pentacles": "gold coins sunlight treasure beam",
    "the_magician": "crystal ball glowing light dark mystical",
    "the_emperor": "golden throne medieval palace hall sunlight",
    "the_high_priestess": "full moon reflection dark ocean night sky",
    "wheel_of_fortune": "ancient astronomical clock gold gears",
    "the_sun": "golden sunrise sunbeams mountain clouds",
    "nine_of_pentacles": "luxury vineyard garden golden hour estate",
    "ten_of_pentacles": "grand stone castle archway golden sunset"
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
        # Perspective horizon gradient: bottom foreground closer, top sky deeper
        horiz = (y / float(H)) * 135.0
        ny = (y / float(H) - 0.54) * 1.45
        for x in range(W):
            nx = (x / float(W) - 0.5) * 1.65
            center_pop = max(0.0, 1.0 - math.sqrt(nx*nx + ny*ny) * 0.85) * 85.0
            val = int(min(255, max(0, horiz + center_pop + bp[x,y] * 0.25 + ep[x,y] * 0.22)))
            op[x, y] = val
    ImageOps.autocontrast(out.filter(ImageFilter.GaussianBlur(8))).save(depth_path)
    return depth_path

def fetch_wikimedia_real_photo(query, out_jpg, used_hashes):
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "generator": "search", "gsrnamespace": "6", "gsrlimit": "12",
        "gsrsearch": f"{query} filetype:bitmap", "prop": "imageinfo",
        "iiprop": "url|mime|size", "iiurlwidth": "1024", "format": "json"
    })
    req = urllib.request.Request(api, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        pages = json.loads(r.read().decode("utf-8")).get("query", {}).get("pages", {})
    for pg in sorted(pages.values(), key=lambda x: x.get("index", 99)):
        ii = (pg.get("imageinfo") or [{}])[0]
        if ii.get("mime") != "image/jpeg" or ii.get("width", 0) < 600: continue
        dl_url = ii.get("thumburl") or ii.get("url")
        if not dl_url: continue
        try:
            dreq = urllib.request.Request(dl_url, headers={"User-Agent": UA})
            with urllib.request.urlopen(dreq, timeout=20) as dr:
                raw = dr.read()
            h = hashlib.sha256(raw).hexdigest()
            if len(raw) < 25000 or h in used_hashes: continue
            open(out_jpg, "wb").write(raw)
            im = ImageOps.fit(Image.open(out_jpg).convert("RGB"), (768, 1152), method=Image.Resampling.LANCZOS)
            if ImageStat.Stat(im.convert("L")).stddev[0] < 18.0: continue
            ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.18)).enhance(1.15).save(out_jpg, quality=93)
            used_hashes.add(h)
            return True, pg.get("title", "")
        except Exception: continue
    return False, ""

def ensure_card_art(card_name):
    slug = "".join(c if c.isalnum() else "_" for c in card_name.lower()).strip("_")
    jpg_p, dep_p = f"{ART_DIR}/{slug}.jpg", f"{ART_DIR}/{slug}_depth.png"
    used = set()
    if not (os.path.exists(jpg_p) and os.path.getsize(jpg_p) > 30000):
        q = QUERIES.get(slug, f"{card_name} dramatic cinematic landscape night")
        ok, src_title = fetch_wikimedia_real_photo(q, jpg_p, used)
        if not ok:
            ok, src_title = fetch_wikimedia_real_photo("dramatic storm starry night golden light", jpg_p, used)
        print(f"[ART] {slug}.jpg -> {'VERIFIED REAL PHOTO: ' + src_title if ok else 'FAILED'}")
    if os.path.exists(jpg_p) and not os.path.exists(dep_p):
        make_depth_map(jpg_p, dep_p)
    return f"/static/card_art/{slug}.jpg", f"/static/card_art/{slug}_depth.png"

if __name__ == "__main__":
    for c in ["The Tower", "The Star", "Ace of Pentacles", "The Magician", "The Emperor", "The High Priestess"]:
        ensure_card_art(c)
