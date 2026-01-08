# 1C Processor Generator - Core Guide for LLMs

**Target:** Claude, GPT, and other LLMs generating 1C:Enterprise 8.3 external processors
**Version:** 3.0.0 (Optimized for Claude Sonnet 4.5+)

---

## 🎯 Your Role & Task Complexity

You are an **expert code generation agent** for 1C:Enterprise 8.3. This is a **COMPLEX, MULTI-STEP TASK** requiring:

- **Deep analysis** of user requirements (functional goals, data structure, workflow)
- **Architectural decisions** (persistent vs temporary data, UI patterns, client-server split)
- **Code generation** across multiple files (YAML configuration + BSL business logic)
- **Validation** against strict platform constraints (Cyrillic alphabet, reserved keywords, metadata rules)

### Complexity Indicators

| Indicator | Details |
|-----------|---------|
| **Domain** | 1C:Enterprise (proprietary Russian ERP platform) |
| **Output** | 500-1500 lines of valid YAML + BSL code |
| **Constraints** | 40+ reserved keywords, Cyrillic restrictions, 1C XML format requirements |
| **Success criteria** | Generated processor compiles and runs in 1C without errors |

⚡ **Use thinking capabilities:** Before generating code, **explicitly reason through architecture decisions** (see Thinking Framework below).

---

## 📦 QUICK START: Basic Workflow

**Before diving into rules, understand the basic workflow:**

### 1. What You Generate (Files)

You generate **2-4 files** that the generator uses to create a complete 1C processor:

```yaml
config.yaml         # Processor structure (YAML) - attributes, forms, commands
handlers.bsl        # Business logic (BSL code) - event handlers, calculations
object_module.bsl   # Optional: reusable logic, exported procedures
tests.yaml          # Optional: test definitions (v2.16.0+)
```

**When to use object_module.bsl:**
- Reusable logic shared between forms (calculations, validations, transformations)
- Heavy server-side calculations and business rules
- Exported procedures (callable via COM for testing, external integrations)

**Alternative: #Область МодульОбъекта region (v2.66.0+)**
Instead of separate `object_module.bsl`, you can write ObjectModule code directly in `handlers.bsl`:
```bsl
#Область МодульОбъекта

Функция СведенияОВнешнейОбработке() Экспорт
    // This code goes to ObjectModule.bsl
КонецФункции

#КонецОбласти

&НаКлиенте
Процедура Command1(Команда)
    // This code goes to FormModule
КонецПроцедуры
```
- Code is auto-wrapped with `#Если Сервер...`
- Supports names: `МодульОбъекта`, `МодульОб'єкта`, `ObjectModule`
- Combines with `bsp:` section if both present

### 2. CLI Commands (How to Run Generator)

**Basic workflow (XML only, fast):**
```bash
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl
```

**With EPF compilation (recommended for immediate testing):**
```bash
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output-format epf
```

**With validation (checks syntax automatically):**
```bash
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output-format epf \
  --validate
```

### 3. What Gets Generated (Output Structure)

The generator creates this directory structure in `tmp/` (or `--output` directory):

```
tmp/ProcessorName/
├── ProcessorName.xml           # Main processor XML
├── ProcessorName.epf           # Compiled EPF (if --output-format epf)
└── ProcessorName/
    ├── Ext/
    │   └── ObjectModule.bsl    # Object module code
    └── Forms/
        └── Форма/
            └── Ext/Form/
                ├── Form.xml     # Form structure (elements, commands)
                └── Module.bsl   # Form module (handlers)
```

### 4. Compilation Modes (Automatic Detection)

The generator automatically chooses the compilation mode:

| Mode | When Used | Speed |
|------|-----------|-------|
| **Fast mode** | No CatalogRef/DocumentRef, no validation | ⚡ Very fast (seconds) |
| **Configuration mode** | Has metadata types OR `validation:` enabled | 🐢 Slower (30-60s) but validates semantics |

### 5. Corner Cases You Must Handle

| Case | What Happens | How to Handle |
|------|--------------|---------------|
| **No Designer found** | Falls back to XML only, shows error | Tell user to install 1C or add `--designer-path` |
| **Validation errors** | Blocks compilation by default | Fix errors OR use `--ignore-validation-errors` (not recommended) |
| **Tests enabled** | Auto-generates pytest tests in `tests/` | Requires `tests_file:` in YAML config |
| **Handler approaches** | Two ways to provide BSL code | `--handlers-file handlers.bsl` (recommended) OR `--handlers handlers/` (legacy) |
| **Multiple forms** | Can have 2+ forms in one processor | Use `forms:` array, set `default: true` on one form |
| **Background Jobs** | Long operations (30s+) need special handling | Add `long_operation: true` to command (v2.17.0+) |
| **DynamicList** | Live database queries need metadata | Add `is_dynamic_list: true` + `main_table:` (v2.6.0+) |
| **FormAttributes** | spreadsheet_document, binary_data, string | Use `form_attributes:` section, not `attributes:` (v2.15.1+) |
| **HTMLDocumentField** | Display HTML content in forms | Use `type: HTMLDocumentField` + `form_attributes: type: string` (v2.39.0+) |
| **Templates (Макети)** | Store HTML/MXL layouts in processor | Use `templates:` section with external files (v2.40.0+) |
| **Template Automation** | Auto-create fields, placeholders, assets | Use `auto_field: true` + `automation:` file (v2.41.0+) |
| **Multiple languages** | Support ru, uk, en | Use Compact Multilang: `title: "RU \| UK"` or `title: [RU, UK]` (v2.69.0+). Legacy: `synonym_ru`, `synonym_uk` |
| **ObjectModule** | Reusable logic, exported procedures, heavy calculations | Use `object_module: { file: ... }` in YAML → See reference/ADVANCED_FEATURES.md |
| **ObjectModule Region** | Write ObjectModule code in handlers.bsl | Use `#Область МодульОбъекта` region (v2.66.0+) - auto-wrapped with `#Если Сервер...` |
| **Module Documentation** | Add documentation region to Module.bsl | Use `documentation_file:` OR `#Область Документация` in handlers.bsl |
| **Testing Fixtures** | Reusable test setup data (DRY testing) | Define `fixtures:` in tests.yaml → See reference/ADVANCED_FEATURES.md (Fixtures) |
| **Extended Assertions** | 12+ assertion types (gt, lt, regex, type checks) | Use in tests: `operator: gt/matches/type/in` → See reference/ADVANCED_FEATURES.md |
| **Visual Properties** | Professional UI styling (width, height, multiline, etc.) | See Visual Design Essentials below |
| **Ukrainian Cyrillic** | XML validation error, won't compile | See CRITICAL RULES below |

---

### 💡 Quick Decision: FormAttributes vs Attributes

**CRITICAL distinction** - choosing wrong section causes runtime errors:

**Use `attributes:` (processor-level, persistent):**
- ✅ Data that **persists** (saved with processor, survives form close)
- ✅ Simple types: `string`, `number`, `boolean`, `date`, `CatalogRef`, `DocumentRef`
- ✅ Business data: settings, parameters, calculation results
- ✅ TabularSection data (persistent tables)
- **Access in BSL:** `Объект.AttributeName`

**Use `form_attributes:` (form-level only, temporary):**
- ✅ **spreadsheet_document** (reports, formatted output - MUST be form attribute)
- ✅ **binary_data** (files, images - MUST be form attribute)
- ✅ **string** (HTML content for HTMLDocumentField - MUST be form attribute, v2.39.0+)
- ✅ **ValueTable** (temporary calculation results, not saved via value_tables:)
- ✅ Temporary UI state (exists only while form is open)
- **Access in BSL:** `AttributeName` (no `Объект.` prefix)

**Example:**
```yaml
attributes:
  - name: CompanyName
    type: string                    # ✅ Persists with processor

  - name: StartDate
    type: date                      # ✅ Persistent business data

form_attributes:
  - name: Report
    type: spreadsheet_document      # ✅ MUST be form attribute!

  - name: HTMLContent
    type: string                    # ✅ For HTMLDocumentField (v2.39.0+)

value_tables:
  - name: Results
    columns: [...]                  # ✅ Temporary table, not saved
```

**Rule of thumb:** If it's `spreadsheet_document`, `binary_data`, or `string` (for HTML) → **MUST** use `form_attributes:`

**Why this matters:** Using wrong section → "Attribute not found" runtime error

---

## 🎨 Visual Design Essentials

**Professional forms require visual properties** - LLMs often miss these, resulting in functional but unprofessional UI.

### Sizing Properties

⚠️ **IMPORTANT: 1C forms use conditional units (NOT pixels!)**
- **width** = **character units** (approximate number of visible characters)
- **height** = **row units** (number of visible rows/lines)
- Actual pixel size depends on: font size, DPI, interface scale (50-400%)

**Element width (in character units):**
```yaml
elements:
  - type: InputField
    name: APIKey
    width: 30              # ✅ 30 characters wide (prevents excessive stretching)

  - type: Button
    name: Calculate
    width: 15              # ✅ 15 characters wide (consistent button sizing)
```

**When to use:**
- `width: 20-40` for InputField (character units - prevents overly wide fields)
- `width: 10-20` for Button (character units - professional appearance)
- `width: 5-15` for Table columns (character units - data fit)

**Element height (in row units):**
```yaml
elements:
  - type: Table
    name: Results
    height: 10            # ✅ 10 visible rows without scrolling

  - type: InputField
    name: Description
    multiline: true
    height: 5             # ✅ 5 visible text lines (row units)
```

**Horizontal stretch control:**
```yaml
elements:
  - type: InputField
    name: Code
    horizontal_stretch: false    # ✅ Prevents field from expanding excessively
```

**When NOT to use:** Forms with dynamic resizing requirements

### Layout & Positioning

**Title location (label positioning):**
```yaml
elements:
  - type: InputField
    name: CompanyName
    title_location: Left         # ✅ Label on left (classic forms)

  - type: InputField
    name: Notes
    multiline: true
    title_location: Top          # ✅ Label above (for wide fields)

  - type: CheckBoxField
    name: Enabled
    title_location: Right        # ✅ Checkbox with label on right
```

**When to use:**
- `Left` - Standard forms, compact layouts (default)
- `Top` - Wide fields (multiline, long inputs)
- `Right` - CheckBox, RadioButton (common pattern)
- `None` - Hide label (use for decorations)

**Group direction:**
```yaml
elements:
  - type: UsualGroup
    name: ButtonToolbar
    group_direction: Horizontal   # ✅ Buttons in a row
    elements:
      - type: Button
        name: Save
      - type: Button
        name: Cancel
```

**Values:** `Vertical` (default), `Horizontal`

### Multi-line Text

**Enable multi-line input:**
```yaml
elements:
  - type: InputField
    name: Description
    attribute: Description
    multiline: true              # ✅ Text area instead of single line
    height: 5                    # Recommended: set height too
    title_location: Top          # Recommended: label above
```

**When to use:**
- Long text fields (descriptions, comments, notes)
- JSON/XML input fields
- Any text exceeding 50-100 characters

### Visual Grouping

**Group representation (visual style):**
```yaml
elements:
  - type: UsualGroup
    name: MainSection
    representation: NormalSeparation    # ✅ Visual separator line
    elements: [...]

  - type: UsualGroup
    name: AdvancedOptions
    representation: WeakSeparation      # ✅ Subtle grouping
    elements: [...]
```

**Values:**
- `None` - No visual separator (default)
- `WeakSeparation` - Subtle grouping
- `NormalSeparation` - Clear visual separator
- `StrongSeparation` - Prominent section divider

**Group behavior (collapsible sections):**
```yaml
elements:
  - type: UsualGroup
    name: AdvancedSettings
    title_ru: Расширенные настройки
    behavior: Collapsible          # ✅ User can collapse/expand
    representation: NormalSeparation
    elements: [...]
```

**Values:**
- `Usual` - Normal group (default)
- `Collapsible` - Can be collapsed by user

**When to use:** Optional settings, advanced options, rarely used fields

### Button Styling

**Button representation (visual style):**
```yaml
commands:
  - name: OpenSettings
    title_ru: Настройки
    handler: OpenSettings
    picture: Settings             # Icon name
    representation: PictureAndText  # ✅ Icon + text

  - name: Refresh
    title_ru: Обновить
    handler: Refresh
    picture: Refresh
    representation: Picture        # ✅ Icon only (compact)
```

**Values:**
- `Text` - Text only (default)
- `Picture` - Icon only
- `PictureAndText` - Icon left, text right
- `TextPicture` - Text left, icon right

### Custom Pictures from SVG (v2.23.0+)

**Convert SVG files to local PNG pictures:**
```yaml
elements:
  - type: PictureDecoration
    name: CompanyLogo
    svg_source: logo.svg           # ✅ SVG file (relative to config.yaml)
    width: 200                     # PNG output size in PIXELS (for SVG→PNG conversion)
    height: 80                     # PNG output size in PIXELS
    picture_size: Proportionally   # Scaling mode (platform auto-scales on form)
```

✅ **NEW in v2.23.1:** Separate sizing for PNG generation and form display!

**Current API (v2.23.1+):**
```yaml
  - type: PictureDecoration
    svg_source: logo.svg
    svg_width: 200         # PNG output size in PIXELS (high quality)
    svg_height: 80
    form_width: 25         # Form display size: 25 characters wide (character units)
    form_height: 10        # Form display size: 10 rows tall (row units)
    picture_size: Proportionally
```

**Backward compatibility:** Old `width`/`height` fields automatically map to `svg_width`/`svg_height`
```yaml
  # Old API (still works):
  width: 200    # → svg_width: 200
  height: 80    # → svg_height: 80
```

**How it works:**
- SVG file automatically converted to PNG during generation
- PNG stored in `Forms/{FormName}/Ext/Form/Items/{ElementName}/Picture.png`
- SVG files validated (must be valid XML with `<svg>` root)
- PNG optimized (max 100KB)

**When to use:** Custom logos, branded icons, vector graphics (scales well)

**Alternative (standard icons):**
```yaml
- type: PictureDecoration
  name: Icon
  picture: StdPicture.Information   # ✅ Built-in 1C platform icons
```

### Table Properties

**Table height and column widths:**
```yaml
elements:
  - type: Table
    name: Products
    tabular_section: Products
    height: 12                    # ✅ 12 visible rows (row units, NOT pixels!)
    columns:
      - name: ProductName
        attribute: ProductName
        width: 30                 # ✅ 30 characters wide (character units)

      - name: Quantity
        attribute: Quantity
        width: 10                 # ✅ 10 characters wide (narrow numeric column)

      - name: Price
        attribute: Price
        width: 15                 # ✅ 15 characters wide
```

**Best practices:**
- Set table `height: 8-15` (visible rows in row units) for good visibility
- Set column `width` (character units) based on data type:
  - Text: 20-40 characters
  - Numbers: 8-15 characters
  - Dates: 12-18 characters
  - Booleans: 5-8 characters

### Input Enhancements

**Password mode (mask characters):**
```yaml
elements:
  - type: InputField
    name: Password
    attribute: Password
    password_mode: true              # ✅ Masks input with *** (v2.35.0+)
```

**When to use:** Password fields, sensitive data input

**Text edit mode:**
```yaml
elements:
  - type: InputField
    name: Document
    attribute: Document
    text_edit: true                  # ✅ Enable text editing capabilities (v2.35.0+)
```

**When to use:** Formatted text documents, rich text editing

**Auto max width:**
```yaml
elements:
  - type: InputField
    name: Description
    attribute: Description
    auto_max_width: true             # ✅ Auto-adjusts width to fit content (v2.35.0+)
```

**When to use:** Fields with variable content length

**Input hint (placeholder text):**
```yaml
elements:
  - type: InputField
    name: APIKey
    attribute: APIKey
    input_hint: "Enter your API key here"    # ✅ Placeholder text
```

**When to use:** Guide users on expected input format

**Choice list (dropdown):**
```yaml
elements:
  - type: InputField
    name: Environment
    attribute: Environment
    choice_list:                  # ✅ Makes field a dropdown/combobox
      - v: "Production"           # v=value, ru=presentation
        ru: "Production"
      - v: "Staging"
        ru: "Staging"
      - v: "Development"
        ru: "Development"
```

**When to use:** Predefined options, validated input

### Form-level Styling

**Window opening mode:**
```yaml
forms:
  - name: Settings
    default: false
    properties:
      WindowOpeningMode: LockOwnerWindow    # ✅ Modal dialog (v2.35.0+)
```

**Values:**
- `Independent` - Non-modal (default)
- `LockOwnerWindow` - Modal dialog
- `LockWholeInterface` - Block entire interface

**Command bar location:**
```yaml
forms:
  - name: MainForm
    default: true
    properties:
      CommandBarLocation: Bottom          # ✅ Command bar at bottom (v2.35.0+)
```

**Values:**
- `None` - Hide command bar
- `Top` - Command bar at top (default)
- `Bottom` - Command bar at bottom

### Special Properties

**Hyperlink (clickable label):**
```yaml
elements:
  - type: LabelDecoration
    name: HelpLink
    title_ru: Открыть справку
    hyperlink: true               # ✅ Clickable, underlined
    events:
      OnClick: OpenHelp
```

**Radio button style:**
```yaml
elements:
  - type: RadioButtonField
    name: Mode
    attribute: Mode
    radio_button_type: Tumbler    # ✅ Modern toggle switch style
```

**Values:**
- `RadioButton` - Classic radio buttons (default)
- `Tumbler` - Modern toggle/switch style

### Element Events (v2.35.0+)

**InputField events:**
```yaml
elements:
  - type: InputField
    name: SelectedValue
    attribute: SelectedValue
    events:
      StartChoice: SelectedValueStartChoice              # Custom choice dialog
      ChoiceProcessing: SelectedValueChoiceProcessing    # After value selection (v2.35.0+)
```

**ChoiceProcessing event:**
- **When fired:** After user selects value from choice dialog
- **Handler signature:** `ОбработкаВыбора(Элемент, ВыбранноеЗначение, СтандартнаяОбработка)`
- **Use case:** Validate selected value, transform data, prevent default processing
- **Example:** Reject empty values, format phone numbers, check duplicates

**Table events:**
```yaml
elements:
  - type: Table
    name: Items
    tabular_section: Items
    events:
      BeforeAddRow: ItemsBeforeAddRow          # Before adding new row (v2.35.0+)
      BeforeDeleteRow: ItemsBeforeDeleteRow    # Before deleting row (v2.35.0+)
      BeforeRowChange: ItemsBeforeRowChange    # Before editing row (v2.35.0+)
```

**BeforeAddRow event:**
- **Handler signature:** `ПередДобавлениемСтроки(Элемент, Отказ, Копирование, Родитель, Группа)`
- **Use case:** Pre-fill new row with default values, validate before adding, prevent row addition
- **Parameters:** `Отказ = Истина` to prevent row addition

**BeforeDeleteRow event:**
- **Handler signature:** `ПередУдалениемСтроки(Элемент, Отказ)`
- **Use case:** Confirm deletion with user, validate before delete, prevent deletion
- **Parameters:** `Отказ = Истина` to prevent row deletion

**BeforeRowChange event:**
- **Handler signature:** `ПередИзменениемСтроки(Элемент, Отказ)`
- **Use case:** Validate before editing, check permissions, prevent editing
- **Parameters:** `Отказ = Истина` to prevent row editing

### Quick Visual Properties Reference

⚠️ **Units of Measurement:**
- Form elements: **character units** (width) / **row units** (height) — NOT pixels!
- PictureDecoration (SVG): **pixels** (for PNG generation only, v2.23.0 limitation)

| Property | Element Types | Units | Common Values | When to Use |
|----------|--------------|-------|---------------|-------------|
| `width` | InputField, Button | **character units** | 10-40 | Control element width in characters |
| `width` | Table Column | **character units** | 5-40 | Column width in characters |
| `svg_width` | PictureDecoration (SVG) | **pixels** | 100-500 | PNG output size (v2.23.1+) |
| `svg_height` | PictureDecoration (SVG) | **pixels** | 50-200 | PNG output size (v2.23.1+) |
| `form_width` | PictureDecoration | **character units** | 10-50 | Form display width (v2.23.1+) |
| `form_height` | PictureDecoration | **row units** | 5-20 | Form display height (v2.23.1+) |
| `height` | Table | **row units** | 5-15 | Visible rows without scrolling |
| `height` | InputField (multiline) | **row units** | 3-10 | Visible text lines |
| `svg_source` | PictureDecoration | "logo.svg" | Custom SVG → PNG (v2.23.0+) |
| `picture` | PictureDecoration | StdPicture.Information | Built-in platform icons |
| `picture_size` | PictureDecoration | Proportionally, Stretch, AutoSize, Tile, RealSize | Image scaling mode |
| `horizontal_stretch` | Any | true/false | Prevent excessive expansion |
| `title_location` | InputField, CheckBox, etc. | None, Left, Right, Top, Bottom, Auto | Label positioning |
| `multiline` | InputField | true | Multi-line text areas |
| `password_mode` | InputField | true | Mask password input (v2.35.0+) |
| `text_edit` | InputField | true/false | Text editing mode (v2.35.0+) |
| `auto_max_width` | InputField | true | Auto-adjust width (v2.35.0+) |
| `group_direction` | UsualGroup | Horizontal, Vertical | Button toolbars, layouts |
| `representation` | UsualGroup | NormalSeparation, WeakSeparation | Visual grouping |
| `behavior` | UsualGroup | Collapsible | Optional sections |
| `input_hint` | InputField | "text" | Placeholder guidance |
| `choice_list` | InputField | [{v, ru, uk, en, t}] | Dropdown selection |
| `hyperlink` | LabelDecoration | true | Clickable links |
| `radio_button_type` | RadioButtonField | Tumbler | Modern toggle style |
| `WindowOpeningMode` | Form (properties) | LockOwnerWindow | Modal dialogs (v2.35.0+) |
| `CommandBarLocation` | Form (properties) | Bottom, Top, None | Command bar position (v2.35.0+) |

**Pro tip:** Combine properties for professional results:
```yaml
- type: InputField
  name: Description
  multiline: true          # Multi-line text area
  height: 5                # 5 visible text lines (row units, NOT pixels!)
  title_location: Top      # Label above (for wide fields)
  width: 40                # 40 characters wide (character units, NOT pixels!)
  input_hint: "Enter detailed description"  # Placeholder guidance
```

---

### 6. Minimal Example (Copy-Paste Ready)

**config.yaml:**
```yaml
processor:
  name: ПримерОбработки
  synonym_ru: Пример обработки
  platform_version: "2.11"

attributes:
  - name: Число
    type: number
    digits: 10
    fraction_digits: 2

forms:
  - name: Форма
    default: true
    elements:
      - type: InputField
        name: Число
        attribute: Число
    commands:
      - name: Рассчитать
        title_ru: Рассчитать
        handler: Рассчитать
```

**handlers.bsl:**
```bsl
// Обробник команди
&НаКлиенте
Процедура Рассчитать(Команда)
    РассчитатьНаСервере();
КонецПроцедуры

&НаСервере
Процедура РассчитатьНаСервере()
    Объект.Число = Объект.Число * 2;
    Сообщить("Готово!");
КонецПроцедуры
```

**Run generator:**
```bash
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output-format epf
```

**Result:** `tmp/ПримерОбработки/ПримерОбработки.epf` ready to open in 1C

### 7. Navigation to Other Documents

**Now that you understand the basics, read these guides based on your task:**

| If you need... | Read this document |
|----------------|-------------------|
| UI patterns (Simple Form, Report, Master-Detail) | [LLM_PATTERNS_ESSENTIAL.md](LLM_PATTERNS_ESSENTIAL.md) |
| Data model decisions (ValueTable vs TabularSection) | [LLM_DATA_GUIDE.md](LLM_DATA_GUIDE.md) |
| **HTML/CSS/JS interfaces in 1C** | [LLM_HTML_GUIDE.md](LLM_HTML_GUIDE.md) |
| Validation, error handling, best practices | [LLM_PRACTICES.md](LLM_PRACTICES.md) |
| Complete YAML API reference | [reference/API_REFERENCE.md](reference/API_REFERENCE.md) |
| Advanced features (Testing, Background Jobs, DynamicList) | [reference/ADVANCED_FEATURES.md](reference/ADVANCED_FEATURES.md) |
| Common errors and solutions | [reference/TROUBLESHOOTING.md](reference/TROUBLESHOOTING.md) |

---

## ⚠️ CRITICAL RULES (with WHY explanations)

### Rule 1: Russian Cyrillic ONLY in Identifiers

**What's forbidden:** Ukrainian Cyrillic letters `і ї є ґ І Ї Є Ґ` in processor/attribute/command/handler **names**

**WHY this matters:**

1C platform validates identifiers with this **exact regex**:
```regex
^[а-яА-ЯёЁa-zA-Z_][а-яА-ЯёЁa-zA-Z0-9_]*$
```

This regex **excludes Ukrainian Cyrillic** because Ukrainian letters are **different Unicode code points**:
- Ukrainian `і` (U+0456) ≠ Russian `и` (U+0438) — looks identical, but platform **rejects it**
- Ukrainian `ї` (U+0457) ≠ Russian combinations
- Ukrainian `є` (U+0454) ≠ Russian `е` (U+0435)
- Ukrainian `ґ` (U+0491) ≠ Russian `г` (U+0433)

**Impact:** Using Ukrainian letters → `XML validation error` → processor doesn't compile

**What IS allowed:**
- ✅ Ukrainian in **user-facing text** (synonyms, titles, tooltips, messages, BSL strings)
- ❌ Ukrainian in **metadata identifiers** (processor name, attribute names, handler names, command names)

**Detection strategy:**

```yaml
# User says: "Створи обробку для пошукового запиту"
# Contains Ukrainian word "пошуковий" (has 'і')

# ❌ WRONG - direct translation to identifier
processor:
  name: ПошуковийЗапит  # Contains Ukrainian 'і' → COMPILATION ERROR

# ✅ RIGHT - translate identifier to Russian, preserve Ukrainian in synonym
processor:
  name: ПоисковыйЗапрос       # Russian Cyrillic (и instead of і)
  synonym:
    ru: "Поисковый запрос"
    uk: "Пошуковий запит"     # ✅ Ukrainian allowed in synonyms
    en: "Search Query"
```

**Mental model:** Identifiers = "machine names" (strict), synonyms = "human names" (flexible)

---

### Rule 2: NO BSL Reserved Keywords in Handler Names

**What's forbidden:** Handler names that match BSL reserved keywords

**Full list (40+ keywords):**
```
Выполнить, Экспорт, Импорт, Процедура, Функция, КонецПроцедуры, КонецФункции,
Прервать, Продолжить, Возврат, Если, Тогда, ИначеЕсли, Иначе, КонецЕсли,
Для, По, Пока, Цикл, КонецЦикла, Каждого, Из, Попытка, Исключение, ВызватьИсключение,
КонецПопытки, Новый, Перем, Знач, И, Или, Не, Истина, Ложь, Неопределено, NULL
```

**WHY this matters:**

Generator wraps your BSL code in procedure signatures. If handler name is a reserved keyword → **parse error**

**Example failure:**

```yaml
commands:
  - name: Execute
    handler: Выполнить  # ❌ "Выполнить" is reserved keyword
```

Generator tries to create:
```bsl
Процедура Выполнить()  # ❌ PARSE ERROR: "Выполнить" is keyword, not identifier
    // Your code here
КонецПроцедуры
```

**Solution pattern - add context:**

```yaml
commands:
  - name: Execute
    handler: ВыполнитьОбработку  # ✅ "Execute Processing" - not reserved
```

Generates valid code:
```bsl
Процедура ВыполнитьОбработку()  # ✅ Valid identifier
    // Your code here
КонецПроцедуры
```

---

### Rule 3: Valid StdPicture Names Only

**What's required:** Picture names must match 1C platform's built-in collection

**WHY this matters:** 1C validates picture names at runtime. Invalid name → picture not displayed OR error

**Common mistakes:**

```yaml
❌ StdPicture.CheckMark   # Does not exist
❌ StdPicture.Save        # Does not exist
✅ StdPicture.Check       # ✅ Exists
✅ StdPicture.Write       # ✅ Exists (save action)
```

**Source of truth:** [VALID_PICTURES.md](reference/VALID_PICTURES.md) (130+ valid names)

**Tip:** When unsure, **omit picture** rather than guessing (pictures are optional)

---

### Rule 4: Handler File Naming = YAML Handler Name

**What's required:** BSL file name must **exactly match** handler name in YAML

```yaml
commands:
  - name: LoadData
    handler: LoadDataНаСервере  # ← File MUST be: handlers/LoadDataНаСервере.bsl
```

**WHY this matters:** Generator looks for file by exact name. Mismatch → `Handler file not found` error

---

### Rule 5: CLI Options Come AFTER Subcommand

**What's required:** All flags (--output-format, --output, etc.) come **after** subcommand name

```bash
❌ WRONG: python -m 1c_processor_generator --output-format epf yaml --config config.yaml
✅ RIGHT: python -m 1c_processor_generator yaml --config config.yaml --output-format epf
```

**WHY this matters:** Standard CLI pattern (git, docker, kubectl). Options belong to subcommand, not global parser.

**Common mistake:** Putting `--output-format epf` before `yaml` → "unrecognized arguments" error

---

## 🔍 COMMON VALIDATION ERRORS (Practical Detection & Fixes)

**CRITICAL:** These errors occur AFTER code generation, blocking compilation. Learn to detect them early.

### Error Type 1: Ukrainian Cyrillic in Identifiers (MOST COMMON)

**Error message:**
```
'ПрофесійнаФорма' does not match '^[а-яА-ЯёЁa-zA-Z_][а-яА-ЯёЁa-zA-Z0-9_]*$'
```

**Root cause:** Used Ukrainian letter instead of Russian equivalent in processor/attribute/handler **name**

**Detection pattern:**
```
User request contains Ukrainian words → scan for these letters:
- Ukrainian 'і' (looks like Latin 'i') → FORBIDDEN in identifiers
- Ukrainian 'ї' → FORBIDDEN
- Ukrainian 'є' → FORBIDDEN
- Ukrainian 'ґ' → FORBIDDEN

ONLY Russian Cyrillic allowed: а-я, А-Я, ё, Ё
```

**Real examples from perfect_form_example:**

| ❌ Ukrainian (error) | ✅ Russian (fixed) | Letter changed |
|---------------------|-------------------|----------------|
| ПрофесійнаФорма | ПрофессиональнаяФорма | і→и, ї→и |
| НазваКомпанії | НазваниеКомпании | і→и |
| ОписДіяльності | ОписаниеДеятельности | і→и |
| СумаКонтракту | СуммаКонтракта | none (but check context) |
| Підтверджено | Подтверждено | і→о |
| Результати | Результаты | і→ы |
| Операція | Операция | і→и |

**Quick fix strategy:**
1. **Translate identifier to Russian** (machine name)
2. **Preserve Ukrainian in synonym** (human name)

```yaml
# ❌ WRONG - Ukrainian identifier
processor:
  name: ПошуковийЗапит  # Contains Ukrainian 'і' → COMPILATION ERROR

# ✅ RIGHT - Russian identifier, Ukrainian synonym
processor:
  name: ПоисковыйЗапрос       # Russian Cyrillic (и instead of і)
  synonym_ru: "Поисковый запрос"
  synonym_uk: "Пошуковий запит"  # ✅ Ukrainian allowed in synonyms
```

**Mental model:**
- Identifiers (names) = **machine-readable** → strict Russian Cyrillic only
- Synonyms/titles = **human-readable** → any language allowed (ru, uk, en)

---

### Error Type 2: BSL Reserved Keywords as Handler Names

**Error message:**
```
Ім'я обробника 'Выполнить' є зарезервованим ключовим словом BSL
```

**Root cause:** Handler name matches BSL reserved keyword → parse error when generator wraps in procedure signature

**Most common violations:**
- `Выполнить` (Execute) - very common user request
- `Экспорт` (Export) - file operations
- `Процедура`, `Функция` - never use these
- `Возврат`, `Прервать` - control flow keywords

**Detection pattern:**
```
When user says: "додай кнопку Виконати" or "add Execute button"
Your handler name: "Выполнить" → CHECK: Is this a reserved keyword?
If YES → add context suffix
```

**Real fix examples:**

| User request | ❌ Handler (reserved) | ✅ Handler (fixed) |
|--------------|----------------------|-------------------|
| "Execute task" | Выполнить | ВыполнитьОбработку |
| "Export data" | Экспорт | ЭкспортироватьДанные |
| "Import file" | Импорт | ИмпортироватьФайл |
| "Return result" | Возврат | ВернутьРезультат |
| "Break operation" | Прервать | ПрерватьОперацию |

**Pattern:** Add **context noun** to make unique identifier (not just generic verb)

```yaml
# ❌ WRONG - reserved keyword
commands:
  - name: Execute
    handler: Выполнить  # PARSE ERROR

# ✅ RIGHT - context added
commands:
  - name: Execute
    handler: ВыполнитьОбработку  # "Execute Processing" - valid identifier
```

**Full list of 40+ reserved keywords:** See Rule 2 above (lines 748-754)

---

### Error Type 3: Invalid Data Types

**Error message:**
```
Атрибут 'Photo': Невідомий тип даних: binary_data
```

**Root cause:** Used type name that doesn't exist in 1C platform

**Valid types:**
```yaml
# Simple types (processor attributes)
- type: string          # Text (default unlimited length)
- type: string
  length: 100           # Limited string (100 characters)
- type: number          # Numeric with precision
  digits: 10
  fraction_digits: 2
- type: boolean         # True/False checkbox
- type: date            # Date and/or time

# Metadata references (require Configuration mode)
- type: CatalogRef.Контрагенты    # Reference to catalog
- type: DocumentRef.Накладная     # Reference to document

# Form-level types (MUST use form_attributes:)
- type: spreadsheet_document      # Reports, formatted output
- type: binary_data               # Files, images (MUST be form attribute)
- type: string                    # HTML content for HTMLDocumentField
```

**Common mistakes:**

| ❌ Invalid type | ✅ Correct approach |
|----------------|---------------------|
| `type: BinaryData` | `type: binary_data` (lowercase!) + use `form_attributes:` |
| `type: HTMLDocument` | `type: string` + use `form_attributes:` for HTMLDocumentField |
| `type: ValueStorage` | Use `binary_data` in `form_attributes:` OR TabularSection column |
| `type: file` | No file type - use `binary_data` in `form_attributes:` |
| `type: image` | Use `binary_data` OR `PictureDecoration` with `svg_source:` |

**Example fix:**
```yaml
# ❌ WRONG
attributes:
  - name: Photo
    type: BinaryData    # Wrong section AND wrong case!

# ✅ RIGHT - Option 1: Form attribute
form_attributes:
  - name: Photo
    type: binary_data   # Correct type (lowercase!), correct section

# ✅ RIGHT - Option 2: Picture decoration (if displaying image)
elements:
  - type: PictureDecoration
    name: Photo
    svg_source: logo.svg    # Convert SVG to PNG automatically
```

---

### Error Type 4: Handler File Not Found

**Error message:**
```
Handler file not found: handlers/ВыполнитьОбработку.bsl
```

**Root cause:** BSL filename doesn't exactly match YAML handler name (case-sensitive, Cyrillic-sensitive)

**Detection checklist:**
- [ ] Filename matches handler name **exactly** (including case)
- [ ] Cyrillic letters match (Russian vs Ukrainian)
- [ ] No typos in either YAML or filename
- [ ] File extension is `.bsl` (not `.txt` or `.bs`)

**Example:**
```yaml
# YAML config
commands:
  - name: Execute
    handler: ВыполнитьОбработку  # ← File MUST be: handlers/ВыполнитьОбработку.bsl
```

**If using single-file approach** (`--handlers-file handlers.bsl`):
```bsl
// handlers.bsl
&НаКлиенте
Процедура ВыполнитьОбработку(Команда)  // ← Name must match YAML exactly
    // Your code
КонецПроцедуры
```

---

### Error Type 5: Root-Level Definitions with forms: Section

**Error message in 1C Designer:**
```
Файл - ...Form.xml: Неверный путь к данным: 'ИмяТаблицы'
Файл - ...Form.xml: Неверный путь к данным: 'Объект.ИмяАтрибута'
```
Or handlers simply don't work (no events fire).

**Root cause:** When using `forms:` section, the following must be INSIDE the form definition, not at root level:
- `form_attributes`
- `value_tables`
- `dynamic_lists`
- `commands`
- `form:` section (`events`, `elements`, `properties`)

The generator ignores root-level definitions when `forms:` section exists.

**Detection checklist:**
- [ ] If using `forms:` section, verify `form_attributes` is INSIDE the form
- [ ] If using `forms:` section, verify `value_tables` is INSIDE the form
- [ ] If using `forms:` section, verify `dynamic_lists` is INSIDE the form
- [ ] If using `forms:` section, verify `commands` is INSIDE the form
- [ ] If using `forms:` section, verify `events` is INSIDE the form (not in `form:` section)

**Example - WRONG (silently ignored):**
```yaml
processor:
  name: MyProcessor

# ❌ ROOT LEVEL - ALL WILL BE IGNORED when using forms: section!
form_attributes:
  - name: PreviewHTML
    type: spreadsheet_document

commands:
  - name: Execute
    title_ru: Выполнить
    title_uk: Виконати
    handler: ВыполнитьОбработку

form:
  events:
    OnOpen: ПриОткрытии  # ❌ IGNORED!
  elements:
    - type: InputField
      name: Field1       # ❌ IGNORED!

forms:
  - name: Form
    default: true
    elements:
      - type: SpreadSheetDocumentField
        name: PreviewField
        attribute: PreviewHTML  # ERROR: attribute not found!
```

**Example - CORRECT:**
```yaml
processor:
  name: MyProcessor

forms:
  - name: Form
    default: true
    # ✅ ALL INSIDE FORM - CORRECT!
    events:
      OnOpen: ПриОткрытии
    form_attributes:
      - name: PreviewHTML
        type: spreadsheet_document
    commands:
      - name: Execute
        title_ru: Выполнить
        title_uk: Виконати
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

---

### Quick Validation Checklist (Run Before Generation)

**Before generating processor, check:**

1. **Cyrillic validation** (30 seconds)
   - [ ] Scan all `name:` fields for Ukrainian letters (і, ї, є, ґ)
   - [ ] If found: translate to Russian equivalent
   - [ ] Preserve Ukrainian in `synonym_uk:`, `title_uk:`, `tooltip_uk:`

2. **Reserved keywords** (15 seconds)
   - [ ] Check all handler names against 40+ reserved keywords
   - [ ] Common violations: Выполнить, Экспорт, Импорт, Возврат, Прервать
   - [ ] If match: add context suffix (e.g., Выполнить → ВыполнитьОбработку)

3. **Type validation** (10 seconds)
   - [ ] No `binary_data`, `ValueStorage`, `file`, `image` types
   - [ ] `SpreadsheetDocument` and `BinaryData` in `form_attributes:` section
   - [ ] Metadata types (CatalogRef, DocumentRef) require Configuration mode

4. **File naming** (5 seconds)
   - [ ] Handler filenames match YAML handler names exactly
   - [ ] All `.bsl` extensions present

5. **forms: section placement** (10 seconds)
   - [ ] If using `forms:` section, verify `form_attributes` is INSIDE form definition
   - [ ] If using `forms:` section, verify `value_tables` is INSIDE form definition
   - [ ] If using `forms:` section, verify `dynamic_lists` is INSIDE form definition
   - [ ] If using `forms:` section, verify `commands` is INSIDE form definition
   - [ ] If using `forms:` section, verify `events` is INSIDE form (NOT in `form:` section)

**Total time:** ~1 minute to prevent compilation errors

---

### Real-World Example: perfect_form_example Fixes

**Initial version (40+ validation errors):**
- Ukrainian 'і' in 35+ identifiers → all changed to Russian 'и'
- Reserved keyword `Выполнить` → changed to `ВыполнитьОбработку`
- Reserved keyword `Экспорт` → changed to `ЭкспортироватьДанные`
- Invalid type `binary_data` → feature removed (not critical for UI showcase)

**Result:** Clean compilation, 73 elements generated, 0 errors

**Lesson:** Spend 1 minute on validation → save 30 minutes debugging compilation errors

---

## 🧠 THINKING FRAMEWORK (Use Before Code Generation)

**ALWAYS think through these steps explicitly** (leverage Claude 4.5 reasoning):

### Step 1: ANALYZE Requirements

**Ask yourself:**
- What is user trying to accomplish? (functional goal)
- What data do they need to work with? (input, output, calculations)
- Is this data **persistent** (saved to DB, survives form close) or **temporary** (in-memory, calculations, reports)?

### Step 2: DECIDE Architecture

**Decision Point A: Data Model**

```
IF data must survive form close (persistent):
    → TabularSection (saved to DB)
ELSE IF data is temporary (reports, calculations):
    → ValueTable (in-memory only)
```

**Decision Point B: UI Pattern**

```
IF simple input + action + result:
    → Pattern 1: Simple Form (input fields + button)

ELSE IF filters + table of results:
    → Pattern 2: Report with Table (filter section + results table)

ELSE IF master table selection auto-updates detail data:
    → Pattern 3: Master-Detail (table with OnActivateRow event)

ELSE IF multi-step sequential process:
    → Pattern 4: Wizard (Pages with step-by-step flow)
```

**Decision Point C: Data Source**

```
IF table data comes from database query:
    → DynamicList + Table (is_dynamic_list: true)

ELSE IF table data from calculations/API:
    → ValueTable + BSL handler
```

### Step 3: VALIDATE Constraints

**Run these checks in parallel** (Claude 4.5 excels at parallel reasoning):

```
CHECK 1: Cyrillic validation
  → Scan all identifiers for Ukrainian letters (і ї є ґ)
  → If found: translate to Russian equivalent

CHECK 2: Reserved keywords
  → Compare handler names against 40+ reserved keywords
  → If match: add context suffix (e.g., Выполнить → ВыполнитьОбработку)

CHECK 3: StdPicture names (if using pictures)
  → Verify against VALID_PICTURES.md
  → If invalid: omit picture OR use valid alternative

CHECK 4: Handler file naming
  → Ensure BSL filenames match YAML handler names exactly
```

### Step 4: GENERATE Code

**Generate in this order:**

1. **config.yaml** (structure)
   - Processor metadata
   - Attributes / TabularSections / ValueTables
   - Forms with elements and commands

2. **handlers.bsl** (business logic) — **RECOMMENDED: single file**
   - Form events (OnOpen, OnCreateAtServer)
   - Command handlers (client + server pairs)
   - Helper functions (auto-detected by generator)

3. **Generation command**
   - Provide complete CLI command with all required flags

### Step 5: EXPLAIN Choices

**Always explain to user:**
- **Why this data model?** (persistent vs temporary, ValueTable vs TabularSection)
- **Why this pattern?** (fits user's workflow)
- **Any assumptions made?** (explicit is better than implicit)

---

## 📚 NAVIGATION MAP (Just-In-Time Information Retrieval)

**START HERE ALWAYS:** This file (LLM_CORE.md)

**THEN, load additional docs based on task type:**

### When Task Involves Data Models

```
IF question about: "Should I use ValueTable or TabularSection?"
IF question about: "How to structure tables?"
IF question about: "Persistent vs temporary data?"
    → READ: LLM_DATA_GUIDE.md (decision framework, flowchart)
```

### When Task Involves UI Patterns

```
IF question about: "Which UI pattern to use?"
IF question about: "How to structure form layout?"
    → READ: LLM_PATTERNS_ESSENTIAL.md (3 canonical patterns, decision tree)

IF pattern not covered in essential docs:
    → READ: reference/ALL_PATTERNS.md (full 10+ pattern library)
```

### When Task Involves Code Quality

```
IF question about: "Naming conventions?"
IF question about: "Validation patterns?"
IF question about: "Error handling?"
IF question about: "Performance best practices?"
    → READ: LLM_PRACTICES.md (principles, templates)
```

### When Unsure What Features Exist (v2.44.0+)

```
IF question about: "What element types are available?"
IF question about: "What events can I use?"
IF question about: "What CLI commands exist?"
IF question about: "What are common mistakes to avoid?"
    → RUN: python -m 1c_processor_generator features
    → OR: python -m 1c_processor_generator features --category elements
    → OR: python -m 1c_processor_generator features --search "table"
    → OR: READ: docs/feature_registry.json (machine-readable)

COMMON MISTAKES (auto-detected with suggestions):
  - type: CommandBar → Use: UsualGroup with group_type: CommandBar
  - type: TextBox → Use: InputField
  - type: Grid → Use: Table
  - type: Tab → Use: Pages
  - event: OnClick → Use: Click (OnClick is only for HTMLDocumentField)
```

### When Task Involves Specific Features

```
IF question about: "DynamicList configuration?"
IF question about: "ObjectModule usage?"
IF question about: "Background jobs / long operations?"
IF question about: "Automated testing / test framework?"
IF question about: "Complete YAML API reference?"
    → SEARCH: reference/API_REFERENCE.md (full YAML specification)
    → OR: reference/ADVANCED_FEATURES.md (specific feature deep dive)

IF question about: "Settings forms / RadioButton / CheckBox / dropdowns?"
    → READ: LLM_PATTERNS_ESSENTIAL.md ("Beyond Essential" → Settings Forms section)
    → OR: reference/ALL_PATTERNS.md (Pattern 7)
    → ELEMENTS: RadioButtonField, CheckBoxField, ChoiceList, InputHint

IF question about: "Nested groups / button toolbars / complex layouts?"
    → READ: LLM_PATTERNS_ESSENTIAL.md ("Beyond Essential" → Complex Layouts section)
    → OR: reference/ALL_PATTERNS.md (Pattern 8)
    → KEY: UsualGroup inside UsualGroup (infinite depth)

IF question about: "Visual styling / professional UI / width / height / multiline?"
    → READ: Visual Design Essentials section above (lines ~167-462)
    → KEY: 13+ visual properties for professional forms

IF question about: "Table row height / font size / column styling?"
    → READ: reference/TABLE_STYLING.md (Table heights, font sizing, column colors)
    → KEY: height_in_table_rows, header_height, font: {size: 20}, back_color

IF question about: "Conditional formatting / row coloring / ConditionalAppearance?"
    → READ: reference/CONDITIONAL_APPEARANCE.md (Dynamic styling based on data)
    → KEY: conditional_appearances at form level, selection, filter, appearance

IF question about: "HTMLDocumentField / display HTML in form?"
    → Use `type: HTMLDocumentField` + `form_attributes: type: string` (v2.39.0+)
    → BSL: `HTMLАтрибут = "<html>...</html>"` - присвоюємо значення form_attribute
    → Events: OnClick (hyperlink clicks), DocumentComplete (after load)
    → READ: reference/API_REFERENCE.md (HTMLDocumentField section)

IF question about: "Templates / Макети / store HTML layouts?"
    → Use `templates:` section with external files (v2.40.0+)
    → Types: HTMLDocument (.html), SpreadsheetDocument (.mxl)
    → BSL: `Обработки.Name.ПолучитьМакет("TemplateName").ПолучитьТекст()`
    → READ: reference/API_REFERENCE.md (Templates section)

IF question about: "HTML Dashboard / HTML+CSS+JS interface / interactive HTML?"
    → Use `templates:` with `auto_field: true` + `automation:` file (v2.41.0+)
    → CRITICAL: NO EMOJI in HTML (use SVG icons) - 1C has limited Unicode support
    → READ: LLM_HTML_GUIDE.md (complete guide with full example)
```

### When Task Results in Error

```
IF compilation error occurs:
IF validation error occurs:
IF unexpected behavior:
    → READ: reference/TROUBLESHOOTING.md (edge cases, common mistakes, solutions)
```

**Principle:** **Just-in-time retrieval**. Don't read all 4,688 lines upfront—fetch what you need when you need it.

---

## 🔄 WORKFLOW (with Parallel Execution Guidance)

### 1. Analyze (sequential)
- Read user requirements
- Apply Thinking Framework Step 1 (ANALYZE)

### 2. Design (parallel thinking possible)
- **In parallel:** Reason about data model AND UI pattern simultaneously
- Apply Thinking Framework Step 2 (DECIDE)

### 3. Validate (parallel checks)
- **Run all 4 checks simultaneously:**
  - Cyrillic validation ║ Reserved keywords check ║ StdPicture validation ║ Handler naming check
- Apply Thinking Framework Step 3 (VALIDATE)
- Claude 4.5 excels at parallel operations—use it

### 4. Generate (sequential, but structured)
- Create config.yaml
- Create handlers.bsl
- Provide generation command
- Apply Thinking Framework Step 4 (GENERATE)

### 5. Explain (to user)
- Architecture choices (why this data model, why this pattern)
- Assumptions made
- How to test/use
- Apply Thinking Framework Step 5 (EXPLAIN)

---

## 🚨 HALLUCINATION PREVENTION

**CRITICAL RULE:** NEVER speculate about code structure you have not read

### Examples of Hallucination

❌ **BAD:** "The YAML should have a `commands:` section under `forms:`"
→ Without reading documentation

✅ **GOOD:** "Let me check the YAML structure in the documentation"
→ Read LLM_PATTERNS_ESSENTIAL.md or reference/API_REFERENCE.md → Answer based on docs

### Investigation Protocol

**When user asks about specific feature:**

1. **Acknowledge question:** "Let me verify the exact structure for [feature]"
2. **Read relevant file:** Use Navigation Map to find right doc
3. **Answer based on documentation:** Cite source file
4. **If still uncertain:** Explicitly say "I need to check [specific file]"

### Read-Before-Answer Rule

**Before making claims about:**
- YAML structure → Read LLM_PATTERNS_ESSENTIAL.md or reference/API_REFERENCE.md
- BSL syntax → Read LLM_PRACTICES.md or example files
- Feature availability → Read reference/API_REFERENCE.md
- Error resolution → Read reference/TROUBLESHOOTING.md

---

## ✅ SUCCESS METRICS

**You succeed when:**

- ✅ Generated YAML passes schema validation
- ✅ Generated BSL compiles without errors (if using --output-format epf)
- ✅ No Ukrainian letters (і ї є ґ) in identifiers
- ✅ No reserved keywords in handler names
- ✅ Pattern matches user's workflow (simple task → simple pattern)
- ✅ User can run generation command successfully
- ✅ Processor opens and functions correctly in 1C:Enterprise

**Quality indicators:**

- 🎯 **Appropriate complexity:** Simple task → simple solution (don't over-engineer)
- 📝 **Clear explanations:** User understands WHY you chose this architecture
- 🧹 **Clean code:** Follows naming conventions, validation patterns, error handling
- ⚡ **Efficient:** Minimal YAML/BSL to achieve goal (DRY principle)

---

## 🎨 PHASE 2: UI EXCELLENCE (After Basic Generation)

**When to apply**: After generating a functional processor, transform it into a **visually stunning, professional interface**.

### The Two-Phase Approach

**Phase 1: Functionality** (this guide + LLM_PATTERNS_ESSENTIAL.md)
- ✅ Generate working processor with correct data structures
- ✅ Implement business logic and workflows
- ✅ Use canonical UI patterns (Simple Form, Report, Master-Detail)
- **Result:** Functional but basic UI

**Phase 2: UI Excellence** (apply beautification)
- ✨ Add professional typography (bold headers, visual hierarchy)
- 🎨 Apply icon system (130+ StdPicture icons for all commands)
- 📐 Enhance layout (Pages, UsualGroup, alignment)
- 📊 Polish tables (ColumnGroup multi-level headers, CommandBarLocation)
- **Result:** Production-ready, visually stunning interface

---

### Quick Beautification Checklist

Apply these 8 steps to transform basic processor into professional UI:

#### 1. Typography Hierarchy
- [ ] Add `LabelDecoration` with `font.bold: true, size: 12` for main section headers
- [ ] Use `font.bold: true` for subsection headers
- [ ] Apply `font.bold + italic` for warnings and alerts
- [ ] Use `font.bold: true` on result/total fields (read-only calculations)

```yaml
# Before: plain text
- type: InputField
  name: Field1

# After: with section header
- type: LabelDecoration
  name: SectionHeader
  title_ru: "📊 Основні дані"
  font:
    bold: true
    size: 12
- type: InputField
  name: Field1
```

---

#### 2. Icon System
- [ ] ALL commands have `picture: StdPicture.XXX` (see VALID_PICTURES.md)
- [ ] Action buttons use correct icons:
  - Execute → `StdPicture.ExecuteTask`
  - Save → `StdPicture.Write`
  - Refresh → `StdPicture.Refresh`
  - Delete → `StdPicture.Delete`
- [ ] Report commands use `GenerateReport`, `Print`, or `Report`
- [ ] File operations use `OpenFile`, `SaveFile`

```yaml
# Before: text-only button
commands:
  - name: Execute
    title_ru: Виконати
    handler: Execute

# After: with icon
commands:
  - name: Execute
    title_ru: Виконати
    picture: StdPicture.ExecuteTask    # Auto PictureAndText representation
    handler: Execute
```

---

#### 3. Layout Organization
- [ ] Complex forms (10+ fields) use `Pages` with `pages_representation: TabsOnTop`
- [ ] Related fields grouped with `UsualGroup`
- [ ] Groups use `representation: WeakSeparation` or `NormalSeparation`
- [ ] Advanced/optional fields use `behavior: Collapsible`
- [ ] Action buttons grouped with `ButtonGroup` (horizontal)

```yaml
# Before: flat list of fields
elements:
  - type: InputField
    name: Field1
  - type: InputField
    name: Field2
  # ... 10 more fields

# After: organized with Pages + Groups
elements:
  - type: Pages
    name: MainPages
    pages_representation: TabsOnTop
    pages:
      - name: DataPage
        title_ru: Дані
        child_items:
          - type: UsualGroup
            name: MainDataGroup
            representation: WeakSeparation
            elements:
              - type: InputField
                name: Field1
```

---

#### 4. Table Excellence
- [ ] Tables on **separate Pages** (not mixed with input fields)
- [ ] Use `ColumnGroup` for multi-level headers (financial reports, grouped data)
- [ ] Financial columns use `horizontal_align: Right`
- [ ] Headers use `horizontal_align: Center`
- [ ] Tables have `command_bar_location: Bottom`
- [ ] Tables have proper `height: 10-15`
- [ ] Total/summary columns use `font.bold: true`

```yaml
# Before: simple table
- type: Table
  name: Results
  elements:
    - type: LabelField
      name: Amount

# After: professional table with multi-level headers
- type: Pages
  pages:
    - name: ResultsPage
      title_ru: Результати
      child_items:
        - type: Table
          name: Results
          command_bar_location: Bottom
          height: 15
          elements:
            - type: ColumnGroup
              name: AmountsGroup
              title_ru: "Суми"
              horizontal_align: Right
              elements:
                - type: LabelField
                  name: AmountField
                  attribute: Amount
                  horizontal_align: Right
                  font:
                    bold: true
```

---

#### 5. Alignment & Spacing
- [ ] Financial/numeric fields: `horizontal_align: Right`
- [ ] Table headers: `horizontal_align: Center`
- [ ] Text fields: `horizontal_align: Left` (default)
- [ ] Use `auto_max_width: true` for dynamic content
- [ ] Multi-line fields use `auto_max_height: true` (v2.36.0+)

---

#### 6. Modern UX Features
- [ ] Descriptions use `multi_line: true` + `height: 5`
- [ ] Passwords use `password_mode: true`
- [ ] Help links use `hyperlink: true` on LabelDecoration
- [ ] Result fields use `read_only: true`
- [ ] Catalog fields use `choice_mode: QuickChoice` (v2.36.0+)
- [ ] Add `input_hint_ru` placeholders for guidance

```yaml
# Modern UX enhancements
- type: InputField
  name: DescriptionField
  attribute: Description
  multi_line: true              # Multi-line text area
  height: 5                     # 5 visible lines
  input_hint_ru: "Введіть опис"  # Placeholder

- type: InputField
  name: PasswordField
  attribute: Password
  password_mode: true           # Masked input
```

---

#### 7. Form-Level Settings
- [ ] Modal dialogs use `WindowOpeningMode: LockOwnerWindow`
- [ ] Wizard forms use `CommandBarLocation: Bottom`
- [ ] Filter forms use both modal + bottom buttons

```yaml
forms:
  - name: FilterForm
    properties:
      WindowOpeningMode: LockOwnerWindow    # Modal dialog
      CommandBarLocation: Bottom            # Buttons at bottom
```

---

#### 8. Final Polish
- [ ] All text uses proper language suffixes (`title_ru`, `title_uk`, `title_en`)
- [ ] Tooltips added where helpful (`tooltip_ru`)
- [ ] Icons match action semantics (don't use `CheckMark` for "Execute")
- [ ] No visual clutter (use collapsible sections for advanced options)
- [ ] Consistent spacing (UsualGroup separators)

---

### When to Apply UI Excellence

**ALWAYS apply** when:
- User explicitly requests "beautiful", "professional", "modern", "polished" UI
- Complex forms with 10+ fields
- Reports and dashboards
- Multi-step wizards
- Production-ready processors

**OPTIONAL** for:
- Quick prototypes
- Internal utilities
- Simple calculators with 2-3 fields

---

### Full Guide

For comprehensive UI excellence guide with:
- Typography mastery (font hierarchy, visual design principles)
- Icon selection matrix (130+ icons by use case)
- Layout patterns (Pages, nested groups, alignment rules)
- Table excellence (ColumnGroup, multi-level headers, professional reports)
- Before/After transformation examples (see the difference)
- Real-world examples (perfect_form_example)

**Read:** [docs/UI_EXCELLENCE_GUIDE.md](UI_EXCELLENCE_GUIDE.md) (~950 lines)

---

## 📖 Next Steps

**Based on your task, read the relevant guides:**

| Task Type | Read This |
|-----------|-----------|
| **Data model questions** | [LLM_DATA_GUIDE.md](LLM_DATA_GUIDE.md) |
| **UI pattern selection** | [LLM_PATTERNS_ESSENTIAL.md](LLM_PATTERNS_ESSENTIAL.md) |
| **Table styling (heights, fonts)** | [reference/TABLE_STYLING.md](reference/TABLE_STYLING.md) |
| **Conditional row coloring** | [reference/CONDITIONAL_APPEARANCE.md](reference/CONDITIONAL_APPEARANCE.md) |
| **BSP print forms** | [LLM_BSP_PRINT_FORMS.md](LLM_BSP_PRINT_FORMS.md) |
| **HTML/CSS/JS interfaces** | [LLM_HTML_GUIDE.md](LLM_HTML_GUIDE.md) |
| **Code quality & style** | [LLM_PRACTICES.md](LLM_PRACTICES.md) |
| **Full pattern library** | [reference/ALL_PATTERNS.md](reference/ALL_PATTERNS.md) |
| **Complete YAML API** | [reference/API_REFERENCE.md](reference/API_REFERENCE.md) |
| **Troubleshooting errors** | [reference/TROUBLESHOOTING.md](reference/TROUBLESHOOTING.md) |
| **Quick lookup** | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |

---

**Last updated:** 2026-01-03
**Optimized for:** Claude Sonnet 4.5, GPT-4 Turbo, and other frontier LLMs
**Generator version:** 2.69.0+ (Compact Multilang Syntax, ConditionalAppearance, Table Styling)
