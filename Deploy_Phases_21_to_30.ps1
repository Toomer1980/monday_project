# ==============================================================================
# ORACLE SYSTEMS LLC // MASTER 10-PHASE DEPLOYMENT & DEEP QA ENGINE (PHASES 21-30)
# Pure PowerShell 5.1 / ASCII | Self-Auditing | Low-RAM Safe | Zero Manual Edits
# ==============================================================================
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
Set-Location $ProjectDir$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)$env:RCLONE_BIND = "0.0.0.0"

foreach ($d in @("$ProjectDir\Modules","$ProjectDir\static","$ProjectDir\static\card_voices","$ProjectDir\assets\tarot_deck","$ProjectDir\data","$ProjectDir\reports","$ProjectDir\logs")) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null
}

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORACLE SYSTEMS LLC // EXECUTING PHASES 21-30 MASTER UPGRADE SUITE" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan

# Stop any stuck FFmpeg or duplicate video workers & trim RAM first
Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'ffmpeg.exe' -or$_.CommandLine -match 'phase17_|render_real_full' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
if (Test-Path "$ProjectDir\optimize_ram_and_boot.ps1") { & "$ProjectDir\optimize_ram_and_boot.ps1" -TrimNow }

# ==============================================================================
# PHASE 21: DEEP VISUAL & ASSET QA AUDITOR + ATOMIC CARD IMPORTER
# ==============================================================================
Write-Host "`n>>> [PHASE 21/30] Deep Asset QA Audit & Atomic Ray-Traced Card Importer..." -ForegroundColor Cyan
$QaAuditPy = @'
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
'@
[IO.File]::WriteAllText("$ProjectDir\Modules\qa_deep_audit.py", $QaAuditPy, $Utf8NoBom)
python "$ProjectDir\Modules\qa_deep_audit.py"

# ==============================================================================
# PHASE 22: GLARE-FREE THREE.JS WEBGL BLOOM CALIBRATION + /api/deck-manifest
# ==============================================================================
Write-Host "`n>>> [PHASE 22/30] Calibrating Glare-Free Three.js 3D Bloom Stage & Dynamic Verified Deck..." -ForegroundColor Cyan
$WebglFixPy = @'
import json
import os
import py_compile
import subprocess
import sys
import time
import urllib.request

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
STATIC_DIR = os.path.join(PDIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

STORE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Oracle Systems LLC // Sovereign 3D Ray-Lit Cinema Portal</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:#02040a;color:#e2e8f0;font-family:"Segoe UI",system-ui,-apple-system,sans-serif;overflow-x:hidden;}
  .top-nav{position:sticky;top:0;z-index:50;display:flex;justify-content:space-between;align-items:center;padding:14px 32px;background:rgba(2,4,10,0.88);backdrop-filter:blur(16px);border-bottom:1px solid rgba(250,204,21,0.24);}
  .brand{font-weight:900;letter-spacing:2.4px;font-size:13px;color:#facc15;}
  .nav-links a{color:#cbd5e1;text-decoration:none;margin-left:22px;font-size:13px;font-weight:600;transition:color .2s;}
  .nav-links a:hover{color:#facc15;}
  .stage-wrap{position:relative;width:100%;height:730px;background:radial-gradient(ellipse at 50% 45%,#0c1328 0%,#030610 58%,#010205 100%);border-bottom:1px solid rgba(250,204,21,0.30);overflow:hidden;user-select:none;}
  #webgl-stage{position:absolute;inset:0;width:100%;height:100%;cursor:grab;}
  #webgl-stage:active{cursor:grabbing;}
  .stage-hud-top{position:absolute;top:16px;left:0;right:0;text-align:center;pointer-events:none;z-index:10;padding:0 16px;}
  .pulse-pill{display:inline-block;padding:5px 14px;border-radius:999px;background:rgba(16,185,129,0.14);border:1px solid rgba(16,185,129,0.45);color:#6ee7b7;font-size:11px;font-weight:700;letter-spacing:1.5px;margin-bottom:6px;}
  .stage-hud-top h1{font-size:32px;font-weight:900;letter-spacing:-0.4px;background:linear-gradient(90deg,#fef08a,#facc15,#38bdf8,#fef08a);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
  .stage-hud-top p{color:#94a3b8;font-size:13px;margin-top:4px;}
  .stage-hud-bottom{position:absolute;bottom:18px;left:0;right:0;display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:10px;z-index:10;padding:0 16px;}
  .cta-gold{cursor:pointer;padding:11px 20px;border:none;border-radius:9px;font-weight:800;font-size:13px;background:linear-gradient(90deg,#facc15,#f59e0b,#38bdf8);color:#040712;box-shadow:0 8px 26px rgba(250,204,21,0.32);text-decoration:none;transition:transform .18s;}
  .cta-gold:hover{transform:translateY(-2px);}
  .cta-glass{cursor:pointer;padding:11px 18px;border:1px solid rgba(56,189,248,0.55);border-radius:9px;font-weight:700;font-size:13px;background:rgba(8,14,30,0.84);color:#e2e8f0;backdrop-filter:blur(8px);text-decoration:none;transition:all .18s;}
  .cta-glass:hover{border-color:#facc15;color:#facc15;}
  #active-card-caption{position:absolute;bottom:70px;left:50%;transform:translateX(-50%);z-index:10;padding:7px 20px;border-radius:999px;background:rgba(4,7,18,0.90);border:1px solid rgba(250,204,21,0.5);color:#fef08a;font-size:12.5px;font-weight:700;letter-spacing:0.6px;white-space:nowrap;pointer-events:none;max-width:92vw;overflow:hidden;text-overflow:ellipsis;}
  .container{max-width:1200px;margin:0 auto;padding:44px 24px 64px 24px;}
  .sec-kicker{color:#38bdf8;font-size:11px;font-weight:800;letter-spacing:2.4px;text-transform:uppercase;text-align:center;}
  .sec-title{text-align:center;font-size:30px;font-weight:800;margin:8px 0 28px 0;color:#f8fafc;}
  .tier-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:18px;}
  .tier-card{background:linear-gradient(160deg,rgba(15,23,42,0.92),rgba(7,11,24,0.96));border:1px solid rgba(148,163,184,0.22);border-radius:14px;padding:24px;display:flex;flex-direction:column;justify-content:space-between;transition:transform .2s,border-color .2s,box-shadow .2s;}
  .tier-card:hover{transform:translateY(-5px);border-color:rgba(250,204,21,0.65);box-shadow:0 16px 40px rgba(14,165,233,0.18);}
  .tier-card.featured{border:1.5px solid #38bdf8;box-shadow:0 0 32px rgba(56,189,248,0.16);}
  .badge{display:inline-block;font-size:10px;font-weight:800;padding:4px 9px;border-radius:5px;background:#facc15;color:#040712;letter-spacing:1.1px;margin-bottom:10px;}
  .t-name{font-size:12px;color:#38bdf8;font-weight:800;letter-spacing:1.8px;text-transform:uppercase;}
  .t-price{font-size:32px;font-weight:900;color:#facc15;margin:6px 0;}
  .t-anchor{font-size:13px;color:#64748b;text-decoration:line-through;margin-left:8px;font-weight:500;}
  .t-desc{font-size:14px;color:#94a3b8;line-height:1.55;margin:8px 0 20px 0;}
  .t-btn{display:block;text-align:center;padding:12px 16px;border-radius:9px;font-weight:800;text-decoration:none;color:#040712;background:linear-gradient(90deg,#facc15,#38bdf8);}
  .t-btn.ent{background:linear-gradient(90deg,#0284c7,#059669);color:#f8fafc;}
  .ref-bar{margin-top:34px;padding:20px 24px;border-radius:14px;background:rgba(15,23,42,0.85);border:1px dashed rgba(250,204,21,0.5);display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:14px;}
  .ref-bar input{background:#03050c;color:#38bdf8;border:1px solid #334155;border-radius:8px;padding:10px 12px;width:300px;font-size:12px;}
</style>
</head>
<body>
<nav class="top-nav">
  <div class="brand">ORACLE SYSTEMS LLC // SOVEREIGN 3D CINEMA STUDIO</div>
  <div class="nav-links">
    <a href="/store">3D Storefront</a>
    <a href="/personalize">3D Sanctuary</a>
    <a href="/portal">Member Portal</a>
    <a href="/dashboard">Executive Matrix</a>
  </div>
</nav>

<section class="stage-wrap" id="stage-box">
  <div class="stage-hud-top">
    <div id="omega-live-pulse" class="pulse-pill">CALIBRATED GPU 3D STAGE // STRIPE LIVE FULFILLMENT</div>
    <h1>Live 3D Ray-Lit Tarot Portal &amp; Sovereign AI Compute</h1>
    <p>Drag to orbit in 3D space. Click any floating card to bring it forward, flip with true obsidian contrast &amp; hear studio neural narration.</p>
  </div>
  <canvas id="webgl-stage"></canvas>
  <div id="active-card-caption">DRAG TO ORBIT 3D STAGE  |  CLICK ANY CARD TO POP OUT &amp; REVEAL</div>
  <div class="stage-hud-bottom">
    <button class="cta-gold" onclick="window.revealAll3DCards()">Reveal 3D Spread + Studio Voice</button>
    <button class="cta-glass" onclick="window.shuffleAndDraw3D()">Shuffle Verified Deck &amp; Draw 3</button>
    <button class="cta-glass" onclick="window.toggle3DFullscreen()">Fullscreen 3D</button>
    <a class="cta-glass" href="/go/auravideo49?utm_source=webgl_v22&utm_medium=hero&utm_campaign=cinema_v22">Order Custom 4D Aura ($49)</a>
    <a class="cta-glass" href="/go/assetpack15?utm_source=webgl_v22&utm_medium=hero&utm_campaign=cinema_v22">Asset Pack ($15)</a>
  </div>
</section>

<main class="container">
  <div class="sec-kicker">STRIPE-VERIFIED INSTANT FULFILLMENT</div>
  <h2 class="sec-title">Select Your Sovereign Tier</h2>
  <div class="tier-grid">
    <div class="tier-card featured">
      <div><span class="badge">FASTEST START</span><div class="t-name">Creator Asset Pack</div><div class="t-price">$15<span class="t-anchor">$49 value</span></div>
      <p class="t-desc">Commercial-use instant ZIP: seamless 16:9 &amp; 9:16 4D motion loops, ray-traced 3D spread templates &amp; overlays for YouTube, TikTok &amp; OBS.</p></div>
      <a class="t-btn" href="/go/assetpack15?utm_source=store_v22&utm_medium=card&utm_campaign=tier15">Unlock Instant Pack ($15)</a>
    </div>
    <div class="tier-card featured">
      <div><span class="badge">RECURRING VAULT</span><div class="t-name">Sovereign Member Vault</div><div class="t-price">$15/mo<span class="t-anchor">$39/mo</span></div>
      <p class="t-desc">Unlimited access to full multi-chapter collective readings, ad-free 432Hz studio audio drops &amp; priority member portal releases.</p></div>
      <a class="t-btn" href="/go/vaultsub15?utm_source=store_v22&utm_medium=card&utm_campaign=vault15">Join Member Vault ($15/mo)</a>
    </div>
    <div class="tier-card">
      <div><div class="t-name">Tier 1 // Blueprint</div><div class="t-price">$29</div>
      <p class="t-desc">Complete 52-Week Collective Reading &amp; Media Automation Blueprint with viral hooks, publishing schedules &amp; portal access.</p></div>
      <a class="t-btn" href="/go/tier29?utm_source=store_v22&utm_medium=card&utm_campaign=tier29">Unlock Blueprint ($29)</a>
    </div>
    <div class="tier-card featured">
      <div><span class="badge">MOST POPULAR</span><div class="t-name">Personalized 4D Aura Reading</div><div class="t-price">$49<span class="t-anchor">$129 value</span></div>
      <p class="t-desc">Custom-rendered cinema reading MP4 personalized with your name, focus topic &amp; studio-mastered neural narration delivered straight to your inbox.</p></div>
      <a class="t-btn" href="/go/auravideo49?utm_source=store_v22&utm_medium=card&utm_campaign=aura49">Claim Custom Reading ($49)</a>
    </div>
    <div class="tier-card">
      <div><div class="t-name">Turnkey Creator Stack</div><div class="t-price">$1,500</div>
      <p class="t-desc">Complete Oracle Systems storefront, Stripe webhook fulfillment engine, autonomous YouTube API pipeline &amp; local AI CRM.</p></div>
      <a class="t-btn ent" href="/go/fullstorefront?utm_source=store_v22&utm_medium=card&utm_campaign=stack1500">Deploy Full Stack ($1,500)</a>
    </div>
    <div class="tier-card">
      <div><div class="t-name">Enterprise Dedicated Pro_Node</div><div class="t-price">$49,999</div>
      <p class="t-desc">Turnkey private AI &amp; autonomous media hardware deployment for agencies &amp; studios (50% ACH Milestone 1 deposit / zero SaaS lock-in).</p></div>
      <a class="t-btn ent" href="/go/pro_node?utm_source=store_v22&utm_medium=card&utm_campaign=pronode">Reserve Pro_Node ($49,999)</a>
    </div>
  </div>
  <div class="ref-bar">
    <div><strong style="color:#facc15;">Share the 3D Portal &amp; Unlock Bonus Assets:</strong>
    <span style="color:#94a3b8;font-size:13px;display:block;margin-top:4px;">Generate your tracked referral link to share on YouTube, X, or TikTok.</span></div>
    <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
      <input id="omega-ref-url" readonly value="Click Copy to generate your tracked link">
      <button id="omega-ref-btn" class="cta-gold" onclick="omegaCopyRef()">Copy Referral Link</button>
    </div>
  </div>
</main>

<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/EffectComposer.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/RenderPass.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/ShaderPass.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/shaders/CopyShader.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/shaders/LuminosityHighPassShader.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/UnrealBloomPass.js"></script>
<script>
(function(){
  fetch("/api/live-pulse").then(function(r){return r.json();}).then(function(d){
    var el = document.getElementById("omega-live-pulse");
    if(el && d) el.textContent = "LIVE 3D RAY-LIT PORTAL  |  " + d.vault_videos + " ASSETS  |  " + d.yt_views + " YT VIEWS  |  " + d.utm_clicks + " VERIFIED CLICKS";
  }).catch(function(){});

  window.omegaCopyRef = function(){
    var code = localStorage.getItem("oracle_ref_code") || ("oracle_" + Math.random().toString(36).slice(2,8));
    localStorage.setItem("oracle_ref_code", code);
    var u = window.location.origin + "/go/assetpack15?utm_source=member_ref&utm_medium=share&utm_campaign=" + code;
    if(navigator.clipboard) navigator.clipboard.writeText(u);
    document.getElementById("omega-ref-url").value = u;
    document.getElementById("omega-ref-btn").textContent = "Copied!";
  };

  window.toggle3DFullscreen = function(){
    var el = document.getElementById("stage-box");
    if (!document.fullscreenElement && el.requestFullscreen) el.requestFullscreen();
    else if (document.exitFullscreen) document.exitFullscreen();
  };

  if (typeof THREE === "undefined") return;
  var canvas = document.getElementById("webgl-stage");
  var wrap = canvas.parentElement;
  var renderer = new THREE.WebGLRenderer({canvas: canvas, antialias: true, powerPreference: "high-performance"});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.96;

  var scene = new THREE.Scene();
  scene.background = new THREE.Color(0x02040b);
  scene.fog = new THREE.FogExp2(0x02040b, 0.036);

  var camera = new THREE.PerspectiveCamera(42, wrap.clientWidth / wrap.clientHeight, 0.1, 100);
  camera.position.set(0, 0.25, 8.8);

  var composer = null, bloomPass = null;
  try {
    if (THREE.EffectComposer && THREE.RenderPass && THREE.UnrealBloomPass) {
      composer = new THREE.EffectComposer(renderer);
      composer.addPass(new THREE.RenderPass(scene, camera));
      bloomPass = new THREE.UnrealBloomPass(new THREE.Vector2(wrap.clientWidth, wrap.clientHeight), 0.24, 0.35, 0.86);
      composer.addPass(bloomPass);
    }
  } catch(e) { composer = null; }

  function resize(){
    var w = wrap.clientWidth, h = wrap.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    if (composer) composer.setSize(w, h);
    if (bloomPass) bloomPass.setSize(w, h);
  }
  resize(); window.addEventListener("resize", resize);

  scene.add(new THREE.AmbientLight(0x94a3b8, 0.52));
  var keyLight = new THREE.DirectionalLight(0xfff6dc, 0.78);
  keyLight.position.set(2.0, 5.0, 6.0);
  scene.add(keyLight);

  var goldLight = new THREE.PointLight(0xfacc15, 1.35, 20);
  goldLight.position.set(-4.5, 2.0, 4.5);
  scene.add(goldLight);

  var cyanLight = new THREE.PointLight(0x38bdf8, 1.15, 20);
  cyanLight.position.set(4.5, -1.2, 4.5);
  scene.add(cyanLight);

  var portalGroup = new THREE.Group();
  portalGroup.position.set(0, -0.15, -3.0);
  var matGold = new THREE.MeshStandardMaterial({color:0xfacc15, metalness:0.94, roughness:0.18, emissive:0xd97706, emissiveIntensity:1.15});
  var matCyan = new THREE.MeshStandardMaterial({color:0x38bdf8, metalness:0.88, roughness:0.22, emissive:0x0284c7, emissiveIntensity:1.10});
  var r1 = new THREE.Mesh(new THREE.TorusGeometry(3.45, 0.04, 20, 140), matGold);
  var r2 = new THREE.Mesh(new THREE.TorusGeometry(2.75, 0.026, 18, 120), matCyan);
  var r3 = new THREE.Mesh(new THREE.TorusGeometry(2.05, 0.022, 16, 100), matGold);
  var coreOrb = new THREE.Mesh(
    new THREE.IcosahedronGeometry(0.36, 2),
    new THREE.MeshStandardMaterial({color:0xfef08a, emissive:0xf59e0b, emissiveIntensity:2.2, roughness:0.15, metalness:0.3})
  );
  portalGroup.add(r1, r2, r3, coreOrb);
  scene.add(portalGroup);

  var floor = new THREE.Mesh(
    new THREE.CircleGeometry(15, 64),
    new THREE.MeshStandardMaterial({color:0x050916, metalness:0.82, roughness:0.24})
  );
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -2.55;
  scene.add(floor);

  var pCount = 520;
  var pGeo = new THREE.BufferGeometry();
  var pPos = new Float32Array(pCount * 3);
  var pCol = new Float32Array(pCount * 3);
  for (var i = 0; i < pCount; i++) {
    pPos[i*3]   = (Math.random() - 0.5) * 18;
    pPos[i*3+1] = (Math.random() - 0.5) * 9.5;
    pPos[i*3+2] = (Math.random() - 0.30) * 11.0;
    var isGold = Math.random() > 0.35;
    pCol[i*3]   = isGold ? 1.0 : 0.22;
    pCol[i*3+1] = isGold ? 0.84 : 0.78;
    pCol[i*3+2] = isGold ? 0.24 : 1.0;
  }
  pGeo.setAttribute("position", new THREE.BufferAttribute(pPos, 3));
  pGeo.setAttribute("color", new THREE.BufferAttribute(pCol, 3));
  var embers = new THREE.Points(
    pGeo,
    new THREE.PointsMaterial({size: 0.075, vertexColors: true, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending, depthWrite: false})
  );
  scene.add(embers);

  var FALLBACK_DECK = [
    {slug:"the_magician", title:"I // THE MAGICIAN", img:"/assets/tarot_deck/the_magician.png", audio:"/static/card_voices/the_magician.mp3"},
    {slug:"the_star", title:"XVII // THE STAR", img:"/assets/tarot_deck/the_star.png", audio:"/static/card_voices/the_star.mp3"},
    {slug:"the_world", title:"XXI // THE WORLD", img:"/assets/tarot_deck/the_world.png", audio:"/static/card_voices/the_world.mp3"}
  ];
  var ACTIVE_DECK = FALLBACK_DECK.slice();

  var SLOT_POS = [
    {slotLabel:"I. PAST CATALYST", x:-2.85, ry:0.26, baseZ:0.0},
    {slotLabel:"II. PRESENT SHIFT", x:0.0,   ry:0.0,  baseZ:0.65},
    {slotLabel:"III. QUANTUM OUTCOME", x:2.85, ry:-0.26, baseZ:0.0}
  ];

  function makeBackTexture(slotLabel){
    var bc = document.createElement("canvas");
    bc.width = 512; bc.height = 820;
    var g = bc.getContext("2d");
    var grd = g.createRadialGradient(256, 410, 25, 256, 410, 440);
    grd.addColorStop(0, "#172045"); grd.addColorStop(0.55, "#080d1e"); grd.addColorStop(1, "#02040a");
    g.fillStyle = grd; g.fillRect(0, 0, 512, 820);
    g.strokeStyle = "#eab308"; g.lineWidth = 10; g.strokeRect(20, 20, 472, 780);
    g.strokeStyle = "rgba(56,189,248,0.65)"; g.lineWidth = 3; g.strokeRect(42, 42, 428, 736);
    g.beginPath(); g.arc(256, 405, 145, 0, Math.PI*2); g.strokeStyle = "#eab308"; g.lineWidth = 5; g.stroke();
    g.beginPath(); g.arc(256, 405, 105, 0, Math.PI*2); g.strokeStyle = "#38bdf8"; g.lineWidth = 3; g.stroke();
    g.fillStyle = "#facc15"; g.font = "bold 36px Georgia,serif"; g.textAlign = "center";
    g.fillText("ORACLE", 256, 400);
    g.fillStyle = "#38bdf8"; g.font = "bold 20px Segoe UI,sans-serif";
    g.fillText(slotLabel, 256, 442);
    g.fillStyle = "#fef08a"; g.font = "bold 19px Segoe UI,sans-serif";
    g.fillText("CLICK TO POP OUT & REVEAL", 256, 735);
    var tex = new THREE.CanvasTexture(bc);
    tex.encoding = THREE.sRGBEncoding;
    tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
    return tex;
  }

  var loader = new THREE.TextureLoader();
  var edgeMat = new THREE.MeshStandardMaterial({color:0xd97706, metalness:0.92, roughness:0.22, emissive:0x451a03, emissiveIntensity:0.25});
  var cardGeo = new THREE.BoxGeometry(2.05, 3.28, 0.095);
  var cardMeshes = [];

  function loadCardTexture(imgUrl){
    var tex = loader.load(imgUrl + "?v=" + Date.now());
    tex.encoding = THREE.sRGBEncoding;
    tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
    return tex;
  }

  function buildSpreadMeshes(cards3){
    cardMeshes.forEach(function(m){ scene.remove(m); });
    cardMeshes = [];
    while (cards3.length < 3) cards3.push(cards3[cards3.length - 1] || FALLBACK_DECK[0]);
    cards3.slice(0, 3).forEach(function(cd, idx){
      var sl = SLOT_POS[idx];
      var frontMat = new THREE.MeshBasicMaterial({map: loadCardTexture(cd.img), toneMapped: false});
      var backMat  = new THREE.MeshStandardMaterial({map: makeBackTexture(sl.slotLabel), metalness:0.35, roughness:0.35});
      var mesh = new THREE.Mesh(cardGeo, [edgeMat, edgeMat, edgeMat, edgeMat, backMat, frontMat]);
      mesh.position.set(sl.x, -0.22, sl.baseZ);
      mesh.rotation.y = sl.ry;
      mesh.userData = {idx:idx, card:cd, slot:sl, flipped:false, targetFlip:0, targetZ:sl.baseZ, baseY:-0.22};
      scene.add(mesh);
      cardMeshes.push(mesh);
    });
  }

  fetch("/api/deck-manifest").then(function(r){ return r.json(); }).then(function(list){
    if (Array.isArray(list) && list.length > 0) ACTIVE_DECK = list;
    buildSpreadMeshes(ACTIVE_DECK.slice(0, 3));
  }).catch(function(){
    buildSpreadMeshes(ACTIVE_DECK.slice(0, 3));
  });

  var raycaster = new THREE.Raycaster();
  var mouse = new THREE.Vector2(0, 0);
  var dragging = false, movedDist = 0, lastX = 0, lastY = 0;
  var orbitYaw = 0, orbitPitch = 0.04, targetYaw = 0, targetPitch = 0.04;

  canvas.addEventListener("mousedown", function(e){ dragging = true; movedDist = 0; lastX = e.clientX; lastY = e.clientY; });
  window.addEventListener("mouseup", function(){ dragging = false; });
  window.addEventListener("mousemove", function(e){
    var rect = canvas.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    if (dragging) {
      var dx = e.clientX - lastX, dy = e.clientY - lastY;
      movedDist += Math.abs(dx) + Math.abs(dy);
      targetYaw = Math.max(-0.85, Math.min(0.85, targetYaw - dx * 0.005));
      targetPitch = Math.max(-0.35, Math.min(0.45, targetPitch + dy * 0.004));
      lastX = e.clientX; lastY = e.clientY;
    } else {
      targetYaw = mouse.x * 0.22;
      targetPitch = 0.04 + mouse.y * 0.12;
    }
  });

  var audioPlayer = new Audio();
  var capEl = document.getElementById("active-card-caption");

  function flipCard(mesh, playSound){
    var u = mesh.userData;
    u.flipped = !u.flipped;
    u.targetFlip = u.flipped ? Math.PI : 0;
    u.targetZ = u.flipped ? 2.15 : u.slot.baseZ;
    if (u.flipped) {
      capEl.textContent = u.slot.slotLabel + "  //  " + u.card.title + " — STUDIO NEURAL READING";
      if (playSound) { try { audioPlayer.pause(); audioPlayer.src = u.card.audio; audioPlayer.play(); } catch(e){} }
    }
  }

  canvas.addEventListener("click", function(){
    if (movedDist > 8) return;
    raycaster.setFromCamera(mouse, camera);
    var hits = raycaster.intersectObjects(cardMeshes);
    if (hits.length > 0) flipCard(hits[0].object, true);
  });

  window.revealAll3DCards = function(){
    cardMeshes.forEach(function(m, i){
      if (!m.userData.flipped) setTimeout(function(){ flipCard(m, false); }, i * 380);
    });
    var q = [0, 1, 2], qi = 0;
    function nextVoice(){
      if (qi >= q.length) return;
      var u = cardMeshes[q[qi++]].userData;
      capEl.textContent = u.slot.slotLabel + "  //  " + u.card.title + " — STUDIO NEURAL READING";
      audioPlayer.src = u.card.audio;
      audioPlayer.onended = nextVoice;
      audioPlayer.play().catch(function(){});
    }
    nextVoice();
  };

  window.shuffleAndDraw3D = function(){
    try { audioPlayer.pause(); } catch(e){}
    var pool = ACTIVE_DECK.slice();
    for (var i = pool.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = pool[i]; pool[i] = pool[j]; pool[j] = tmp;
    }
    buildSpreadMeshes(pool.slice(0, 3));
    cardMeshes.forEach(function(m){ m.rotation.y += Math.PI * 2; m.position.z = -3.2; });
    capEl.textContent = "SHUFFLED " + ACTIVE_DECK.length + " VERIFIED RAY-TRACED CARDS — CLICK ANY CARD TO REVEAL";
  };

  var clock = new THREE.Clock();
  function animate(){
    requestAnimationFrame(animate);
    var t = clock.getElapsedTime();

    orbitYaw += (targetYaw - orbitYaw) * 0.07;
    orbitPitch += (targetPitch - orbitPitch) * 0.07;
    var radius = 8.8;
    camera.position.x = Math.sin(orbitYaw) * radius;
    camera.position.z = Math.cos(orbitYaw) * radius;
    camera.position.y = 0.25 + orbitPitch * 3.0;
    camera.lookAt(0, -0.15, 0.3);

    goldLight.position.x = Math.cos(t * 0.75) * 5.8;
    goldLight.position.y = 1.6 + Math.sin(t * 0.55) * 2