# Using 1C Processor Generator with Web Chats

> **Guide for:** Claude.ai, ChatGPT, Google Gemini web interfaces

This guide explains how to use AI web chats to generate 1C:Enterprise processors with our YAML+BSL generator.

---

## Quick Platform Comparison

| Platform | Free Context | Best For |
|----------|--------------|----------|
| **Claude.ai** | 100K tokens | Full workflow with GitHub |
| **ChatGPT** | 8K tokens | Custom GPT assistant |
| **Gemini** | 32K tokens | File upload workflow |

---

## Method 1: Claude.ai Web

### Option A: GitHub Integration (Recommended)

**Setup:**
1. Go to [claude.ai](https://claude.ai)
2. Create a new Project or start a chat
3. Click **"Connect to GitHub"** (if available)
4. Select `1c-processor-generator` repository
5. Use **"Configure files"** to select relevant docs

**What happens:**
- `CLAUDE.md` automatically loaded into context
- Claude has access to full documentation
- Can reference any file from the repo

**Prompt example:**
```
Створи обробку для імпорту товарів з Excel.
Потрібно: поле для вибору файлу, таблиця для попереднього перегляду,
кнопка "Імпортувати".

Використовуй формат з docs/LLM_WEB_LITE.md
```

### Option B: Manual File Upload

**Setup:**
1. Download `LLM_WEB_LITE.md` from repo
2. Start new conversation in Claude.ai
3. Attach the file to your message

**Prompt example:**
```
[Attached: LLM_WEB_LITE.md]

На основі цієї документації створи обробку для розрахунку зарплати.
Поля: ПІБ, Оклад, Дні. Кнопка "Розрахувати".
```

---

## Method 2: ChatGPT

### Option A: Use Custom GPT (Easiest)

> Coming soon: "1C Processor Generator" in GPT Store

**How it will work:**
1. Search for "1C Processor Generator" in GPT Store
2. Start conversation
3. Describe what you need in natural language

### Option B: Create Your Own Project

**Setup:**
1. Go to [chat.openai.com](https://chat.openai.com)
2. Click **"Explore GPTs"** → **"Create"**
3. Or use **Projects** feature:
   - Click your profile → **Projects**
   - Create new project "1C Generator"
   - Upload `LLM_WEB_LITE.md` as knowledge file
   - Set custom instructions (see below)

**Custom Instructions template:**
```
You are a 1C:Enterprise processor generator assistant. You help users create
YAML configs and BSL handlers for the 1c-processor-generator tool.

Rules:
1. Always output config.yaml and handlers.bsl as separate code blocks
2. Each BSL handler is a Процедура with &НаКлиенте or &НаСервере directive
3. For tables, always add is_value_table: true
4. Add default: true to the main form
5. Use Cyrillic for user-facing names (title_ru, title_uk)
6. Use Latin or Cyrillic for internal names (name)

When user describes requirements, generate complete config.yaml and handlers.bsl.
```

### Option C: Manual (Free Tier)

**Setup:**
1. Copy content of `WEB_QUICK_START.md` (smallest doc)
2. Paste at the beginning of your conversation

**Prompt example:**
```
[Paste WEB_QUICK_START.md content here]

---

Тепер на основі цієї документації створи обробку:
- Назва: КалькуляторНДС
- Поля: Сумма (число), Ставка (число, default 20)
- Кнопка: Розрахувати
- Результат: СуммаСНДС
```

---

## Method 3: Google Gemini

### Setup

1. Go to [gemini.google.com](https://gemini.google.com)
2. Click **"+"** to start new conversation
3. Click **upload icon** (📎) to attach files
4. Upload `LLM_WEB_LITE.md`

**Tips:**
- Files stay in context for the whole conversation
- Can upload up to 10 files per prompt
- Free tier: 32K tokens (fits our lite doc easily)

**Prompt example:**
```
[Upload LLM_WEB_LITE.md]

Прочитай документацію і створи обробку для:
- Звіт по продажах за період
- Фільтри: дата початку, дата кінця, контрагент
- Таблиця результатів: Товар, Кількість, Сума
- Кнопка "Сформувати"
```

---

## Which Files to Use?

| Your Context | File to Use | Tokens |
|--------------|-------------|--------|
| ChatGPT Free | `WEB_QUICK_START.md` | ~2K |
| Gemini Free | `LLM_WEB_LITE.md` | ~5K |
| Claude Free | `LLM_WEB_LITE.md` or `LLM_CORE.md` | ~5-20K |
| Any Paid tier | Full docs via GitHub/upload | Any |

---

## Effective Prompting Tips

### 1. Be Specific About Requirements

**Bad:**
```
Зроби обробку для роботи з клієнтами
```

**Good:**
```
Зроби обробку для пошуку клієнтів:
- Поле пошуку: текстове, 50 символів
- Кнопка "Знайти"
- Таблиця результатів: Назва, ІПН, Телефон
- При виборі рядка показувати деталі клієнта
```

### 2. Specify Output Format

```
Створи config.yaml та handlers.bsl окремими блоками коду.
Використовуй формат з документації.
```

### 3. Ask for Validation

```
Перевір чи всі attribute: посилаються на існуючі атрибути,
і чи всі tabular_section: посилаються на value_tables.
```

### 4. Iterate Incrementally

```
1. Спочатку зроби базову форму без таблиці
2. Потім додай таблицю результатів
3. Потім додай логіку завантаження даних
```

---

## After Generation

### Step 1: Save Files

Save generated content to:
```
my_processor/
├── config.yaml      # YAML config
└── handlers.bsl     # BSL handlers
```

### Step 2: Run Generator

```bash
cd my_processor
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output output
```

### Step 3: Use Result

- **XML output:** Load in 1C Configurator, compile to EPF
- **EPF output:** Open directly in 1C:Enterprise

---

## Troubleshooting

### "Not enough context"

**Problem:** LLM says it doesn't understand the format

**Solution:** Make sure you uploaded the documentation file first

### "Invalid YAML"

**Problem:** Generated YAML has syntax errors

**Solution:** Ask LLM to validate:
```
Перевір синтаксис YAML - чи всі відступи правильні?
```

### "Unknown attribute"

**Problem:** Generator says attribute doesn't exist

**Solution:** Check that all `attribute:` values match names in `attributes:` section

### "Table is empty"

**Problem:** Table shows no data

**Solution:** Add `is_value_table: true` to Table element

---

## Example Prompt Library

### Simple Form
```
Створи обробку для введення контактних даних:
- Поля: ПІБ (рядок 200), Телефон (рядок 20), Email (рядок 100)
- Кнопка "Зберегти" - показує повідомлення з введеними даними
```

### Report with Table
```
Створи звіт "Залишки товарів":
- Фільтр: Склад (довідник)
- Таблиця: Товар, Кількість, Ціна, Сума
- Кнопка "Оновити"
```

### Master-Detail
```
Створи обробку "Ролі користувачів":
- Ліва таблиця: список ролей (Назва)
- Права таблиця: користувачі вибраної ролі (Логін, ПІБ)
- При виборі ролі оновлюється список користувачів
```

### Data Import
```
Створи обробку для імпорту з Excel:
- Поле вибору файлу
- Таблиця попереднього перегляду
- Кнопки "Завантажити" і "Імпортувати"
```

---

## Platform Updates (December 2025)

- **Claude.ai:** GitHub integration now available for Projects
- **ChatGPT:** Projects feature supports team sharing
- **Gemini:** Projects feature announced for late 2025

---

*For full documentation, see: [LLM_CORE.md](LLM_CORE.md), [LLM_PATTERNS_ESSENTIAL.md](LLM_PATTERNS_ESSENTIAL.md)*
