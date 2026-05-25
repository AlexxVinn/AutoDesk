# Local LLM for natural commands

Use a **small local model** only to translate speech → JSON action steps. Execution stays deterministic (no agent loop).

## Is this a good idea?

**Yes**, for your goal (“sound natural, not memorize exact phrases”):

| Approach | Pros | Cons |
|----------|------|------|
| Rules only | Fast, free, reliable | Robotic phrasing |
| Cloud LLM (GPT) | Very fluent | Cost, privacy, latency |
| **Local small LLM** | Private, no per-command fee, fluid | Needs RAM/GPU; occasional wrong JSON |

**Recommended:** `mode: "natural"` or `hybrid` + local LLM fallback.

```
Voice → Whisper → Parser (rules / layout / local LLM) → JSON plan → Executor
```

The LLM never clicks or launches directly—it only outputs `{"steps":[...]}`.

## Quick setup (Ollama — Windows)

1. Install [Ollama](https://ollama.com/download)
2. Pull a small instruct model:
   ```powershell
   ollama pull qwen2.5:3b
   ```
   Other good options: `llama3.2:3b`, `phi3:mini`, `gemma2:2b`
3. Edit `config/settings.json`:
   ```json
   "parser": {
     "mode": "natural",
     "llm_enabled": true,
     "provider": "ollama",
     "base_url": "http://127.0.0.1:11434/v1",
     "llm_model": "qwen2.5:3b",
     "use_openai_sdk": true
   }
   ```
4. Restart the backend.

Ollama exposes an OpenAI-compatible API at `http://127.0.0.1:11434/v1`.

## Parsing modes

| mode | Behavior |
|------|----------|
| `hybrid` | Exact rules first → layout phrases → LLM |
| `natural` | Layout phrases → **LLM** → rules (best for casual speech) |
| `llm` | LLM only (if enabled) |
| `rules` | No LLM |

## Other local servers

Any **OpenAI-compatible** endpoint works (LM Studio, llama.cpp server, LocalAI):

```json
"provider": "openai_compatible",
"base_url": "http://127.0.0.1:1234/v1",
"llm_model": "your-model-name"
```

Cloud OpenAI still works:

```json
"provider": "openai",
"llm_model": "gpt-4o-mini",
"openai_api_key_env": "OPENAI_API_KEY"
```

## Model tips

- **3B–7B instruct** models are enough for command JSON.
- Keep **temperature 0** (already set) for stable plans.
- If JSON breaks, try `qwen2.5:3b` or step up to `7b`.
- First call may be slow (model load); later commands are faster.

## Example

You say:

> “I'm going to work — open my Alexandr Chrome, YouTube and ChatGPT, put Cursor on the right full height, and turn the volume down a bit”

The local LLM might output:

```json
{
  "steps": [
    {"action": "run_preset", "params": {"preset_id": "alexandr_browser_stack"}},
    {"action": "apply_layout", "params": {"layout_id": "cursor_right_chrome_tl_telegram_bl"}},
    {"action": "adjust_volume", "params": {"delta": -15}}
  ]
}
```

The executor runs those steps the same way as voice-exact rules.

## Safety

- Invalid actions are rejected by the executor.
- Keep `hybrid` if you want instant paths for phrases you say 100×/day (`focus cursor`).
- Logs show `"parser": "llm:ollama"` so you can debug misparses.

## Cost

**$0 per command** after hardware — only electricity + one-time model download.
