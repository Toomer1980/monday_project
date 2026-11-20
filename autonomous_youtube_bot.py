import os, sys, json, glob, time
from playwright.sync_api import sync_playwright

root = "C:/Users/toome/Desktop/SovereignCore"
vault = root + "/Content_Vault_52Weeks"
ledger_file = root + "/uploaded_videos_ledger.json"
profile_dir = root + "/Edge_Autopilot_Profile"
url_file = root + "/CURRENT_STORE_URL.txt"
channel_id = "UC_UH7CHyWHxIdzsDGm9R4nw"
os.chdir(root)
os.makedirs(profile_dir, exist_ok=True)

store_url = open(url_file, "r", encoding="utf-8").read().strip() if os.path.exists(url_file) else "https://cents-extended-jewellery-samba.trycloudflare.com/store"
uploaded = json.load(open(ledger_file, "r", encoding="utf-8")) if os.path.exists(ledger_file) else {}

def complete_publish_dialog(page, label):
    # Dismiss any thumbnail/phone verification popup if present
    for dismiss_txt in ["Cancel", "Close", "Dismiss"]:
        try:
            dlg = page.locator("ytcp-dialog").filter(has_text="Verify")
            if dlg.count() > 0:
                dlg.get_by_text(dismiss_txt).first.click(timeout=2000)
                time.sleep(1)
        except Exception: pass

    # Scroll to and force-click Not Made For Kids radio button
    try:
        nfk = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        nfk.scroll_into_view_if_needed(timeout=8000)
        nfk.click(force=True, timeout=8000)
        time.sleep(1)
    except Exception as e:
        print(f"    [*] Audience select note: {e}")

    # Jump straight to Visibility tab (#step-badge-3) or step via #next-button
    try:
        page.locator("#step-badge-3").click(timeout=6000)
        time.sleep(2)
    except Exception:
        for _ in range(3):
            try:
                page.locator("#next-button").click(timeout=5000)
                time.sleep(1.5)
            except Exception: pass

    # Select PUBLIC visibility
    try:
        pub = page.locator("tp-yt-paper-radio-button[name='PUBLIC']").first
        pub.scroll_into_view_if_needed(timeout=8000)
        pub.click(force=True, timeout=8000)
        time.sleep(2)
    except Exception as e:
        print(f"    [*] Public radio note: {e}")

    # Wait until #done-button is visible and enabled, then click Publish
    done = page.locator("#done-button").first
    done.wait_for(state="visible", timeout=20000)
    for _ in range(20):
        if done.get_attribute("aria-disabled") != "true":
            break
        time.sleep(1)
    done.click(timeout=15000)
    print(f"[+] PUBLISHED LIVE: {label}")
    time.sleep(6)
    try: page.locator("#close-button").first.click(timeout=4000)
    except Exception: pass
    time.sleep(2)

mode_arg = sys.argv[1] if len(sys.argv) > 1 else "publish_drafts"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        channel="msedge",
        headless=False,
        args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
        no_viewport=True
    )
    page = context.pages[0] if context.pages else context.new_page()

    # Phase 1: Always clear and publish any existing Draft videos first
    print(f"[*] Checking for uploaded Draft videos on channel {channel_id}...")
    page.goto(f"https://studio.youtube.com/channel/{channel_id}/videos/upload", wait_until="domcontentloaded", timeout=60000)
    time.sleep(6)

    draft_count = 0
    while True:
        draft_btns = page.locator("ytcp-button").filter(has_text="Edit draft")
        if draft_btns.count() == 0:
            break
        draft_count += 1
        print(f"[*] Publishing Draft #{draft_count}...")
        draft_btns.first.click(timeout=10000)
        time.sleep(4)
        try:
            title_txt = page.locator("#textbox").nth(0).inner_text().strip()
        except Exception:
            title_txt = f"Draft_{draft_count}"
        try:
            complete_publish_dialog(page, title_txt)
            for mf in glob.glob(vault + "/Week_*.mp4"):
                wn = os.path.basename(mf).split("_")[1]
                if f"Week {wn}" in title_txt:
                    uploaded[os.path.basename(mf)] = {"title": title_txt, "channel_id": channel_id, "published_at": time.strftime("%Y-%m-%d %H:%M:%S"), "store_url": store_url}
            json.dump(uploaded, open(ledger_file, "w", encoding="utf-8"), indent=2)
        except Exception as e:
            print(f"[!] Draft #{draft_count} publish note: {e}")
            break
        page.goto(f"https://studio.youtube.com/channel/{channel_id}/videos/upload", wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

    print(f"[+] Draft publisher finished ({draft_count} drafts pushed LIVE).")

    # Phase 2: Upload new pending videos if numeric count was passed (e.g. python autonomous_youtube_bot.py 2)
    if mode_arg.isdigit():
        max_per_run = int(mode_arg)
        mp4_files = sorted(glob.glob(vault + "/Week_*.mp4"))
        pending = [f for f in mp4_files if os.path.basename(f) not in uploaded][:max_per_run]
        for mp4_path in pending:
            fn = os.path.basename(mp4_path)
            parts = os.path.splitext(fn)[0].split("_")
            wnum = parts[1]
            slug_title = " ".join(parts[2:])
            yt_title = f"URGENT COLLECTIVE TAROT READING (Week {wnum}): {slug_title} | Timeless Energy Alignment"[:98]
            nl = chr(10)
            yt_desc = nl.join([
                f"TIMELESS COLLECTIVE TAROT READING // WEEK {wnum}: {slug_title.upper()}",
                "If this message found you today, trust that the timing is real. Type I CLAIM THIS ALIGNMENT in the comments below.",
                "",
                "INSTANT ACCESS & DIGITAL BLUEPRINTS (LIVE STOREFRONT):",
                f"-> Full Oracle Systems Storefront : {store_url}",
                f"-> 52-Week Collective Reading & Media Blueprint ($29.00) : {store_url}",
                f"-> SovereignCore Pro Automation Node License ($99.00) : {store_url}",
                f"-> Oracle Studio & Merchandising Automation Suite ($249.00) : {store_url}",
                "",
                "SUBSCRIBE & TURN ON NOTIFICATIONS for daily collective readings!",
                "#TarotReading #CollectiveReading #EnergyUpdate #OracleSystems #SpiritualAwakening"
            ])
            print(f"[*] Uploading {fn} -> {yt_title}")
            page.goto(f"https://studio.youtube.com/channel/{channel_id}/videos/upload?d=ud", wait_until="domcontentloaded", timeout=60000)
            page.locator("input[type='file']").first.wait_for(state="attached", timeout=25000)
            page.locator("input[type='file']").first.set_input_files(mp4_path)
            page.locator("#textbox").first.wait_for(state="visible", timeout=30000)
            time.sleep(3)
            boxes = page.locator("#textbox")
            boxes.nth(0).click(); page.keyboard.press("Control+A"); page.keyboard.press("Backspace"); boxes.nth(0).fill(yt_title)
            time.sleep(1)
            boxes.nth(1).click(); page.keyboard.press("Control+A"); page.keyboard.press("Backspace"); boxes.nth(1).fill(yt_desc)
            time.sleep(2)
            try:
                complete_publish_dialog(page, fn)
                uploaded[fn] = {"title": yt_title, "channel_id": channel_id, "published_at": time.strftime("%Y-%m-%d %H:%M:%S"), "store_url": store_url}
                json.dump(uploaded, open(ledger_file, "w", encoding="utf-8"), indent=2)
            except Exception as e:
                print(f"[!] Upload publish note on {fn}: {e}")

    context.close()
