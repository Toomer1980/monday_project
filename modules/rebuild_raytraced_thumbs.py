import glob
import json
import os
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
DECK_DIR = os.path.join(PDIR, "assets", "tarot_deck")
THUMB_DIR = os.path.join(PDIR, "Content_Vault_4D_Thumbnails")
MANIFEST_P = os.path.join(PDIR, "data", "verified_deck_manifest.json")
os.makedirs(THUMB_DIR, exist_ok=True)


def load_font(size):
    for p in (r"C:\Windows\Fonts\georgiab.ttf", r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def tilt_3d(img_rgba, tilt_dir):
    if tilt_dir == 0:
        return img_rgba
    w, h = img_rgba.size
    dy = int(h * 0.06)
    dst = [(0, dy), (w, 0), (w, h), (0, h - dy)] if tilt_dir < 0 else [(0, 0), (w, dy), (w, h - dy), (0, h)]
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    mat = []
    for (x, y), (u, v) in zip(dst, src):
        mat.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        mat.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    coeffs = np.linalg.solve(np.array(mat, dtype=np.float64), np.array([c for pt in src for c in pt], dtype=np.float64))
    return img_rgba.transform((w, h), Image.Transform.PERSPECTIVE, coeffs.tolist(), Image.Resampling.BICUBIC)


def render_thumb(out_jpg, headline, deck_items, seed_idx):
    w, h = 1280, 720
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = (xx - w * 0.5) / (w * 0.5), (yy - h * 0.42) / (h * 0.5)
    rad = np.sqrt(dx * dx + dy * dy)
    r = np.clip(5 + 38 * np.exp(-rad * 2.0), 0, 255)
    g = np.clip(8 + 30 * np.exp(-rad * 2.0), 0, 255)
    b = np.clip(18 + 56 * np.exp(-rad * 1.7), 0, 255)
    bg = Image.fromarray(np.stack([r, g, b], axis=-1).astype(np.uint8), mode="RGB").convert("RGBA")

    c_l = deck_items[(seed_idx + 0) % len(deck_items)]
    c_m = deck_items[(seed_idx + 1) % len(deck_items)]
    c_r = deck_items[(seed_idx + 2) % len(deck_items)]

    def load_c(item, cw, ch, tilt):
        fp = os.path.join(DECK_DIR, f"{item['slug']}.png")
        im = Image.open(fp).convert("RGBA").resize((cw, ch), Image.Resampling.LANCZOS)
        return tilt_3d(im, tilt)

    im_l = load_c(c_l, 275, 420, -1)
    im_r = load_c(c_r, 275, 420, 1)
    im_m = load_c(c_m, 315, 480, 0)

    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([w // 2 - 175, 62, w // 2 + 175, 560], radius=24, fill=(250, 204, 21, 115))
    bg = Image.alpha_composite(bg, glow.filter(ImageFilter.GaussianBlur(radius=26)))

    bg.alpha_composite(im_l, (195, 108))
    bg.alpha_composite(im_r, (w - 195 - im_r.width, 108))
    bg.alpha_composite(im_m, (w // 2 - im_m.width // 2, 74))

    bar = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar)
    bd.rectangle([0, 568, w, h], fill=(3, 5, 14, 232))
    bd.line([(0, 568), (w, 568)], fill=(250, 204, 21, 230), width=3)
    bg = Image.alpha_composite(bg, bar)

    d = ImageDraw.Draw(bg)
    clean_h = re.sub(r"[^A-Za-z0-9 &\-!]", "", headline).upper()[:30]
    f_big = load_font(54)
    hb = d.textbbox((0, 0), clean_h, font=f_big)
    d.text((w // 2 - (hb[2] - hb[0]) // 2, 584), clean_h, font=f_big, fill=(250, 204, 21, 255))

    sub = "  +  ".join([c_l["title"].split("//")[-1].strip(), c_m["title"].split("//")[-1].strip(), c_r["title"].split("//")[-1].strip()])
    f_sub = load_font(22)
    sb = d.textbbox((0, 0), sub, font=f_sub)
    d.text((w // 2 - (sb[2] - sb[0]) // 2, 658), sub, font=f_sub, fill=(186, 230, 253, 245))
    bg.convert("RGB").save(out_jpg, "JPEG", quality=93, optimize=True)


def main():
    deck = json.load(open(MANIFEST_P, "r", encoding="utf-8")) if os.path.exists(MANIFEST_P) else []
    if not deck:
        print("[PHASE 24 WARN] No verified cards in manifest; skipping thumbnail rebuild.")
        return
    thumbs = sorted(glob.glob(os.path.join(THUMB_DIR, "*_3D_Thumb.jpg")))
    for idx, tp in enumerate(thumbs):
        base = os.path.basename(tp).replace("_3D_Thumb.jpg", "")
        headline = re.sub(r"^(Short|Week)_\d+_", "", base).replace("_", " ")
        render_thumb(tp, headline, deck, idx)
    print(f"[PHASE 24 PASS] Rebuilt ALL {len(thumbs)} thumbnails using your {len(deck)} verified ray-traced 3D cards!")


if __name__ == "__main__":
    main()