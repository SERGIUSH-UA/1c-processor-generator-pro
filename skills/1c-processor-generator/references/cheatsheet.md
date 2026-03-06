# 1C Processor Generator - Quick Reference

**One-page cheatsheet for fast development** | Version 2.69.0

---

## ⚠️ CRITICAL RULES (READ FIRST!)

### 1. **ONLY Russian Cyrillic Alphabet**
```yaml
❌ WRONG: ПошуковийЗапит    # Ukrainian: і, ї, є, ґ
✅ RIGHT: ПоисковыйЗапрос   # Russian: и, й, е, г
```
**Allowed:** `а-я А-Я ё Ё a-z A-Z 0-9 _`
**NOT allowed:** `і ї є ґ І Ї Є Ґ` (visually similar but DIFFERENT Unicode!)

### 2. **NO BSL Reserved Keywords**
```yaml
❌ WRONG: name: Выполнить, Экспорт, Импорт, Процедура
✅ RIGHT: name: ВыполнитьКоманду, ЭкспортироватьДанные
```
[Full list: 40+ keywords in validators.py]

### 3. **Valid StdPicture Names Only**
```yaml
❌ WRONG: StdPicture.CheckMark, StdPicture.Save
✅ RIGHT: StdPicture.Write, StdPicture.SaveFile
```
📄 **Full list:** [VALID_PICTURES.md](VALID_PICTURES.md) (130+ pictures)

### 4. **Handler File Naming = YAML name**
```yaml
commands:
  - name: LoadDataНаСервере  # ← YAML name

# File must be: handlers/LoadDataНаСервере.bsl
# NOT: handlers/LoadDataServer.bsl ❌
```

### 5. **Multilingual (v2.69.0+) & Read-Only**
```yaml
# Compact Multilang Syntax (v2.69.0+):
languages: [ru, uk]  # Project-level declaration

# Pipe format (most compact, recommended):
title: "Название | Назва"

# Array format:
title: ["Название", "Назва"]

# Dict format (legacy):
title: {ru: "Название", uk: "Назва"}

# Read-only elements
read_only: true  # For InputField, Table, UsualGroup, columns
```

---

## 🚀 Quick Start (5 Steps)

```bash
# 1. Create processors/MyProcessor/config.yaml
processor:
  name: MyProcessor
  title_ru: Мой процессор
  platform_version: "2.11"  # 2.10, 2.11, 2.18, 2.19, etc.

attributes:
  - name: TextField
    type: string

# 2. Create processors/MyProcessor/handlers.bsl
Сообщить("Процессор открыт!");

# 3. Generate
python -m 1c_processor_generator yaml \
  --config processors/MyProcessor/config.yaml \
  --handlers-file processors/MyProcessor/handlers.bsl

# 4. Output: tmp/MyProcessor/
# 5. Load .epf into 1C
```

---

## 📊 ValueTable vs TabularSection

**Key Question:** Does data need to survive form close?

| Feature | TabularSection | ValueTable |
|---------|----------------|------------|
| **Saved to DB?** | ✅ Yes (permanent) | ❌ No (temporary) |
| **Use for** | Document lines | Reports, search results |

```yaml
# Persistent data (saved to database) - at processor level
tabular_sections:
  - name: DocumentLines
    columns: [{name: Product, type: string}]

# Temporary data (in-memory only) - inside form!
forms:
  - name: Форма
    value_tables:
      - name: SearchResults
        columns: [{name: Result, type: string}]
```

**Rule:** If it's a report/calculation/search → **ValueTable**

---

## 🎯 Common Patterns

### Pattern 1: Master-Detail Table
```yaml
forms:
  - name: Форма
    default: true
    elements:
      - type: Table
        name: MasterTable
        events:
          OnActivateRow: MasterTableOnActivateRow  # Auto-loads detail
      - type: Table
        name: DetailTable
```

**Handlers:**
- `MasterTableOnActivateRow.bsl` (client) - gets selected row
- `MasterTableOnActivateRowНаСервере.bsl` (server) - loads detail data

### Pattern 2: Command with Server Call
```yaml
forms:
  - name: Форма
    default: true
    commands:
      - name: LoadData
        title_ru: Загрузить данные
        picture: StdPicture.Refresh
```

**Handlers:**
- `LoadData.bsl` (client) - calls server
- `LoadDataНаСервере.bsl` (server) - does actual work

### Pattern 3: Web Request Pattern
```yaml
attributes:
  - {name: URL, type: string}
  - {name: ResponseText, type: string}

forms:
  - name: Форма
    default: true
    value_tables:
      - name: Results
        columns: [{name: Title, type: string}]
```

**Handler:** Use `HTTPСоединение` + `HTTPЗапрос` in BSL

---

## 🔧 Data Types Reference

```yaml
# Simple types
type: string              # Необмежена строка (unlimited, length=0)
type: string, length: 100 # Обмежена строка (limited to 100)
type: number              # Число(15,2)
type: date                # Дата
type: boolean             # Булево

# References (1C objects)
type: CatalogRef.Products
type: DocumentRef.Orders
```

---

## 🎨 UI Elements Quick Reference

```yaml
forms:
  - name: Форма
    default: true
    elements:
      # Input field
      - type: InputField
        name: MyField
        attribute: TextField  # Links to attribute

      # Button
      - type: Button
        name: MyButton
        command: ExecuteCommand  # Links to command

      # Table (TabularSection or ValueTable)
      - type: Table
        name: MyTable
        tabular_section: Lines  # OR value_table: Results

      # Group (container)
      - type: UsualGroup
        name: MyGroup
        title_ru: Группа
        child_items: [...]  # Nested elements

      # Label
      - type: LabelDecoration
        name: MyLabel
        title_ru: "Введите данные:"
```

---

## 🐛 Most Frequent Errors

### Error 1: Ukrainian Cyrillic (10 min lost)
```
❌ Атрибут 'ПошуковийЗапіт': містить неприпустимі символи
```
**Fix:** Replace `і→и`, `ї→й`, `є→е`, `ґ→г` everywhere (YAML + BSL files)

### Error 2: Invalid StdPicture (3 min lost)
```
❌ Команда 'Save': Невідома стандартна картинка: StdPicture.CheckMark
```
**Fix:** Use [VALID_PICTURES.md](VALID_PICTURES.md) → `StdPicture.Write`

### Error 3: Handler File Mismatch (7 min lost)
```
❌ Відсутній обробник: handlers/ЗагрузитиДанные.bsl
```
**Fix:** Rename files to EXACTLY match YAML names (including НаСервере suffix!)

### Error 4: BSL Reserved Keyword
```
❌ Команда 'Выполнить': зарезервоване ключове слово BSL
```
**Fix:** Add suffix → `ВыполнитьКоманду`, `ВыполнитьДействие`

---

## 📁 Directory Structure

```
my-project/
├── processors/           # ⚠️ Create processors in this subfolder!
│   └── MyProcessor/      # ← One folder per processor
│       ├── config.yaml   # ← Main configuration
│       └── handlers.bsl  # ← BSL business logic (single file)
└── tmp/                  # ← Generated output
    └── MyProcessor/
        ├── MyProcessor.xml
        ├── Forms/
        │   └── Форма/
        │       ├── Форма.xml
        │       └── Ext/
        │           └── Form/
        │               └── Module.bsl
        └── Ext/
            └── ObjectModule.bsl
```

---

## 📚 Full Documentation

- **[LLM_PROMPT.md](LLM_PROMPT.md)** - Comprehensive guide with all patterns
- **[YAML_GUIDE.md](YAML_GUIDE.md)** - Complete YAML API reference
- **[VALID_PICTURES.md](VALID_PICTURES.md)** - All 130+ valid StdPicture names
- **[UI_PATTERNS.md](UI_PATTERNS.md)** - Copy-paste UI patterns library
- **[README.md](README.md)** - Installation and quick start

---

## 💡 Pro Tips

1. **Always check Cyrillic first** - Use `python -c "print('і' == 'и')"` → False!
2. **Start with minimal example** - Add complexity incrementally
3. **Use VALID_PICTURES.md** - Don't guess StdPicture names
4. **Test in 1C early** - Generate and load .epf after each feature
5. **Follow naming:** `HandlerНаСервере.bsl`, not `HandlerServer.bsl`

---

## 🆘 Getting Help

```bash
# Generate minimal example (default version 2.11)
python -m 1c_processor_generator minimal TestProcessor

# Generate for older platform (version 2.10)
python -m 1c_processor_generator minimal TestProcessor 2.10

# Generate for newer platform (version 2.18)
python -m 1c_processor_generator minimal TestProcessor 2.18

# Generate full example with table
python -m 1c_processor_generator example

# Validate without generating
# (coming soon: --validate-only flag)
```

**Validation errors?** Check:
1. ⚠️ Cyrillic alphabet (Russian only!)
2. 📄 StdPicture name in VALID_PICTURES.md
3. 🔑 Handler name not in BSL keywords
4. 📁 Handler file exists and matches YAML name

---

**Last updated:** 2026-01-03 | **Version:** 2.69.0
**Generated by:** 1C Processor Generator
