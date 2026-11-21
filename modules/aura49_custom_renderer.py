import base64
import datetime as dt
import json
import math
import os
import re
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def load_font(size):
    for p in (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\calibrib.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def detect_encoder():
    try:
        res = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True, timeout=8)
        if "h264_nvenc" in res.stdout:
            t = subprocess.run(
                ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=128x128:d=0.1", "-c:v", "h264_nvenc", "-f", "null", "-"],
                capture_output=True, timeout=8,
            )
            if t.returncode == 0:
                return "h264_nvenc"
    except Exception:
        pass
    return "libx264"


def render_custom_cover(out_jpg, customer_name, focus_topic, order_id):
    w, h = 1280, 720
    xs = np.linspace(-2.2, 2.2, w // 4, dtype=np.float32)
    ys = np.linspace(-1.4, 1.4, h // 4, dtype=np.float32)
    X, Y = np.meshgrid(xs, ys)
    R = np.sqrt(X * X + Y * Y) + 1e-5
    ang = np.arctan2(Y, X)
    fluid = (np.sin(X * 2.5 + 0.8) + np.cos(Y * 2.7 - 0.6) + np.sin(R * 4.8 + np.sin(ang * 3.0))) / 3.0
    vortex = np.exp(-R * 1.1) * (0.55 + 0.45 * np.sin(R * 7.5 + ang * 2.0))
    rc = np.clip(14 + 45 * (fluid * 0.5 + 0.5) + 145 * vortex, 0, 255)
    gc = np.clip(22 + 90 * (fluid * 0.5 + 0.5) + 150 * vortex, 0, 255)
    bc = np.clip(44 + 155 * (fluid * 0.5 + 0.5) + 125 * vortex, 0, 255)
    bg = np.stack([rc, gc, bc], axis=-1).astype(np.uint8)
    img = Image.fromarray(bg, mode="RGB").resize((w, h), Image.Resampling.BILINEAR).convert("RGBA")

    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy, sc = w * 0.5, h * 0.44, 240.0
    for i in range(4):
        rad = sc * (0.58 + i * 0.14)
        gd.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=(56, 228, 255, 130 - i * 22) if i % 2 == 0 else (250, 204, 21, 130 - i * 22), width=4)

    verts = [[x, y, z, wv] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1) for wv in (-1, 1)]
    pts = []
    for x, y, z, wv in verts:
        x1, w1 = x * math.cos(0.7) - wv * math.sin(0.7), x * math.sin(0.7) + wv * math.cos(0.7)
        y1, z1 = y * math.cos(0.5) - z * math.sin(0.5), y * math.sin(0.5) + z * math.cos(0.5)
        wp = 2.4 / (3.4 - w1)
        zp = 2.5 / (4.2 - z1 * wp)
        pts.append((cx + x1 * wp * sc * 0.6 * zp, cy + y1 * wp * sc * 0.6 * zp))
    for i in range(16):
        for j in range(i + 1, 16):
            if sum(abs(verts[i][k] - verts[j][k]) > 0.1 for k in range(4)) == 1:
                gd.line([pts[i], pts[j]], fill=(250, 204, 21, 215) if (i + j) % 2 == 0 else (56, 228, 255, 200), width=4)

    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(radius=3)))
    bar = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar)
    bd.rectangle([0, 0, w, 96], fill=(5, 9, 22, 185))
    bd.rectangle([0, 505, w, h], fill=(5, 9, 22, 225))
    bd.line([(0, 505), (w, 505)], fill=(56, 228, 255, 235), width=3)
    img = Image.alpha_composite(img, bar)
    d = ImageDraw.Draw(img)

    f_top = load_font(30)
    f_big = load_font(56)
    f_sub = load_font(28)
    d.text((48, 30), "PRIVATE 4D TESSERACT & MOBIUS AURA READING // ORACLE SYSTEMS LLC", font=f_top, fill=(56, 228, 255, 255))
    cname = customer_name.upper()[:28]
    for off in range(5, 0, -1):
        d.text((48 + off, 528 + off), f"PREPARED FOR: {cname}", font=f_big, fill=(8, 18, 38, 230))
    d.text((48, 528), f"PREPARED FOR: {cname}", font=f_big, fill=(250, 204, 21, 255))
    d.text((48, 608), f"FOCUS: {focus_topic.upper()[:42]}   |   ORDER: {order_id}", font=f_sub, fill=(226, 232, 240, 255))
    d.text((48, 656), f"VERIFIED DIGITAL FULFILLMENT  //  {dt.date.today().isoformat()}", font=load_font(22), fill=(56, 228, 255, 220))
    img.convert("RGB").save(out_jpg, "JPEG", quality=93, optimize=True)


def clean_drawtext(s):
    return re.sub(r"[^A-Za-z0-9 \-\|\.]", "", s or "").strip()


def render_custom_aura_mp4(pdir, customer_name, focus_topic, order_id, duration_sec, customer_email):
    out_dir = os.path.join(pdir, "deliverables", "aura49_fulfilled")
    pub_deliv = os.path.join(pdir, "deliverables")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(pub_deliv, exist_ok=True)

    safe_slug = re.sub(r"[^A-Za-z0-9]+", "_", f"{order_id}_{customer_name}").strip("_")[:48]
    out_mp4 = os.path.join(out_dir, f"Aura49_{safe_slug}_4D.mp4")
    out_jpg = os.path.join(out_dir, f"Aura49_{safe_slug}_Cover.jpg")
    out_meta = os.path.join(out_dir, f"Aura49_{safe_slug}_Receipt.json")

    render_custom_cover(out_jpg, customer_name, focus_topic, order_id)

    master_loop = os.path.join(pdir, "Content_Vault_4D_Thumbnails", "_master_4d_portal_1280x720.mp4")
    if not os.path.exists(master_loop):
        # Fallback to first upgraded 4D full video if master loop was cleaned
        full_dir = os.path.join(pdir, "Content_Vault_4D_Full")
        cands = [os.path.join(full_dir, f) for f in sorted(os.listdir(full_dir)) if f.endswith("_4D_MAX.mp4")] if os.path.exists(full_dir) else []
        master_loop = cands[0] if cands else ""

    enc = detect_encoder()
    safe_name = clean_drawtext(customer_name).upper()[:30] or "SOVEREIGN MEMBER"
    safe_focus = clean_drawtext(focus_topic).upper()[:38] or "QUANTUM ALIGNMENT"
    safe_oid = clean_drawtext(order_id).upper()[:26] or "AURA49"

    # Combine 4-second personalized 3D cover intro + seamless 4D Tesseract/Mobius video body with soothing 432Hz harmonic drone
    intro_sec = min(4, max(2, duration_sec // 3))
    body_sec = max(2, duration_sec - intro_sec)

    if master_loop and os.path.exists(master_loop):
        filt = (
            f"[0:v]scale=1280:720,fps=24,format=yuv420p,fade=t=out:st={intro_sec - 1}:d=1[v0];"
            f"[1:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1,fps=24,trim=duration={body_sec},setpts=PTS-STARTPTS,"
            f"drawbox=x=0:y=0:w=iw:h=68:color=black@0.55:t=fill,"
            f"drawtext=text='PRIVATE 4D AURA READING // {safe_name}':fontcolor=0x38BDF8:fontsize=26:x=(w-text_w)/2:y=22,"
            f"drawbox=x=0:y=ih-86:w=iw:h=86:color=black@0.62:t=fill,"
            f"drawtext=text='FOCUS - {safe_focus}  |  ORDER {safe_oid}':fontcolor=0xFACC15:fontsize=25:x=(w-text_w)/2:y=h-56,"
            f"format=yuv420p[v1];"
            f"[v0][v1]concat=n=2:v=1:a=0[vout];"
            f"aevalsrc='0.10*sin(2*PI*432*t)+0.05*sin(2*PI*528*t)+0.03*sin(2*PI*216*t)':s=44100:d={duration_sec}[aout]"
        )
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-loop", "1", "-t", str(intro_sec), "-i", out_jpg,
            "-stream_loop", "-1", "-i", master_loop,
            "-filter_complex", filt,
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", enc, "-pix_fmt", "yuv420p",
        ]
    else:
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-loop", "1", "-t", str(duration_sec), "-i", out_jpg,
            "-f", "lavfi", "-i", f"aevalsrc=0.10*sin(2*PI*432*t):s=44100:d={duration_sec}",
            "-c:v", enc, "-pix_fmt", "yuv420p",
        ]

    cmd += (["-preset", "p4", "-b:v", "2800k"] if enc == "h264_nvenc" else ["-preset", "veryfast", "-crf", "23"])
    cmd += ["-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out_mp4]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg Aura49 render failed: {res.stderr[:300]}")

    # Copy into deliverables\ root so /api/download/secure-asset can serve it immediately
    secure_copy = os.path.join(pub_deliv, os.path.basename(out_mp4))
    shutil.copy2(out_mp4, secure_copy)

    mb = round(os.path.getsize(out_mp4) / (1024 ** 2), 2)
    meta = {
        "order_id": order_id,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "focus_topic": focus_topic,
        "duration_sec": duration_sec,
        "encoder": enc,
        "fulfilled_utc": dt.datetime.utcnow().isoformat() + "Z",
        "mp4_path": out_mp4,
        "secure_download_copy": secure_copy,
        "cover_jpg": out_jpg,
        "size_mb": mb,
    }
    json.dump(meta, open(out_meta, "w", encoding="utf-8"), indent=2)
    print(f"[FULFILLED] {os.path.basename(out_mp4)} ({mb:.2f} MB, {duration_sec}s, {enc}) -> staged in deliverables\\")
    return meta


def main():
    pdir = sys.argv[1]
    cfg = json.loads(base64.b64decode(sys.argv[2]).decode("utf-8"))
    state_p = os.path.join(pdir, "data", "aura49_fulfillment_state.json")
    state = {"fulfilled_orders": {}}
    if os.path.exists(state_p):
        try:
            state = json.load(open(state_p, "r", encoding="utf-8"))
        except Exception:
            pass

    mode = cfg.get("mode", "MANUAL")
    dur = int(cfg.get("duration_sec", 90))

    if mode == "MANUAL":
        oid = cfg.get("order_id") or ("AURA_" + dt.datetime.now().strftime("%Y%m%d_%H%M%S"))
        cname = cfg.get("customer_name") or "Sovereign Member"
        cemail = cfg.get("customer_email") or ""
        topic = cfg.get("focus_topic") or "Quantum Abundance & Clarity"
        meta = render_custom_aura_mp4(pdir, cname, topic, oid, dur, cemail)
        state.setdefault("fulfilled_orders", {})[oid] = meta
        json.dump(state, open(state_p, "w", encoding="utf-8"), indent=2)
        return

    # STRIPE_POLL mode: process newly paid $49 charges passed in via JSON file
    charges_p = cfg.get("charges_json", "")
    if not charges_p or not os.path.exists(charges_p):
        print("[INFO] No Stripe charges JSON provided.")
        return
    data = json.load(open(charges_p, "r", encoding="utf-8"))
    charges = data.get("data", data) if isinstance(data, dict) else data
    rendered = 0
    for ch in charges:
        if not ch.get("paid") or ch.get("refunded"):
            continue
        amt = int(ch.get("amount") or 0)
        if amt != 4900:
            continue
        oid = ch.get("id") or ""
        if oid in (state.get("fulfilled_orders") or {}):
            continue
        bd = ch.get("billing_details") or {}
        md = ch.get("metadata") or {}
        cname = (bd.get("name") or md.get("customer_name") or "Valued Member").strip()
        cemail = (bd.get("email") or ch.get("receipt_email") or "").strip()
        topic = (md.get("focus_topic") or md.get("topic") or "Quantum Abundance & Sovereign Clarity").strip()
        meta = render_custom_aura_mp4(pdir, cname, topic, oid, dur, cemail)
        state.setdefault("fulfilled_orders", {})[oid] = meta
        rendered += 1

    json.dump(state, open(state_p, "w", encoding="utf-8"), indent=2)
    print(f"[STRIPE POLL DONE] Newly fulfilled $49 AuraVideo49 orders: {rendered} | Total fulfilled: {len(state.get('fulfilled_orders', {}))}")


if __name__ == "__main__":
    main()