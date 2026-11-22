import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import glob
import json
import math
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
DECK_DIR = os.path.join(PDIR, "assets", "tarot_deck")
THUMB_DIR = os.path.join(PDIR, "Content_Vault_4D_Thumbnails")
MANIFEST_P = os.path.join(PDIR, "data", "verified_deck_manifest.json")
os.makedirs(THUMB_DIR, exist_ok=True)

VERTS4 = np.array([[x, y, z, w] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1) for w in (-1, 1)], dtype=np.float32)
EDGES4 = [(i, j) for i in range(16) for j in range(i + 1, 16) if np.sum(np.abs(VERTS4[i] - VERTS4[j]) > 0.1) == 1]


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


def draw_4d5d_geometry(canvas_rgba, phase_ang):
    W, H = canvas_rgba.size
    cx, cy = W // 2, int(H * 0.44)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)

    # 5D Mobius glowing multi-strand ribbon
    u_grid = np.linspace(0, math.tau, 110, endpoint=True)
    for vv, col, lw in ((-0.34, (56, 228, 255, 130), 5), (0.0, (250, 204, 21, 145), 6), (0.34, (168, 85, 247, 125), 5)):
        pts = []
        for u in u_grid:
            uu = u + phase_ang
            rm = 1.95 + vv * math.cos(uu * 0.5)
            xm, ym, zm = rm * math.cos(uu), rm * math.sin(uu), vv * math.sin(uu * 0.5)
            yt = ym * 0.52 - zm * 0.85
            zt = ym * 0.85 + zm * 0.52
            sc = (W * 0.25) / (3.8 - zt * 0.42)
            pts.append((cx + xm * sc, cy + yt * sc))
        d.line(pts, fill=col, width=lw)

    # True 4D Tesseract (16 vertices, 32 edges)
    c1, s1 = math.cos(phase_ang * 1.1), math.sin(phase_ang * 1.1)
    c2, s2 = math.cos(phase_ang * 0.7), math.sin(phase_ang * 0.7)
    x = VERTS4[:, 0] * c1 - VERTS4[:, 3] * s1
    w4 = VERTS4[:, 0] * s1 + VERTS4[:, 3] * c1
    y = VERTS4[:, 1] * c2 - VERTS4[:, 2] * s2
    z = VERTS4[:, 1] * s2 + VERTS4[:, 2] * c2
    p4 = 2.8 / (3.3 - w4 * 0.75)
    x3, y3, z3 = x * p4, y * p4, z * p4
    sc3 = (W * 0.21) / (4.1 - z3 * 0.55)
    pts2 = [(cx + x3[k] * sc3[k], cy + y3[k] * sc3[k], w4[k]) for k in range(16)]
    for i, j in EDGES4:
        is_g = (pts2[i][2] + pts2[j][2]) > 0
        col = (250, 204, 21, 175) if is_g else (56, 228, 255, 165)
        d.line([(pts2[i][0], pts2[i][1]), (pts2[j][0], pts2[j][1])], fill=col, width=5)
    for px, py, _w in pts2:
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=(254, 240, 138, 225))

    glow = lay.filter(ImageFilter.GaussianBlur(radius=10))
    out = Image.alpha_composite(canvas_rgba, glow)
    return Image.alpha_composite(out, lay)


def render_qhd_thumb(out_jpg, headline, deck_items, seed_idx):
    # 2560x1440 Ultra-Crisp 2K QHD 16:9 YouTube Master Thumbnail
    W, H = 2560, 1440
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = (xx - W * 0.5) / (W * 0.5), (yy - H * 0.44) / (H * 0.5)
    rad = np.sqrt(dx * dx + dy * dy)
    bg = Image.fromarray(np.stack([
        np.clip(5 + 48 * np.exp(-rad * 2.0), 0, 255),
        np.clip(8 + 38 * np.exp(-rad * 2.0), 0, 255),
        np.clip(22 + 78 * np.exp(-rad * 1.65), 0, 255),
    ], axis=-1).astype(np.uint8), mode="RGB").convert("RGBA")

    bg = draw_4d5d_geometry(bg, 0.55 + seed_idx * 0.37)

    c_l = deck_items[(seed_idx + 0) % len(deck_items)]
    c_m = deck_items[(seed_idx + 1) % len(deck_items)]
    c_r = deck_items[(seed_idx + 2) % len(deck_items)]

    def load_c(item, cw, ch, tilt):
        fp = os.path.join(DECK_DIR, f"{item['slug']}.png")
        im = Image.open(fp).convert("RGBA").resize((cw, ch), Image.Resampling.LANCZOS)
        ImageDraw.Draw(im).rounded_rectangle([3, 3, cw - 4, ch - 4], radius=24, outline=(250, 204, 21, 230), width=5)
        return tilt_3d(im, tilt)

    im_l = load_c(c_l, 550, 840, -1)
    im_r = load_c(c_r, 550, 840, 1)
    im_m = load_c(c_m, 640, 970, 0)

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([W // 2 - 360, 110, W // 2 + 360, 1120], radius=48, fill=(250, 204, 21, 130))
    bg = Image.alpha_composite(bg, glow.filter(ImageFilter.GaussianBlur(radius=46)))

    bg.alpha_composite(im_l, (350, 200))
    bg.alpha_composite(im_r, (W - 350 - im_r.width, 200))
    bg.alpha_composite(im_m, (W // 2 - im_m.width // 2, 130))

    bar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar)
    bd.rectangle([0, 1125, W, H], fill=(3, 5, 16, 238))
    bd.line([(0, 1125), (W, 1125)], fill=(250, 204, 21, 240), width=6)
    bg = Image.alpha_composite(bg, bar)

    d = ImageDraw.Draw(bg)
    clean_h = re.sub(r"[^A-Za-z0-9 &\-!]", "", headline).upper()[:28]
    f_big = load_font(112)
    hb = d.textbbox((0, 0), clean_h, font=f_big)
    d.text((W // 2 - (hb[2] - hb[0]) // 2, 1152), clean_h, font=f_big, fill=(250, 204, 21, 255))

    sub = "4D TESSERACT  //  5D MOBIUS  //  " + "  +  ".join([
        c_l["title"].split("//")[-1].strip(),
        c_m["title"].split("//")[-1].strip(),
        c_r["title"].split("//")[-1].strip(),
    ])
    f_sub = load_font(42)
    sb = d.textbbox((0, 0), sub, font=f_sub)
    d.text((W // 2 - (sb[2] - sb[0]) // 2, 1315), sub, font=f_sub, fill=(186, 230, 253, 250))

    bg.convert("RGB").save(out_jpg, "JPEG", quality=95, optimize=True)


def main():
    deck = json.load(open(MANIFEST_P, "r", encoding="utf-8")) if os.path.exists(MANIFEST_P) else []
    if not deck:
        print("[THUMBS WARN] No verified cards in manifest.")
        return
    thumbs = sorted(glob.glob(os.path.join(THUMB_DIR, "*.jpg")))
    for idx, tp in enumerate(thumbs):
        base = os.path.basename(tp).replace("_3D_Thumb.jpg", "").replace("_REAL_Thumb.jpg", "").replace(".jpg", "")
        headline = re.sub(r"^(Short|Week)_\d+_", "", base).replace("_", " ")
        render_qhd_thumb(tp, headline, deck, idx)
    print(f"[ULTRA 2K QHD THUMBS PASS] Upgraded ALL {len(thumbs)} thumbnails to 2560x1440 with 4D Tesseract + 5D Mobius + {len(deck)}/10 Ray-Traced Cards!")


if __name__ == "__main__":
    main()
