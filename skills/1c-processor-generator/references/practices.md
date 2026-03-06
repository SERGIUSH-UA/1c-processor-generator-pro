# 1C Processor Generator - Development Practices

**Target:** LLMs generating 1C processors
**Core guide:** [LLM_CORE.md](LLM_CORE.md)

---

## 🎯 Core Principles

### Principle 1: Explicit Over Implicit

**Why:** 1C platform is strict about metadata — ambiguity causes runtime errors

**Application:**
- ✅ Explicit field names (`ДатаНачалаПоле` not just `Дата1`)
- ✅ Explicit handler names (`LoadDataНаСервере` not just `Load`)
- ✅ Explicit validation messages ("Укажите дату начала" not just "Ошибка")

### Principle 2: Validate Early, Fail Fast

**Why:** Better UX — catch errors before server call, save time

**Application:**
- ✅ Client-side validation before server calls
- ✅ Return immediately on validation failure (`Возврат;`)
- ✅ Clear error messages to user (`Сообщить()`)

### Principle 3: Separation of Concerns

**Why:** Maintainability, performance, 1C architecture

**Application:**
- Client: UI, validation, user feedback
- Server: Database, calculations, business logic
- Clear boundary: Client validates → Server processes

### Principle 4: Convention Over Configuration

**Why:** Consistency, predictability, easier maintenance

**Application:**
- Standard naming: `AttributeПоле`, `AttributeТаблица`
- Standard structure: Filters → Buttons → Results
- Standard events: `OnOpen`, `OnCreateAtServer`

---

## 📝 Naming Conventions

### Processor Name

**Format:** PascalCase in Russian Cyrillic

```yaml
processor:
  name: ОтчетПоПродажам  # ✅ Clear, descriptive, PascalCase
```

**Why Russian Cyrillic?** Platform validation regex: `^[а-яА-ЯёЁa-zA-Z_][а-яА-ЯёЁa-zA-Z0-9_]*$`

**Common mistakes:**
```yaml
❌ otchet_po_prodazham  # Latin + underscores (bad style)
❌ ОтчетПродажи         # Too generic
❌ ПошуковийЗапит       # Ukrainian (contains 'і') - COMPILATION ERROR
```

### Attributes

**Format:** PascalCase descriptive names

```yaml
attributes:
  - name: ДатаНачала      # ✅ StartDate
  - name: ДатаОкончания   # ✅ EndDate
  - name: СуммаИтого      # ✅ TotalAmount
```

**Avoid:**
```yaml
❌ Data1, Data2          # Generic, unclear
❌ d1, d2                # Cryptic abbreviations
❌ дата_начала           # Underscores (bad style)
```

### Form Elements

**Format:** `AttributeName + Type`

```yaml
elements:
  - type: InputField
    name: ДатаНачалаПоле       # Attribute + "Поле"
    attribute: ДатаНачала

  - type: Table
    name: РезультатыТаблица    # Attribute + "Таблица"
    tabular_section: Результаты

  - type: Button
    name: СформироватьКнопка   # Command + "Кнопка"
    command: Сформировать
```

**Why suffix?** Prevents name conflicts, clear type indication

### Commands & Handlers

**Format:** Action verbs (commands), descriptive names (handlers)

```yaml
commands:
  - name: Сформировать               # ✅ Action verb
    handler: СформироватьОтчет       # ✅ Descriptive

  - name: Загрузить
    handler: ЗагрузитьДанныеНаСервере  # ✅ Explicit server handler
```

**Reserved keyword avoidance:**
```yaml
❌ handler: Выполнить      # Reserved keyword → parse error
✅ handler: ВыполнитьОбработку  # Add context → works
```

**See also:** [LLM_CORE.md](LLM_CORE.md) Rule 2 for full reserved keywords list

---

## ✅ Validation Patterns

### Pattern 1: Required Field Validation

```bsl
Если НЕ ЗначениеЗаполнено(Объект.ДатаНачала) Тогда
    Сообщить("Укажите дату начала!");
    Возврат;
КонецЕсли;
```

**Template:**
```bsl
Если НЕ ЗначениеЗаполнено(Объект.<Field>) Тогда
    Сообщить("Заполните <FieldName>!");
    Возврат;
КонецЕсли;
```

### Pattern 2: Date Range Validation

```bsl
Если Объект.ДатаОкончания < Объект.ДатаНачала Тогда
    Сообщить("Дата окончания не может быть меньше даты начала!");
    Возврат;
КонецЕсли;
```

**Template:**
```bsl
Если Объект.<EndDate> < Объект.<StartDate> Тогда
    Сообщить("Дата окончания меньше даты начала!");
    Возврат;
КонецЕсли;
```

### Pattern 3: Numeric Range Validation

```bsl
Если Объект.Количество <= 0 Тогда
    Сообщить("Количество должно быть больше нуля!");
    Возврат;
КонецЕсли;
```

**Template:**
```bsl
Если Объект.<Number> <= <MinValue> Тогда
    Сообщить("<Field> должно быть больше <MinValue>!");
    Возврат;
КонецЕсли;
```

### Pattern 4: Table Not Empty

```bsl
Если Объект.Lines.Количество() = 0 Тогда
    Сообщить("Добавьте хотя бы одну строку!");
    Возврат;
КонецЕсли;
```

**Template:**
```bsl
Если Объект.<Table>.Количество() = 0 Тогда
    Сообщить("Таблица пуста!");
    Возврат;
КонецЕсли;
```

### Pattern 5: Combined Validation (Reusable)

```bsl
&НаКлиенте
Процедура ValidateFilters()
    // Date fields
    Если НЕ ЗначениеЗаполнено(Объект.ДатаНачала) Тогда
        Сообщить("Укажите дату начала!");
        Возврат Ложь;
    КонецЕсли;

    Если НЕ ЗначениеЗаполнено(Объект.ДатаОкончания) Тогда
        Сообщить("Укажите дату окончания!");
        Возврат Ложь;
    КонецЕсли;

    // Date range
    Если Объект.ДатаОкончания < Объект.ДатаНачала Тогда
        Сообщить("Неверный диапазон дат!");
        Возврат Ложь;
    КонецЕсли;

    Возврат Истина;
КонецПроцедуры

&НаКлиенте
Процедура Generate(Команда)
    Если НЕ ValidateFilters() Тогда
        Возврат;  // Validation failed
    КонецЕсли;

    GenerateНаСервере();
    Сообщить("Отчет сформирован!");
КонецПроцедуры
```

**Why reusable validation?** DRY principle, consistent error handling

---

## 🚨 Error Handling

### Principle: Graceful Degradation

**Don't crash — inform user and recover**

### Pattern 1: Try-Catch for External Operations

```bsl
&НаСервере
Процедура ExportToFileНаСервере(FilePath)
    Попытка
        ЗаписьJSON = Новый ЗаписьJSON;
        ЗаписьJSON.ОткрытьФайл(FilePath);
        // ... export logic ...
        ЗаписьJSON.Закрыть();
        Сообщить("Файл экспортирован: " + FilePath);
    Исключение
        Сообщить("Ошибка экспорта: " + ОписаниеОшибки());
    КонецПопытки;
КонецПроцедуры
```

**When to use:**
- File operations (read/write)
- Network requests (API calls)
- External system integration

### Pattern 2: Defensive Coding (Check Before Use)

```bsl
&НаКлиенте
Процедура TableOnActivateRow(Элемент)
    ТекущаяСтрока = Элементы.Table.ТекущиеДанные;

    // ✅ Defensive check
    Если ТекущаяСтрока = Неопределено Тогда
        DetailData.Clear();
        Возврат;
    КонецЕсли;

    // Safe to use ТекущаяСтрока
    LoadDetailsНаСервере(ТекущаяСтрока.ID);
КонецПроцедуры
```

**Always check for:**
- `Неопределено` (Undefined) before accessing properties
- Empty collections before iteration
- Null references before method calls

### Pattern 3: User-Friendly Error Messages

```bsl
❌ BAD:
Сообщить("Ошибка!");  // Useless

✅ GOOD:
Сообщить("Не удалось загрузить данные. Проверьте подключение к базе.");

✅ BETTER:
Сообщить("Ошибка загрузки данных: " + ОписаниеОшибки());
```

**Error message components:**
1. **What happened** (action that failed)
2. **Why it matters** (impact on user)
3. **What to do** (next steps, if known)

---

## ⚡ Client-Server Architecture

### Principle: Minimize Server Calls

**Why:** Network latency, server load, user experience

### Pattern 1: Validate Client-Side First

```bsl
&НаКлиенте
Процедура SaveData(Команда)
    // ✅ Validate locally BEFORE server call
    Если НЕ ЗначениеЗаполнено(Объект.Name) Тогда
        Сообщить("Введите имя!");
        Возврат;  // No server call
    КонецЕсли;

    // Validation passed → call server
    SaveDataНаСервере();
КонецПроцедуры
```

**Anti-pattern:**
```bsl
❌ BAD - validate on server (slow, network overhead)
&НаКлиенте
Процедура SaveData(Команда)
    // Calls server even with empty fields
    SaveDataНаСервере();
КонецПроцедуры

&НаСервере
Процедура SaveDataНаСервере()
    Если НЕ ЗначениеЗаполнено(Объект.Name) Тогда
        // Too late — already made server call
        Сообщить("Введите имя!");
        Возврат;
    КонецЕсли;
КонецПроцедуры
```

### Pattern 2: Client-Server Pair (Standard)

**Client handler** (validation + UI):
```bsl
&НаКлиенте
Процедура LoadData(Команда)
    // Validate
    Если НЕ ЗначениеЗаполнено(Объект.StartDate) Тогда
        Сообщить("Укажите дату начала!");
        Возврат;
    КонецЕсли;

    // Clear UI
    Results.Clear();

    // Call server
    LoadDataНаСервере();

    // UI feedback
    Сообщить("Загружено: " + Results.Количество() + " записей");
КонецПроцедуры
```

**Server handler** (database + calculations):
```bsl
&НаСервере
Процедура LoadDataНаСервере()
    Запрос = Новый Запрос;
    Запрос.Текст = "SELECT ...";
    Запрос.УстановитьПараметр("StartDate", Объект.StartDate);

    Результат = Запрос.Выполнить().Выгрузить();

    Для Каждого Строка Из Результат Цикл
        НоваяСтрока = Results.Add();
        // ... populate row ...
    КонецЦикла;
КонецПроцедуры
```

### Pattern 3: Server Handler with Parameters

**When:** Need custom parameters (not just `Объект` fields)

```bsl
&НаКлиенте
Процедура TableOnActivateRow(Элемент)
    ТекущаяСтрока = Элементы.Table.ТекущиеДанные;

    Если ТекущаяСтрока = Неопределено Тогда
        Возврат;
    КонецЕсли;

    // Call server with parameter
    LoadDetailsНаСервере(ТекущаяСтрока.RoleID);
КонецПроцедуры

&НаСервере
Процедура LoadDetailsНаСервере(РольID)  // ← Custom parameter
    DetailData.Clear();

    // Use parameter in query
    Запрос = Новый Запрос;
    Запрос.Текст = "SELECT ... WHERE RoleID = &RoleID";
    Запрос.УстановитьПараметр("RoleID", РольID);

    // ... load data ...
КонецПроцедуры
```

**Note:** Full signature required (`&НаСервере` + `Процедура` + parameters)

---

## 🚀 Performance Tips

### Tip 1: Use ValueTable for Temporary Data

**Why:** No database overhead, faster load/clear

```yaml
# ✅ Fast - in-memory only
forms:
  - name: Форма
    value_tables:
      - name: ReportResults
        columns: [...]
```

```yaml
# ❌ Slow - writes to database
tabular_sections:
  - name: ReportResults  # Don't do this for reports!
    columns: [...]
```

**Rule:** Reports/calculations → ValueTable, persistent data → TabularSection

**See also:** [LLM_DATA_GUIDE.md](LLM_DATA_GUIDE.md) for detailed decision framework

### Tip 2: Clear Before Load

**Why:** Avoids duplicates, ensures fresh data

```bsl
&НаСервере
Процедура LoadDataНаСервере()
    Results.Clear();  // ✅ Always clear first

    Запрос = Новый Запрос;
    // ... load data ...
КонецПроцедуры
```

### Tip 3: Use read_only for Calculated Fields

**Why:** Prevents accidental edits, clearer intent (v2.13.1+)

```yaml
attributes:
  - name: Total
    type: number
    digits: 15
    fraction_digits: 2
    read_only: true  # ✅ Calculated, not editable

forms:
  - name: Форма
    elements:
      - type: InputField
        name: TotalField
        attribute: Total
        read_only: true  # ✅ Form element also read-only
```

### Tip 4: Minimize Form Elements

**Why:** Faster rendering, simpler UI

```
✅ Good:  5-15 elements per form
⚠️ OK:    15-30 elements (group with UsualGroup)
❌ Bad:   30+ elements (consider Pages or multiple forms)
```

### Tip 5: Sort After Load (Not in Query)

**Why:** Flexibility, reusable queries

```bsl
&НаСервере
Процедура LoadDataНаСервере()
    Results.Clear();

    Запрос = Новый Запрос;
    Запрос.Текст = "SELECT ... ";  // No ORDER BY
    Результат = Запрос.Выполнить().Выгрузить();

    Для Каждого Строка Из Результат Цикл
        // ... populate Results ...
    КонецЦикла;

    // ✅ Sort in memory (fast, flexible)
    Results.Sort("Product Asc, Amount Desc");
КонецПроцедуры
```

---

## 🎨 Code Style

### BSL Formatting

```bsl
// ✅ Good formatting
&НаКлиенте
Процедура Generate(Команда)
    Если НЕ ЗначениеЗаполнено(Объект.StartDate) Тогда
        Сообщить("Укажите дату начала!");
        Возврат;
    КонецЕсли;

    Results.Clear();
    GenerateНаСервере();
    Сообщить("Готово!");
КонецПроцедуры
```

**Rules:**
- Indentation: 4 spaces (or tab)
- One statement per line
- Blank lines between logical blocks
- Clear variable names (Russian or transliterated English)

### Comments

```bsl
// ✅ Good - explains WHY
// Очищаем результаты перед загрузкой, чтобы избежать дублирования
Results.Clear();

// ❌ Bad - explains WHAT (obvious from code)
// Очищаем результаты
Results.Clear();
```

**When to comment:**
- Non-obvious business logic
- Workarounds for platform limitations
- Complex algorithms

**When NOT to comment:**
- Obvious operations (self-documenting code is better)
- Repeating what code says

---

## 💬 Tooltip Representation (v2.70.2+)

Controls how element tooltips are displayed. Available for all form elements.

### When to use each value:

| Value | Best for | Example |
|-------|----------|---------|
| `Button` | Complex fields needing documentation | Date picker with format rules, reference fields |
| `ShowBottom` | Compact forms, inline hints | Amount fields, status explanations |
| `ShowTop` | Elements at bottom of form | Fields near page footer |
| `Balloon` | Long explanatory text | Multi-line help, step-by-step instructions |
| `None` | Self-explanatory fields | Simple checkboxes, obvious buttons |
| `ShowAuto` | Default (platform decides) | When unsure |

### Usage examples:

```yaml
# Complex reference field - button for help
- type: InputField
  name: ContractorField
  attribute: Contractor
  tooltip_ru: "Выберите контрагента из справочника..."
  tooltip_uk: "Виберіть контрагента зі довідника..."
  tooltip_representation: Button

# Amount with inline hint
- type: InputField
  name: AmountField
  attribute: Amount
  tooltip_ru: "Сумма в валюте документа"
  tooltip_representation: ShowBottom

# Self-explanatory checkbox - no tooltip needed
- type: CheckBoxField
  name: IsActiveField
  attribute: IsActive
  tooltip_representation: None
```

### Recommendations:

- **Use `Button`** for fields with long documentation or non-obvious behavior
- **Use `ShowBottom`** for short inline hints (1-2 sentences)
- **Use `Balloon`** when tooltip has 3+ lines of text
- **Use `None`** when label text is self-explanatory
- **Default to `ShowAuto`** when unsure

---

## 📋 Quick Reference: Common Patterns

| Task | Pattern | File |
|------|---------|------|
| **Validate required field** | `НЕ ЗначениеЗаполнено(Объект.Field)` | Client BSL |
| **Validate date range** | `EndDate < StartDate` | Client BSL |
| **Clear table** | `Results.Clear()` | Client or Server BSL |
| **Show message** | `Сообщить("Message")` | Client BSL |
| **Query database** | `Запрос = Новый Запрос; ...` | Server BSL |
| **Add table row** | `НоваяСтрока = Results.Add()` | Server BSL |
| **Sort table** | `Results.Sort("Field Asc")` | Server BSL |
| **Error handling** | `Попытка ... Исключение ... КонецПопытки` | Server BSL |
| **Get current row** | `Элементы.Table.ТекущиеДанные` | Client BSL |
| **Check undefined** | `Если X = Неопределено Тогда ...` | Client or Server BSL |

---

**Last updated:** 2026-01-05
**Generator version:** 2.70.2+
