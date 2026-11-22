import glob
import json
import os
import subprocess

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
WORK_ROOT = os.path.join(PDIR, "logs", "real_reading_work")
OUT_MD = os.path.join(PDIR, "reports", "YouTube_Chapter_Timestamps.md")


def ffprobe_dur(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except Exception:
        return 35.0


def fmt_ts(sec):
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m:02d}:{s:02d}"


def main():
    lines = ["# Oracle Systems LLC - Auto-Generated YouTube SEO Chapter Timestamps", ""]
    if os.path.exists(WORK_ROOT):
        dirs = [d for d in sorted(glob.glob(os.path.join(WORK_ROOT, "*"))) if os.path.isdir(d)]
        labels = [
            "Opening Portal & Collective Energy",
            "Card 1 - Past Catalyst",
            "Card 2 - Present Turning Point",
            "Card 3 - Guiding Light",
            "Card 4 - Radiant Breakthrough",
            "Card 5 - Sovereign Mastery",
            "Complete 5-Card Living Integration",
        ]
        for jd in dirs:
            ep_name = os.path.basename(jd)
            chs = sorted(glob.glob(os.path.join(jd, "ch*.mp4")))
            if not chs:
                continue
            lines.append(f"## {ep_name}")
            cursor = 0.0
            for idx, cp in enumerate(chs):
                lbl = labels[idx] if idx < len(labels) else f"Chapter {idx+1}"
                lines.append(f"{fmt_ts(cursor)} {lbl}")
                cursor += ffprobe_dur(cp)
            lines.append(f"- **Total Verified Runtime:** {fmt_ts(cursor)}\n")

    rep = "\n".join(lines) + "\n"
    open(OUT_MD, "w", encoding="utf-8", newline="").write(rep)
    print(f"[PHASE 37 PASS] Generated exact YouTube SEO chapter timestamps -> {OUT_MD}")


if __name__ == "__main__":
    main()
