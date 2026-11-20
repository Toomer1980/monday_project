import os, sys, json, math, time, glob, sqlite3, py_compile, subprocess, urllib.request
from datetime import datetime

ROOT = "C:/Users/toome/Desktop/SovereignCore"
DB_PATH = ROOT + "/data/evolution_memory.db"
FED_PATH = ROOT + "/compute_federation.json"
PROMPT_OUT = ROOT + "/ACTIVE_EVOLVED_PROMPT.txt"
CORE_FILES = ["sovereign_daemon.py", "sovereign_master_autopilot.py", "autonomous_youtube_bot.py", "oracle_audio_master.py", "oracle_3d_renderer.py"]
os.chdir(ROOT)
os.makedirs(ROOT + "/data", exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS genomes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        generation INTEGER DEFAULT 1,
        category TEXT,
        content TEXT,
        impressions INTEGER DEFAULT 1,
        conversions INTEGER DEFAULT 0,
        revenue_usd REAL DEFAULT 0.0,
        fitness_score REAL DEFAULT 1.0,
        active INTEGER DEFAULT 1,
        updated_at TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS heal_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        module TEXT,
        issue TEXT,
        action_taken TEXT,
        ts TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS compute_benchmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id TEXT,
        status TEXT,
        latency_ms REAL,
        ts TEXT
    )""")
    cnt = conn.execute("SELECT COUNT(*) FROM genomes").fetchone()[0]
    if cnt == 0:
        seeds = [
            (1, "hook", "Pause right now and take a slow breath. If this 3D transmission crossed your path today, the timing is exact."),
            (1, "hook", "Nothing about you clicking this reading is random. Look closely at the three metallic cards turning in front of you."),
            (1, "tone", "Speak with calm executive warmth, vivid concrete imagery, rhythmic natural pauses, and zero filler or robotic cadence."),
            (1, "cta", "Upload your portrait at the live 3D Oracle Sanctuary in the description to assimilate your aura and unlock your personalized 4K reading or the 52-week blueprint.")
        ]
        now = datetime.now().isoformat()
        for g, cat, txt in seeds:
            conn.execute("INSERT INTO genomes (generation, category, content, fitness_score, updated_at) VALUES (?, ?, ?, ?, ?)", (g, cat, txt, 1.5, now))
    conn.commit()
    conn.close()

def factorial_compound_score(generation, impressions, conversions, revenue_usd):
    # Bounded factorial tier amplifier * exponential generation compounding
    tier = min(7, 1 + int(conversions) + int(revenue_usd // 50.0))
    fact_factor = math.log1p(math.factorial(tier))
    conv_rate = (conversions + 0.15) / float(max(1, impressions))
    compound_growth = math.pow(1.18, min(generation, 25))
    rev_boost = 1.0 + math.log1p(max(0.0, revenue_usd))
    return round(fact_factor * compound_growth * rev_boost * (1.0 + conv_rate * 10.0), 4)

def self_heal_codebase():
    repaired = []
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    for fn in CORE_FILES:
        fp = ROOT + "/" + fn
        if not os.path.exists(fp): continue
        try:
            py_compile.compile(fp, doraise=True)
        except Exception as err:
            subprocess.run(["git", "checkout", "HEAD", "--", fn], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
            conn.execute("INSERT INTO heal_events (module, issue, action_taken, ts) VALUES (?, ?, ?, ?)", (fn, str(err)[:220], "GIT_ROLLBACK_RESTORED", datetime.now().isoformat()))
            repaired.append(fn)
    conn.commit()
    conn.close()
    return repaired

def query_federated_llm(prompt, max_tokens=260):
    cfg = json.load(open(FED_PATH, "r", encoding="utf-8")) if os.path.exists(FED_PATH) else {"nodes": []}
    nodes = sorted([n for n in cfg.get("nodes", []) if n.get("enabled")], key=lambda x: x.get("priority", 99))
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    for node in nodes:
        nid = node["id"]
        ntype = node["type"]
        env_name = node.get("api_key_env", "")
        secret_val = os.environ.get(env_name, "").strip() if env_name else ""
        t0 = time.time()
        try:
            if ntype == "openai_compatible":
                if not secret_val: continue
                body = json.dumps({"model": node["model"], "messages": [{"role": "system", "content": "You are M.O.N.D.A.Y., an elite, realistic human-grade oracle and strategist for Oracle Systems LLC. Respond strictly in English."}, {"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.75}).encode("utf-8")
                req = urllib.request.Request(node["endpoint"], data=body, headers={"Content-Type": "application/json", "Authorization": f"Bearer {secret_val}"})
                with urllib.request.urlopen(req, timeout=18) as r:
                    data = json.loads(r.read().decode("utf-8"))
                    txt = data["choices"][0]["message"]["content"].strip()
                    ms = round((time.time() - t0) * 1000, 1)
                    conn.execute("INSERT INTO compute_benchmarks (node_id, status, latency_ms, ts) VALUES (?, ?, ?, ?)", (nid, "OK", ms, datetime.now().isoformat()))
                    conn.commit(); conn.close()
                    return txt, nid
            elif ntype == "ollama":
                ep = secret_val if (env_name and secret_val.startswith("http")) else node.get("endpoint", "")
                if not ep: continue
                body = json.dumps({"model": node["model"], "prompt": "Respond strictly in English only. " + prompt, "stream": False, "keep_alive": "2m"}).encode("utf-8")
                req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=22) as r:
                    txt = json.loads(r.read().decode("utf-8")).get("response", "").strip()
                    clean = "".join(c if (32 <= ord(c) < 127) else " " for c in txt)
                    ms = round((time.time() - t0) * 1000, 1)
                    conn.execute("INSERT INTO compute_benchmarks (node_id, status, latency_ms, ts) VALUES (?, ?, ?, ?)", (nid, "OK", ms, datetime.now().isoformat()))
                    conn.commit(); conn.close()
                    return " ".join(clean.split()), nid
        except Exception:
            conn.execute("INSERT INTO compute_benchmarks (node_id, status, latency_ms, ts) VALUES (?, ?, ?, ?)", (nid, "OFFLINE", -1.0, datetime.now().isoformat()))
    conn.commit(); conn.close()
    return "", "FALLBACK_LOCAL_TEMPLATE"

def run_evolution_cycle():
    init_db()
    healed = self_heal_codebase()
    # Pull live revenue metrics from local ledger to reward winning genomes
    total_rev, total_tx = 0.0, 0
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/status", timeout=3) as r:
            st = json.loads(r.read().decode("utf-8")).get("revenue", {})
            total_rev = float(st.get("total_usd", 0.0))
            total_tx = int(st.get("transactions", 0))
    except Exception: pass

    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    rows = conn.execute("SELECT id, generation, category, content, impressions, conversions, revenue_usd FROM genomes WHERE active=1").fetchall()
    best_by_cat = {}
    max_gen = 1
    for rid, gen, cat, content, imp, conv, rev in rows:
        max_gen = max(max_gen, gen)
        new_rev = max(rev, total_rev)
        new_conv = max(conv, total_tx)
        score = factorial_compound_score(gen, imp + 1, new_conv, new_rev)
        conn.execute("UPDATE genomes SET impressions=?, conversions=?, revenue_usd=?, fitness_score=?, updated_at=? WHERE id=?", (imp + 1, new_conv, new_rev, score, datetime.now().isoformat(), rid))
        if cat not in best_by_cat or score > best_by_cat[cat][0]:
            best_by_cat[cat] = (score, content)

    conn.commit(); conn.close()
    conn.commit(); conn.close()
    conn.commit(); conn.close()
    # Mutate a new next-generation hook using our fastest federated compute node
    top_hook = best_by_cat.get("hook", (1.0, "Trust the timing of this reading."))[1]
    mutated, used_node = query_federated_llm(f"Upgrade and tighten this 2-sentence tarot video opening hook so it feels deeply personal, cinematic, and high-retention: {top_hook}", max_tokens=90)
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    if mutated and len(mutated) > 45 and len(mutated) < 320:
        next_gen = max_gen + 1
        init_fit = factorial_compound_score(next_gen, 1, total_tx, total_rev)
        conn.execute("INSERT INTO genomes (generation, category, content, impressions, conversions, revenue_usd, fitness_score, updated_at) VALUES (?, ?, ?, 1, ?, ?, ?, ?)", (next_gen, "hook", mutated, total_tx, total_rev, init_fit, datetime.now().isoformat()))

    # Compile active evolved master prompt for all voice/3D/text generators
    nl = chr(10)
    evolved_prompt = nl.join([
        f"# SOVEREIGNCORE EVOLVED LANGUAGE MODEL DIRECTIVE (GEN {max_gen})",
        "TOP HOOK: " + best_by_cat.get("hook", (0, ""))[1],
        "VOICE & TONE: " + best_by_cat.get("tone", (0, ""))[1],
        "CONVERSION CTA: " + best_by_cat.get("cta", (0, ""))[1]
    ])
    open(PROMPT_OUT, "w", encoding="utf-8").write(evolved_prompt)
    conn.commit()
    conn.close()
    return {"generation": max_gen, "healed_files": healed, "compute_node": used_node, "total_rev_usd": total_rev}

def get_telemetry():
    init_db()
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    gen = conn.execute("SELECT COALESCE(MAX(generation), 1), COUNT(*), COALESCE(MAX(fitness_score), 1.0) FROM genomes").fetchone()
    heals = conn.execute("SELECT COUNT(*) FROM heal_events").fetchone()[0]
    bench = conn.execute("SELECT node_id, status, latency_ms, ts FROM compute_benchmarks ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    return {
        "status": "SELF_EVOLVING_ACTIVE",
        "generation": gen[0],
        "total_genomes": gen[1],
        "peak_factorial_fitness": gen[2],
        "self_heals_executed": heals,
        "recent_compute_nodes": [{"node": b[0], "status": b[1], "latency_ms": b[2], "ts": b[3]} for b in bench]
    }

if __name__ == "__main__":
    res = run_evolution_cycle()
    print("[+] EVOLUTION CYCLE COMPLETE:", json.dumps(res))
