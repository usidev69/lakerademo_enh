# Lakera Guard Demo

An interactive single-page application for exploring and testing [Lakera Guard](https://www.lakera.ai/) — an AI security layer that detects prompt injections, jailbreaks, PII leakage, and other LLM threats in real time.

---

## What it does

The demo simulates a full LLM pipeline with Lakera Guard protecting both the input and the output:

```
User prompt → Lakera Guard IN → LLM → Lakera Guard OUT → Response
```

You can send prompts through the pipeline, see exactly what Lakera Guard detects at each stage, and observe how the pipeline behaves when a threat is blocked, warned, or allowed through.

---

## Features

### Pipeline architecture
The architecture panel shows the five nodes of the pipeline as clickable cards. Each card opens a configuration modal:

| Node | Description |
|---|---|
| **User** | System prompt and user context configuration |
| **Lakera Guard IN** | Screens the user prompt before it reaches the LLM |
| **LLM** | The language model that generates the response |
| **Lakera Guard OUT** | Screens the LLM response before it is shown |
| **Output** | Response display format and metadata options |

### Prompt library
The left sidebar holds a library of test prompts organised by category:

- **Normal** — benign prompts with no expected threats
- **Prompt injection** — attempts to hijack the model's instructions
- **Jailbreak** — attempts to bypass safety filters (DAN-style, roleplay framing, etc.)
- **Sensitive data** — prompts containing PII such as names, national IDs, and bank account numbers, adapted per language (DNI, SSN, NIR, CF)
- **Custom** — prompts you create manually or import from a Parquet file

You can search, create, edit, delete, and import prompts. Parquet files with a `text`, `prompt`, `content`, or `message` column are automatically detected.

### Red Team transformations
Before running the pipeline you can apply one or more transformations to the prompt to test whether obfuscated inputs bypass detection:

| Category | Transformations |
|---|---|
| **Encoding** | ROT13, Base64, Hexadecimal, Binary, Morse |
| **Visual obfuscation** | L33tspeak, Unicode homoglyphs, Zero-width spaces, Dot-separated, Reversed text, Scrambled interior |
| **LLM-assisted** | Translate to exotic language, Paraphrase, Convert to poem, Metaphor/story, Roleplay framing, Strategic typos |

Transformations can be chained. The original prompt is preserved and can be restored at any time.

### Lakera Guard analysis panel
After running the pipeline the Guard panel shows, for each of Guard IN and Guard OUT:

- Whether the prompt/response was flagged or clean
- Which detectors fired (prompt injection, jailbreak, PII, secrets, toxicity, malicious links, content moderation, custom regex)
- The raw payload returned by the API, including matched PII entities and their locations
- The full raw JSON response for debugging

### LLM response panel
Shows the model's response with optional metadata (model name, input/output token counts, latency). When Guard OUT detects a threat, the response is either blocked, shown with a warning banner, or silently logged — depending on the configured action.

### Configuration
All components are configured through their respective modals, with settings persisted in the browser's `localStorage`. A full configuration can also be saved to and loaded from a JSON file, and pre-populated via a `.env` file on the server.

**Supported LLM providers:** OpenAI, Anthropic, Google Gemini, Ollama, LM Studio.

### Multilingual UI
The interface is fully translated into **Spanish, English, French, and Italian**. The language can be switched at any time from the header. Demo prompts are also replaced with culturally-adapted versions in the selected language. The preference is saved across sessions.

---

## Architecture

The application is a **zero-dependency single-page app** (`index.html`). All logic runs in the browser — there is no backend framework, no build step, and no npm.

A lightweight Python proxy (`proxy.py`, ~200 lines, stdlib only) is included to work around the browser's CORS restrictions when calling the Lakera API directly. It also serves the HTML file and exposes a `/api/config` endpoint that injects `.env` values into the UI on load.

```
browser (index.html)
    │
    ├─ calls LLM APIs directly (OpenAI, Anthropic, Gemini, Ollama, LM Studio)
    │
    └─ calls Lakera API via proxy
            │
            └─ python3 proxy.py  ──►  https://api.lakera.ai/v2/guard
```

---

## Quick start

See [INSTALL.md](INSTALL.md) for full installation instructions.

```bash
# 1. Copy and fill in your API keys
cp .env.example .env
# edit .env

# 2. Start the proxy server
python3 proxy.py

# 3. Open the app
#    http://localhost:8080
```

---

## Project structure

```
lakerademo/
├── index.html        # The entire frontend application
├── proxy.py          # CORS proxy + static file server
├── .env.example      # Environment variable template
├── INSTALL.md        # Installation guide
└── README.md         # This file
```
