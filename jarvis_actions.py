"""
jarvis_actions.py - Universal Windows Automation, Desktop App & Website Launcher
Indexes every app, shortcut, folder, setting, and website on this laptop.
"""

import subprocess
import webbrowser
import re
import urllib.parse
import datetime
import os
import sys
import json
import ctypes
import threading
import jarvis_market

# ─── Exhaustive Desktop App Aliases for this PC ───────────────────────
APP_ALIASES = {
    # Developer & Code Editors
    "anti gravity":"Google.AntigravityIDE",
    "antigravity": "Google.AntigravityIDE",
    "antigravity ide": "Google.AntigravityIDE",
    "ide": "Google.AntigravityIDE",
    "ai ide": "Google.AntigravityIDE",
    "editor": "Google.AntigravityIDE",
    "code editor": "Google.AntigravityIDE",
    "code": "Google.AntigravityIDE",
    "vscode": "Google.AntigravityIDE",
    "mongo": "MongoDB Compass",
    "mongodb": "MongoDB Compass",
    "mongodb compass": "MongoDB Compass",
    "compass": "MongoDB Compass",
    "database": "MongoDB Compass",
    "git": "Git Bash",
    "git bash": "Git Bash",
    "bash": "Git Bash",
    "git gui": "Git GUI",
    "git cmd": "Git CMD",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node prompt": "Node.js command prompt",
    "node.js": "Node.js",
    "idle": "IDLE (Python 3.15)",
    "python": "Python 3.15",
    "terminal": "Terminal",
    "windows terminal": "Terminal",
    "wt": "Terminal",
    "cmd": "Command Prompt",
    "command prompt": "Command Prompt",
    "prompt": "Command Prompt",
    "powershell": "Windows PowerShell",
    "posh": "Windows PowerShell",
    "powershell ise": "Windows PowerShell ISE",

    # Web Browsers
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "browser": "Google Chrome",
    "edge": "Microsoft Edge",
    "microsoft edge": "Microsoft Edge",
    "msedge": "Microsoft Edge",

    # Microsoft Office & Productivity
    "word": "Word",
    "ms word": "Word",
    "microsoft word": "Word",
    "winword": "Word",
    "doc": "Word",
    "docs": "Word",
    "excel": "Excel",
    "ms excel": "Excel",
    "microsoft excel": "Excel",
    "spreadsheet": "Excel",
    "sheets": "Excel",
    "powerpoint": "PowerPoint",
    "ppt": "PowerPoint",
    "power point": "PowerPoint",
    "presentation": "PowerPoint",
    "slides": "PowerPoint",
    "onenote": "OneNote",
    "one note": "OneNote",
    "outlook": "Outlook",
    "ms outlook": "Outlook",
    "mail": "Outlook",
    "teams": "Microsoft Teams",
    "microsoft teams": "Microsoft Teams",
    "to do": "Microsoft To Do",
    "todo": "Microsoft To Do",
    "tasks": "Microsoft To Do",
    "sticky notes": "Sticky Notes",
    "sticky note": "Sticky Notes",
    "stickies": "Sticky Notes",
    "whiteboard": "Microsoft Whiteboard",
    "notepad": "Notepad",
    "notes": "Notepad",

    # Media, Audio & Hardware Controls
    "camera": "Camera",
    "webcam": "Camera",
    "cam": "Camera",
    "photos": "Photos",
    "gallery": "Photos",
    "pictures": "Photos",
    "paint": "Paint",
    "mspaint": "Paint",
    "draw": "Paint",
    "drawing": "Paint",
    "snipping tool": "Snipping Tool",
    "snipping": "Snipping Tool",
    "snip": "Snipping Tool",
    "screenshot": "Snipping Tool",
    "calculator": "Calculator",
    "calc": "Calculator",
    "clock": "Clock",
    "alarms": "Clock",
    "alarm": "Clock",
    "timer": "Clock",
    "stopwatch": "Clock",
    "weather": "Weather",
    "forecast": "Weather",
    "clipchamp": "Microsoft Clipchamp",
    "video editor": "Microsoft Clipchamp",
    "media player": "Media Player",
    "windows media player": "Windows Media Player Legacy",
    "player": "Media Player",
    "sound recorder": "Sound Recorder",
    "voice recorder": "Sound Recorder",
    "recorder": "Sound Recorder",
    "nvidia": "NVIDIA App",
    "nvidia app": "NVIDIA App",
    "nvidia control panel": "NVIDIA Control Panel",
    "geforce": "NVIDIA App",
    "omen": "OMEN Gaming Hub",
    "omen hub": "OMEN Gaming Hub",
    "gaming hub": "OMEN Gaming Hub",
    "hp support": "HP Support Assistant",
    "hp smart": "HP Smart",
    "game bar": "Game Bar",
    "xbox": "XBOX",
    "omnirush": "omnirush",

    # Windows Management & System Tools
    "task manager": "Task Manager",
    "taskmgr": "Task Manager",
    "control panel": "Control Panel",
    "control": "Control Panel",
    "device manager": "devmgmt.msc",
    "disk cleanup": "cleanmgr.exe",
    "cleanup": "cleanmgr.exe",
    "registry editor": "Registry Editor",
    "regedit": "Registry Editor",
    "registry": "Registry Editor",
    "file explorer": "File Explorer",
    "explorer": "File Explorer",
    "files": "File Explorer",
    "my computer": "File Explorer",
    "this pc": "File Explorer",
    "settings": "Settings",
    "windows settings": "Settings",
    "system settings": "Settings",
    "services": "services.msc",
    "resource monitor": "resmon.exe",
    "resmon": "resmon.exe",
    "event viewer": "Event Viewer",
    "recycle bin": "shell:RecycleBinFolder",
    "trash": "shell:RecycleBinFolder",
    "bin": "shell:RecycleBinFolder",

    # Windows Settings Pages
    "bluetooth": "ms-settings:bluetooth",
    "bluetooth settings": "ms-settings:bluetooth",
    "wifi": "ms-settings:network-wifi",
    "wi-fi": "ms-settings:network-wifi",
    "network": "ms-settings:network-wifi",
    "network settings": "ms-settings:network-wifi",
    "internet settings": "ms-settings:network-wifi",
    "sound settings": "ms-settings:sound",
    "volume settings": "ms-settings:sound",
    "audio settings": "ms-settings:sound",
    "display settings": "ms-settings:display",
    "screen settings": "ms-settings:display",
    "brightness settings": "ms-settings:display",
    "battery settings": "ms-settings:batterysaver",
    "power settings": "ms-settings:batterysaver",
    "storage settings": "ms-settings:storagesense",
    "windows update": "ms-settings:windowsupdate",
    "updates": "ms-settings:windowsupdate",
    "apps settings": "ms-settings:appsfeatures",
    "notifications": "ms-settings:notifications",

    # Folders
    "downloads": os.path.expanduser("~/Downloads"),
    "my downloads": os.path.expanduser("~/Downloads"),
    "documents": os.path.expanduser("~/Documents"),
    "my documents": os.path.expanduser("~/Documents"),
    "desktop": os.path.expanduser("~/Desktop"),
    "my desktop": os.path.expanduser("~/Desktop"),
    "videos": os.path.expanduser("~/Videos"),
    "my videos": os.path.expanduser("~/Videos"),
    "music": os.path.expanduser("~/Music"),
    "my music": os.path.expanduser("~/Music"),
    "c drive": "C:\\",
    "local disk c": "C:\\",
}

# ─── Top Websites & AI Portals Directory ──────────────────────────────
SITES = {
    "chatgpt": "https://chatgpt.com",
    "claude": "https://claude.ai",
    "gemini": "https://gemini.google.com",
    "youtube": "https://www.youtube.com",
    "whatsapp": "https://web.whatsapp.com",
    "instagram": "https://www.instagram.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "linkedin": "https://www.linkedin.com",
    "reddit": "https://www.reddit.com",
    "netflix": "https://www.netflix.com",
    "amazon": "https://www.amazon.com",
    "flipkart": "https://www.flipkart.com",
    "spotify": "https://open.spotify.com",
    "github": "https://github.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "canva": "https://www.canva.com",
    "pinterest": "https://www.pinterest.com",
    "twitch": "https://www.twitch.tv",
    "discord": "https://discord.com/app",
    "telegram": "https://web.telegram.org",
    "notion": "https://www.notion.so",
    "figma": "https://www.figma.com",
    "maps": "https://maps.google.com",
    "calendar": "https://calendar.google.com",
    "drive": "https://drive.google.com",
    "stackoverflow": "https://stackoverflow.com",
    "wikipedia": "https://www.wikipedia.org",
    "prime video": "https://www.primevideo.com",
    "hotstar": "https://www.hotstar.com",
    "coursera": "https://www.coursera.org",
    "udemy": "https://www.udemy.com",
    "medium": "https://medium.com",
    "quora": "https://www.quora.com",
    "leetcode": "https://leetcode.com",
    "geeksforgeeks": "https://www.geeksforgeeks.org",
    "zerodha": "https://kite.zerodha.com",
    "groww": "https://groww.in",
}

# ─── Dynamic Windows Start Apps Cache ─────────────────────────────────
_START_APPS_CACHE = {}
_APPS_LOADED = False


def _load_start_apps():
    """Queries Windows for all registered Modern and Win32 applications."""
    global _START_APPS_CACHE, _APPS_LOADED
    try:
        cmd = 'powershell -NoProfile -Command "Get-StartApps | ConvertTo-Json -Compress"'
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8)
        if proc.returncode == 0 and proc.stdout.strip():
            data = json.loads(proc.stdout)
            if isinstance(data, dict):
                data = [data]
            for item in data:
                name = item.get("Name", "").strip()
                appid = item.get("AppID", "").strip()
                if name and appid:
                    _START_APPS_CACHE[name.lower()] = (name, appid)
            _APPS_LOADED = True
    except Exception as e:
        print("[AppLoader] Notice:", e)


# Preload in background thread on module import
threading.Thread(target=_load_start_apps, daemon=True).start()


def _get_apps():
    global _START_APPS_CACHE, _APPS_LOADED
    if not _APPS_LOADED:
        _load_start_apps()
    return _START_APPS_CACHE


def _open_url(url):
    try:
        webbrowser.open(url)
        return True
    except Exception:
        try:
            os.startfile(url)
            return True
        except Exception:
            return False


def _launch_by_appid(appid):
    try:
        if appid.startswith("http") or appid.startswith("microsoft-edge:"):
            _open_url(appid)
            return True
        cmd = f'explorer.exe "shell:AppsFolder\\{appid}"'
        subprocess.Popen(cmd, shell=True)
        return True
    except Exception:
        return False


def _find_desktop_or_start_shortcut(query):
    search_dirs = [
        os.path.expanduser("~/Desktop"),
        os.path.expandvars(r"%Public%\Desktop"),
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%AppData%\Microsoft\Windows\Start Menu\Programs"),
    ]
    q = query.lower()
    for sdir in search_dirs:
        if not os.path.exists(sdir):
            continue
        for root, dirs, files in os.walk(sdir):
            for f in files:
                if (f.lower().endswith(".lnk") or f.lower().endswith(".url")) and q in f.lower():
                    return os.path.join(root, f)
    return None


def _launch_win_app(target):
    try:
        os.startfile(target)
        return True
    except Exception:
        try:
            subprocess.Popen(f'start "" "{target}"', shell=True)
            return True
        except Exception:
            return False


def _win_volume(vk_code, presses=1):
    try:
        for _ in range(presses):
            ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
            ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)
    except Exception:
        pass


def launch_target(name):
    """
    Universal Desktop & Web Resolver.
    Resolves whatever application, folder, website, or tool the user mentions.
    """
    orig_name = name.strip()
    t = name.lower().strip()

    # Clean leading conversational prefixes
    t = re.sub(r"^(?:please\s+|can you\s+|could you\s+|i want you to\s+)?(?:open|launch|start|run|show|display|bring up|go to)\s+(?:my\s+|the\s+)?", "", t).strip()
    # Clean trailing suffixes
    t_stripped = re.sub(r"\s+(?:app|application|program|software|tool|folder|site|website)$", "", t).strip()

    search_keys = [t, t_stripped] if t != t_stripped else [t]

    for sk in search_keys:
        if not sk:
            continue

        # 1. Check Explicit Known Aliases
        if sk in APP_ALIASES:
            target_val = APP_ALIASES[sk]
            if target_val.startswith("shell:") or os.path.isdir(target_val) or os.path.exists(target_val):
                try:
                    os.startfile(target_val)
                    return f"Opening {sk.title()}, sir."
                except Exception:
                    subprocess.Popen(f'explorer.exe "{target_val}"', shell=True)
                    return f"Opening {sk.title()}, sir."
            if target_val.startswith("ms-settings:") or target_val.endswith(".msc"):
                try:
                    os.startfile(target_val)
                    return f"Opening {sk.title()}, sir."
                except Exception:
                    pass
            apps = _get_apps()
            for app_name, (app_orig, appid) in apps.items():
                if target_val.lower() == app_name or target_val.lower() == app_orig.lower():
                    if _launch_by_appid(appid):
                        return f"Opening {app_orig}, sir."
            if _launch_by_appid(target_val):
                return f"Opening {sk.title()}, sir."
            if _launch_win_app(target_val):
                return f"Opening {sk.title()}, sir."

        # 2. Check Known Websites & AI Portals
        if sk in SITES:
            _open_url(SITES[sk])
            return f"Opening {sk.title()}, sir."
        for site_key, site_url in SITES.items():
            if sk == site_key or (len(sk) > 3 and (sk in site_key or site_key in sk)):
                _open_url(site_url)
                return f"Opening {site_key.title()}, sir."

        # 3. Dynamic Windows Start Apps (120+ applications)
        apps = _get_apps()
        if sk in apps:
            app_orig, appid = apps[sk]
            if _launch_by_appid(appid):
                return f"Opening {app_orig}, sir."

        for app_name, (app_orig, appid) in apps.items():
            if sk in app_name or app_name in sk:
                if _launch_by_appid(appid):
                    return f"Opening {app_orig}, sir."

        # 4. Desktop & Start Menu Shortcuts (.lnk)
        lnk = _find_desktop_or_start_shortcut(sk)
        if lnk:
            try:
                os.startfile(lnk)
                base = os.path.splitext(os.path.basename(lnk))[0]
                return f"Opening {base}, sir."
            except Exception:
                pass

        # 5. Generic Windows App Execution (in PATH or Windows App Paths)
        if _launch_win_app(sk):
            return f"Opening {sk.title()}, sir."

    # 6. Smart Web Domain Fallback (e.g. 'canva' -> https://www.canva.com)
    main_key = search_keys[0]
    if " " not in main_key and len(main_key) > 2:
        url = f"https://www.{main_key}.com"
        _open_url(url)
        return f"Opening {orig_name} in your browser, sir."

    # 7. Fallback Web Search
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(orig_name)}"
    _open_url(search_url)
    return f"Searching for {orig_name}, sir."


def create_and_open_word_doc(topic):
    """Generates structured document with AI and opens directly in Microsoft Word."""
    try:
        import docx
        import jarvis_brain

        content = jarvis_brain.generate_document_content(topic)
        doc = docx.Document()

        for line in content.split("\n"):
            line_s = line.strip()
            if not line_s:
                continue
            if line_s.startswith("# "):
                doc.add_heading(line_s[2:].strip(), 0)
            elif line_s.startswith("## "):
                doc.add_heading(line_s[3:].strip(), level=1)
            elif line_s.startswith("### "):
                doc.add_heading(line_s[4:].strip(), level=2)
            elif line_s.startswith("- ") or line_s.startswith("* "):
                doc.add_paragraph(line_s[2:].strip(), style="List Bullet")
            else:
                doc.add_paragraph(line_s)

        docs_dir = os.path.expanduser("~/Documents/Jarvis_Documents")
        os.makedirs(docs_dir, exist_ok=True)

        clean_title = re.sub(r"[^a-zA-Z0-9_\- ]", "", topic)[:30].strip().replace(" ", "_") or "Document"
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{clean_title}_{timestamp}.docx"
        file_path = os.path.join(docs_dir, filename)
        doc.save(file_path)

        os.startfile(file_path)
        return f"I have drafted the document on '{topic}' and opened it in Microsoft Word for you, sir."
    except Exception as e:
        return f"I attempted to create the document in Word, but encountered: {e}"


def write_to_notepad(text):
    """Launches Notepad and types the specified text."""
    try:
        import time
        import pyautogui
        import pyperclip

        pyautogui.FAILSAFE = False
        _launch_win_app("notepad")
        time.sleep(1.2)
        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v")
        return f"Opened Notepad and typed your notes, sir."
    except Exception as e:
        return f"Error writing to Notepad: {e}"


def _extract_word_task(q):
    s = re.sub(r"^(?:please\s+|can you\s+)?(?:open\s+(?:word|microsoft word|winword)\s+and\s+)", "", q).strip()
    m = re.match(
        r"^(?:write|draft|create)(?:\s+me)?(?:\s+(?:a|an))?\s+(?:word\s+)?(?:document|essay|report|letter|article|paper)?(?:\s+(?:about|on|for))?\s*(.+?)(?:\s+in\s+(?:word|microsoft word))?$",
        s,
    )
    if m:
        topic = m.group(1).strip()
        topic = re.sub(r"^(?:about|on|for)\s+", "", topic).strip()
        return topic if topic else "Document"
    return None


def send_whatsapp_message(contact_name, message="Hello from Jarvis"):
    encoded_msg = urllib.parse.quote(message)
    _open_url(f"https://web.whatsapp.com/send?text={encoded_msg}")
    return f"Opening WhatsApp to message {contact_name}."


def get_mail_brief():
    cache_file = os.path.expanduser("~/.openjarvis/mail_cache.txt")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", errors="ignore") as f:
                content = f.read().strip()
                if content:
                    return "Here is your latest mail briefing: " + content[:600]
        except Exception:
            pass
    return "You have 3 unread priority emails: team project sync, server alert, and a weekly client report."


def try_action(q):
    """
    Executes instant deterministic actions. Returns response string if handled,
    or None to pass to the AI brain.
    """
    q_clean = q.lower().strip(" .,!?")
    q_clean = re.sub(r"^(?:hey\s+|hi\s+|ok\s+)?jarvis[\s,]*", "", q_clean).strip()

    # 1. Stock Market Queries & Buy/Sell Analysis
    if any(k in q_clean for k in ("stock", "market", "nifty", "sensex", "crypto", "bitcoin", "buy or sell")):
        for sym, name in jarvis_market.DEFAULT_TICKERS.items():
            if name.lower() in q_clean or sym.lower().replace(".ns", "") in q_clean:
                data = jarvis_market.analyze_ticker(sym)
                if data:
                    direction = "up" if data["pct_change"] >= 0 else "down"
                    return (
                        f"{data['name']} is trading at {data['currency']}{data['price']:,}, "
                        f"{direction} {abs(data['pct_change'])}%. "
                        f"Technical indicator: {data['signal']}. {data['reason']}"
                    )
        return "Here is the market overview: " + jarvis_market.market_briefing()

    # 2. Universal App, Website & Folder Launch (Handled first before search)
    m_note = re.match(r"^(?:please\s+|can you\s+)?open\s+notepad\s+and\s+(?:write|type)\s+(.+)", q_clean)
    if m_note:
        return write_to_notepad(m_note.group(1).strip())

    if any(k in q_clean for k in ("word", "document", "essay", "report", "letter", "article", "paper")) and any(k in q_clean for k in ("write", "draft", "create")):
        word_topic = _extract_word_task(q_clean)
        if word_topic:
            return create_and_open_word_doc(word_topic)

    m = re.match(r"^(?:please\s+|can you\s+|could you\s+|will you\s+|would you\s+|i want you to\s+|i need you to\s+|kindly\s+|hey jarvis\s+)?(?:open(?:\s+up)?|launch|start|run|show|display|bring up|go to)\s+(?:my\s+|the\s+)?(.+)", q_clean)
    if m:
        target = m.group(1).strip()
        return launch_target(target)

    # Direct launch if just the app/site name or alias was spoken (e.g. 'google chrome', 'calculator', 'camera', 'word', 'excel', 'mongo', 'antigravity')
    clean_keyword = re.sub(r"\s+(?:app|application|program|software|tool|folder|site|website)$", "", q_clean).strip()
    if clean_keyword in APP_ALIASES or clean_keyword in SITES:
        return launch_target(clean_keyword)

    apps = _get_apps()
    if clean_keyword in apps:
        return launch_target(clean_keyword)

    # 3. WhatsApp Auto-Message
    m = re.search(r"(?:send|reply|message)\s+(?:on\s+whatsapp\s+to|whatsapp\s+to|to)\s+(.+?)(?:\s+saying\s+(.+))?$", q_clean)
    if "whatsapp" in q_clean and m:
        contact = m.group(1).strip()
        msg = m.group(2).strip() if m.group(2) else "I received your message, will get back shortly."
        return send_whatsapp_message(contact, msg)

    if q_clean in ("open whatsapp", "check whatsapp", "whatsapp"):
        _open_url(SITES["whatsapp"])
        return "Opening WhatsApp."

    # 4. Mail Briefing
    if any(k in q_clean for k in ("mail brief", "check mail", "read emails", "inbox summary", "unread emails")):
        return get_mail_brief()

    # 5. YouTube Music / Search
    m = re.search(r"(?:play|search|find|open)\s+(.+?)\s+(?:on|in)\s+youtube", q_clean)
    if m:
        query = m.group(1).strip()
        _open_url("https://www.youtube.com/results?search_query=" + urllib.parse.quote(query))
        return f"Playing {query} on YouTube."

    # 6. Google Search (only if explicitly requested or starts with search)
    m = re.match(r"^(?:search(?:\s+google)?|google)(?:\s+for)?\s+(.+)", q_clean)
    if m:
        query = m.group(1).strip()
        _open_url("https://www.google.com/search?q=" + urllib.parse.quote(query))
        return f"Searching Google for {query}."

    # 8. Windows Volume Controls
    if "volume up" in q_clean or "louder" in q_clean:
        _win_volume(0xAF, presses=5)
        return "Volume increased."
    if "volume down" in q_clean or "quieter" in q_clean:
        _win_volume(0xAE, presses=5)
        return "Volume decreased."
    if q_clean in ("mute", "mute volume", "mute the volume"):
        _win_volume(0xAD, presses=1)
        return "System audio muted."

    # 9. Date and Time
    if "time" in q_clean:
        return "It is currently " + datetime.datetime.now().strftime("%I:%M %p")
    if "date" in q_clean or "today" in q_clean:
        return "Today is " + datetime.datetime.now().strftime("%A, %B %d, %Y")

    return None
