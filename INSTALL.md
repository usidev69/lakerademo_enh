# Lakera Guard Demo — Guía de instalación

Esta guía explica cómo instalar y ejecutar la aplicación en un ordenador nuevo a partir
del fichero `.zip` que contiene el directorio del proyecto.

---

## Requisitos previos

| Software | Versión mínima | Notas |
|---|---|---|
| Python | **3.12** | Incluido en la mayoría de Linux modernos; macOS/Windows requieren instalación |
| Conexión a Internet | — | El proxy llama a la API de Lakera; la UI carga `hyparquet` desde CDN |

No se necesita ninguna dependencia de Python adicional (el servidor usa exclusivamente la
biblioteca estándar).

---

## 1 · Instalar Python 3.12+

### Windows

1. Abre <https://www.python.org/downloads/windows/> y descarga el instalador
   **Python 3.12.x — Windows installer (64-bit)**.
2. Ejecuta el instalador. **Marca** la casilla _"Add Python to PATH"_ antes de hacer clic
   en _Install Now_.
3. Verifica la instalación abriendo **PowerShell** o **Símbolo del sistema** y ejecutando:
   ```
   python --version
   ```
   Debe mostrar `Python 3.12.x` (o superior).

### macOS

**Opción A — Instalador oficial (recomendado para usuarios sin experiencia):**

1. Abre <https://www.python.org/downloads/macos/> y descarga el instalador
   **Python 3.12.x — macOS universal2**.
2. Abre el `.pkg` descargado y sigue el asistente.
3. Verifica en **Terminal**:
   ```
   python3 --version
   ```

**Opción B — Homebrew:**

```bash
brew install python@3.12
```
**Opción C - uv:**
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

En distribuciones basadas en RPM (Fedora, RHEL, Rocky Linux):

```bash
sudo dnf install -y python3.12
```

Verifica:

```bash
python3.12 --version
```

---

## 2 · Extraer el fichero ZIP

### Windows (Explorador de archivos)

Haz clic derecho sobre el `.zip` → **Extraer todo…** → elige la carpeta de destino →
**Extraer**.

### Windows (PowerShell)

```powershell
Expand-Archive -Path lakerademo.zip -DestinationPath C:\ruta\destino
```

### macOS / Linux

```bash
unzip lakerademo.zip -d /ruta/destino
```

Esto crea el directorio `lakerademo/` con todos los ficheros de la aplicación.

---

## 3 · Configurar las API keys

La aplicación necesita al menos una **Lakera API key** y, opcionalmente, una clave de
proveedor LLM (OpenAI, Anthropic, Gemini, etc.) para que el chat funcione.

1. Entra en el directorio extraído:
   ```bash
   cd /ruta/destino/lakerademo
   ```
2. Copia el fichero de ejemplo y ábrelo con cualquier editor de texto:

   ```bash
   # macOS / Linux
   cp .env.example .env

   # Windows (PowerShell)
   Copy-Item .env.example .env
   ```

3. Rellena los valores necesarios. Ejemplo mínimo:

   ```
   LAKERA_API_KEY=tu_lakera_api_key_aqui

   LLM_PROVIDER=openai
   LLM_API_KEY=tu_openai_api_key_aqui
   LLM_MODEL=gpt-4o
   ```

   Consulta la sección de referencia al final de este fichero para conocer todas las
   variables disponibles.

> **Importante:** El fichero `.env` no admite comentarios en la misma línea que un valor
> (`KEY=valor  # esto rompe el parser`). Los comentarios deben ir en su propia línea,
> empezando por `#`.

---

## 4 · Ejecutar el servidor

Desde el directorio `lakerademo/`:

```bash
# macOS / Linux
python3 proxy.py

# Windows
python proxy.py
```

Puerto personalizado (opcional):

```bash
python3 proxy.py 9090
```

Al arrancar verás algo similar a:

```
  .env  loaded 4 variable(s): LAKERA_API_KEY, LLM_PROVIDER, LLM_API_KEY, LLM_MODEL
  env   config: {'lakeraApiKey': 'lakera…', 'llmProvider': 'openai', ...}

Lakera Guard Demo  →  http://localhost:8080
Proxy endpoint     →  http://localhost:8080/proxy/lakera
Env config         →  http://localhost:8080/api/config
Press Ctrl+C to stop.
```

---

## 5 · Abrir la aplicación

Abre tu navegador y ve a:

```
http://localhost:8080
```

La interfaz se carga completamente en el navegador. No hace falta instalar nada más.

Para detener el servidor pulsa **Ctrl + C** en la terminal.

---

## Referencia de variables de entorno / `.env`

```
# ── Lakera Guard ───────────────────────────────────────────────────
LAKERA_API_KEY=               # Requerido

# Proyectos específicos para Guard IN (screening de prompts)
LAKERA_GUARD_IN_PROJECT_ID=
LAKERA_GUARD_IN_PROJECT_NAME=

# Proyectos específicos para Guard OUT (screening de respuestas)
LAKERA_GUARD_OUT_PROJECT_ID=
LAKERA_GUARD_OUT_PROJECT_NAME=

# Fallback compartido si no se especifican los valores IN/OUT anteriores
LAKERA_PROJECT_ID=
LAKERA_PROJECT_NAME=

# Opcional: sobreescribir el endpoint por defecto
# LAKERA_ENDPOINT=https://api.lakera.ai/v2/guard

# ── Proveedor LLM ──────────────────────────────────────────────────
# Proveedores soportados: openai | anthropic | gemini | ollama | lmstudio
LLM_PROVIDER=openai
LLM_API_KEY=
LLM_MODEL=

# Solo necesario para ollama / lmstudio
# LLM_ENDPOINT=http://localhost:11434

# Opcional: sobreescribir el system prompt por defecto
# LLM_SYSTEM_PROMPT=You are a helpful assistant.
```

Las **variables de entorno del sistema** tienen siempre prioridad sobre los valores del
fichero `.env`. Esto permite, por ejemplo, inyectar las claves desde un gestor de secretos
o desde la configuración de un CI/CD sin modificar el fichero.

---

## Solución de problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `python: command not found` | Python no está en el PATH | Usa `python3` en lugar de `python`, o reinstala marcando "Add to PATH" |
| `Address already in use` | El puerto 8080 está ocupado | Arranca con otro puerto: `python3 proxy.py 9090` |
| La UI carga en blanco o falla hyparquet | Sin conexión a Internet | La UI descarga `hyparquet` desde CDN (`esm.sh`) al arrancar; necesita conexión |
| "Lakera API error 401" | API key incorrecta o vacía | Comprueba `LAKERA_API_KEY` en `.env`; no uses comillas y evita comentarios en la misma línea |
| "Target host not allowed" | Endpoint personalizado con host no permitido | El proxy solo acepta `api.lakera.ai`, `us-east-1.api.lakera.ai` y `eu-west-1.api.lakera.ai` |
| El modelo del LLM no se aplica | Valor de `LLM_MODEL` vacío en `.env` | Rellena `LLM_MODEL` con un nombre de modelo válido (p. ej. `gpt-4o`, `gemini-2.0-flash`) |
