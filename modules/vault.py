import os, json, base64, hashlib, ctypes
from ctypes import wintypes
BASE_DIR = r"C:\Users\toome\Desktop\SovereignCore" if os.name == "nt" and os.path.exists(r"C:\Users\toome\Desktop\SovereignCore") else os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VAULT_PATH = os.path.join(BASE_DIR, "config", "vault.enc.json")
class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]
def _xor(b):
    k = hashlib.sha256(os.environ.get("SOVEREIGN_API_KEY", "SovereignKey").encode()).digest()
    return bytes([x ^ k[i % len(k)] for i, x in enumerate(b)])
def dpapi_encrypt(text):
    raw = str(text).encode("utf-8")
    if os.name == "nt":
        buf = ctypes.create_string_buffer(raw, len(raw))
        bi = DATA_BLOB(len(raw), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))
        bo = DATA_BLOB()
        if ctypes.windll.crypt32.CryptProtectData(ctypes.byref(bi), None, None, None, None, 0, ctypes.byref(bo)):
            res = ctypes.string_at(bo.pbData, bo.cbData)
            ctypes.windll.kernel32.LocalFree(bo.pbData)
            return "DPAPI:" + base64.b64encode(res).decode("ascii")
    return "CLOUD:" + base64.b64encode(_xor(raw)).decode("ascii")
def dpapi_decrypt(cipher):
    if str(cipher).startswith("CLOUD:"):
        return _xor(base64.b64decode(cipher[6:])).decode("utf-8")
    b = base64.b64decode(cipher[6:] if str(cipher).startswith("DPAPI:") else cipher)
    if os.name == "nt":
        buf = ctypes.create_string_buffer(b, len(b))
        bi = DATA_BLOB(len(b), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))
        bo = DATA_BLOB()
        if ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(bi), None, None, None, None, 0, ctypes.byref(bo)):
            res = ctypes.string_at(bo.pbData, bo.cbData)
            ctypes.windll.kernel32.LocalFree(bo.pbData)
            return res.decode("utf-8")
    return ""
def _load():
    if not os.path.exists(VAULT_PATH): return {}
    try: return json.load(open(VAULT_PATH, "r", encoding="utf-8"))
    except Exception: return {}
def set_secret(k, v):
    if not k or v is None: return
    os.makedirs(os.path.dirname(VAULT_PATH), exist_ok=True)
    s = _load()
    s[str(k)] = dpapi_encrypt(str(v))
    json.dump(s, open(VAULT_PATH, "w", encoding="utf-8"), indent=2)
def get_secret(k):
    s = _load()
    if k not in s: return os.environ.get(k)
    try: return dpapi_decrypt(s[k])
    except Exception: return os.environ.get(k)
def list_secret_keys():
    return list(_load().keys())