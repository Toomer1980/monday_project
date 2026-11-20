import os, math, hashlib, urllib.request, urllib.parse
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw

ROOT = "C:/Users/toome/Desktop/SovereignCore"
ART_DIR = ROOT + "/static/card_art"
os.makedirs(ART_DIR, exist_ok=True)

PROMPTS = {
    "the_tower": "photorealistic dark medieval obsidian stone tower on jagged cliff struck by dramatic golden lightning bolt, glowing storm clouds, flying embers, volumetric cinematic lighting, 8k unreal engine 5 hyperdetailed",
    "the_star": "photorealistic glowing radiant celestial star over tranquil midnight crystal mountain lake, shimmering blue and gold aurora borealis sky, ethereal mist, cinematic 8k hyperdetailed photography",
    "ace_of_pentacles": "photorealistic giant ornate solid gold pentacle coin floating above lush emerald garden archway, golden sunbeams god rays pouring through mist, floating gold dust, 8k cinematic unreal engine 5",
    "the_magician": "photorealistic futuristic obsidian altar with floating glowing gold infinity halo, crystal chalice, flame wand, dramatic volumetric studio light, 8k cinematic hyperdetailed",
    "the_emperor": "photorealistic majestic golden marble throne in misty mountain citadel at sunset, warm cinematic god rays, royal crimson and gold accents, 8k hyperdetailed",
    "the_high_priestess": "photorealistic luminous silver crescent moon between dark marble temple pillars over still reflective water, blue ethereal mist, 8k cinematic photography"
}

CLASSIC_URLS = {
    "the_tower": "https://upload.wikimedia.org/wikipedia/commons/5/53/RWS_Tarot_16_Tower.jpg",
    "the_star": "https://upload.wikimedia.org/wikipedia/commons/d/db/RWS_Tarot_17_Star.jpg",
    "ace_of_pentacles": "https://upload.wikimedia.org/wikipedia/commons/f/fd/Pents01.jpg",
    "the_magician": "https://upload.wikimedia.org/wikipedia/commons/d/de/RWS_Tarot_01_Magician.jpg",
    "the_emperor": "https://upload.wikimedia.org/wikipedia/commons/c/c3/RWS_Tarot_04_Emperor.jpg",
    "the_high_priestess": "https://upload.wikimedia.org/wikipedia/commons/8/88/RWS_Tarot_02_High_Priestess.jpg"
}

def make_depth_map(img_path, depth_path):
    im = Image.open(img_path).convert("RGB").resize((512, 768))
    gray = ImageOps.autocontrast(im.convert("L"), cutoff=3)
    edges = gray.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(8))
    base = gray.filter(ImageFilter.GaussianBlur(14))
    W, H = im.size
    out = Image.new("L", (W, H))
    bp, ep, op = base.load(), edges.load(), out.load()
    for y in range(H):
        ny = (y / float(H) - 0.56) * 1.45
        for x in range(W):
            nx = (x / float(W) - 0.5) * 1.65
            rad = max(0.0, 1.0 - math.sqrt(nx*nx + ny*ny) * 0.78)
            val = int(min(255, max(0, bp[x,y] * 0.42 + ep[x,y] * 0.28 + rad * 155.0)))
            op[x, y] = val
    out = out.filter(ImageFilter.GaussianBlur(10))
    ImageOps.autocontrast(out).save(depth_path)
    return depth_path

def ensure_card_art(card_name):
    slug = "".join(c if c.isalnum() else "_" for c in card_name.lower()).strip("_")
    jpg_p = f"{ART_DIR}/{slug}.jpg"
    dep_p = f"{ART_DIR}/{slug}_depth.png"
    if not (os.path.exists(jpg_p) and os.path.getsize(jpg_p) > 25000):
        prompt = PROMPTS.get(slug, f"photorealistic cinematic tarot artwork of {card_name}, dramatic volumetric lighting, glowing gold accents, misty deep atmosphere, 8k hyperdetailed unreal engine 5")
        seed = int(hashlib.md5(slug.encode()).hexdigest()[:6], 16)
        urls = [f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=768&height=1152&model=flux&nologo=true&seed={seed}"]
        if slug in CLASSIC_URLS: urls.append(CLASSIC_URLS[slug])
        fetched = False
        for u in urls:
            try:
                req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                with urllib.request.urlopen(req, timeout=25) as r:
                    data = r.read()
                    if len(data) > 15000:
                        open(jpg_p, "wb").write(data)
                        im = Image.open(jpg_p).convert("RGB").resize((768, 1152))
                        ImageEnhance.Contrast(im).enhance(1.15).save(jpg_p, quality=92)
                        fetched = True; print(f"[ART] Downloaded photorealistic window plate: {slug}.jpg")
                        break
            except Exception as e:
                print(f"[ART] Source fallback for {slug}: {e}")
        if not fetched:
            im = Image.new("RGB", (768, 1152), (12, 14, 34))
            ImageDraw.Draw(im).ellipse([180, 320, 588, 728], fill=(220, 170, 60))
            im.filter(ImageFilter.GaussianBlur(45)).save(jpg_p, quality=92)
    if not os.path.exists(dep_p):
        make_depth_map(jpg_p, dep_p)
    return f"/static/card_art/{slug}.jpg", f"/static/card_art/{slug}_depth.png"

if __name__ == "__main__":
    for c in ["The Tower", "The Star", "Ace of Pentacles"]:
        ensure_card_art(c)
    print("[+] Photorealistic card plates & 3D depth maps ready.")
