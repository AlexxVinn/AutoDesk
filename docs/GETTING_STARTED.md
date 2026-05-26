# Workspace Assistant — Getting Started Guide

Welcome. This guide assumes you have never used the app before. By the end, you will know what it does, how to install it, and how to control your desktop with voice or typed commands.

---

## What is this?

**Workspace Assistant** is a small desktop helper for developers. You tell it what you want — by voice or by typing — and it:

- Opens apps (Cursor, Chrome, Telegram, Viber, Terminal, …)
- Arranges windows (split screen, custom layouts)
- Opens projects and websites
- Controls volume and audio output (headsets vs earbuds)
- Runs **presets** (multi-step workflows like “Coding Mode”)

It is **not** a chatbot that thinks for itself. It listens, converts your words into a short list of actions, and runs those actions on Windows in a predictable way.

```
You speak or type  →  App understands  →  Actions run on your PC
```

---

## What you need

| Requirement | Notes |
|-------------|--------|
| **Windows 10/11** | Full features (window snap, audio, app launch) |
| **Python 3.11+** | Powers the backend |
| **Microphone** | Optional, for voice |
| **Node.js 20+** | Only if you use the desktop window (Tauri UI) |
| **Rust** | Only if you build the desktop app yourself |

Everything runs **on your computer**. Voice recognition uses a local model (no cloud required for speech). Optional AI (Ollama) can make commands more natural — see [LOCAL_LLM.md](LOCAL_LLM.md).

---

## First-time setup (about 10 minutes)

### Step 1 — Get the project

Clone or download the repository, then open a terminal in the project folder.

### Step 2 — Install the backend

Open **PowerShell** in the project folder and run:

```powershell
.\scripts\install-backend.ps1
```

Or manually:

```powershell
cd backend
python -m pip install -e ".[windows]"
```

This installs the engine that listens, understands commands, and controls your apps.

### Step 3 — Start the backend

```powershell
.\scripts\start-backend.ps1
```

Leave this window open. You should see it listening on:

**http://127.0.0.1:9477**

If that works, the brain of the app is running.

### Step 4 — Open the desktop window (optional but recommended)

Open a **second** PowerShell window:

```powershell
cd app
npm install
npm run tauri:dev
```

A small window titled **Workspace Assistant** appears. It connects to the backend automatically.

> **Tip:** You can also use the app without the window by sending commands to the API, but the window is the easiest way to start.

---

## The desktop window — tour

When the app opens, you see four areas:

```
┌─────────────────────────────────────────┐
│  ● Workspace Assistant     Connected    │  ← Status (green = OK)
├─────────────────────────────────────────┤
│  Command: [ type here........... ] Run  │  ← Type a command + Enter
├─────────────────────────────────────────┤
│  Presets                                │
│  [ Coding Mode ] [ Focus Mode ] ...     │  ← One-click workflows
├─────────────────────────────────────────┤
│  Last action                            │
│  { success, steps... }                  │  ← What just happened
├─────────────────────────────────────────┤
│  [ Voice: off ]  [ Reconnect ]          │  ← Footer controls
└─────────────────────────────────────────┘
```

| Part | What it does |
|------|----------------|
| **Green dot** | Backend is connected |
| **Command box** | Type a command and press **Enter** or **Run** |
| **Presets** | Buttons for saved workflows (click = run immediately) |
| **Last action** | JSON feedback — `success: true` means it worked |
| **Voice: off/on** | Turns microphone listening on or off |
| **Reconnect** | Use if the backend was restarted |

---

## Your first commands (try these in order)

Type each line in the **Command** box and press **Enter**.

1. **`focus cursor`** — Brings Cursor to the front (if it is open)
2. **`open cursor`** — Opens Cursor and maximizes it
3. **`open chrome`** — Opens Chrome (your configured profile)
4. **`split screen`** — Cursor on the left, Chrome on the right
5. **`open coding workspace`** — Runs the full “Coding Mode” preset

If **Last action** shows `"success": true`, you are good.

---

## Voice control

1. Make sure the **backend** is running.
2. In the app, click **Voice: off** → it becomes **Voice: on**.
3. Speak clearly after a short pause. Example: *“Focus cursor.”*
4. The app transcribes your speech locally, runs the command, and shows the result in **Last action**.

### Optional wake word

By default, the app listens to everything you say while voice is on. To require a wake phrase first, edit `config/settings.json`:

```json
"wake_word_enabled": true,
"wake_word": "hey desk"
```

Then say: *“Hey desk, open coding workspace.”*

### Voice tips

- Speak in a normal room (less background noise = better)
- First transcription may be slow while the speech model loads
- For faster response, use a smaller Whisper model (`tiny.en` in settings); for accuracy, use `small.en`

---

## Presets — one button, many steps

A **preset** is a saved routine. Example **Coding Mode** might:

1. Open Cursor  
2. Open Chrome  
3. Open ChatGPT  
4. Open your project folder  
5. Split windows  
6. Focus Cursor  

You trigger it by:

- Clicking the preset button in the UI, or  
- Saying / typing **`open coding workspace`** or **`coding mode`**

Built-in presets (see `config/presets.json`):

| Name | What it does (summary) |
|------|-------------------------|
| **Coding Mode** | Dev layout: Cursor + Chrome + ChatGPT + project |
| **Focus Mode** | Closes distractions, music, then coding layout |
| **Split Screen** | Cursor left, Chrome right |
| **Alexandr Chrome Stack** | Your Chrome profile + YouTube + ChatGPT + Cursor fullscreen |

You can add your own presets by editing `config/presets.json` (JSON format).

---

## Window layouts — arrange apps your way

Beyond simple left/right split, you can place apps in zones:

- **top_left**, **top_right**, **bottom_left**, **bottom_right**
- **left**, **right**, **top**, **bottom**

### Say a layout phrase

Examples (type or speak):

- *“Cursor right chrome top left telegram bottom left”*
- *“Put cursor on the right and chrome top left and terminal bottom left”*
- *“Quad layout”* (four apps in quadrants)

### Or use a layout name

- *“Layout cursor_right_chrome_tl_telegram_bl”*

Layouts live in `config/layouts.json`. You can add custom ones.

---

## Apps supported out of the box

| App | Example commands |
|-----|------------------|
| **Cursor** | `open cursor`, `focus cursor` (also understands “courser”) |
| **Chrome** | `open chrome`, `open chrome in my Alexandr Vinnitchii account` |
| **ChatGPT** | `open chatgpt` |
| **YouTube** | `open youtube` |
| **Telegram** | `open telegram` |
| **Viber** | `open viber` |
| **Terminal** | `open terminal` |
| **Google** | `search google for rust async tutorial` |

Paths to executables are in `config/apps.json`. If an app does not open on your PC, update the path there.

---

## Audio — volume and headphones

| Command | Effect |
|---------|--------|
| `set volume to 40` | Volume at 40% |
| `volume up` / `volume down` | Change by ~10% |
| `mute` / `unmute` | Mute toggle |
| `switch audio to earbuds` | Default output → earbuds |
| `use headsets` | Default output → headsets |

Your headphone names must match Windows device names. See [AUDIO_SETUP.md](AUDIO_SETUP.md).

Requires: `pip install pycaw comtypes` (included in Windows install).

---

## ChatGPT + Cursor workflow

1. *“Open chatgpt”* (in your Chrome profile)  
2. *“Make a prompt to chatgpt: \"Explain this error in simple terms\""*  
3. Wait for ChatGPT to finish writing  
4. *“Copy the results and paste to cursor”*

Step 4 uses keyboard/clipboard automation. It works best when the ChatGPT tab is visible.

---

## Talk naturally (optional AI)

By default, commands use **fixed patterns** (fast, free). For more fluid speech, enable a **local AI** (Ollama) that only translates your words to actions — it does not control the PC directly.

See **[LOCAL_LLM.md](LOCAL_LLM.md)** for setup. After that, set in `config/settings.json`:

```json
"mode": "natural",
"llm_enabled": true
```

Then you can say things like: *“I’m starting work — set up Chrome and Cursor like usual and lower the volume.”*

---

## Configuration files (where to customize)

All in the **`config/`** folder:

| File | Purpose |
|------|---------|
| `settings.json` | Voice, AI parser, server port |
| `apps.json` | App paths, Chrome profiles, Telegram/Viber |
| `projects.json` | Project folders (“open my physics project”) |
| `presets.json` | Multi-step workflows |
| `layouts.json` | Window grid layouts |
| `audio.json` | Headset / earbud name matching |

After editing any file, **restart the backend**.

### Chrome profile (important)

If you use a named Chrome profile, set the correct folder in `config/apps.json`. See [CHROME_PROFILE_SETUP.md](CHROME_PROFILE_SETUP.md).

---

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| **Disconnected** in UI | Start backend: `.\scripts\start-backend.ps1` → click **Reconnect** |
| Command not understood | Check spelling; try a preset button; enable local LLM (`natural` mode) |
| App does not open | Fix path in `config/apps.json` |
| Window snap wrong | Bring apps to foreground first; say `open cursor` then layout command |
| Voice does nothing | Click **Voice: on**; check microphone permissions in Windows |
| Volume/audio fails | Install Windows extras: `pip install pycaw comtypes` |
| Slow first voice command | Normal — Whisper model loading; later commands are faster |

---

## Daily workflow example

**Morning:**

1. Start backend + desktop app  
2. Click **Coding Mode** or say *“open coding workspace”*  
3. Say *“switch audio to headsets”*

**During work:**

- *“Focus cursor”* when you switch to the editor  
- *“Open telegram”* / *“Layout quad work”* when messaging  
- *“Volume down”* if music is loud  

**End of day:**

- *“Focus mode”* or close apps manually  

---

## What this app will NOT do

- Browse the web or click buttons like a human (no vision AI)  
- Run forever without you (not a fully autonomous agent)  
- Guarantee 100% voice accuracy (quiet room + clear speech helps)  
- Replace Cursor’s built-in AI  

It **will** save you time on repetitive “open this, snap that, switch audio” tasks.

---

## Learn more

| Doc | Topic |
|-----|--------|
| [README.md](../README.md) | Technical overview |
| [LOCAL_LLM.md](LOCAL_LLM.md) | Natural language with Ollama |
| [AUDIO_SETUP.md](AUDIO_SETUP.md) | Headphones / speakers |
| [CHROME_PROFILE_SETUP.md](CHROME_PROFILE_SETUP.md) | Chrome profiles |

---

## Quick reference card

```
PRESETS          open coding workspace | coding mode | focus mode | split screen
APPS             open cursor | open chrome | open telegram | open viber
FOCUS            focus cursor | focus chrome
LAYOUT           cursor right chrome top left telegram bottom left
AUDIO            volume up | set volume to 50 | mute | switch audio to earbuds
CHATGPT          open chatgpt | make a prompt to chatgpt: "..."
                 copy the results and paste to cursor
```

Happy building.
