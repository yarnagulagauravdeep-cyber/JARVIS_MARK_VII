"""
jarvis_brain.py - Hybrid Cloud + Offline AI Brain with Rate Limit Failover
Uses free Groq endpoints for ultra-fast responses, and smoothly falls back
to offline local processing if API rate limits or network issues occur.
"""

import os
import re
import time
from openai import OpenAI
from dotenv import load_dotenv
import jarvis_actions

# Load .env
load_dotenv()

# Active, verified models available on Groq
MODELS = [
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b"
]

_client = None
_history = []
_cooldown_until = 0.0


def clear_history():
    """Reset LLM context memory."""
    global _history
    _history = []

SYSTEM_PROMPT = """You are Jarvis, a fast, highly capable AI executive assistant running on the user's Windows computer.
You are inspired by Tony Stark's J.A.R.V.I.S from Iron Man.
Respond concisely in 1-2 sentences. Be direct, helpful, witty, and natural.
Address the user as "sir" occasionally.
Do not use filler, disclaimers, or formal corporate jargon.
Keep responses snappy and conversational.
"""


def _get_api_key():
    """Get Groq API key from environment (.env) or config."""
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if key:
        return key

    # Direct parse of .env
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GROQ_API_KEY") and "=" in line:
                        val = line.split("=", 1)[1].strip().strip("'\"")
                        if val:
                            return val
        except Exception:
            pass

    keyfile = os.path.expanduser("~/.openjarvis/free.key")
    if os.path.exists(keyfile):
        try:
            return open(keyfile).read().strip()
        except Exception:
            pass

    return None


def ready():
    """Returns True if the cloud brain is active and not currently rate-limited."""
    key = _get_api_key()
    if not key:
        return False
    return time.time() >= _cooldown_until


def _is_rate_limited(e):
    status = getattr(e, "status_code", None)
    if status == 429:
        return True
    s = str(e).lower()
    return any(w in s for w in ("429", "rate limit", "too many requests", "rate_limit", "exceeded"))


def _retry_after_seconds(e, default=60):
    s = str(e).lower()
    m = re.search(r"try again in\s*(\d+)m\s*([0-9]+(?:\.[0-9]+)?)s", s)
    if m:
        return int(float(m.group(1)) * 60 + float(m.group(2))) + 2
    m = re.search(r"try again in\s*([0-9]+(?:\.[0-9]+)?)s", s)
    if m:
        return int(float(m.group(1))) + 2
    return default


def _set_cooldown(secs):
    global _cooldown_until
    _cooldown_until = max(_cooldown_until, time.time() + float(secs))


def _local_fallback(q):
    """
    Called when Groq API is temporarily rate-limited or offline.
    Executes local desktop actions or returns helpful response.
    """
    action_res = jarvis_actions.try_action(q)
    if action_res:
        return action_res

    return (
        "Cloud API is cooling down, sir, but my local assistant is active. "
        "I can open your desktop apps, type into them, search the web, or check stock markets for you."
    )


def think(q):
    """
    Main entry point for queries.
    1. Tries local deterministic actions first (instant response)
    2. Then tries cloud LLM via Groq with conversation context
    3. Seamlessly falls back if API rate-limited
    """
    global _client, _history

    # 1. Immediate local action check
    local_done = jarvis_actions.try_action(q)
    if local_done:
        return local_done

    key = _get_api_key()
    if not key or time.time() < _cooldown_until:
        return _local_fallback(q)

    if _client is None:
        _client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

    msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + _history[-6:] + [{"role": "user", "content": q}]

    for model in MODELS:
        try:
            resp = _client.chat.completions.create(
                model=model,
                messages=msgs,
                max_tokens=350,
                temperature=0.7,
            )
            answer = resp.choices[0].message.content.strip()
            _history += [{"role": "user", "content": q}, {"role": "assistant", "content": answer}]
            return answer
        except Exception as e:
            if _is_rate_limited(e):
                wait_sec = _retry_after_seconds(e)
                _set_cooldown(wait_sec)
                print(f"[Rate-limit triggered: cooldown for {wait_sec}s]")
                return _local_fallback(q)
            print(f"[Model {model} failed: {e}]")

    return _local_fallback(q)


def generate_document_content(topic):
    """
    Generates a comprehensive, well-structured document on a given topic
    for Microsoft Word export.
    """
    global _client
    key = _get_api_key()
    if not key:
        return f"# {topic.title()}\n\n## Overview\nThis document was prepared by Jarvis regarding {topic}.\n\n## Key Points\n- Overview and background\n- Core analysis\n- Recommendations and next steps\n\n## Conclusion\nGenerated locally by Jarvis."

    if _client is None:
        _client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

    prompt = (
        f"You are an elite executive assistant and professional document writer. "
        f"Write a thorough, professional, and well-structured document about: '{topic}'.\n\n"
        f"Format strictly in clean Markdown:\n"
        f"- Start directly with '# <Document Title>'\n"
        f"- Use '## <Heading>' for major sections\n"
        f"- Use '### <Subheading>' where helpful\n"
        f"- Write detailed, clear paragraphs\n"
        f"- Include bullet points ('- ') for key takeaways\n"
        f"- End with a conclusion or formal sign-off\n"
        f"Do NOT include any chat filler or preamble like 'Here is your document'. Start immediately with the title."
    )

    for model in MODELS:
        try:
            resp = _client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Document generation failed with {model}: {e}]")

    return f"# {topic.title()}\n\n## Overview\nDocument draft on {topic}.\n\n## Summary\nPlease review the details."


if __name__ == "__main__":
    print("Testing Jarvis Brain...")
    print("Time check:", think("what time is it"))
    print("AI Chat check:", think("Hello Jarvis, what can you do?"))
