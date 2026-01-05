# Changelog

All notable changes to 1C Processor Generator will be documented here.

## [2.71.x] - 2026-01-05 - InputField Controls & Table Properties

**InputField Button Controls:**
- `mark_negatives` - Highlight negative numbers in red
- `open_button`, `create_button`, `clear_button` - Control button visibility
- `drop_list_button`, `spin_button` - Additional input controls
- `auto_mark_incomplete` - Mark empty required fields

**Button Properties:**
- `default_button` - Mark as default (activated on Enter)
- `shape_representation` - Button visual style (Auto, None, WhenActive, Always)

**Table Properties:**
- `search_string_location` - Search bar position (None, CommandBar)
- `row_picture_data_path` - DataPath to row icon column
- `selection_mode` - Row selection (SingleRow, MultiRow)

**Other:**
- BSP Integration is now FREE (no license required)
- Type normalization - Auto-fix LLM-generated typos (SpreadsheetDocumentField → SpreadSheetDocumentField)
- form_attributes access validation

## [2.70.x] - 2026-01-05 - Enum Validation & UI Properties

- **ToolTipRepresentation** - Control tooltip display (None, Button, ShowTop, Balloon, etc.)
- **ChoiceButtonRepresentation** - Control choice button placement (Auto, ShowInInputField, ShowInDropList)
- **TabsOnLeftHorizontal** - New pages_representation value for left-side horizontal tabs
- **WindowOpeningMode: Independent** - Non-blocking window opening
- Comprehensive enum validation with "did you mean" suggestions

## [2.69.x] - 2026-01-03 - Compact Syntax

**Compact Multilang Syntax:**
- Pipe format: `title: "Текст | Текст"`
- Array format: `title: ["Текст", "Текст"]`
- Project-level languages: `languages: [ru, uk]`

**Compact choice_list:**
- New short keys: `{v, ru, uk, en, t}` instead of `{value, presentation_ru, ...}`
- ~40% token savings

**Validation:**
- Form element attribute validation
- Python 3.14 compatibility

## [2.68.x] - 2026-01-02 - ConditionalAppearance

- **ConditionalAppearance** - Form-level conditional styling for table rows
  - Highlight error rows, color-code status fields
  - Filter conditions: Equal, NotEqual
  - Appearance: back_color, text_color, font_bold, visible, enabled
- **Table height properties** - height_in_table_rows, header_height, footer_height
- **Font size support** - `font: {size: 20}` with proper height attribute

## [2.66.x] - 2025-12-30 - ObjectModule Regions

- **ObjectModule Region Support** - Write ObjectModule code directly in handlers.bsl
  - Region markers: `#Область МодульОбъекта` / `#Region ObjectModule`
  - Auto-wrapped with server context
- **clear-cache CLI** - `python -m 1c_processor_generator clear-cache`
- **Platform 8.3.15-8.3.19 compatibility** - Fixed Configuration.xml generation

## [2.64.x] - 2025-12-28 - ValueTree Support

- **ValueTree** - Hierarchical tree data support
  - Tree representation mode for Table (`representation: tree`)
  - Tree properties: initial_tree_view, show_root, allow_root_choice
  - Example: JSON tree visualization
- **OnGetDataAtServer event** - For DynamicList row styling
- **Auto-detect XML format version** - Based on installed 1C platform

## [2.63.x] - 2025-12-27 - Excel Templates

- **Excel → MXL Converter** - Auto-convert .xlsx to 1C SpreadsheetDocument format
  - CLI: `python -m 1c_processor_generator excel2mxl input.xlsx -o output.mxl`
  - Named Ranges → MXL areas (Заголовок, СтрокаТаблицы, Подвал)
  - Parameters in cells: `{Наименование}` → MXL parameters
- Optional dependency: `pip install 1c-processor-generator[excel]`

## [2.61.x] - 2025-12-26 - BAF Support

- **BAF Support** - Ukrainian alternative to 1C:Enterprise (Business Automation Framework)
  - Auto-detection in standard paths
  - Works with identical Designer commands
- **Version check notification** - Automatic update notifications
- **Optional dependencies** - svg, excel, all extras

## [2.60.x] - 2025-12-26 - Multi-Python Support

- **Python 3.10-3.14 support** - All modern Python versions
- **Windows x64/x86 support** - Both architectures
- Minimum Python version changed from 3.7 to 3.10

## [2.57.x] - 2025-12-16 - BSP Print Forms

- **BSP Integration** - External Print Forms support
  - `bsp:` section in YAML for BSP-compatible processors
  - Auto-generation of registration functions
  - MXL and Word template support
- **CommonModule stub generation** - Auto-generates BSP module stubs
- **setup-1c CLI** - `python -m 1c_processor_generator setup-1c`

## [2.47.x] - 2025-12-05 - PlannerField

- **PlannerField** - Scheduler/planner widget
  - Dimensions, items, drag-drop support
  - Color-coded items
  - DragCheck and Drag events
- **Smart Stub Generator** - Auto-generates stub attributes from DynamicList query_text
- **HandlerValidator** - Pre-generation validation for BSL handlers

## [2.40.x] - 2025-11-26 - Templates (Макети)

- **Templates support** - HTMLDocument, SpreadsheetDocument
  - Content from external files
  - BSL: `ПолучитьМакет("TemplateName").ПолучитьТекст()`
- **HTMLDocumentField** - Display HTML content in forms
  - OnClick event for hyperlinks
- **Templates Automation** - auto_field, placeholders, assets
- **InputField Styling** - colors, fonts, tooltips
- **CommonPicture stub generation**

## [1.0.0] - 2024-12-13 - Initial Release

**Core Features:**
- YAML configuration for processor definition
- BSL handlers in single file format
- XML generation for 1C:Enterprise 8.3
- EPF compilation (PRO)
- Form elements: InputField, Button, Table, Pages, Groups, Labels, CheckBox, RadioButton
- Tabular sections and ValueTable support
- Client-server architecture with automatic pairing
- Sync tool for bidirectional YAML ↔ XML synchronization

**PRO Features:**
- EPF file generation
- Validation with CheckConfig
- No watermark in generated code

---

For detailed documentation see [docs/](docs/) folder.

*For licensing information visit: https://itdeo.tech/1c-processor-generator*
