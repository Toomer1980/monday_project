import os
import py_compile
import re
import shutil
import sys

pdir, bdir = sys.argv[1], sys.argv[2]
dp = os.path.join(pdir, "sovereign_daemon.py")
bak = os.path.join(bdir, "sovereign_daemon.py.bak")
shutil.copy2(dp, bak)

src = open(dp, "r", encoding="utf-8").read()
# Remove previous Phase 7/11 hooks cleanly for idempotency
src = re.sub(r'\r?\n# === ORACLE_PORTAL_UPSELL_HOOK_START ===.*?# === ORACLE_PORTAL_UPSELL_HOOK_END ===\r?\n?', '\n', src, flags=re.DOTALL)
src = re.sub(r'\r?\n# === ORACLE_4D_STOREFRONT_HOOK_START ===.*?# === ORACLE_4D_STOREFRONT_HOOK_END ===\r?\n?', '\n', src, flags=re.DOTALL)

hook = r'''
# === ORACLE_4D_STOREFRONT_HOOK_START ===
@app.after_request
def _oracle_enhance_4d_store_and_portal(resp):
    try:
        ct = (resp.content_type or "").lower()
        if resp.status_code != 200 or "text/html" not in ct:
            return resp
        if request.path not in ("/store", "/portal"):
            return resp
        body = resp.get_data(as_text=True)

        if request.path == "/store" and "oracle-4d-hero" not in body:
            hero = (
                '<style>'
                'body{background:#050814 !important;color:#e2e8f0 !important;font-family:"Segoe UI",system-ui,sans-serif !important;}'
                '#oracle-4d-hero{max-width:1080px;margin:20px auto 26px auto;padding:28px 24px;'
                'background:radial-gradient(circle at 20% 20%,rgba(56,189,248,0.22),transparent 50%),'
                'radial-gradient(circle at 80% 30%,rgba(250,204,21,0.18),transparent 52%),'
                'linear-gradient(135deg,#070d1f 0%,#0f172a 55%,#091326 100%);'
                'border:1px solid rgba(56,189,248,0.45);border-radius:14px;box-shadow:0 0 36px rgba(14,165,233,0.18);}'
                '.o4d-kicker{color:#38bdf8;font-size:12px;letter-spacing:2.4px;font-weight:700;text-transform:uppercase;}'
                '.o4d-title{margin:8px 0 10px 0;font-size:32px;line-height:1.18;'
                'background:linear-gradient(90deg,#facc15,#38bdf8,#fef08a);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}'
                '.o4d-sub{color:#cbd5e1;font-size:15px;max-width:780px;margin:0 0 22px 0;}'
                '.o4d-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;}'
                '.o4d-card{background:rgba(15,23,42,0.88);border:1px solid rgba(250,204,21,0.35);border-radius:10px;padding:16px;'
                'display:flex;flex-direction:column;justify-content:space-between;}'
                '.o4d-card.featured{border:1.5px solid #38bdf8;box-shadow:0 0 22px rgba(56,189,248,0.22);}'
                '.o4d-price{font-size:24px;font-weight:800;color:#facc15;margin:6px 0;}'
                '.o4d-desc{font-size:13px;color:#94a3b8;margin:0 0 14px 0;line-height:1.45;}'
                '.o4d-btn{display:block;text-align:center;padding:10px 14px;border-radius:7px;font-weight:700;text-decoration:none;color:#050814;'
                'background:linear-gradient(90deg,#facc15,#38bdf8);}'
                '.o4d-btn.alt{background:linear-gradient(90deg,#0284c7,#059669);color:#f8fafc;}'
                '</style>'
                '<section id="oracle-4d-hero">'
                '<div class="o4d-kicker">ORACLE SYSTEMS LLC // 4D TESSERACT &amp; MOBIUS QUANTUM ARCHITECTURE</div>'
                '<h1 class="o4d-title">Autonomous 4D Media, Precision Readings &amp; Sovereign AI Compute</h1>'
                '<p class="o4d-sub">Every checkout is Stripe-verified with automated digital fulfillment and instant member portal access.</p>'
                '<div class="o4d-grid">'
                '<div class="o4d-card"><div><div class="o4d-kicker">TIER 1 // STARTER</div><div class="o4d-price">$29</div>'
                '<p class="o4d-desc">Starter Portal Access with immediate digital delivery and verified member vault entry.</p></div>'
                '<a class="o4d-btn" href="/go/tier29?utm_source=store_hero&utm_medium=card&utm_campaign=store_v11">Unlock Starter ($29)</a></div>'
                '<div class="o4d-card featured"><div><div class="o4d-kicker">MOST POPULAR // 4D AURA</div><div class="o4d-price">$49</div>'
                '<p class="o4d-desc">Custom 3D/4K 4D Tesseract &amp; Mobius Aura Reading Video with instant secure download token.</p></div>'
                '<a class="o4d-btn" href="/go/auravideo49?utm_source=store_hero&utm_medium=card&utm_campaign=store_v11">Order 4D Aura ($49)</a></div>'
                '<div class="o4d-card"><div><div class="o4d-kicker">CREATOR STACK</div><div class="o4d-price">$1,500</div>'
                '<p class="o4d-desc">Full Oracle Systems Storefront Bundle: autonomous 52-week 4D video pipeline, Stripe automation &amp; CRM.</p></div>'
                '<a class="o4d-btn alt" href="/go/fullstorefront?utm_source=store_hero&utm_medium=card&utm_campaign=store_v11">Deploy Full Bundle ($1,500)</a></div>'
                '<div class="o4d-card"><div><div class="o4d-kicker">ENTERPRISE HARDWARE</div><div class="o4d-price">$49,999</div>'
                '<p class="o4d-desc">Dedicated Turnkey Pro_Node AI infrastructure (50% ACH Milestone 1 deposit / zero SaaS lock-in).</p></div>'
                '<a class="o4d-btn alt" href="/go/pro_node?utm_source=store_hero&utm_medium=card&utm_campaign=store_v11">Reserve Pro_Node ($49,999)</a></div>'
                '</div></section>'
            )
            if re.search(r'<body[^>]*>', body, flags=re.IGNORECASE):
                body = re.sub(r'(<body[^>]*>)', r'\1' + hero, body, count=1, flags=re.IGNORECASE)
            else:
                body = hero + body
            resp.set_data(body)

        if request.path == "/portal" and "oracle-portal-upsell" not in body and "</body>" in body.lower():
            banner = (
                '<div id="oracle-portal-upsell" style="max-width:760px;margin:24px auto;padding:22px;'
                'background:linear-gradient(135deg,#070d1f,#111827);border:1.5px solid #f59e0b;border-radius:12px;'
                'box-shadow:0 0 28px rgba(245,158,11,0.18);font-family:sans-serif;color:#f8fafc;text-align:center;">'
                '<div style="color:#38bdf8;font-size:12px;letter-spacing:2px;font-weight:bold;">VERIFIED MEMBER UPGRADE // ORACLE SYSTEMS LLC</div>'
                '<h3 style="margin:8px 0;color:#facc15;">Scale to the Full 4D Storefront Bundle or Dedicated Enterprise Pro_Node</h3>'
                '<p style="font-size:14px;color:#cbd5e1;margin:0 0 16px 0;">Direct Stripe-verified upgrade with tracked member provisioning and priority support.</p>'
                '<a href="/go/fullstorefront?utm_source=portal_upsell&utm_medium=banner&utm_campaign=member_upgrade" target="_blank" rel="noopener" '
                'style="display:inline-block;margin:6px;padding:11px 20px;background:#059669;color:#fff;text-decoration:none;border-radius:7px;font-weight:bold;">Upgrade: Full Storefront ($1,500)</a>'
                '<a href="/go/pro_node?utm_source=portal_upsell&utm_medium=banner&utm_campaign=enterprise_upgrade" target="_blank" rel="noopener" '
                'style="display:inline-block;margin:6px;padding:11px 20px;background:#0284c7;color:#fff;text-decoration:none;border-radius:7px;font-weight:bold;">Enterprise Pro_Node ($49,999)</a>'
                '</div></body>'
            )
            body = re.sub(r'</body>', banner, body, count=1, flags=re.IGNORECASE)
            resp.set_data(body)
    except Exception:
        pass
    return resp
# === ORACLE_4D_STOREFRONT_HOOK_END ===
'''

m = re.search(r'\r?\nif\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:', src)
src = (src[:m.start()] + "\n" + hook + "\n" + src[m.start():]) if m else (src.rstrip() + "\n" + hook + "\n")
open(dp, "w", encoding="utf-8", newline="").write(src)
py_compile.compile(dp, doraise=True)
print("[PASS] Patched /store (4D Tesseract Hero + 4 Cards) & /portal (Member Upsell) -> py_compile PASS")