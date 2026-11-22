import argparse
import asyncio
import json
import os
import random
import re
import subprocess
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
DECK_DIR = os.path.join(PDIR, "assets", "tarot_deck")
SHORTS_DIR = os.path.join(PDIR, "Content_Vault_4D_Shorts")
WORK_DIR = os.path.join(PDIR, "logs", "cinema_shorts_work")
MANIFEST_P = os.path.join(PDIR, "data", "verified_deck_manifest.json")
os.makedirs(WORK_DIR, exist_ok=True)


def load_font(size):
    for p in (r"C:\Windows\Fonts\georgiab.ttf", r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def synth_voice(text, out_mp3):
    import edge_tts
    voices = ["en-US-AndrewMultilingualNeural", "en-US-BrianMultilingualNeural", "en-US-ChristopherNeural"]
    for i in range(4):
        try:
            if os.path.exists(out_mp3):
                os.remove(out_mp3)
            async def _r(vn=voices[i % len(voices)]):
                await edge_tts.Communicate(text, voice=vn, rate="-5%", pitch="-2Hz").save(out_mp3)
            asyncio.run(_r())
            if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 1500:
                time.sleep(1.2)
                return
        except Exception:
            time.sleep(2.0 * (i + 1))
    raise RuntimeError("TTS failed for cinema short")


def audio_dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path], capture_output=True, text=True)
    try:
        return max(3.5, float(r.stdout.strip()))
    except Exception:
        return 7.0


def build_vertical_plate(out_png, card_item, step_kicker, hook_line):
    w, h = 1080, 1920
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = (xx - w * 0.5) / (w * 0.5), (yy - h * 0.48) / (h * 0.5)
    rad = np.sqrt(dx * dx + dy * dy)
    r = np.clip(4 + 44 * np.exp(-rad * 2.1), 0, 255)
    g = np.clip(7 + 34 * np.exp(-rad * 2.1), 0, 255)
    b = np.clip(18 + 60 * np.exp(-rad * 1.8), 0, 255)
    bg = Image.fromarray(np.stack([r, g, b], axis=-1).astype(np.uint8), mode="RGB").convert("RGBA")

    rng = random.Random(step_kicker + card_item["slug"])
    emb = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ed = ImageDraw.Draw(emb)
    for _ in range(90):
        ex, ey, er = rng.randint(30, w - 30), rng.randint(120, h - 180), rng.choice([2, 3, 5, 7])
        col = (250, 204, 21, rng.randint(75, 190)) if rng.random() > 0.35 else (56, 228, 255, rng.randint(70, 180))
        ed.ellipse([ex - er, ey - er, ex + er, ey + er], fill=col)
    bg = Image.alpha_composite(bg, emb.filter(ImageFilter.GaussianBlur(radius=2.2)))

    cw, ch = 760, 1140
    px, py = (w - cw) // 2, 340
    halo = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(halo).rounded_rectangle([px - 24, py - 24, px + cw + 24, py + ch + 24], radius=36, fill=(250, 204, 21, 130))
    bg = Image.alpha_composite(bg, halo.filter(ImageFilter.GaussianBlur(radius=34)))

    art_p = os.path.join(DECK_DIR, f"{card_item['slug']}.png")
    cim = Image.open(art_p).convert("RGBA").resize((cw, ch), Image.Resampling.LANCZOS)
    bg.alpha_composite(cim, (px, py))

    hud = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hud)
    hd.rectangle([0, 0, w, 260], fill=(3, 5, 14, 215))
    hd.rectangle([0, h - 360, w, h], fill=(3, 5, 14, 232))
    hd.line([(80, 260), (w - 80, 260)], fill=(250, 204, 21, 200), width=3)
    hd.line([(80, h - 360), (w - 80, h - 360)], fill=(56, 189, 248, 200), width=3)

    f_k = load_font(36)
    kb = hd.textbbox((0, 0), step_kicker.upper(), font=f_k)
    hd.text((w // 2 - (kb[2] - kb[0]) // 2, 108), step_kicker.upper(), font=f_k, fill=(56, 228, 255, 255))

    cname = card_item["title"].split("//")[-1].strip()
    f_t = load_font(64)
    tb = hd.textbbox((0, 0), cname, font=f_t)
    hd.text((w // 2 - (tb[2] - tb[0]) // 2, 168), cname, font=f_t, fill=(250, 204, 21, 255))

    f_h = load_font(44)
    hb = hd.textbbox((0, 0), hook_line.upper()[:34], font=f_h)
    hd.text((w // 2 - (hb[2] - hb[0]) // 2, h - 295), hook_line.upper()[:34], font=f_h, fill=(254, 240, 138, 255))

    cta = "TAP LINK IN DESCRIPTION FOR LIVE 3D PORTAL"
    f_c = load_font(30)
    cb = hd.textbbox((0, 0), cta, font=f_c)
    hd.text((w // 2 - (cb[2] - cb[0]) // 2, h - 205), cta, font=f_c, fill=(226, 232, 240, 240))

    Image.alpha_composite(bg, hud).convert("RGB").save(out_png, "PNG", optimize=True)


def render_vertical_scene(img_png, aud_mp3, out_mp4, dur):
    frames = max(48, int(dur * 24))
    filt = (
        f"[0:v]scale=1188:2112,zoompan=z='min(1.0 + 0.08*on/{frames},1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=24,"
        f"fade=t=in:st=0:d=0.45,fade=t=out:st={max(0.5, dur - 0.45):.2f}:d=0.45,format=yuv420p[vout];"
        f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,equalizer=f=180:width_type=o:w=1.2:g=3,acompressor=threshold=-18dB:ratio=3:attack=15:release=150,loudnorm=I=-14:TP=-1.5:LRA=9[vvoice];"
        f"aevalsrc='0.030*sin(2*PI*432*t)+0.015*sin(2*PI*528*t)':s=44100:d={dur:.2f}[pad];"
        f"[vvoice][pad]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-threads", "2", "-filter_threads", "2", "-filter_complex_threads", "2",
        "-i", img_png, "-i", aud_mp3, "-filter_complex", filt,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-threads", "2", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out_mp4,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr[:220])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--short-file", type=str, default="Short_11_Karmic_Harvest_4D_MAX.mp4")
    args = ap.parse_args()

    deck = json.load(open(MANIFEST_P, "r", encoding="utf-8"))
    if len(deck) < 3:
        deck = (deck * 3)[:3]
    cards3 = deck[:3]
    topic = re.sub(r"^Short_\d+_", "", args.short_file.replace("_4D_MAX.mp4", "")).replace("_", " ")
    job = os.path.join(WORK_DIR, args.short_file.replace(".mp4", ""))
    os.makedirs(job, exist_ok=True)

    scenes = [
        (cards3[0], "CARD 1 // PAST CATALYST", f"SHIFT UNLOCKED: {topic}",
         f"Stop scrolling for three seconds. Card one in your {topic} spread is {cards3[0]['title'].split('//')[-1].strip()}. Everything you built quietly behind the scenes is locking into place right now."),
        (cards3[1], "CARD 2 // PRESENT SHIFT", "TIMING TURNING UPWARD",
         f"Card two steps straight out of the portal: {cards3[1]['title'].split('//')[-1].strip()}. Watch for an unexpected opening or financial pivot over the next seventy-two hours."),
        (cards3[2], "CARD 3 // SOVEREIGN OUTCOME", "CLAIM YOUR 3D READING",
         f"And card three seals the spread: {cards3[2]['title'].split('//')[-1].strip()}. Type I claim this alignment below, and tap the description link to explore the live 3D Tarot Portal."),
    ]

    parts = []
    for i, (cd, kick, hook, script) in enumerate(scenes, 1):
        img_p = os.path.join(job, f"s{i}.png")
        aud_p = os.path.join(job, f"s{i}.mp3")
        mp4_p = os.path.join(job, f"s{i}.mp4")
        build_vertical_plate(img_p, cd, kick, hook)
        synth_voice(script, aud_p)
        render_vertical_scene(img_p, aud_p, mp4_p, audio_dur(aud_p))
        parts.append(mp4_p)

    lst = os.path.join(job, "list.txt")
    with open(lst, "w", encoding="utf-8", newline="") as f:
        for p in parts:
            f.write("file '" + p.replace("\\", "/") + "'\n")
    out_mp4 = os.path.join(SHORTS_DIR, args.short_file)
    res = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", out_mp4], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr[:220])
    print(f"[PHASE 26 PASS] Rendered 3-scene ray-traced 9:16 Cinema Short -> {out_mp4} ({os.path.getsize(out_mp4)/(1024**2):.1f} MB)")


if __name__ == "__main__":
    main()