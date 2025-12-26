# Advanced Features Guide

**Target:** LLMs and developers implementing complex scenarios
**Core guide:** [LLM_CORE.md](../LLM_CORE.md)

---

## 📦 ObjectModule (v2.7.4+)

### Overview

**ObjectModule** allows custom business logic callable from forms via `Объект.MethodName()`.

**Use when:**
- ✅ Reusable logic shared between multiple forms
- ✅ Server-side heavy calculations
- ✅ Business rules (validation, calculations, transformations)
- ✅ Exportable procedures/functions

**Don't use when:**
- ❌ Form-specific UI code (use form handlers)
- ❌ Client-side operations

### Required Structure

```bsl
#Если Сервер Или ТолстыйКлиентОбычноеПриложение Или ВнешнееСоединение Тогда

#Область ПрограммныйИнтерфейс

Функция Calculate(Parameters) Экспорт
    // Public API - callable from forms
    Result = InternalCalculation(Parameters);
    Возврат Result;
КонецФункции

#КонецОбласти

#Область СлужебныеПроцедурыИФункции

Функция InternalCalculation(Parameters)
    // Private implementation
    Возврат Новый Структура("Result", 42);
КонецФункции

#КонецОбласти

#Иначе
 ВызватьИсключение НСтр("ru='Недопустимый вызов объекта на клиенте.';uk='Неприпустимий виклик об`єкту на клієнтові.'");
#КонецЕсли
```

### YAML Configuration

```yaml
processor:
  name: Calculator

object_module:
  file: object_module.bsl  # Path to ObjectModule file

forms:
  - name: Форма
    default: true

    commands:
      - name: Calculate
        handler: Calculate
```

### Calling from Forms

```bsl
// Form handler
&НаСервере
Процедура CalculateНаСервере()
    // Call ObjectModule method
    Результат = Объект.Calculate(Parameters);
    Объект.Result = Результат.Result;
КонецПроцедуры
```

### Validation

Generator validates:
- ❌ Empty file
- ❌ BSL reserved keywords in procedure names
- ❌ Ukrainian letters in procedure names
- ⚠️ Missing `#Если Сервер` wrapper (warning)
- ⚠️ Missing regions (warning)

**See also:** Example in `examples/yaml/calculator_with_object_module/`

---

## 🔗 DynamicList Advanced (v2.6.0+)

### Overview

**DynamicList** provides live database queries with auto-refresh capabilities.

**Three modes:**

1. **Auto-query** (MainTable only) - Simple
2. **Manual query + MainTable** - Complex with DynamicDataRead
3. **Manual query only** - Static query

### Smart Stub Generator (v2.49.0+)

**Problem:** DynamicList with columns referencing Document/Catalog fields (like `СписокДокументов.Дата`) fails EPF compilation because Designer validates DataPath against stub metadata.

**Solution:** Generator auto-parses `query_text`, extracts fields from SELECT, infers types, and generates stubs with matching `<Attribute>` elements.

**How it works:**
```yaml
dynamic_lists:
  - name: PaymentsList
    main_table: Document.Payment
    manual_query: true
    query_text: |
      ВЫБРАТЬ
        Payment.Ссылка КАК Ссылка,
        Payment.Дата КАК Дата,
        Payment.Сумма КАК Сумма,
        Payment.Организация КАК Организация,
        Payment.Контрагент КАК Контрагент
      ИЗ
        Документ.Payment КАК Payment
```

**Generator automatically:**
1. Parses SELECT fields (`Сумма`, `Организация`, `Контрагент`)
2. Skips standard fields (`Ссылка`, `Дата`, `Номер`, `Проведен`)
3. Infers types from names (`Сумма` → number, `*Дата*` → date)
4. Generates stub Document.Payment with `<Attribute>` elements
5. EPF compiles successfully

**Type inference rules:**
| Pattern | Type | Example |
|---------|------|---------|
| `*Сумма*`, `*Количество*`, `*Курс*` | number (15,2) | Сумма, КоличествоПлатежей |
| `*Дата*`, `*Date*` | dateTime | ДатаОплаты, StartDate |
| Default | string (unlimited) | Контрагент, Организация |

**Fallback option:**
```yaml
dynamic_lists:
  - name: ComplexList
    skip_stub_validation: true  # Disable smart stubs
```

**Use `skip_stub_validation: true` when:**
- CASE expressions in SELECT
- UNION queries
- Complex subqueries
- Nested field access (`Контрагент.Наименование`)

### Mode 1: Auto-Query (Simplest)

**Use when:** Display all fields from single database table

```yaml
dynamic_lists:
  - name: OrdersList
    main_table: Document.Order  # Auto-generates query
    # manual_query: false (default)
```

**Result:** Shows all Document.Order fields automatically

### Mode 2: Manual Query + MainTable

**Use when:** Complex query with filters, CASE WHEN, JOINs

```yaml
dynamic_lists:
  - name: PaymentsList
    main_table: Document.Payment  # Enables DynamicDataRead=true
    manual_query: true

    query_text: |
      ВЫБРАТЬ
        Payment.Ref,
        Payment.Date,
        Payment.Number,
        ВЫБОР
          КОГДА Payment.Type = ЗНАЧЕНИЕ(Enum.PaymentType.ToEmployee)
          ТОГДА Payment.Employee
          ИНАЧЕ Payment.Contractor
        КОНЕЦ КАК Recipient,
        Payment.Amount
      ИЗ
        Document.Payment КАК Payment
      ГДЕ
        Payment.Date МЕЖДУ &StartDate И &EndDate

    use_always_fields:  # Always loaded (required for row selection)
      - Ref            # WITHOUT list name prefix in YAML
      - BankAccount    # Generator adds prefix automatically

    columns:
      - field: Date
        title_ru: Дата
        width: 12
      - field: Number
        title_ru: Номер
        width: 8
```

**Key points:**
- `main_table` present → `DynamicDataRead: true` (live connection)
- `use_always_fields` WITHOUT prefix (generator adds it)
- Requires Table element on form with `is_dynamic_list: true`

### Mode 3: Manual Query Only

**Use when:** Static query (no live updates)

```yaml
dynamic_lists:
  - name: StaticReport
    manual_query: true
    # NO main_table → DynamicDataRead: false

    query_text: |
      ВЫБРАТЬ
        "Static value" КАК Field1
```

**Result:** Query runs once, no live updates

### UseAlways Fields

**Purpose:** Fields loaded even if not visible (required for row selection, drill-down)

**Rules:**
1. Only valid when `main_table` specified (otherwise removed with warning)
2. Requires Table element on form
3. Specify WITHOUT list name prefix in YAML

**Example:**
```yaml
dynamic_lists:
  - name: MyList
    main_table: Document.Order
    use_always_fields:
      - Ref          # ✅ In YAML
      - Contractor   # ✅ In YAML

# Generated XML uses prefix:
# MyList.Ref, MyList.Contractor
```

### Displaying DynamicList

**CRITICAL:** Must use Table element with `is_dynamic_list: true` under `properties:`

```yaml
elements:
  - type: Table
    name: PaymentsTable
    tabular_section: PaymentsList  # References dynamic_lists name
    properties:
      is_dynamic_list: true  # ⚠️ MUST be under properties!
```

**Common mistake:**
```yaml
❌ WRONG:
- type: Table
  name: PaymentsTable
  is_dynamic_list: true  # ❌ Top-level doesn't work
```

**See also:** [ALL_PATTERNS.md](ALL_PATTERNS.md) Pattern 3

---

## ⏳ Background Jobs / Long Operations (v2.17.0+)

### Overview

**Background Jobs** run long operations with progress feedback without freezing UI.

**Generator auto-creates 4 handlers from 1-3 user-written handlers:**
1. **Button handler** (client) - starts operation
2. **Start in background** (server) - initiates background job
3. **Completion handler** (client) - processes result
4. **Server logic** (server) - actual business logic

### YAML Configuration

```yaml
forms:
  - name: Форма

    commands:
      - name: ProcessData
        title_ru: Обработать данные
        handler: ProcessData
        long_operation: true  # ✅ Enables background job

        # Optional parameters (defaults shown):
        long_operation_params:
          wait_completion: 2             # Initial wait (sec)
          timeout: 300                   # Max duration (sec)
          show_progress_window: true     # Show progress dialog
          show_messages: false           # Show messages in progress
          use_progress_bar: false        # % progress bar
          title_ru: "Обработка данных"   # Progress window title
```

### User Writes (1-3 handlers)

**1. Server logic** (required):
```bsl
// handlers/ProcessDataНаСервере.bsl
Выборка = Query.Execute().Выбрать();
Всего = Выборка.Количество();
Счетчик = 0;

Пока Выборка.Следующий() Цикл
    // Process row
    ProcessRow(Выборка);

    Счетчик = Счетчик + 1;

    // Update progress (optional)
    Процент = Счетчик / Всего * 100;
    ДлительныеОперации.СообщитьПрогресс(Процент,
        СтрШаблон("Обработано %1 из %2", Счетчик, Всего));
КонецЦикла;
```

**2. Pre-validation** (optional):
```bsl
// handlers/ProcessDataПроверкаПередЗапуском.bsl
Если Объект.Lines.Количество() = 0 Тогда
    Сообщить("Нет данных для обработки!");
    Возврат Ложь;  # Blocks background job
КонецЕсли;

Возврат Истина;  # Allows start
```

**3. Result processing** (optional):
```bsl
// handlers/ProcessDataОбработкаРезультата.bsl
Если Результат.Статус = "Выполнено" Тогда
    Сообщить("Обработка завершена!");
    LoadResults();  # Refresh UI
Иначе
    Сообщить("Ошибка: " + Результат.Сообщение);
КонецЕсли;
```

### Generator Auto-Creates

**1. Button handler:**
```bsl
&НаКлиенте
Процедура ProcessData(Команда)
    ПараметрыОжидания = ДлительныеОперацииКлиент.ПараметрыОжидания(ЭтаФорма);
    ПараметрыОжидания.ВыводитьОкноОжидания = Истина;
    # ... auto-generated boilerplate ...
КонецПроцедуры
```

**2. Start in background:**
```bsl
&НаСервере
Функция ProcessDataЗапуститьВФоне()
    ПараметрыВыполнения = ДлительныеОперации.ПараметрыВыполненияВФоне(УникальныйИдентификатор);
    # ... auto-generated boilerplate ...
    Возврат ДлительныеОперации.ВыполнитьВФоне(...);
КонецФункции
```

**3. Completion handler:**
```bsl
&НаКлиенте
Процедура ProcessDataЗавершение(Результат, ДополнительныеПараметры) Экспорт
    # ... auto-generated result handling ...
КонецПроцедуры
```

**Total generated:** ~79 lines of boilerplate from 20-30 lines of user code

**See also:** Example in `examples/yaml/long_operation_simple/`

---

## 🏛️ Configuration Mode (v2.10.0+)

### Overview

**Configuration mode** generates minimal Configuration.xml with metadata (catalogs, documents) for processors using complex types.

**Auto-activates when:**
1. Processor uses `CatalogRef.*` or `DocumentRef.*` types, OR
2. Validation configured in YAML (`validation:` section)

### Automatic CatalogRef/DocumentRef Detection

**Example:**
```yaml
attributes:
  - name: User
    type: CatalogRef.Users  # ← Triggers Configuration mode

  - name: Order
    type: DocumentRef.Order
```

**Generator automatically:**
1. Detects required metadata (Users catalog, Order document)
2. Creates Configuration.xml with minimal metadata
3. Generates processor in Configuration (not standalone)
4. Compiles to EPF with metadata references

**Variant A Architecture:** Configuration contains **only metadata**, not processor itself

---

## 📄 FormAttributes (v2.15.1+)

### Overview

**FormAttributes** are form-level attributes for types that **cannot** be processor attributes.

**Use when:**
- SpreadsheetDocument (formatted reports)
- BinaryData (file handling)

### SpreadsheetDocument Example

```yaml
forms:
  - name: Форма

    form_attributes:  # ✅ Form-level
      - name: Report
        type: spreadsheet_document  # Cannot be processor attribute
        synonym_ru: Отчет

    elements:
      - type: SpreadSheetDocumentField
        name: ReportField
        attribute: Report  # References form_attributes.name
```

**Key difference:**
```yaml
❌ WRONG (v2.15.0):
attributes:  # Processor-level
  - name: Report
    type: spreadsheet_document  # ERROR: Not valid processor type

✅ CORRECT (v2.15.1+):
forms:
  - name: Форма
    form_attributes:  # Form-level
      - name: Report
        type: spreadsheet_document  # ✅ Valid form type
```

### DetailProcessing Event

**Use when:** User double-clicks cell in SpreadsheetDocument (drill-down)

```yaml
elements:
  - type: SpreadSheetDocumentField
    name: ReportField
    attribute: Report
    events:
      DetailProcessing: ReportDetailProcessing
```

```bsl
&НаКлиенте
Процедура ReportDetailProcessing(Элемент, Расшифровка, СтандартнаяОбработка)
    СтандартнаяОбработка = Ложь;  # Block default behavior

    # Custom drill-down logic
    Если ТипЗнч(Расшифровка) = Тип("ДокументСсылка.Заказ") Тогда
        ОткрытьЗначение(Расшифровка);  # Open document form
    КонецЕсли;
КонецПроцедуры
```

---

## ✅ Validation Configuration (v2.12.0+)

### Overview

**Validation** performs BSL syntax and semantic checks during EPF generation.

**Two types:**
1. **Синтаксична перевірка** (syntax) - Always enabled (fast, ~5-10 sec)
2. **Семантична перевірка** (semantic) - Opt-in (deep, ~15-30 sec)

### Синтаксична перевірка (Default)

**Validates:**
- ✅ BSL syntax errors
- ✅ Unknown methods/functions
- ✅ Incorrect parameters

**Always runs** when `--output-format epf` (no configuration needed)

### Семантична перевірка (Opt-In)

**Validates:**
- ✅ Empty handlers (performance issue)
- ✅ Unreferenced procedures (dead code)
- ✅ Incorrect references (missing forms/commands)
- ✅ Handler existence

**Requires YAML configuration:**

```yaml
validation:
  semantic_check_enabled: true      # Enable semantic validation

  # Optional: Семантична перевірка parameters (defaults shown)
  check_web_client: false         # Check WebClient compatibility
  check_extended_modules: false   # Extended type checks
  check_config_parameters:
    - ThinClient                  # Check ThinClient compatibility
    - ManagedApplication          # Check managed forms
```

### Full Configuration Example

```yaml
processor:
  name: MyProcessor

validation:
  # Синтаксична перевірка (always enabled, these are defaults)
  syntax_check_enabled: true
  check_use_module_strict_mode: false
  check_modules_parameters: []

  # Семантична перевірка (opt-in)
  semantic_check_enabled: true
  check_web_client: true
  check_extended_modules: true
  check_config_parameters:
    - ThinClient
    - WebClient
    - ManagedApplication
```

### Ignoring Validation Errors

**CLI flag:**
```bash
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --output-format epf \
  --ignore-validation-errors  # Force compile despite errors
```

**Use cases:**
- Development/testing (known issues)
- Incomplete metadata (Configuration mode limitations)

**See also:** docs/VALIDATION_GUIDE.md (700+ lines, comprehensive)

---

## 🖼️ Multiple Forms (v2.6.0+)

### Overview

**Multiple forms** support separate windows (settings, wizards, dialogs).

**Use when:**
- Settings/configuration dialogs
- About/Help windows
- Additional data entry forms
- Preview/Details windows

**Don't use when:**
- Sequential steps in same window (use Pages)
- Tabs with related data (use Pages)

### YAML Structure

```yaml
forms:
  # Main form
  - name: Форма
    default: true  # ✅ Mark one form as default

    elements: [...]
    commands: [...]

  # Settings form
  - name: Настройки
    default: false

    properties:
      title_ru: Настройки
      WindowOpeningMode: LockOwnerWindow  # Modal dialog

    elements: [...]
    commands: [...]
```

### Opening Forms from BSL

```bsl
&НаКлиенте
Процедура OpenSettings(Команда)
    // Open modal settings form
    ОткрытьФорму(
        "ВнешняяОбработка." + ЭтаФорма.ИмяФормы + ".Форма.Настройки",
        ,  # No parameters
        ЭтаФорма  # Owner form
    );
КонецПроцедуры
```

### Per-Form handlers_dir

```yaml
forms:
  - name: Форма
    handlers_dir: handlers_main

  - name: Настройки
    handlers_dir: handlers_settings
```

**Directory structure:**
```
my_processor/
├── config.yaml
├── handlers_main/
│   ├── Command1.bsl
│   └── Command2.bsl
└── handlers_settings/
    ├── Save.bsl
    └── Close.bsl
```

---

## 🧪 Automated Testing Framework (v2.16.0+, PRODUCTION READY v2.21.0+)

### Overview

**Testing Framework** provides automated testing for EPF files through COM-based execution in 1C.

**Evolution timeline:**
- v2.16.0 - Initial release (pytest conflict issue)
- v2.16.1 - Standalone test runner (✅ COM works)
- v2.18.0 - ABC Architecture (BaseConnection)
- v2.19.0 - Automation Server Support (❌ NOT POSSIBLE - see v2.24.0)
- v2.20.0 - Extended Assertions (12+ types)
- v2.21.0 - Fixtures Support (**PRODUCTION READY**)
- v2.22.0 - Quality improvements (DRY refactoring)
- v2.23.2 - Test Framework Architecture Redesign
- v2.24.0 - Documented Automation Server COM limitation

**Use when:**
- ✅ Automated regression testing
- ✅ CI/CD pipeline integration
- ✅ Command validation (declarative)
- ✅ Complex business logic testing (procedural)
- ❌ UI testing (NOT AVAILABLE - COM limitation, see docs/research/V83_INVESTIGATION_REPORT.md)

### ⚠️ WARNING: Testing Framework Updated to v2.23.2

**The format shown below is OUTDATED (v2.16.0)**. The testing framework was completely redesigned in v2.23.2.

**For current documentation, see:**
- `docs/LLM_TESTING_WORKFLOW.md` - Step-by-step workflow (recommended)
- `examples/yaml/calculator_with_tests/` - Working example
- `examples/yaml/table_test_example/` - Form testing example

### New Architecture (v2.23.2+)

The new format uses **separate sections** for ObjectModule and Form tests:

```yaml
# ObjectModule tests - External Connection (fast, no UI)
objectmodule_tests:
  declarative:
    - name: test_addition
      setup:
        attributes:
          Number1: 5
          Number2: 3
      execute_command: Calculate
      assert:
        attributes:
          Result: 8

  procedural:
    file: objectmodule_tests.bsl
    procedures: [Тест_Calculation]

# Form tests - Automation Server (slow, with UI)
forms:
  - name: Форма  # ← Form name required
    procedural:
      file: form_tests.bsl
      procedures: [Тест_FormButton]
```

### ❌ OLD Format (v2.16.0 - DO NOT USE)

The examples below are **deprecated** and will NOT work with v2.23.2+:

```yaml
# ❌ DEPRECATED - DO NOT USE
tests:
  declarative:
    - name: "Add two numbers"
      command: Calculate
      ...

# ❌ DEPRECATED - DO NOT USE
tests:
  procedural:
    - name: "Complex validation test"
      file: tests/test_validation.bsl
```

### YAML Configuration (tests.yaml)

**Full structure:**

```yaml
processor:
  name: Calculator
  file: processors/Calculator/Calculator.epf

connection:
  type: External  # External (fast) or Automation (UI testing)
  connection_string: "File=\"C:/temp_ib\";"

fixtures:
  default_numbers:
    Number1: 10
    Number2: 20
  zero_values:
    Number1: 0
    Number2: 0

tests:
  declarative:
    - name: "Add positive numbers"
      command: Calculate
      fixture: default_numbers  # Reuse fixture
      assertions:
        - field: Result
          operator: eq
          expected: 30

    - name: "Handle zero values"
      command: Calculate
      fixture: zero_values
      assertions:
        - field: Result
          operator: eq
          expected: 0

  procedural:
    - name: "Complex business logic"
      file: tests/test_complex.bsl
      timeout: 60
```

### Fixtures System (v2.21.0+)

**Purpose:** Reusable test setup data (DRY principle)

**Define fixtures:**
```yaml
fixtures:
  valid_user:
    UserName: "TestUser"
    Email: "test@example.com"

  admin_user:
    UserName: "Admin"
    Email: "admin@example.com"
    Role: "Administrator"
```

**Use in tests:**
```yaml
tests:
  declarative:
    - name: "Create valid user"
      command: CreateUser
      fixture: valid_user  # ← Reuses fixture data

    - name: "Create admin"
      command: CreateUser
      fixture: admin_user
```

**Benefits:**
- ✅ DRY (Don't Repeat Yourself)
- ✅ Centralized test data management
- ✅ Easy to update (change once, affects all tests)

### Extended Assertions (v2.20.0+)

**12+ assertion types for flexible testing:**

#### Equality Assertions
```yaml
- field: Result
  operator: eq      # Equal
  expected: 42

- field: Status
  operator: ne      # Not equal
  expected: "Error"
```

#### Numeric Assertions
```yaml
- field: Amount
  operator: gt      # Greater than
  expected: 100

- field: Discount
  operator: lt      # Less than
  expected: 50

- field: Total
  operator: gte     # Greater than or equal
  expected: 1000

- field: Tax
  operator: lte     # Less than or equal
  expected: 20

- field: Price
  operator: between
  expected: [10, 100]  # Between 10 and 100
```

#### String Assertions
```yaml
- field: Email
  operator: matches
  expected: "^[a-z]+@[a-z]+\\.[a-z]+$"  # Regex

- field: Name
  operator: starts_with
  expected: "Test"

- field: FileName
  operator: ends_with
  expected: ".xml"

- field: Description
  operator: length
  expected: 100  # Exactly 100 characters
```

#### Type Assertions
```yaml
- field: User
  operator: type
  expected: "CatalogRef.Users"

- field: OptionalField
  operator: is_null
  expected: true

- field: RequiredField
  operator: not_null
  expected: true
```

#### Collection Assertions
```yaml
- field: Status
  operator: in
  expected: ["Active", "Pending", "Completed"]

- field: ErrorCode
  operator: not_in
  expected: [0, 200, 201]
```

### Connection Types

**1. External Connection (Default - Fast)**

```yaml
connection:
  type: External  # V83.COMConnector
  connection_string: "File=\"C:/temp_ib\";"
```

**Pros:**
- ✅ Fast (headless, no UI)
- ✅ No security warning (uses temp_ib from compilation)
- ✅ Perfect for command testing

**Cons:**
- ❌ Can't test UI interactions (buttons, fields)
- ❌ Can't capture form messages

---

**2. ❌ Automation Server - NOT AVAILABLE**

**⚠️ CRITICAL: Automation Server cannot be implemented (v2.23.2+)**

After extensive COM investigation (2025-11-18), form testing via V83.Application is technically impossible due to fundamental COM limitations.

**Why it doesn't work:**
- ❌ V83.Application inaccessible from Python (RPC_E_DISCONNECTED)
- ❌ PowerShell Connect() succeeds but object is hollow
- ❌ V83.COMConnector.ПолучитьФорму() fails ("Интерактивные операції недоступні")
- ❌ External Connection is headless by design

**What this means:**
- ❌ Form testing not possible
- ❌ UI interaction testing not available
- ❌ `forms[]` section in tests.yaml will not execute
- ✅ Use External Connection (ObjectModule tests) instead

**Intended use (not possible):**
```yaml
connection:
  type: Automation  # ← This type DOES NOT WORK
```

**Alternative: Use ObjectModule tests**
- ✅ Fast, reliable testing via External Connection
- ✅ Full business logic coverage
- ✅ Command execution, data validation
- ❌ No UI access (use manual testing for forms)

**See:** `docs/research/V83_INVESTIGATION_REPORT.md`

### Declarative Tests Example

```yaml
processor:
  name: Calculator
  file: processors/Calculator/Calculator.epf

connection:
  type: External
  connection_string: "File=\"C:/temp_ib\";"

fixtures:
  positive_numbers:
    Number1: 5
    Number2: 3

  negative_numbers:
    Number1: -10
    Number2: -5

tests:
  declarative:
    - name: "Add positive numbers"
      command: Calculate
      fixture: positive_numbers
      assertions:
        - field: Result
          operator: eq
          expected: 8
        - field: Result
          operator: gt
          expected: 0

    - name: "Add negative numbers"
      command: Calculate
      fixture: negative_numbers
      assertions:
        - field: Result
          operator: eq
          expected: -15
        - field: Result
          operator: lt
          expected: 0

    - name: "Validate required fields"
      command: Calculate
      setup:
        Number1: null  # Empty field
      assertions:
        - field: ErrorMessage
          operator: starts_with
          expected: "Заполните"
```

### Procedural Tests Example

**tests.yaml:**
```yaml
tests:
  procedural:
    - name: "Complex calculation validation"
      file: tests/test_calculation.bsl
      timeout: 30
```

**tests/test_calculation.bsl:**
```bsl
// Test procedure - full BSL access
Процедура ТестСложногоРасчета(Обработка, Результат) Экспорт
    // Setup
    Обработка.Number1 = 100;
    Обработка.Number2 = 50;

    // Execute command
    Обработка.Calculate();

    // Validate result
    Если Обработка.Result <> 150 Тогда
        Результат.Успех = Ложь;
        Результат.Сообщение = "Ожидалось 150, получено " + Обработка.Result;
        Возврат;
    КонецЕсли;

    // Complex validation
    Если Обработка.Result > 200 Тогда
        Результат.Успех = Ложь;
        Результат.Сообщение = "Результат превышает максимум";
        Возврат;
    КонецЕсли;

    // Success
    Результат.Успех = Истина;
    Результат.Сообщение = "Тест пройден";
КонецПроцедуры
```

### Running Tests

**Standalone test runner (v2.16.1+):**

```bash
# Run all tests
python test_runner.py tests.yaml

# Run with verbose output
python test_runner.py tests.yaml --verbose

# Run specific test
python test_runner.py tests.yaml --test "Add positive numbers"
```

**Output:**
```
Running tests for: Calculator
Connection: External (File="C:/temp_ib";)

✓ Add positive numbers (0.5s)
✓ Add negative numbers (0.4s)
✓ Validate required fields (0.3s)
✓ Complex calculation validation (1.2s)

4 passed, 0 failed (2.4s total)
```

### Architecture (v2.18.0+)

**ABC Design Pattern:**

```
BaseConnection (ABC)
    ├── ExternalConnection (V83.COMConnector)
    └── AutomationServerConnection (V83.Application)

EPFTester
    ├── Receives connection via dependency injection
    ├── Executes declarative tests
    ├── Executes procedural tests
    └── Validates assertions
```

**Benefits:**
- ✅ Clean separation of concerns
- ✅ Easy to add new connection types
- ✅ Testable (dependency injection)
- ✅ Zero technical debt (v2.18.0+)

### Security (v2.22.0+)

**Path traversal protection:**

```yaml
❌ BLOCKED:
tests:
  procedural:
    - file: "../../../etc/passwd"  # Rejected

✅ ALLOWED:
tests:
  procedural:
    - file: "tests/my_test.bsl"    # Safe
```

**All paths validated** to prevent directory traversal attacks.

### Example: Complete Testing Workflow

**1. Create tests.yaml:**
```yaml
processor:
  name: OrderProcessor
  file: processors/OrderProcessor/OrderProcessor.epf

connection:
  type: External
  connection_string: "File=\"C:/temp_ib\";"

fixtures:
  valid_order:
    CustomerName: "Test Customer"
    Amount: 1000
    Quantity: 5

tests:
  declarative:
    - name: "Create valid order"
      command: CreateOrder
      fixture: valid_order
      assertions:
        - field: OrderNumber
          operator: not_null
        - field: Total
          operator: eq
          expected: 5000  # Quantity * Amount

  procedural:
    - name: "Validate discount calculation"
      file: tests/test_discount.bsl
      timeout: 30
```

**2. Run tests:**
```bash
python test_runner.py tests.yaml
```

**3. CI/CD integration:**
```bash
# In GitHub Actions / GitLab CI
- name: Run EPF Tests
  run: python test_runner.py tests.yaml
  continue-on-error: false  # Fail build if tests fail
```

### When to Use Testing Framework

**✅ Use when:**
- Implementing critical business logic
- CI/CD pipeline exists
- Regression testing needed
- Multiple developers on team
- Production-ready processors

**❌ Skip when:**
- Quick prototypes
- One-off scripts
- Simple processors (<5 commands)
- No ongoing maintenance

### See Also

- **Example:** `examples/yaml/calculator_with_tests/` (4 declarative + 2 procedural tests)
- **Module:** `1c_processor_generator/testing/epf_tester.py`
- **Documentation:** Testing framework uses temp_ib from compilation (no security warning)

---

## 📚 Summary Table

| Feature | Version | Use When | Complexity |
|---------|---------|----------|------------|
| **ObjectModule** | v2.7.4+ | Reusable business logic | Medium |
| **DynamicList** | v2.6.0+ | Live database queries | Medium-High |
| **Smart Stub Generator** | v2.49.0+ | DynamicList with custom columns | Auto |
| **Background Jobs** | v2.17.0+ | Long operations (>5 sec) | High |
| **Configuration Mode** | v2.10.0+ | CatalogRef/DocumentRef | Auto |
| **FormAttributes** | v2.15.1+ | SpreadsheetDocument | Low |
| **Validation** | v2.12.0+ | Production-ready EPF | Low-Medium |
| **Multiple Forms** | v2.6.0+ | Dialogs, wizards | Low |
| **Testing Framework** | v2.21.0+ | Automated testing, CI/CD | Medium-High |

---

**Last updated:** 2025-12-05
**Generator version:** 2.49.0+
