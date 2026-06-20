# OPEN VS — Developer Security Toolkit

> 116+ security tools in a single Python file — no pip, no setup required. Just run it.

---

## Download & Install

### Windows
```powershell
# 1. Install Python if not already: https://python.org
# 2. Download the file
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/FLEIPLEI/open-vs/main/open_vs.py" -OutFile "open_vs.py"
# 3. Run
python open_vs.py
```

### Linux / macOS
```bash
# Download
wget https://raw.githubusercontent.com/FLEIPLEI/open-vs/main/open_vs.py
# or
curl -O https://raw.githubusercontent.com/FLEIPLEI/open-vs/main/open_vs.py

# Run
python3 open_vs.py
```

### Android (Termux)
```bash
# 1. Install Termux from F-Droid (not Play Store)
# 2. In Termux:
pkg update && pkg install python
curl -O https://raw.githubusercontent.com/FLEIPLEI/open-vs/main/open_vs.py
python open_vs.py
```

### Download as ZIP
Click **Code → Download ZIP** at the top right, extract it, then:
```bash
python open_vs.py
```

---

## What is OPEN VS?

OPEN VS is an all-in-one security toolkit that runs entirely from a single `.py` file. No `pip install`, no virtual environments, no dependencies — just Python 3.8+ and the file.

Start the tool, enter a tool number (e.g. `116`) or search for a keyword (e.g. `admin`) and the tool launches immediately.

---

## Features

- **116 tools** in a single file
- Runs on **Windows, Linux and Android/Termux**
- **Python standard library only** — no pip required
- Clean terminal UI with color output
- Tools keep scanning until something is found (Ctrl+C to stop)
- Detailed reports with step-by-step exploitation and fix instructions

---

## Tool Categories

| Category | Examples |
|----------|----------|
| **Network** | Port scanner, ARP scan, DNS lookup, WHOIS, Traceroute |
| **Web Security** | SQLi tester, XSS finder, Admin bypass, CORS tester, HTTP header analysis |
| **Auth & Bypass** | Admin Auth Bypass (116), Default credentials, Cookie forgery, Header bypass |
| **Passwords** | Hash cracker (MD5/SHA), Password generator, Strength checker |
| **APIs** | JWT analyzer, API security tester, OAuth checker |
| **Minecraft** | MC server scanner, Plugin security check, MOTD analysis |
| **Crypto** | Hash tools, Base64, Caesar cipher, Hex converter |
| **OSINT** | IP info, Domain checker, Email validator, Geo lookup |
| **System** | Port listener, Environment scanner, Process checker |
| **Other** | Fake data generator, QR code, WiFi scanner, and more |

---

## Usage

```
python open_vs.py
```

```
╔══════════════════════════════════════════════════════════════════════════╗
║  OPEN VS — Developer Security Toolkit                                    ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Enter a tool number (1-116) or search by keyword                        ║
╚══════════════════════════════════════════════════════════════════════════╝

> 116
```

- Enter a number → launch tool directly
- Enter a keyword (e.g. `sql`, `port`, `admin`) → show matching tools
- `h` → list all tools
- `q` → quit

---

## Requirements

- Python **3.8 or higher**
- No additional packages needed

---

## Disclaimer

This tool is intended for **authorized security testing and educational purposes only.**
Only use it on systems you own or have explicit permission to test.
The author is not responsible for any misuse.

---

## Platform Support

| Platform | Status |
|----------|--------|
| Windows 10/11 | ✅ Fully supported |
| Linux (Ubuntu, Debian, Arch, ...) | ✅ Fully supported |
| Android (Termux) | ✅ Fully supported |
| macOS | ✅ Should work (untested) |
