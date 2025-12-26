# LLM Sync Guide: Bidirectional YAML↔XML Synchronization

**For:** LLM agents assisting with 1C processor development
**Version:** v2.42.0+ (Handler Architecture & Full Property Mapping)
**Last Updated:** 2025-11-26

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Comment Preservation (v2.30.0)](#comment-preservation-v230)
4. [Complete Workflow](#complete-workflow)
5. [LLM Instructions](#llm-instructions)
6. [Practical Examples](#practical-examples)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [CLI Reference](#cli-reference)

---

## Overview

### What is Sync Tool?

The **Sync Tool** enables bidirectional synchronization between source files (YAML + BSL) and modified EPF/XML files from 1C Configurator. This allows developers to:

1. Generate EPF from YAML+BSL source
2. Make quick edits in 1C Configurator (UI tool)
3. Export modified XML from Configurator
4. Sync changes back to source files

**Key Problem Solved:** Manual XML editing is error-prone. Configurator provides GUI but changes are lost. Sync tool bridges this gap.

### Why Comment Preservation Matters (v2.30.0)

**Before v2.30.0:**
```yaml
attributes:
  # ВАЖНО: Это поле обязательное для отчета
  - name: ReportDate
    type: date
```

After sync → Comments lost:
```yaml
attributes:
  - name: ReportDate
    type: date  # Modified in Configurator
```

**After v2.30.0:**
```yaml
attributes:
  # ВАЖНО: Это поле обязательное для отчета
  - name: ReportDate
    type: date  # Modified in Configurator, comment preserved!
```

---

## Quick Start

### Minimal Workflow (3 Steps)

```bash
# Step 1: Generate EPF with snapshot
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output-format epf

# Step 2: Edit in 1C Configurator (manual)
# - Open EPF in Configurator
# - Make changes (rename fields, fix code, adjust UI)
# - Export to XML: File → Save As → XML (exports full directory)
#   Example exported structure:
#     modified_export/
#     ├── MyProc.xml          ← Use this path below
#     ├── Ext/ObjectModule.bsl
#     └── Forms/Форма/...

# Step 3: Sync changes back
python -m 1c_processor_generator sync \
  --modified-xml modified_export/MyProc.xml \
  --config config.yaml \
  --handlers handlers.bsl
```

**Result:** YAML and BSL files updated with Configurator changes, comments preserved.

**Note:** `--modified-xml` expects path to the **main processor XML file** in the exported directory (e.g., `MyProc.xml`), not the directory itself.

---

## Comment Preservation (v2.30.0)

### How It Works

The sync tool uses **ruamel.yaml** with custom helpers to preserve:
- **Inline comments:** `key: value  # comment`
- **End-of-line comments:** `- name: Field  # important field`
- **Block comments:** Multi-line comments before sections
- **Formatting:** Indentation, spacing, key ordering

### What Gets Preserved

✅ **Comments:**
```yaml
# This is a block comment
attributes:
  - name: Product  # This inline comment is preserved
    type: string
    length: 100  # Max length for product names
```

✅ **Formatting:**
```yaml
forms:
  - name: Форма
    elements:
      - type: InputField  # Spacing preserved
        name: ProductField
```

✅ **Ordering:**
```yaml
# Order of keys preserved even after sync
processor:
  name: MyProcessor
  synonym_ru: Мой процессор
  platform_version: "2.11"
```

### Automatic (Zero Configuration)

Comment preservation is **automatic** in v2.30.0+. No YAML config needed:

```yaml
# Your comments here - automatically preserved!
processor:
  name: DataImporter
```

No special flags, no configuration section. Just works.

---

## Complete Workflow

### Step-by-Step Process

#### Step 1: Initial Generation with Snapshot

```bash
python -m 1c_processor_generator yaml \
  --config processors/MyProc/config.yaml \
  --handlers-file processors/MyProc/handlers.bsl \
  --output processors/MyProc/output \
  --output-format epf
```

**What Happens:**
1. Generates EPF file: `output/MyProc.epf`
2. Creates snapshot directory: `output/_snapshot/`
   - `original.xml` - Generated XML before compilation
   - `original_handlers.bsl` - All BSL code
3. Snapshot used as baseline for future sync

**Important:** Always use `--output-format epf` to create snapshot. XML-only generation doesn't create snapshots.

#### Step 2: Edit in 1C Configurator

**Open Configurator:**
1. Launch 1C:Enterprise Configurator
2. Open your configuration
3. Find External Data Processor: Tools → External Data Processors
4. Open your EPF file

**Make Changes:**
- Rename fields (e.g., `Tovar` → `Product`)
- Change types (e.g., `string` → `number`)
- Modify BSL procedures (fix bugs, add logic)
- Adjust UI layout (move fields, change titles)
- Add/delete form elements ✅ (v2.26.0+)

**Export to XML (Full Directory Structure):**
1. File → Save Configuration As... (or right-click processor → Export)
2. Choose "XML files" format
3. Select directory: `processors/MyProc/modified_export/`
4. Configurator exports **entire directory structure** (not just one XML file)

**Exported Structure:**
```
modified_export/
├── MyProc.xml                    # ← Main processor XML (use this path in --modified-xml)
├── Ext/
│   ├── ObjectModule.bsl          # Object module BSL code
│   └── ManagerModule.bsl         # Manager module (if exists)
├── Forms/
│   └── Форма/
│       ├── Форма.xml             # Form metadata
│       └── Ext/
│           ├── Form.xml          # Form structure and elements
│           └── Form/
│               └── Module.bsl    # Form module BSL code
└── ... (other objects if any)
```

**Important:** Configurator exports the same structure as `--output-format xml` generates. You'll use the main XML file path in sync command.

#### Step 3: Sync Changes Back

```bash
python -m 1c_processor_generator sync \
  --modified-xml processors/MyProc/modified_export/MyProc.xml \
  --config processors/MyProc/config.yaml \
  --handlers processors/MyProc/handlers.bsl
```

**How Sync Analyzes All Changes:**

Even though you specify only the main XML file, sync tool **automatically discovers and analyzes ALL files** in the exported directory:

1. **Main Processor XML** (`MyProc.xml`)
   - Processor metadata (name, version, synonyms)
   - Attributes definitions
   - Tabular sections
   - Commands definitions

2. **Form Structure XML** (`Forms/Форма/Ext/Form.xml`)
   - Form elements (InputField, Table, Button, etc.)
   - Element properties (width, title, tooltip)
   - Element hierarchy (groups, pages, nesting)

3. **Object Module BSL** (`Ext/ObjectModule.bsl`)
   - Exported procedures for commands
   - Helper functions

4. **Form Module BSL** (`Forms/Форма/Ext/Form/Module.bsl`)
   - Event handlers (OnOpen, OnCreateAtServer, etc.)
   - Command handlers (button clicks)
   - Element event handlers (OnActivateRow, etc.)

**Comparison Process:**
- Compares modified files with snapshot (`_snapshot/original.xml`, `_snapshot/original_handlers.bsl`)
- Detects changes in XML structure (XMLDiffer)
- Detects changes in BSL code (BSLDiffer)
- Shows **all differences** in interactive mode

**Interactive Approval:**
```
🔍 Detected 5 changes:

1. [RENAME] Attribute 'Tovar' → 'Product'
   Apply this change? [y/n/a/s/d/q] (y=yes, n=no, a=all, s=skip all, d=detailed, q=quit): y

2. [MODIFY] Attribute 'Product' property 'type': string → number
   Apply this change? [y/n/a/s/d/q]: y

3. [BSL_CHANGE] Procedure 'CalculateНаСервере' modified
   Apply this change? [y/n/a/s/d/q]: d  # Show detailed diff

   --- Original
   +++ Modified
   @@ -1,3 +1,5 @@
    &НаСервере
    Процедура CalculateНаСервере()
   -    Объект.Result = Объект.Number1 + Объект.Number2;
   +    // Fixed: Added validation
   +    Если Объект.Number1 > 0 И Объект.Number2 > 0 Тогда
   +        Объект.Result = Объект.Number1 + Объект.Number2;
   +    КонецЕсли;
    КонецПроцедуры

   Apply this change? [y/n/a/s/d/q]: y

4. [MODIFY] Form element 'ProductField' property 'width': 200 → 300
   Apply this change? [y/n/a/s/d/q]: y

5. [ADD] Form element 'DiscountField' (InputField)
   Apply this change? [y/n/a/s/d/q]: y

✅ Applied 5/5 changes
💾 Backup created: processors/MyProc/config.yaml.backup_20251120_143022
✅ YAML updated: processors/MyProc/config.yaml
✅ BSL updated: processors/MyProc/handlers.bsl
```

**Options Explained:**
- `y` (yes) - Apply this change
- `n` (no) - Skip this change
- `a` (all) - Apply all remaining changes without asking
- `s` (skip all) - Skip all remaining changes
- `d` (detailed) - Show detailed diff (for BSL/YAML changes)
- `p` (preview) - Preview mode, show changes without applying
- `q` (quit) - Abort sync (no changes applied)

#### Step 4: Verify Results

```bash
# Check git diff to see what changed
git diff config.yaml handlers.bsl

# Verify comments preserved
cat config.yaml | grep "#"

# Regenerate to test
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output-format epf
```

---

## LLM Instructions

### When User Requests Sync

**Scenario:** User says "I edited the processor in Configurator, sync it back"

**Your Response Pattern:**

```markdown
I'll sync the changes from Configurator back to your source files.

First, I need to locate the exported XML directory. Configurator exports a full
directory structure (like --output-format xml), not a single file.

Let me check:
- Config: [path/to/config.yaml]
- Handlers: [path/to/handlers.bsl]
- Exported directory: [path/to/modified_export/]
- Main XML file: [path/to/modified_export/ProcessorName.xml]

Running sync command...
```

**Command Template:**
```bash
python -m 1c_processor_generator sync \
  --modified-xml {exported_dir}/ProcessorName.xml \
  --config {path_to_config_yaml} \
  --handlers {path_to_handlers_bsl}
```

**Important for LLMs:**
- User exports **full directory** from Configurator (not single XML)
- You must specify path to **main processor XML file** (e.g., `MyProc.xml`) in that directory
- Sync tool **automatically discovers and analyzes ALL files** in exported directory:
  - Main processor XML (attributes, tabular sections, commands)
  - Form XML (form structure, elements, properties)
  - Object Module BSL (command procedures, helpers)
  - Form Module BSL (event handlers, command handlers)
- Comparison is comprehensive: XML structure (XMLDiffer) + BSL code (BSLDiffer)
- If user says "I exported to `modified_export/`", construct path: `modified_export/ProcessorName.xml`

### LLM-Friendly Mode (Automated)

For fully automated sync without interactive prompts:

```bash
python -m 1c_processor_generator sync \
  --modified-xml modified.xml \
  --config config.yaml \
  --handlers handlers.bsl \
  --llm-mode
```

**Output (JSON format):**
```json
{
  "status": "success",
  "changes_detected": 5,
  "changes_applied": 5,
  "backup_path": "config.yaml.backup_20251120_143022",
  "sections_updated": ["attributes", "form_elements", "handlers"],
  "details": [
    {
      "type": "rename",
      "category": "attribute",
      "old_name": "Tovar",
      "new_name": "Product"
    },
    {
      "type": "modify",
      "category": "attribute",
      "name": "Product",
      "property": "type",
      "old_value": "string",
      "new_value": "number"
    }
  ]
}
```

**Use `--llm-mode` when:**
- User wants automatic sync (no prompts)
- You need structured output for parsing
- Running in CI/CD pipeline
- Batch processing multiple processors

### Handling Errors

**If sync fails:**

```python
# Error: Snapshot not found
✗ Error: Snapshot directory not found at 'output/_snapshot/'
Solution: Regenerate EPF with --output-format epf to create snapshot

# Error: XML parse error
✗ Error: Failed to parse modified XML
Solution: Check XML file is valid export from Configurator

# Error: Conflict detected
✗ Error: Conflicting changes detected in attribute 'Product'
Solution: Use interactive mode to review conflicts
```

**Your Response:**
```markdown
The sync failed because [reason]. Let me fix this:

1. [Solution step 1]
2. [Solution step 2]

Retrying sync...
```

---

## Practical Examples

### Example 1: Rename Field in Configurator

**Initial YAML:**
```yaml
attributes:
  # Назва товару (обов'язкове поле)
  - name: Tovar
    type: string
    synonym_ru: Товар
```

**User Action in Configurator:**
- Renamed `Tovar` → `Product`
- Changed title to "Product"
- Exported to directory: `modified_export/`

**Exported Structure:**
```
modified_export/
├── MyProc.xml          ← Main XML file
├── Ext/
│   └── ObjectModule.bsl
└── Forms/Форма/...
```

**Sync Command:**
```bash
python -m 1c_processor_generator sync \
  --modified-xml modified_export/MyProc.xml \
  --config config.yaml \
  --handlers handlers.bsl
```

**Result YAML:**
```yaml
attributes:
  # Назва товару (обов'язкове поле)  ← Comment preserved!
  - name: Product  # ← Name updated
    type: string
    synonym_ru: Товар
```

### Example 2: Fix BSL Bug in Configurator

**Initial BSL (`handlers.bsl`):**
```bsl
// CalculateНаСервере
Объект.Result = Объект.Number1 + Объект.Number2;
```

**User Action in Configurator:**
- Added validation before calculation
- Fixed potential division by zero

**Modified BSL in Configurator:**
```bsl
// CalculateНаСервере
Если Объект.Number1 > 0 И Объект.Number2 > 0 Тогда
    Объект.Result = Объект.Number1 + Объект.Number2;
Иначе
    Сообщить("Ошибка: числа должны быть больше 0");
КонецЕсли;
```

**Sync Result:**
- `handlers.bsl` updated with new validation code
- Procedure header comment preserved
- Helper functions untouched

### Example 3: Change Multiple Properties

**Initial YAML:**
```yaml
forms:
  - name: Форма
    elements:
      # Основное поле ввода
      - type: InputField
        name: ProductField
        width: 200
        title_ru: Товар
```

**Changes in Configurator:**
1. Width: 200 → 300
2. Title: "Товар" → "Продукт"
3. Added tooltip: "Введите название продукта"

**Sync Output:**
```
🔍 Detected 3 changes in form element 'ProductField':
1. Property 'width': 200 → 300
2. Property 'title_ru': 'Товар' → 'Продукт'
3. Property 'tooltip_ru': None → 'Введите название продукта'

Apply all 3 changes? [y/n/a/s/d/q]: a
```

**Result YAML:**
```yaml
forms:
  - name: Форма
    elements:
      # Основное поле ввода  ← Comment preserved!
      - type: InputField
        name: ProductField
        width: 300  # ← Updated
        title_ru: Продукт  # ← Updated
        tooltip_ru: Введите название продукта  # ← Added
```

### Example 4: Add New Form Element (v2.26.0+)

**Initial YAML:**
```yaml
forms:
  - name: Форма
    elements:
      - type: InputField
        name: ProductField
        attribute: Product
```

**User Action in Configurator:**
- Added new field "Discount" (InputField)
- Placed below ProductField

**Sync Output:**
```
🔍 Detected 1 structural change:

[ADD] Form element 'DiscountField' (InputField)
  - Position: After 'ProductField'
  - Attribute: Discount
  - Title: "Скидка"

⚠️  Warning: Adding element requires creating attribute 'Discount'
   Create attribute automatically? [y/n]: y

✅ Created attribute 'Discount' (type: number, digits: 15, fraction: 2)
✅ Added form element 'DiscountField'
```

**Result YAML:**
```yaml
attributes:
  - name: Product
    type: string
  - name: Discount  # ← Auto-created
    type: number
    digits: 15
    fraction_digits: 2

forms:
  - name: Форма
    elements:
      - type: InputField
        name: ProductField
        attribute: Product
      - type: InputField  # ← Added
        name: DiscountField
        attribute: Discount
        title_ru: Скидка
```

---

## Best Practices

### For LLMs

**DO:**
1. ✅ Always check for snapshot before suggesting sync
2. ✅ Verify XML file path exists before running sync
3. ✅ Use `--llm-mode` for automated workflows
4. ✅ Show user what changes will be applied before sync
5. ✅ Suggest reviewing git diff after sync
6. ✅ Recommend testing regeneration after sync

**DON'T:**
1. ❌ Don't sync without snapshot (regenerate EPF first)
2. ❌ Don't auto-approve destructive changes (deletions)
3. ❌ Don't skip validation after sync
4. ❌ Don't sync if user made manual YAML edits (conflicts!)
5. ❌ Don't forget to backup config before sync

### For Users (Explain These)

**Workflow Best Practices:**

1. **Always Generate with EPF Format:**
   ```bash
   # ✅ Good: Creates snapshot
   --output-format epf

   # ❌ Bad: No snapshot, sync won't work
   --output-format xml
   ```

2. **Use Version Control:**
   ```bash
   # Before sync
   git add config.yaml handlers.bsl
   git commit -m "Before Configurator edits"

   # After sync
   git diff  # Review changes
   git commit -m "Synced changes from Configurator"
   ```

3. **Test After Sync:**
   ```bash
   # Always regenerate to verify
   python -m 1c_processor_generator yaml \
     --config config.yaml \
     --handlers-file handlers.bsl \
     --output-format epf
   ```

4. **Keep Comments Meaningful:**
   ```yaml
   # ✅ Good: Explains WHY
   attributes:
     # Required for tax calculation (ФЗ-54)
     - name: TaxRate

   # ❌ Bad: States obvious
   attributes:
     # This is TaxRate attribute
     - name: TaxRate
   ```

### Comment Guidelines

**Good Comments (Preserved by Sync):**

```yaml
processor:
  # v2.5.0: Added support for multiple currencies
  name: CurrencyConverter

attributes:
  # ВАЖНО: Используется в отчете по ЗУП
  - name: EmployeeID
    type: string

  # TODO: Migrate to Catalog.Currencies in v3.0
  - name: CurrencyCode
    type: string
    length: 3  # ISO 4217 format

forms:
  - name: Форма
    commands:
      # 🔥 Hot path: Called on every row change
      - name: Calculate
        handler: CalculateКнопка
```

**Comments to Avoid:**

```yaml
# ❌ Redundant
attributes:
  # This is an attribute
  - name: Product

# ❌ Outdated (will confuse after sync)
attributes:
  # Type: string (100 chars max)
  - name: Product
    type: number  # Oops, comment outdated!

# ❌ Implementation details (use BSL comments)
commands:
  # This calls CalculateНаСервере with parameters Number1, Number2
  - name: Calculate  # Too detailed, put in BSL
```

---

## Troubleshooting

### Problem 1: "Snapshot not found"

**Error:**
```
✗ Error: Snapshot directory not found at 'output/_snapshot/'
Cannot perform sync without baseline snapshot.
```

**Solution:**
```bash
# Regenerate EPF to create snapshot
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output output \
  --output-format epf

# Now sync will work
python -m 1c_processor_generator sync \
  --modified-xml modified.xml \
  --config config.yaml \
  --handlers handlers.bsl
```

### Problem 2: "Comments Lost After Sync"

**Symptom:** Comments disappeared after sync.

**Cause:** Using version < 2.30.0

**Solution:**
```bash
# Check version
python -m 1c_processor_generator --version

# If < 2.30.0, upgrade:
pip install --upgrade 1c-processor-generator

# Restore comments from git
git restore config.yaml

# Re-run sync with v2.30.0+
```

### Problem 3: "Conflicting Changes Detected"

**Error:**
```
⚠️  Warning: Conflicting changes detected:
- Attribute 'Product' modified in both Configurator and source YAML
```

**Solution:**
```bash
# Check what changed in source
git diff config.yaml

# Option 1: Keep Configurator changes
# - Commit/stash local YAML changes first
git stash
python -m 1c_processor_generator sync ...

# Option 2: Keep source changes
# - Skip sync, regenerate EPF from source
python -m 1c_processor_generator yaml --output-format epf

# Option 3: Manual merge
# - Use detailed diff mode in sync
# - Selectively apply changes with y/n/d options
```

### Problem 4: "XML Parse Error"

**Error:**
```
✗ Error: Failed to parse XML: not well-formed (invalid token)
```

**Causes & Solutions:**

1. **Incomplete Export from Configurator:**
   - Export again, ensure "Full configuration" is selected
   - Don't export just selected objects
   - Verify exported directory contains: ProcessorName.xml + Ext/ + Forms/

2. **Corrupted XML File:**
   - Check file size (should be > 50KB for typical processor)
   - Open in text editor, verify `<?xml version="1.0"?>` header
   - Check if Configurator export completed successfully

3. **Wrong File Path:**
   - Verify path points to **main XML file**: `--modified-xml modified_export/MyProc.xml`
   - NOT directory: `--modified-xml modified_export/` ❌
   - NOT other XML: `--modified-xml modified_export/Forms/Форма/Форма.xml` ❌
   - Use absolute path if relative fails
   - Check file exists: `ls -la modified_export/MyProc.xml`

### Problem 5: "BSL Changes Not Applied"

**Symptom:** BSL procedure changes from Configurator not synced to handlers.bsl.

**Debugging:**

```bash
# Run sync with verbose output
python -m 1c_processor_generator sync \
  --modified-xml modified.xml \
  --config config.yaml \
  --handlers handlers.bsl \
  --verbose

# Check snapshot BSL
cat output/_snapshot/original_handlers.bsl | grep "ПроцедураName"

# Manually compare
diff output/_snapshot/original_handlers.bsl handlers.bsl
```

**Common Causes:**
- Procedure name mismatch (case-sensitive)
- Helper function not in snapshot (added after generation)
- Syntax error in modified BSL

---

## CLI Reference

### Sync Command

```bash
python -m 1c_processor_generator sync [OPTIONS]
```

**Required Options:**
```
--modified-xml PATH      Path to main processor XML file in exported directory
                        (Configurator exports full directory structure, specify
                        the main XML file: exported_dir/ProcessorName.xml)
--config PATH           Path to source config.yaml
--handlers PATH         Path to source handlers.bsl (or directory)
```

**Optional Flags:**
```
--llm-mode              Enable LLM-friendly mode (JSON output, auto-approve)
--verbose               Show detailed logging
--no-backup             Skip creating .backup files (not recommended)
--force                 Skip conflict detection, force apply changes
```

**Examples:**

```bash
# Interactive sync (default)
# Configurator exported to: modified_export/
# Directory contains: MyProc.xml, Ext/, Forms/, etc.
python -m 1c_processor_generator sync \
  --modified-xml modified_export/MyProc.xml \
  --config config.yaml \
  --handlers handlers.bsl

# Automated sync for LLMs
python -m 1c_processor_generator sync \
  --modified-xml modified_export/MyProc.xml \
  --config config.yaml \
  --handlers handlers.bsl \
  --llm-mode

# Verbose output for debugging
python -m 1c_processor_generator sync \
  --modified-xml modified_export/MyProc.xml \
  --config config.yaml \
  --handlers handlers.bsl \
  --verbose
```

**Important:**
- Configurator exports **full directory** (MyProc.xml + Ext/ + Forms/ + ...)
- `--modified-xml` expects path to **main XML file** (e.g., `modified_export/MyProc.xml`)
- Sync tool **automatically discovers and analyzes ALL files** in directory:
  - Main processor XML → XMLDiffer → Detects metadata changes
  - Form XML files → XMLDiffer → Detects form structure changes
  - BSL modules (Object, Form) → BSLDiffer → Detects code changes
- Shows comprehensive diff covering ALL detected changes

### Generation Command (with Snapshot)

```bash
python -m 1c_processor_generator yaml \
  --config PATH \
  --handlers-file PATH \
  --output PATH \
  --output-format epf  # ← Creates snapshot
```

**Snapshot Location:**
```
output/
├── MyProc.epf
└── _snapshot/
    ├── original.xml              # Generated XML before compilation
    └── original_handlers.bsl     # All BSL code
```

---

## Version History

### v2.42.0 (2025-11-26) - Handler Architecture & Full Property Mapping
- ✅ **Handler Registry Pattern** - Extensible architecture with 9 element handlers
- ✅ **Template Sync** - HTMLDocument, SpreadsheetDocument (v2.40.0+)
- ✅ **FormParameter Sync** - Form parameters with key_parameter, synonym (v2.36.0+)
- ✅ **Full Property Mapping:**
  - Font properties (bold, italic, size, face_name)
  - Alignment (horizontal_align, vertical_align)
  - Choice properties (choice_mode, quick_choice, choice_history_on_input)
  - InputField (multiline, password_mode, text_edit, auto_max_width/height)
  - Visual (picture, picture_size, zoomable, hyperlink)
  - Group (group_direction, representation, show_title, behavior)
- ✅ **38 new handler tests** (100% passing)

### v2.30.0 (2025-11-20) - Comment & Formatting Preservation
- ✅ Full comment preservation during sync
- ✅ YAML formatting preservation (indentation, spacing, ordering)
- ✅ 100% backward compatible (zero API changes)

### v2.28.0 (2025-11-20) - Nested Elements & Advanced Diff
- ✅ Hierarchical tree extraction for nested elements
- ✅ Advanced conflict resolution with detailed diff
- ✅ Professional visualization (side-by-side diff)

### v2.27.0 (2025-11-19) - ValueTable & FormAttribute Support
- ✅ ValueTable column sync (add/delete)
- ✅ FormAttribute support (SpreadsheetDocument, BinaryData)

### v2.26.0 (2025-11-19) - Structural Changes
- ✅ Add/delete operations for elements, attributes, commands
- ✅ Conflict resolution UI with granular control
- ✅ YAMLPatcher for safe YAML modifications

### v2.25.0 (2025-01-19) - Initial Sync Tool
- ✅ Bidirectional YAML↔XML synchronization
- ✅ Snapshot system for baseline comparison
- ✅ Change detection (rename, modify, type changes)

---

## Summary for LLMs

**Key Takeaways:**

1. **Always use `--output-format epf`** to create snapshot (required for sync)
2. **v2.30.0+ preserves comments automatically** (no configuration needed)
3. **Configurator exports FULL DIRECTORY** (ProcessorName.xml + Ext/ + Forms/)
4. **--modified-xml expects MAIN XML FILE path** (e.g., `modified_export/MyProc.xml`)
5. **Sync analyzes ALL files automatically** (XML + BSL, comprehensive diff)
6. **Interactive mode is default** (use `--llm-mode` for automation)
7. **Verify after sync** (regenerate EPF, check git diff)
8. **Comments are valuable** (encourage meaningful comments)

**Workflow Checklist:**
- [ ] Generate EPF with `--output-format epf`
- [ ] User edits in Configurator
- [ ] User exports to directory (full structure: XML + BSL + Forms)
- [ ] Locate main XML file in exported directory
- [ ] Run sync command with path to main XML file
- [ ] Review changes in interactive mode
- [ ] Verify with git diff
- [ ] Test regeneration

**When User Says:** "I edited in Configurator"
**You Should:**
1. Ask: "Did you export the processor to XML?"
2. Ask: "What directory did you export to?"
3. Locate main XML file: `{export_dir}/{ProcessorName}.xml`
4. Run sync command with correct path

**When User Says:** "Comments were lost"
**You Should:** Check version (must be v2.30.0+), upgrade if needed.

**When User Says:** "Sync command fails - file not found"
**You Should:**
1. Verify they exported FULL DIRECTORY from Configurator
2. Check they're pointing to main XML file, not directory
3. Use `ls` to verify file exists

---

## Additional Resources

- **CHANGELOG.md** - Full version history with detailed changes
- **SYNC_ROADMAP.md** - Future sync tool features and roadmap
- **LLM_PROMPT.md** - Main LLM guide for processor generation
- **TROUBLESHOOTING.md** - Comprehensive troubleshooting guide

---

**Last Updated:** 2025-11-26
**Applies To:** v2.42.0 and later
**Tested On:** 1C:Enterprise 8.3.25.1394
