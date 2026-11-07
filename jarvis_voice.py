"""
jarvis_voice.py - Live Speech Recognition & Audio Response Loop
Listens through your microphone or console, processes commands, and speaks back aloud.
Supports Windows SAPI5 and PowerShell Speech Synthesis.
"""

import sys
import os
import time
import subprocess
import threading

# Ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import jarvis_brain

# ─── Text-to-Speech Engine ───────────────────────────────────────────
_tts_engine = None
_tts_lock = threading.Lock()


def _init_tts():
    """Initialize speech engine safely on Windows."""
    global _tts_engine
    try:
        import pythoncom
        pythoncom.CoInitialize()
    except Exception:
        pass

    try:
        import pyttsx3
        _tts_engine = pyttsx3.init()
        voices = _tts_engine.getProperty("voices")
        for v in voices:
            name = v.name.lower()
            if "david" in name or "zira" in name or "english" in name or "mark" in name:
                _tts_engine.setProperty("voice", v.id)
                break
        _tts_engine.setProperty("rate", 175)
        _tts_engine.setProperty("volume", 0.95)
        return True
    except Exception as e:
        print(f"[TTS] pyttsx3 notice: {e}")
        _tts_engine = None
        return False


def speak(text):
    """Speak text aloud using pyttsx3, with native PowerShell fallback."""
    if not text:
        return
    print(f"\n[JARVIS]: {text}\n")

    # 1. Try pyttsx3
    spoken = False
    if _tts_engine:
        try:
            with _tts_lock:
                _tts_engine.say(text)
                _tts_engine.runAndWait()
                spoken = True
        except Exception:
            pass

    # 2. Native Windows PowerShell Speech fallback (never fails)
    if not spoken:
        try:
            clean_text = text.replace('"', '`"').replace("'", "''")
            cmd = f'Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Rate = 1; $s.Speak("{clean_text}")'
            subprocess.run(['powershell', '-NoProfile', '-Command', cmd],
                           capture_output=True, timeout=12)
        except Exception:
            pass


# ─── Speech Recognition / Audio Loop ──────────────────────────────────
def listen_loop():
    """Voice listener loop with microphone input and graceful text fallback."""
    _init_tts()
    speak("Jarvis online. All systems operational, sir.")

    # Try SpeechRecognition
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8
        mic = sr.Microphone()
    except Exception as e:
        print(f"\n[MIC Notice]: Direct microphone driver (PyAudio) not configured: {e}")
        print("[TIP]: You can use the web HUD at http://localhost:8000 for browser microphone & 3D UI,")
        print("      or type commands directly below.\n")
        text_input_loop()
        return

    with mic as source:
        print()
        print("=" * 60)
        print("  J.A.R.V.I.S  AI  ASSISTANT  IS  LISTENING")
        print("=" * 60)
        print()
        print("  Voice commands you can try:")
        print("    • 'Jarvis, open Chrome'")
        print("    • 'Open Notepad and write meeting notes'")
        print("    • 'Play lofi on YouTube'")
        print("    • 'Stock market report'")
        print("    • 'What time is it?'")
        print("    • 'Volume up' / 'Mute'")
        print()
        print("  Press Ctrl+C to stop")
        print("=" * 60)
        print()
        print("Calibrating microphone for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1.2)
        print("Microphone ready!\n")

    while True:
        try:
            with mic as source:
                print("🎤 Listening... ", end="", flush=True)
                audio = recognizer.listen(source, timeout=8, phrase_time_limit=10)
            print("Processing... ", end="", flush=True)

            t0 = time.time()
            query = recognizer.recognize_google(audio).strip()
            rec_time = time.time() - t0
            print(f"\n✓ You said: \"{query}\" ({rec_time:.1f}s)")

            # Strip wake word
            q_clean = query.lower()
            if "jarvis" in q_clean:
                q_clean = q_clean.replace("jarvis", "").strip(" ,.!?")

            if not q_clean:
                speak("Yes sir, I'm listening.")
                continue

            response = jarvis_brain.think(q_clean)
            speak(response)

        except KeyboardInterrupt:
            print("\nShutting down Jarvis. Goodbye, sir!")
            break
        except Exception:
            # sr.WaitTimeoutError, UnknownValueError, etc.
            continue


def text_input_loop():
    """Text-based interactive console mode."""
    print("=" * 60)
    print("  J.A.R.V.I.S  INTERACTIVE  TERMINAL  MODE")
    print("=" * 60)
    print("  Commands to test:")
    print("    • open notepad and write hello world")
    print("    • open chrome")
    print("    • stock market report")
    print("    • play lofi on youtube")
    print("    • what time is it")
    print("    • volume up")
    print()
    print("  Type 'quit' or 'exit' to shut down.")
    print("=" * 60)
    print()

    while True:
        try:
            user_input = input("You > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "bye", "goodbye"):
                speak("Goodbye, sir. Systems standing down.")
                break

            response = jarvis_brain.think(user_input)
            speak(response)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye, sir!")
            break


if __name__ == "__main__":
    listen_loop()
