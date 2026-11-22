(function(){
  if (document.getElementById("omega-5d-canvas")) return;
  var c = document.createElement("canvas");
  c.id = "omega-5d-canvas";
  c.style.cssText = "position:fixed;inset:0;width:100vw;height:100vh;z-index:0;pointer-events:none;opacity:0.65;";
  document.body.insertBefore(c, document.body.firstChild);
  var ctx = c.getContext("2d");
  var W = 0, H = 0, mx = 0, my = 0;
  function resize(){ W = c.width = window.innerWidth; H = c.height = window.innerHeight; }
  resize(); window.addEventListener("resize", resize);
  window.addEventListener("mousemove", function(e){
    mx = (e.clientX / Math.max(1, W) - 0.5) * 1.4;
    my = (e.clientY / Math.max(1, H) - 0.5) * 1.4;
  });

  // 5D Penteract (32 vertices, 80 edges) projected 5D -> 4D -> 3D -> 2D
  var verts = [];
  for (var i = 0; i < 32; i++) {
    verts.push([(i&1)?1:-1, (i&2)?1:-1, (i&4)?1:-1, (i&8)?1:-1, (i&16)?1:-1]);
  }
  var edges = [];
  for (var a = 0; a < 32; a++) {
    for (var b = a + 1; b < 32; b++) {
      var diff = a ^ b;
      if (diff && (diff & (diff - 1)) === 0) edges.push([a, b, (a + b) % 3]);
    }
  }
  var stars = [];
  for (var s = 0; s < 75; s++) {
    stars.push({a: Math.random()*Math.PI*2, r: 0.25 + Math.random()*0.65, sp: 0.002 + Math.random()*0.006, sz: 1 + Math.random()*2.2});
  }

  function rot(v, i, j, th) {
    var ca = Math.cos(th), sa = Math.sin(th);
    var vi = v[i], vj = v[j];
    v[i] = vi * ca - vj * sa;
    v[j] = vi * sa + vj * ca;
  }

  var t = 0;
  function frame(){
    t += 0.0085;
    ctx.fillStyle = "rgba(4,7,18,0.28)";
    ctx.fillRect(0, 0, W, H);
    var cx = W * 0.5, cy = H * 0.42;
    var sc = Math.min(W, H) * 0.31;

    for (var k = 0; k < stars.length; k++) {
      var st = stars[k];
      st.a += st.sp;
      var px = cx + Math.cos(st.a) * sc * (1.2 + st.r) * (1 + 0.18 * Math.cos(st.a * 0.5));
      var py = cy + Math.sin(st.a * 1.5) * sc * (0.65 + st.r * 0.5);
      ctx.fillStyle = (k % 2 === 0) ? "rgba(56,189,248,0.55)" : "rgba(250,204,21,0.50)";
      ctx.beginPath(); ctx.arc(px, py, st.sz, 0, Math.PI * 2); ctx.fill();
    }

    var pts = [];
    for (var i = 0; i < 32; i++) {
      var v = verts[i].slice();
      rot(v, 0, 4, t * 0.7 + mx * 0.4);
      rot(v, 1, 3, t * 0.9 + my * 0.4);
      rot(v, 2, 4, t * 0.5);
      rot(v, 0, 2, t * 0.45 + mx * 0.35);
      rot(v, 1, 2, my * 0.35);
      var p5 = 2.6 / (3.8 - v[4]);
      var p4 = 2.5 / (3.8 - v[3] * p5);
      var p3 = 2.4 / (4.1 - v[2] * p5 * p4);
      var ksc = p5 * p4 * p3 * sc * 0.52;
      pts.push([cx + v[0] * ksc, cy + v[1] * ksc]);
    }

    var palette = ["rgba(56,189,248,0.44)", "rgba(250,204,21,0.40)", "rgba(167,139,250,0.38)"];
    ctx.lineWidth = 1.3;
    for (var e = 0; e < edges.length; e++) {
      var p1 = pts[edges[e][0]], p2 = pts[edges[e][1]];
      ctx.strokeStyle = palette[edges[e][2]];
      ctx.beginPath(); ctx.moveTo(p1[0], p1[1]); ctx.lineTo(p2[0], p2[1]); ctx.stroke();
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  fetch("/api/live-pulse").then(function(r){ return r.json(); }).then(function(d){
    var el = document.getElementById("omega-live-pulse");
    if (el && d) {
      el.textContent = "LIVE TELEMETRY: " + d.vault_videos + " 4D ASSETS RENDERED  |  " + d.yt_views + " YOUTUBE VIEWS  |  " + d.utm_clicks + " VERIFIED CHECKOUT CLICKS  |  STRIPE LIVE PAYOUTS ACTIVE";
    }
  }).catch(function(){});
})();
function omegaCopyRef(){
  var code = localStorage.getItem("oracle_ref_code");
  if (!code) { code = "oracle_" + Math.random().toString(36).slice(2, 8); localStorage.setItem("oracle_ref_code", code); }
  var url = window.location.origin + "/go/assetpack15?utm_source=member_ref&utm_medium=share&utm_campaign=" + code;
  if (navigator.clipboard) navigator.clipboard.writeText(url);
  var btn = document.getElementById("omega-ref-btn");
  if (btn) { btn.textContent = "Referral Link Copied! Share to Unlock Bonus Pack"; }
  var inp = document.getElementById("omega-ref-url");
  if (inp) { inp.value = url; }
}
