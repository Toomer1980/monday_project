import datetime as dt
import json
import os
import sqlite3
import requests

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
CRM_DB = os.path.join(PDIR, "data", "pronode_crm.db")
HOT_MD = os.path.join(PDIR, "reports", "Hot_B2B_Replies.md")


def find_gmail_token():
    for cand in (
        os.path.join(PDIR, "config", "gmail_token.json"),
        os.path.join(PDIR, "config", "google_mail_token.json"),
        os.path.join(PDIR, "gmail_token.json"),
        os.path.join(PDIR, "token.json"),
    ):
        if os.path.exists(cand):
            return cand
    return ""


def main():
    if not os.path.exists(CRM_DB):
        print("[REPLY-MON] CRM DB not found.")
        return

    c = sqlite3.connect(CRM_DB)
    c.row_factory = sqlite3.Row
    contacted = c.execute("SELECT id, company, email, stage FROM prospects WHERE UPPER(COALESCE(stage,''))='CONTACTED'").fetchall()
    if not contacted:
        print("[REPLY-MON] No CONTACTED prospects to monitor yet.")
        c.close()
        return

    tok_p = find_gmail_token()
    if not tok_p:
        print(f"[REPLY-MON] Monitoring {len(contacted)} contacted agency(s) | Check Gmail inbox directly (no local read token path found).")
        c.close()
        return

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        creds = Credentials.from_authorized_user_file(tok_p)
        if not creds.valid or creds.expired:
            creds.refresh(Request())
        hdrs = {"Authorization": f"Bearer {creds.token}"}

        hot_hits = []
        for row in contacted:
            em = (row["email"] or "").lower()
            dom = em.split("@")[-1] if "@" in em else ""
            if not dom:
                continue
            r = requests.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                headers=hdrs,
                params={"q": f"from:@{dom} newer_than:14d", "maxResults": 3},
                timeout=12,
            )
            if r.status_code == 403:
                print(f"[REPLY-MON NOTE] Gmail token is send-only (HTTP 403 on inbox read). Check Gmail manually for replies from your {len(contacted)} contacted agencies.")
                c.close()
                return
            if r.status_code == 200:
                msgs = r.json().get("messages") or []
                if msgs:
                    c.execute("UPDATE prospects SET stage='REPLIED' WHERE id=?", (row["id"],))
                    c.commit()
                    hot_hits.append((row["company"], em, len(msgs)))
                    print(f"  [HOT B2B REPLY DETECTED] {row['company']} <{em}> ({len(msgs)} message(s))")

        lines = [
            f"# Oracle Systems LLC - Hot B2B Agency Replies ({dt.datetime.now().strftime('%Y-%m-%d %H:%M')} EST)",
            f"- **Contacted Agencies Monitored:** {len(contacted)}",
            f"- **Hot Replies Detected:** {len(hot_hits)}",
            "",
        ]
        for comp, em, cnt in hot_hits:
            lines.append(f"- **{comp}** (`{em}`) — {cnt} incoming message(s) -> Send Proposal PDF from `deliverables\\proposals\\` & book 10-min walkthrough!")
        if not hot_hits:
            lines.append("- No replies yet (first 10 emails just dispatched today; typical B2B reply window is 4-48 hours).")
        open(HOT_MD, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
        print(f"[REPLY-MON PASS] Checked {len(contacted)} contacted agencies | Hot replies: {len(hot_hits)}")
    except Exception as ex:
        print(f"[REPLY-MON NOTE] {str(ex)[:140]}")
    finally:
        c.close()


if __name__ == "__main__":
    main()
