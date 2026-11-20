import sys, json
p="C:/Users/toome/Desktop/SovereignCore/VOICE_CONFIG.json"
c=json.load(open(p))
if len(sys.argv)>1 and sys.argv[1].lower() in ("neural","custom"):
 c["mode"]=sys.argv[1].lower(); json.dump(c,open(p,"w"),indent=2)
print("[+] Active Voice Mode:", c["mode"].upper())
