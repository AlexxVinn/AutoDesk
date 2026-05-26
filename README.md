# Workspace Assistant (AutoDesk)

Desktop productivity assistant for Windows — voice and text commands, presets, window layouts, and audio control.

## Documentation

| Guide | For |
|-------|-----|
| **[docs/SETUP_AND_USER_GUIDE.md](docs/SETUP_AND_USER_GUIDE.md)** | **Full setup + daily use (start here)** |
| [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) | Short first-time tour |
| [docs/CHROME_PROFILE_SETUP.md](docs/CHROME_PROFILE_SETUP.md) | Chrome profile configuration |
| [docs/AUDIO_SETUP.md](docs/AUDIO_SETUP.md) | Headsets / earbuds |
| [docs/LOCAL_LLM.md](docs/LOCAL_LLM.md) | Natural language via Ollama |

## Quick start (Windows)

```powershell
cd C:\Users\AlexV\Desktop\AutoDesk
.\scripts\install-backend.ps1
.\scripts\start-backend.ps1
```

In a second terminal (optional UI):

```powershell
cd app
npm install
npm run tauri:dev
```

Backend: http://127.0.0.1:9477

## What it does

- Opens/focuses apps (Cursor, Chrome, Telegram, Viber, Terminal)
- Window layouts and split screen
- Volume and audio output switching
- Presets (Coding Mode, Focus Mode, custom workflows)
- Optional local LLM for natural speech (Ollama)

Execution is **deterministic** — not a fully autonomous agent.

## Project structure

```
AutoDesk/
├── backend/          # Python FastAPI service
├── app/              # Tauri desktop UI
├── config/           # apps, presets, layouts, settings
├── scripts/          # install & start scripts (Windows)
└── docs/             # user guides
```

## License

MIT
