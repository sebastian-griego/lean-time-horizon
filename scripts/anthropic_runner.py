from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def extract_lean(text: str) -> str:
    match = re.search(r"```(?:lean)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip() + "\n"
    return text.strip() + "\n"


def main() -> int:
    key = os.environ.get("ANTHROPIC_API_KEY")
    prompt_path = os.environ.get("PROMPT_PATH")
    model = os.environ.get("MODEL")
    if not key:
        print("ANTHROPIC_API_KEY is not set", file=sys.stderr)
        return 2
    if not prompt_path or not model:
        print("PROMPT_PATH and MODEL must be set", file=sys.stderr)
        return 2

    prompt = Path(prompt_path).read_text(encoding="utf-8")
    payload = {
        "model": model,
        "max_tokens": int(os.environ.get("ANTHROPIC_MAX_TOKENS", "4096")),
        "temperature": float(os.environ.get("ANTHROPIC_TEMPERATURE", "0")),
        "messages": [{"role": "user", "content": prompt}],
    }
    request = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": os.environ.get("ANTHROPIC_VERSION", "2023-06-01"),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=int(os.environ.get("ANTHROPIC_TIMEOUT_SECONDS", "120"))) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(body, file=sys.stderr)
        return 1

    text_parts = [block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"]
    print(extract_lean("\n".join(text_parts)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
