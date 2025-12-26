# Quick Reference - 1C Processor Generator

**1-page cheatsheet for LLMs**

---

## Form Elements

| Element | YAML | Required | Optional |
|---------|------|----------|----------|
| **InputField** | `type: InputField`<br>`attribute: AttrName`<br>`read_only: true` | name, attribute | events, choice_list, input_hint_ru/uk/en, width, height, multiline, horizontal_stretch, title_location, read_only, **title_text_color, text_color, back_color, border_color, title_font, font** (v2.43.0+) |
| **RadioButtonField** (v2.2) | `type: RadioButtonField`<br>`attribute: AttrName`<br>`choice_list: []`<br>`radio_button_type: Tumbler` | name, attribute, choice_list | radio_button_type, title_location, events |
| **CheckBoxField** (v2.2) | `type: CheckBoxField`<br>`attribute: AttrName` | name, attribute | width, title_location, events |
| **LabelField** | `type: LabelField`<br>`attribute: AttrName` | name | attribute, data_path, hyperlink, events |
| **LabelDecoration** | `type: LabelDecoration`<br>`title: "Text"`<br>`font: { bold: true }` | name, title | font, hyperlink, horizontal_align, vertical_align, events |
| **Table** | `type: Table`<br>`tabular_section: TableName`<br>`read_only: true` | name, tabular_section | is_value_table, is_dynamic_list (under properties!), events, read_only, height, horizontal_stretch |
| **SpreadSheetDocumentField** (v2.15.0) | `type: SpreadSheetDocumentField`<br>`attribute: ReportField` | name, attribute | title_location, vertical_scrollbar, horizontal_scrollbar, show_grid, show_headers, edit, protection, events (DetailProcessing) |
| **Button** | `type: Button`<br>`command: CommandName` | name, command | width, representation |
| **UsualGroup** | `type: UsualGroup`<br>`child_items: []`<br>`read_only: true` | name, child_items | title, show_title, group_direction, behavior, read_only |
| **ColumnGroup** (v2.37.0) | `type: ColumnGroup`<br>`elements: []`<br>`group_layout: Horizontal` | name, elements | title_ru/uk/en, tooltip_ru/uk/en, group_layout, show_in_header, horizontal_align, vertical_align |
| **Pages** | `type: Pages`<br>`pages: []` | name, pages | pages_representation |

---

## Visual Properties - Units of Measurement ⚠️

**CRITICAL: 1C forms use conditional units (NOT pixels!)**

| Property | Element Type | Units | Description | Example Values |
|----------|--------------|-------|-------------|----------------|
| `width` | InputField, Button | **character units** | Approximate number of visible characters | 10-40 (InputField), 10-20 (Button) |
| `width` | Table Column | **character units** | Column width in characters | 5-40 (text), 8-15 (numbers) |
| `svg_width` | PictureDecoration (SVG) | **pixels** | PNG output width (v2.23.1+) | 100-500 |
| `svg_height` | PictureDecoration (SVG) | **pixels** | PNG output height (v2.23.1+) | 50-200 |
| `form_width` | PictureDecoration | **character units** | Form display width (v2.23.1+) | 10-50 |
| `form_height` | PictureDecoration | **row units** | Form display height (v2.23.1+) | 5-20 |
| `height` | Table | **row units** | Number of visible rows without scrolling | 5-15 |
| `height` | InputField (multiline) | **row units** | Number of visible text lines | 3-10 |
| `horizontal_stretch` | Table, InputField | **boolean** | Stretch element to fill horizontal space | true, false |

**Important Notes:**
- **Form elements** (InputField, Button, Table, Column): width = **character units**, height = **row units**
- **Actual pixel size** depends on: font size, DPI, interface scale (50-400%)
- **Platform auto-converts** conditional units → pixels at runtime
- **PictureDecoration (v2.23.1+):** Separate sizing for PNG generation and form display!
  - `svg_width`/`svg_height` - PNG output in **pixels** (high quality)
  - `form_width`/`form_height` - Form display in **character/row units** (optional)
  - **Backward compatible:** Old `width`/`height` → automatically map to `svg_width`/`svg_height`

**Examples:**
```yaml
# InputField with sizing
- type: InputField
  width: 30              # 30 characters wide (NOT 30 pixels!)
  multiline: true
  height: 5              # 5 visible text lines (NOT 5 pixels!)

# Table with sizing
- type: Table
  height: 12             # 12 visible rows (NOT 12 pixels!)
  horizontal_stretch: true  # Stretch to fill horizontal space
  columns:
    - name: ProductName
      width: 30          # 30 characters wide (NOT 30 pixels!)

# PictureDecoration (SVG) - NEW in v2.23.1!
- type: PictureDecoration
  svg_source: logo.svg
  svg_width: 200         # PNG output: 200x80 pixels (high quality)
  svg_height: 80
  form_width: 25         # Form display: 25 characters wide
  form_height: 10        # Form display: 10 rows tall
  picture_size: Proportionally
```

---

## InputField Styling (v2.43.0+)

**Color and font customization for InputField elements:**

```yaml
- type: InputField
  name: StyledField
  attribute: Description

  # Colors (HEX format only - #RRGGBB)
  title_text_color: "#616EFF"  # Title label color
  text_color: "#330910"        # Input text color
  back_color: "#F0FFF0"        # Background color
  border_color: "#DB6C1F"      # Border color

  # Title font
  title_font:
    ref: "style:LargeTextFont"
    bold: true
    italic: true

  # Field text font
  font:
    ref: "style:ExtraLargeTextFont"
    faceName: "Arial"          # Custom font family
    height: 10
    scale: 102                 # 102% scale
```

**Font Reference Options:**
| Reference | Description |
|-----------|-------------|
| `style:NormalTextFont` | Standard form text (default) |
| `style:LargeTextFont` | Large text |
| `style:SmallTextFont` | Small captions |
| `style:ExtraLargeTextFont` | Extra large titles |
| `sys:DefaultGUIFont` | System GUI font |

**Font Properties:**
- `ref` - Base font reference (required)
- `faceName` - Font family name (Arial, Tahoma, etc.)
- `height` - Font height in points
- `scale` - Scale percentage (100 = normal)
- `bold`, `italic`, `underline`, `strikethrough` - Style flags

---

## Data Types

| Type | YAML Syntax | Example |
|------|-------------|---------|
| String | `type: string`<br>`length: 100` | Name, Description |
| Number | `type: number`<br>`digits: 15`<br>`fraction_digits: 2` | Amount, Price, Quantity |
| Boolean | `type: boolean` | IsActive, Completed |
| Date | `type: date` | Date, Timestamp |
| CatalogRef | `type: CatalogRef.Name` | CatalogRef.Пользователи |
| DocumentRef | `type: DocumentRef.Name` | DocumentRef.Заказ |
| EnumRef | `type: EnumRef.Name` | EnumRef.Статусы |
| Generic Catalog | `type: CatalogRef` | Any catalog |
| Generic Document | `type: DocumentRef` | Any document |

**Multilingual (v2.13.0+):** Use nested format: `synonym: {ru: "...", uk: "...", en: "..."}` for processor, attributes, columns, commands, form elements (title/tooltip/input_hint).

**Read-Only (v2.13.1+):** Add `read_only: true` to InputField, Table, UsualGroup, or table columns (TabularSection/ValueTable).

**Form Attributes (v2.15.1+):** Use `form_attributes:` for UI-only types (SpreadsheetDocument, BinaryData). They use DataPath **without** `Объект.` prefix.

```yaml
forms:
  - name: Форма
    form_attributes:
      - name: Отчет
        type: spreadsheet_document  # NOT in processor attributes!
```

---

## Form Properties

Control form window behavior and appearance:

| Property | Values | Description | Example |
|----------|--------|-------------|---------|
| `window_opening_mode` | `LockOwnerWindow`, `Independent`, `LockWholeInterface` | How form window opens | `LockOwnerWindow` for modal dialogs |
| `command_bar_location` | `Top`, `Bottom`, `None`, `Auto` | Command bar position | `Bottom` for settings dialogs |
| `auto_title` | `true`, `false` | Auto-generate form title | `false` for custom titles |

**YAML:**
```yaml
forms:
  - name: Настройки
    properties:
      window_opening_mode: LockOwnerWindow  # Modal dialog
      command_bar_location: Bottom
      auto_title: false
      title_ru: "Настройки системы"
      title_uk: "Налаштування системи"
      title_en: "System Settings"
```

**WindowOpeningMode values:**
- `LockOwnerWindow` - Modal dialog (blocks parent window)
- `Independent` - Independent window (doesn't block parent)
- `LockWholeInterface` - Blocks entire interface (rarely used)

---

## Form Events

| Event | Handler Signature | When |
|-------|-------------------|------|
| **OnOpen** | `ПриОткрытии(Отказ)` | Form opens (client) |
| **OnCreateAtServer** | `ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)` | Form created (server) |
| **OnClose** | `ПриЗакрытии(ЗавершениеРаботы)` | Form closes |
| **BeforeClose** | `ПередЗакрытием(...)` | Before close (can cancel) |

**YAML:**
```yaml
forms:
  - name: Форма
    default: true
    events:
      OnOpen: ПриОткрытии
```

**Auto server call:** If `handlers/ПриОткрытииНаСервере.bsl` exists, it's called automatically.

---

## Element Events

| Event | Handler Signature | Applies To |
|-------|-------------------|------------|
| **OnChange** | `ПриИзменении(Элемент)` | InputField |
| **Click** | `Нажатие(Элемент)` | LabelField, Button |
| **StartChoice** | `НачалоВыбора(Элемент, ДанныеВыбора, СтандартнаяОбработка)` | InputField |
| **Clearing** | `Очистка(Элемент, СтандартнаяОбработка)` | InputField |
| **OnActivateRow** | `ПриАктивизацииСтроки(Элемент)` | Table (Client + Server) |
| **Selection** | `Выбор(Элемент, ВыбраннаяСтрока, Поле, СтандартнаяОбработка)` | Table (Client) |
| **OnStartEdit** | `ПриНачалеРедактирования(Элемент, НоваяСтрока, Копирование)` | Table (Client) |

**YAML:**
```yaml
- type: InputField
  name: Field
  attribute: Attr
  events:
    OnChange: FieldПриИзменении

- type: Table
  name: ItemsTable
  tabular_section: Items
  is_value_table: true
  events:
    OnActivateRow: ItemsTableOnActivateRow  # Auto-creates server handler if exists
```

**Table events:** OnActivateRow auto-generates paired server handler if `handlers/HandlerNameНаСервере.bsl` exists.

---

## Commands

```yaml
forms:
  - name: Форма
    default: true
    commands:
      - name: CommandName          # Unique identifier
        title_ru: Заголовок        # Russian title
        title_uk: Заголовок        # Ukrainian title
        handler: HandlerName       # BSL file: handlers/HandlerName.bsl
        tooltip_ru: Подсказка      # Optional tooltip
        tooltip_uk: Підказка
        picture: StdPicture.Name   # Optional icon (StdPicture.* or CommonPicture.*)
        shortcut: F5               # Optional keyboard shortcut
```

**Common shortcuts:**
- `F5` - Refresh/Generate
- `Ctrl+S` - Save
- `Ctrl+N` - New
- `Delete` - Delete

**Common pictures:**
- `StdPicture.ExecuteTask` - Execute/Run
- `StdPicture.SaveFile` - Save/Export
- `StdPicture.OpenFile` - Open/Import
- `StdPicture.Refresh` - Refresh/Reload
- `StdPicture.CustomizeForm` - Settings
- `StdPicture.InputFieldClear` - Clear

**Auto-representation (v2.2.0):** Buttons automatically get `representation: PictureAndText` when command has `picture`. Override with explicit `representation` on button.

**Auto server call:** If `handlers/HandlerNameНаСервере.bsl` exists, it's called from client handler.

---

## Common Patterns

### 1. Simple Form
```yaml
attributes:
  - name: Field1
    type: string
forms:
  - name: Форма
    default: true
    elements:
      - type: InputField
        name: Field1Поле
        attribute: Field1
      - type: Button
        name: OKКнопка
        command: OK
    commands:
      - name: OK
        handler: OK
```

### 2. Table Report
```yaml
attributes:
  - name: StartDate
    type: date
forms:
  - name: Форма
    default: true
    value_tables:
      - name: Results
        columns:
          - {name: Col1, type: string, length: 100}
    elements:
      - type: InputField
        attribute: StartDate
      - type: Button
        command: Generate
      - type: Table
        tabular_section: Results
        is_value_table: true
```

### 3. Wizard
```yaml
forms:
  - name: Форма
    default: true
    elements:
      - type: Pages
        name: Steps
        pages:
          - name: Step1
            title: Шаг 1
            child_items:
              - type: InputField
                attribute: Field1
          - name: Step2
            title: Шаг 2
            child_items:
              - type: Table
                tabular_section: Data
```

### 4. Simple Dynamic List (Database Query)

⚠️ **CRITICAL:** DynamicList requires TWO parts:
1. `dynamic_lists:` section - data source
2. `Table` element with `is_dynamic_list: true` - display

**Simplest variant (auto-query from table):**
```yaml
forms:
  - name: Форма
    default: true
    # 1. Define DynamicList data source (inside form!)
    dynamic_lists:
      - name: СписокДокументов
        title_ru: Список документов
        title_uk: Список документів
        main_table: Document.Заказ  # Automatic query from this table
    # 2. Display with Table element
    elements:
      - type: Table
        name: СписокДокументовТаблица
        tabular_section: СписокДокументов  # ⚠️ References dynamic_lists.name
        properties:
          is_dynamic_list: true  # ⚠️ MUST be under properties:!
```

**With custom query + columns:**
```yaml
forms:
  - name: Форма
    default: true
    dynamic_lists:
      - name: СписокПлатежей
        title_ru: Список платежей
        main_attribute: true
        manual_query: true
        main_table: Document.ПлатежноеПоручение  # Enables DynamicDataRead=true
        query_text: |
          ВЫБРАТЬ
            Док.Ссылка,
            Док.Дата,
            Док.Номер,
            Док.Сумма
          ИЗ Документ.ПлатежноеПоручение КАК Док
        use_always_fields: [Ссылка, Дата]  # ⚠️ WITHOUT prefix in YAML!
        columns:
          - {field: Дата, title_ru: Дата, width: 12}
          - {field: Номер, title_ru: Номер, width: 8}
    elements:
      - type: Table
        tabular_section: СписокПлатежей
        properties:
          is_dynamic_list: true
```

**Key points:**
- **is_dynamic_list** MUST be under `properties:`, not top-level!
- **main_table** → DynamicDataRead=true (live DB connection)
- **No main_table** → DynamicDataRead=false (static query)
- **use_always_fields** - WITHOUT prefix in YAML (generator adds it)

---

### 5. Master-Detail with OnActivateRow
```yaml
forms:
  - name: Форма
    default: true
    value_tables:
      - name: Roles
        columns:
          - {name: RoleName, type: string, length: 100}
      - name: Users
        columns:
          - {name: UserName, type: string, length: 100}
    events:
      OnCreateAtServer: OnCreateAtServer
    elements:
      - type: Table
        name: RolesTable
        tabular_section: Roles
        is_value_table: true
        events:
          OnActivateRow: RolesTableOnActivateRow
      - type: Table
        name: UsersTable
        tabular_section: Users
        is_value_table: true
```

**handlers/RolesTableOnActivateRowНаСервере.bsl:**
```bsl
&НаСервере
Процедура RolesTableOnActivateRowНаСервере(RoleName)
    Users.Clear();
    // Load users by RoleName parameter
    ...
КонецПроцедуры
```

### 6. Group Layout
```yaml
forms:
  - name: Форма
    default: true
    elements:
      - type: UsualGroup
        name: FilterGroup
        title: Filters
        show_title: true
        group_direction: Vertical  # or Horizontal
        child_items:
          - type: InputField
            attribute: Filter1
          - type: InputField
            attribute: Filter2
```

---

## BSL Handler Files

**Structure:**
```
handlers/
├── EventName.bsl                      # Client event
├── EventNameНаСервере.bsl             # Server part (optional)
├── CommandName.bsl                    # Client command
├── CommandNameНаСервере.bsl           # Server part (optional)
├── TableПриАктивизацииСтроки.bsl      # Table event (client)
└── TableПриАктивизацииСтрокиНаСервере.bsl  # Table event (server)
```

**Files can contain:**

**Option 1: Body only** (generator adds signature):
```bsl
Если НЕ ЗначениеЗаполнено(Объект.Number1) Тогда
    Сообщить("Введите число!");
    Возврат;
КонецЕсли;

Объект.Result = Объект.Number1 * 2;
```

**Option 2: Full signature** (used as-is, for custom parameters):
```bsl
&НаСервере
Процедура LoadDataНаСервере(RoleID)
    Data.Clear();

    // Load data based on RoleID parameter
    Query = New Query;
    Query.SetParameter("RoleID", RoleID);
    ...
КонецПроцедуры
```

**Generator auto-detects:** If file starts with `&` or `Процедура`, uses as-is; otherwise wraps.

---

## Module Documentation (v2.14.0+)

**Option 1: Region in handlers.bsl** (simple, 2 files):
```bsl
#Область Документация

// Module documentation here
// Can contain hundreds of lines
//
// Safe code examples:
// Функция GetData()
//     Возврат 123;
// КонецФункции

#КонецОбласті

Процедура ПриОткрытии(Отказ)
    ...
КонецПроцедуры
```

**Option 2: Separate file** (clean, 3 files):
```yaml
forms:
  - name: Форма
    documentation_file: "docs/module_doc.bsl"  # Relative to config.yaml
```

File `docs/module_doc.bsl`:
```bsl
// Documentation content (already with // prefixes)
// Will be placed in #Область Документация
```

**Option 3: Both** (combines both sources):
- File content first, then region content
- Useful for shared docs + form-specific docs

**Result in Module.bsl:**
```bsl
#Область Документация

// Your documentation here

#КонецОбласті

#Область ОбработчикиСобытийФормы
...
```

**Key benefits:**
- Documentation extracted BEFORE procedure parsing (safe for code examples)
- Region markers `#Область/#КонецОбласті` removed automatically
- No parsing conflicts with `Функция...КонецФункции` in comments

---

## Properties & Behaviors

### UsualGroup

| Property | Values | Default | Description |
|----------|--------|---------|-------------|
| group_direction | Vertical, Horizontal | Vertical | Element arrangement direction |
| representation | None, NormalSeparation, WeakSeparation, StrongSeparation | None | Visual separator style around group |
| behavior | Usual, Collapsible | Usual | Makes group collapsible with expand/collapse |
| show_title | true, false | false | Shows group title as header |
| read_only | true, false | false | Makes all child elements read-only recursively |
| title_ru/uk/en | string | - | Multilingual group title (shown if show_title=true) |

### ButtonGroup (v2.15.0+)

Visual container for grouping related buttons.

| Property | Values | Default | Description |
|----------|--------|---------|-------------|
| group_direction | Vertical, Horizontal | Horizontal | Button arrangement direction |
| title_ru/uk/en | string | - | Optional visual separator label |
| elements | Button[] | - | Child buttons (use `elements:` NOT `child_items:`) |

**Note:** ButtonGroup is simpler than UsualGroup - no `representation`, `behavior`, or advanced features.

### Pages

| Property | Values | Default |
|----------|--------|---------|
| pages_representation | TabsOnTop, TabsOnBottom, None | TabsOnTop |

---

## Complete Minimal Example

```yaml
processor:
  name: МояОбробка
  synonym_ru: Моя обработка
  synonym_uk: Моя обробка

attributes:
  - name: Поле1
    type: string
    length: 100

forms:
  - name: Форма
    default: true
    elements:
      - type: InputField
        name: Поле1Поле
        attribute: Поле1
      - type: Button
        name: ВыполнитьКнопка
        command: Выполнить
    commands:
      - name: Выполнить
        title_ru: Выполнить
        title_uk: Виконати
        handler: Выполнить
```

**handlers/Выполнить.bsl:**
```bsl
Сообщить("Поле1 = " + Объект.Поле1);
```

**Generate:**
```bash
python -m 1c_processor_generator yaml \
  --config processors/МояОбробка/config.yaml \
  --handlers-file processors/МояОбробка/handlers.bsl
```

---

## Validation Patterns

```bsl
// Required field
Если НЕ ЗначениеЗаполнено(Объект.Field) Тогда
    Сообщить("Заполните поле!");
    Возврат;
КонецЕсли;

// Date range
Если Объект.EndDate < Объект.StartDate Тогда
    Сообщить("Дата окончания меньше даты начала!");
    Возврат;
КонецЕсли;

// Try-catch
Попытка
    // Risky operation
    DoSomething();
Исключение
    Сообщить("Ошибка: " + ОписаниеОшибки());
КонецПопытки;
```

---

## CurrentData Pattern

**Display data from current table row:**

```yaml
forms:
  - name: Форма
    default: true
    value_tables:
      - name: Products
        columns:
          - {name: Price, type: number}
    elements:
      - type: Table
        name: ProductsTable
        tabular_section: Products
        is_value_table: true
      - type: LabelField
        name: CurrentPriceLabel
        data_path: Items.ProductsTable.CurrentData.Price
```

---

**For full documentation:** See YAML_GUIDE.md, LLM_PROMPT.md

**Version:** 2.46.0 (2025-12-05)
**New in 2.46.0:** Page Element Refactoring - eliminated technical debt, Page now uses FormElement, DRY compliance improvements
**New in 2.43.0:** InputField Styling - colors (title_text_color, text_color, back_color, border_color) and fonts (title_font, font with faceName, scale)
**New in 2.38.0:** Technical Debt Refactoring - architecture modernization (DesignerLogParser, ElementPreparer, IDAllocator, Jinja2 macros)
**New in 2.28.0:** Nested Elements & Advanced Diff - hierarchical tree extraction, unlimited nesting depth for UsualGroup/Pages, advanced conflict resolution UI (detailed diff, side-by-side preview)
**New in 2.27.0:** ValueTable & FormAttribute Support - ValueTable column operations (add/delete), FormAttribute sync, comprehensive test fixes (24 tests)
**New in 2.26.0:** Structural Changes & Conflict Resolution - add/delete operations for 4 element types, YAMLPatcher with reference checking, interactive conflict resolution
**New in 2.15.1:** FormAttribute support - form-only attributes (SpreadsheetDocument, BinaryData) with correct DataPath (no "Объект." prefix), standard command validation
**New in 2.15.0:** SpreadSheetDocumentField, ButtonGroup - formatted reports with drill-down support
**New in 2.13.0:** English language support - trilingual output (ru/uk/en) with *_en fields, auto-defaults, Languages/English.xml generation
**New in 2.12.0:** Семантична перевірка Semantic Validation - deep semantic checks (empty handlers, unreferenced procedures, incorrect references) with YAML configuration
**New in 2.11.1:** BSL Validation through синтаксична перевірка - automatic syntax checking with dual-format log parsing, error classification, and XDTO fixes (cfg: prefix, XML formatting)
**New in 2.11.0:** Major Code Refactoring - EPFCompiler, ConfigurationGenerator, CLI modernized with improved architecture (-529 lines in main files, +821 in focused modules)
**New in 2.10.0:** Automatic CatalogRef/DocumentRef support - intelligent compilation mode selection (Configuration mode for complex types)
**New in 2.8.0:** EPF Direct Generation - compile XML to EPF through Designer (`--output-format epf`)
**New in 2.7.3:** Recursive element processing - infinite nesting depth support
**New in 2.7.2:** Helper functions duplication fix - 36% Module.bsl size reduction
**New in 2.7.1:** Nested UsualGroup support - UsualGroup inside UsualGroup
**New in 2.7.0:** Single file BSL approach - `--handlers-file` (5-10x faster for LLMs), automatic helper detection
**New in 2.6.0:** DynamicList support - live database queries (simple auto-query and complex manual query variants)
**New in 2.2.0:** RadioButtonField, CheckBoxField, ChoiceList, InputHint, Command pictures with auto-representation
**New in 2.1.0:** Table events (OnActivateRow, Selection, OnStartEdit), Full BSL signatures support
