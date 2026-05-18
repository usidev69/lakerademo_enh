# i18n Multilanguage Support — Lakera Guard Demo

**Date:** 2026-05-18  
**Status:** Approved  
**Approach:** Option A — `data-i18n` attribute + JS translation dictionary (no external dependencies)

---

## Scope

Add UI language switching (ES / EN / FR / IT) to `index.html`. All interface text and demo prompt content changes when the language is switched. User-created or parquet-imported prompts are not affected.

---

## Architecture

### State

Add `lang` to the top-level `state` object:

```js
const state = {
  lang: 'es',   // new field
  theme: 'dark',
  // ...
};
```

### Translation dictionary

A single `TRANSLATIONS` constant object defined once in the `<script>` block, before any functions:

```js
const TRANSLATIONS = {
  es: { 'btn.run': '▶ Ejecutar', ... },
  en: { 'btn.run': '▶ Run', ... },
  fr: { 'btn.run': '▶ Exécuter', ... },
  it: { 'btn.run': '▶ Esegui', ... },
};
```

Flat key → string map per locale. Keys use dot-notation namespacing: `btn.*`, `panel.*`, `modal.*`, `status.*`, `sidebar.*`, `arch.*`, `badge.*`, `error.*`, `prompt.*`.

### t() helper

```js
function t(key) {
  return (TRANSLATIONS[state.lang] ?? {})[key]
      ?? (TRANSLATIONS.es ?? {})[key]
      ?? key;
}
```

Fallback chain: active lang → Spanish → raw key. This ensures nothing breaks if a translation is missing.

---

## DOM Static Text

Elements with translatable text receive `data-i18n="key"` attribute:

```html
<button class="btn btn-success" id="btnRun" data-i18n="btn.run">▶ Ejecutar</button>
```

Elements with translatable `title` or `placeholder` attributes receive:
- `data-i18n-title="key"` → sets `el.title`
- `data-i18n-placeholder="key"` → sets `el.placeholder`

### applyLang()

```js
function applyLang() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    el.title = t(el.dataset.i18nTitle);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
  document.documentElement.lang = state.lang;
}
```

Called once on page load and every time `setLang()` is invoked.

---

## Dynamic JS Strings

All hardcoded Spanish strings inside JS functions are replaced with `t('key')` calls.

### Affected functions and key areas

| Function / Area | Example replacement |
|---|---|
| `setTheme()` | `setStatus(t('status.theme') + t, 'ok')` |
| `runPipeline()` | Status pill texts, innerHTML error blocks |
| `finishPipeline()` | `t('status.pipeline.done')` / `t('status.pipeline.blocked')` |
| `resetResults()` | Empty-state innerHTML uses `t()` for text nodes |
| `selectPrompt()` | `setStatus(t('status.prompt.selected') + ...)` |
| `updateInputPanel()` | Placeholder text, transform badge text |
| `renderPrompts()` | Empty-state "no results" text |
| `catBadge()` | Badge labels: Inyección → `t('badge.injection')`, etc. |
| `renderArch()` | Node labels and tooltips via `archNodes` data |
| `toggleEditMode()` | Button titles for edit/save |
| `resetWorkingText()` | Status message |
| `importParquetFile()` | Status message after import |
| Error blocks (LLM, Lakera IN/OUT) | All Spanish inline HTML strings |

### archNodes

The `archNodes` array labels and tips are converted to i18n keys:

```js
const archNodes = [
  { id:'user', icon:'👤', labelKey:'arch.user.label', cls:'n-user', modal:'modalTransform', tipKey:'arch.user.tip' },
  // ...
];
```

`renderArch()` calls `t(n.labelKey)` and `t(n.tipKey)`.

---

## Demo Prompts Multilanguage

A `DEMO_PROMPTS` constant holds the 10 demo prompts in each of the four languages:

```js
const DEMO_PROMPTS = {
  es: [ { id:1, name:'Saludo simple', ... }, ... ],
  en: [ { id:1, name:'Simple greeting', ... }, ... ],
  fr: [ { id:1, name:'Salutation simple', ... }, ... ],
  it: [ { id:1, name:'Saluto semplice', ... }, ... ],
};
```

Each prompt has: `id`, `name`, `category`, `text`, `desc`.  
Categories remain as fixed codes (`normal`, `injection`, `jailbreak`, `sensitive`, `custom`) — only the badge labels are translated.

### Prompt replacement on language change

```js
function reloadDemoPrompts(lang) {
  // Only replace prompts that are not user-created or parquet-imported
  const userPrompts = state.prompts.filter(p => p.source === 'user' || p.source === 'parquet');
  state.prompts = [...DEMO_PROMPTS[lang], ...userPrompts];
  // Re-assign sequential IDs to avoid collisions
  let id = 1;
  state.prompts.forEach(p => { p.id = id++; });
  state.selectedPromptId = null;
  renderPrompts();
  resetResults();
  // Clear selection UI
  document.getElementById('btnRun').disabled = true;
  document.getElementById('btnEditPrompt').disabled = true;
  document.getElementById('btnDeletePrompt').disabled = true;
  document.getElementById('sbPromptName').textContent = '';
}
```

---

## Language Selector UI

A `<select>` element is added to `.header-actions` in the HTML, between the `|` separator and the "Cargar Config" button:

```html
<select id="langSelect" class="btn btn-sm" onchange="setLang(this.value)" title="Cambiar idioma / Change language">
  <option value="es">🇪🇸 ES</option>
  <option value="en">🇬🇧 EN</option>
  <option value="fr">🇫🇷 FR</option>
  <option value="it">🇮🇹 IT</option>
</select>
```

Styled via the existing `.btn.btn-sm` class — no new CSS needed.

---

## setLang()

```js
function setLang(code) {
  if (!TRANSLATIONS[code]) return;
  state.lang = code;
  document.getElementById('langSelect').value = code;
  reloadDemoPrompts(code);
  applyLang();
  localStorage.setItem('lang', code);
  setStatus(t('status.lang.changed'), 'ok');
}
```

---

## Persistence

On page load (inside `init()`):

```js
const savedLang = localStorage.getItem('lang');
if (savedLang && TRANSLATIONS[savedLang]) state.lang = savedLang;
```

`applyLang()` is called once at the end of `init()` after the DOM is fully rendered.

---

## Translation Coverage

All four locales must cover:

**Buttons:** run, stop, new, edit, delete, save, cancel, load config, save config, create theme, apply, undo, reset, config user  
**Panel titles:** architecture, input prompt, lakera analysis, llm response  
**Status pills:** idle, running, ok, blocked, waiting, no selection, analyzing, completed, error  
**Sidebar:** label, search placeholder, toolbar buttons  
**Modal titles and form labels:** all 6 modals (user, lakeraIn, lakeraOut, LLM, output, prompt editor, transform, theme editor)  
**Architecture nodes:** 5 node labels + 5 tooltips  
**Badge labels:** injection, jailbreak, normal, sensitive, custom  
**Status bar messages:** ~15 dynamic strings  
**Error messages:** LLM error, Lakera IN error, Lakera OUT error, no API key  
**Empty states:** 4 panel empty states  
**Demo prompts:** 10 prompts × 4 languages = 40 prompt objects  

---

## Out of Scope

- Right-to-left language support
- Plural forms
- Date/number locale formatting
- Translation of user-created or parquet-imported prompts
- The proxy.py backend (Python only, no UI)
