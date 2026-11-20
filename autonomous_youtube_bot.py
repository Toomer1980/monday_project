import os, sys, json, glob, time
from playwright.sync_api import sync_playwright

root = "C:/Users/toome/Desktop/SovereignCore"
vault = root + "/Content_Vault_52Weeks"
shorts_dir = root + "/Content_Vault_Shorts"
ledger_file = root + "/uploaded_videos_ledger.json"
profile_dir = root + "/Edge_Autopilot_Profile"
url_file = root + "/CURRENT_STORE_URL.txt"
channel_id = "UC_UH7CHyWHxIdzsDGm9R4nw"
os.chdir(root)
os.makedirs(profile_dir, exist_ok=True)

store_url = open(url_file, "r", encoding="utf-8").read().strip() if os.path.exists(url_file) else "https://cents-extended-jewellery-samba.trycloudflare.com/store"
uploaded = json.load(open(ledger_file, "r", encoding="utf-8")) if os.path.exists(ledger_file) else {}

def make_clean_meta(wnum, slug_title, is_short=False):
    nl = chr(10)
    if is_short:
        yt_title = f"URGENT TAROT MESSAGE: {slug_title} #shorts #tarot #manifestation"[:98]
    else:
        yt_title = f"URGENT COLLECTIVE TAROT READING (Week {wnum}): {slug_title} | Timeless Energy Alignment"[:98]
    yt_desc = nl.join([
        f"TIMELESS COLLECTIVE TAROT READING // WEEK {wnum}: {slug_title.upper()}",
        "If this message found you today, trust that the timing is real. Type I CLAIM THIS ALIGNMENT in the comments below.",
        "",
        "INSTANT ACCESS & DIGITAL BLUEPRINTS (LIVE STOREFRONT):",
        f"- Full Oracle Systems Storefront : {store_url}",
        f"- 52-Week Collective Reading & Media Blueprint ($29.00) : {store_url}",
        f"- SovereignCore Pro Automation Node License ($99.00) : {store_url}",
        f"- Oracle Studio & Merchandising Automation Suite ($249.00) : {store_url}",
        "",
        "SUBSCRIBE & TURN ON NOTIFICATIONS for daily collective readings!",
        "#shorts #TarotReading #CollectiveReading #EnergyUpdate #OracleSystems #SpiritualAwakening"
    ])
    return yt_title.replace("<", "").replace(">", ""), yt_desc.replace("<", "").replace(">", "")

def complete_publish_dialog(page, label):
    nfk = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
    try:
        nfk.scroll_into_view_if_needed(timeout=8000)
        if nfk.get_attribute("aria-checked") != "true":
            nfk.click(timeout=6000)
            time.sleep(1)
        if nfk.get_attribute("aria-checked") != "true":
            page.get_by_text("No, it's not made for kids", exact=False).first.click(timeout=5000)
            time.sleep(1)
    except Exception as e:
        print(f"    [*] Audience select note: {e}")

    pub = page.locator("tp-yt-paper-radio-button[name='PUBLIC']").first
    for _ in range(6):
        if pub.is_visible():
            break
        nxt = page.locator("#next-button").first
        for _w in range(10):
            if nxt.is_visible() and nxt.get_attribute("aria-disabled") != "true":
                break
            time.sleep(1)
        if nxt.is_visible() and nxt.get_attribute("aria-disabled") != "true":
            nxt.click(timeout=6000)
            time.sleep(2)
        else:
            try:
                page.locator("#step-badge-3").click(timeout=4000)
                time.sleep(2)
            except Exception: pass

    pub.wait_for(state="visible", timeout=20000)
    pub.scroll_into_view_if_needed(timeout=5000)
    pub.click(timeout=6000)
    time.sleep(1.5)
    if pub.get_attribute("aria-checked") != "true":
        pub.click(force=True, timeout=5000)
        time.sleep(1.5)

    done = page.locator("#done-button").first
    done.wait_for(state="visible", timeout=20000)
    for _ in range(25):
        if done.get_attribute("aria-disabled") != "true":
            break
        time.sleep(1)
    done.click(timeout=15000)
    print(f"[+] PUBLISHED LIVE: {label}")
    time.sleep(6)
    try: page.locator("#close-button").first.click(timeout=4000)
    except Exception: pass
    time.sleep(2)

def backfill_missing_descriptions(page):
    print("[*] Checking live published videos for missing storefront descriptions...")
    page.goto(f"https://studio.youtube.com/channel/{channel_id}/videos/upload", wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    targets = []
    rows = page.locator("ytcp-video-row")
    for idx in range(rows.count()):
        row = rows.nth(idx)
        txt = row.inner_text()
        if "Add description" in txt and "Edit draft" not in txt:
            link = row.locator("a#video-title").first
            href = link.get_attribute("href")
            title = link.inner_text().strip()
            if href:
                targets.append((href, title))
    print(f"[+] Found {len(targets)} published videos needing storefront descriptions.")
    for href, raw_title in targets:
        edit_url = href if href.startswith("http") else "https://studio.youtube.com" + href
        parts = raw_title.replace("_", " ").split()
        wnum = parts[1] if len(parts) > 1 and parts[1].isdigit() else "01"
        slug_title = " ".join(parts[2:]) if len(parts) > 2 else raw_title
        yt_title, yt_desc = make_clean_meta(wnum, slug_title, is_short=False)
        page.goto(edit_url, wait_until="domcontentloaded", timeout=60000)
        page.locator("#textbox").nth(1).wait_for(state="visible", timeout=25000)
        time.sleep(2)
        boxes = page.locator("#textbox")
        boxes.nth(0).click(); page.keyboard.press("Control+A"); page.keyboard.press("Backspace"); boxes.nth(0).fill(yt_title)
        time.sleep(1)
        boxes.nth(1).click(); page.keyboard.press("Control+A"); page.keyboard.press("Backspace"); boxes.nth(1).fill(yt_desc)
        time.sleep(2)
        save_btn = page.locator("ytcp-button#save").first
        for _ in range(10):
            if save_btn.get_attribute("aria-disabled") != "true":
                break
            time.sleep(1)
        if save_btn.get_attribute("aria-disabled") != "true":
            save_btn.click(timeout=10000)
            print(f"    [+] Saved live storefront link + viral title on: {yt_title}")
            time.sleep(4)

def clear_existing_drafts(page):
    print("[*] Checking Videos & Shorts tabs for existing drafts...")
    page.goto(f"https://studio.youtube.com/channel/{channel_id}/videos/upload", wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    for tab_name in ["Videos", "Shorts"]:
        try:
            tab = page.locator("tp-yt-paper-tab").filter(has_text=tab_name).first
            if tab.is_visible():
                tab.click(timeout=5000)
                time.sleep(3)
        except Exception: pass
        while True:
            draft_btns = page.locator("ytcp-button").filter(has_text="Edit draft")
            if draft_btns.count() == 0: break
            draft_btns.first.click(timeout=10000)
            page.locator("#textbox").nth(1).wait_for(state="visible", timeout=25000)
            time.sleep(2)
            boxes = page.locator("#textbox")
            title_txt = boxes.nth(0).inner_text().strip()
            is_sh = (tab_name == "Shorts") or ("#shorts" in title_txt.lower())
            slug_guess = title_txt.replace("URGENT TAROT MESSAGE:", "").split("#")[0].strip() or "Sovereign Alignment"
            clean_title, clean_desc = make_clean_meta("01", slug_guess, is_short=is_sh)
            # Rewrite description without angle brackets to clear the red Details validation error
            boxes.nth(1).click(); page.keyboard.press("Control+A"); page.keyboard.press("Backspace"); boxes.nth(1).fill(clean_desc)
            time.sleep(2)
            try:
                complete_publish_dialog(page, title_txt)
                for folder in [vault, shorts_dir]:
                    for mf in glob.glob(folder + "/*.mp4"):
                        fn = os.path.basename(mf)
                        slug = " ".join(os.path.splitext(fn)[0].split("_")[2:])
                        if slug.lower() in title_txt.lower() and (("short" in fn.lower()) == is_sh):
                            uploaded[fn] = {"title": title_txt, "channel_id": channel_id, "published_at": time.strftime("%Y-%m-%d %H:%M:%S"), "store_url": store_url}
                json.dump(uploaded, open(ledger_file, "w", encoding="utf-8"), indent=2)
            except Exception as e:
                print(f"[!] Draft publish note: {e}")
                break
            page.reload(wait_until="domcontentloaded", timeout=60000)
            time.sleep(4)

def upload_video(page, mp4_path, is_short=False):
    fn = os.path.basename(mp4_path)
    parts = os.path.splitext(fn)[0].split("_")
    wnum = parts[1]
    slug_title = " ".join(parts[2:])
    yt_title, yt_desc = make_clean_meta(wnum, slug_title, is_short=is_short)
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
    complete_publish_dialog(page, fn)
    uploaded[fn] = {"title": yt_title, "type": "short" if is_short else "long", "channel_id": channel_id, "published_at": time.strftime("%Y-%m-%d %H:%M:%S"), "store_url": store_url}
    json.dump(uploaded, open(ledger_file, "w", encoding="utf-8"), indent=2)

mode = sys.argv[1] if len(sys.argv) > 1 else "daily"
count = int(sys.argv[2]) if len(sys.argv) > 2 else (int(mode) if mode.isdigit() else 2)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir, channel="msedge", headless=False,
        args=["--disable-blink-features=AutomationControlled", "--start-maximized"], no_viewport=True
    )
    page = context.pages[0] if context.pages else context.new_page()
    backfill_missing_descriptions(page)
    clear_existing_drafts(page)
    long_pending = [f for f in sorted(glob.glob(vault + "/Week_*.mp4")) if os.path.basename(f) not in uploaded]
    short_pending = [f for f in sorted(glob.glob(shorts_dir + "/Short_*.mp4")) if os.path.basename(f) not in uploaded]
    if mode == "shorts":
        for sp in short_pending[:count]: upload_video(page, sp, is_short=True)
    elif mode == "daily":
        for lp in long_pending[:1]: upload_video(page, lp, is_short=False)
        for sp in short_pending[:1]: upload_video(page, sp, is_short=True)
    elif mode.isdigit():
        for lp in long_pending[:count]: upload_video(page, lp, is_short=False)
    context.close()
