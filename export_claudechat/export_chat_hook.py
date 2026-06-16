#!/usr/bin/env python3
"""
Claude Code hook: auto-export the current session transcript to readable Markdown.

Wired as a Stop hook in ~/.claude/settings.json, so it runs every time Claude
finishes a turn — keeping a live Markdown archive of every conversation.

Reads the hook JSON payload on stdin (transcript_path, cwd, session_id) and writes:
    ~/saved_chats/<project-folder-name>/<mm-dd-yyyy>.md

The date is the session's start date. If a *different* session writes to the same
project on the same day, it falls back to <mm-dd-yyyy>_2.md, _3.md, ... so no
existing archive is ever overwritten.

Exits 0 quietly on any problem so it never blocks the session.
"""
import sys, os, json
from datetime import datetime
from pathlib import Path

def text_from_content(content):
    if isinstance(content, str):
        return content.strip()
    parts = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
    return "\n".join(p for p in parts if p).strip()

def session_date(records):
    """mm-dd-yyyy from the earliest timestamp in the transcript; today if none."""
    for d in records:
        ts = d.get("timestamp")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                return dt.astimezone().strftime("%m-%d-%Y")
            except ValueError:
                pass
    return datetime.now().strftime("%m-%d-%Y")

def resolve_path(dest_dir, date_str, session_id):
    """Pick mm-dd-yyyy.md, but avoid clobbering a different session's file."""
    marker = f"<!-- session:{session_id} -->"
    n = 1
    while True:
        name = f"{date_str}.md" if n == 1 else f"{date_str}_{n}.md"
        path = dest_dir / name
        if not path.exists():
            return path                      # free slot
        try:
            if marker in path.read_text(encoding="utf-8")[:200]:
                return path                  # our own file from an earlier turn
        except OSError:
            return path
        n += 1                               # taken by another session, try next

def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except (json.JSONDecodeError, ValueError):
        return 0

    transcript = payload.get("transcript_path")
    cwd = payload.get("cwd") or os.getcwd()
    session_id = payload.get("session_id") or "session"
    if not transcript or not os.path.isfile(transcript):
        return 0

    records = []
    with open(transcript, encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                records.append(json.loads(raw))
            except json.JSONDecodeError:
                continue

    project = os.path.basename(os.path.normpath(cwd)) or "unknown-project"
    dest_dir = Path.home() / "saved_chats" / project
    dest_dir.mkdir(parents=True, exist_ok=True)
    date_str = session_date(records)
    out = resolve_path(dest_dir, date_str, session_id)

    lines = [
        f"<!-- session:{session_id} -->",
        f"# {project} — conversation ({date_str})",
        f"\n*Session `{session_id}` · auto-exported*\n",
        "\n---\n",
    ]
    for d in records:
        t = d.get("type")
        msg = d.get("message")
        if not isinstance(msg, dict):
            continue
        if t == "user":
            txt = text_from_content(msg.get("content", ""))
            if txt:
                lines.append(f"## 🧑 User\n\n{txt}\n")
        elif t == "assistant":
            content = msg.get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text" and block.get("text", "").strip():
                        lines.append(f"## 🤖 Claude\n\n{block['text'].strip()}\n")

    try:
        out.write_text("\n".join(lines), encoding="utf-8")
    except OSError:
        pass
    return 0

if __name__ == "__main__":
    sys.exit(main())
