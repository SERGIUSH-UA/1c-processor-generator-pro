# Claude Project Template: 1C Processor Generator

## How to Create Claude Project

### Method 1: GitHub Integration (Recommended)

1. Go to [claude.ai](https://claude.ai)
2. Create new **Project** (click Projects → New Project)
3. Name it: "1C Processor Generator"
4. Click **"Connect GitHub Repository"**
5. Select `1c-processor-generator` repo
6. In **"Configure files"**, select:
   - `CLAUDE.md` (auto-included)
   - `docs/LLM_WEB_LITE.md`
   - `docs/QUICK_REFERENCE.md`
   - `examples/yaml/` (selected examples)

### Method 2: Manual Setup

1. Create new Project in Claude.ai
2. Go to **Project Settings** → **Custom Instructions**
3. Copy content from `project_instructions.md` below
4. Upload files to project:
   - `docs/LLM_WEB_LITE.md`
   - `docs/QUICK_REFERENCE.md`

---

## Project Structure

```
Claude Project: 1C Processor Generator
├── Custom Instructions (from project_instructions.md)
├── Connected Repo: 1c-processor-generator
│   ├── CLAUDE.md (auto)
│   ├── docs/LLM_WEB_LITE.md
│   └── docs/QUICK_REFERENCE.md
└── Conversations...
```

---

## Project Instructions

Copy this to **Project Settings → Custom Instructions**:

```
You are a 1C:Enterprise processor generation assistant. You help users create
external data processors (.epf files) using the 1c-processor-generator tool.

## Your Capabilities
1. Generate YAML configuration files (config.yaml)
2. Generate BSL handler code (handlers.bsl)
3. Explain 1C development concepts
4. Debug and fix generator-related issues

## Output Format
Always output two separate code blocks:
1. config.yaml - YAML configuration
2. handlers.bsl - BSL handlers (procedures with directives)

## Key Rules
1. Each handler is Процедура with &НаКлиенте or &НаСервере
2. Add is_value_table: true for ValueTable elements
3. Add default: true to main form
4. Use &НаСервере for server procedures
5. Validate all references (attributes, tables, commands)

## Languages
- Internal names: Latin or Cyrillic
- User-facing text: Russian (title_ru) and Ukrainian (title_uk)
- Handler names: Cyrillic allowed

## Documentation
Refer to connected files for:
- YAML syntax: LLM_WEB_LITE.md
- Element reference: QUICK_REFERENCE.md
- Full patterns: LLM_CORE.md

## Response Style
1. Ask clarifying questions for complex requirements
2. Explain BSL code when generating
3. Suggest improvements when appropriate
4. Validate before outputting final code
```

---

## Testing the Project

After setup, test with these prompts:

### Test 1: Simple Form
```
Створи обробку для введення контактних даних:
- Поля: ПІБ, Телефон, Email
- Кнопка "Зберегти"
```

### Test 2: Report with Table
```
Створи звіт по продажах:
- Фільтри: Дата з, Дата по
- Таблиця: Товар, Кількість, Сума
- Кнопка "Сформувати"
```

### Test 3: Master-Detail
```
Створи форму ролей користувачів:
- Ліворуч: список ролей
- Праворуч: користувачі вибраної ролі
- При виборі ролі оновлюється список
```

---

## Benefits of Claude Project

| Feature | Benefit |
|---------|---------|
| **GitHub Integration** | Auto-access to full documentation |
| **Persistent Context** | No need to re-upload files |
| **Conversation History** | Reference previous generations |
| **Shared Instructions** | Consistent behavior across chats |

---

## Sharing the Project

To share with team members:
1. Go to Project Settings
2. Click **"Share"**
3. Add team member emails
4. They get same context and instructions

---

## Files Reference

| File | Purpose | Where to Get |
|------|---------|--------------|
| `LLM_WEB_LITE.md` | Core documentation | `docs/` folder |
| `QUICK_REFERENCE.md` | Element reference | `docs/` folder |
| `CLAUDE.md` | Project instructions | Root folder |
| Examples | Sample configs | `examples/yaml/` |

---

## Troubleshooting

### "I don't have access to the file"
- Check GitHub connection
- Verify file is in "Configure files" list
- Try re-connecting repository

### "Generated code has errors"
- Ask Claude to validate the output
- Reference specific documentation section
- Share error message for debugging

### "Context seems limited"
- Use Projects instead of regular chat
- Enable "Include project context" in chat
