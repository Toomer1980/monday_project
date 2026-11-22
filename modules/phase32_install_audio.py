import os
import py_compile

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
STATIC_DIR = os.path.join(PDIR, "static")
STORE_HTML = os.path.join(STATIC_DIR, "oracle_webgl_store.html")
os.makedirs(STATIC_DIR, exist_ok=True)

JS_CODE = """(function(){
  if (document.getElementById("p32-intention-bar")) return;
  var hudTop = document.querySelector(".stage-hud-top");
  var hudBot = document.querySelector(".stage-hud-bottom");
  if (!hudTop || !hudBot) return;

  // Web Audio API 432Hz + 528Hz Soft Harmonic Ambient Synth & Card-Flip Chime (0 external files)
  var actx = null, masterGain = null, ambNodes = [], ambOn = false;
  function ensureAudio(){
    if (!actx) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return false;
      actx = new AC();
      masterGain = actx.createGain();
      masterGain.gain.value = 0.04;
      masterGain.connect(actx.destination);
    }
    if (actx.state === "suspended") actx.resume();
    return true;
  }

  window.p32PlayChime = function(){
    if (!ensureAudio()) return;
    var now = actx.currentTime;
    [528, 660, 792].forEach(function(freq, i){
      var osc = actx.createOscillator();
      var g = actx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, now + i * 0.07);
      g.gain.setValueAtTime(0.001, now + i * 0.07);
      g.gain.exponentialRampToValueAtTime(0.09, now + i * 0.07 + 0.04);
      g.gain.exponentialRampToValueAtTime(0.0008, now + i * 0.07 + 1.1);
      osc.connect(g); g.connect(actx.destination);
      osc.start(now + i * 0.07); osc.stop(now + i * 0.07 + 1.15);
    });
  };

  window.p32ToggleAmbience = function(){
    var btn = document.getElementById("p32-amb-btn");
    if (!ensureAudio()) return;
    if (ambOn) {
      ambNodes.forEach(function(o){ try { o.stop(); } catch(e){} });
      ambNodes = []; ambOn = false;
      if (btn) btn.textContent = "432Hz Ambience: OFF";
    } else {
      [216, 432, 528].forEach(function(f, idx){
        var osc = actx.createOscillator();
        var g = actx.createGain();
        osc.type = "sine";
        osc.frequency.value = f;
        g.gain.value = idx === 0 ? 0.45 : (idx === 1 ? 0.35 : 0.20);
        osc.connect(g); g.connect(masterGain);
        osc.start();
        ambNodes.push(osc);
      });
      ambOn = true;
      if (btn) btn.textContent = "432Hz Ambience: ON";
    }
  };

  // Intention Bar injected cleanly below HUD title (pointer-events auto)
  var bar = document.createElement("div");
  bar.id = "p32-intention-bar";
  bar.style.cssText = "pointer-events:auto;margin:10px auto 0 auto;display:flex;justify-content:center;gap:8px;max-width:600px;flex-wrap:wrap;";
  bar.innerHTML =
    '<input id="p32-intent-input" type="text" maxlength="90" placeholder="Enter your name or focus question before drawing..." ' +
    'style="flex:1;min-width:240px;padding:8px 14px;border-radius:999px;background:rgba(4,7,18,0.85);border:1px solid rgba(250,204,21,0.45);color:#fef08a;font-size:12.5px;outline:none;">' +
    '<button id="p32-draw-btn" style="cursor:pointer;padding:8px 16px;border-radius:999px;border:none;background:linear-gradient(90deg,#facc15,#38bdf8);color:#040712;font-weight:800;font-size:12px;">Align &amp; Draw</button>';
  hudTop.appendChild(bar);

  document.getElementById("p32-draw-btn").onclick = function(){
    var val = (document.getElementById("p32-intent-input").value || "").trim();
    window.p32PlayChime();
    if (typeof window.shuffleAndDraw3D === "function") window.shuffleAndDraw3D();
    var cap = document.getElementById("active-card-caption");
    if (cap && val) cap.textContent = "ALIGNED FOR: " + val.toUpperCase().slice(0, 48) + " // CLICK ANY CARD TO HEAR READING";
  };

  // Add 432Hz Ambient toggle button cleanly into bottom HUD
  var ambBtn = document.createElement("button");
  ambBtn.id = "p32-amb-btn";
  ambBtn.className = "cta-glass";
  ambBtn.textContent = "432Hz Ambience: OFF";
  ambBtn.onclick = window.p32ToggleAmbience;
  hudBot.appendChild(ambBtn);

  // Subtle chime when clicking the 3D WebGL stage
  var cvs = document.getElementById("webgl-stage");
  if (cvs) cvs.addEventListener("click", function(){ window.p32PlayChime(); });
})();
"""

open(os.path.join(STATIC_DIR, "phase32_interactive_audio.js"), "w", encoding="utf-8", newline="").write(JS_CODE)

if os.path.exists(STORE_HTML):
    html = open(STORE_HTML, "r", encoding="utf-8").read()
    tag = '<script src="/static/phase32_interactive_audio.js"></script>'
    if tag not in html and "</body>" in html:
        html = html.replace("</body>", tag + "\n</body>", 1)
        open(STORE_HTML, "w", encoding="utf-8", newline="").write(html)
print("[PHASE 32 PASS] Mounted 432Hz Web Audio Synth + Custom Intention Draw Bar onto /store (non-destructive)!")
