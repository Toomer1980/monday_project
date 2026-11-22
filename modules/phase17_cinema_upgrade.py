import argparse
import asyncio
import datetime as dt
import glob
import json
import math
import os
import py_compile
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
os.chdir(PDIR)

MAJOR_ARCANA = [
    ("THE STAR", "XVII", "DIVINE ALIGNMENT & CLARITY", "#38bdf8", "#facc15"),
    ("WHEEL OF FORTUNE", "X", "SUDDEN WINDFALL & CYCLE SHIFT", "#facc15", "#c084fc"),
    ("THE SUN", "XIX", "UNSTOPPABLE ABUNDANCE & POWER", "#fbbf24", "#f97316"),
    ("THE MAGICIAN", "I", "SOVEREIGN CREATION & MASTERY", "#a855f7", "#38bdf8"),
    ("THE WORLD", "XXI", "COMPLETE REALM EXPANSION", "#10b981", "#facc15"),
    ("THE EMPRESS", "III", "MAGNETIC WEALTH & FLOW", "#ec4899", "#facc15"),
    ("ACE OF PENTACLES", "I", "NEW FINANCIAL PORTAL OPENED", "#22c55e", "#38bdf8"),
    ("THE EMPEROR", "IV", "ARCHITECTURAL AUTHORITY", "#f59e0b", "#ef4444"),
]


def load_font(size):
    for p in (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\georgia.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def get_public_url():
    p = os.path.join(PDIR, "config", "public_url.txt")
    if os.path.exists(p):
        u = open(p, "r", encoding="utf-8").read().strip().rstrip("/")
        if u.startswith("http"):
            return u
    return "http://127.0.0.1:8000"


def find_elevenlabs_key():
    ep = os.path.join(PDIR, ".env")
    if os.path.exists(ep):
        for ln in open(ep, "r", encoding="utf-8", errors="ignore"):
            if ln.strip().startswith("ELEVENLABS_API_KEY="):
                val = ln.split("=", 1)[1].strip().strip('"').strip("'")
                if len(val) >= 20 and "YOUR_" not in val.upper():
                    return val
    desk = os.path.join(os.path.expanduser("~"), "Desktop")
    for fn in ("Eleven lab API.txt", "elevenlabs_api.txt", "ElevenLabs_API.txt"):
        fp = os.path.join(desk, fn)
        if os.path.exists(fp):
            raw = open(fp, "r", encoding="utf-8", errors="ignore").read().strip()
            m = re.search(r"(sk_[A-Za-z0-9]{24,}|[a-f0-9]{32})", raw)
            if m:
                return m.group(1)
    return ""


def ensure_edge_tts():
    try:
        import edge_tts  # noqa
        return True
    except ImportError:
        print("[VOICE] Installing Microsoft Neural edge-tts (studio broadcast voice, $0 cost)...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "edge-tts"], check=False)
        try:
            import edge_tts  # noqa
            return True
        except ImportError:
            return False


def synthesize_cinema_voice(text, out_mp3, voice_name="en-US-AndrewMultilingualNeural"):
    """Tier 1: ElevenLabs Neural Studio Voice (if active key+quota). Tier 2: Microsoft Neural edge-tts."""
    os.makedirs(os.path.dirname(out_mp3), exist_ok=True)
    el_key = find_elevenlabs_key()
    if el_key:
        try:
            voice_id = "pNInz6obpgDQGcFmaJgB"
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            payload = json.dumps({
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.48, "similarity_boost": 0.80, "style": 0.35, "use_speaker_boost": True},
            }).encode("utf-8")
            req = urllib.request.Request(
                url, data=payload,
                headers={"xi-api-key": el_key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if len(data) > 2000:
                    open(out_mp3, "wb").write(data)
                    return "ElevenLabs-Neural (Adam / eleven_multilingual_v2)"
        except Exception as ex:
            print(f"[VOICE NOTE] ElevenLabs skipped ({str(ex)[:80]}) -> switching to Microsoft Neural Broadcast Voice...")

    if ensure_edge_tts():
        import edge_tts

        async def _gen():
            comm = edge_tts.Communicate(text, voice=voice_name, rate="-7%", pitch="-3Hz")
            await comm.save(out_mp3)

        asyncio.run(_gen())
        if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 1000:
            return f"Microsoft-Neural ({voice_name})"

    raise RuntimeError("No neural TTS engine available. Check internet connection for edge-tts.")


def detect_encoder():
    try:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True, timeout=6)
        if "h264_nvenc" in r.stdout:
            t = subprocess.run(
                ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=128x128:d=0.1", "-c:v", "h264_nvenc", "-f", "null", "-"],
                capture_output=True, timeout=8,
            )
            if t.returncode == 0:
                return "h264_nvenc"
    except Exception:
        pass
    return "libx264"


# ==============================================================================
# 1. HOLOGRAPHIC 3-CARD SPREAD RENDERER (THUMBNAILS + VIDEO OPENING SPREAD)
# ==============================================================================
def draw_holographic_card(title, roman, subtitle, c1_hex, c2_hex, cw=290, ch=460):
    def hex2rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    r1, g1, b1 = hex2rgb(c1_hex)
    r2, g2, b2 = hex2rgb(c2_hex)
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)

    d.rounded_rectangle([2, 2, cw - 3, ch - 3], radius=22, fill=(9, 14, 34, 248), outline=(250, 204, 21, 255), width=4)
    d.rounded_rectangle([12, 12, cw - 13, ch - 13], radius=16, fill=(11, 18, 42, 245), outline=(r1, g1, b1, 210), width=2)

    cx, cy = cw // 2, int(ch * 0.42)
    for k in range(5):
        rad = 34 + k * 17
        col = (r1, g1, b1, max(45, 220 - k * 35)) if k % 2 == 0 else (r2, g2, b2, max(45, 210 - k * 35))
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=col, width=2)

    for i in range(8):
        ang = i * math.pi / 4.0
        x2 = cx + math.cos(ang) * 92
        y2 = cy + math.sin(ang) * 92
        d.line([(cx, cy), (x2, y2)], fill=(250, 204, 21, 185), width=2)
    pts_outer = [(cx, cy - 82), (cx + 76, cy), (cx, cy + 82), (cx - 76, cy)]
    d.polygon(pts_outer, outline=(56, 228, 255, 240))
    pts_inner = [(cx, cy - 48), (cx + 46, cy), (cx, cy + 48), (cx - 46, cy)]
    d.polygon(pts_inner, outline=(250, 204, 21, 245))

    f_rom = load_font(26)
    f_tit = load_font(24)
    f_sub = load_font(14)
    rb = d.textbbox((0, 0), roman, font=f_rom)
    d.text((cx - (rb[2] - rb[0]) // 2, 24), roman, font=f_rom, fill=(250, 204, 21, 255))

    d.rectangle([18, ch - 118, cw - 18, ch - 24], fill=(5, 9, 22, 230), outline=(250, 204, 21, 180), width=1)
    tb = d.textbbox((0, 0), title, font=f_tit)
    d.text((cx - (tb[2] - tb[0]) // 2, ch - 104), title, font=f_tit, fill=(250, 204, 21, 255))
    sb = d.textbbox((0, 0), subtitle[:28], font=f_sub)
    d.text((cx - (sb[2] - sb[0]) // 2, ch - 62), subtitle[:28], font=f_sub, fill=(56, 228, 255, 240))
    return card


def render_3card_spread_thumbnail(out_jpg, headline, theme_idx=0):
    w, h = 1280, 720
    bg = Image.new("RGBA", (w, h), (4, 7, 18, 255))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([180, -60, 1100, 680], fill=(14, 165, 233, 72))
    gd.ellipse([360, 60, 920, 580], fill=(250, 204, 21, 68))
    gd.ellipse([480, 140, 800, 460], fill=(168, 85, 247, 75))
    bg = Image.alpha_composite(bg, glow.filter(ImageFilter.GaussianBlur(radius=68)))

    d_bg = ImageDraw.Draw(bg)
    for gx in range(0, w + 1, 80):
        d_bg.line([(w // 2, 260), (gx, h)], fill=(56, 189, 248, 34), width=1)
    for gy in range(360, h, 44):
        d_bg.line([(0, gy), (w, gy)], fill=(250, 204, 21, 26), width=1)

    c_left = MAJOR_ARCANA[(theme_idx + 0) % len(MAJOR_ARCANA)]
    c_mid  = MAJOR_ARCANA[(theme_idx + 1) % len(MAJOR_ARCANA)]
    c_rgt  = MAJOR_ARCANA[(theme_idx + 2) % len(MAJOR_ARCANA)]

    im_l = draw_holographic_card(*c_left, cw=270, ch=420).rotate(12, resample=Image.Resampling.BICUBIC, expand=True)
    im_r = draw_holographic_card(*c_rgt,  cw=270, ch=420).rotate(-12, resample=Image.Resampling.BICUBIC, expand=True)
    im_m = draw_holographic_card(*c_mid,  cw=305, ch=470)

    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle([w // 2 - 170, 86, w // 2 + 170, 578], radius=24, fill=(56, 228, 255, 110))
    bg = Image.alpha_composite(bg, sh.filter(ImageFilter.GaussianBlur(radius=22)))

    bg.alpha_composite(im_l, (175, 130))
    bg.alpha_composite(im_r, (w - 175 - im_r.width, 130))
    bg.alpha_composite(im_m, (w // 2 - im_m.width // 2, 92))

    bar = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar)
    bd.rectangle([0, 0, w, 74], fill=(4, 7, 18, 200))
    bd.rectangle([0, 565, w, h], fill=(4, 7, 18, 228))
    bd.line([(0, 565), (w, 565)], fill=(250, 204, 21, 240), width=3)
    bg = Image.alpha_composite(bg, bar)

    d = ImageDraw.Draw(bg)
    top_txt = "ORACLE SYSTEMS 5D HOLOGRAPHIC SPREAD  //  PAST  |  PRESENT  |  QUANTUM SHIFT"
    tb = d.textbbox((0, 0), top_txt, font=load_font(22))
    d.text((w // 2 - (tb[2] - tb[0]) // 2, 24), top_txt, font=load_font(22), fill=(56, 228, 255, 255))

    clean_h = re.sub(r"[^A-Za-z0-9 &\-!]", "", headline).upper()[:34]
    f_big = load_font(56)
    hb = d.textbbox((0, 0), clean_h, font=f_big)
    hx = w // 2 - (hb[2] - hb[0]) // 2
    for off in range(4, 0, -1):
        d.text((hx + off, 586 + off), clean_h, font=f_big, fill=(5, 10, 24, 235))
    d.text((hx, 586), clean_h, font=f_big, fill=(250, 204, 21, 255))

    sub_txt = f"{c_left[0]}  +  {c_mid[0]}  +  {c_rgt[0]}"
    sb = d.textbbox((0, 0), sub_txt, font=load_font(24))
    d.text((w // 2 - (sb[2] - sb[0]) // 2, 662), sub_txt, font=load_font(24), fill=(226, 232, 240, 245))

    bg.convert("RGB").save(out_jpg, "JPEG", quality=94, optimize=True)


# ==============================================================================
# 2. UPGRADE /store WITH LIVE INTERACTIVE 3D HOLOGRAPHIC CARD SPREAD + NEURAL VOICE
# ==============================================================================
def upgrade_web_card_spread_and_voice():
    static_dir = os.path.join(PDIR, "static")
    audio_dir = os.path.join(static_dir, "card_voices")
    os.makedirs(audio_dir, exist_ok=True)

    spread_scripts = [
        ("card_past.mp3", "Card one: The Magician. Every skill, setback, and silent late night you endured has converged into sovereign architectural mastery. The hesitation phase is officially over."),
        ("card_present.mp3", "Card two: Wheel of Fortune. The frequency around your financial timeline is rotating sharply upward right now. A decisive door is opening—step through it before the cycle locks."),
        ("card_future.mp3", "Card three: The Sun. Total clarity, magnetic abundance, and unmistakable momentum. Claim your personalized 4D Aura Reading below to lock in your exact alignment blueprint."),
    ]
    for fname, script in spread_scripts:
        out_mp3 = os.path.join(audio_dir, fname)
        if not os.path.exists(out_mp3) or os.path.getsize(out_mp3) < 2000:
            voice_used = synthesize_cinema_voice(script, out_mp3)
            print(f"[WEB VOICE READY] {fname} via {voice_used}")

    card_js_path = os.path.join(static_dir, "omega_card_spread.js")
    card_js = """(function(){
  var hero = document.getElementById("oracle-4d-hero");
  if (!hero || document.getElementById("omega-tarot-stage")) return;

  var style = document.createElement("style");
  style.textContent = [
    "#omega-tarot-stage{margin:18px 0 26px 0;padding:22px 18px;border-radius:16px;background:radial-gradient(circle at 50% 0%,rgba(56,189,248,0.18),rgba(5,8,20,0.92) 70%);border:1px solid rgba(250,204,21,0.45);box-shadow:0 0 42px rgba(250,204,21,0.12);}",
    ".ots-hdr{text-align:center;margin-bottom:18px;}",
    ".ots-hdr h2{margin:4px 0;font-size:24px;background:linear-gradient(90deg,#facc15,#38bdf8,#fef08a);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}",
    ".ots-hdr p{margin:0;color:#cbd5e1;font-size:13px;}",
    ".ots-row{display:flex;flex-wrap:wrap;justify-content:center;gap:22px;perspective:1200px;}",
    ".ots-card{width:230px;height:350px;cursor:pointer;position:relative;transform-style:preserve-3d;transition:transform 0.85s cubic-bezier(.2,.8,.2,1);}",
    ".ots-card.flipped{transform:rotateY(180deg);}",
    ".ots-card:hover:not(.flipped){transform:translateY(-8px) rotateX(6deg) rotateY(-6deg);}",
    ".ots-face{position:absolute;inset:0;border-radius:16px;backface-visibility:hidden;overflow:hidden;display:flex;flex-direction:column;justify-content:space-between;padding:16px;box-sizing:border-box;}",
    ".ots-back{background:radial-gradient(circle at 50% 45%,#172554 0%,#050814 75%);border:2px solid #facc15;box-shadow:0 0 26px rgba(56,189,248,0.35),inset 0 0 24px rgba(250,204,21,0.22);align-items:center;justify-content:center;text-align:center;}",
    ".ots-sigil{width:130px;height:130px;border-radius:50%;border:2px solid rgba(250,204,21,0.85);display:flex;align-items:center;justify-content:center;box-shadow:0 0 28px rgba(56,189,248,0.5);animation:otsPulse 3.2s infinite ease-in-out;}",
    "@keyframes otsPulse{0%,100%{transform:scale(1);box-shadow:0 0 22px rgba(56,189,248,0.45);}50%{transform:scale(1.06);box-shadow:0 0 38px rgba(250,204,21,0.75);}}",
    ".ots-front{transform:rotateY(180deg);background:linear-gradient(155deg,#0f172a 0%,#1e1b4b 50%,#050814 100%);border:2px solid #38bdf8;box-shadow:0 0 34px rgba(250,204,21,0.38);text-align:center;}",
    ".ots-front::after{content:'';position:absolute;inset:-60%;background:linear-gradient(115deg,transparent 35%,rgba(255,255,255,0.16) 50%,transparent 65%);transform:rotate(18deg);pointer-events:none;animation:otsSheen 4.5s infinite linear;}",
    "@keyframes otsSheen{0%{transform:translateX(-70%) rotate(18deg);}100%{transform:translateX(70%) rotate(18deg);}}",
    ".ots-pos{font-size:10px;letter-spacing:2px;color:#38bdf8;font-weight:800;text-transform:uppercase;}",
    ".ots-num{font-size:20px;color:#facc15;font-weight:800;margin-top:2px;}",
    ".ots-art{margin:8px auto;width:128px;height:128px;border-radius:50%;border:1.5px solid rgba(250,204,21,0.75);background:radial-gradient(circle,rgba(250,204,21,0.28),rgba(56,189,248,0.12) 60%,transparent 75%);display:flex;align-items:center;justify-content:center;font-size:48px;text-shadow:0 0 24px #facc15;}",
    ".ots-name{font-size:17px;font-weight:900;color:#fef08a;letter-spacing:1px;}",
    ".ots-msg{font-size:11.5px;color:#cbd5e1;line-height:1.4;margin:6px 0;}",
    ".ots-bar{margin-top:16px;display:flex;flex-wrap:wrap;justify-content:center;gap:10px;align-items:center;}",
    ".ots-btn{cursor:pointer;padding:9px 18px;border:none;border-radius:8px;font-weight:800;font-size:13px;background:linear-gradient(90deg,#facc15,#38bdf8);color:#050814;}"
  ].join("");
  document.head.appendChild(style);

  var cards = [
    {pos:"I. PAST CATALYST", num:"I", sym:"&#10022;", name:"THE MAGICIAN", msg:"Every lesson has forged sovereign mastery. Hesitation ends tonight.", audio:"/static/card_voices/card_past.mp3"},
    {pos:"II. PRESENT SHIFT", num:"X", sym:"&#9788;", name:"WHEEL OF FORTUNE", msg:"Your financial frequency is rotating sharply upward. Step through the portal.", audio:"/static/card_voices/card_present.mp3"},
    {pos:"III. QUANTUM OUTCOME", num:"XIX", sym:"&#9728;", name:"THE SUN", msg:"Total clarity, magnetic wealth, and unstoppable forward momentum.", audio:"/static/card_voices/card_future.mp3"}
  ];

  var stage = document.createElement("div");
  stage.id = "omega-tarot-stage";
  var html = '<div class="ots-hdr"><div class="ots-pos">LIVE INTERACTIVE 5D HOLOGRAPHIC SPREAD // STUDIO NEURAL VOICE</div>'
    + '<h2>Tap Each Holographic Card to Reveal Your Alignment &amp; Hear the Studio Reading</h2>'
    + '<p>Zero robotic speech — narrated by our studio neural voice engine. Flip all 3 cards to unlock your custom reading pathway.</p></div><div class="ots-row">';

  cards.forEach(function(cd, idx){
    html += '<div class="ots-card" data-idx="' + idx + '" onclick="omegaFlipCard(this,' + idx + ')">'
      + '<div class="ots-face ots-back"><div class="ots-pos">' + cd.pos + '</div><div class="ots-sigil"><div style="color:#facc15;font-weight:900;letter-spacing:2px;font-size:13px;">ORACLE<br>5D</div></div><div style="color:#38bdf8;font-size:12px;font-weight:700;margin-top:14px;">TAP TO REVEAL</div></div>'
      + '<div class="ots-face ots-front"><div><div class="ots-pos">' + cd.pos + '</div><div class="ots-num">' + cd.num + '</div></div>'
      + '<div class="ots-art">' + cd.sym + '</div>'
      + '<div><div class="ots-name">' + cd.name + '</div><div class="ots-msg">' + cd.msg + '</div></div></div></div>';
  });
  html += '</div><div class="ots-bar"><button class="ots-btn" onclick="omegaRevealAll()">Reveal Full 3-Card Spread + Play Studio Voice</button>'
    + '<a class="ots-btn" style="text-decoration:none;background:linear-gradient(90deg,#059669,#0284c7);color:#fff;" href="/go/auravideo49?utm_source=card_spread&utm_medium=cta&utm_campaign=holo_spread_v17">Claim Your Custom 4D Aura Reading ($49)</a></div>';
  stage.innerHTML = html;

  var grid = hero.querySelector(".o4d-grid");
  if (grid) hero.insertBefore(stage, grid); else hero.appendChild(stage);

  var player = new Audio();
  window.omegaFlipCard = function(el, idx){
    el.classList.add("flipped");
    try { player.pause(); player.src = cards[idx].audio; player.play(); } catch(e){}
  };
  window.omegaRevealAll = function(){
    var all = document.querySelectorAll(".ots-card");
    all.forEach(function(el, i){ setTimeout(function(){ el.classList.add("flipped"); }, i * 420); });
    var seq = [0, 1, 2], pos = 0;
    function playNext(){
      if (pos >= seq.length) return;
      player.src = cards[seq[pos++]].audio;
      player.onended = playNext;
      player.play().catch(function(){});
    }
    playNext();
  };
})();
"""
    open(card_js_path, "w", encoding="utf-8", newline="").write(card_js)

    dp = os.path.join(PDIR, "sovereign_daemon.py")
    src = open(dp, "r", encoding="utf-8").read()
    if "omega_card_spread.js" not in src:
        src = src.replace(
            'if _req.path == "/static/omega_5d_engine.js":',
            'if _req.path == "/static/omega_card_spread.js":\n'
            '            return _sfd(_o.path.join(base_dir, "static"), "omega_card_spread.js", mimetype="application/javascript")\n'
            '        if _req.path.startswith("/static/card_voices/"):\n'
            '            return _sfd(_o.path.join(base_dir, "static", "card_voices"), _req.path.rsplit("/", 1)[-1], mimetype="audio/mpeg")\n'
            '        if _req.path == "/static/omega_5d_engine.js":',
            1,
        )
        src = src.replace(
            '<script src=\\"/static/omega_5d_engine.js\\"></script>',
            '<script src=\\"/static/omega_5d_engine.js\\"></script><script src=\\"/static/omega_card_spread.js\\"></script>',
            1,
        )
        open(dp, "w", encoding="utf-8", newline="").write(src)
        py_compile.compile(dp, doraise=True)

        ns = subprocess.run(["netstat", "-ano"], capture_output=True, text=True).stdout
        pids = {ln.split()[-1] for ln in ns.splitlines() if ":8000 " in ln and "LISTENING" in ln.upper() and ln.split()[-1].isdigit()}
        for pid in pids:
            subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
        time.sleep(2)
        boot_log = open(os.path.join(PDIR, "logs", "daemon_boot.log"), "w", encoding="utf-8")
        subprocess.Popen([sys.executable, dp], cwd=PDIR, stdout=boot_log, stderr=boot_log, creationflags=0x08000000)
        time.sleep(3)
    print("[STORE SPREAD PASS] Interactive 3D Holographic Card Spread + Studio Neural Voice live on /store!")


# ==============================================================================
# 3. RE-RENDER ALL 104 3-CARD HOLOGRAPHIC THUMBNAILS + UPGRADE VIDEOS WITH NEURAL VOICE
# ==============================================================================
def upgrade_thumbnails_and_videos(video_limit=5):
    thumb_dir = os.path.join(PDIR, "Content_Vault_4D_Thumbnails")
    short_dir = os.path.join(PDIR, "Content_Vault_4D_Shorts")
    voice_tmp = os.path.join(PDIR, "logs", "cinema_voice_cache")
    os.makedirs(thumb_dir, exist_ok=True)
    os.makedirs(voice_tmp, exist_ok=True)

    thumbs = sorted(glob.glob(os.path.join(thumb_dir, "*_3D_Thumb.jpg")))
    for idx, tp in enumerate(thumbs):
        base = os.path.basename(tp).replace("_3D_Thumb.jpg", "")
        headline = re.sub(r"^(Short|Week)_\d+_", "", base).replace("_", " ")
        render_3card_spread_thumbnail(tp, headline, theme_idx=idx)
    print(f"[THUMBS PASS] Upgraded ALL {len(thumbs)} vault thumbnails to 3-Card Holographic Spread art!")

    shorts = sorted(glob.glob(os.path.join(short_dir, "*_4D_MAX.mp4")))
    state_p = os.path.join(PDIR, "data", "cinema_voice_upgraded.json")
    done = set(json.load(open(state_p, "r", encoding="utf-8"))) if os.path.exists(state_p) else set()

    priority = [s for s in shorts if any(k in os.path.basename(s) for k in ("Short_11_", "Short_09_", "Short_03_", "Short_04_", "Short_05_"))]
    ordered = priority + [s for s in shorts if s not in priority]
    todo = [s for s in ordered if os.path.basename(s) not in done][:video_limit]

    enc = detect_encoder()
    upgraded_now = 0
    for idx, mp4_path in enumerate(todo):
        fname = os.path.basename(mp4_path)
        slug = fname.replace("_4D_MAX.mp4", "")
        topic = re.sub(r"^Short_\d+_", "", slug).replace("_", " ")
        c1, c2, c3 = MAJOR_ARCANA[idx % len(MAJOR_ARCANA)], MAJOR_ARCANA[(idx + 1) % len(MAJOR_ARCANA)], MAJOR_ARCANA[(idx + 2) % len(MAJOR_ARCANA)]

        script = (
            f"Pause everything for three seconds and look directly into the five-dimensional card spread opening for {topic}. "
            f"Card one, {c1[0].title()}, clears the static from your past timeline. "
            f"Card two, {c2[0].title()}, signals an immediate upward financial and energetic shift happening right now. "
            f"And card three, {c3[0].title()}, locks in unmistakable momentum and sovereign clarity. "
            f"Type I claim this alignment below, and tap the link in the description to unlock your personalized 4D Aura Reading or the fifteen-dollar Creator Asset Pack."
        )
        v_mp3 = os.path.join(voice_tmp, f"{slug}_neural.mp3")
        t_jpg = os.path.join(thumb_dir, f"{slug}_3D_Thumb.jpg")
        if not os.path.exists(t_jpg):
            render_3card_spread_thumbnail(t_jpg, topic, theme_idx=idx)

        try:
            engine_name = synthesize_cinema_voice(script, v_mp3)
            tmp_out = mp4_path + ".cinema.mp4"
            filt = (
                "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=24,format=yuv420p,fade=t=out:st=2.8:d=0.7[v0];"
                "[1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=24,trim=duration=28,setpts=PTS-STARTPTS,format=yuv420p[v1];"
                "[v0][v1]concat=n=2:v=1:a=0[vout];"
                "[2:a]aformat=sample_rates=44100:channel_layouts=stereo,equalizer=f=180:width_type=o:w=1.2:g=3,acompressor=threshold=-18dB:ratio=3:attack=15:release=150,loudnorm=I=-14:TP=-1.5:LRA=9[vvoice];"
                "aevalsrc='0.055*sin(2*PI*432*t)+0.028*sin(2*PI*528*t)+0.018*sin(2*PI*216*t)':s=44100:d=31.5[pad];"
                "[vvoice][pad]amix=inputs=2:duration=longest:dropout_transition=2[aout]"
            )
            cmd = [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-loop", "1", "-t", "3.5", "-i", t_jpg,
                "-i", mp4_path,
                "-i", v_mp3,
                "-filter_complex", filt,
                "-map", "[vout]", "-map", "[aout]",
                "-c:v", enc, "-pix_fmt", "yuv420p",
            ]
            cmd += (["-preset", "p4", "-b:v", "3200k"] if enc == "h264_nvenc" else ["-preset", "veryfast", "-crf", "22"])
            cmd += ["-c:a", "aac", "-b:a", "192k", "-t", "31.5", "-movflags", "+faststart", tmp_out]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(tmp_out) and os.path.getsize(tmp_out) > 200000:
                shutil.move(tmp_out, mp4_path)
                done.add(fname)
                upgraded_now += 1
                print(f"[CINEMA VIDEO PASS {upgraded_now}/{len(todo)}] {fname} -> Studio Voice ({engine_name}) + 3-Card Holo Spread ({enc})")
            else:
                if os.path.exists(tmp_out):
                    os.remove(tmp_out)
                print(f"[VIDEO WARN] {fname}: {res.stderr[:200]}")
        except Exception as ex:
            print(f"[VIDEO WARN] {fname}: {ex}")

    json.dump(sorted(done), open(state_p, "w", encoding="utf-8"), indent=2)
    print(f"[VAULT VOICE STATUS] Upgraded this run: {upgraded_now} | Total cinema-voice upgraded: {len(done)}/{len(shorts)}")


# ==============================================================================
# 4. UPDATE ALL LIVE YOUTUBE DESCRIPTIONS WITH TRACKED 5D STOREFRONT LINKS
# ==============================================================================
def update_live_youtube_descriptions():
    pub = get_public_url()
    tok_p = os.path.join(PDIR, "config", "youtube_token.json")
    if not os.path.exists(tok_p):
        print("[YT-DESC] Skipped: config/youtube_token.json not found.")
        return

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials.from_authorized_user_file(tok_p)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        yt = build("youtube", "v3", credentials=creds)

        ch = yt.channels().list(part="contentDetails", mine=True).execute()
        items = ch.get("items") or []
        if not items:
            print("[YT-DESC] No channel found.")
            return
        uploads_pl = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        pl_res = yt.playlistItems().list(part="snippet", playlistId=uploads_pl, maxResults=15).execute()

        updated = 0
        for it in (pl_res.get("items") or []):
            vid = it["snippet"]["resourceId"]["videoId"]
            v_res = yt.videos().list(part="snippet", id=vid).execute()
            v_items = v_res.get("items") or []
            if not v_items:
                continue
            snip = v_items[0]["snippet"]
            title = snip.get("title", "5D Holographic Oracle Reading")
            cat_id = snip.get("categoryId", "22")
            new_desc = (
                "5D HOLOGRAPHIC CARD SPREAD // ORACLE SYSTEMS LLC\n"
                "INTERACTIVE 5D PENTERACT PORTAL + STUDIO NEURAL READING\n\n"
                "Step into the live rotating 5D Penteract field, flip your own 3-Card Holographic Spread, "
                "and unlock instant Stripe-verified digital fulfillment:\n\n"
                f"-> LIVE INTERACTIVE 5D CARD SPREAD & STOREFRONT:\n{pub}/store\n\n"
                f"-> INSTANT $15 4D CREATOR ASSET PACK (Loops + 3D Templates):\n{pub}/go/assetpack15?utm_source=youtube&utm_medium=desc&utm_campaign={vid}\n\n"
                f"-> $15/MO SOVEREIGN 4D MEMBER VAULT (30-Min Transmissions + 432Hz):\n{pub}/go/vaultsub15?utm_source=youtube&utm_medium=desc&utm_campaign={vid}\n\n"
                f"-> CUSTOM PERSONALIZED 4D AURA READING ($49 - Your Name & Focus):\n{pub}/go/auravideo49?utm_source=youtube&utm_medium=desc&utm_campaign={vid}\n\n"
                f"-> FULL CREATOR AUTOMATION STACK ($1,500) & PRO_NODE ($49,999):\n{pub}/go/fullstorefront?utm_source=youtube&utm_medium=desc&utm_campaign={vid}\n\n"
                "Comment 'I CLAIM THIS ALIGNMENT' below to lock in the shift.\n"
                "#5DTarot #4DTesseract #OracleSystems #QuantumAlignment #CollectiveReading #Shorts"
            )
            snip["description"] = new_desc
            snip["categoryId"] = cat_id
            yt.videos().update(part="snippet", body={"id": vid, "snippet": snip}).execute()
            updated += 1
            print(f"[YT-DESC UPDATED {updated}] https://youtu.be/{vid} | {title[:55]}")

        print(f"[YT-DESC COMPLETE] Updated descriptions on {updated} live YouTube video(s) with active 5D storefront links!")
    except Exception as ex:
        print(f"[YT-DESC WARN] {ex}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--web-spread", action="store_true")
    ap.add_argument("--vault-upgrade", action="store_true")
    ap.add_argument("--video-limit", type=int, default=5)
    ap.add_argument("--update-yt", action="store_true")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    if args.all or args.web_spread:
        upgrade_web_card_spread_and_voice()
    if args.all or args.vault_upgrade:
        upgrade_thumbnails_and_videos(video_limit=args.video_limit)
    if args.all or args.update_yt:
        update_live_youtube_descriptions()


if __name__ == "__main__":
    main()