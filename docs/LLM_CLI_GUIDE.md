# LLM CLI Guide - Command Templates

**Quick reference for LLMs working with 1C Processor Generator**

---

## 📦 FREE vs PRO

| Feature | FREE | PRO |
|---------|------|-----|
| XML generation | ✅ Unlimited | ✅ Unlimited |
| Sync tool | ✅ | ✅ |
| Documentation | ✅ | ✅ |
| EPF compilation | ❌ | ✅ |
| Семантична валідація | ❌ | ✅ |
| Watermark in code | Yes | No |

**PRO License:** https://itdeo.tech/1c-processor-generator

---

## 🎯 Generation Templates

### Template 1: Generate EPF (PRO - Try First)

```bash
python -m 1c_processor_generator yaml \
  --config {config_path} \
  --handlers-file {handlers_path} \
  --output {target_directory} \
  --output-format epf
```

**Use when:** User asks to generate a processor (default case)

**Requires:** PRO license OR active trial

### Template 2: Generate XML (FREE - Fallback)

```bash
python -m 1c_processor_generator yaml \
  --config {config_path} \
  --handlers-file {handlers_path} \
  --output {target_directory}
```

**Use when:**
- Template 1 returns "Designer не знайдено"
- Template 1 returns "EPF компіляція потребує PRO ліцензії"
- User explicitly asks for XML only

---

## 🔑 License Commands

### Check License Status

```bash
python -m 1c_processor_generator license-status
```

**Output (no license):**
```
📋 Статус ліцензії: FREE
   PRO функції недоступні

💡 Активуйте ліцензію: python -m 1c_processor_generator activate YOUR-KEY
💡 Або спробуйте trial: python -m 1c_processor_generator trial
```

**Output (with license):**
```
📋 Статус ліцензії: PRO
   Тип: year
   Діє до: 2025-12-13
   Машин: 1/2
```

### Activate License

```bash
python -m 1c_processor_generator activate PRO-XXXX-XXXX-XXXX
```

**Success:**
```
🔑 Активація ліцензії: PRO-XXXX***
✅ Ліцензію активовано!
   Тип: year
   Діє до: 2025-12-13
```

**Errors:**
- `Невірний ключ ліцензії` → key is invalid
- `Ліцензія вже використана на максимальній кількості машин` → machine limit reached
- `Термін дії ліцензії закінчився` → license expired

### Request Trial (7 days)

```bash
python -m 1c_processor_generator trial
```

**Success:**
```
🎁 Запит trial ліцензії...
✅ Trial активовано!
   Діє до: 2024-12-20 (7 днів)
```

**Error:**
- `Trial вже використано на цій машині` → trial already used

### Clear License Cache

```bash
python -m 1c_processor_generator cache-clear
```

**Use when:** Troubleshooting license issues

---

## 📋 5 Rules (DO NOT BREAK)

1. ✅ **Always use `--output`** - files go directly to target directory
2. ❌ **Never copy files** - no robocopy, xcopy, copy after generation
3. 🔄 **Auto-fallback** - license error or "Designer не знайдено" → use Template 2
4. 🚫 **No improvisation** - use templates exactly, only replace `{placeholders}`
5. 📝 **Parameter order** - `yaml` → `--config` → `--handlers-file` → `--output` → `--output-format`

---

## 🚀 Decision Tree

```
User asks to generate processor
    ↓
Check: python -m 1c_processor_generator license-status
    ↓
┌─────────────────────────┬───────────────────────────┐
│ PRO/Trial active        │ FREE (no license)         │
│ → Use Template 1 (EPF)  │ → Use Template 2 (XML)    │
│                         │   OR suggest trial        │
└─────────────────────────┴───────────────────────────┘
    ↓
If Template 1 fails with:
- "Designer не знайдено" → Template 2 (XML)
- "PRO ліцензія потрібна" → Suggest trial or Template 2
```

---

## 💡 Example Workflows

### Workflow 1: User Has License

```bash
# 1. Verify license
python -m 1c_processor_generator license-status
# Output: PRO, year, expires 2025-12-13

# 2. Generate EPF
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output output/ \
  --output-format epf

# Done - EPF file created
```

### Workflow 2: User Without License (Suggest Trial)

```bash
# 1. Check status
python -m 1c_processor_generator license-status
# Output: FREE

# 2. Suggest trial
python -m 1c_processor_generator trial
# Output: Trial активовано! 7 днів

# 3. Now generate EPF
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output output/ \
  --output-format epf
```

### Workflow 3: User Without License (XML Fallback)

```bash
# 1. Check status
python -m 1c_processor_generator license-status
# Output: FREE

# 2. Generate XML (always works)
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output output/

# 3. Tell user: "XML згенеровано. Для EPF потрібна PRO ліцензія."
```

---

## ❌ Common Mistakes

```bash
# ❌ Generate without --output, then copy
python -m 1c_processor_generator yaml --config config.yaml --handlers-file handlers.bsl
robocopy tmp/Processor output/

# ❌ Try EPF without checking license first
python -m 1c_processor_generator yaml --config config.yaml --output-format epf
# Error: PRO ліцензія потрібна

# ❌ Wrong parameter order
python -m 1c_processor_generator --config config.yaml yaml --handlers-file handlers.bsl
```

---

## 🔧 Troubleshooting

| Error | Solution |
|-------|----------|
| `PRO ліцензія потрібна` | `trial` command or use XML fallback |
| `Designer не знайдено` | Use Template 2 (XML), install 1C Designer |
| `Невірний ключ` | Check key format: PRO-XXXX-XXXX-XXXX |
| `Термін дії закінчився` | Purchase new license |
| `Перевищено ліміт машин` | Deactivate on other machine or upgrade |
| `Сервер недоступний` | Grace period 7 days, check internet |

---

## 📞 Support

- **Email:** support@itdeo.tech
- **Buy PRO:** https://itdeo.tech/1c-processor-generator

---

**Remember:** Check license status first, then choose appropriate template.
