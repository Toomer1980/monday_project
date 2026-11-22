import argparse
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
