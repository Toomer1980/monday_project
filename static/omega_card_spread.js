(function(){
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
