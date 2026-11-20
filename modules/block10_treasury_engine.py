import configparser
import csv
import datetime as dt
import glob
import json
import os
import shutil
import sqlite3
import tomllib
import urllib.error
import urllib.request

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOML_PATH = os.path.join(PROJECT_DIR, "config", "sovereign_block10.toml")
INI_PATH = os.path.join(PROJECT_DIR, "config", "sovereign_treasury.ini")


def load_configs():
    with open(TOML_PATH, "rb") as f:
        toml_cfg = tomllib.load(f)
    ini_cfg = configparser.ConfigParser()
    ini_cfg.read(INI_PATH, encoding="utf-8")

    drift = []
    if abs(toml_cfg["treasury_rules"]["tax_reserve_pct"] - ini_cfg.getfloat("treasury", "tax_reserve_pct")) > 1e-6:
        drift.append("tax_reserve_pct mismatch between TOML and INI")
    if abs(toml_cfg["cloud_tiers"]["tier_3_enterprise_ha"]["unlock_pronode_deposit_usd"] - ini_cfg.getfloat("cloud_gates", "tier3_unlock_deposit_usd")) > 1e-2:
        drift.append("tier3_unlock_deposit_usd mismatch between TOML and INI")
    return toml_cfg, ini_cfg, drift


def add_business_days(start_date, n, holidays):
    curr = start_date
    added = 0
    while added < n:
        curr += dt.timedelta(days=1)
        if curr.weekday() < 5 and curr not in holidays:
            added += 1
    return curr


def check_endpoints(host, port, timeout):
    base = f"http://{host}:{port}"
    checks = {}
    for path, ok_codes in [
        ("/dashboard", {200}),
        ("/store", {200}),
        ("/portal", {200}),
        ("/api/download/secure-asset?token=HEALTHCHECK", {403}),
    ]:
        try:
            req = urllib.request.Request(base + path, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                code = resp.getcode()
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as e:
            code = f"ERR:{type(e).__name__}"
        checks[path] = {"status": code, "healthy": code in ok_codes}
    return checks


def scan_vaults(cfg):
    v = cfg["vault_inventory"]
    full_dir = os.path.join(PROJECT_DIR, v["full_videos_dir"])
    short_dir = os.path.join(PROJECT_DIR, v["shorts_dir"])
    deliv_dir = os.path.join(PROJECT_DIR, v["deliverables_dir"])

    full_count = len(glob.glob(os.path.join(full_dir, "*.mp4"))) if os.path.isdir(full_dir) else 0
    short_count = len(glob.glob(os.path.join(short_dir, "*.mp4"))) if os.path.isdir(short_dir) else 0
    deliv_count = len(glob.glob(os.path.join(deliv_dir, "*.mp4"))) if os.path.isdir(deliv_dir) else 0
    return {
        "full_videos": full_count,
        "expected_full": v["expected_full_videos"],
        "shorts": short_count,
        "expected_shorts": v["expected_shorts"],
        "deliverables_mp4": deliv_count,
        "complete": (full_count >= v["expected_full_videos"] and short_count >= v["expected_shorts"]),
    }


def parse_float(val):
    if val is None:
        return 0.0
    s = str(val).replace("$", "").replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return 0.0


def load_live_stripe_api_snapshot(cfg):
    snap_rel = cfg.get("stripe_api_polling", {}).get("snapshot_json", os.path.join("audit_inbox", "stripe_live_api_snapshot.json"))
    snap_path = os.path.join(PROJECT_DIR, snap_rel)
    if not os.path.exists(snap_path):
        return None
    try:
        with open(snap_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("live_api_connected"):
            return data
    except Exception:
        return None
    return None


def scan_audit_inbox(cfg):
    inbox = os.path.join(PROJECT_DIR, cfg["audit_paths"]["inbox_dir"])
    stripe_rows = []
    bank_balance = 0.0
    crypto_usd = 0.0
    files_read = []

    for csv_path in sorted(glob.glob(os.path.join(inbox, "*.csv"))):
        name = os.path.basename(csv_path)
        lname = name.lower()
        files_read.append(name)
        try:
            with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    norm = {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
                    if "stripe" in lname or "balance" in norm or ("amount" in norm and "fee" in norm):
                        status = norm.get("status", "succeeded").lower()
                        if status in ("paid", "succeeded", "available", "pending", ""):
                            gross = parse_float(norm.get("amount") or norm.get("gross") or norm.get("amount_paid"))
                            fee = parse_float(norm.get("fee") or norm.get("fees"))
                            net = parse_float(norm.get("net")) if norm.get("net") else (gross - fee)
                            if gross > 0:
                                stripe_rows.append({
                                    "source": name,
                                    "date": norm.get("created date (utc)") or norm.get("created") or norm.get("date") or dt.date.today().isoformat(),
                                    "gross": gross,
                                    "fee": fee,
                                    "net": net,
                                    "status": status or "succeeded",
                                })
                    elif "keybank" in lname or "bank" in lname:
                        bal = parse_float(norm.get("balance") or norm.get("running balance") or norm.get("ending balance"))
                        if bal > 0:
                            bank_balance = bal
                    elif "kraken" in lname or "bitcoin" in lname or "btc" in lname:
                        usd = parse_float(norm.get("usd_value") or norm.get("value_usd") or norm.get("amount_usd"))
                        crypto_usd += max(0.0, usd)
        except Exception as e:
            files_read.append(f"{name} (ERR: {e})")

    return {
        "files_read": files_read,
        "stripe_csv_rows": stripe_rows,
        "verified_bank_usd": round(bank_balance, 2),
        "verified_crypto_usd": round(crypto_usd, 2),
    }


def scan_local_sqlite(cfg):
    test_email = cfg["treasury_rules"]["internal_test_email"].lower()
    legacy_amt = cfg["treasury_rules"]["legacy_test_price_usd"]
    internal_test_orders = []
    external_local_orders = []

    for db_path in glob.glob(os.path.join(PROJECT_DIR, "**", "*.db"), recursive=True):
        if any(skip in db_path.lower() for skip in ("\\backups\\", "\\.git\\", "\\venv\\")):
            continue
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            for tbl in tables:
                cols = [c[1].lower() for c in cur.execute(f'PRAGMA table_info("{tbl}")').fetchall()]
                if "amount_cents" in cols:
                    email_col = "customer_email" if "customer_email" in cols else None
                    q = "SELECT amount_cents" + (f", {email_col}" if email_col else ", ''") + f' FROM "{tbl}"'
                    for amt_cents, em in cur.execute(q).fetchall():
                        usd = (amt_cents or 0) / 100.0
                        if usd <= 0:
                            continue
                        em_clean = (em or "").strip().lower()
                        if em_clean == test_email and abs(usd - legacy_amt) < 0.01:
                            internal_test_orders.append(usd)
                        else:
                            external_local_orders.append({"db": os.path.basename(db_path), "usd": usd, "email": em_clean})
            conn.close()
        except Exception:
            pass

    return {
        "internal_test_count": len(internal_test_orders),
        "internal_test_gross_usd": round(sum(internal_test_orders), 2),
        "other_local_count": len(external_local_orders),
        "other_local_gross_usd": round(sum(x["usd"] for x in external_local_orders), 2),
    }


def run_reconciliation():
    toml_cfg, ini_cfg, drift = load_configs()
    st = toml_cfg["stripe"]
    tr = toml_cfg["treasury_rules"]
    ct = toml_cfg["cloud_tiers"]
    hw = toml_cfg["hardware_guards"]

    today = dt.date.today()
    holidays = {dt.date.fromisoformat(d) for d in st["us_bank_holidays"]}

    endpoints = check_endpoints(hw["server_host"], hw["server_port"], hw["health_timeout_sec"])
    vaults = scan_vaults(toml_cfg)
    live_api = load_live_stripe_api_snapshot(toml_cfg)
    inbox = scan_audit_inbox(toml_cfg)
    local_db = scan_local_sqlite(toml_cfg)

    stripe_available_usd = 0.0
    stripe_pending_usd = 0.0
    payouts_enabled = None
    requirements_due = []
    next_payout_str = st["initial_payout_date"]

    # Priority 1: Live Stripe API Snapshot (polled by run_block10_treasury.ps1)
    if live_api and live_api.get("charge_count", 0) > 0:
        verified_tx_count = int(live_api["charge_count"])
        verified_gross = float(live_api["charges_gross_usd"])
        verified_fees = float(live_api["charges_fees_usd"])
        verified_net = float(live_api["charges_net_usd"])
        max_single_payment = float(live_api.get("max_single_charge_usd", verified_gross))
        stripe_available_usd = float(live_api.get("available_usd", 0.0))
        stripe_pending_usd = float(live_api.get("pending_usd", 0.0))
        payouts_enabled = live_api.get("payouts_enabled")
        requirements_due = live_api.get("requirements_currently_due") or []
        if live_api.get("next_payout_arrival_date"):
            next_payout_str = live_api["next_payout_arrival_date"]
        revenue_source = f"LIVE Stripe API ({verified_tx_count} balance tx | Polled {live_api.get('polled_utc', 'now')})"
    # Priority 2: Manual Stripe CSV exports in audit_inbox\
    elif inbox["stripe_csv_rows"]:
        verified_tx_count = len(inbox["stripe_csv_rows"])
        verified_gross = sum(r["gross"] for r in inbox["stripe_csv_rows"])
        verified_fees = sum(
            r["fee"] if r["fee"] > 0 else (r["gross"] * st["managed_payments_fee_pct"] + r["gross"] * st["card_fee_pct"] + st["card_fee_fixed_usd"])
            for r in inbox["stripe_csv_rows"]
        )
        verified_net = verified_gross - verified_fees
        max_single_payment = max(r["gross"] for r in inbox["stripe_csv_rows"])
        revenue_source = f"Stripe CSV Export ({verified_tx_count} tx)"
    # Priority 3: Confirmed seed receipt ($49 on Nov 20, 2026)
    else:
        verified_tx_count = 1
        verified_gross = tr["verified_seed_gross_usd"]
        verified_fees = verified_gross * st["managed_payments_fee_pct"] + verified_gross * st["card_fee_pct"] + st["card_fee_fixed_usd"]
        verified_net = verified_gross - verified_fees
        max_single_payment = verified_gross
        if live_api:
            stripe_available_usd = float(live_api.get("available_usd", 0.0))
            stripe_pending_usd = float(live_api.get("pending_usd", 0.0))
            payouts_enabled = live_api.get("payouts_enabled")
            requirements_due = live_api.get("requirements_currently_due") or []
        revenue_source = f"Confirmed Seed Receipt {tr['verified_seed_receipt_id']} (set STRIPE_SECRET_KEY in .env for live API polling)"

    tax_reserve = verified_net * tr["tax_reserve_pct"]
    after_tax_net = verified_net - tax_reserve
    tier1_total_mo = ct["tier_1_lean"]["monthly_hosting_usd"] + ct["ai_pro_monthly_usd"]
    op_buffer_target = tier1_total_mo * tr["operating_buffer_months"]

    t3 = ct["tier_3_enterprise_ha"]
    if max_single_payment >= t3["unlock_pronode_deposit_usd"]:
        recommended_cloud = "TIER_3_ENTERPRISE_HA_UNLOCKED"
        gate_reason = f"Funded Pro_Node deposit detected (>= ${t3['unlock_pronode_deposit_usd']:,.2f}). Safe to provision ${t3['monthly_hosting_usd']:,.2f}/mo HA cluster ({t3['target_yr1_margin_pct']:.1f}% Yr-1 margin)."
    elif verified_net >= ct["tier_1_lean"]["unlock_verified_net_usd"]:
        recommended_cloud = "TIER_1_LEAN_READY"
        gate_reason = f"Verified net (${verified_net:,.2f}) clears Tier 1 Lean threshold (${ct['tier_1_lean']['unlock_verified_net_usd']:,.2f}). Upgrade to DigitalOcean ${ct['tier_1_lean']['monthly_hosting_usd']:.2f}/mo; keep Tier 3 HA LOCKED."
    else:
        recommended_cloud = "TIER_0_LOCAL_HOLD_TIER3_LOCKED"
        gate_reason = f"Tier 3 HA (${t3['monthly_hosting_usd']:,.2f}/mo) strictly LOCKED until >= ${t3['unlock_pronode_deposit_usd']:,.2f} Pro_Node deposit clears. Current verified net: ${verified_net:,.2f}."

    next_t2_payout = add_business_days(today, st["ongoing_payout_business_days"], holidays)

    state_path = os.path.join(PROJECT_DIR, toml_cfg["audit_paths"]["state_file"])
    prev_state = None
    if os.path.exists(state_path):
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                prev_state = json.load(f)
        except Exception:
            prev_state = None

    delta_gross = round(verified_gross - (prev_state.get("verified_gross_usd", 0.0) if prev_state else 0.0), 2)
    run_number = (prev_state.get("run_number", 0) if prev_state else 0) + 1

    snapshot = {
        "run_number": run_number,
        "timestamp_utc": dt.datetime.utcnow().isoformat() + "Z",
        "config_drift": drift,
        "revenue_source": revenue_source,
        "live_stripe_api_connected": bool(live_api),
        "stripe_available_usd": round(stripe_available_usd, 2),
        "stripe_pending_usd": round(stripe_pending_usd, 2),
        "stripe_payouts_enabled": payouts_enabled,
        "stripe_requirements_due": requirements_due,
        "verified_tx_count": verified_tx_count,
        "verified_gross_usd": round(verified_gross, 2),
        "verified_fees_usd": round(verified_fees, 2),
        "verified_net_usd": round(verified_net, 2),
        "delta_gross_since_last_run": delta_gross,
        "tax_reserve_pct": tr["tax_reserve_pct"],
        "tax_reserve_usd": round(tax_reserve, 2),
        "after_tax_retained_usd": round(after_tax_net, 2),
        "verified_bank_usd": inbox["verified_bank_usd"],
        "verified_crypto_usd": inbox["verified_crypto_usd"],
        "quarantined_internal_test_tx": local_db["internal_test_count"],
        "quarantined_internal_test_usd": local_db["internal_test_gross_usd"],
        "tier1_monthly_burn_with_ai_usd": round(tier1_total_mo, 2),
        "operating_buffer_3mo_target_usd": round(op_buffer_target, 2),
        "cloud_gate_status": recommended_cloud,
        "cloud_gate_reason": gate_reason,
        "next_payout_date": next_payout_str,
        "rolling_t2_payout_for_today": next_t2_payout.isoformat(),
        "vaults": vaults,
        "endpoints": endpoints,
    }

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    ymd = today.strftime("%Y%m%d")
    reports_dir = os.path.join(PROJECT_DIR, toml_cfg["audit_paths"]["reports_dir"])
    staging_dir = os.path.join(PROJECT_DIR, toml_cfg["audit_paths"]["drive_staging_dir"])
    md_path = os.path.join(reports_dir, f"Block10_Treasury_Report_{ymd}.md")
    csv_path = os.path.join(reports_dir, f"Block10_Ledger_{ymd}.csv")

    verify_line = (
        f"Payouts Enabled: {payouts_enabled} | Requirements Due: {', '.join(requirements_due) if requirements_due else 'None'}"
        if payouts_enabled is not None else "Not polled yet (add STRIPE_SECRET_KEY to .env)"
    )

    md_lines = [
        f"# Oracle Systems LLC — Block 10 Automated Treasury Audit (Run #{run_number})",
        f"- **Date:** {today.isoformat()} | **Source:** {revenue_source}",
        f"- **Config Sync (.toml <-> .ini):** {'CLEAN' if not drift else 'DRIFT: ' + '; '.join(drift)}",
        f"- **Stripe Account Verification:** {verify_line}",
        "",
        "## Verified Financial Scorecard",
        f"- **Live Stripe Available Balance:** ${stripe_available_usd:,.2f}",
        f"- **Live Stripe Pending Balance:** ${stripe_pending_usd:,.2f}",
        f"- **Verified Stripe Gross:** ${verified_gross:,.2f} (Delta vs prior run: ${delta_gross:+,.2f})",
        f"- **Stripe Fees:** ${verified_fees:,.2f}",
        f"- **Verified Stripe Net:** ${verified_net:,.2f}",
        f"- **Tax Reserve Set-Aside ({tr['tax_reserve_pct']*100:.0f}%):** ${tax_reserve:,.2f}",
        f"- **Net Retained After Reserve:** ${after_tax_net:,.2f}",
        f"- **Verified Bank Balance (audit_inbox CSV):** ${inbox['verified_bank_usd']:,.2f}",
        f"- **Verified Crypto Holdings (audit_inbox CSV):** ${inbox['verified_crypto_usd']:,.2f}",
        f"- **Quarantined Internal Test Rows ($99 legacy):** {local_db['internal_test_count']} tx (${local_db['internal_test_gross_usd']:,.2f})",
        "",
        "## Payout Availability & Cloud Tier Gate",
        f"- **Next Scheduled Stripe Payout:** {next_payout_str} (Morning EST ACH batch)",
        f"- **Ongoing T+2 Payout (if charged today):** {next_t2_payout.isoformat()}",
        f"- **Cloud Gate Status:** `{recommended_cloud}`",
        f"- **Gate Rule:** {gate_reason}",
        "",
        "## Self-Aware Infrastructure & Vault Telemetry",
        f"- **Content Vault:** {vaults['full_videos']}/{vaults['expected_full']} Full Videos | {vaults['shorts']}/{vaults['expected_shorts']} Shorts | {vaults['deliverables_mp4']} Deliverable MP4(s)",
    ]
    for ep, info in endpoints.items():
        md_lines.append(f"- **Endpoint `{ep}`:** HTTP {info['status']} ({'PASS' if info['healthy'] else 'FAIL'})")

    with open(md_path, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(md_lines) + "\n")

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Run", "Date", "Available_USD", "Pending_USD", "Verified_Gross", "Fees", "Verified_Net", "Tax_Reserve", "After_Reserve", "Bank_USD", "Crypto_USD", "Quarantined_Test_USD", "Cloud_Gate"])
        w.writerow([run_number, today.isoformat(), round(stripe_available_usd, 2), round(stripe_pending_usd, 2), round(verified_gross, 2), round(verified_fees, 2), round(verified_net, 2), round(tax_reserve, 2), round(after_tax_net, 2), inbox["verified_bank_usd"], inbox["verified_crypto_usd"], local_db["internal_test_gross_usd"], recommended_cloud])

    shutil.copy2(md_path, os.path.join(staging_dir, os.path.basename(md_path)))
    shutil.copy2(csv_path, os.path.join(staging_dir, os.path.basename(csv_path)))

    print("\n".join(md_lines))


if __name__ == "__main__":
    run_reconciliation()