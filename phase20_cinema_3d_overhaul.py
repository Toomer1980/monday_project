import glob
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import time
import urllib.request

from PIL import Image

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
os.chdir(PDIR)
DECK_DIR = os.path.join(PDIR, "assets", "tarot_deck")
STATIC_DIR = os.path.join(PDIR, "static")
os.makedirs(DECK_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)


# ==============================================================================
# 1. AUTO-NORMALIZE ALL SAVED RAY-TRACED CARDS (.jpg/.jpeg/.webp -> .png)
# ==============================================================================
def normalize_deck_images():
    """Finds any .jpg/.jpeg/.webp/.png card saved in assets\\tarot_deck or Downloads and converts to clean .png."""
    aliases = {
        "the_sun": ["the_sun", "sun", "xix", "the sun", "e083d4c2"],
        "the_magician": ["the_magician", "magician", "the magician"],
        "wheel_of_fortune": ["wheel_of_fortune", "wheel", "wheel of fortune"],
        "the_star": ["the_star", "star", "the star"],
        "the_world": ["the_world", "world", "the world"],
        "the_empress": ["the_empress", "empress"],
        "the_emperor": ["the_emperor", "emperor"],
        "ace_of_pentacles": ["ace_of_pentacles", "pentacles"],
        "the_high_priestess": ["the_high_priestess", "high_priestess"],
        "the_chariot": ["the_chariot", "chariot"],
    }
    dl_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    converted = []

    for slug, names in aliases.items():
        dst_png = os.path.join(DECK_DIR, f"{slug}.png")
        for search_dir in (DECK_DIR, dl_dir):
            if not os.path.exists(search_dir):
                continue
            for ext in ("*.jpg", "*.jpeg", "*.webp", "*.png"):
                for fp in glob.glob(os.path.join(search_dir, ext)):
                    base = os.path.splitext(os.path.basename(fp))[0].lower().replace("-", "_").strip()
                    base_us = base.replace(" ", "_")
                    if base in names or base_us in names:
                        if os.path.abspath(fp) == os.path.abspath(dst_png):
                            continue
                        try:
                            im = Image.open(fp).convert("RGB")
                            im.save(dst_png, "PNG", optimize=True)
                            converted.append((slug, os.path.basename(fp)))
                            if search_dir == DECK_DIR:
                                os.remove(fp)
                        except Exception as ex:
                            print(f"[WARN] Could not convert {fp}: {ex}")

    print(f"[1/4] Deck normalizer finished | Converted/imported {len(converted)} file(s): {converted}")
    present = [f for f in sorted(os.listdir(DECK_DIR)) if f.lower().endswith(".png")]
    print(f"      Active .png deck files ({len(present)}): {', '.join(present)}")


# ==============================================================================
# 2. UPGRADE THREE.JS WEBGL STAGE WITH UNREALBLOOMPASS + DRAG-ORBIT + SHUFFLE DRAW
# ==============================================================================
def install_phase20_webgl_bloom_store():
    store_html_path = os.path.join(STATIC_DIR, "oracle_webgl_store.html")
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Oracle Systems LLC // Sovereign 3D Ray-Lit Cinema Portal</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:#02040a;color:#e2e8f0;font-family:"Segoe UI",system-ui,-apple-system,sans-serif;overflow-x:hidden;}
  .top-nav{position:sticky;top:0;z-index:50;display:flex;justify-content:space-between;align-items:center;padding:14px 32px;background:rgba(2,4,10,0.84);backdrop-filter:blur(16px);border-bottom:1px solid rgba(250,204,21,0.24);}
  .brand{font-weight:900;letter-spacing:2.4px;font-size:13px;color:#facc15;}
  .nav-links a{color:#cbd5e1;text-decoration:none;margin-left:22px;font-size:13px;font-weight:600;transition:color .2s;}
  .nav-links a:hover{color:#facc15;}
  .stage-wrap{position:relative;width:100%;height:720px;background:radial-gradient(ellipse at 50% 45%,#101733 0%,#040712 58%,#010206 100%);border-bottom:1px solid rgba(250,204,21,0.32);overflow:hidden;user-select:none;}
  #webgl-stage{position:absolute;inset:0;width:100%;height:100%;cursor:grab;}
  #webgl-stage:active{cursor:grabbing;}
  .stage-hud-top{position:absolute;top:16px;left:0;right:0;text-align:center;pointer-events:none;z-index:10;padding:0 16px;}
  .pulse-pill{display:inline-block;padding:5px 14px;border-radius:999px;background:rgba(16,185,129,0.14);border:1px solid rgba(16,185,129,0.45);color:#6ee7b7;font-size:11px;font-weight:700;letter-spacing:1.5px;margin-bottom:6px;}
  .stage-hud-top h1{font-size:32px;font-weight:900;letter-spacing:-0.4px;background:linear-gradient(90deg,#fef08a,#facc15,#38bdf8,#fef08a);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
  .stage-hud-top p{color:#94a3b8;font-size:13px;margin-top:4px;}
  .stage-hud-bottom{position:absolute;bottom:18px;left:0;right:0;display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:10px;z-index:10;padding:0 16px;}
  .cta-gold{cursor:pointer;padding:11px 20px;border:none;border-radius:9px;font-weight:800;font-size:13px;background:linear-gradient(90deg,#facc15,#f59e0b,#38bdf8);color:#040712;box-shadow:0 8px 28px rgba(250,204,21,0.36);text-decoration:none;transition:transform .18s;}
  .cta-gold:hover{transform:translateY(-2px);}
  .cta-glass{cursor:pointer;padding:11px 18px;border:1px solid rgba(56,189,248,0.55);border-radius:9px;font-weight:700;font-size:13px;background:rgba(8,14,30,0.82);color:#e2e8f0;backdrop-filter:blur(8px);text-decoration:none;transition:all .18s;}
  .cta-glass:hover{border-color:#facc15;color:#facc15;}
  #active-card-caption{position:absolute;bottom:70px;left:50%;transform:translateX(-50%);z-index:10;padding:7px 20px;border-radius:999px;background:rgba(4,7,18,0.88);border:1px solid rgba(250,204,21,0.5);color:#fef08a;font-size:12.5px;font-weight:700;letter-spacing:0.6px;white-space:nowrap;pointer-events:none;max-width:92vw;overflow:hidden;text-overflow:ellipsis;}
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

<section class="stage-wrap">
  <div class="stage-hud-top">
    <div id="omega-live-pulse" class="pulse-pill">LIVE GPU WEBGL + UNREAL BLOOM 3D ENGINE // STRIPE LIVE</div>
    <h1>Live 3D Ray-Lit Tarot Portal &amp; Sovereign AI Compute</h1>
    <p>Drag to orbit in 3D space. Click any floating card to pop it forward with bloom lighting &amp; studio neural voice.</p>
  </div>
  <canvas id="webgl-stage"></canvas>
  <div id="active-card-caption">DRAG TO ORBIT 3D STAGE  |  CLICK ANY CARD TO POP OUT &amp; REVEAL</div>
  <div class="stage-hud-bottom">
    <button class="cta-gold" onclick="window.revealAll3DCards()">Reveal 3D Spread + Studio Voice</button>
    <button class="cta-glass" onclick="window.shuffleAndDraw3D()">Shuffle Deck &amp; Draw 3 New Cards</button>
    <a class="cta-glass" href="/go/auravideo49?utm_source=webgl_bloom&utm_medium=hero&utm_campaign=cinema_v20">Order Custom 4D Aura ($49)</a>
    <a class="cta-glass" href="/go/assetpack15?utm_source=webgl_bloom&utm_medium=hero&utm_campaign=cinema_v20">Instant Asset Pack ($15)</a>
  </div>
</section>

<main class="container">
  <div class="sec-kicker">STRIPE-VERIFIED INSTANT FULFILLMENT</div>
  <h2 class="sec-title">Select Your Sovereign Tier</h2>
  <div class="tier-grid">
    <div class="tier-card featured">
      <div>
        <span class="badge">FASTEST START</span>
        <div class="t-name">Creator Asset Pack</div>
        <div class="t-price">$15<span class="t-anchor">$49 value</span></div>
        <p class="t-desc">Commercial-use instant ZIP: seamless 16:9 &amp; 9:16 4D motion loops, celestial overlays &amp; high-res templates for YouTube, TikTok &amp; OBS.</p>
      </div>
      <a class="t-btn" href="/go/assetpack15?utm_source=store_v20&utm_medium=card&utm_campaign=tier15">Unlock Instant Pack ($15)</a>
    </div>
    <div class="tier-card featured">
      <div>
        <span class="badge">RECURRING VAULT</span>
        <div class="t-name">Sovereign Member Vault</div>
        <div class="t-price">$15/mo<span class="t-anchor">$39/mo</span></div>
        <p class="t-desc">Unlimited access to full multi-chapter collective readings, ad-free 432Hz studio audio drops &amp; priority member portal releases.</p>
      </div>
      <a class="t-btn" href="/go/vaultsub15?utm_source=store_v20&utm_medium=card&utm_campaign=vault15">Join Member Vault ($15/mo)</a>
    </div>
    <div class="tier-card">
      <div>
        <div class="t-name">Tier 1 // Blueprint</div>
        <div class="t-price">$29</div>
        <p class="t-desc">Complete 52-Week Collective Reading &amp; Media Automation Blueprint with viral hooks, publishing schedules &amp; portal access.</p>
      </div>
      <a class="t-btn" href="/go/tier29?utm_source=store_v20&utm_medium=card&utm_campaign=tier29">Unlock Blueprint ($29)</a>
    </div>
    <div class="tier-card featured">
      <div>
        <span class="badge">MOST POPULAR</span>
        <div class="t-name">Personalized 4D Aura Reading</div>
        <div class="t-price">$49<span class="t-anchor">$129 value</span></div>
        <p class="t-desc">Custom-rendered cinema reading MP4 personalized with your name, focus topic &amp; studio-mastered neural narration delivered straight to your inbox.</p>
      </div>
      <a class="t-btn" href="/go/auravideo49?utm_source=store_v20&utm_medium=card&utm_campaign=aura49">Claim Custom Reading ($49)</a>
    </div>
    <div class="tier-card">
      <div>
        <div class="t-name">Turnkey Creator Stack</div>
        <div class="t-price">$1,500</div>
        <p class="t-desc">Complete Oracle Systems storefront, Stripe webhook fulfillment engine, autonomous YouTube API pipeline &amp; local AI CRM.</p>
      </div>
      <a class="t-btn ent" href="/go/fullstorefront?utm_source=store_v20&utm_medium=card&utm_campaign=stack1500">Deploy Full Stack ($1,500)</a>
    </div>
    <div class="tier-card">
      <div>
        <div class="t-name">Enterprise Dedicated Pro_Node</div>
        <div class="t-price">$49,999</div>
        <p class="t-desc">Turnkey private AI &amp; autonomous media hardware deployment for agencies &amp; studios (50% ACH Milestone 1 deposit / zero SaaS lock-in).</p>
      </div>
      <a class="t-btn ent" href="/go/pro_node?utm_source=store_v20&utm_medium=card&utm_campaign=pronode">Reserve Pro_Node ($49,999)</a>
    </div>
  </div>

  <div class="ref-bar">
    <div>
      <strong style="color:#facc15;">Share the 3D Portal &amp; Unlock Bonus Assets:</strong>
      <span style="color:#94a3b8;font-size:13px;display:block;margin-top:4px;">Generate your tracked referral link to share on YouTube, X, or TikTok.</span>
    </div>
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
    if(el && d) el.textContent = "LIVE GPU 3D + UNREAL BLOOM  |  " + d.vault_videos + " STUDIO ASSETS  |  " + d.yt_views + " YT VIEWS  |  " + d.utm_clicks + " VERIFIED CLICKS";
  }).catch(function(){});

  window.omegaCopyRef = function(){
    var code = localStorage.getItem("oracle_ref_code") || ("oracle_" + Math.random().toString(36).slice(2,8));
    localStorage.setItem("oracle_ref_code", code);
    var u = window.location.origin + "/go/assetpack15?utm_source=member_ref&utm_medium=share&utm_campaign=" + code;
    if(navigator.clipboard) navigator.clipboard.writeText(u);
    document.getElementById("omega-ref-url").value = u;
    document.getElementById("omega-ref-btn").textContent = "Copied!";
  };

  if (typeof THREE === "undefined") return;
  var canvas = document.getElementById("webgl-stage");
  var wrap = canvas.parentElement;
  var renderer = new THREE.WebGLRenderer({canvas: canvas, antialias: true, powerPreference: "high-performance"});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;

  var scene = new THREE.Scene();
  scene.background = new THREE.Color(0x03050d);
  scene.fog = new THREE.FogExp2(0x03050d, 0.038);

  var camera = new THREE.PerspectiveCamera(42, wrap.clientWidth / wrap.clientHeight, 0.1, 100);
  camera.position.set(0, 0.25, 8.8);

  var composer = null, bloomPass = null;
  try {
    if (THREE.EffectComposer && THREE.RenderPass && THREE.UnrealBloomPass) {
      composer = new THREE.EffectComposer(renderer);
      composer.addPass(new THREE.RenderPass(scene, camera));
      bloomPass = new THREE.UnrealBloomPass(new THREE.Vector2(wrap.clientWidth, wrap.clientHeight), 0.62, 0.48, 0.34);
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

  scene.add(new THREE.AmbientLight(0x475569, 1.45));
  var keyLight = new THREE.DirectionalLight(0xfff4d2, 2.0);
  keyLight.position.set(2.5, 5.5, 6.5);
  scene.add(keyLight);

  var goldLight = new THREE.PointLight(0xfacc15, 4.2, 22);
  goldLight.position.set(-4.5, 2.2, 4.8);
  scene.add(goldLight);

  var cyanLight = new THREE.PointLight(0x38bdf8, 3.6, 22);
  cyanLight.position.set(4.5, -1.6, 4.8);
  scene.add(cyanLight);

  var violetLight = new THREE.PointLight(0xa855f7, 2.2, 20);
  violetLight.position.set(0, 3.5, -2.5);
  scene.add(violetLight);

  var portalGroup = new THREE.Group();
  portalGroup.position.set(0, -0.15, -2.8);
  var matGold = new THREE.MeshStandardMaterial({color:0xfacc15, metalness:0.95, roughness:0.16, emissive:0x854d0e, emissiveIntensity:0.55});
  var matCyan = new THREE.MeshStandardMaterial({color:0x38bdf8, metalness:0.90, roughness:0.20, emissive:0x0284c7, emissiveIntensity:0.65});
  var r1 = new THREE.Mesh(new THREE.TorusGeometry(3.45, 0.045, 20, 140), matGold);
  var r2 = new THREE.Mesh(new THREE.TorusGeometry(2.75, 0.030, 18, 120), matCyan);
  var r3 = new THREE.Mesh(new THREE.TorusGeometry(2.05, 0.025, 16, 100), matGold);
  var coreOrb = new THREE.Mesh(
    new THREE.IcosahedronGeometry(0.42, 2),
    new THREE.MeshStandardMaterial({color:0xfef08a, emissive:0xf59e0b, emissiveIntensity:1.7, roughness:0.15, metalness:0.4})
  );
  portalGroup.add(r1, r2, r3, coreOrb);
  scene.add(portalGroup);

  var floor = new THREE.Mesh(
    new THREE.CircleGeometry(15, 64),
    new THREE.MeshStandardMaterial({color:0x050918, metalness:0.85, roughness:0.22})
  );
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -2.55;
  scene.add(floor);

  var pCount = 650;
  var pGeo = new THREE.BufferGeometry();
  var pPos = new Float32Array(pCount * 3);
  var pCol = new Float32Array(pCount * 3);
  for (var i = 0; i < pCount; i++) {
    pPos[i*3]   = (Math.random() - 0.5) * 18;
    pPos[i*3+1] = (Math.random() - 0.5) * 9.5;
    pPos[i*3+2] = (Math.random() - 0.30) * 11.0;
    var isGold = Math.random() > 0.32;
    pCol[i*3]   = isGold ? 1.0 : 0.20;
    pCol[i*3+1] = isGold ? 0.84 : 0.80;
    pCol[i*3+2] = isGold ? 0.22 : 1.0;
  }
  pGeo.setAttribute("position", new THREE.BufferAttribute(pPos, 3));
  pGeo.setAttribute("color", new THREE.BufferAttribute(pCol, 3));
  var embers = new THREE.Points(
    pGeo,
    new THREE.PointsMaterial({size: 0.085, vertexColors: true, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false})
  );
  scene.add(embers);

  var FULL_DECK = [
    {slug:"the_magician", title:"I // THE MAGICIAN", msg:"Sovereign creation and skill convergence activated.", audio:"/static/card_voices/card_past.mp3"},
    {slug:"wheel_of_fortune", title:"X // WHEEL OF FORTUNE", msg:"Sudden upward cycle shift and windfall opening.", audio:"/static/card_voices/card_present.mp3"},
    {slug:"the_sun", title:"XIX // THE SUN", msg:"Unstoppable abundance, clarity, and magnetic power.", audio:"/static/card_voices/card_future.mp3"},
    {slug:"the_star", title:"XVII // THE STAR", msg:"Divine alignment, vision, and restored momentum.", audio:"/static/card_voices/card_past.mp3"},
    {slug:"the_world", title:"XXI // THE WORLD", msg:"Complete realm expansion and cycle mastery.", audio:"/static/card_voices/card_future.mp3"}
  ];

  var SLOT_POS = [
    {slotLabel:"I. PAST CATALYST", x:-2.85, ry:0.28, baseZ:0.0},
    {slotLabel:"II. PRESENT SHIFT", x:0.0,   ry:0.0,  baseZ:0.65},
    {slotLabel:"III. QUANTUM OUTCOME", x:2.85, ry:-0.28, baseZ:0.0}
  ];

  function makeBackTexture(slotLabel){
    var bc = document.createElement("canvas");
    bc.width = 512; bc.height = 820;
    var g = bc.getContext("2d");
    var grd = g.createRadialGradient(256, 410, 25, 256, 410, 440);
    grd.addColorStop(0, "#1e295a"); grd.addColorStop(0.55, "#090f24"); grd.addColorStop(1, "#02040a");
    g.fillStyle = grd; g.fillRect(0, 0, 512, 820);
    g.strokeStyle = "#facc15"; g.lineWidth = 12; g.strokeRect(20, 20, 472, 780);
    g.strokeStyle = "rgba(56,189,248,0.75)"; g.lineWidth = 3; g.strokeRect(42, 42, 428, 736);
    g.beginPath(); g.arc(256, 405, 150, 0, Math.PI*2); g.strokeStyle = "#facc15"; g.lineWidth = 5; g.stroke();
    g.beginPath(); g.arc(256, 405, 108, 0, Math.PI*2); g.strokeStyle = "#38bdf8"; g.lineWidth = 3; g.stroke();
    g.fillStyle = "#facc15"; g.font = "bold 36px Georgia,serif"; g.textAlign = "center";
    g.fillText("ORACLE", 256, 400);
    g.fillStyle = "#38bdf8"; g.font = "bold 20px Segoe UI,sans-serif";
    g.fillText(slotLabel, 256, 442);
    g.fillStyle = "#fef08a"; g.font = "bold 19px Segoe UI,sans-serif";
    g.fillText("CLICK TO POP OUT & REVEAL", 256, 735);
    var tex = new THREE.CanvasTexture(bc);
    tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
    return tex;
  }

  var loader = new THREE.TextureLoader();
  var edgeMat = new THREE.MeshStandardMaterial({color:0xfacc15, metalness:0.98, roughness:0.12, emissive:0x78350f, emissiveIntensity:0.55});
  var cardGeo = new THREE.BoxGeometry(2.05, 3.28, 0.095);
  var cardMeshes = [];

  function loadCardTexture(slug){
    var tex = loader.load("/assets/tarot_deck/" + slug + ".png?v=" + Date.now());
    tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
    return tex;
  }

  function buildSpreadMeshes(cards3){
    cardMeshes.forEach(function(m){ scene.remove(m); });
    cardMeshes = [];
    cards3.forEach(function(cd, idx){
      var sl = SLOT_POS[idx];
      var frontMat = new THREE.MeshStandardMaterial({map: loadCardTexture(cd.slug), metalness:0.20, roughness:0.24});
      var backMat  = new THREE.MeshStandardMaterial({map: makeBackTexture(sl.slotLabel), metalness:0.45, roughness:0.25});
      var mesh = new THREE.Mesh(cardGeo, [edgeMat, edgeMat, edgeMat, edgeMat, backMat, frontMat]);
      mesh.position.set(sl.x, -0.22, sl.baseZ);
      mesh.rotation.y = sl.ry;
      var aura = new THREE.Mesh(
        new THREE.PlaneGeometry(2.34, 3.58),
        new THREE.MeshBasicMaterial({color: idx === 1 ? 0xfacc15 : 0x38bdf8, transparent:true, opacity:0.16, side:THREE.DoubleSide, blending:THREE.AdditiveBlending})
      );
      aura.position.z = -0.06;
      mesh.add(aura);
      mesh.userData = {idx:idx, card:cd, slot:sl, flipped:false, targetFlip:0, targetZ:sl.baseZ, baseY:-0.22};
      scene.add(mesh);
      cardMeshes.push(mesh);
    });
  }
  buildSpreadMeshes([FULL_DECK[0], FULL_DECK[1], FULL_DECK[2]]);

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
      targetYaw = mouse.x * 0.24;
      targetPitch = 0.04 + mouse.y * 0.14;
    }
  });

  var audioPlayer = new Audio();
  var capEl = document.getElementById("active-card-caption");

  function flipCard(mesh, playSound){
    var u = mesh.userData;
    u.flipped = !u.flipped;
    u.targetFlip = u.flipped ? Math.PI : 0;
    u.targetZ = u.flipped ? 2.10 : u.slot.baseZ;
    if (u.flipped) {
      capEl.textContent = u.slot.slotLabel + "  //  " + u.card.title + " — " + u.card.msg;
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
      capEl.textContent = u.slot.slotLabel + "  //  " + u.card.title + " — " + u.card.msg;
      audioPlayer.src = u.card.audio;
      audioPlayer.onended = nextVoice;
      audioPlayer.play().catch(function(){});
    }
    nextVoice();
  };

  window.shuffleAndDraw3D = function(){
    try { audioPlayer.pause(); } catch(e){}
    var pool = FULL_DECK.slice();
    for (var i = pool.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = pool[i]; pool[i] = pool[j]; pool[j] = tmp;
    }
    buildSpreadMeshes(pool.slice(0, 3));
    cardMeshes.forEach(function(m){ m.rotation.y += Math.PI * 2; m.position.z = -3.2; });
    capEl.textContent = "SHUFFLED RAY-TRACED DECK — CLICK ANY FLOATING 3D CARD TO REVEAL";
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
    goldLight.position.y = 1.6 + Math.sin(t * 0.55) * 2.2;
    cyanLight.position.x = Math.sin(t * 0.65) * 5.8;
    coreOrb.rotation.y = t * 0.8; coreOrb.rotation.x = t * 0.5;

    r1.rotation.x = t * 0.22; r1.rotation.y = t * 0.26;
    r2.rotation.x = -t * 0.28; r2.rotation.z = t * 0.16;
    r3.rotation.y = -t * 0.36;

    var arr = embers.geometry.attributes.position.array;
    for (var i = 0; i < pCount; i++) {
      arr[i*3+1] += 0.0055;
      arr[i*3+2] += 0.011;
      if (arr[i*3+2] > 7.8 || arr[i*3+1] > 5.0) {
        arr[i*3+1] = -4.6;
        arr[i*3+2] = -3.8;
      }
    }
    embers.geometry.attributes.position.needsUpdate = true;

    raycaster.setFromCamera(mouse, camera);
    var hits = raycaster.intersectObjects(cardMeshes);
    var hoverObj = hits.length ? hits[0].object : null;

    cardMeshes.forEach(function(m, i){
      var u = m.userData;
      var isH = (m === hoverObj);
      var goalZ = u.targetZ + (isH ? 0.55 : 0);
      m.position.z += (goalZ - m.position.z) * 0.095;
      m.position.y = u.baseY + Math.sin(t * 1.5 + i * 1.4) * 0.11;
      var goalRy = u.slot.ry + u.targetFlip;
      m.rotation.y += (goalRy - m.rotation.y) * 0.10;
      var goalRx = isH ? -mouse.y * 0.20 : 0;
      m.rotation.x += (goalRx - m.rotation.x) * 0.08;
    });

    if (composer) composer.render(); else renderer.render(scene, camera);
  }
  animate();
})();
</script>
</body>
</html>
"""
    open(store_html_path, "w", encoding="utf-8", newline="").write(html)
    print(f"[2/4] Upgraded {store_html_path} (UnrealBloomPass + Drag-Orbit + Full-Deck Shuffle Draw)")


# ==============================================================================
# 3. UPGRADE 7-CHAPTER ZERO-LOOP VIDEO RENDERER WITH 3D PERSPECTIVE TILT + REAL CARDS
# ==============================================================================
def upgrade_video_renderer_3d_raytraced():
    engine_path = os.path.join(PDIR, "Modules", "render_real_full_reading.py")
    lines = [
        "import argparse, asyncio, datetime as dt, json, math, os, random, re, subprocess, sys, time, urllib.request",
        "import numpy as np",
        "from PIL import Image, ImageDraw, ImageFilter, ImageFont",
        "",
        'PDIR = r"C:\\Users\\toome\\Desktop\\SovereignCore"',
        'DECK_DIR = os.path.join(PDIR, "assets", "tarot_deck")',
        'OUT_DIR = os.path.join(PDIR, "Content_Vault_4D_Full")',
        'THUMB_DIR = os.path.join(PDIR, "Content_Vault_4D_Thumbnails")',
        'WORK_DIR = os.path.join(PDIR, "logs", "real_reading_work")',
        "for _d in (OUT_DIR, THUMB_DIR, WORK_DIR): os.makedirs(_d, exist_ok=True)",
        "",
        "DECK_META = [",
        '    ("the_magician", "THE MAGICIAN", "sovereign creation, skill convergence, and turning vision into tangible structure"),',
        '    ("wheel_of_fortune", "WHEEL OF FORTUNE", "a sudden upward shift in timing, unexpected financial openings, and destiny turning in your favor"),',
        '    ("the_star", "THE STAR", "deep clarity after static, restored confidence, and unmistakable alignment with your true direction"),',
        '    ("the_sun", "THE SUN", "radiant visibility, unstoppable abundance, and breakthroughs that can no longer stay hidden"),',
        '    ("the_world", "THE WORLD", "completing an exhausting cycle and stepping into a higher realm of ownership and freedom"),',
        "]",
        "",
        "def load_font(size):",
        '    for p in (r"C:\\Windows\\Fonts\\georgiab.ttf", r"C:\\Windows\\Fonts\\segoeuib.ttf", r"C:\\Windows\\Fonts\\arialbd.ttf"):',
        "        if os.path.exists(p):",
        "            try: return ImageFont.truetype(p, size)",
        "            except Exception: pass",
        "    return ImageFont.load_default()",
        "",
        "def find_card_image(slug):",
        '    for ext in (".png", ".jpg", ".jpeg", ".webp"):',
        "        fp = os.path.join(DECK_DIR, slug + ext)",
        "        if os.path.exists(fp): return fp",
        '    return ""',
        "",
        "def perspective_tilt(img_rgba, tilt_dir=0):",
        "    w, h = img_rgba.size",
        "    if tilt_dir == 0: return img_rgba",
        "    dy = int(h * 0.055)",
        "    dst = [(0, dy), (w, 0), (w, h), (0, h - dy)] if tilt_dir < 0 else [(0, 0), (w, dy), (w, h - dy), (0, h)]",
        "    src = [(0, 0), (w, 0), (w, h), (0, h)]",
        "    m = []",
        "    for (x, y), (u, v) in zip(dst, src):",
        "        m.append([x, y, 1, 0, 0, 0, -u * x, -u * y])",
        "        m.append([0, 0, 0, x, y, 1, -v * x, -v * y])",
        "    coeffs = np.linalg.solve(np.array(m, dtype=np.float64), np.array([c for pt in src for c in pt], dtype=np.float64))",
        "    return img_rgba.transform((w, h), Image.Transform.PERSPECTIVE, coeffs.tolist(), Image.Resampling.BICUBIC)",
        "",
        "def ollama_expand_chapter(topic, ch_title, card_name, card_meaning, target_words):",
        "    try:",
        '        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as r:',
        '            models = [m.get("name", "") for m in json.loads(r.read().decode("utf-8")).get("models", [])]',
        '        usable = [m for m in models if not any(b in m.lower() for b in (":0.5b", ":1b", ":1.5b", "tinyllama"))]',
        "        if usable:",
        '            prompt = f"You are a calm, authoritative tarot reader delivering a spoken collective reading on \'{topic}\'. Write approximately {target_words} words of continuous spoken narration for \'{ch_title}\' focusing on \'{card_name}\' ({card_meaning}). Warm second-person prose. No stage directions, no markdown, no bullets, no repetition."',
        '            payload = json.dumps({"model": usable[0], "prompt": prompt, "stream": False, "options": {"temperature": 0.72, "repeat_penalty": 1.22, "num_predict": int(target_words * 1.6)}}).encode("utf-8")',
        '            req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=payload, headers={"Content-Type": "application/json"}, method="POST")',
        "            with urllib.request.urlopen(req, timeout=120) as resp:",
        '                txt = re.sub(r"[#*`_]", "", json.loads(resp.read().decode("utf-8")).get("response", "").strip())',
        "                if len(txt.split()) >= max(55, int(target_words * 0.45)): return txt",
        "    except Exception: pass",
        '    return f"Take a slow, steady breath as we step into {ch_title} in this collective reading on {topic}. Look closely at the luminous card rising forward right now: {card_name}, carrying the direct frequency of {card_meaning}. Notice how sharply this energy separates your next chapter from every cycle of hesitation you outgrew. When {card_name} claims this position, it confirms that the groundwork you built in silence is now locking into visible results. Trust the clearest move directly in front of you this week, protect your focus, and watch alignment accelerate as we illuminate the next card in your spread."',
        "",
        "def synth_voice(text, out_mp3):",
        "    import edge_tts",
        '    voices = ["en-US-AndrewMultilingualNeural", "en-US-BrianMultilingualNeural", "en-US-ChristopherNeural"]',
        "    last_err = None",
        "    for i in range(4):",
        "        v = voices[i % len(voices)]",
        "        try:",
        "            if os.path.exists(out_mp3): os.remove(out_mp3)",
        '            async def _run(vn=v): await edge_tts.Communicate(text, voice=vn, rate="-6%", pitch="-2Hz").save(out_mp3)',
        "            asyncio.run(_run())",
        "            if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 1500:",
        "                time.sleep(1.5); return v",
        "        except Exception as ex:",
        "            last_err = ex; time.sleep(2.5 * (i + 1))",
        '    raise RuntimeError(f"TTS failed: {last_err}")',
        "",
        "def get_audio_duration(path):",
        '    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path], capture_output=True, text=True)',
        "    try: return max(4.0, float(r.stdout.strip()))",
        "    except Exception: return 12.0",
        "",
        "def compose_3d_cinema_scene(out_png, topic, ch_label, active_cards, focus_idx):",
        "    w, h = 1920, 1080",
        "    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)",
        "    dx, dy = (xx - w * 0.5) / (w * 0.5), (yy - h * 0.45) / (h * 0.5)",
        "    rad = np.sqrt(dx * dx + dy * dy)",
        "    r = np.clip(5 + 46 * np.exp(-rad * 2.1) + 30 * np.exp(-((dx * 1.4) ** 2 + (dy * 1.4) ** 2) * 3.0), 0, 255)",
        "    g = np.clip(8 + 38 * np.exp(-rad * 2.0) + 24 * np.exp(-((dx - 0.3) ** 2 + dy ** 2) * 2.6), 0, 255)",
        "    b = np.clip(20 + 66 * np.exp(-rad * 1.7) + 34 * np.exp(-((dx + 0.3) ** 2 + dy ** 2) * 2.4), 0, 255)",
        '    stage = Image.fromarray(np.stack([r, g, b], axis=-1).astype(np.uint8), mode="RGB").convert("RGBA")',
        "    rng = random.Random(ch_label)",
        '    em_bg = Image.new("RGBA", (w, h), (0, 0, 0, 0))',
        "    ed = ImageDraw.Draw(em_bg)",
        "    for _ in range(120):",
        "        ex, ey, er = rng.randint(40, w - 40), rng.randint(120, h - 150), rng.choice([2, 3, 4, 6])",
        "        col = (250, 204, 21, rng.randint(85, 210)) if rng.random() > 0.35 else (56, 228, 255, rng.randint(75, 195))",
        "        ed.ellipse([ex - er, ey - er, ex + er, ey + er], fill=col)",
        "    stage = Image.alpha_composite(stage, em_bg.filter(ImageFilter.GaussianBlur(radius=1.8)))",
        "    n = len(active_cards)",
        "    card_w, card_h = (365, 550) if n <= 3 else (305, 465)",
        "    gap = 42 if n <= 3 else 24",
        "    start_x = (w - (n * card_w + max(0, n - 1) * gap)) // 2",
        "    base_y = 222 if n <= 3 else 258",
        "    draw_order = [i for i in range(n) if i != focus_idx] + [focus_idx]",
        "    for idx in draw_order:",
        "        slug, cname, _m = active_cards[idx]",
        "        is_focus = (idx == focus_idx)",
        "        scale = 1.18 if is_focus else 0.94",
        "        cw, ch = int(card_w * scale), int(card_h * scale)",
        "        px = start_x + idx * (card_w + gap) - (cw - card_w) // 2",
        "        py = base_y - (ch - card_h) // 2 - (30 if is_focus else 0)",
        "        mid = (n - 1) / 2.0",
        "        tilt = 0 if is_focus else (-1 if idx < mid else (1 if idx > mid else 0))",
        '        fx = Image.new("RGBA", (w, h), (0, 0, 0, 0))',
        "        fd = ImageDraw.Draw(fx)",
        "        fd.rounded_rectangle([px + 14, py + 24, px + cw + 14, py + ch + 24], radius=24, fill=(0, 0, 0, 195))",
        "        if is_focus: fd.rounded_rectangle([px - 22, py - 22, px + cw + 22, py + ch + 22], radius=28, fill=(250, 204, 21, 155))",
        "        stage = Image.alpha_composite(stage, fx.filter(ImageFilter.GaussianBlur(radius=28 if is_focus else 16)))",
        "        art_p = find_card_image(slug)",
        "        if art_p:",
        '            cim = Image.open(art_p).convert("RGBA").resize((cw, ch), Image.Resampling.LANCZOS)',
        "            ImageDraw.Draw(cim).rounded_rectangle([2, 2, cw - 3, ch - 3], radius=18, outline=(250, 204, 21, 225), width=4)",
        '            if not is_focus: cim = Image.alpha_composite(cim, Image.new("RGBA", (cw, ch), (4, 7, 18, 78)))',
        "            cim = perspective_tilt(cim, tilt_dir=tilt)",
        "            stage.alpha_composite(cim, (px, py))",
        '    em_fg = Image.new("RGBA", (w, h), (0, 0, 0, 0))',
        "    efd = ImageDraw.Draw(em_fg)",
        "    for _ in range(30):",
        "        ex, ey, er = rng.randint(80, w - 80), rng.randint(150, h - 165), rng.randint(5, 11)",
        "        efd.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(254, 215, 102, rng.randint(65, 135)))",
        "    stage = Image.alpha_composite(stage, em_fg.filter(ImageFilter.GaussianBlur(radius=4.5)))",
        '    hud = Image.new("RGBA", (w, h), (0, 0, 0, 0))',
        "    hd = ImageDraw.Draw(hud)",
        "    hd.rectangle([0, 0, w, 110], fill=(3, 5, 14, 222))",
        "    hd.line([(0, 110), (w, 110)], fill=(250, 204, 21, 195), width=2)",
        "    hd.rectangle([0, h - 154, w, h], fill=(3, 5, 14, 236))",
        "    hd.line([(0, h - 154), (w, h - 154)], fill=(56, 189, 248, 195), width=2)",
        '    hd.text((64, 34), f"ORACLE SYSTEMS 3D COLLECTIVE READING  //  {topic.upper()[:52]}", font=load_font(31), fill=(56, 228, 255, 255))',
        "    f_ch = load_font(38)",
        "    cb = hd.textbbox((0, 0), ch_label.upper(), font=f_ch)",
        "    hd.text((w // 2 - (cb[2] - cb[0]) // 2, h - 130), ch_label.upper(), font=f_ch, fill=(250, 204, 21, 255))",
        '    cards_line = "  |  ".join(c[1] for c in active_cards)',
        "    f_sub = load_font(23)",
        "    sb = hd.textbbox((0, 0), cards_line, font=f_sub)",
        "    hd.text((w // 2 - (sb[2] - sb[0]) // 2, h - 62), cards_line, font=f_sub, fill=(226, 232, 240, 240))",
        '    Image.alpha_composite(stage, hud).convert("RGB").save(out_png, "PNG", optimize=True)',
        "",
        "def render_chapter_mp4(img_png, aud_mp3, out_mp4, dur_sec):",
        "    frames = max(48, int(dur_sec * 24))",
        "    filt = (",
        '        f"[0:v]scale=2112:1188,zoompan=z=\'min(1.0 + 0.09*on/{frames},1.09)\':x=\'iw/2-(iw/zoom/2)+sin(on/45)*14\':y=\'ih/2-(ih/zoom/2)\':d={frames}:s=1280x720:fps=24,"',
        '        f"eq=brightness=\'0.015*sin(2*PI*t/6)\':saturation=1.08,fade=t=in:st=0:d=0.8,fade=t=out:st={max(0.8, dur_sec - 0.8):.2f}:d=0.8,format=yuv420p[vout];"',
        '        f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,equalizer=f=180:width_type=o:w=1.2:g=3,acompressor=threshold=-18dB:ratio=3:attack=15:release=150,loudnorm=I=-14:TP=-1.5:LRA=9[vvoice];"',
        '        f"aevalsrc=\'0.032*sin(2*PI*432*t)+0.016*sin(2*PI*528*t)\':s=44100:d={dur_sec:.2f}[pad];"',
        '        "[vvoice][pad]amix=inputs=2:duration=first:dropout_transition=2[aout]"',
        "    )",
        "    cmd = [",
        '        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",',
        '        "-threads", "2", "-filter_threads", "2", "-filter_complex_threads", "2",',
        '        "-i", img_png, "-i", aud_mp3, "-filter_complex", filt,',
        '        "-map", "[vout]", "-map", "[aout]",',
        '        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-threads", "2", "-pix_fmt", "yuv420p",',
        '        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out_mp4,',
        "    ]",
        "    res = subprocess.run(cmd, capture_output=True, text=True)",
        '    if res.returncode != 0: raise RuntimeError(f"FFmpeg chapter failed: {res.stderr[:260]}")',
        "",
        "def main():",
        "    ap = argparse.ArgumentParser()",
        '    ap.add_argument("--week", type=int, default=2)',
        '    ap.add_argument("--topic", type=str, default="Silent Abundance & Financial Breakthrough")',
        '    ap.add_argument("--target-minutes", type=int, default=3)',
        "    args = ap.parse_args()",
        '    slug = re.sub(r"[^A-Za-z0-9]+", "_", f"Week_{args.week:02d}_{args.topic}").strip("_")',
        "    job_dir = os.path.join(WORK_DIR, slug)",
        "    os.makedirs(job_dir, exist_ok=True)",
        "    spread = DECK_META[:5]",
        "    words_per_ch = max(75, int((args.target_minutes * 135) / 7))",
        "    chapters = [",
        '        ("Chapter 1 - Opening Portal & Collective Energy", spread[:1], 0),',
        '        (f"Chapter 2 - Past Catalyst: {spread[0][1]}", spread[:1], 0),',
        '        (f"Chapter 3 - Present Turning Point: {spread[1][1]}", spread[:2], 1),',
        '        (f"Chapter 4 - Guiding Light: {spread[2][1]}", spread[:3], 2),',
        '        (f"Chapter 5 - Solar Breakthrough: {spread[3][1]}", spread[:4], 3),',
        '        (f"Chapter 6 - Sovereign Mastery: {spread[4][1]}", spread[:5], 4),',
        '        ("Chapter 7 - Complete 5-Card 3D Integration", spread[:5], 3),',
        "    ]",
        '    print(f"=== RENDERING 3D RAY-TRACED 7-CHAPTER READING: {slug} (Target: ~{args.target_minutes} min) ===")',
        "    part_mp4s, total_sec = [], 0.0",
        "    for idx, (ch_title, vis_cards, focus_i) in enumerate(chapters, 1):",
        "        c_slug, c_name, c_meaning = vis_cards[focus_i]",
        '        print(f"  [{idx}/7] Rendering 3D scene + studio voice: {ch_title} ...")',
        "        prose = ollama_expand_chapter(args.topic, ch_title, c_name, c_meaning, words_per_ch)",
        '        aud_p, img_p, mp4_p = os.path.join(job_dir, f"ch{idx:02d}.mp3"), os.path.join(job_dir, f"ch{idx:02d}.png"), os.path.join(job_dir, f"ch{idx:02d}.mp4")',
        "        v_used = synth_voice(prose, aud_p)",
        "        dur = get_audio_duration(aud_p)",
        "        compose_3d_cinema_scene(img_p, args.topic, ch_title, vis_cards, focus_i)",
        "        render_chapter_mp4(img_p, aud_p, mp4_p, dur)",
        "        part_mp4s.append(mp4_p); total_sec += dur",
        '        print(f"        [PASS] {dur:.1f}s unique 3D chapter ({v_used}) | Total: {total_sec/60.0:.2f} min")',
        '    list_txt = os.path.join(job_dir, "concat.txt")',
        '    with open(list_txt, "w", encoding="utf-8", newline="") as f:',
        "        for p in part_mp4s: f.write(\"file '\" + p.replace(chr(92), '/') + \"'\\n\")",
        '    final_mp4 = os.path.join(OUT_DIR, f"{slug}_REAL_FULL.mp4")',
        '    res = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", list_txt, "-c", "copy", "-movflags", "+faststart", final_mp4], capture_output=True, text=True)',
        '    if res.returncode != 0: raise RuntimeError(f"Final concat failed: {res.stderr[:250]}")',
        '    thumb_out = os.path.join(THUMB_DIR, f"{slug}_REAL_Thumb.jpg")',
        '    Image.open(os.path.join(job_dir, "ch06.png")).convert("RGB").resize((1280, 720), Image.Resampling.LANCZOS).save(thumb_out, "JPEG", quality=94)',
        '    print(f"\\n[COMPLETE - 3D ZERO-LOOP] {final_mp4} ({os.path.getsize(final_mp4)/(1024**2):.1f} MB | {total_sec/60.0:.2f} min)")',
        '    print(f"[THUMBNAIL READY]         {thumb_out}")',
        "",
        'if __name__ == "__main__":',
        "    main()",
        "",
    ]
    open(engine_path, "w", encoding="utf-8", newline="").write("\n".join(lines))
    py_compile.compile(engine_path, doraise=True)
    print("[3/4] Upgraded Modules\\render_real_full_reading.py (3D Perspective Tilt + Ray-Traced 5-Card Flagship Deck + Volumetric Motion)")


# ==============================================================================
# 4. VERIFY LIVE PORT 8000 SERVES PHASE 20 BLOOM STAGE
# ==============================================================================
def verify_live_stage():
    ok = False
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/store", timeout=4) as r:
            txt = r.read().decode("utf-8", "ignore")
            ok = (r.status == 200 and "UnrealBloomPass" in txt and "shuffleAndDraw3D" in txt)
    except Exception:
        pass
    print(f"[4/4] Live /store Three.js UnrealBloomPass + Full-Deck Shuffle Draw Verified: {ok}")


def main():
    normalize_deck_images()
    install_phase20_webgl_bloom_store()
    upgrade_video_renderer_3d_raytraced()
    verify_live_stage()
    print("\n[PHASE 20 COMPLETE] Ready to open /store and render your 3D ray-traced 7-chapter video!")


if __name__ == "__main__":
    main()