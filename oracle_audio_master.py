import os, sys, math, wave, struct, random, time, subprocess

ROOT = "C:/Users/toome/Desktop/SovereignCore"
AUDIO_CACHE = ROOT + "/static/audio_fx"
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
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        buf = bytearray()
        lp = 0.0
        for i in range(total):
            t = i / float(sr)
            # Deep warm harmonic bed (108Hz + 216Hz + 324Hz + gentle 432Hz shimmer)
            drone = (0.36 * math.sin(2*math.pi*108.0*t) +
                     0.28 * math.sin(2*math.pi*216.0*t) +
                     0.18 * math.sin(2*math.pi*324.0*t + 0.4) +
                     0.10 * math.sin(2*math.pi*432.0*t + 0.9))
            breathe = 0.65 + 0.35 * math.sin(2*math.pi*0.09*t)
            l_sig = drone * breathe * 0.22
            r_sig = drone * (0.65 + 0.35 * math.cos(2*math.pi*0.08*t)) * 0.22
            # Timed 3D card flip swoosh + crystal chime at card reveal moments
            for ft in flip_times:
                dt = t - ft
                if 0.0 <= dt <= 0.45:
                    env = math.sin(math.pi * (dt / 0.45))
                    nz = random.uniform(-1.0, 1.0)
                    lp = lp * 0.72 + nz * 0.28
                    swoosh = lp * env * 0.42
                    chime = math.sin(2*math.pi*864.0*dt) * math.exp(-dt * 6.5) * 0.24
                    l_sig += swoosh * 0.9 + chime
                    r_sig += swoosh * 1.1 + chime * 0.95
            li = int(max(-1.0, min(1.0, l_sig)) * 32767)
            ri = int(max(-1.0, min(1.0, r_sig)) * 32767)
            buf.extend(struct.pack("<hh", li, ri))
        wf.writeframes(buf)
    return bed_path

def synthesize_human_voice(text, out_mp3, voice_pref=None):
    clean_txt = " ".join(text.replace("#", " ").replace("*", " ").replace(">", " ").replace("<", " ").split())
    raw_voice = out_mp3.replace(".mp3", "_raw_voice.mp3")
    txt_tmp = out_mp3.replace(".mp3", "_voice_in.txt")
    open(txt_tmp, "w", encoding="utf-8").write(clean_txt)

    # Tier 1: Local Kokoro-82M ONNX if local weights are placed in SovereignCore/models/
    kokoro_model = ROOT + "/models/kokoro-v1.0.onnx"
    kokoro_voices = ROOT + "/models/voices-v1.0.bin"
    synthesized = False
    if os.path.exists(kokoro_model) and os.path.exists(kokoro_voices):
        try:
            from kokoro_onnx import Kokoro
            import soundfile as sf
            k = Kokoro(kokoro_model, kokoro_voices)
            samples, sr = k.create(clean_txt, voice="af_heart", speed=0.98, lang="en-us")
            wav_tmp = out_mp3.replace(".mp3", "_kokoro.wav")
            sf.write(wav_tmp, samples, sr)
            subprocess.run(["ffmpeg", "-y", "-i", wav_tmp, "-b:a", "192k", raw_voice], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.remove(wav_tmp)
            synthesized = os.path.exists(raw_voice) and os.path.getsize(raw_voice) > 5000
        except Exception:
            synthesized = False

    # Tier 2: Expressive Conversational Multilingual Neural Voices (zero robotic rate distortion)
    if not synthesized:
        voices = [voice_pref] if voice_pref else []
        voices += ["en-US-AvaMultilingualNeural", "en-US-AndrewMultilingualNeural", "en-US-BrianMultilingualNeural", "en-US-EmmaMultilingualNeural", "en-US-AriaNeural"]
        for v in voices:
            if not v: continue
            try:
                subprocess.run(["edge-tts", "--voice", v, "--file", txt_tmp, "--write-media", raw_voice], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(raw_voice) and os.path.getsize(raw_voice) > 8000:
                    print(f"[AUDIO] Synthesized expressive voice ({v})")
                    synthesized = True
                    break
            except Exception:
                time.sleep(1.2)

    try: os.remove(txt_tmp)
    except Exception: pass
    if not synthesized:
        return False

    bed = ensure_cinematic_bed(120)
    # Studio warm EQ + subtle acoustic hall + balanced bed mix + broadcast loudnorm
    filt = "[0:a]highpass=f=75,equalizer=f=220:t=q:w=1.2:g=2.0,equalizer=f=3200:t=q:w=1.5:g=-1.2,aecho=0.8:0.88:28:0.10,volume=1.18[v];[1:a]volume=0.22[b];[v][b]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-15:TP=-1.5:LRA=11[outa]"
    subprocess.run(["ffmpeg", "-y", "-i", raw_voice, "-i", bed, "-filter_complex", filt, "-map", "[outa]", "-c:a", "libmp3lame", "-b:a", "192k", out_mp3], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try: os.remove(raw_voice)
    except Exception: pass
    return os.path.exists(out_mp3)

if __name__ == "__main__":
    bed = ensure_cinematic_bed(120)
    print("[+] Cinematic 432Hz + Card-Flip Foley Audio Master ready:", bed)
