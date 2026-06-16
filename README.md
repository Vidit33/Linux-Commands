<<<<<<< HEAD
# Linux Commands Reference

A personal cheatsheet of Linux commands — from everyday terminal basics to Git workflow, SSH setup, Raspberry Pi configuration, and ESP32 hardware integration.

## Contents

| File | Description |
|------|-------------|
| [`commands.md`](commands.md) | Core Linux commands: navigation, file ops, permissions, processes, Git, SSH |
| [`hardware.md`](hardware.md) | Hardware-specific: Raspberry Pi static IP, ESP32-P4 audio capture |

## Topics Covered

- Terminal navigation and file management
- Text output, grep, and piping
- Process and disk management
- SSH key generation and GitHub setup
- Git workflow and branch management
- Git SSH troubleshooting
- Raspberry Pi password reset and health checks
- ESP32-P4 serial audio recording

## Claude Recovery

- [export_chat.py](export_chat.py) = For Manually recovering a chat when you are inside the folder.
- [export_chat_hook.py](export_chat_hook.py) = for automatically recovering the saved chats.

```bash
-mkdir -p ~/.claude/hooks
-cp export_chat_hook.py ~/.claude/hooks/export_chat_hook.py
-Edit ~/.claude/settings.json and merge this hooks block in (don't wipe existing keys). If the file doesn't exist yet, create it with just this:
  {
    "hooks": {
      "Stop": [
        {
          "hooks": [
            {
              "type": "command",
              "command": "python3 \"$HOME/.claude/hooks/export_chat_hook.py\" 2>/dev/null || true",
              "async": true,
              "suppressOutput": true,
              "statusMessage": "Archiving chat…"
            } 
          ] 
        } 
      ] 
    } 
  } 
 If settings.json already has content, just add the "hooks" key alongside your existing ones (mind the commas).
-python3 -c "import json; json.load(open('$HOME/.claude/settings.json')); print('valid')"
-Hooks load at session startup, so new windows pick it up automatically.
 An already-open session needs a /hooks reload or restart.
 After your first turn, confirm it's working: ls ~/saved_chats/<project-folder-name>/ — you should see <mm-dd-yyyy>.md.

```

## License

[GPL-3.0](LICENSE)
=======
## Linux-Commands
`These are the different commands For a linux system which even a beginner can use` 

| `File Name` | `commands explanation` |
| ---- | ---- |
| `1.` | `Basic linux commands` |
| `2.` | `Everything Related to SSH`|
| `3.` | `how to get back ur Rpi, if u forget the password` |


## Note:-
`These will be updated as this goes ahead in period of time`
>>>>>>> refs/remotes/origin/main
