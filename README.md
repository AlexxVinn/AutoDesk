# Workspace Assistant (Phase 1)

A **fast, deterministic** desktop productivity assistant for developers. Voice and text commands map to structured actions; execution uses native OS automation — not an autonomous agent.

## Architecture

```
┌─────────────────┐     WebSocket/HTTP      ┌──────────────────────────────────┐
│  Tauri Desktop  │ ◄──────────────────────►│  Python Backend (FastAPI)        │
│  (Vite UI)      │                         │  ┌────────┐  ┌────────┐  ┌──────┐ │
└─────────────────┘                         │  │ Voice  │→ │ Parser │→ │ Exec │ │
                                            │  └────────┘  └────────┘  └──┬───┘ │
                                            │       │            │          │    │
                                            │       ▼            ▼          ▼    │
                                            │  Faster-Whisper  Rules/LLM  Win32 │
                                            └──────────────────────────────────┘
```

| Module | Role |
|--------|------|
| `voice/` | Always-on mic, VAD chunks, Faster-Whisper transcription, optional wake word |
| `parser/` | Rule-based patterns first; optional OpenAI JSON plan (no execution) |
| `executor/` | Deterministic step runner |
| `automation/` | App launch, URLs, folders, hotkeys |
| `windows/` | Win32 snap/focus/move (stub on Linux for dev) |
| `presets/` | JSON workflow definitions |

## Quick start (Windows)

### 1. Backend

```powershell
cd backend
python -m pip install -e ".[windows]"
$env:WORKSPACE_ASSISTANT_CONFIG = "..\config"
python -m workspace_assistant.main
```

Or: `.\scripts\install-backend.ps1` then `.\scripts\start-backend.ps1`

Backend listens on `http://127.0.0.1:9477`.

### 2. Desktop UI (Tauri)

Requires [Rust](https://rustup.rs/) and Node 20+.

```powershell
cd app
npm install
npm run tauri:dev
```

### 3. Configure

Edit JSON in `config/`:

- `settings.json` — voice, parser, server port
- `apps.json` — executables, title patterns, Chrome profiles
- `projects.json` — project paths for Cursor/folder open
- `presets.json` — multi-step workflows (Coding Mode, Focus Mode, etc.)

Set `parser.llm_enabled: true` and `OPENAI_API_KEY` for natural-language fallback. Execution stays deterministic.

## Example commands

| Say / type | Behavior |
|------------|----------|
| Open coding workspace | Runs `open_coding_workspace` preset |
| Launch Cursor and Chrome | Starts both apps |
| Focus Cursor | Focuses Cursor window by title |
| Split screen | Snap Cursor left, Chrome right |
| Open my physics project | Opens `physics` project path in Cursor |
| Search Google for … | Opens Google search URL |

With LLM enabled, e.g. *"Open Cursor and ChatGPT side by side and load my Phyzic project"* becomes a JSON action plan, then the executor runs it.

## Voice

- **Always listen**: enabled in `settings.json` (`voice.always_listen`)
- **Wake word**: set `wake_word_enabled: true` and `wake_word: "hey desk"`
- **Model**: `voice.whisper_model` (default `base.en`; use `small.en` for accuracy, `tiny.en` for speed)

Toggle voice from the desktop footer or `POST /voice/toggle`.

## API

- `GET /health`
- `GET /presets`
- `POST /command` `{ "text": "focus cursor" }`
- `POST /preset/{id}`
- `WS /ws` — live results and voice transcripts

## Development (Linux/macOS)

Window control uses a **stub** manager (logs actions). Install backend without pywin32:

```bash
cd backend && pip install -e . && PYTHONPATH=src pytest
```

## Design constraints (Phase 1)

- No autonomous agent loop
- No screenshot / vision clicking
- LLM only for parsing → structured steps
- Prefer Win32 APIs, title matching, process launch, keyboard shortcuts

## License

MIT (add your license as needed)
