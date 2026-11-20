import base64
import csv
import datetime as dt
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    print("[INSTALL] Installing pillow & numpy for procedural 4D tesseract + Mobius rendering...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "pillow", "numpy"])
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter, ImageFont


def to_unicode_bold(text):
    out = []
    for ch in text:
        o = ord(ch)
        if 65 <= o <= 90:
            out.append(chr(0x1D5D4 + (o - 65)))
        elif 97 <= o <= 122:
            out.append(chr(0x1D5EE + (o - 97)))
        elif 48 <= o <= 57:
            out.append(chr(0x1D7EC + (o - 48)))
        else:
            out.append(ch)
    return "".join(out)


def load_font(size):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\calibrib.ttf",
        r"C:\Windows\Fonts\impact.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def detect_nvenc():
    try:
        res = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True, timeout=8)
        if "h264_nvenc" in res.stdout:
            test = subprocess.run(
                ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=128x128:d=0.1", "-c:v", "h264_nvenc", "-f", "null", "-"],
                capture_output=True, timeout=8
            )
            if test.returncode == 0:
                return "h264_nvenc"
    except Exception:
        pass
    return "libx264"


# Build 4D hypercube (tesseract): 16 vertices, 32 edges
TESS_VERTS = np.array(
    [[x, y, z, w] for x in (-1.0, 1.0) for y in (-1.0, 1.0) for z in (-1.0, 1.0) for w in (-1.0, 1.0)],
    dtype=np.float32,
)
TESS_EDGES = []
for i in range(16):
    for j in range(i + 1, 16):
        if int(np.sum(np.abs(TESS_VERTS[i] - TESS_VERTS[j]) > 0.1)) == 1:
            TESS_EDGES.append((i, j))


def render_4d_frame(width, height, phase, title_top="", title_main="", is_thumb=False):
    # 1. Translucent fluid quantum plasma field (computed at 1/4 res for speed, upscaled smoothly)
    sw, sh = max(160, width // 4), max(90, height // 4)
    xs = np.linspace(-2.2, 2.2, sw, dtype=np.float32)
    ys = np.linspace(-1.4, 1.4, sh, dtype=np.float32)
    X, Y = np.meshgrid(xs, ys)
    R = np.sqrt(X * X + Y * Y) + 1e-5
    ang = np.arctan2(Y, X)

    fluid = (
        np.sin(X * 2.4 + phase)
        + np.cos(Y * 2.6 - phase * 1.2)
        + np.sin(R * 4.5 - phase * 2.0 + np.sin(ang * 3.0 + phase))
    ) / 3.0
    vortex = np.exp(-R * 1.15) * (0.55 + 0.45 * np.sin(R * 8.0 - phase * 3.0 + ang * 2.0))

    r_ch = np.clip((10 + 40 * (fluid * 0.5 + 0.5) + 130 * vortex * np.maximum(0.0, np.sin(phase * 0.7 + R))), 0, 255)
    g_ch = np.clip((18 + 95 * (fluid * 0.5 + 0.5) + 150 * vortex), 0, 255)
    b_ch = np.clip((38 + 155 * (fluid * 0.5 + 0.5) + 120 * vortex), 0, 255)

    bg = np.stack([r_ch, g_ch, b_ch], axis=-1).astype(np.uint8)
    img = Image.fromarray(bg, mode="RGB").resize((width, height), Image.Resampling.BILINEAR).convert("RGBA")

    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    sharp = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sharp)

    cx, cy = width * 0.5, height * (0.48 if not is_thumb else 0.45)
    scale = min(width, height) * (0.34 if not is_thumb else 0.37)

    # 2. Concentric quantum portal rings
    for ring_i in range(4):
        rad = scale * (0.62 + ring_i * 0.14 + 0.03 * math.sin(phase * 2.0 + ring_i))
        alpha = max(35, 130 - ring_i * 25)
        col = (56, 228, 255, alpha) if ring_i % 2 == 0 else (245, 200, 75, alpha)
        gdraw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=col, width=4)

    # 3. Parametric 3D Mobius Strip ribbon
    u_steps = 96
    v_vals = (-0.34, -0.17, 0.0, 0.17, 0.34)
    ca, sa = math.cos(phase * 0.8), math.sin(phase * 0.8)
    cb, sb = math.cos(0.55 + 0.25 * math.sin(phase)), math.sin(0.55 + 0.25 * math.sin(phase))

    for vi, vv in enumerate(v_vals):
        pts = []
        for ui in range(u_steps + 1):
            u = (2.0 * math.pi * ui) / u_steps + phase * 0.5
            rad_m = 1.15 + vv * math.cos(u * 0.5)
            mx = rad_m * math.cos(u)
            my = rad_m * math.sin(u)
            mz = vv * math.sin(u * 0.5)
            # 3D rotation
            rx = mx * ca - mz * sa
            rz = mx * sa + mz * ca
            ry = my * cb - rz * sb
            rz2 = my * sb + rz * cb
            persp = 3.2 / (3.8 - rz2)
            pts.append((cx + rx * scale * 0.62 * persp, cy + ry * scale * 0.62 * persp))
        col_g = (45, 245, 220, 145) if vi in (0, 4) else (255, 215, 95, 115)
        gdraw.line(pts, fill=col_g, width=4 if vi in (0, 4) else 2)
        sdraw.line(pts, fill=(210, 255, 255, 165) if vi == 2 else col_g, width=2)

    # 4. Rotating 4D Tesseract (XW, YZ, XY rotation -> 4D->3D->2D projection)
    c1, s1 = math.cos(phase), math.sin(phase)
    c2, s2 = math.cos(phase * 0.7), math.sin(phase * 0.7)
    proj_2d = []
    depths = []
    for v in TESS_VERTS:
        x, y, z, w = float(v[0]), float(v[1]), float(v[2]), float(v[3])
        # XW 4D rotation
        x1 = x * c1 - w * s1
        w1 = x * s1 + w * c1
        # YZ 4D rotation
        y1 = y * c2 - z * s2
        z1 = y * s2 + z * c2
        # XY rotation
        x2 = x1 * c2 - y1 * s2
        y2 = x1 * s2 + y1 * c2
        # 4D -> 3D projection
        w_persp = 2.4 / (3.4 - w1)
        x3, y3, z3 = x2 * w_persp, y2 * w_persp, z1 * w_persp
        # 3D -> 2D projection
        z_persp = 2.5 / (4.2 - z3)
        px = cx + x3 * scale * 0.58 * z_persp
        py = cy + y3 * scale * 0.58 * z_persp
        proj_2d.append((px, py))
        depths.append(w1 + z3)

    for i, j in TESS_EDGES:
        d_avg = (depths[i] + depths[j]) * 0.5
        gold_edge = d_avg > 0.25
        g_col = (255, 210, 75, 210) if gold_edge else (0, 235, 255, 190)
        s_col = (255, 245, 185, 240) if gold_edge else (170, 250, 255, 220)
        lw = 5 if gold_edge else 3
        gdraw.line([proj_2d[i], proj_2d[j]], fill=g_col, width=lw + 2)
        sdraw.line([proj_2d[i], proj_2d[j]], fill=s_col, width=lw - 1)

    for px, py in proj_2d:
        r_dot = 5 if is_thumb else 4
        gdraw.ellipse([px - r_dot * 2, py - r_dot * 2, px + r_dot * 2, py + r_dot * 2], fill=(255, 220, 90, 180))
        sdraw.ellipse([px - r_dot, py - r_dot, px + r_dot, py + r_dot], fill=(255, 255, 255, 255))

    glow = glow.filter(ImageFilter.GaussianBlur(radius=6 if is_thumb else 4))
    img = Image.alpha_composite(img, glow)
    img = Image.alpha_composite(img, sharp)

    # 5. Pop-out 3D HUD Typography (for Thumbnails & Movie-Thumbs)
    if title_main:
        tdraw = ImageDraw.Draw(img)
        f_top = load_font(max(24, int(height * 0.048)))
        f_main = load_font(max(44, int(height * 0.105)))
        f_badge = load_font(max(22, int(height * 0.040)))

        # Dark glass bottom & top vignette bars for readability
        bar = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        bdraw = ImageDraw.Draw(bar)
        bdraw.rectangle([0, 0, width, int(height * 0.15)], fill=(4, 8, 20, 175))
        bdraw.rectangle([0, int(height * 0.72), width, height], fill=(4, 8, 20, 215))
        bdraw.line([(0, int(height * 0.72)), (width, int(height * 0.72))], fill=(56, 228, 255, 220), width=3)
        img = Image.alpha_composite(img, bar)
        tdraw = ImageDraw.Draw(img)

        if title_top:
            tdraw.text((int(width * 0.04), int(height * 0.04)), title_top.upper(), font=f_top, fill=(56, 228, 255, 255))

        # 3D extruded pop-out depth shadow stack
        tx = int(width * 0.04)
        ty = int(height * 0.75)
        main_up = title_main.upper()[:28]
        for off in range(7, 0, -1):
            tdraw.text((tx + off, ty + off), main_up, font=f_main, fill=(10, 25, 45, 220))
        tdraw.text((tx - 2, ty - 2), main_up, font=f_main, fill=(0, 235, 255, 200))
        tdraw.text((tx, ty), main_up, font=f_main, fill=(255, 215, 75, 255))

        badge_txt = "4D TESSERACT QUANTUM PORTAL  //  ORACLE SYSTEMS LLC"
        tdraw.text((tx, int(height * 0.90)), badge_txt, font=f_badge, fill=(225, 245, 255, 240))

    return img.convert("RGB")


def build_master_4d_loop(out_mp4, width, height, encoder, seconds=8, fps=20):
    if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 50000:
        return out_mp4

    total_frames = seconds * fps
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{width}x{height}", "-pix_fmt", "rgb24", "-r", str(fps),
        "-i", "-",
        "-c:v", encoder,
        "-pix_fmt", "yuv420p",
    ]
    if encoder == "h264_nvenc":
        cmd += ["-preset", "p4", "-b:v", "3500k"]
    else:
        cmd += ["-preset", "fast", "-crf", "23"]
    cmd.append(out_mp4)

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(total_frames):
        phase = (2.0 * math.pi * fi) / total_frames
        frame = render_4d_frame(width, height, phase)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"Failed generating 4D master loop {out_mp4}")
    return out_mp4


def build_movie_thumbnail(out_mp4, topic, badge_top, encoder):
    if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 20000:
        return
    width, height, fps, seconds = 1280, 720, 15, 4
    total_frames = fps * seconds
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{width}x{height}", "-pix_fmt", "rgb24", "-r", str(fps),
        "-i", "-",
        "-c:v", encoder, "-pix_fmt", "yuv420p",
    ]
    if encoder == "h264_nvenc":
        cmd += ["-preset", "p4", "-b:v", "2500k"]
    else:
        cmd += ["-preset", "fast", "-crf", "24"]
    cmd.append(out_mp4)

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(total_frames):
        phase = (2.0 * math.pi * fi) / total_frames
        frame = render_4d_frame(width, height, phase, title_top=badge_top, title_main=topic, is_thumb=True)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()


def build_bold_4d_description(kind, seq_num, topic, slug, base_url, use_utm):
    if use_utm:
        med = kind.lower()
        l49 = f"{base_url}/go/auravideo49?utm_source=youtube&utm_medium={med}&utm_campaign={slug}"
        l29 = f"{base_url}/go/tier29?utm_source=youtube&utm_medium={med}&utm_campaign={slug}"
        l1500 = f"{base_url}/go/fullstorefront?utm_source=youtube&utm_medium={med}&utm_campaign={slug}"
    else:
        l49 = "https://buy.stripe.com/6oU28rb29evn8di7UxcQU00"
        l29 = "https://buy.stripe.com/bJefZheeldrj1OU8YBcQU01"
        l1500 = "https://buy.stripe.com/28E9AT6LT0Ex79e7UxcQU03"

    h1 = to_unicode_bold(f"4D TESSERACT QUANTUM PORTAL // {topic.upper()}")
    h2 = to_unicode_bold("MOBIUS STRIP FLUID FIELD // ORACLE SYSTEMS LLC")
    cta1 = to_unicode_bold("UNLOCK YOUR CUSTOM 3D/4K AURA READING ($49):")
    cta2 = to_unicode_bold("STARTER PORTAL ACCESS ($29):")
    cta3 = to_unicode_bold("FULL ORACLE SYSTEMS STOREFRONT ($1,500):")
    cta4 = to_unicode_bold("ENTERPRISE PRO_NODE ARCHITECTURE ($49,999):")

    return (
        f"{h1}\n"
        f"{h2}\n\n"
        f"Step past linear perception into the rotating 4D Tesseract and endless Mobius Strip quantum field. "
        f"As the translucent fluid geometry locks into focus, notice how effortlessly your mind aligns with "
        f"forgotten architectural precision, calm clarity, and decisive forward momentum on {topic}.\n\n"
        f"Breathe in once... let the rotating hypercube quiet every distraction... and feel the next exact move "
        f"becoming unmistakable right now.\n\n"
        f"{cta1}\n{l49}\n\n"
        f"{cta2}\n{l29}\n\n"
        f"{cta3}\n{l1500}\n\n"
        f"{cta4}\nhttps://buy.stripe.com/aFa4gzgmt9b379efmZcQU04\n\n"
        f"Transmission Sequence: {kind} #{seq_num} | Campaign ID: {slug}\n"
        f"#4DTesseract #MobiusStrip #QuantumPortal #OracleSystems #FuturisticTarot #CollectiveReading #Shorts"
    )


def render_upgraded_video(src_mp4, loop_mp4, dst_mp4, width, height, target_sec, title_text, encoder):
    safe_title = re.sub(r"[^A-Za-z0-9 \-]", "", title_text).upper()[:34]
    # Blend existing source video (stream-looped) with translucent 4D tesseract/Mobius master loop
    filt = (
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1[base];"
        f"[1:v]scale={width}:{height},format=rgba,colorchannelmixer=aa=0.42[portal];"
        f"[base][portal]overlay=0:0:shortest=0,drawbox=x=0:y=ih-96:w=iw:h=96:color=black@0.55:t=fill,"
        f"drawtext=text='4D QUANTUM PORTAL // {safe_title}':fontcolor=0xFFD74B:fontsize=30:x=(w-text_w)/2:y=h-64[vout]"
    )
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-stream_loop", "-1", "-i", src_mp4,
        "-stream_loop", "-1", "-i", loop_mp4,
        "-filter_complex", filt,
        "-map", "[vout]", "-map", "0:a?",
        "-t", str(target_sec),
        "-c:v", encoder, "-pix_fmt", "yuv420p",
    ]
    if encoder == "h264_nvenc":
        cmd += ["-preset", "p4", "-b:v", "2800k"]
    else:
        cmd += ["-preset", "veryfast", "-crf", "24"]
    cmd += ["-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", dst_mp4]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg encode failed for {os.path.basename(src_mp4)}: {res.stderr[:300]}")


def main():
    project_dir = sys.argv[1]
    cfg = json.loads(base64.b64decode(sys.argv[2]).decode("utf-8"))

    full_in = os.path.join(project_dir, "Content_Vault_52Weeks")
    short_in = os.path.join(project_dir, "Content_Vault_Shorts")
    full_out = os.path.join(project_dir, "Content_Vault_4D_Full")
    short_out = os.path.join(project_dir, "Content_Vault_4D_Shorts")
    thumb_out = os.path.join(project_dir, "Content_Vault_4D_Thumbnails")
    desc_out = os.path.join(project_dir, "reports", "youtube_4d_descriptions")
    staging_dir = os.path.join(project_dir, "Oracle_Audit_2026")

    for d in (full_out, short_out, thumb_out, desc_out, staging_dir):
        os.makedirs(d, exist_ok=True)

    full_files = sorted(glob.glob(os.path.join(full_in, "*.mp4")))
    short_files = sorted(glob.glob(os.path.join(short_in, "*.mp4")))

    mode = cfg.get("mode", "TEST_FIRST")  # META_ONLY | TEST_FIRST | ALL
    full_sec = int(cfg.get("full_duration_sec", 1800))
    short_sec = int(cfg.get("short_duration_sec", 175))
    base_url = (cfg.get("base_url") or "").strip().rstrip("/")
    use_utm = bool(base_url and ("127.0.0.1" not in base_url) and ("localhost" not in base_url))
    start_dt = dt.date.today() + dt.timedelta(days=1)

    encoder = detect_nvenc()
    print(f"[ENGINE] Encoder: {encoder} | Mode: {mode} | Full Target: {full_sec}s | Short Target: {short_sec}s")
    print(f"[INVENTORY] Found {len(full_files)} Full Videos and {len(short_files)} Shorts")

    # Disk space guard before full batch video encode
    free_gb = shutil.disk_usage(project_dir).free / (1024 ** 3)
    if mode == "ALL":
        est_gb = ((len(full_files) * full_sec + len(short_files) * short_sec) * (3.0 / 8.0)) / 1024.0
        print(f"[DISK GUARD] Free C: {free_gb:.1f} GB | Estimated 104-video 4D batch size: ~{est_gb:.1f} GB")
        if free_gb < est_gb + 15.0:
            print(f"[ABORTED] Not enough free disk space ({free_gb:.1f} GB free, need ~{est_gb + 15.0:.1f} GB). Reduce -FullDurationSec or free space.")
            sys.exit(2)

    # 1. Generate 3D pop-out thumbnails + bold 4D descriptions + manifest for ALL 104 assets
    manifest_rows = []
    days_to_fri = (4 - start_dt.weekday() + 7) % 7
    first_fri = start_dt + dt.timedelta(days=days_to_fri)

    for idx, fp in enumerate(full_files):
        slug = os.path.splitext(os.path.basename(fp))[0]
        seq = f"{idx + 1:02d}"
        topic = re.sub(r"^Week_\d+_", "", slug).replace("_", " ")
        pub_date = (first_fri + dt.timedelta(days=idx * 7)).isoformat()
        thumb_jpg = os.path.join(thumb_out, f"{slug}_3D_Thumb.jpg")
        movie_thumb = os.path.join(thumb_out, f"{slug}_3D_MovieThumb.mp4")
        desc_txt = os.path.join(desc_out, f"{slug}_4D_Description.txt")
        dst_video = os.path.join(full_out, f"{slug}_4D_MAX.mp4")

        if not os.path.exists(thumb_jpg):
            im = render_4d_frame(1280, 720, phase=idx * 0.45, title_top=f"WEEK {seq} // 4D TESSERACT TRANSMISSION", title_main=topic, is_thumb=True)
            im.save(thumb_jpg, "JPEG", quality=92, optimize=True)

        desc = build_bold_4d_description("FullVideo", seq, topic, slug, base_url, use_utm)
        with open(desc_txt, "w", encoding="utf-8", newline="") as f:
            f.write(desc + "\n")

        manifest_rows.append({
            "sequence": seq, "type": "FullVideo", "publish_date": pub_date, "publish_time": "18:00 EST",
            "topic": topic, "source_mp4": fp, "upgraded_4d_mp4": dst_video, "target_sec": full_sec,
            "thumb_3d_jpg": thumb_jpg, "movie_thumb_mp4": movie_thumb, "description_file": desc_txt,
            "seo_title": f"{to_unicode_bold('4D PORTAL')} | Week {seq}: {topic} - Quantum Tesseract & Mobius Reading",
            "description": desc,
        })

    for idx, fp in enumerate(short_files):
        slug = os.path.splitext(os.path.basename(fp))[0]
        seq = f"{idx + 1:02d}"
        topic = re.sub(r"^Short_\d+_", "", slug).replace("_", " ")
        pub_date = (start_dt + dt.timedelta(days=idx)).isoformat()
        thumb_jpg = os.path.join(thumb_out, f"{slug}_3D_Thumb.jpg")
        movie_thumb = os.path.join(thumb_out, f"{slug}_3D_MovieThumb.mp4")
        desc_txt = os.path.join(desc_out, f"{slug}_4D_Description.txt")
        dst_video = os.path.join(short_out, f"{slug}_4D_MAX.mp4")

        if not os.path.exists(thumb_jpg):
            im = render_4d_frame(1280, 720, phase=idx * 0.62 + 1.1, title_top=f"SHORT #{seq} // QUANTUM SHIFT", title_main=topic, is_thumb=True)
            im.save(thumb_jpg, "JPEG", quality=92, optimize=True)

        desc = build_bold_4d_description("Short", seq, topic, slug, base_url, use_utm)
        with open(desc_txt, "w", encoding="utf-8", newline="") as f:
            f.write(desc + "\n")

        manifest_rows.append({
            "sequence": seq, "type": "Short", "publish_date": pub_date, "publish_time": "12:00 EST",
            "topic": topic, "source_mp4": fp, "upgraded_4d_mp4": dst_video, "target_sec": short_sec,
            "thumb_3d_jpg": thumb_jpg, "movie_thumb_mp4": movie_thumb, "description_file": desc_txt,
            "seo_title": f"#Shorts {to_unicode_bold('4D PORTAL')} | {topic} (#{seq})",
            "description": desc,
        })

    print(f"[PASS] Verified/generated 3D pop-out JPEG thumbnails + bold 4D descriptions for all {len(manifest_rows)} assets!")

    # 2. Render 4D master loops + Picture-Movie Thumbnails + Upgraded Videos based on mode
    if mode in ("TEST_FIRST", "ALL"):
        loop_land = os.path.join(thumb_out, "_master_4d_portal_1280x720.mp4")
        loop_vert = os.path.join(thumb_out, "_master_4d_portal_1080x1920.mp4")
        print("[RENDER] Building seamless 4D Tesseract + Mobius Fluid Portal master loops...")
        build_master_4d_loop(loop_land, 1280, 720, encoder)
        build_master_4d_loop(loop_vert, 1080, 1920, encoder)

        targets = []
        if mode == "TEST_FIRST":
            first_full = [r for r in manifest_rows if r["type"] == "FullVideo"][:1]
            first_short = [r for r in manifest_rows if r["type"] == "Short"][:1]
            targets = first_full + first_short
        else:
            targets = manifest_rows

        done = 0
        for row in targets:
            badge = f"{row['type'].upper()} #{row['sequence']} // 4D TESSERACT PORTAL"
            if not os.path.exists(row["movie_thumb_mp4"]):
                build_movie_thumbnail(row["movie_thumb_mp4"], row["topic"], badge, encoder)

            if os.path.exists(row["upgraded_4d_mp4"]) and os.path.getsize(row["upgraded_4d_mp4"]) > 100000:
                print(f"  [SKIP-DONE] {os.path.basename(row['upgraded_4d_mp4'])}")
                done += 1
                continue

            is_short = (row["type"] == "Short")
            w, h = (1080, 1920) if is_short else (1280, 720)
            loop_src = loop_vert if is_short else loop_land
            print(f"  [ENCODING {row['type']} #{row['sequence']}] {row['topic']} -> {row['target_sec']}s ({encoder})...")
            render_upgraded_video(row["source_mp4"], loop_src, row["upgraded_4d_mp4"], w, h, row["target_sec"], row["topic"], encoder)
            done += 1
            mb = os.path.getsize(row["upgraded_4d_mp4"]) / (1024 ** 2)
            print(f"  [PASS] {os.path.basename(row['upgraded_4d_mp4'])} ({mb:.1f} MB)")

        print(f"[RENDER COMPLETE] Processed {done}/{len(targets)} upgraded 4D video(s) + 3D picture-movie thumbnails.")

    # 3. Export master CSV + JSON manifest
    manifest_rows.sort(key=lambda x: (x["publish_date"], x["type"]))
    csv_out = os.path.join(project_dir, "reports", "youtube_52week_4d_manifest.csv")
    json_out = os.path.join(project_dir, "reports", "youtube_52week_4d_manifest.json")

    fields = ["sequence", "type", "publish_date", "publish_time", "topic", "target_sec", "seo_title", "thumb_3d_jpg", "movie_thumb_mp4", "upgraded_4d_mp4", "description_file"]
    with open(csv_out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(manifest_rows)

    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(manifest_rows, f, indent=2, ensure_ascii=False)

    shutil.copy2(csv_out, os.path.join(staging_dir, os.path.basename(csv_out)))
    print(f"[MANIFEST READY] {csv_out} (copy staged in Oracle_Audit_2026)")


if __name__ == "__main__":
    main()