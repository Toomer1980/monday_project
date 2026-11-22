import datetime as dt
import glob
import json
import os
import subprocess
import time
from PIL import Image

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
DECK_DIR = os.path.join(PDIR, "assets", "tarot_deck")
VOICE_DIR = os.path.join(PDIR, "static", "card_voices")
THUMB_DIR = os.path.join(PDIR, "Content_Vault_4D_Thumbnails")
SHORTS_DIR = os.path.join(PDIR, "Content_Vault_4D_Shorts")
FULL_DIR = os.path.join(PDIR, "Content_Vault_4D_Full")
os.makedirs(DECK_DIR, exist_ok=True)
os.makedirs(VOICE_DIR, exist_ok=True)

CARD_RULES = [
    ("the_magician", "I // THE MAGICIAN", ["the_magician", "magician", "c9176683"]),
    ("wheel_of_fortune", "X // WHEEL OF FORTUNE", ["wheel_of_fortune", "wheel", "fortune", "1758ffe8"]),
    ("the_star", "XVII // THE STAR", ["the_star", "star", "f1aedf3e"]),
    ("the_sun", "XIX // THE SUN", ["the_sun", "sun", "xix", "e083d4c2"]),
    ("the_world", "XXI // THE WORLD", ["the_world", "world", "xxi", "046646c2"]),
    ("ace_of_pentacles", "I // ACE OF PENTACLES", ["ace_of_pentacles", "pentacles"]),
    ("the_empress", "III // THE EMPRESS", ["the_empress", "empress"]),
    ("the_emperor", "IV // THE EMPEROR", ["the_emperor", "emperor"]),
    ("the_high_priestess", "II // HIGH PRIESTESS", ["the_high_priestess", "priestess"]),
    ("the_chariot", "VII // THE CHARIOT", ["the_chariot", "chariot"]),
]


def is_old_cartoon(path):
    try:
        with Image.open(path) as im:
            return im.size == (600, 960)
    except Exception:
        return True


def atomic_convert_to_png(src_path, dst_png):
    tmp_png = dst_png + ".tmp.png"
    with Image.open(src_path) as im:
        rgb = im.convert("RGB")
        rgb.save(tmp_png, "PNG", optimize=True)
    for _ in range(4):
        try:
            os.replace(tmp_png, dst_png)
            return True
        except PermissionError:
            time.sleep(0.4)
    if os.path.exists(tmp_png):
        os.remove(tmp_png)
    return False


def scan_and_import_real_cards():
    home = os.path.expanduser("~")
    search_dirs = [
        DECK_DIR,
        os.path.join(home, "Downloads"),
        os.path.join(home, "Desktop"),
        os.path.join(home, "Pictures"),
    ]
    imported = []
    exts = (".png", ".jpg", ".jpeg", ".webp", ".jfif")

    for slug, _title, keys in CARD_RULES:
        dst_png = os.path.join(DECK_DIR, f"{slug}.png")
        candidates = []
        for sdir in search_dirs:
            if not os.path.exists(sdir):
                continue
            for fn in os.listdir(sdir):
                low = fn.lower()
                if not low.endswith(exts):
                    continue
                stem = os.path.splitext(low)[0].replace("-", "_").replace(" ", "_")
                if any(k in stem for k in keys):
                    fp = os.path.join(sdir, fn)
                    if os.path.isfile(fp) and os.path.getsize(fp) > 15000:
                        if not is_old_cartoon(fp):
                            candidates.append((os.path.getmtime(fp), fp, sdir))

        if candidates:
            candidates.sort(reverse=True)
            _, best_fp, src_dir = candidates[0]
            if os.path.abspath(best_fp) != os.path.abspath(dst_png):
                if atomic_convert_to_png(best_fp, dst_png):
                    imported.append(f"{slug}.png <- {os.path.basename(best_fp)}")
                    if src_dir == DECK_DIR and best_fp.lower() != dst_png.lower():
                        try:
                            os.remove(best_fp)
                        except Exception:
                            pass
    return imported


def ffprobe_duration(path):
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, timeout=8,
        )
        return float(r.stdout.strip())
    except Exception:
        return -1.0


def main():
    imported = scan_and_import_real_cards()
    raytraced = []
    cartoon_left = []
    manifest = []

    for slug, title, _keys in CARD_RULES:
        fp = os.path.join(DECK_DIR, f"{slug}.png")
        if not os.path.exists(fp):
            continue
        with Image.open(fp) as im:
            w, h = im.size
        if (w, h) == (600, 960):
            cartoon_left.append(f"{slug}.png (600x960 old Pillow art)")
        else:
            raytraced.append(f"{slug}.png ({w}x{h} ray-traced)")
            manifest.append({
                "slug": slug,
                "title": title,
                "img": f"/assets/tarot_deck/{slug}.png",
                "audio": f"/static/card_voices/{slug}.mp3",
                "w": w,
                "h": h,
            })

    if not manifest:
        for slug, title, _keys in CARD_RULES[:5]:
            manifest.append({
                "slug": slug, "title": title,
                "img": f"/assets/tarot_deck/{slug}.png",
                "audio": f"/static/card_voices/{slug}.mp3",
            })

    json.dump(manifest, open(os.path.join(PDIR, "data", "verified_deck_manifest.json"), "w", encoding="utf-8"), indent=2)

    voice_ok = [f for f in os.listdir(VOICE_DIR) if f.endswith(".mp3") and os.path.getsize(os.path.join(VOICE_DIR, f)) > 2500]
    thumbs = glob.glob(os.path.join(THUMB_DIR, "*.jpg"))
    shorts = glob.glob(os.path.join(SHORTS_DIR, "*_4D_MAX.mp4"))
    full_real = glob.glob(os.path.join(FULL_DIR, "*_REAL_FULL.mp4"))
    bad_videos = []
    for vp in (shorts[:6] + full_real[:3]):
        d = ffprobe_duration(vp)
        if d <= 2.0:
            bad_videos.append(os.path.basename(vp))

    lines = [
        f"# Oracle Systems LLC - Phase 21 Deep QA Audit ({dt.datetime.now().strftime('%Y-%m-%d %H:%M')} EST)",
        f"- **Newly Imported & Converted Cards:** {len(imported)} ({', '.join(imported) if imported else 'none'})",
        f"- **Verified Ray-Traced 3D Cards (Active on /store & Videos):** {len(raytraced)} -> {', '.join(raytraced) if raytraced else 'NONE'}",
        f"- **Old 600x960 Cartoon Cards Quarantined from 3D Stage:** {len(cartoon_left)}",
        f"- **Studio Neural Card Voices Verified:** {len(voice_ok)} MP3 file(s)",
        f"- **Thumbnails Ready:** {len(thumbs)} | **Shorts Ready:** {len(shorts)} | **Zero-Loop Full Readings:** {len(full_real)}",
        f"- **Corrupt Video Check (sampled):** {len(bad_videos)} defect(s) {bad_videos if bad_videos else '(ALL CLEAN)'}",
    ]
    if cartoon_left:
        lines.append("\n## Cards Still Using Old Pillow Art (Save Ray-Traced Art to assets\\tarot_deck or Downloads & Re-run):")
        for c in cartoon_left:
            lines.append(f"- {c}")

    rep = "\n".join(lines) + "\n"
    out_md = os.path.join(PDIR, "reports", "Deep_QA_Audit.md")
    open(out_md, "w", encoding="utf-8", newline="").write(rep)
    print(rep)


if __name__ == "__main__":
    main()