#!/usr/bin/env python3
"""
Oracle Systems LLC // Android Termux Mobile Command HUD (Phase 46)
Usage in Android Termux:
  cd ~/monday_project && git pull && python termux_hud.py --url https://oraclesystemsllc.com
"""
import argparse
import json
import os
import sys
import urllib.request


def fetch_json(base_url, path):
    req = urllib.request.Request(base_url.rstrip("/") + path, headers={"User-Agent": "OracleTermuxHUD/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser(description="Oracle Systems SovereignCore Android Termux Mobile HUD")
    ap.add_argument("--url", type=str, default="", help="Live Cloudflare or oraclesystemsllc.com base URL")
    args = ap.parse_args()

    url = args.url.strip()
    if not url:
        for cand in ("config/public_url.txt", os.path.expanduser("~/.oracle_url")):
            if os.path.exists(cand):
                url = open(cand, "r", encoding="utf-8").read().strip()
                if url.startswith("http"):
                    break
    if not url:
        url = "https://oraclesystemsllc.com"

    print("=" * 64)
    print("  ORACLE SYSTEMS LLC // TERMUX SOVEREIGN MOBILE HUD (v50)")
    print(f"  Target Node: {url}")
    print("=" * 64)
    try:
        pulse = fetch_json(url, "/api/live-pulse")
        telem = fetch_json(url, "/api/exec-telemetry")
        deck = fetch_json(url, "/api/deck-manifest")
        print(f"  [STATUS]      {telem.get('status', 'ONLINE')} | Phase {telem.get('phase', 50)}/50 ({telem.get('completion_pct', 100)}%)")
        print(f"  [TREASURY]    Stripe Pending Net: ${float(telem.get('stripe_pending_usd', 0)):,.2f}")
        print(f"  [TRAFFIC]     YouTube Views: {pulse.get('yt_views', 0)} | Verified /go Clicks: {pulse.get('utm_clicks', 0)}")
        print(f"  [3D DECK]     {len(deck)} Verified Ray-Traced Cards Active on /store")
        print(f"  [B2B CRM]     {telem.get('pronode_prospects', 0)} Pro_Node Prospect(s) Active")
        tiers = telem.get("utm_by_tier") or {}
        if tiers:
            print("  [CLICKS/TIER] " + " | ".join(f"{k}:{v}" for k, v in sorted(tiers.items())))
        print("=" * 64)
    except Exception as ex:
        print(f"  [OFFLINE/NOTE] Could not reach {url}: {ex}")
        print("  Tip: Pass your active tunnel URL -> python termux_hud.py --url https://<your-url>")


if __name__ == "__main__":
    main()
