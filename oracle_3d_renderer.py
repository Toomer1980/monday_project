import os, sys, math, time, urllib.parse, subprocess
from playwright.sync_api import sync_playwright
import oracle_audio_master

ROOT = "C:/Users/toome/Desktop/SovereignCore"
os.chdir(ROOT)

def get_audio_duration(audio_path):
    try:
        out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path], text=True).strip()
        return max(10.0, float(out))
    except Exception:
        return 42.0

def detect_video_encoder():
    try:
        enc = subprocess.check_output(["ffmpeg", "-hide_banner", "-encoders"], text=True, stderr=subprocess.DEVNULL)
        if "h264_nvenc" in enc:
            test = subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=640x360:d=0.1", "-c:v", "h264_nvenc", "-f", "null", "-"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if test.returncode == 0:
                return "h264_nvenc"
    except Exception: pass
    return "libx264"

def render_3d_video(out_mp4, title, c1, c2, c3, spoken_text, kicker="ORACLE SYSTEMS COLLECTIVE TAROT // LIVE 3D", aura="#38bdf8", portrait_url="", mode="1080p", fps=24):
    dims = {"4k": (3840, 2160), "1080p": (1920, 1080), "short": (1080, 1920)}
    W, H = dims.get(mode, (1920, 1080))
    mp3_path = out_mp4.replace(".mp4", "_3d_master.mp3")
    print(f"[3D-ENGINE] Mastering cinematic voice + foley for: {title}")
    oracle_audio_master.synthesize_human_voice(spoken_text, mp3_path)
    dur = get_audio_duration(mp3_path)
    if mode == "short": dur = min(dur, 45.0)
    total_frames = int(math.ceil(dur * fps))
    vcodec = detect_video_encoder()
    print(f"[3D-ENGINE] Rendering {W}x{H} @ {fps}fps ({total_frames} frames, {dur:.1f}s) using GPU/encoder: {vcodec}")

    params = urllib.parse.urlencode({"render": "1", "kicker": kicker, "title": title, "c1": c1, "c2": c2, "c3": c3, "aura": aura, "portrait": portrait_url})
    stage_url = f"http://127.0.0.1:8000/oracle-3d?{params}"

    ff_cmd = [
        "ffmpeg", "-y",
        "-f", "image2pipe", "-vcodec", "mjpeg", "-framerate", str(fps), "-i", "-",
        "-i", mp3_path,
        "-map", "0:v", "-map", "1:a",
        "-c:v", vcodec, "-pix_fmt", "yuv420p",
        "-b:v", "18M" if mode == "4k" else "8M",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", out_mp4
    ]
    proc = subprocess.Popen(ff_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True, args=["--use-gl=angle", "--enable-webgl", "--ignore-gpu-blocklist"])
        page = browser.new_page(viewport={"width": W, "height": H})
        page.goto(stage_url, wait_until="networkidle", timeout=60000)
        page.wait_for_function("typeof window.setTimeline === 'function'", timeout=20000)
        t0 = time.time()
        for f_idx in range(total_frames):
            t_sec = f_idx / float(fps)
            page.evaluate(f"window.setTimeline({t_sec:.4f})")
            jpg = page.screenshot(type="jpeg", quality=92)
            proc.stdin.write(jpg)
            if f_idx % (fps * 10) == 0 and f_idx > 0:
                pct = int((f_idx / float(total_frames)) * 100)
                print(f"    [*] 3D Render Progress: {pct}% ({f_idx}/{total_frames} frames, {time.time()-t0:.1f}s)")
        browser.close()

    proc.stdin.close()
    proc.wait()
    print(f"[+] 3D ANIMATED MASTER COMPLETE: {out_mp4} ({os.path.getsize(out_mp4)//1024} KB)")
    return out_mp4

if __name__ == "__main__":
    mode_arg = sys.argv[1] if len(sys.argv) > 1 else "1080p"
    out_file = ROOT + "/Content_Vault_52Weeks/Week_01_Sudden_Breakthrough.mp4"
    if mode_arg == "4k":
        out_file = ROOT + "/Content_Vault_52Weeks/Week_01_Sudden_Breakthrough_4K.mp4"
    elif mode_arg == "short":
        out_file = ROOT + "/Content_Vault_Shorts/Short_01_Sudden_Breakthrough.mp4"
    script = "Hey everyone, welcome back to the Oracle Systems live collective reading. If this video found you today, trust that the timing is real. Take a slow breath in, and let it out. Today we are channeling The Tower, The Star, and the Ace of Pentacles. First, in your past foundation, The Tower cleared away outdated ground that could no longer hold where you are going. Second, in your present shift, The Star is pouring crystal clarity and renewed momentum directly into your path. And finally, your incoming outcome is the Ace of Pentacles: a real, tangible financial opening arriving within the next few days. Type I claim this alignment in the comments below, and visit the link in the description to experience your own live 3D personalized reading or unlock the full fifty-two week blueprint."
    render_3d_video(out_file, "Sudden Financial & Spiritual Breakthrough", "The Tower", "The Star", "Ace of Pentacles", script, kicker="ORACLE SYSTEMS COLLECTIVE TAROT // WEEK 01", mode=mode_arg)
