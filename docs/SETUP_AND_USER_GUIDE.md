# Workspace Assistant — Setup & User Guide (Windows)

Complete guide for installing, configuring, and using Workspace Assistant on your PC.

**Example project path:** `C:\Users\AlexV\Desktop\AutoDesk`

---

## Table of contents

1. [What this program does](#1-what-this-program-does)
2. [Requirements](#2-requirements)
3. [Installation](#3-installation)
4. [First run](#4-first-run)
5. [Using the desktop app](#5-using-the-desktop-app)
6. [Commands you can use](#6-commands-you-can-use)
7. [Voice control](#7-voice-control)
8. [Configuration](#8-configuration)
9. [Optional: natural language (Ollama)](#9-optional-natural-language-ollama)
10. [Optional: build a desktop installer](#10-optional-build-a-desktop-installer)
11. [Troubleshooting](#11-troubleshooting)
12. [Quick reference](#12-quick-reference)

---

## 1. What this program does

Workspace Assistant is a **desktop productivity tool** for developers. You **type** or **speak** commands; it runs **fixed actions** on Windows:

- Open and focus apps (Cursor, Chrome, Telegram, Viber, Terminal)
- Snap and arrange windows (split screen, custom grids)
- Open projects and URLs (ChatGPT, YouTube, Google)
- Control volume and switch audio output (headsets ↔ earbuds)
- Run **presets** — saved multi-step workflows (e.g. “Coding Mode”)

It is **not** a fully autonomous AI agent. A small parser (rules + optional local LLM) turns your words into steps; a **deterministic executor** runs them. That keeps behavior fast and predictable.

---

## 2. Requirements

| Item | Required? | Notes |
|------|-----------|--------|
| Windows 10 or 11 | Yes | Full window/audio automation |
| Python 3.11 or newer | Yes | [python.org](https://www.python.org/downloads/) — check **“Add Python to PATH”** during install |
| Microphone | For voice | Any USB or built-in mic |
| Node.js 20+ | For UI window | [nodejs.org](https://nodejs.org/) |
| Rust | For UI window | [rustup.rs](https://rustup.rs/) — only if you run `npm run tauri:dev` |
| Ollama | Optional | For natural-language commands — see [LOCAL_LLM.md](LOCAL_LLM.md) |

**Internet:** Needed once to install packages and download the speech model. Day-to-day voice works offline after that.

---

## 3. Installation

### Step 1 — Open PowerShell in the project folder

```powershell
cd C:\Users\AlexV\Desktop\AutoDesk
```

### Step 2 — Install Python dependencies

**Easy way:**

```powershell
.\scripts\install-backend.ps1
```

**Manual way:**

```powershell
cd backend
python -m pip install --upgrade pip
python -m pip install -e ".[windows]"
cd ..
```

This installs FastAPI, speech recognition (Faster-Whisper), Windows automation (pywin32), volume control (pycaw), and related tools.

> **If `python` is not found:** Try `py -3.11` instead of `python`, or reinstall Python with “Add to PATH” enabled.

### Step 3 — Configure your machine (important)

Before first use, edit these files in the `config` folder (see [Section 8](#8-configuration)):

1. **`apps.json`** — paths to Cursor, Chrome, Telegram, Viber on **your** PC  
2. **`projects.json`** — folders for “open my X project”  
3. **`apps.json` → Chrome profile** — correct `Profile 2` (or yours) for your Google account  

See [CHROME_PROFILE_SETUP.md](CHROME_PROFILE_SETUP.md) for Chrome profile steps.

### Step 4 — Install UI dependencies (optional)

Only if you want the graphical window:

```powershell
cd app
npm install
cd ..
```

---

## 4. First run

You need **two parts** running: the **backend** (engine) and optionally the **desktop UI**.

### Start the backend (required)

```powershell
cd C:\Users\AlexV\Desktop\AutoDesk
.\scripts\start-backend.ps1
```

Or manually:

```powershell
$env:WORKSPACE_ASSISTANT_CONFIG = "C:\Users\AlexV\Desktop\AutoDesk\config"
cd C:\Users\AlexV\Desktop\AutoDesk\backend
$env:PYTHONPATH = "src"
python -m workspace_assistant.main
```

**Leave this window open.** You should see logs and:

```text
Uvicorn running on http://127.0.0.1:9477
```

**Test in browser:** open http://127.0.0.1:9477/health — you should see `{"status":"ok",...}`.

### Start the desktop UI (recommended)

Open a **second** PowerShell window:

```powershell
cd C:\Users\AlexV\Desktop\AutoDesk\app
npm run tauri:dev
```

The **Workspace Assistant** window opens and connects to the backend.

> **Without the UI:** You can still send commands via HTTP (advanced). The window is the easiest way for daily use.

---

## 5. Using the desktop app

### Window layout

```
┌──────────────────────────────────────────┐
│ ● Workspace Assistant      Connected   │  ← status
├──────────────────────────────────────────┤
│ Command: [  type here...          ] Run │
├──────────────────────────────────────────┤
│ Presets:  [Coding Mode] [Focus Mode] …   │
├──────────────────────────────────────────┤
│ Last action:  { "success": true, ... }   │
├──────────────────────────────────────────┤
│ [ Voice: off ]  [ Reconnect ]            │
└──────────────────────────────────────────┘
```

| Control | Action |
|---------|--------|
| **Command + Enter** | Run a typed command |
| **Run** | Same as Enter |
| **Preset button** | Run a saved workflow immediately |
| **Last action** | Shows success/failure and steps run |
| **Voice: off/on** | Enable microphone listening |
| **Reconnect** | Re-link to backend after restart |

### Status dot

- **Green + “Connected”** — ready  
- **Red + “Disconnected”** — start the backend, then click **Reconnect**

### Your first 5 minutes

1. Start backend + UI (Section 4).  
2. Type `focus cursor` → Enter.  
3. Type `open chrome` → Enter.  
4. Click **Coding Mode** preset (or type `open coding workspace`).  
5. Click **Voice: on** and say *“Split screen.”*

---

## 6. Commands you can use

### Apps

| Command | What happens |
|---------|----------------|
| `open cursor` | Opens Cursor, maximized |
| `focus cursor` | Brings Cursor to front |
| `open chrome` | Opens Chrome (default profile from config) |
| `open chrome in my Alexandr Vinnitchii account` | Chrome with your named profile |
| `open chatgpt` | ChatGPT in Chrome |
| `open youtube` | YouTube in Chrome |
| `open telegram` | Telegram |
| `open viber` | Viber |
| `open terminal` | Windows Terminal |

Voice may hear “courser” — that still maps to Cursor.

### Window layout

| Command | What happens |
|---------|----------------|
| `split screen` | Cursor left, Chrome right |
| `cursor right chrome top left telegram bottom left` | 3-pane custom layout |
| `put cursor on the right and chrome top left and terminal bottom left` | Same idea, free wording |
| `quad layout` | Four apps in quadrants |
| `layout cursor_right_chrome_tl_telegram_bl` | Run a named layout from config |

### Presets (workflows)

| Command / button | What happens |
|------------------|----------------|
| `open coding workspace` | Full dev setup (Cursor, Chrome, ChatGPT, project, split) |
| `coding mode` | Same as above |
| `focus mode` | Reduce distractions, then coding layout |
| `open alexandr stack` | Chrome profile + YouTube + ChatGPT + Cursor fullscreen |

### Audio (Windows)

| Command | What happens |
|---------|----------------|
| `set volume to 40` | Volume 40% |
| `volume up` / `volume down` | ±10% |
| `mute` / `unmute` | Mute toggle |
| `switch audio to earbuds` | Default output → earbuds |
| `use headsets` | Default output → headsets |

Configure device names in `config/audio.json` — see [AUDIO_SETUP.md](AUDIO_SETUP.md).

### ChatGPT + Cursor

| Step | Command |
|------|---------|
| 1 | `open chatgpt` |
| 2 | `make a prompt to chatgpt: "Your question here"` |
| 3 | Wait until ChatGPT finishes |
| 4 | `copy the results and paste to cursor` |

### Projects

| Command | What happens |
|---------|----------------|
| `open my physics project` | Opens folder/project from `projects.json` |
| `open phyzic project` | Same, by project id |

---

## 7. Voice control

### Enable voice

1. Backend must be running.  
2. In the app, click **Voice: off** → **Voice: on**.  
3. Speak after a brief pause (e.g. *“Focus cursor.”*).  
4. Check **Last action** for results.

### Settings (`config/settings.json`)

| Setting | Default | Meaning |
|---------|---------|---------|
| `voice.enabled` | `true` | Voice feature on |
| `voice.always_listen` | `true` | Listen while voice is toggled on |
| `voice.wake_word_enabled` | `false` | If `true`, require wake phrase first |
| `voice.wake_word` | `"hey desk"` | Wake phrase text |
| `voice.whisper_model` | `base.en` | `tiny.en` = faster, `small.en` = more accurate |

**Wake word example:** Enable wake word, then say *“Hey desk, open coding workspace.”*

### Tips

- Quiet room, clear speech  
- First command may be slow (model loading)  
- Restart backend after changing `settings.json`

---

## 8. Configuration

All files are in:

```text
C:\Users\AlexV\Desktop\AutoDesk\config\
```

Restart the backend after any edit.

### `settings.json` — global behavior

```json
{
  "host": "127.0.0.1",
  "port": 9477,
  "voice": { ... },
  "parser": {
    "mode": "hybrid",
    "llm_enabled": false
  }
}
```

| `parser.mode` | Behavior |
|---------------|----------|
| `hybrid` | Exact phrases first, then AI (if enabled) |
| `natural` | AI first — best for casual speech |
| `rules` | No AI, phrases only |
| `llm` | AI only (if enabled) |

### `apps.json` — applications

Set correct paths for your PC:

```json
"cursor": {
  "windows": {
    "exe": "%LOCALAPPDATA%\\Programs\\cursor\\Cursor.exe"
  }
}
```

Telegram example:

```json
"telegram": {
  "windows": {
    "exe": "%APPDATA%\\Telegram Desktop\\Telegram.exe"
  }
}
```

### `projects.json` — project folders

```json
"phyzic": {
  "label": "Phyzic",
  "path": "C:\\Users\\AlexV\\Projects\\phyzic",
  "cursor_args": ["C:\\Users\\AlexV\\Projects\\phyzic"]
}
```

### `presets.json` — workflows

Add presets with `steps` — each step is an `action` + `params`. Copy an existing preset and modify.

### `layouts.json` — window grids

Each layout has `slots`: `app_id` + `zone` (`top_left`, `right`, etc.).

### `audio.json` — headphones

Match strings to your Windows playback device names (Settings → Sound).

---

## 9. Optional: natural language (Ollama)

If you don’t want to memorize exact commands:

1. Install [Ollama](https://ollama.com/download).  
2. Run: `ollama pull qwen2.5:3b`  
3. Merge into `settings.json` (see `config/settings.local-llm.example.json`):

```json
"parser": {
  "mode": "natural",
  "llm_enabled": true,
  "provider": "ollama",
  "base_url": "http://127.0.0.1:11434/v1",
  "llm_model": "qwen2.5:3b"
}
```

4. Restart backend.

Full details: [LOCAL_LLM.md](LOCAL_LLM.md).

---

## 10. Optional: build a desktop installer

Development UI:

```powershell
cd C:\Users\AlexV\Desktop\AutoDesk\app
npm run tauri:dev
```

Production build:

```powershell
npm run tauri:build
```

Installer output is under `app\src-tauri\target\release\bundle\`.

You still need the **Python backend running** alongside the installed app.

---

## 11. Troubleshooting

| Problem | Solution |
|---------|----------|
| `python` not recognized | Use `py -3.11` or add Python to PATH |
| Disconnected in UI | Run `.\scripts\start-backend.ps1`, click **Reconnect** |
| Port 9477 in use | Change `port` in `settings.json` or close the other process |
| Command not understood | Try preset buttons; enable Ollama (`natural` mode) |
| App doesn’t open | Fix `exe` path in `apps.json` |
| Window snap wrong | Open apps first (`open cursor`, `open chrome`), then layout command |
| Voice silent | Windows Settings → Privacy → Microphone → allow desktop apps |
| `pycaw` / audio errors | Re-run: `pip install pycaw comtypes` in backend venv |
| Whisper very slow | Use `"whisper_model": "tiny.en"` in settings |
| ChatGPT copy fails | Keep ChatGPT tab visible; install `pywinauto` |

### Logs

Watch the **backend PowerShell window** for errors when a command fails.

### Test API manually

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:9477/command `
  -ContentType "application/json" `
  -Body '{"text":"focus cursor"}'
```

---

## 12. Quick reference

### Daily startup

```powershell
# Window 1
cd C:\Users\AlexV\Desktop\AutoDesk
.\scripts\start-backend.ps1

# Window 2
cd C:\Users\AlexV\Desktop\AutoDesk\app
npm run tauri:dev
```

### Command cheat sheet

```text
WORKSPACE     open coding workspace | coding mode | focus mode | split screen
APPS          open cursor | focus cursor | open chrome | open telegram | open viber
LAYOUT        cursor right chrome top left telegram bottom left | quad layout
AUDIO         volume up | set volume to 50 | mute | switch audio to earbuds
CHATGPT       open chatgpt | make a prompt to chatgpt: "..." | copy the results and paste to cursor
PROJECTS      open my physics project
```

### Config files

| File | Purpose |
|------|---------|
| `settings.json` | Voice, AI, port |
| `apps.json` | App paths, Chrome profiles |
| `projects.json` | Project paths |
| `presets.json` | Multi-step workflows |
| `layouts.json` | Window arrangements |
| `audio.json` | Headset/earbud matching |

---

## Related docs

- [CHROME_PROFILE_SETUP.md](CHROME_PROFILE_SETUP.md)  
- [AUDIO_SETUP.md](AUDIO_SETUP.md)  
- [LOCAL_LLM.md](LOCAL_LLM.md)  
- [README.md](../README.md) — technical overview  

---

*Workspace Assistant Phase 1 — Windows-first desktop productivity.*
