#!/usr/bin/env python3
"""
Export a Claude Code conversation transcript (.jsonl) to readable Markdown.

This is the MANUAL exporter. Day-to-day archiving already happens automatically
via the Stop hook (~/.claude/hooks/export_chat_hook.py), which writes to
~/saved_chats/<project>/. Use this script when you want to export on demand into
the current folder, or convert a specific old session.

Usage:
    python3 export_chat.py                      # newest session for THIS project
    python3 export_chat.py path/to/session.jsonl
    python3 export_chat.py --thinking           # also include the model's thinking
    python3 export_chat.py --tools              # also note tool calls

Output: <mm-dd-yyyy>.md in the current directory (matching the hook's naming;
falls back to _2, _3, ... if that name is already taken by another session).
Transcripts live in ~/.claude/projects/<encoded-project-path>/<session-id>.jsonl
"""
import sys, os, json, glob
from datetime import datetime
from pathlib import Path

def project_dir():
    enc = str(Path.cwd()).replace("/", "-")
    return Path.home() / ".claude" / "projects" / enc

def newest_transcript():
    files = sorted(glob.glob(str(project_dir() / "*.jsonl")), key=os.path.getmtime)
    if not files:
        sys.exit(f"No transcripts found in {project_dir()}")
    return files[-1]

def text_from_content(content):
    if isinstance(content, str):
        return content.strip()
    parts = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
    return "\n".join(p for p in parts if p).strip()

def session_stamp(records):
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

def resolve_path(dest_dir, stamp, session_id):
    marker = f"<!-- session:{session_id} -->"
    n = 1
    while True:
        name = f"{stamp}.md" if n == 1 else f"{stamp}_{n}.md"
        path = dest_dir / name
        if not path.exists():
            return path
        try:
            if marker in path.read_text(encoding="utf-8")[:200]:
                return path
        except OSError:
            return path
        n += 1

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    include_thinking = "--thinking" in flags
    include_tools = "--tools" in flags

    src = args[0] if args else newest_transcript()

    records, session_id = [], "session"
    with open(src, encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                d = json.loads(raw)
            except json.JSONDecodeError:
                continue
            records.append(d)
            if d.get("sessionId") and session_id == "session":
                session_id = d["sessionId"]

    stamp = session_stamp(records)
    out = resolve_path(Path.cwd(), stamp, session_id)

    project = Path.cwd().name
    lines = [
        f"<!-- session:{session_id} -->",
        f"# {project} — conversation ({stamp})",
        f"\n*Source: `{src}`*\n",
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
                    if not isinstance(block, dict):
                        continue
                    bt = block.get("type")
                    if bt == "text" and block.get("text", "").strip():
                        lines.append(f"## 🤖 Claude\n\n{block['text'].strip()}\n")
                    elif bt == "thinking" and include_thinking and block.get("thinking", "").strip():
                        lines.append(f"> 💭 *thinking:* {block['thinking'].strip()}\n")
                    elif bt == "tool_use" and include_tools:
                        lines.append(f"> 🔧 *tool call:* `{block.get('name','?')}`\n")

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out} ({os.path.getsize(out)} bytes)")

if __name__ == "__main__":
    main()
