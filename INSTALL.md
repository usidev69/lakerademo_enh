# Lakera Guard Demo — Installation Guide

This guide explains how to install and run the application on a new machine from the
`.zip` file containing the project directory.

---

## Prerequisites

| Software | Minimum version | Notes |
|---|---|---|
| Python | **3.12** | Included in most modern Linux distros; macOS/Windows require installation |
| Internet connection | — | The proxy calls the Lakera API; the UI loads `hyparquet` from CDN |

No additional Python dependencies are required (the server uses only the standard library).

---

## 1 · Install Python 3.12+

### Windows

1. Open <https://www.python.org/downloads/windows/> and download the
   **Python 3.12.x — Windows installer (64-bit)**.
2. Run the installer. **Check** the _"Add Python to PATH"_ checkbox before clicking
   _Install Now_.
3. Verify the installation by opening **PowerShell** or **Command Prompt** and running:
   ```
   python --version
   ```
   It should display `Python 3.12.x` (or higher).

### macOS

**Option A — Official installer (recommended for non-technical users):**

1. Open <https://www.python.org/downloads/macos/> and download the
   **Python 3.12.x — macOS universal2** installer.
2. Open the downloaded `.pkg` file and follow the wizard.
3. Verify in **Terminal**:
   ```
   python3 --version
   ```

**Option B — Homebrew:**

```bash
brew install python@3.12
```

**Option C — uv:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
cd lakerademo
uv init
uv venv
source .venv/bin/activate
```

### Linux (Debian / Ubuntu)

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv
```

On RPM-based distributions (Fedora, RHEL, Rocky Linux):

```bash
sudo dnf install -y python3.12
```

Verify:

```bash
python3.12 --version
```

---

## 2 · Extract the ZIP file

### Windows (File Explorer)

Right-click the `.zip` file → **Extract All…** → choose a destination folder → **Extract**.

### Windows (PowerShell)

```powershell
Expand-Archive -Path lakerademo.zip -DestinationPath C:\path\to\destination
```

### macOS / Linux

```bash
unzip lakerademo.zip -d /path/to/destination
```

This creates the `lakerademo/` directory with all application files.

---

## 3 · Configure API keys

The application requires at least one **Lakera API key** and, optionally, an LLM provider
key (OpenAI, Anthropic, Gemini, etc.) for the chat to work.

1. Enter the extracted directory:
   ```bash
   cd /path/to/destination/lakerademo
   ```
2. Copy the example file and open it with any text editor:

   ```bash
   # macOS / Linux
   cp .env.example .env

   # Windows (PowerShell)
   Copy-Item .env.example .env
   ```

3. Fill in the required values. Minimal example:

   ```
   LAKERA_API_KEY=your_lakera_api_key_here

   LLM_PROVIDER=openai
   LLM_API_KEY=your_openai_api_key_here
   LLM_MODEL=gpt-4o
   ```

   See the reference section at the end of this file for all available variables.

> **Important:** The `.env` file does not support inline comments on the same line as a
> value (`KEY=value  # this breaks the parser`). Comments must be on their own line,
> starting with `#`.

---

## 4 · Start the server

From the `lakerademo/` directory:

```bash
# macOS / Linux
python3 proxy.py

# Windows
python proxy.py
```

Custom port (optional):

```bash
python3 proxy.py 9090
```

On startup you will see something like:

```
  .env  loaded 4 variable(s): LAKERA_API_KEY, LLM_PROVIDER, LLM_API_KEY, LLM_MODEL
  env   config: {'lakeraApiKey': 'lakera…', 'llmProvider': 'openai', ...}

Lakera Guard Demo  →  http://localhost:8080
Proxy endpoint     →  http://localhost:8080/proxy/lakera
Env config         →  http://localhost:8080/api/config
Press Ctrl+C to stop.
```

---

## 5 · Open the application

Open your browser and navigate to:

```
http://localhost:8080
```

The interface runs entirely in the browser. No further installation is needed.

To stop the server press **Ctrl + C** in the terminal.

---

## Environment variable reference / `.env`

```
# ── Lakera Guard ───────────────────────────────────────────────────
LAKERA_API_KEY=               # Required

# Specific projects for Guard IN (prompt screening)
LAKERA_GUARD_IN_PROJECT_ID=
LAKERA_GUARD_IN_PROJECT_NAME=

# Specific projects for Guard OUT (response screening)
LAKERA_GUARD_OUT_PROJECT_ID=
LAKERA_GUARD_OUT_PROJECT_NAME=

# Shared fallback if the IN/OUT values above are not set
LAKERA_PROJECT_ID=
LAKERA_PROJECT_NAME=

# Optional: override the default endpoint
# LAKERA_ENDPOINT=https://api.lakera.ai/v2/guard

# ── LLM Provider ───────────────────────────────────────────────────
# Supported providers: openai | anthropic | gemini | ollama | lmstudio
LLM_PROVIDER=openai
LLM_API_KEY=
LLM_MODEL=

# Required only for ollama / lmstudio
# LLM_ENDPOINT=http://localhost:11434

# Optional: override the default system prompt
# LLM_SYSTEM_PROMPT=You are a helpful assistant.
```

System environment variables always take precedence over values in the `.env` file.
This allows, for example, injecting keys from a secrets manager or a CI/CD configuration
without modifying the file.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `python: command not found` | Python not in PATH | Use `python3` instead of `python`, or reinstall with "Add to PATH" checked |
| `Address already in use` | Port 8080 is in use | Start on a different port: `python3 proxy.py 9090` |
| UI loads blank or hyparquet fails | No internet connection | The UI downloads `hyparquet` from CDN (`esm.sh`) on startup; internet required |
| "Lakera API error 401" | Incorrect or missing API key | Check `LAKERA_API_KEY` in `.env`; do not use quotes and avoid inline comments |
| "Target host not allowed" | Custom endpoint with a blocked host | The proxy only accepts `api.lakera.ai`, `us-east-1.api.lakera.ai` and `eu-west-1.api.lakera.ai` |
| LLM model setting not applied | `LLM_MODEL` empty in `.env` | Set `LLM_MODEL` to a valid model name (e.g. `gpt-4o`, `gemini-2.0-flash`) |
