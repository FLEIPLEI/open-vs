# OPEN VS — Developer Security Toolkit

> Ein einzelnes Python-Script mit 116+ Sicherheits-Tools für Entwickler, Pentester und Security-Researcher. Keine Installation, keine Dependencies — einfach starten.

---

## Download & Start

### Windows
```powershell
# 1. Python installieren falls noch nicht: https://python.org
# 2. Datei herunterladen
curl -O https://raw.githubusercontent.com/FLEIPLEI/open-vs/main/open_vs.py
# 3. Starten
python open_vs.py
```

### Linux / macOS
```bash
# 1. Herunterladen
wget https://raw.githubusercontent.com/FLEIPLEI/open-vs/main/open_vs.py
# oder
curl -O https://raw.githubusercontent.com/FLEIPLEI/open-vs/main/open_vs.py

# 2. Starten
python3 open_vs.py
```

### Android (Termux)
```bash
# 1. Termux aus F-Droid installieren (nicht Play Store)
# 2. In Termux:
pkg update && pkg install python
curl -O https://raw.githubusercontent.com/FLEIPLEI/open-vs/main/open_vs.py
python open_vs.py
```

### Oder als ZIP herunterladen
Oben rechts auf **Code → Download ZIP** klicken, entpacken, dann:
```bash
python open_vs.py
```

---

## Was ist OPEN VS?

OPEN VS ist ein All-in-One Security Toolkit das komplett in einer einzigen `.py` Datei läuft. Kein `pip install`, keine virtuellen Umgebungen, keine Abhängigkeiten — nur Python 3.8+ und die Datei.

Du startest das Tool, gibst eine Tool-Nummer ein (z.B. `116`) oder suchst nach einem Begriff (z.B. `admin`) und das Tool startet sofort.

---

## Features

- **116 Tools** in einer einzigen Datei
- Läuft auf **Windows, Linux und Android/Termux**
- Nur **Python Standard-Library** — kein pip nötig
- Sauberes Terminal-UI mit Farben
- Tools laufen automatisch weiter bis etwas gefunden wird (Ctrl+C zum Stoppen)
- Detaillierte Berichte mit Schritt-für-Schritt Anleitungen

---

## Tool-Kategorien

| Kategorie | Beispiele |
|-----------|-----------|
| **Netzwerk** | Port-Scanner, ARP-Scanner, DNS-Lookup, WHOIS, Traceroute, Nmap-Wrapper |
| **Web Security** | SQLi-Tester, XSS-Finder, Admin-Bypass, CORS-Tester, HTTP-Header-Analyse |
| **Auth & Bypass** | Admin Auth Bypass (116), Default-Creds, Cookie-Forgery, Header-Bypass |
| **Passwörter** | Hash-Cracker (MD5/SHA), Passwort-Generator, Stärke-Check |
| **APIs** | JWT-Analyzer, API-Security-Tester, OAuth-Checker |
| **Minecraft** | MC-Server-Scanner, Plugin-Sicherheits-Check, MOTD-Analyse |
| **Krypto** | Hash-Tools, Base64, Caesar, Hex-Konverter |
| **OSINT** | IP-Info, Domain-Checker, Email-Validator, Geo-Lookup |
| **System** | Port-Listener, Environment-Scanner, Prozess-Checker |
| **Sonstiges** | Fake-Daten-Generator, QR-Code, WiFi-Scanner, uvm. |

---

## Benutzung

```
python open_vs.py
```

```
╔══════════════════════════════════════════════════════════════════════════╗
║  OPEN VS — Developer Security Toolkit                                    ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Tool-Nummer eingeben (1-116) oder Begriff suchen                        ║
╚══════════════════════════════════════════════════════════════════════════╝

> 116
```

- Zahl eingeben → Tool direkt starten
- Begriff eingeben (z.B. `sql`, `port`, `admin`) → passende Tools anzeigen
- `h` → Alle Tools auflisten
- `q` → Beenden

---

## Voraussetzungen

- Python **3.8 oder höher**
- Keine weiteren Pakete nötig

---

## Rechtlicher Hinweis

Dieses Tool ist ausschließlich für **autorisierte Sicherheitstests und Bildungszwecke** gedacht.  
Nutze es nur auf Systemen die dir gehören oder für die du ausdrückliche Genehmigung hast.  
Der Autor übernimmt keine Haftung für Missbrauch.

---

## Plattform-Unterstützung

| Plattform | Status |
|-----------|--------|
| Windows 10/11 | ✅ Vollständig |
| Linux (Ubuntu, Debian, Arch, ...) | ✅ Vollständig |
| Android (Termux) | ✅ Vollständig |
| macOS | ✅ Sollte funktionieren (ungetestet) |
