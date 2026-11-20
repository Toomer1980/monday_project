import os as _os_path_mod
_BASE_DIR = _os_path_mod.path.dirname(_os_path_mod.path.abspath(__file__)).replace("\\", "/")
import os, sys, json, math, wave, struct, random, time, subprocess, urllib.request

ROOT = _BASE_DIR
AUDIO_CACHE = ROOT + "/static/audio_fx"
VCFG_PATH = ROOT + "/VOICE_CONFIG.json"
NO_WIN = 0x08000000
os.makedirs(AUDIO_CACHE, exist_ok=True)

def ensure_cinematic_bed(duration_sec=120):
    bed_path = AUDIO_CACHE + "/oracle_cinematic_bed.wav"
    if os.path.exists(bed_path) and os.path.getsize(bed_path) > 100000:
        return bed_path
    sr = 24000
    total = sr * duration_sec
    flip_times = [3.0, 14.0, 28.0]
    random.seed(42)
    with wave.open(bed_path, "w") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr)
        buf = bytearray(); lp = 0.0
        for i in range(total):
            t = i / float(sr)
            drone = (0.36*math.sin(2*math.pi*108.0*t) + 0.28*math.sin(2*math.pi*216.0*t) + 0.18*math.sin(2*math.pi*324.0*t+0.4) + 0.10*math.sin(2*math.pi*432.0*t+0.9))
            l_sig = drone * (0.65 + 0.35*math.sin(2*math.pi*0.09*t)) * 0.22
            r_sig = drone * (0.65 + 0.35*math.cos(2*math.pi*0.08*t)) * 0.22
            for ft in flip_times:
                dt = t - ft
                if 0.0 <= dt <= 0.45:
                    env = math.sin(math.pi * (dt / 0.45))
                    lp = lp * 0.72 + random.uniform(-1.0, 1.0) * 0.28
                    swoosh = lp * env * 0.42
                    chime = math.sin(2*math.pi*864.0*dt) * math.exp(-dt * 6.5) * 0.24
                    l_sig += swoosh * 0.9 + chime; r_sig += swoosh * 1.1 + chime * 0.95
            buf.extend(struct.pack("<hh", int(max(-1.0, min(1.0, l_sig))*32767), int(max(-1.0, min(1.0, r_sig))*32767)))
        wf.writeframes(buf)
    return bed_path

def synthesize_human_voice(text, out_mp3, voice_pref=None):
    cfg = json.load(open(VCFG_PATH, "r", encoding="utf-8")) if os.path.exists(VCFG_PATH) else {"mode": "neural"}
    clean_txt = " ".join(text.replace("#", " ").replace("*", " ").replace(">", " ").replace("<", " ").split())
    raw_voice = out_mp3.replace(".mp3", "_raw_voice.mp3")
    txt_tmp = out_mp3.replace(".mp3", "_voice_in.txt")
    open(txt_tmp, "w", encoding="utf-8").write(clean_txt)
    synthesized = False

    # Mode 1: Custom User Voice (ElevenLabs Voice Clone if key set, or user recorded narration track)
    if cfg.get("mode") == "custom":
        el_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
        el_vid = os.environ.get("ELEVENLABS_VOICE_ID", "").strip() or cfg.get("elevenlabs_voice_id", "").strip()
        if el_key and el_vid:
            try:
                req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{el_vid}", data=json.dumps({"text": clean_txt, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.45, "similarity_boost": 0.85}}).encode("utf-8"), headers={"xi-api-key": el_key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
                with urllib.request.urlopen(req, timeout=25) as r:
                    open(raw_voice, "wb").write(r.read())
                    synthesized = os.path.exists(raw_voice) and os.path.getsize(raw_voice) > 5000
            except Exception: pass
        if not synthesized and os.path.exists(cfg.get("custom_sample", "")) and os.path.getsize(cfg.get("custom_sample", "")) > 20000:
            subprocess.run(["ffmpeg", "-y", "-i", cfg["custom_sample"], "-b:a", "192k", raw_voice], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=NO_WIN)
            synthesized = os.path.exists(raw_voice) and os.path.getsize(raw_voice) > 5000

    # Mode 2: Flagship Neural Voice (Default & Instant Fallback)
    if not synthesized:
        voices = [voice_pref or cfg.get("neural_voice")] + ["en-US-AvaMultilingualNeural", "en-US-AndrewMultilingualNeural", "en-US-BrianMultilingualNeural", "en-US-AriaNeural"]
        for v in voices:
            if not v: continue
            try:
                subprocess.run(["edge-tts", "--voice", v, "--file", txt_tmp, "--write-media", raw_voice], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=NO_WIN)
                if os.path.exists(raw_voice) and os.path.getsize(raw_voice) > 8000:
                    synthesized = True; break
            except Exception: time.sleep(1.0)

    try: os.remove(txt_tmp)
    except Exception: pass
    if not synthesized: return False

    bed = ensure_cinematic_bed(120)
    filt = "[0:a]highpass=f=75,equalizer=f=220:t=q:w=1.2:g=2.0,equalizer=f=3200:t=q:w=1.5:g=-1.2,aecho=0.8:0.88:28:0.10,volume=1.18[v];[1:a]volume=0.22[b];[v][b]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-15:TP=-1.5:LRA=11[outa]"
    subprocess.run(["ffmpeg", "-y", "-i", raw_voice, "-i", bed, "-filter_complex", filt, "-map", "[outa]", "-c:a", "libmp3lame", "-b:a", "192k", out_mp3], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=NO_WIN)
    try: os.remove(raw_voice)
    except Exception: pass
    return os.path.exists(out_mp3)
