(function(){
  var hero = document.getElementById("oracle-4d-hero");
  if (!hero) return;
  var prev = document.getElementById("omega-tarot-stage");
  if (prev) prev.remove();

  var style = document.createElement("style");
  style.textContent = [
    "body{background:radial-gradient(circle at 50% 0%,#0f172a 0%,#050814 55%,#02040a 100%) !important;}",
    "#omega-tarot-stage{margin:18px 0 28px 0;padding:24px 18px;border-radius:16px;background:linear-gradient(180deg,rgba(11,17,36,0.96),rgba(5,8,20,0.98));border:1px solid rgba(250,204,21,0.45);box-shadow:0 18px 48px rgba(0,0,0,0.65);}",
    ".ots-hdr{text-align:center;margin-bottom:20px;}",
    ".ots-hdr h2{margin:6px 0;font-size:25px;color:#fef08a;letter-spacing:0.4px;}",
    ".ots-hdr p{margin:0;color:#94a3b8;font-size:13.5px;}",
    ".ots-row{display:flex;flex-wrap:wrap;justify-content:center;gap:26px;perspective:1300px;}",
    ".ots-card{width:240px;height:384px;cursor:pointer;position:relative;transform-style:preserve-3d;transition:transform 0.85s cubic-bezier(.2,.8,.2,1);}",
    ".ots-card.flipped{transform:rotateY(180deg);}",
    ".ots-card:hover:not(.flipped){transform:translateY(-8px) rotateX(4deg) rotateY(-5deg);}",
    ".ots-face{position:absolute;inset:0;border-radius:16px;backface-visibility:hidden;overflow:hidden;box-sizing:border-box;}",
    ".ots-back{background:radial-gradient(circle at 50% 45%,#1e293b 0%,#090d1f 75%);border:2px solid #facc15;box-shadow:0 12px 32px rgba(0,0,0,0.65),inset 0 0 28px rgba(250,204,21,0.18);display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:22px;text-align:center;}",
    ".ots-sigil{width:136px;height:136px;border-radius:50%;border:2px solid rgba(250,204,21,0.85);display:flex;align-items:center;justify-content:center;background:radial-gradient(circle,rgba(250,204,21,0.18),transparent 70%);}",
    ".ots-front{transform:rotateY(180deg);border:2px solid #facc15;box-shadow:0 14px 38px rgba(250,204,21,0.28);background:#050814;}",
    ".ots-front img{width:100%;height:100%;object-fit:cover;display:block;}",
    ".ots-cap{position:absolute;left:0;right:0;bottom:0;padding:8px 10px;background:linear-gradient(transparent,rgba(4,7,18,0.95) 35%);color:#e2e8f0;font-size:11px;text-align:center;}",
    ".ots-pos{font-size:10px;letter-spacing:2px;color:#38bdf8;font-weight:800;text-transform:uppercase;}",
    ".ots-bar{margin-top:20px;display:flex;flex-wrap:wrap;justify-content:center;gap:12px;align-items:center;}",
    ".ots-btn{cursor:pointer;padding:10px 20px;border:none;border-radius:8px;font-weight:800;font-size:13px;background:linear-gradient(90deg,#facc15,#38bdf8);color:#050814;}"
  ].join("");
  document.head.appendChild(style);

  var cards = [
    {pos:"I. PAST CATALYST", name:"THE MAGICIAN", img:"/assets/tarot_deck/the_magician.png", msg:"Every lesson forged sovereign mastery.", audio:"/static/card_voices/card_past.mp3"},
    {pos:"II. PRESENT SHIFT", name:"WHEEL OF FORTUNE", img:"/assets/tarot_deck/wheel_of_fortune.png", msg:"Financial frequency rotating upward now.", audio:"/static/card_voices/card_present.mp3"},
    {pos:"III. QUANTUM OUTCOME", name:"THE SUN", img:"/assets/tarot_deck/the_sun.png", msg:"Total clarity and unstoppable momentum.", audio:"/static/card_voices/card_future.mp3"}
  ];

  var stage = document.createElement("div");
  stage.id = "omega-tarot-stage";
  var html = '<div class="ots-hdr"><div class="ots-pos">INTERACTIVE ILLUSTRATED TAROT SPREAD // STUDIO NEURAL NARRATION</div>'
    + '<h2>Tap Any Card to Reveal the Illustrated Artwork &amp; Hear Your Reading</h2>'
    + '<p>Full-bleed illustrated Major Arcana cards paired with studio broadcast neural narration.</p></div><div class="ots-row">';

  cards.forEach(function(cd, idx){
    html += '<div class="ots-card" onclick="omegaFlipCard(this,' + idx + ')">'
      + '<div class="ots-face ots-back"><div class="ots-pos">' + cd.pos + '</div><div class="ots-sigil"><div style="color:#facc15;font-weight:900;letter-spacing:2px;font-size:13px;">ORACLE<br>SYSTEMS</div></div><div style="color:#fef08a;font-size:12px;font-weight:700;">TAP TO REVEAL CARD</div></div>'
      + '<div class="ots-face ots-front"><img src="' + cd.img + '" alt="' + cd.name + '"><div class="ots-cap">' + cd.msg + '</div></div></div>';
  });
  html += '</div><div class="ots-bar"><button class="ots-btn" onclick="omegaRevealAll()">Reveal All 3 Illustrated Cards + Play Studio Reading</button>'
    + '<a class="ots-btn" style="text-decoration:none;background:linear-gradient(90deg,#059669,#0284c7);color:#fff;" href="/go/auravideo49?utm_source=card_spread&utm_medium=cta&utm_campaign=real_art_v18">Order Your Custom Full Reading ($49)</a></div>';
  stage.innerHTML = html;

  var grid = hero.querySelector(".o4d-grid");
  if (grid) hero.insertBefore(stage, grid); else hero.appendChild(stage);

  var player = new Audio();
  window.omegaFlipCard = function(el, idx){
    el.classList.add("flipped");
    try { player.pause(); player.src = cards[idx].audio; player.play(); } catch(e){}
  };
  window.omegaRevealAll = function(){
    document.querySelectorAll(".ots-card").forEach(function(el, i){ setTimeout(function(){ el.classList.add("flipped"); }, i * 450); });
    var seq = [0, 1, 2], pos = 0;
    function next(){
      if (pos >= seq.length) return;
      player.src = cards[seq[pos++]].audio;
      player.onended = next;
      player.play().catch(function(){});
    }
    next();
  };
})();
