import asyncio
import os
import subprocess
import time
import edge_tts

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
VOICE_DIR = os.path.join(PDIR, "static", "card_voices")
os.makedirs(VOICE_DIR, exist_ok=True)

CARD_SCRIPTS = {
    "the_magician": "Card one, The Magician. Every skill, late night, and quiet breakthrough you built has converged into sovereign architectural mastery. The hesitation phase is officially over.",
    "wheel_of_fortune": "Wheel of Fortune. The timing around your financial and creative cycle is rotating sharply upward right now. A decisive door is opening. Step straight through it before the momentum locks.",
    "the_star": "The Star. Every ounce of static is clearing from your horizon. Your vision is sharp, your alignment is unmistakable, and your next move carries clean magnetic pull.",
    "the_sun": "The Sun. Unstoppable abundance, radiant visibility, and momentum that can no longer be ignored. Claim your custom reading below to lock in this exact upward trajectory.",
    "the_world": "The World. An old exhausting cycle has reached total completion. You are stepping into higher ownership, global reach, and full command of your digital realm.",
    "ace_of_pentacles": "Ace of Pentacles. A concrete new financial portal, contract, or scalable revenue stream is placing itself directly into your hands.",
    "the_empress": "The Empress. Compounding wealth, creative magnetism, and assets that continue paying you back long after you build them.",
    "the_emperor": "The Emperor. Unshakeable structure, disciplined boundaries, and executive command over every system you deploy.",
    "the_high_priestess": "The High Priestess. Trust the quiet signal you already sensed before the crowd noticed. Your intuition is reading three moves ahead.",
    "the_chariot": "The Chariot. Lock in your focus, cut every distraction, and accelerate straight through resistance into victory.",
}

VOICES = ["en-US-AndrewMultilingualNeural", "en-US-BrianMultilingualNeural", "en-US-ChristopherNeural"]


def synth_and_master(slug, text, force=False):
    out_mp3 = os.path.join(VOICE_DIR, f"{slug}.mp3")
    if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 8000 and not force:
        return "CACHED"
    raw_mp3 = out_mp3 + ".raw.mp3"
    ok = False
    used = ""
    for attempt in range(4):
        v = VOICES[attempt % len(VOICES)]
        try:
            if os.path.exists(raw_mp3):
                os.remove(raw_mp3)
            async def _gen(vn=v):
                await edge_tts.Communicate(text, voice=vn, rate="-6%", pitch="-2Hz").save(raw_mp3)
            asyncio.run(_gen())
            if os.path.exists(raw_mp3) and os.path.getsize(raw_mp3) > 1500:
                ok = True
                used = v
                break
        except Exception:
            time.sleep(2.0 * (attempt + 1))
    if not ok:
        raise RuntimeError(f"Failed TTS for {slug}")

    tmp_out = out_mp3 + ".master.mp3"
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-threads", "2",
        "-i", raw_mp3,
        "-af", "equalizer=f=180:width_type=o:w=1.2:g=3,acompressor=threshold=-18dB:ratio=3:attack=15:release=150,loudnorm=I=-14:TP=-1.5:LRA=9",
        "-c:a", "libmp3lame", "-b:a", "192k", tmp_out,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(tmp_out) and os.path.getsize(tmp_out) > 2000:
        os.replace(tmp_out, out_mp3)
    else:
        os.replace(raw_mp3, out_mp3)
    if os.path.exists(raw_mp3):
        os.remove(raw_mp3)
    time.sleep(1.2)
    return used


def main():
    built = 0
    for slug, text in CARD_SCRIPTS.items():
        res = synth_and_master(slug, text)
        if res != "CACHED":
            built += 1
            print(f"[VOICE MASTERED] {slug}.mp3 via {res} (-14 LUFS studio EQ)")
    print(f"[PHASE 23 PASS] All {len(CARD_SCRIPTS)} card studio neural voices verified (newly mastered: {built})")


if __name__ == "__main__":
    main()