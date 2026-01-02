# 1C Processor Generator - UI Patterns & Examples

**Target audience:** LLMs generating 1C processors
**Main document:** [LLM_PROMPT.md](LLM_PROMPT.md)

---

## 🎨 UI Patterns

### Pattern 1: Simple Form (Input + Action)

**Use case:** User enters data, clicks button to process

```yaml
processor:
  name: SimpleCalculator
  platform_version: "2.11"  # Optional: 2.10, 2.11, 2.18, 2.19, etc. (default: 2.11)

attributes:
  - name: Number1
    type: number
  - name: Number2
    type: number
  - name: Result
    type: number

forms:
  - name: Форма
    default: true

    elements:
      - type: InputField
        name: Number1Field
        attribute: Number1
      - type: InputField
        name: Number2Field
        attribute: Number2
      - type: Button
        name: CalculateButton
        command: Calculate
      - type: InputField
        name: ResultField
        attribute: Result
        read_only: true  # Calculated field (v2.13.1+)

    commands:
      - name: Calculate
        title: {ru: Вычислить, uk: Обчислити, en: Calculate}  # Multilingual (v2.13.0+)
        handler: Calculate
```

**handlers/Calculate.bsl:**
```bsl
Объект.Result = Объект.Number1 + Объект.Number2;
Сообщить("Результат: " + Объект.Result);
```

---

### Pattern 2: Report with Table

**Use case:** User sets filters, clicks button, sees results in table

```yaml
processor:
  name: SalesReport

attributes:
  - name: StartDate
    type: date
  - name: EndDate
    type: date

forms:
  - name: Форма
    default: true

    value_tables:
      - name: Results
        columns:
          - name: Product
            type: string
            length: 200
          - name: Quantity
            type: number
            digits: 10
            fraction_digits: 2
          - name: Amount
            type: number
            digits: 15
            fraction_digits: 2

    elements:
      # Filters
      - type: UsualGroup
        name: FilterGroup
        title: Filters
        show_title: true
        child_items:
          - type: InputField
            name: StartDateField
            attribute: StartDate
          - type: InputField
            name: EndDateField
            attribute: EndDate
          - type: Button
            name: GenerateButton
            command: Generate

      # Results table (read-only for reports)
      - type: Table
        name: ResultsTable
        tabular_section: Results
        read_only: true  # Reports are typically read-only
        properties:
          is_value_table: true

    commands:
      - name: Generate
        title_ru: Сформировать
        title_uk: Сформувати
        handler: Generate
```

**handlers/Generate.bsl:**
```bsl
Если НЕ ЗначениеЗаполнено(Объект.StartDate) Тогда
    Сообщить("Укажите дату начала!");
    Возврат;
КонецЕсли;

ЗагрузитьДанныеНаСервере();
```

**handlers/ЗагрузитьДанныеНаСервере.bsl:**
```bsl
Results.Clear();

Запрос = Новый Запрос;
Запрос.Текст = "SELECT ...";
Запрос.УстановитьПараметр("StartDate", Объект.StartDate);

Результат = Запрос.Выполнить().Выгрузить();

Для Каждого Строка Из Результат Цикл
    НоваяСтрока = Results.Add();
    НоваяСтрока.Product = Строка.Product;
    НоваяСтрока.Quantity = Строка.Quantity;
    НоваяСтрока.Amount = Строка.Amount;
КонецЦикла;
```

---

### Pattern 3: Simple Dynamic List (Auto-Query)

**Use case:** Display data from database table automatically

**⚠️ CRITICAL for LLMs:** DynamicList requires **TWO parts**:
1. `dynamic_lists:` section - defines the data source
2. `form.elements` with `Table` + `is_dynamic_list: true` property - displays the list

**Key features:**
- `main_table` - Specifies database table (Document.*, Catalog.*, etc.)
- **No manual_query** - 1C automatically generates query from main_table
- **MainTable present = DynamicDataRead: true** automatically
- Columns auto-generated from table fields

```yaml
processor:
  name: СписокДокументов
  synonym_ru: Список документов
  synonym_uk: Список документів
  platform_version: "2.11"  # Optional: Supports any version (2.10, 2.11, 2.18, 2.19, etc.)

forms:
  - name: Форма
    default: true

    # 1. Define DynamicList data source
    dynamic_lists:
      - name: СписокЗаказов
        title_ru: Список заказов
        title_uk: Список замовлень
        main_table: Document.Заказ  # ⚠️ CRITICAL: Automatic query from this table
        # manual_query: false is default - no custom query needed!

    # 2. Display DynamicList on form with Table element
    elements:
      - type: Table
        name: СписокЗаказовТаблица
        tabular_section: СписокЗаказов  # ⚠️ CRITICAL: References dynamic_lists.name
        properties:
          is_dynamic_list: true  # ⚠️ CRITICAL: Must be under properties:!
```

**Result:** Table automatically shows all fields from Document.Заказ with live database connection

---

### Pattern 3.5: Complex Dynamic List with MainTable and Filters

**Use case:** Database query with MainTable, filters, UseAlways, and custom columns

**⚠️ CRITICAL differences from simple Dynamic List:**
- **MainTable specified** → DynamicDataRead=true (live database connection)
- **UseAlways** - fields always loaded (only valid when Table element exists!)
- **Columns** - explicitly define which fields to display and their widths
- **Properties in Table** - `is_dynamic_list: true` must be under `properties:`, not top-level!

```yaml
processor:
  name: СписокПлатежей
  synonym_ru: Список платежных поручений
  synonym_uk: Список платіжних доручень

# Optional: Filter attributes
attributes:
  - name: ДатаНачала
    type: date
    synonym_ru: Дата начала
    synonym_uk: Дата початку
  - name: ДатаОкончания
    type: date
    synonym_ru: Дата окончания
    synonym_uk: Дата закінчення

forms:
  - name: Форма
    default: true

    properties:
      title_ru: Список платежных поручений
      title_uk: Список платіжних доручень
      auto_title: false

    events:
      OnCreateAtServer: ПриСозданииНаСервере

    # 1. Define complex DynamicList with MainTable
    dynamic_lists:
      - name: СписокПлатежей
        title_ru: Список платежных поручений
        title_uk: Список платіжних доручень
        main_attribute: true  # Main form attribute
        manual_query: true
        main_table: Document.ПлатежноеПоручение  # ⚠️ CRITICAL: Enables DynamicDataRead=true

        # Complex query with CASE WHEN
        query_text: |
          ВЫБРАТЬ
            ДокументПлатежноеПоручение.Ссылка,
            ДокументПлатежноеПоручение.Дата,
            ДокументПлатежноеПоручение.Номер,
            ДокументПлатежноеПоручение.БанковскийСчет,
            ВЫБОР
              КОГДА ДокументПлатежноеПоручение.ВидОперации = ЗНАЧЕНИЕ(Перечисление.ВидыОперацийПлатежноеПоручение.Подотчетнику)
              ТОГДА ДокументПлатежноеПоручение.Подотчетник
              ИНАЧЕ ДокументПлатежноеПоручение.Контрагент
            КОНЕЦ КАК Контрагент,
            ДокументПлатежноеПоручение.СуммаДокумента,
            ДокументПлатежноеПоручение.Оплачено
          ИЗ
            Документ.ПлатежноеПоручение КАК ДокументПлатежноеПоручение
          ГДЕ
            ДокументПлатежноеПоручение.Дата МЕЖДУ &ДатаНачала И &ДатаОкончания

        # UseAlways - fields that must always be loaded (⚠️ only when Table exists!)
        use_always_fields:
          - Ссылка            # ⚠️ WITHOUT list name prefix in YAML!
          - БанковскийСчет    # Generator adds prefix automatically

        # Columns - define display order and widths
        columns:
          - field: Дата
            title_ru: Дата
            title_uk: Дата
            width: 12
          - field: Номер
            title_ru: Номер
            title_uk: Номер
            width: 8
          - field: Контрагент
            title_ru: Контрагент
            title_uk: Контрагент
            width: 20
          - field: СуммаДокумента
            title_ru: Сумма
            title_uk: Сума
            width: 12
          - field: Оплачено
            title_ru: Оплачено
            title_uk: Оплачено
            width: 8

    # 2. Display DynamicList on form with Table element
    elements:
      # Optional: Filter group
      - type: UsualGroup
        name: ГруппаФильтров
        title: Фильтры
        show_title: true
        child_items:
          - type: InputField
            name: ДатаНачалаПоле
            attribute: ДатаНачала
          - type: InputField
            name: ДатаОкончанияПоле
            attribute: ДатаОкончания

      # ⚠️ CRITICAL: Table element to display DynamicList
      - type: Table
        name: СписокПлатежейТаблица
        tabular_section: СписокПлатежей  # References dynamic_lists.name
        properties:
          is_dynamic_list: true  # ⚠️ MUST be under properties:, not top-level!

    commands:
      - name: Обновить
        title_ru: Обновить
        title_uk: Оновити
        handler: ОбновитьСписок
        picture: StdPicture.Refresh
```

**handlers/ПриСозданииНаСервере.bsl:**
```bsl
// Initialize default filter values
Объект.ДатаНачала = НачалоМесяца(ТекущаяДата());
Объект.ДатаОкончания = КонецДня(ТекущаяДата());
```

**handlers/ОбновитьСписок.bsl:**
```bsl
// Refresh the dynamic list
Элементы.СписокПлатежейТаблица.Обновить();
Сообщить("Список обновлен");
```

**⚠️ CRITICAL points for DynamicList (LLMs must remember):**

1. **YAML Structure:**
   ```yaml
   # ❌ WRONG:
   - type: Table
     name: MyTable
     tabular_section: MyList
     is_dynamic_list: true  # WRONG - top level!

   # ✅ CORRECT:
   - type: Table
     name: MyTable
     tabular_section: MyList
     properties:           # CORRECT - under properties!
       is_dynamic_list: true
   ```

2. **UseAlways field names:**
   - In YAML: `use_always_fields: [Ref, Field1]` (without prefix)
   - Generated XML: `<Field>ListName.Ref</Field>` (with prefix)
   - Generator adds prefix automatically!

3. **DynamicDataRead logic:**
   - `main_table: Document.Something` → `DynamicDataRead: true`
   - No main_table → `DynamicDataRead: false`
   - Generator handles this automatically based on main_table presence

4. **UseAlways validation:**
   - Generator validates that Table element exists on form
   - If no Table → UseAlways removed automatically + warning
   - Always add Table element when using use_always_fields!

5. **Columns generation:**
   - If columns specified → generates LabelField for each column
   - If no columns + manual_query → no columns generated
   - If no columns + !manual_query → auto-generates Description column

**When to use DynamicList:**
- ✅ Live database queries (documents, catalogs, journals)
- ✅ User needs to see real-time data with filters
- ✅ Data comes from database tables with complex queries
- ✅ Need standard 1C list features (sorting, filtering, conditional appearance)

**When NOT to use DynamicList (use ValueTable instead):**
- ❌ Temporary calculations and transformations
- ❌ Data aggregations that don't map to database tables
- ❌ Results that need to be modified by user before saving
- ❌ Non-persistent preview data

---

### Pattern 4: Wizard (Multi-step)

**Use case:** User completes steps sequentially

```yaml
processor:
  name: ImportWizard

attributes:
  - name: FileName
    type: string
    length: 500
  - name: Encoding
    type: string
    length: 50

forms:
  - name: Форма
    default: true

    value_tables:
      - name: PreviewData
        columns:
          - name: Column1
            type: string
            length: 100

    elements:
      - type: Pages
        name: WizardPages
        pages_representation: TabsOnTop
        pages:
          - name: Step1
            title: Шаг 1: Выбор файла
            child_items:
              - type: InputField
                name: FileNameField
                attribute: FileName
              - type: Button
                name: SelectFileButton
                command: SelectFile

          - name: Step2
            title: Шаг 2: Предпросмотр
            child_items:
              - type: Table
                name: PreviewTable
                tabular_section: PreviewData
                properties:
                  is_value_table: true

          - name: Step3
            title: Шаг 3: Импорт
            child_items:
              - type: Button
                name: ImportButton
                command: Import

    commands:
      - name: SelectFile
        title_ru: Выбрать файл
        title_uk: Вибрати файл
        handler: SelectFile
      - name: Import
        title_ru: Импорт
        title_uk: Імпорт
        handler: Import
```

---

### Pattern 5: Master-Detail (with OnActivateRow event)

**Use case:** Table + auto-loading details when row selected

```yaml
processor:
  name: UsersByRole
  synonym_ru: Просмотр пользователей по ролям
  synonym_uk: Перегляд користувачів за ролями

forms:
  - name: Форма
    default: true

    events:
      OnCreateAtServer: OnCreateAtServer

    value_tables:
      - name: Roles
        columns:
          - name: RoleName
            type: string
            length: 100
          - name: Synonym
            type: string
            length: 200

      - name: Users
        columns:
          - name: UserName
            type: string
            length: 100
          - name: FullName
            type: string
            length: 200

    elements:
      # Master: Roles table with OnActivateRow event
      - type: Table
        name: RolesTable
        tabular_section: Roles
        properties:
          is_value_table: true
        events:
          OnActivateRow: RolesTableOnActivateRow

      # Detail: Users table (auto-updated on row change)
      - type: Table
        name: UsersTable
        tabular_section: Users
        properties:
          is_value_table: true
```

**handlers/OnCreateAtServer.bsl:**
```bsl
// Load all roles from metadata
Roles.Clear();

For Each Role In Metadata.Roles Do
    NewRow = Roles.Add();
    NewRow.RoleName = Role.Name;
    NewRow.Synonym = Role.Synonym;
EndDo;

Roles.Sort("Synonym");
```

**handlers/RolesTableOnActivateRow.bsl:**
```bsl
// Get current row
CurrentRow = Items.RolesTable.CurrentData;

If CurrentRow = Undefined Then
    Users.Clear();
    Return;
EndIf;

// Call server to load users
RolesTableOnActivateRowAtServer(CurrentRow.RoleName);
```

**handlers/RolesTableOnActivateRowAtServer.bsl:**
```bsl
&OnServer
Procedure RolesTableOnActivateRowAtServer(RoleName)
    Users.Clear();

    If IsBlankString(RoleName) Then
        Return;
    EndIf;

    Role = Metadata.Roles.Find(RoleName);
    If Role = Undefined Then
        Return;
    EndIf;

    InfoBaseUsers = InfoBaseUsers.GetUsers();

    For Each IBUser In InfoBaseUsers Do
        HasRole = False;
        For Each UserRole In IBUser.Roles Do
            If UserRole = Role Then
                HasRole = True;
                Break;
            EndIf;
        EndDo;

        If HasRole Then
            NewRow = Users.Add();
            NewRow.UserName = IBUser.Name;
            NewRow.FullName = IBUser.FullName;
        EndIf;
    EndDo;

    Users.Sort("UserName");
EndProcedure
```

**Key points:**
- OnActivateRow automatically triggers when user clicks on a row
- Client handler gets current row data and calls server
- Server handler receives parameters (RoleName) and loads data
- Use full signature in server handler for custom parameters

---

### Pattern 6: CRUD Interface

**Use case:** Create, Read, Update, Delete operations

```yaml
processor:
  name: DataManager

attributes:
  - name: CurrentID
    type: string
    length: 36
  - name: CurrentName
    type: string
    length: 200

forms:
  - name: Форма
    default: true

    value_tables:
      - name: Records
        columns:
          - name: ID
            type: string
            length: 36
          - name: Name
            type: string
            length: 200

    elements:
      # Table
      - type: Table
        name: RecordsTable
        tabular_section: Records
        properties:
          is_value_table: true

      # Edit fields
      - type: UsualGroup
        name: EditGroup
        title: Edit
        child_items:
          - type: InputField
            name: CurrentNameField
            attribute: CurrentName

      # Action buttons
      - type: UsualGroup
        name: ButtonBar
        group_direction: Horizontal
        child_items:
          - type: Button
            name: AddButton
            command: Add
          - type: Button
            name: UpdateButton
            command: Update
          - type: Button
            name: DeleteButton
            command: Delete

    commands:
      - name: Add
        title_ru: Добавить
        title_uk: Додати
        handler: Add
      - name: Update
        title_ru: Изменить
        title_uk: Змінити
        handler: Update
      - name: Delete
        title_ru: Удалить
        title_uk: Видалити
        handler: Delete
```

---

### Pattern 7: Settings Form (with v2.2.0 elements)

**Use case:** Configuration form with RadioButton, CheckBox, dropdown lists, and search

**New elements:**
- `RadioButtonField` - Single choice from options (Tumbler/RadioButton style)
- `CheckBoxField` - Boolean flags
- `InputField + ChoiceList` - Dropdown list with predefined values
- `InputField + InputHint` - Placeholder text in input fields

```yaml
processor:
  name: НастройкиОбработки
  synonym_ru: Настройки обработки
  synonym_uk: Налаштування обробки

attributes:
  # RadioButtonField attribute
  - name: ТипОперации
    type: string
    length: 20
    synonym_ru: Тип операции
    synonym_uk: Тип операції

  # CheckBoxField attributes
  - name: ВыполнитьПроверку
    type: boolean
    synonym_ru: Выполнить проверку
    synonym_uk: Виконати перевірку

  - name: АвтоОбновление
    type: boolean
    synonym_ru: Автоматическое обновление
    synonym_uk: Автоматичне оновлення

  # InputField with ChoiceList
  - name: РежимРаботы
    type: string
    length: 50
    synonym_ru: Режим работы
    synonym_uk: Режим роботи

  # InputField with InputHint
  - name: ПоискСтроки
    type: string
    length: 150
    synonym_ru: Поиск
    synonym_uk: Пошук

  # Status field
  - name: Статус
    type: string
    length: 200

forms:
  - name: Форма
    default: true

    properties:
      title: true
      title_ru: "Настройки обработки"
      title_uk: "Налаштування обробки"
      auto_title: false

    events:
      OnOpen: ПриОткрытии

    elements:
    # Group 1: Operation type (RadioButtonField)
    - type: UsualGroup
      name: ГруппаТипОперации
      title: Тип операции
      show_title: true
      group_direction: Vertical
      child_items:
        - type: RadioButtonField
          name: ТипОперацииПоле
          attribute: ТипОперации
          title_location: None
          radio_button_type: Tumbler  # or RadioButton
          choice_list:
            - value: "Импорт"
              value_type: "xs:string"
              presentation_ru: "Импорт данных"
              presentation_uk: "Імпорт даних"
            - value: "Экспорт"
              value_type: "xs:string"
              presentation_ru: "Экспорт данных"
              presentation_uk: "Експорт даних"
            - value: "Обмен"
              value_type: "xs:string"
              presentation_ru: "Обмен данными"
              presentation_uk: "Обмін даними"
          events:
            OnChange: ТипОперацииПриИзменении

    # Group 2: Options (CheckBoxField)
    - type: UsualGroup
      name: ГруппаНастройки
      title: Настройки
      show_title: true
      group_direction: Vertical
      child_items:
        - type: CheckBoxField
          name: ВыполнитьПроверкуПоле
          attribute: ВыполнитьПроверку
          title_location: Right
          width: 30

        - type: CheckBoxField
          name: АвтоОбновлениеПоле
          attribute: АвтоОбновление
          title_location: Right
          width: 30

    # Group 3: Mode (InputField with ChoiceList)
    - type: UsualGroup
      name: ГруппаРежим
      title: Режим работы
      show_title: true
      group_direction: Vertical
      child_items:
        - type: InputField
          name: РежимРаботыПоле
          attribute: РежимРаботы
          title_location: Top
          width: 40
          horizontal_stretch: false
          choice_list:
            - value: "Автоматический"
              value_type: "xs:string"
              presentation_ru: "Автоматический"
              presentation_uk: "Автоматичний"
            - value: "Ручной"
              value_type: "xs:string"
              presentation_ru: "Ручной"
              presentation_uk: "Ручний"
            - value: "Пошаговый"
              value_type: "xs:string"
              presentation_ru: "Пошаговый"
              presentation_uk: "Покроковий"

    # Group 4: Search (InputField with InputHint)
    - type: UsualGroup
      name: ГруппаПоиск
      title: Поиск
      show_title: true
      group_direction: Vertical
      child_items:
        - type: InputField
          name: ПоискСтрокиПоле
          attribute: ПоискСтроки
          title_location: Top
          width: 50
          input_hint_ru: "Введите текст для поиска..."
          input_hint_uk: "Введіть текст для пошуку..."

    # Status label
    - type: LabelField
      name: СтатусПоле
      attribute: Статус

      # Buttons
      - type: UsualGroup
        name: ГруппаКнопки
        group_direction: Horizontal
        child_items:
          - type: Button
            name: ПрименитьКнопка
            command: Применить
            width: 20
            representation: Text

    commands:
      - name: Применить
        title_ru: Применить
        title_uk: Застосувати
        handler: Применить
```

**handlers/ПриОткрытии.bsl:**
```bsl
// Initialize default values
Объект.ТипОперации = "Импорт";
Объект.ВыполнитьПроверку = Истина;
Объект.АвтоОбновление = Ложь;
Объект.РежимРаботы = "Автоматический";
Объект.Статус = "Готов к настройке";
```

**handlers/ТипОперацииПриИзменении.bsl:**
```bsl
// Update status when operation type changes
Объект.Статус = "Выбран тип операции: " + Объект.ТипОперации;
```

**handlers/Применить.bsl:**
```bsl
// Validate settings
Если ПустаяСтрока(Объект.ТипОперации) Тогда
    Сообщить("Выберите тип операции!");
    Возврат;
КонецЕсли;

Если ПустаяСтрока(Объект.РежимРаботы) Тогда
    Сообщить("Выберите режим работы!");
    Возврат;
КонецЕсли;

// Apply settings
ПрименитьНаСтройкиНаСервере();
Объект.Статус = "✓ Настройки применены";
ПоказатьПредупреждение(, "Настройки успешно применены!");
```

**Key features of new elements:**

1. **RadioButtonField:**
   - `radio_button_type: Tumbler` - iOS-style toggle switch
   - `radio_button_type: RadioButton` - Traditional radio buttons
   - `choice_list` - Required, defines available options
   - `title_location: None` - Hide individual titles for cleaner look

2. **CheckBoxField:**
   - Simpler than InputField for boolean values
   - `title_location: Right` - Common pattern for checkboxes
   - `width` - Control element width

3. **InputField + ChoiceList:**
   - Creates dropdown/combobox
   - `choice_list` with `value` and `presentation_ru/uk`
   - User can select from predefined values
   - `horizontal_stretch: false` - Don't stretch to fill

4. **InputField + InputHint:**
   - `input_hint_ru/uk` - Placeholder text (like HTML placeholder)
   - Shows hint when field is empty
   - Disappears when user starts typing

---

### Pattern 8: Nested UsualGroup (Complex Layouts) - v2.7.1

**Use case:** Organize buttons and controls in multi-level groups inside Pages

**⚡ NEW: Full support for UsualGroup inside UsualGroup**
- Nest UsualGroup multiple levels deep
- Useful for button toolbars, collapsible panels, organized sections
- Each nested level maintains proper ID sequencing

```yaml
processor:
  name: ПоискDuckDuckGo
  synonym_ru: Поиск DuckDuckGo
  synonym_uk: Пошук DuckDuckGo

attributes:
  - name: ПоисковыйЗапрос
    type: string
    length: 300
    synonym_ru: Поисковый запрос
    synonym_uk: Пошуковий запит

forms:
  - name: Форма
    default: true

    value_tables:
      - name: SearchResults
        columns:
          - name: Title
            type: string
            length: 300
          - name: URL
            type: string
            length: 500

    elements:
      - type: Pages
        name: MainPages
        pages_representation: None
        pages:
          - name: SearchPage
            title: Поиск
            child_items:
              # Search input group
              - type: UsualGroup
                name: ГруппаПоиска
                title: Параметры поиска
                show_title: true
                group_direction: Vertical
                child_items:
                  - type: InputField
                    name: ПоисковыйЗапросПоле
                    attribute: ПоисковыйЗапрос

                  # ⭐ NESTED UsualGroup for buttons
                  - type: UsualGroup
                    name: ГруппаКнопокПоиска
                    group_direction: Horizontal
                    show_title: false
                    child_items:
                      - type: Button
                        name: ПоискКнопка
                        command: Search
                      - type: Button
                        name: ОчиститьКнопка
                        command: Clear

              # Results table
              - type: Table
                name: SearchResultsTable
                tabular_section: SearchResults
                properties:
                  is_value_table: true

    commands:
      - name: Search
        title_ru: Поиск
        title_uk: Пошук
        handler: ВыполнитьПоиск
        shortcut: F5
      - name: Clear
        title_ru: Очистить
        title_uk: Очистити
        handler: ОчиститьРезультаты
```

**Key points for nested UsualGroup:**
- ✅ Parent UsualGroup can contain child UsualGroup elements
- ✅ Nested groups can have different group_direction (Vertical parent with Horizontal child)
- ✅ Button elements inside nested groups are fully supported
- ✅ All form element types supported: InputField, Button, LabelField, etc.
- ✅ Page titles now correctly display (fixed in v2.7.1)
- 💡 Use nested groups to organize buttons in toolbars while keeping them in logical sections

---

### Pattern 9: Multiple Forms (Main + Settings)

**Use case:** Processor with main form and separate settings dialog

**⚡ NEW in v2.8.0:** Full multiple forms support with separate handlers

```yaml
processor:
  name: ОбработкаДанных
  synonym_ru: Обработка данных
  synonym_uk: Обробка даних

attributes:
  - name: Параметр1
    type: string
    length: 100
    synonym_ru: Параметр 1
    synonym_uk: Параметр 1

  - name: Результат
    type: string
    length: 500

forms:
  # Main form (default)
  - name: Форма
    default: true
    handlers_dir: handlers_main

    properties:
      title_ru: Главная форма
      title_uk: Головна форма

    elements:
      - type: InputField
        name: Параметр1Поле
        attribute: Параметр1

      - type: LabelField
        name: РезультатПоле
        attribute: Результат

      - type: UsualGroup
        name: ГруппаКнопок
        group_direction: Horizontal
        child_items:
          - type: Button
            name: ВыполнитьКнопка
            command: Выполнить
          - type: Button
            name: НастройкиКнопка
            command: ОткрытьНастройки

    commands:
      - name: Выполнить
        title_ru: Выполнить
        title_uk: Виконати
        handler: Выполнить
        picture: StdPicture.ExecuteTask

      - name: ОткрытьНастройки
        title_ru: Настройки
        title_uk: Налаштування
        handler: ОткрытьНастройки
        picture: StdPicture.CustomizeForm
        shortcut: F9

  # Settings form
  - name: Настройки
    default: false
    handlers_dir: handlers_settings

    properties:
      title_ru: Настройки обработки
      title_uk: Налаштування обробки
      WindowOpeningMode: LockOwnerWindow

    elements:
      - type: LabelDecoration
        name: ЗаголовокНастроек
        properties:
          title: Параметры обработки

      - type: UsualGroup
        name: ГруппаНастроек
        title: Параметры
        show_title: true
        child_items:
          - type: InputField
            name: ПараметрНастройкиПоле
            attribute: Параметр1
            properties:
              title_location: Left

      - type: UsualGroup
        name: ГруппаКнопокНастроек
        group_direction: Horizontal
        child_items:
          - type: Button
            name: СохранитьКнопка
            command: Сохранить
          - type: Button
            name: ЗакрытьКнопка
            command: ЗакрытьФорму

    commands:
      - name: Сохранить
        title_ru: Сохранить
        title_uk: Зберегти
        handler: Сохранить
        picture: StdPicture.Write

      - name: ЗакрытьФорму
        title_ru: Закрыть
        title_uk: Закрити
        handler: ЗакрытьФорму

    events:
      OnOpen: ПриОткрытииНастроек
```

**handlers_main/ОткрытьНастройки.bsl:**
```bsl
&НаКлиенте
Процедура ОткрытьНастройки(Команда)
    // Open Settings form modally
    ОткрытьФорму("ВнешняяОбработка." + ЭтаФорма.ИмяФормы + ".Форма.Настройки", , ЭтаФорма);
КонецПроцедуры
```

**handlers_main/Выполнить.bsl:**
```bsl
&НаКлиенте
Процедура Выполнить(Команда)
    ВыполнитьНаСервере();
КонецПроцедуры

&НаСервере
Процедура ВыполнитьНаСервере()
    Объект.Результат = "Обработано: " + Объект.Параметр1;
    Сообщить("Выполнение завершено");
КонецПроцедуры
```

**handlers_settings/ПриОткрытииНастроек.bsl:**
```bsl
&НаКлиенте
Процедура ПриОткрытииНастроек(Отказ)
    // Initialize settings form
    Сообщить("Настройки открыты");
КонецПроцедуры
```

**handlers_settings/Сохранить.bsl:**
```bsl
&НаКлиенте
Процедура Сохранить(Команда)
    // Save settings logic
    Сообщить("Настройки сохранены: " + Объект.Параметр1);
    Закрыть();
КонецПроцедуры
```

**handlers_settings/ЗакрытьФорму.bsl:**
```bsl
&НаКлиенте
Процедура ЗакрытьФорму(Команда)
    Закрыть();
КонецПроцедуры
```

**Key points for multiple forms:**
- ✅ Each form can have own `handlers_dir` for organized code
- ✅ Mark one form as `default: true` - it opens by default
- ✅ Open forms using `ОткрытьФорму("ВнешняяОбработка." + ИмяФормы + ".Форма.FormName")`
- ✅ Use `WindowOpeningMode: LockOwnerWindow` for modal dialogs
- ✅ Each form has own elements, commands, events, value_tables, dynamic_lists
- ✅ Shared attributes defined at processor level
- 💡 Perfect for Settings, About, Help dialogs separate from main form

**When to use multiple forms:**
- Settings/Configuration that shouldn't clutter main form
- About/Help information windows
- Additional data entry forms (e.g., "Add record" dialog)
- Preview/Details windows
- Any multi-window workflow

---

## 🎨 Commands and Pictures

Commands can have pictures (icons) that are displayed on buttons. The generator supports:

**Supported picture types:**
- `StdPicture.*` - Standard platform pictures (130+ validated names)
- `CommonPicture.*` - Configuration-specific pictures

**Auto-representation feature:**
When a command has a picture, buttons automatically get `representation: PictureAndText` to display both icon and text. This can be overridden by explicitly setting `representation` property on the button.

**Example:**
```yaml
forms:
  - name: Форма
    default: true
    commands:
      - name: ВыполнитьДействие
        title_ru: Выполнить
        title_uk: Виконати
        picture: StdPicture.ExecuteTask  # ✅ Valid picture
        handler: ВыполнитьДействие
      - name: ЭкспортДанных
        title_ru: Экспорт
        title_uk: Експорт
        picture: StdPicture.SaveFile
        handler: ЭкспортДанных
    elements:
      # This button will automatically get representation: PictureAndText
      - type: Button
        name: ВыполнитьКнопка
        command: ВыполнитьДействие
      # This button overrides to show only text
      - type: Button
        name: ЭкспортКнопка
        command: ЭкспортДанных
        representation: Text  # Override auto-representation
```

**Common StdPicture names:**
- `StdPicture.ExecuteTask` - Execute/Run actions
- `StdPicture.InputFieldClear` - Clear/Reset actions
- `StdPicture.SaveFile` - Save/Export actions
- `StdPicture.OpenFile` - Open/Import actions
- `StdPicture.CustomizeForm` - Settings/Configuration
- `StdPicture.User` - User-related actions
- `StdPicture.Refresh` - Refresh/Reload actions
- `StdPicture.Print` - Print actions

**Picture validation:**
The generator validates StdPicture names against known platform pictures. If you use an invalid name, you'll get a validation error with suggestions. See [VALID_PICTURES.md](VALID_PICTURES.md) for the full list of 130+ pictures.

---

## 📂 BSL Handlers Structure

### ⚡ RECOMMENDED: Single File Approach (v2.7.0)

Create **ONE file** `handlers.bsl` with ALL procedures:

```bsl
// ========================================
// Form Events
// ========================================

&НаКлиенте
Процедура ПриОткрытии(Отказ)
    Объект.Текст = "Готово к работе";
КонецПроцедуры

// ========================================
// Commands
// ========================================

&НаКлиенте
Процедура Сформировать(Команда)
    СформироватьНаСервере();
КонецПроцедуры

&НаСервере
Процедура СформироватьНаСервере()
    Результаты.Clear();
    // Server logic
    ЗагрузитьДанные();  // ← Calls helper function
КонецПроцедуры

// ========================================
// HELPERS (not in YAML - auto-detected!)
// ========================================

&НаСервере
Функция ЗагрузитьДанные()
    // Helper function called by multiple handlers
    // Generator auto-detects this as helper
    Query = New Query;
    Query.Text = "SELECT ...";
    Return Query.Execute().Unload();
КонецФункции
```

**✨ Key features:**
- ✅ ALL procedures in one file (handlers + helpers)
- ✅ Generator auto-detects helpers (procedures NOT in YAML)
- ✅ Helpers placed in "СлужебныеПроцедурыИФункції" section
- ✅ 5-10x faster for LLMs to generate
- ✅ Easier to maintain related code together

**Usage:**
```bash
python -m 1c_processor_generator yaml --config config.yaml --handlers-file handlers.bsl
```

---

### 📁 Legacy: Multiple Files Approach (still supported)

```
handlers/
├── FormEvents/
│   ├── ПриОткрытии.bsl
│   └── ПриСозданииНаСервере.bsl
├── Commands/
│   ├── Generate.bsl
│   ├── GenerateНаСервере.bsl
│   └── ЗагрузитьДанные.bsl    # Helper as separate file
```

**Usage:**
```bash
python -m 1c_processor_generator yaml --config config.yaml --handlers handlers/
```

---

### 🎨 BSL Procedure Formats

BSL files (or procedures in single file) can have two formats:

**Option 1: Body only** (generator adds signature):
```bsl
// ✅ Body only - signature added automatically
Объект.Result = Объект.Number1 + Объект.Number2;
```

**Option 2: Full procedure with signature** (used as-is):
```bsl
// ✅ Full signature - used as-is (useful for custom parameters)
&НаСервере
Процедура LoadDataНаСервере(RoleID)
    Data.Clear();
    // Load data based on RoleID
КонецПроцедуры
```

Generator auto-detects: if code starts with `&`, `Процедура`, `Функция`, `Procedure`, `Function`, `Асинх`, or `Async`, uses as-is; otherwise wraps in signature.

---

### 💡 Helper Functions Explained

**What are helpers?**
- Procedures/functions called by multiple handlers
- NOT specified in YAML (form.events, commands, element events)
- Generator auto-detects them and places in "СлужебныеПроцедурыИФункції" section

**Example:**
```yaml
# config.yaml - only lists main handlers
commands:
  - name: Сложить
    handler: Сложить
  - name: Умножить
    handler: Умножить
```

```bsl
// handlers.bsl - includes helper not in YAML
&НаКлиенте
Процедура Сложить(Команда)
    СложитьНаСервере();
КонецПроцедуры

&НаСервере
Процедура СложитьНаСервере()
    Объект.Результат = ВыполнитьОперацию("+");  // ← Calls helper
КонецПроцедуры

// ⭐ This is a HELPER - not in YAML!
&НаСервере
Функция ВыполнитьОперацию(Операция)
    // Shared logic used by multiple handlers
    Если Операция = "+" Тогда
        Возврат Объект.Число1 + Объект.Число2;
    КонецЕсли;
КонецФункции
```

**Result:** Generator automatically places `ВыполнитьОперацію` in helpers section.

---

## 💡 Common Use Cases

### Use Case 1: "Generate sales report for the month"

**Analysis:**
- Input: Date period (StartDate, EndDate)
- Output: Table with sales data
- Action: Generate button
- Pattern: Report with Table

**YAML:**
```yaml
processor:
  name: ОтчетПоПродажам
  synonym_ru: Отчет по продажам
  synonym_uk: Звіт по продажах

attributes:
  - name: ДатаНачала
    type: date
  - name: ДатаОкончания
    type: date

forms:
  - name: Форма
    default: true

    value_tables:
      - name: Результаты
        columns:
          - name: Месяц
            type: string
            length: 20
          - name: Сумма
            type: number
            digits: 15
            fraction_digits: 2

    elements:
      - type: InputField
        name: ДатаНачалаПоле
        attribute: ДатаНачала
      - type: InputField
        name: ДатаОкончанияПоле
        attribute: ДатаОкончания
      - type: Button
        name: СформироватьКнопка
        command: Сформировать
      - type: Table
        name: РезультатыТаблица
        tabular_section: Результаты
        properties:
          is_value_table: true

    commands:
      - name: Сформировать
        title_ru: Сформировать
        title_uk: Сформувати
        handler: Сформировать
```

---

### Use Case 2: "Import data from file"

**Analysis:**
- Input: File path
- Process: Load, validate, import
- Pattern: Wizard (select file → preview → import)

**YAML:**
```yaml
processor:
  name: ИмпортДанных

attributes:
  - name: ПутьКФайлу
    type: string
    length: 500

forms:
  - name: Форма
    default: true

    value_tables:
      - name: Предпросмотр
        columns:
          - name: Данные
            type: string
            length: 500

    elements:
      - type: Pages
        name: Этапы
        pages:
          - name: Шаг1
            title: Выбор файла
            child_items:
              - type: InputField
                name: ПутьКФайлуПоле
                attribute: ПутьКФайлу
              - type: Button
                name: ВыбратьКнопка
                command: ВыбратьФайл
          - name: Шаг2
            title: Предпросмотр
            child_items:
              - type: Table
                name: ПредпросмотрТаблица
                tabular_section: Предпросмотр
                properties:
                  is_value_table: true
              - type: Button
                name: ИмпортКнопка
                command: Импорт

    commands:
      - name: ВыбратьФайл
        title_ru: Выбрать файл
        title_uk: Вибрати файл
        handler: ВыбратьФайл
      - name: Импорт
        title_ru: Импорт
        title_uk: Імпорт
        handler: Импорт
```

---

### Use Case 3: "User selection wizard"

**Analysis:**
- Step 1: Select user
- Step 2: Select role
- Step 3: Confirm and apply
- Pattern: Wizard

**YAML:**
```yaml
processor:
  name: УстановкаРоли

attributes:
  - name: Пользователь
    type: CatalogRef.Пользователи
  - name: Роль
    type: string
    length: 100

forms:
  - name: Форма
    default: true

    elements:
      - type: Pages
        name: Шаги
        pages:
          - name: ШагПользователь
            title: Выбор пользователя
            child_items:
              - type: InputField
                name: ПользовательПоле
                attribute: Пользователь
          - name: ШагРоль
            title: Выбор роли
            child_items:
              - type: InputField
                name: РольПоле
                attribute: Роль
          - name: ШагПодтверждение
            title: Подтверждение
            child_items:
              - type: LabelDecoration
                name: Информация
                properties:
                  title: Нажмите кнопку для применения
              - type: Button
                name: ПрименитьКнопка
                command: Применить

    commands:
      - name: Применить
        title_ru: Применить
        title_uk: Застосувати
        handler: Применить
```

---

### Pattern 10: SpreadsheetDocument Report (v2.15.1+)

**Use case:** Formatted report with drill-down support

**⚠️ CRITICAL:** Use `form_attributes:` for SpreadsheetDocument (NOT `attributes:`!)

```yaml
processor:
  name: ПримерОтчета

attributes:
  # Regular attributes (saved to processor metadata)
  - name: Период
    type: date
    synonym_ru: Период

forms:
  - name: Форма
    default: true

    form_attributes:
      # Form-only attribute (NOT in processor metadata)
      - name: Отчет
        type: spreadsheet_document
        synonym_ru: Отчет

    elements:
      - type: InputField
        name: Период
        attribute: Период

      - type: SpreadSheetDocumentField
        name: ОтчетПоле
        attribute: Отчет  # DataPath: Отчет (NO "Объект." prefix!)
        title_location: None
        vertical_scrollbar: true
        horizontal_scrollbar: true
        events:
          DetailProcessing: ОтчетПолеОбработкаРасшифровки

      - type: Button
        name: СформироватьКнопка
        command: Сформировать

    commands:
      - name: Сформировать
        title_ru: Сформировать
        handler: Сформировать
        picture: StdPicture.GenerateReport
        shortcut: F5

    events:
      OnCreateAtServer: ПриСозданииНаСервере
```

**handlers.bsl:**
```bsl
&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
    Объект.Период = ТекущаяДата();
КонецПроцедуры

&НаКлиенте
Процедура Сформировать(Команда)
    СформироватьНаСервере();
КонецПроцедуры

&НаСервере
Процедура СформироватьНаСервере()
    Отчет.Очистить();
    ТабДок = Новый ТабличныйДокумент;

    // Header
    Область = ТабДок.Область(1, 1, 1, 3);
    Область.Текст = "Отчет за период: " + Формат(Объект.Период, "ДФ='dd.MM.yyyy'");
    Область.Шрифт = Новый Шрифт(, 14, Истина);

    // Data rows with drill-down
    Для Индекс = 1 По 10 Цикл
        Строка = 2 + Индекс;
        ТабДок.Область(Строка, 1).Текст = "Элемент " + Формат(Индекс, "ЧГ=0");
        ТабДок.Область(Строка, 2).Текст = Формат(Индекс * 100, "ЧДЦ=2");

        // Add drill-down details
        ТабДок.Область(Строка, 1, Строка, 2).Расшифровка = "Details_" + Формат(Индекс, "ЧГ=0");
    КонецЦикла;

    Отчет = ТабДок;
КонецПроцедуры

&НаКлиенте
Процедура ОтчетПолеОбработкаРасшифровки(Элемент, Расшифровка, СтандартнаяОбработка)
    СтандартнаяОбработка = Ложь;
    Если ТипЗнч(Расшифровка) = Тип("Строка") Тогда
        Сообщить("Клик по элементу: " + Расшифровка);
    КонецЕсли;
КонецПроцедуры
```

**Key points:**
- ✅ `form_attributes:` (NOT `attributes:`) for SpreadsheetDocument
- ✅ DataPath without "Объект." prefix: `Отчет` (not `Объект.Отчет`)
- ✅ DetailProcessing event for drill-down support
- ✅ Use `Отчет` directly in BSL (not `Объект.Отчет`)

---

### Pattern 11: Dashboard (KPI Cards with Loading State) - v2.46.0+

**Use case:** Display key performance indicators with trends and loading state

**Key features:**
- KPI cards with colored trend indicators (↑↓→)
- Loading State pattern (shows spinner while data loads)
- FormattedString for colored text
- Period navigation

```yaml
processor:
  name: ПростойДашборд
  synonym:
    ru: Простой дашборд показателей

attributes:
  # KPI values
  - name: ВсегоПродаж
    type: number
    digits: 15
    fraction_digits: 2
  - name: КоличествоЗаказов
    type: number
    digits: 10

forms:
  - name: Форма
    default: true
    events:
      OnCreateAtServer: ПриСозданииНаСервере

    elements:
      # Header
      - type: LabelDecoration
        name: Заголовок
        title_ru: "ПАНЕЛЬ ПОКАЗАТЕЛЕЙ"
        font:
          bold: true
          height: 14
        horizontal_align: Center

      # Period selector
      - type: UsualGroup
        name: ГруппаПериод
        group_direction: Horizontal
        child_items:
          - type: InputField
            name: ПериодС
            attribute: ПериодС
            width: 12
          - type: Button
            name: КнопкаОбновить
            command: Обновить

      # Loading/Content Pages (Loading State Pattern)
      - type: Pages
        name: СтраницыКонтент
        pages_representation: None  # Hide tabs - controlled programmatically
        pages:
          # Loading page
          - name: СтраницаЗагрузка
            child_items:
              - type: UsualGroup
                name: ГруппаЗагрузка
                horizontal_align: Center
                child_items:
                  - type: PictureDecoration
                    name: КартинкаЗагрузка
                    picture: StdPicture.Information
                    width: 5
                    height: 5
                  - type: LabelDecoration
                    name: ТекстЗагрузка
                    title_ru: "Загрузка данных..."
                    horizontal_align: Center

          # KPI Cards page
          - name: СтраницаПоказатели
            child_items:
              # KPI cards row
              - type: UsualGroup
                name: РядПоказателей
                group_direction: Horizontal
                child_items:
                  # Card 1: Sales
                  - type: UsualGroup
                    name: КарточкаПродажи
                    group_direction: Vertical
                    representation: StrongSeparation
                    child_items:
                      - type: LabelDecoration
                        name: ЗаголовокПродажи
                        title_ru: "ПРОДАЖИ"
                        font:
                          bold: true
                        horizontal_align: Center
                      - type: LabelField
                        name: ЗначениеПродажи
                        attribute: ВсегоПродаж
                        horizontal_align: Center
                      # Colored trend with FormattedString
                      - type: LabelDecoration
                        name: ТрендПродажи
                        title_ru: "↑ +12.5%"
                        formatted: true  # Enable FormattedString
                        horizontal_align: Center

    commands:
      - name: Обновить
        title_ru: Обновить
        handler: ОбновитьДанные
        picture: StdPicture.Refresh
```

**handlers.bsl:**
```bsl
//# ПриСозданииНаСервере
    // Show loading page initially
    Элементы.СтраницыКонтент.ТекущаяСтраница = Элементы.СтраницаЗагрузка;

    // Load data
    ЗагрузитьДанныеНаСервере();

    // Switch to content page
    Элементы.СтраницыКонтент.ТекущаяСтраница = Элементы.СтраницаПоказатели;

//# ЗагрузитьДанныеНаСервере
&НаСервере
Процедура ЗагрузитьДанныеНаСервере()
    // Load KPI data from database
    Объект.ВсегоПродаж = 1250000.50;
    Объект.КоличествоЗаказов = 847;

    // Update trend labels with colors
    ОбновитьТрендМетку(Элементы.ТрендПродажи, 12.5, "up");
КонецПроцедуры

//# ОбновитьТрендМетку
&НаСервере
Процедура ОбновитьТрендМетку(Элемент, Изменение, Направление)
    Если Направление = "up" Тогда
        Элемент.Заголовок = Новый ФорматированнаяСтрока(
            "↑ +" + Формат(Изменение, "ЧДЦ=1") + "%",
            Новый Шрифт(,,Истина),
            WebЦвета.Зеленый);
    ИначеЕсли Направление = "down" Тогда
        Элемент.Заголовок = Новый ФорматированнаяСтрока(
            "↓ " + Формат(Изменение, "ЧДЦ=1") + "%",
            Новый Шрифт(,,Истина),
            WebЦвета.Красный);
    Иначе
        Элемент.Заголовок = "→ 0.0%";
    КонецЕсли;
КонецПроцедуры
```

**Key patterns:**
- ✅ **Loading State:** Pages with `pages_representation: None` for programmatic switching
- ✅ **KPI Cards:** UsualGroup with `representation: StrongSeparation`
- ✅ **Colored Trends:** LabelDecoration with `formatted: true` + FormattedString in BSL
- ✅ **PictureDecoration:** For loading indicator icons

**See example:** `examples/yaml/simple_dashboard/`

---

### Pattern 12: Task Manager (Master-Detail CRUD) (v2.46.0+)

**Use case:** Task management with status filtering, priority indicators, CRUD operations

**Key features:**
- Master-Detail for task list and details
- Status-based filtering (via CheckBoxField or ChoiceList)
- Priority indicators with FormattedString
- CRUD operations (Add, Edit, Delete, Complete)

**Note:** This pattern uses Table with filtering, NOT drag-drop Kanban. For visual scheduling with drag-drop, see Pattern 13 (PlannerField).

```yaml
processor:
  name: ДиспетчерЗадач
  synonym:
    ru: Диспетчер задач

attributes:
  - name: ФильтрСтатус
    type: string
    length: 20
  - name: ТекущееНазвание
    type: string
    length: 200

value_tables:
  - name: СписокЗадач
    columns:
      - name: Название
        type: string
        length: 200
      - name: Статус
        type: string
        length: 20
      - name: Приоритет
        type: string
        length: 20
      - name: Срок
        type: date
      - name: Описание
        type: string

forms:
  - name: Форма
    default: true
    events:
      OnCreateAtServer: ПриСозданииНаСервере

    elements:
      # Toolbar with status filter
      - type: UsualGroup
        name: ГруппаТулбар
        group_direction: Horizontal
        child_items:
          - type: InputField
            name: ФильтрСтатусПоле
            attribute: ФильтрСтатус
            width: 15
            list_choice_mode: true
            choice_list:
              - value: ""
                presentation_ru: "Все"
              - value: "Новая"
                presentation_ru: "Новые"
              - value: "В работе"
                presentation_ru: "В работе"
              - value: "Готово"
                presentation_ru: "Готовые"
            events:
              OnChange: ФильтрИзменен

      # Master-Detail layout
      - type: UsualGroup
        name: ГруппаСодержимое
        group_direction: Horizontal
        child_items:
          # Master: Task list
          - type: Table
            name: ТаблицаЗадач
            tabular_section: СписокЗадач
            width: 50
            height: 15
            events:
              OnActivateRow: ЗадачиПриАктивизацииСтроки
            columns:
              - name: Название
                attribute: СписокЗадач.Название
                width: 25
              - name: Статус
                attribute: СписокЗадач.Статус
                width: 10
              - name: Приоритет
                attribute: СписокЗадач.Приоритет
                width: 10

          # Detail: Selected task
          - type: UsualGroup
            name: ГруппаДетали
            group_direction: Vertical
            representation: StrongSeparation
            child_items:
              - type: LabelDecoration
                name: ЗаголовокДетали
                title_ru: "Детали задачи"
                font:
                  bold: true
              - type: InputField
                name: ТекущееНазваниеПоле
                attribute: ТекущееНазвание
                title_ru: "Название"
              # Status change buttons
              - type: UsualGroup
                name: ГруппаСменыСтатуса
                group_direction: Horizontal
                child_items:
                  - type: Button
                    name: КнопкаВРаботу
                    command: ВзятьВРаботу
                  - type: Button
                    name: КнопкаГотово
                    command: ОтметитьГотово

    commands:
      - name: ДобавитьЗадачу
        title_ru: Добавить
        handler: ДобавитьЗадачуКоманда
        picture: StdPicture.CreateListItem

      - name: ВзятьВРаботу
        title_ru: В работу
        handler: ВзятьВРаботуКоманда
        picture: StdPicture.ExecuteTask

      - name: ОтметитьГотово
        title_ru: Готово
        handler: ОтметитьГотовоКоманда
        picture: StdPicture.Post
```

**handlers.bsl:**
```bsl
//# ЗадачиПриАктивизацииСтроки
    // Master-Detail: Update details panel
    ОбновитьДеталиЗадачиНаСервере();

//# ФильтрИзменен
    ПрименитьФильтрНаСервере();

//# ОбновитьДеталиЗадачиНаСервере
&НаСервере
Процедура ОбновитьДеталиЗадачиНаСервере()
    ТекущаяСтрока = Элементы.ТаблицаЗадач.ТекущаяСтрока;
    Если ТекущаяСтрока = Неопределено Тогда
        Возврат;
    КонецЕсли;

    ДанныеСтроки = Объект.СписокЗадач.НайтиПоИдентификатору(ТекущаяСтрока);
    Если ДанныеСтроки <> Неопределено Тогда
        Объект.ТекущееНазвание = ДанныеСтроки.Название;
    КонецЕсли;
КонецПроцедуры

//# ВзятьВРаботуКоманда
    ИзменитьСтатусЗадачиНаСервере("В работе");

//# ИзменитьСтатусЗадачиНаСервере
&НаСервере
Процедура ИзменитьСтатусЗадачиНаСервере(НовыйСтатус)
    ТекущаяСтрока = Элементы.ТаблицаЗадач.ТекущаяСтрока;
    Если ТекущаяСтрока = Неопределено Тогда
        Возврат;
    КонецЕсли;

    ДанныеСтроки = Объект.СписокЗадач.НайтиПоИдентификатору(ТекущаяСтрока);
    Если ДанныеСтроки <> Неопределено Тогда
        ДанныеСтроки.Статус = НовыйСтатус;
    КонецЕсли;
КонецПроцедуры
```

**Key patterns:**
- ✅ **Master-Detail:** Table with OnActivateRow → detail panel update
- ✅ **Status Filtering:** ChoiceList + OnChange event
- ✅ **CRUD Operations:** Add/Edit/Delete commands
- ✅ **Status Workflow:** Buttons for changing task status

**Limitations (no native drag-drop):**
- Use commands/buttons for status changes instead of drag-drop
- Filter by status to simulate "columns"

**See example:** `examples/yaml/task_manager/`

---

### Pattern 13: Contact Center / Planner (v2.47.0+)

**Use case:** Multi-form processor with call journal, schedule (PlannerField), and reports

**Key features:**
- Multiple forms (Main, Report, Schedule)
- SpreadSheetDocumentField for reports
- **PlannerField with pl:Planner type** for visual scheduling with drag-drop
- CalendarField for date navigation
- ValueTables for call log

**Important:** PlannerField requires a special `planner` type attribute (generates `pl:Planner` XML type with Settings). This is NOT a ValueTable!

```yaml
processor:
  name: КонтактЦентрЛайт
  synonym:
    ru: Контакт-центр Лайт

attributes:
  - name: ТекущаяДата
    type: date
  - name: ЗвонковСегодня
    type: number
    digits: 10

forms:
  - name: Форма
    default: true
    events:
      OnCreateAtServer: ПриСозданииНаСервере

    # PlannerField requires planner type form_attribute (NOT ValueTable!)
    form_attributes:
      - name: Планировщик
        type: planner           # Special type: generates pl:Planner with Settings
        time_scale: Hour        # Hour, Day, Week, Month
        time_scale_interval: 1
        display_current_date: true
        show_weekends: true

    value_tables:
      - name: ЖурналЗвонков
        columns:
          - name: Время
            type: date
          - name: Клиент
            type: string
            length: 200
          - name: Статус
            type: string
            length: 20

    elements:
      # Statistics header
      - type: UsualGroup
        name: ГруппаШапка
        group_direction: Horizontal
        child_items:
          - type: LabelDecoration
            name: Заголовок
            title_ru: "КОНТАКТ-ЦЕНТР"
            font:
              bold: true
              height: 14
          - type: LabelField
            name: ЗвонковСегодня
            attribute: ЗвонковСегодня
            title_ru: "Звонков:"

      # Tabs: Journal and Planner
      - type: Pages
        name: СтраницыКонтент
        pages:
          - name: СтраницаЖурнал
            title_ru: Журнал звонков
            child_items:
              - type: Table
                name: ТаблицаЗвонков
                tabular_section: ЖурналЗвонков
                events:
                  OnActivateRow: ЗвонкиПриАктивизацииСтроки

          - name: СтраницаПланировщик
            title_ru: Расписание
            child_items:
              - type: UsualGroup
                name: ГруппаПланировщик
                group_direction: Horizontal
                child_items:
                  # Calendar for date selection
                  - type: CalendarField
                    name: КалендарьВыбора
                    attribute: ТекущаяДата
                    width: 10
                    events:
                      OnChange: КалендарьПриИзменении
                  # PlannerField with drag-drop
                  - type: PlannerField
                    name: ПланировщикОператоров
                    attribute: Планировщик   # References form_attribute, NOT ValueTable!
                    height: 15
                    enable_drag: true        # Enable drag-drop scheduling
                    events:
                      Drag: ПланировщикПеретаскивание
                      DragCheck: ПланировщикПроверкаПеретаскивания
                      BeforeCreate: ПланировщикПередСозданием
                      OnEditEnd: ПланировщикПриОкончанииРедактирования

    commands:
      - name: Обновить
        title_ru: Обновить
        handler: ОбновитьКоманда
        picture: StdPicture.Refresh

      - name: ОткрытьОтчет
        title_ru: Отчет
        handler: ОткрытьОтчетКоманда
        picture: StdPicture.Report

  # Report form with SpreadSheet
  - name: ФормаОтчет
    events:
      OnCreateAtServer: ОтчетПриСозданииНаСервере

    form_attributes:
      - name: ОтчетЗвонки
        type: spreadsheet_document  # Note: lowercase with underscore
        synonym_ru: Отчет по звонкам

    elements:
      - type: LabelDecoration
        name: ЗаголовокОтчета
        title_ru: "ОТЧЕТ ПО ЗВОНКАМ"
        font:
          bold: true
          height: 12

      # Report parameters with ChoiceList
      - type: UsualGroup
        name: ГруппаПараметры
        group_direction: Horizontal
        child_items:
          - type: InputField
            name: ОтчетПериодС
            attribute: ОтчетПериодС
            width: 12
          - type: InputField
            name: ОтчетОператор
            attribute: ОтчетОператор
            list_choice_mode: true
            choice_list:
              - value: ""
                presentation_ru: "Все"
              - value: "Иванов И.И."
                presentation_ru: "Иванов И.И."
          - type: Button
            name: КнопкаСформировать
            command: СформироватьОтчет

      # SpreadSheet for report output
      - type: SpreadSheetDocumentField
        name: ТабличныйДокумент
        attribute: ОтчетЗвонки
        width: 80
        height: 20

    commands:
      - name: СформироватьОтчет
        title_ru: Сформировать
        handler: СформироватьОтчетКоманда
        picture: StdPicture.GenerateReport
```

**handlers.bsl:**
```bsl
//# ПриСозданииНаСервере
    // Load demo call data
    ЗагрузитьДемоДанныеЗвонковНаСервере();
    ОбновитьСтатистикуНаСервере();

//# ЗвонкиПриАктивизацииСтроки
    // Master-Detail for call details
    ОбновитьДеталиЗвонкаНаСервере();

//# ОткрытьОтчетКоманда
    // Open report form
    ОткрытьФорму("ВнешняяОбработка.КонтактЦентрЛайт.Форма.ФормаОтчет");

//# ОтчетПриСозданииНаСервере
    // Initialize report period
    Объект.ОтчетПериодС = НачалоМесяца(ТекущаяДата());
    Объект.ОтчетПериодПо = КонецМесяца(ТекущаяДата());

//# СформироватьОтчетКоманда
    СформироватьОтчетНаСервере();

//# СформироватьОтчетНаСервере
&НаСервере
Процедура СформироватьОтчетНаСервере()
    // Get template and fill with data
    Макет = ПолучитьМакет("ОтчетЗвонки");
    // Fill report logic...
    Сообщить("Отчет сформирован");
КонецПроцедуры
```

**Key patterns:**
- ✅ **Multiple Forms:** Main + Report forms, opened via `ОткрытьФорму()`
- ✅ **SpreadSheetDocumentField:** For formatted reports (uses `form_attributes`)
- ✅ **PlannerField:** Schedule/calendar view (v2.46.0+)
- ✅ **Statistics Header:** Live counters with LabelField
- ✅ **ChoiceList Filtering:** Dropdown for operator selection

**Form-level vs Processor-level:**
- `attributes:` - Processor-level, shared across all forms
- `form_attributes:` - Form-level only (SpreadsheetDocument, HTMLDocument)
- `value_tables:` - Can be at processor or form level

**See example:** `examples/yaml/contact_center_lite/`

---

### Pattern 14: Tree / Hierarchical Data (v2.64.0+)

**Use case:** Display hierarchical data as expandable tree (JSON viewer, folder structure, org chart)

**When to use:**
- ✅ Hierarchical data (folders, categories, org structures)
- ✅ JSON/XML viewer with nested structure
- ✅ Configuration tree with settings and subsettings
- ✅ Any parent-child relationships

**Architecture:**
- `value_trees:` section (NOT value_tables!) defines tree attribute
- `Table` element with `representation: tree`
- Tree-specific properties: `initial_tree_view`, `show_root`, etc.

```yaml
processor:
  name: JSONViewer
  synonym:
    ru: Просмотр JSON
    uk: Перегляд JSON

forms:
  - name: Форма
    default: true

    value_trees:
      - name: DataTree
        title:
          ru: Дерево данных
          uk: Дерево даних
        columns:
          - name: Name
            type: string
          - name: Value
            type: string
          - name: NodeType
            type: string
            length: 50
          - name: HasChildren
            type: boolean

    elements:
      - type: Table
        name: TreeTable
        tabular_section: DataTree
        representation: tree
        initial_tree_view: expand_top_level
        show_root: false
        allow_root_choice: false
        columns:
          - name: Name
          - name: Value
          - name: NodeType

      - type: UsualGroup
        name: ButtonsGroup
        group_direction: Horizontal
        child_items:
          - type: Button
            name: RefreshButton
            command: Refresh
          - type: Button
            name: LoadJSONButton
            command: LoadJSON

    commands:
      - name: Refresh
        title:
          ru: Обновить
          uk: Оновити
        handler: Refresh
        picture: StdPicture.Refresh
        shortcut: F5

      - name: LoadJSON
        title:
          ru: Загрузить JSON
          uk: Завантажити JSON
        handler: LoadJSON
        picture: StdPicture.OpenFile
```

**handlers.bsl:**
```bsl
#Область ОбработчикиКомандФормы

&НаКлиенте
Процедура Refresh(Команда)
    RefreshНаСервере();
КонецПроцедуры

&НаСервере
Процедура RefreshНаСервере()
    FillTreeWithSample();
КонецПроцедуры

&НаКлиенте
Процедура LoadJSON(Команда)
    Dialog = New FileDialog(FileDialogMode.Open);
    Dialog.Filter = "JSON files (*.json)|*.json";
    Dialog.Title = "Select JSON file";

    If Dialog.Choose() Then
        LoadJSONFileНаСервере(Dialog.FullFileName);
    EndIf;
КонецПроцедуры

#КонецОбласти

#Область СлужебныеПроцедурыИФункции

&НаСервере
Процедура FillTreeWithSample()
    // Clear tree
    DataTree.GetItems().Clear();

    // Root level: Settings object
    Settings = DataTree.GetItems().Add();
    Settings.Name = "Settings";
    Settings.NodeType = "Object";
    Settings.HasChildren = True;

    // Level 2: Database section
    DB = Settings.GetItems().Add();
    DB.Name = "Database";
    DB.NodeType = "Object";
    DB.HasChildren = True;

    // Level 3: Database properties
    Host = DB.GetItems().Add();
    Host.Name = "Host";
    Host.Value = "localhost";
    Host.NodeType = "Value";

    Port = DB.GetItems().Add();
    Port.Name = "Port";
    Port.Value = "5432";
    Port.NodeType = "Value";

    // Level 2: API section
    API = Settings.GetItems().Add();
    API.Name = "API";
    API.NodeType = "Object";
    API.HasChildren = True;

    Token = API.GetItems().Add();
    Token.Name = "Token";
    Token.Value = "***hidden***";
    Token.NodeType = "Value";
КонецПроцедуры

&НаСервере
Процедура LoadJSONFileНаСервере(FilePath)
    Try
        TextReader = New TextReader(FilePath, TextEncoding.UTF8);
        JSONContent = TextReader.Read();
        TextReader.Close();

        JSONReader = New JSONReader;
        JSONReader.SetString(JSONContent);
        JSONData = ReadJSON(JSONReader);
        JSONReader.Close();

        // Clear tree and fill from JSON
        DataTree.GetItems().Clear();
        FillTreeFromValue(DataTree.GetItems(), "JSON", JSONData);
    Except
        Message("Error loading JSON: " + ErrorDescription());
    EndTry;
КонецПроцедуры

&НаСервере
Процедура FillTreeFromValue(ParentItems, Key, Value)
    // Recursive function to build tree from any value
    ValueType = TypeOf(Value);

    If ValueType = Type("Structure") OR ValueType = Type("Map") Then
        // Object
        Node = ParentItems.Add();
        Node.Name = Key;
        Node.NodeType = "Object";
        Node.HasChildren = True;

        For Each KeyValue In Value Do
            FillTreeFromValue(Node.GetItems(), KeyValue.Key, KeyValue.Value);
        EndDo;

    ElsIf ValueType = Type("Array") Then
        // Array
        Node = ParentItems.Add();
        Node.Name = Key;
        Node.NodeType = "Array";
        Node.HasChildren = True;

        For Index = 0 To Value.UBound() Do
            FillTreeFromValue(Node.GetItems(), "[" + Index + "]", Value[Index]);
        EndDo;

    Else
        // Primitive value
        Node = ParentItems.Add();
        Node.Name = Key;
        Node.Value = String(Value);
        Node.NodeType = "Value";
        Node.HasChildren = False;
    EndIf;
КонецПроцедуры

#КонецОбласти
```

**Tree Properties Reference:**
| Property | Values | Description |
|----------|--------|-------------|
| `representation` | `list`, `tree` | Table display mode (default: list) |
| `initial_tree_view` | `no_expand`, `expand_top_level`, `expand_all_levels` | Initial expansion state |
| `show_root` | `true`, `false` | Show/hide root element |
| `allow_root_choice` | `true`, `false` | Allow selecting root node |
| `choice_folders_and_items` | `folders`, `items`, `folders_and_items` | What can be selected |

**BSL Tree Navigation:**
```bsl
// Get children of current node
Children = Node.GetItems();

// Get parent of current node
Parent = Node.GetParent();

// Clear all children
Node.GetItems().Clear();

// Add child node
Child = Node.GetItems().Add();
Child.Name = "New Child";

// Access root items
RootItems = DataTree.GetItems();
```

**When to use ValueTree:**
- ✅ Hierarchical structures (folder trees, categories)
- ✅ JSON/XML visualization
- ✅ Nested configurations
- ✅ Parent-child data

**When NOT to use ValueTree (use ValueTable):**
- ❌ Flat tabular data
- ❌ Simple lists without hierarchy
- ❌ Data without parent-child relationships

**See example:** `examples/yaml/tree_example/`

---

**Version:** 2.64.0
**Last updated:** 2025-12-28
**Main document:** [LLM_PROMPT.md](LLM_PROMPT.md)
