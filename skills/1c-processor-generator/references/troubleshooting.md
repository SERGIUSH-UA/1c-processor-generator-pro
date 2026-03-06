# Troubleshooting Guide

**Target:** LLMs and developers debugging 1C processor generation issues
**Core guide:** [LLM_CORE.md](../LLM_CORE.md)

---

## 🚨 Most Common Errors

### Error 1: Ukrainian Cyrillic in Identifiers

**Symptom:**
```
XML validation error: Invalid character in identifier
```

**Cause:** Ukrainian letters (і, ї, є, ґ) in processor/attribute/command names

**Example:**
```yaml
❌ WRONG:
attributes:
  - name: ПошуковийЗапит  # Contains Ukrainian 'і'
```

**Fix:**
```yaml
✅ CORRECT:
attributes:
  - name: ПоисковыйЗапрос  # Russian 'и' instead
  synonym_uk: "Пошуковий запит"  # Ukrainian allowed in synonyms
```

**See also:** [LLM_CORE.md](../LLM_CORE.md) Rule 1

---

### Error 2: BSL Reserved Keyword in Handler Name

**Symptom:**
```
BSL parse error: Expected identifier, found keyword 'Выполнить'
```

**Cause:** Handler name is a BSL reserved keyword

**Example:**
```yaml
❌ WRONG:
commands:
  - name: Execute
    handler: Выполнить  # Reserved keyword
```

**Fix:**
```yaml
✅ CORRECT:
commands:
  - name: Execute
    handler: ВыполнитьОбработку  # Add context
```

**See also:** [LLM_CORE.md](../LLM_CORE.md) Rule 2

---

### Error 3: Invalid StdPicture Name

**Symptom:**
```
Warning: StdPicture.CheckMark not found
```

**Cause:** Picture name doesn't exist in 1C platform

**Example:**
```yaml
❌ WRONG:
commands:
  - name: Save
    picture: StdPicture.CheckMark  # Doesn't exist
```

**Fix:**
```yaml
✅ CORRECT:
commands:
  - name: Save
    picture: StdPicture.Check  # Exists

# OR omit picture (optional)
commands:
  - name: Save
    # No picture specified
```

**See also:** [VALID_PICTURES.md](../VALID_PICTURES.md)

---

### Error 4: Handler File Not Found

**Symptom:**
```
FileNotFoundError: handlers/LoadData.bsl not found
```

**Cause:** Mismatch between YAML handler name and BSL file name

**Example:**
```yaml
commands:
  - name: LoadData
    handler: LoadDataНаСервере  # ← File must be: LoadDataНаСервере.bsl
```

**File structure:**
```
❌ WRONG:
handlers/
  LoadData.bsl  # File name doesn't match

✅ CORRECT:
handlers/
  LoadDataНаСервере.bsl  # Matches handler name exactly
```

**See also:** [LLM_CORE.md](../LLM_CORE.md) Rule 4

---

### Error 5: `is_dynamic_list` at Wrong Level

**Symptom:**
```
YAML validation error: Unknown field 'is_dynamic_list' at Table level
```

**Cause:** `is_dynamic_list: true` at wrong YAML level

**Example:**
```yaml
❌ WRONG:
- type: Table
  name: MyTable
  tabular_section: MyList
  is_dynamic_list: true  # ❌ Top level
```

**Fix:**
```yaml
✅ CORRECT:
- type: Table
  name: MyTable
  tabular_section: MyList
  properties:           # ✅ Under properties
    is_dynamic_list: true
```

**See also:** [ALL_PATTERNS.md](ALL_PATTERNS.md) Pattern 3 (DynamicList)

---

### Error 6: ValueTable Accessed with `Объект.` Prefix

**Symptom:**
```
BSL runtime error: Property 'Results' not found on object
```

**Cause:** ValueTable accessed via `Объект.Results` instead of direct `Results`

**Example:**
```bsl
❌ WRONG:
НоваяСтрока = Объект.Results.Add();  # ValueTable is NOT on Объект
```

**Fix:**
```bsl
✅ CORRECT:
НоваяСтрока = Results.Add();  # Direct access (form attribute)
```

**Rule:**
- TabularSection: `Объект.TableName` (object-level)
- ValueTable: `TableName` (form-level)

**See also:** [LLM_DATA_GUIDE.md](../LLM_DATA_GUIDE.md)

---

### Error 7: CLI Options Before Subcommand

**Symptom:**
```
error: unrecognized arguments: yaml --config config.yaml
```

**Cause:** Flags placed before subcommand name

**Example:**
```bash
❌ WRONG:
python -m 1c_processor_generator --output-format epf yaml --config config.yaml
```

**Fix:**
```bash
✅ CORRECT:
python -m 1c_processor_generator yaml --config config.yaml --output-format epf
```

**Rule:** Options come AFTER subcommand (standard CLI pattern)

**See also:** [LLM_CORE.md](../LLM_CORE.md) Rule 5

---

### Error 8: Root-Level Definitions with forms: Section

**Symptom in 1C Designer:**
```
Файл - ...Form.xml: Неверный путь к данным: 'DataTable'
Файл - ...Form.xml: Неверный путь к данным: 'Объект.PreviewHTML'
```
Or: Handlers don't work (no events fire), commands don't appear.

**Cause:** When using `forms:` section, the following must be INSIDE each form definition:
- `form_attributes`
- `value_tables`
- `dynamic_lists`
- `commands`
- `events` (NOT in `form:` section)

The generator ignores root-level definitions when `forms:` section exists.

**Example:**
```yaml
❌ WRONG (all root-level definitions will be ignored):
processor:
  name: MyProcessor

# ROOT LEVEL - ALL WILL BE IGNORED when using forms: section!
form_attributes:
  - name: PreviewHTML
    type: spreadsheet_document

commands:
  - name: Execute
    title: "Выполнить | Виконати"
    handler: ВыполнитьОбработку

form:
  events:
    OnOpen: ПриОткрытии  # ❌ IGNORED!

forms:
  - name: Form
    default: true
    elements:
      - type: SpreadSheetDocumentField
        name: PreviewField
        attribute: PreviewHTML  # ERROR: attribute not found!
```

**Fix:**
```yaml
languages: [ru, uk]

✅ CORRECT:
processor:
  name: MyProcessor

forms:
  - name: Form
    default: true
    # ALL INSIDE FORM - CORRECT!
    events:
      OnOpen: ПриОткрытии
    form_attributes:
      - name: PreviewHTML
        type: spreadsheet_document
    commands:
      - name: Execute
        title: "Выполнить | Виконати"
        handler: ВыполнитьОбработку
    elements:
      - type: SpreadSheetDocumentField
        name: PreviewField
        attribute: PreviewHTML  # OK - attribute exists
```

**Note:** The generator now shows a warning when this mistake is detected:
```
⚠️ YAML WARNING: Misplaced definitions will be IGNORED!
⚠️ Found at root level: form_attributes (PreviewHTML), commands (Execute), form: {events (OnOpen)}
```

**See also:** [LLM_CORE.md](../LLM_CORE.md) Error Type 5

---

### Error 9: HTMLDocumentField Missing form_attribute (v2.39.0+)

**Symptom:**
```
Неверный путь к данным: 'HTMLContent'
```
Or HTML field shows nothing / attribute not found error.

**Cause:** HTMLDocument attribute defined at root level instead of inside form definition, or forgot to create form_attribute.

**Example:**
```yaml
❌ WRONG:
# Missing form_attribute entirely
elements:
  - type: HTMLDocumentField
    name: PreviewField
    attribute: HTMLContent  # Attribute doesn't exist!

❌ WRONG:
# form_attribute at root level (ignored when using forms:)
form_attributes:
  - name: HTMLContent
    type: string              # Also wrong location!

forms:
  - name: Форма
    elements:
      - type: HTMLDocumentField
        attribute: HTMLContent  # Won't find it!
```

**Fix:**
```yaml
✅ CORRECT:
forms:
  - name: Форма
    form_attributes:
      - name: HTMLContent
        type: string           # ← string for HTML, inside form definition
    elements:
      - type: HTMLDocumentField
        name: PreviewField
        attribute: HTMLContent  # ✅ Now finds it
```

**BSL usage:**
```bsl
// HTMLDocumentField прив'язаний до form_attribute через DataPath
// Просто присвоюємо значення атрибуту форми:
HTMLContent = "<html><body>Hello</body></html>";

// Or load from template (v2.40.0+)
HTMLContent = Обработки.ProcessorName.ПолучитьМакет("EmailTemplate").ПолучитьТекст();
```

**See also:** [API_REFERENCE.md](API_REFERENCE.md) HTMLDocumentField section

---

### Error 10: Template File Not Found (v2.40.0+)

**Symptom:**
```
Template file not found: templates/email.html
```
Or parser returns None.

**Cause:** Template file path doesn't exist or path is wrong.

**Example:**
```yaml
❌ WRONG:
templates:
  - name: EmailTemplate
    type: HTMLDocument
    file: email.html  # File doesn't exist at this path
```

**Fix:**
```yaml
✅ CORRECT:
# 1. Create the file relative to config.yaml
# If config.yaml is in /project/config.yaml
# Then file should be at /project/templates/email.html

templates:
  - name: EmailTemplate
    type: HTMLDocument
    file: templates/email.html  # ← Relative to config.yaml location
```

**Directory structure:**
```
project/
├── config.yaml
├── handlers.bsl
└── templates/
    └── email.html    # ← Template file here
```

**Supported template types:**
- `HTMLDocument` - .html files (text, UTF-8)
- `SpreadsheetDocument` - .mxl files (binary)

**See also:** [API_REFERENCE.md](API_REFERENCE.md) Templates section

---

## 🔍 Validation Errors

### Validation Error 1: Empty Handler (CheckConfig)

**Symptom:**
```
CheckConfig warning: Handler 'LoadData' is empty
```

**Cause:** BSL file exists but contains no code

**Example:**
```bsl
// handlers/LoadData.bsl
// Empty file or only comments
```

**Fix:**
```bsl
// handlers/LoadData.bsl
Объект.Result = "Data loaded";
Сообщить("Done!");
```

**Note:** CheckConfig validation (v2.12.0+) detects semantic issues

---

### Validation Error 2: Unreferenced Procedure

**Symptom:**
```
CheckConfig warning: Procedure 'HelperFunction' is not referenced
```

**Cause:** Procedure defined but never called (dead code)

**Fix:**
1. **Use it:** Call from another handler
2. **Remove it:** Delete if not needed
3. **Suppress:** Set `check_config_enabled: false` if intentional

---

### Validation Error 3: Missing Form/Command Reference

**Symptom:**
```
CheckConfig error: Command 'LoadData' referenced but not found
```

**Cause:** YAML references command that doesn't exist

**Example:**
```yaml
elements:
  - type: Button
    command: LoadData  # ← Command doesn't exist
```

**Fix:**
```yaml
# Add command definition
commands:
  - name: LoadData
    title: "Загрузить"
    handler: LoadData
```

---

## ⚡ Performance Issues

### Issue 1: Slow Form Load (Large TabularSection)

**Symptom:** Form takes 5-10 seconds to open

**Cause:** TabularSection with 1000+ rows loaded from database

**Fix:** Use ValueTable + load on demand
```yaml
# ❌ Slow - loads all rows at form open
tabular_sections:
  - name: Results  # Loads from DB

# ✅ Fast - load only when needed
forms:
  - name: Форма
    value_tables:
      - name: Results  # Empty until loaded
```

---

### Issue 2: Slow Report Generation

**Symptom:** Report button freezes UI for 30+ seconds

**Cause:** Heavy query running on client

**Fix:** Move to server handler
```bsl
❌ WRONG (client):
&НаКлиенте
Процедура Generate(Команда)
    Запрос = Новый Запрос;  # ❌ Client can't run queries efficiently
    ...
КонецПроцедуры

✅ CORRECT (server):
&НаКлиенте
Процедура Generate(Команда)
    GenerateНаСервере();  # ✅ Calls server
КонецПроцедуры

&НаСервере
Процедура GenerateНаСервере()
    Запрос = Новый Запрос;  # ✅ Server runs query
    ...
КонецПроцедуры
```

---

## 🐛 Runtime Errors

### Runtime Error 1: Undefined Row Access

**Symptom:**
```
BSL runtime error: Cannot read property 'ID' of undefined
```

**Cause:** Accessing `ТекущиеДанные` without checking for `Неопределено`

**Fix:**
```bsl
❌ WRONG:
ТекущаяСтрока = Элементы.Table.ТекущиеДанные;
ID = ТекущаяСтрока.ID;  # ❌ May be Неопределено

✅ CORRECT:
ТекущаяСтрока = Элементы.Table.ТекущиеДанные;

Если ТекущаяСтрока = Неопределено Тогда
    Возврат;  # ✅ Safe exit
КонецЕсли;

ID = ТекущаяСтрока.ID;  # ✅ Safe access
```

---

### Runtime Error 2: File Path Errors (Windows)

**Symptom:**
```
File operation error: Invalid path 'C:UsersMeDocuments...'
```

**Cause:** Backslashes not escaped in BSL strings

**Fix:**
```bsl
❌ WRONG:
FilePath = "C:\Users\Me\Documents\file.txt";  # ❌ Backslashes interpreted

✅ CORRECT:
FilePath = "C:\Users\Me\Documents\file.txt";  # ✅ Escaped backslashes

# OR use forward slashes
FilePath = "C:/Users/Me/Documents/file.txt";  # ✅ Works in 1C
```

---

### Runtime Error 3: Date Comparison Type Mismatch

**Symptom:**
```
Type mismatch: Cannot compare Date and Undefined
```

**Cause:** Comparing date attribute before it's filled

**Fix:**
```bsl
❌ WRONG:
Если Объект.EndDate < Объект.StartDate Тогда  # ❌ May be Неопределено
    ...
КонецЕсли;

✅ CORRECT:
Если ЗначениеЗаполнено(Объект.StartDate)
    И ЗначениеЗаполнено(Объект.EndDate)
    И Объект.EndDate < Объект.StartDate Тогда  # ✅ Safe comparison
    ...
КонецЕсли;
```

---

## 📦 Compilation Errors

### Compilation Error 1: XDTO Exception (v2.11.0 fix)

**Symptom:**
```
XDTO error: Unexpected prefix 'cfg:' for ExternalDataProcessorObject
```

**Cause:** Incorrect namespace prefix in generated XML (fixed in v2.11.1+)

**Fix:** Upgrade to v2.11.1+ or manually remove `cfg:` prefix from XML

---

### Compilation Error 2: BSL Syntax Error

**Symptom:**
```
CheckModules error: Expected 'КонецПроцедуры', found 'EndProcedure'
```

**Cause:** Mixed Russian/English keywords

**Fix:** Use consistent Russian keywords
```bsl
❌ WRONG:
Procedure Test()  # English
    ...
КонецПроцедуры    # Russian

✅ CORRECT:
Процедура Test()  # Russian
    ...
КонецПроцедуры    # Russian
```

---

## 🔧 Configuration Issues

### Issue 1: Designer Not Found (EPF generation)

**Symptom:**
```
Error: 1C Designer not found in standard locations
```

**Cause:** Auto-detection failed (non-standard install path)

**Fix:** Specify explicit path
```bash
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output-format epf \
  --designer-path "D:/1C/8.3.25/bin/1cv8.exe"
```

---

### Issue 2: Validation Fails in Configuration Mode

**Symptom:**
```
CheckModules error: Catalog 'Products' not found
```

**Cause:** Using CatalogRef without metadata in configuration

**Fix:** This is expected — Configuration mode creates minimal metadata

**Options:**
1. Ignore validation errors: `--ignore-validation-errors`
2. Use full database for testing (not temp_ib)

---

## 🎯 Edge Cases

### Edge Case 1: SpreadsheetDocument Attribute Location

**Issue:** SpreadsheetDocument must be form attribute, not processor attribute (v2.15.1 fix)

```yaml
❌ WRONG (v2.15.0):
attributes:  # ❌ Processor-level
  - name: Report
    type: spreadsheet_document

✅ CORRECT (v2.15.1+):
forms:
  - name: Форма
    form_attributes:  # ✅ Form-level
      - name: Report
        type: spreadsheet_document
```

---

### Edge Case 2: DynamicList UseAlways Without Table

**Issue:** `use_always_fields` specified but no Table element on form

**Symptom:**
```
Warning: UseAlways fields removed - no Table element found
```

**Fix:** Add Table element
```yaml
dynamic_lists:
  - name: MyList
    use_always_fields: [Ref, Field1]

elements:
  - type: Table  # ✅ Required for UseAlways
    name: MyListTable
    tabular_section: MyList
    properties:
      is_dynamic_list: true
```

---

### Edge Case 3: Multilingual Values Empty String

**Issue:** Empty strings in multilingual synonym/title

**Symptom:** Field displays with no label

**Fix:** Provide all language values
```yaml
❌ WRONG:
synonym:
  ru: ""  # Empty
  uk: "Товар"

✅ CORRECT:
synonym:
  ru: "Товар"
  uk: "Товар"
  en: "Product"
```

---

## 📚 Debugging Checklist

**When generation fails, check:**

1. ✅ All identifiers use Russian Cyrillic (no Ukrainian і/ї/є/ґ)
2. ✅ Handler names not BSL reserved keywords
3. ✅ Handler file names match YAML handler names exactly
4. ✅ StdPicture names valid (or omitted)
5. ✅ CLI options come AFTER subcommand name
6. ✅ `is_dynamic_list` under `properties:` (not top-level)
7. ✅ ValueTable accessed directly (not `Объект.ValueTable`)

**When runtime fails, check:**
8. ✅ `ТекущиеДанные` checked for `Неопределено`
9. ✅ Date fields validated before comparison
10. ✅ File paths use escaped backslashes or forward slashes
11. ✅ Client-server split correct (queries on server)
12. ✅ Large datasets use ValueTable (not TabularSection)

---

**Last updated:** 2025-11-16
**Generator version:** 2.22.0+
