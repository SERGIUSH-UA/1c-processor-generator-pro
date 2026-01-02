# Data Import Wizard Example / Приклад майстра імпорту даних

**Purpose:** Complete wizard-style interface for importing data from CSV files

**Демонструє:**
- Multi-step wizard using Pages element
- File selection dialog with StartChoice event
- CSV file parsing and preview
- Step-by-step navigation (Back/Next buttons)
- Data validation and import to catalog
- Results display with success/error tracking
- Complex client-server workflow

---

## Use Case / Випадок використання

User requests: *"Create a wizard for importing products from CSV file with preview before import"*

This example demonstrates the complete wizard pattern with 4 steps:
1. File selection
2. Data preview
3. Import settings
4. Results display

---

## Structure / Структура

```
data_import/
├── config.yaml                      # Wizard configuration
└── handlers/
    ├── ПриОткрытии.bsl              # Initialize wizard
    ├── ПутьКФайлуНачалоВыбора.bsl   # File dialog
    ├── ЗагрузитьПредпросмотр.bsl    # Load preview (client)
    ├── ЗагрузитьПредпросмотрНаСервере.bsl  # Parse CSV (server)
    ├── НазадШаг1.bsl                # Navigation: Back to Step 1
    ├── ДалееШаг3.bsl                # Navigation: Forward to Step 3
    ├── НазадШаг2.bsl                # Navigation: Back to Step 2
    ├── ВыполнитьИмпорт.bsl          # Import validation (client)
    ├── ВыполнитьИмпортНаСервере.bsl # Import execution (server)
    └── Закрыть.bsl                  # Close form
```

---

## Wizard Flow / Потік майстра

```
┌─────────────────┐
│  Step 1: File   │  ← ПриОткрытии: Initialize
│   Selection     │  ← ПутьКФайлуНачалоВыбора: File dialog
└────────┬────────┘
         │ ЗагрузитьПредпросмотр
         ▼
┌─────────────────┐
│  Step 2: Preview│  ← ЗагрузитьПредпросмотрНаСервере: Parse CSV
│   (Table)       │
└────┬───────┬────┘
 Назад│      │Далее
     ▼       ▼
 Step 1   ┌─────────────────┐
          │ Step 3: Settings│
          │  (Import params)│
          └────┬───────┬────┘
           Назад│      │ВыполнитьИмпорт
               ▼       ▼
           Step 2   ┌─────────────────┐
                    │  Step 4: Results│  ← ВыполнитьИмпортНаСервере: Import
                    │   (Summary)     │
                    └────────┬────────┘
                             │Закрыть
                             ▼
                          [Close]
```

---

## Key Features / Ключові можливості

### 1. Pages Element for Wizard

```yaml
form:
  elements:
    - type: Pages
      name: ШагиМастера
      pages_representation: TabsOnTop
      pages:
        - name: Шаг1
          title: Шаг 1: ...
          child_items: [...]
        - name: Шаг2
          title: Шаг 2: ...
          child_items: [...]
```

**Why Pages?**
- Organizes multi-step workflows
- Each page can have its own layout
- User sees progress (tab titles)
- Easy navigation between steps

### 2. File Selection Dialog

**StartChoice event** on InputField opens file dialog:

```bsl
Диалог = Новый ДиалогВыбораФайла(РежимДиалогаВыбораФайла.Открытие);
Диалог.Фильтр = "CSV файлы (*.csv)|*.csv|Все файлы (*.*)|*.*";

Если Диалог.Выбрать() Тогда
    Объект.ПутьКФайлу = Диалог.ПолноеИмяФайла;
КонецЕсли;

СтандартнаяОбработка = Ложь;  // Cancel default behavior
```

**Important:** `СтандартнаяОбработка = Ложь` prevents default input field behavior

### 3. CSV Parsing Pattern

```bsl
ТекстовыйДокумент = Новый ТекстовыйДокумент;
ТекстовыйДокумент.Прочитать(ПутьКФайлу, Кодировка);

Для СтрокаНомер = 1 По ТекстовыйДокумент.КоличествоСтрок() Цикл
    Строка = ТекстовыйДокумент.ПолучитьСтроку(СтрокаНомер);
    Части = СтрРазделить(Строка, ";", Ложь);

    // Process parts...
КонецЦикла;
```

### 4. Page Navigation

**Client-side page switching:**
```bsl
Элементы.ШагиМастера.ТекущаяСтраница = Элементы.Шаг2Предпросмотр;
```

**Pattern:**
- Simple handlers for Back/Next buttons
- Set `ТекущаяСтраница` property
- Validate data before moving forward

### 5. Dynamic Catalog Access

```bsl
// Get catalog manager by name (string)
МенеджерСправочника = Справочники[Объект.Справочник];

// Create new item
НовыйЭлемент = МенеджерСправочника.СоздатьЭлемент();
НовыйЭлемент.Записать();
```

**Why dynamic?**
- User can choose target catalog at runtime
- More flexible than hardcoded catalog name
- Requires error handling (catalog might not exist)

### 6. Import with Results Tracking

```bsl
// Process each row
Для Каждого Строка Из Предпросмотр Цикл
    Попытка
        // Import logic...

        // Log success
        Результат = РезультатыИмпорта.Добавить();
        Результат.Статус = "Создано";
    Исключение
        // Log error
        Результат = РезультатыИмпорта.Добавить();
        Результат.Статус = "Ошибка";
        Результат.Сообщение = ОписаниеОшибки();
    КонецПопытки;
КонецЦикла;
```

**Result tracking provides:**
- User sees what succeeded/failed
- Detailed error messages per row
- Import statistics (created/updated/errors)

---

## Element Events / Події елементів

### StartChoice Event

Triggers when user clicks "..." button or presses F4 in InputField:

```yaml
- type: InputField
  name: ПутьКФайлуПоле
  attribute: ПутьКФайлу
  events:
    StartChoice: ПутьКФайлуНачалоВыбора
```

**Handler must:**
- Open selection dialog
- Set field value
- Cancel standard processing: `СтандартнаяОбработка = Ложь`

---

## Validation Patterns / Паттерни валідації

### 1. File Validation

```bsl
// Check file path filled
Если НЕ ЗначениеЗаполнено(Объект.ПутьКФайлу) Тогда
    Сообщить("Выберите файл!");
    Возврат;
КонецЕсли;

// Check file exists
Файл = Новый Файл(Объект.ПутьКФайлу);
Если НЕ Файл.Существует() Тогда
    Сообщить("Файл не найден!");
    Возврат;
КонецЕсли;
```

### 2. Data Validation

```bsl
// Check table has data
Если Предпросмотр.Количество() = 0 Тогда
    Сообщить("Нет данных!");
    Возврат;
КонецЕсли;
```

### 3. User Confirmation

```bsl
Ответ = Вопрос(
    "Импортировать " + Количество + " записей?",
    РежимДиалогаВопрос.ДаНет
);

Если Ответ = КодВозвратаДиалога.Нет Тогда
    Возврат;
КонецЕсли;
```

---

## Generation Command / Команда генерації

```bash
cd ~/SmallBusiness\.claude\tools\1c_processor_generator\examples\yaml\data_import

python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers handlers/
```

---

## Learning Points for LLMs / Уроки для ЛЛМ

1. **Wizard = Pages + Navigation**
   - Use Pages element for multi-step workflows
   - Each page is independent layout
   - Navigation handlers just switch pages

2. **File Operations Pattern**
   - StartChoice event for file dialogs
   - `ДиалогВыбораФайла` with filter
   - Must cancel standard processing
   - Server-side file reading with encoding

3. **CSV Parsing**
   - Use `ТекстовыйДокумент` for text files
   - `СтрРазделить()` to parse delimited data
   - Skip empty lines
   - Handle encoding (UTF-8, Windows-1251, etc.)

4. **Dynamic Metadata Access**
   - `Справочники[Name]` - access by string name
   - `МенеджерСправочника.СоздатьЭлемент()` - create new
   - `Ссылка.ПолучитьОбъект()` - get object for editing
   - Always wrap in try-catch (might not exist)

5. **Import Best Practices**
   - Preview before import
   - Track results (success/error per row)
   - Check for existing items (by code/name)
   - Support "create new" vs "update existing"
   - Show summary statistics

6. **Two ValueTables Pattern**
   - One for preview (before import)
   - One for results (after import)
   - Different column sets for different purposes

7. **User Confirmation**
   - Use `Вопрос()` for important actions
   - Show what will be done
   - Check return code

---

## Variations / Варіації

This wizard pattern can be adapted for:
- Excel import (use `COM.Excel` or `SpreadsheetDocument`)
- XML/JSON import (use `XMLReader` or `JSONReader`)
- Database import (connect via ODBC)
- Multi-file import (loop through folder)
- Import with field mapping (add mapping step)
- Export wizard (reverse flow: select → filter → format → export)

---

**Version:** 2.7.3
**Last updated:** 2025-10-14
