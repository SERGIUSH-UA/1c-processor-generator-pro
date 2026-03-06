---
name: 1c-processor-generator
description: >
  Generate 1C:Enterprise 8.3 external data processors (.epf) from YAML config and BSL handlers.
  Use when asked to create 1C processors, EPF files, obrabotki, or generate YAML+BSL for
  1C:Enterprise. Triggers: "1C processor", "EPF", "обработка", "обробка", "external data processor",
  "YAML config for 1C", "BSL handler", "1c-processor-generator", "create 1C form".
metadata:
  author: SERGIUSH-UA
  version: 2.76.0
  category: development
  tags: [1c-enterprise, code-generation, epf, bsl]
evaluations:
  triggers:
    should_trigger:
      - "Create a 1C processor for invoice generation"
      - "Generate YAML config and BSL handlers for a report form"
      - "Help me build an EPF file for data import"
      - "I need a 1C external data processor with a table and filters"
    should_not_trigger:
      - "Write a Python script for data analysis"
      - "Create a React component for a dashboard"
      - "Help me with Excel formulas"
      - "Write SQL queries for PostgreSQL"
  functional:
    - prompt: "Create a calculator processor with two number fields and Add/Subtract buttons"
      expected: "Valid config.yaml with Number attributes, commands with non-reserved handler names, handlers.bsl with math logic"
    - prompt: "Create a sales report with date filters and a results table"
      expected: "config.yaml with date attributes, ValueTable in value_tables, OnCreateAtServer event, handlers.bsl with server query"
    - prompt: "Create a processor with Save and Delete buttons with icons"
      expected: "StdPicture.SaveFile (not Save), StdPicture.Delete - valid StdPicture names only"
---

# 1C Processor Generator

## What This Skill Does

This skill generates 1C:Enterprise 8.3 external data processors (.epf files) from declarative YAML configurations and BSL (Built-in Scripting Language) handlers.

**Your role as an LLM:** Generate two files:
- `config.yaml` - processor structure (attributes, forms, UI elements, commands)
- `handlers.bsl` - business logic (event handlers, calculations, server queries)

The generator handles all technical complexity: UUID generation, sequential ID numbering, XML structure, client-server pairing, and metadata. You focus on business logic and UI design.

**Output:** Valid 1C XML files or compiled .epf binary, ready to open in 1C:Enterprise.

## Quick Workflow

**Step 1:** Analyze user requirements. Decide on data model and UI pattern.

**Step 2:** Generate `config.yaml` (YAML structure) and `handlers.bsl` (BSL business logic).

**Step 3:** User runs the generator:
```bash
# Generate XML (always works, free)
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output output_dir

# Generate EPF (requires PRO license + 1C Designer)
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output output_dir \
  --output-format epf

# Generate EPF via cloud (PRO license, no local Designer needed)
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output output_dir \
  --output-format epf \
  --cloud
```

## YAML Structure Essentials

```yaml
processor:
  name: МояОбработка              # Internal name (Russian Cyrillic or Latin)
  synonym_ru: Моя обработка       # Display name Russian
  synonym_uk: Моя обробка         # Display name Ukrainian

attributes:                       # Processor-level data (persistent)
  - name: Поле1
    type: string
    length: 100

forms:
  - name: Форма
    default: true
    # value_tables, form_attributes, commands, events - ALL go INSIDE form
    value_tables:                  # Temporary tables (not saved)
      - name: Результаты
        columns:
          - name: Колонка1
            type: string
    events:
      OnCreateAtServer: ПриСозданииНаСервере
    elements:                     # UI elements
      - type: InputField
        name: Поле1Поле
        attribute: Поле1
      - type: Button
        name: ВыполнитьКнопка
        command: Выполнить
    commands:
      - name: Выполнить
        title_ru: Выполнить
        handler: ВыполнитьОбработку    # NOT "Выполнить" - reserved!
        picture: StdPicture.ExecuteTask
```

## Data Types

| Type | YAML | Notes |
|------|------|-------|
| String | `type: string, length: 100` | `length: 0` or omit = unlimited |
| Number | `type: number, digits: 15, fraction_digits: 2` | |
| Boolean | `type: boolean` | |
| Date | `type: date` | |
| CatalogRef | `type: CatalogRef.Контрагенты` | Reference to catalog |
| DocumentRef | `type: DocumentRef.Заказ` | Reference to document |
| SpreadsheetDoc | `type: spreadsheet_document` | MUST use `form_attributes:` |

**Persistent data** (`attributes:`) - saved with processor, access via `Объект.Name`.
**Temporary data** (`form_attributes:`) - form-level only, access via `Name` (no `Объект.` prefix). Required for `spreadsheet_document`, `binary_data`.

## Form Elements

| Element | Key Properties |
|---------|---------------|
| `InputField` | `attribute`, `width`, `multiline`, `height`, `read_only`, `choice_list`, `events` |
| `Table` | `tabular_section`, `is_value_table: true`, `height`, `columns`, `events` |
| `Button` | `command`, `width`, `representation`, `default_button` |
| `LabelDecoration` | `title`, `font: {bold, size}`, `hyperlink`, `horizontal_align` |
| `LabelField` | `attribute`, `data_path`, `hyperlink` |
| `UsualGroup` | `child_items`, `group_direction: Horizontal/Vertical`, `representation` |
| `Pages` | `pages: [{name, title, child_items}]`, `pages_representation` |
| `CheckBoxField` | `attribute`, `title_location` |
| `RadioButtonField` | `attribute`, `choice_list`, `radio_button_type: Tumbler` |
| `SpreadSheetDocumentField` | `attribute` (form_attribute), `events: {DetailProcessing}` |
| `HTMLDocumentField` | `attribute` (form_attribute, type: string) |
| `PictureDecoration` | `svg_source` or `picture: StdPicture.Name` |
| `ColumnGroup` | `elements`, `group_layout`, `show_in_header` |
| `ButtonGroup` | `elements` (Button children) |

**Units:** `width` = character units, `height` = row units (NOT pixels).

## BSL Handlers Format

Put ALL handlers in one `handlers.bsl` file (single-file approach, recommended):

```bsl
// Command handler - client calls server
&НаКлиенте
Процедура ВыполнитьОбработку(Команда)
    ВыполнитьОбработкуНаСервере();
КонецПроцедуры

&НаСервере
Процедура ВыполнитьОбработкуНаСервере()
    // Database queries, calculations here
    Объект.Результат = Объект.Число1 + Объект.Число2;
КонецПроцедуры

// Form event handler
&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
    // Initialize form data
КонецПроцедуры

// Table event - master-detail pattern
&НаКлиенте
Процедура ТаблицаПриАктивизацииСтроки(Элемент)
    ОбновитьДеталиНаСервере();
КонецПроцедуры
```

**Client-server pattern:** Client procedure calls server with `НаСервере` suffix.
**Access patterns:** Processor attributes via `Объект.AttrName`, ValueTable via `TableName`, form elements via `Элементы.ElemName`.

**ObjectModule region** (v2.66.0+): Write ObjectModule code directly in handlers.bsl:
```bsl
#Область МодульОбъекта
Функция СведенияОВнешнейОбработке() Экспорт
    // Goes to ObjectModule.bsl
КонецФункции
#КонецОбласти
```

## Critical Rules (MUST READ)

### Rule 1: Russian Cyrillic ONLY in Identifiers

**Forbidden:** Ukrainian letters `і ї є ґ І Ї Є Ґ` in processor/attribute/command/handler **names**.

1C validates identifiers with regex: `^[а-яА-ЯёЁa-zA-Z_][а-яА-ЯёЁa-zA-Z0-9_]*$`

Ukrainian `і` (U+0456) != Russian `и` (U+0438) - looks identical but causes compilation errors.

```yaml
# User says: "Створи обробку для пошукового запиту"
processor:
  name: ПоисковыйЗапрос       # Russian (и, not і)
  synonym_uk: "Пошуковий запит" # Ukrainian OK in synonyms
```

**Mental model:** Identifiers = machine names (strict Russian), synonyms = human names (any language).

### Rule 2: NO BSL Reserved Keywords as Handler Names

**Full list (73 keywords):**
```
Выполнить, Экспорт, Импорт, Процедура, Функция, КонецПроцедуры, КонецФункции,
Прервать, Продолжить, Возврат, Если, Тогда, ИначеЕсли, Иначе, КонецЕсли,
Для, По, Пока, Цикл, КонецЦикла, Каждого, Из, Попытка, Исключение,
ВызватьИсключение, КонецПопытки, Новый, Перем, Знач, И, Или, Не,
Истина, Ложь, Неопределено, NULL, Найти
```

**Fix pattern:** Add context noun. `Выполнить` -> `ВыполнитьОбработку`, `Экспорт` -> `ЭкспортироватьДанные`.

See `references/cheatsheet.md` for the complete list.

### Rule 3: Valid StdPicture Names Only

Common valid names: `ExecuteTask`, `SaveFile`, `OpenFile`, `Refresh`, `Delete`, `CreateListItem`, `Change`, `InputFieldClear`, `GenerateReport`, `Check`, `Write`.

Common mistakes: `StdPicture.Save` (wrong) -> `StdPicture.SaveFile` (correct). `StdPicture.CheckMark` (wrong) -> `StdPicture.Check` (correct).

When unsure, **omit picture** rather than guessing. Full list: `references/valid-pictures.md`.

### Rule 4: ValueTable vs TabularSection

| Feature | TabularSection | ValueTable |
|---------|----------------|------------|
| Saved to DB? | Yes (persistent) | No (temporary) |
| YAML section | `tabular_sections:` | `value_tables:` (inside form) |
| Use for | Document lines, persistent data | Reports, search results, calculations |
| Table element | default | requires `is_value_table: true` |

See `references/data-guide.md` for detailed decision framework.

### Rule 5: forms: Section Placement

When using `forms:` array, ALL of these MUST be INSIDE the form definition:
- `value_tables`, `form_attributes`, `dynamic_lists`, `commands`, `events`

Root-level definitions are IGNORED when `forms:` section exists.

## Three Core Patterns

### Pattern 1: Simple Form
Input fields + action buttons. Use for: data entry, settings, calculators.

```yaml
processor:
  name: Калькулятор
  synonym_ru: Калькулятор
attributes:
  - name: Число1
    type: number
    digits: 15
    fraction_digits: 2
  - name: Результат
    type: number
    digits: 15
    fraction_digits: 2
forms:
  - name: Форма
    default: true
    elements:
      - type: InputField
        name: Число1Поле
        attribute: Число1
      - type: InputField
        name: РезультатПоле
        attribute: Результат
        read_only: true
      - type: Button
        name: РассчитатьКнопка
        command: Рассчитать
    commands:
      - name: Рассчитать
        title_ru: Рассчитать
        handler: РассчитатьОбработку
```

```bsl
&НаКлиенте
Процедура РассчитатьОбработку(Команда)
    РассчитатьНаСервере();
КонецПроцедуры

&НаСервере
Процедура РассчитатьНаСервере()
    Объект.Результат = Объект.Число1 * 2;
КонецПроцедуры
```

Full example: `assets/example-simple-form/`

### Pattern 2: Report with Table
Filter fields + results table. Use for: reports, data display, search results.

```yaml
processor:
  name: ОтчетПродажи
  synonym_ru: Отчет по продажам
attributes:
  - name: НачалоПериода
    type: date
  - name: КонецПериода
    type: date
forms:
  - name: Форма
    default: true
    value_tables:
      - name: Результаты
        columns:
          - name: Товар
            type: string
            length: 150
          - name: Сумма
            type: number
            digits: 15
            fraction_digits: 2
    elements:
      - type: UsualGroup
        name: Фильтры
        group_direction: Horizontal
        child_items:
          - type: InputField
            name: НачалоПоле
            attribute: НачалоПериода
          - type: InputField
            name: КонецПоле
            attribute: КонецПериода
          - type: Button
            name: СформироватьКнопка
            command: Сформировать
      - type: Table
        name: РезультатыТаблица
        tabular_section: Результаты
        is_value_table: true
        height: 15
        horizontal_stretch: true
    commands:
      - name: Сформировать
        title_ru: Сформировать
        handler: СформироватьОтчет
```

Full example: `assets/example-report-table/`

### Pattern 3: Master-Detail
Two linked tables - selecting a row in master updates detail. Use for: parent-child relationships.

```yaml
forms:
  - name: Форма
    default: true
    value_tables:
      - name: Роли
        columns:
          - name: Наименование
            type: string
            length: 150
      - name: Пользователи
        columns:
          - name: Логин
            type: string
            length: 100
    events:
      OnCreateAtServer: ПриСозданииНаСервере
    elements:
      - type: UsualGroup
        name: Главная
        group_direction: Horizontal
        child_items:
          - type: Table
            name: РолиТаблица
            tabular_section: Роли
            is_value_table: true
            width: 40
            events:
              OnActivateRow: РолиПриАктивизацииСтроки
          - type: Table
            name: ПользователиТаблица
            tabular_section: Пользователи
            is_value_table: true
            horizontal_stretch: true
```

Key: `OnActivateRow` event on master table triggers server call to update detail table.

Full example: `assets/example-master-detail/`

## CLI Commands

```bash
# Generate XML (free, always works)
python -m 1c_processor_generator yaml \
  --config config.yaml --handlers-file handlers.bsl --output output_dir

# Generate EPF (PRO license + local 1C Designer)
python -m 1c_processor_generator yaml \
  --config config.yaml --handlers-file handlers.bsl --output output_dir --output-format epf

# Generate EPF via cloud (PRO license, no local Designer)
python -m 1c_processor_generator yaml \
  --config config.yaml --handlers-file handlers.bsl --output output_dir --output-format epf --cloud

# Check license status
python -m 1c_processor_generator license-status

# Request 7-day trial
python -m 1c_processor_generator trial

# Feature discovery
python -m 1c_processor_generator features --search "table"
```

**Rules:** Always use `--output`. Never copy files after generation. Parameter order: `yaml` -> `--config` -> `--handlers-file` -> `--output` -> `--output-format`.

See `references/cli-guide.md` for complete CLI reference.

## Thinking Framework

Before generating code, reason through these 5 steps:

1. **ANALYZE** - What is the user's functional goal? What data do they need?
2. **DECIDE** - Persistent or temporary data? Which UI pattern (Simple Form / Report+Table / Master-Detail / Wizard)?
3. **VALIDATE** - Scan identifiers for Ukrainian letters. Check handler names against reserved keywords. Verify StdPicture names.
4. **GENERATE** - Write config.yaml first (structure), then handlers.bsl (logic). Use client-server pairs for DB operations.
5. **EXPLAIN** - Tell user what was generated, how to run the generator, and any design decisions made.

## When to Load References

Load additional reference files based on the task at hand:

| Task | Reference to load |
|------|-------------------|
| UI design, layout | `references/patterns-essential.md`, `references/all-patterns.md` |
| Data model decisions | `references/data-guide.md` |
| Complete YAML API | `references/api-reference.md` |
| Element styling, colors, fonts | `references/styling-guide.md` |
| HTML/CSS/JS interfaces | `references/html-guide.md` |
| Testing workflow | `references/testing-workflow.md` |
| Sync tool (bidirectional YAML/XML) | `references/sync-guide.md` |
| CLI details, license | `references/cli-guide.md` |
| Errors and debugging | `references/troubleshooting.md` |
| Icons / pictures | `references/valid-pictures.md` |
| Excel templates | `references/excel-templates.md` |
| BSP print forms | `references/bsp-print-forms.md` |
| Advanced (DynamicList, BackgroundJobs, Testing) | `references/advanced-features.md` |
| Quick cheatsheet | `references/quick-reference.md` |
| Common mistakes | `references/cheatsheet.md` |
| Feature lookup | `scripts/feature_lookup.py` or `references/feature-registry.json` |

## Pre-Generation Checklist

Before outputting config.yaml and handlers.bsl, verify:

1. All `name:` fields use Russian Cyrillic only (no Ukrainian i/yi/ye/g)
2. All handler names are NOT BSL reserved keywords
3. All `attribute:` values exist in `attributes:` or `form_attributes:`
4. All `tabular_section:` values exist in `value_tables:` or `tabular_sections:`
5. All `command:` values on buttons exist in `commands:`
6. ValueTables have `is_value_table: true` on their Table element
7. Server procedures have `&НаСервере` directive
8. One form has `default: true`
