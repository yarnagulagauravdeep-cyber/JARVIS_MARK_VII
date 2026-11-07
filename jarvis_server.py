"""
jarvis_server.py - FastAPI Backend Server for Jarvis AI Assistant
Serves the holographic HUD, handles voice/text commands, TTS, and real-time state.
This is the MAIN entry point - run this to start Jarvis.
"""

import asyncio
import os
import sys
import time
import json
import threading
import datetime
import queue
import subprocess

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import uvicorn

# Ensure we can import sibling modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import jarvis_brain
import jarvis_actions
import jarvis_market

# ─── Global State ────────────────────────────────────────────────────
state = {
    "state": "idle",
    "note": "System Operational",
    "mode": "HYBRID",
    "model": "Groq / GPT-OSS-20B + Local",
    "last_you": "",
    "last_tool": "",
    "tool_active": False,
    "t_rec": 0.0,
    "t_think": 0.0,
    "tools": 0,
    "facts": 0,
    "mail_age": None,
    "chat": [],
    "cards": [],
    "stocks": [],
    "sys": {},
    "mic": {"n": 0, "a": []},
}

chat_counter = 0
tts_queue = queue.Queue()

# ─── TTS Engine (Dedicated Background Worker with COM support) ───────
def _tts_worker():
    """Background thread that handles speech output safely on Windows."""
    try:
        import pythoncom
        pythoncom.CoInitialize()
    except Exception:
        pass

    eng = None
    try:
        import pyttsx3
        eng = pyttsx3.init()
        voices = eng.getProperty("voices")
        for v in voices:
            name = v.name.lower()
            if "david" in name or "zira" in name or "english" in name:
                eng.setProperty("voice", v.id)
                break
        eng.setProperty("rate", 175)
        eng.setProperty("volume", 0.95)
    except Exception as e:
        print(f"[TTS] pyttsx3 init notice: {e}")

    while True:
        text = tts_queue.get()
        if text is None:
            break

        # Attempt 1: pyttsx3
        spoken = False
        if eng:
            try:
                eng.say(text)
                eng.runAndWait()
                spoken = True
            except Exception:
                pass

        # Attempt 2: Native PowerShell System.Speech (100% fail-proof fallback)
        if not spoken:
            try:
                clean_text = text.replace('"', '`"').replace("'", "''")
                cmd = f'Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Rate = 1; $s.Speak("{clean_text}")'
                subprocess.run(['powershell', '-NoProfile', '-Command', cmd],
                               capture_output=True, timeout=12)
            except Exception:
                pass


def speak(text):
    """Queue text for speech output (non-blocking)."""
    if text:
        tts_queue.put(text)


# ─── Chat & State Helpers ────────────────────────────────────────────
def add_chat(kind, text):
    """Add a message to the chat log. kind = 'you', 'jarvis', or 'sys'."""
    global chat_counter
    chat_counter += 1
    msg = {
        "i": chat_counter,
        "k": kind,
        "x": text,
        "t": datetime.datetime.now().strftime("%H:%M:%S"),
    }
    state["chat"].append(msg)
    if len(state["chat"]) > 100:
        state["chat"] = state["chat"][-100:]


def set_state(s, note=None):
    """Update UI state."""
    state["state"] = s
    if note:
        state["note"] = note


def get_system_vitals():
    """Get CPU, RAM, disk, battery info."""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/")
        disk_free = round(disk.free / (1024 ** 3), 1)
        disk_pct = disk.percent

        result = {
            "cpu": cpu,
            "ram": ram,
            "disk": disk_pct,
            "free": disk_free,
        }

        bat = psutil.sensors_battery()
        if bat:
            result["bat"] = bat.percent
            result["plug"] = bat.power_plugged

        boot = psutil.boot_time()
        result["up"] = int(time.time() - boot)

        return result
    except Exception:
        return {"cpu": 0, "ram": 0, "disk": 0, "free": 0}


# ─── Process a user query ───────────────────────────────────────────
def process_query(text, backend_speak=True):
    """Process a user's voice/text command and return the response."""
    global state

    text = text.strip()
    if not text:
        return ""

    # Update state
    state["last_you"] = text
    add_chat("you", text)
    set_state("thinking", f"Processing: {text[:35]}...")

    t0 = time.time()

    # Get response from brain (local actions + Groq cloud failover)
    try:
        response = jarvis_brain.think(text)
    except Exception as e:
        response = f"I encountered an issue processing that, sir: {str(e)[:100]}"
        print(f"[ERROR] Brain error: {e}")

    elapsed = time.time() - t0
    state["t_think"] = round(elapsed, 2)
    state["tools"] = state.get("tools", 0) + 1
    state["last_tool"] = "Executed Action"

    # Add to chat
    add_chat("jarvis", response)
    set_state("speaking", "Jarvis Responding")

    # Speak on the backend only if requested (browser speaks for HUD requests)
    if backend_speak:
        speak(response)

    # After speaking, transition back to listening
    def reset_state():
        time.sleep(max(1.2, len(response) * 0.05))
        set_state("listening", "Ready")

    threading.Thread(target=reset_state, daemon=True).start()

    return response


# ─── Stock Market Background Refresh ─────────────────────────────────
def refresh_stocks():
    """Fetch live stock data in background."""
    try:
        stocks = []
        for sym, name in jarvis_market.DEFAULT_TICKERS.items():
            data = jarvis_market.analyze_ticker(sym)
            if data:
                chart = jarvis_market._fetch_chart(sym)
                spark = []
                if chart:
                    quotes = chart.get("indicators", {}).get("quote", [{}])[0].get("close", [])
                    spark = [q for q in quotes[-20:] if q is not None]

                stocks.append({
                    "sym": sym,
                    "name": name,
                    "price": data["price"],
                    "pct": data["pct_change"],
                    "spark": spark,
                    "above": data["signal"] in ("STRONG BUY", "BUY / ACCUMULATE"),
                    "mom": data["pct_change"],
                    "signal": data["signal"],
                    "stale": False,
                    "err": False,
                })
            else:
                stocks.append({
                    "sym": sym,
                    "name": name,
                    "price": 0,
                    "pct": 0,
                    "spark": [],
                    "above": False,
                    "mom": 0,
                    "signal": "OFFLINE",
                    "stale": True,
                    "err": True,
                })
        state["stocks"] = stocks
    except Exception as e:
        print(f"[Stocks] Error fetching market data: {e}")


def stock_refresh_loop():
    """Periodically refresh stock data."""
    while True:
        refresh_stocks()
        time.sleep(120)


# ─── FastAPI Application ─────────────────────────────────────────────
app = FastAPI(title="Jarvis AI Assistant", version="2.0")


@app.on_event("startup")
async def startup():
    # Start TTS worker thread
    tts_thread = threading.Thread(target=_tts_worker, daemon=True)
    tts_thread.start()

    # Start stock refresh loop
    stock_thread = threading.Thread(target=stock_refresh_loop, daemon=True)
    stock_thread.start()

    # Initial system vitals
    set_state("starting", "Calibrating systems...")
    state["sys"] = get_system_vitals()

    # Initial Welcome message
    add_chat("sys", "Jarvis AI Assistant initialized. All neural cores armed.")
    welcome_text = "Good day, sir. All systems are operational. What can I do for you?"
    add_chat("jarvis", welcome_text)
    speak("Jarvis online. All systems operational.")

    await asyncio.sleep(1.5)
    set_state("listening", "Ready")


NO_CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0"
}


@app.get("/")
async def serve_hud():
    """Serve the holographic HUD frontend with zero caching."""
    hud_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis_workplace.html")
    with open(hud_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(
        content=content,
        headers=NO_CACHE_HEADERS
    )


@app.get("/api/state")
async def get_state():
    """Return current Jarvis state for the HUD to poll."""
    state["sys"] = get_system_vitals()
    return JSONResponse(state, headers=NO_CACHE_HEADERS)


@app.post("/api/command")
async def post_command(data: dict):
    """Receive a command from the HUD text input or continuous voice recognition."""
    text = data.get("text", "").strip()
    # Browser HUD handles speech synthesis itself with natural voice, so backend_speak=False avoids echo
    backend_speak = data.get("backend_speak", False)
    if not text:
        return JSONResponse({"reply": ""}, headers=NO_CACHE_HEADERS)

    response = process_query(text, backend_speak=backend_speak)
    return JSONResponse({"reply": response}, headers=NO_CACHE_HEADERS)


@app.post("/api/chat/clear")
@app.get("/api/chat/clear")
async def clear_chat():
    """Clear chat stream, reset counter and AI conversation history, and start a fresh session."""
    global chat_counter
    state["chat"] = []
    chat_counter = 0
    jarvis_brain.clear_history()
    add_chat("sys", "Chat history cleared. All neural cores re-armed.")
    add_chat("jarvis", "Ready for a fresh session, sir. What can I do for you?")
    return JSONResponse({"ok": True, "chat": state["chat"]}, headers=NO_CACHE_HEADERS)


@app.get("/api/stocks")
async def get_stocks():
    return JSONResponse(state.get("stocks", []), headers=NO_CACHE_HEADERS)


if __name__ == "__main__":
    print()
    print("=" * 65)
    print("  J.A.R.V.I.S  AI  ASSISTANT  ·  MARK VII")
    print("=" * 65)
    print()
    print("  ✓ Groq Cloud AI Brain: Active")
    print("  ✓ Windows Desktop Automation & App Discovery: Ready")
    print("  ✓ In-App Keyboard & Typing Engine: Loaded")
    print("  ✓ Text-to-Speech Engine: Armed")
    print()
    print("  Server URL: http://localhost:8000")
    print("  Open this URL in Google Chrome or Microsoft Edge")
    print("=" * 65)
    print()

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
