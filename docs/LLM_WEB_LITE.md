# 1C Processor Generator - Web Chat Edition

> **Target:** ~5K tokens | **Covers:** 80% use cases | **For:** ChatGPT, Gemini, Claude Web

---

## What is this?

A YAML+BSL to 1C:Enterprise external processor (.epf) generator. You write simple YAML config + BSL handlers, generator creates valid 1C XML files.

**Workflow:**
1. LLM generates `config.yaml` + `handlers.bsl`
2. User runs: `python -m 1c_processor_generator yaml --config config.yaml --handlers-file handlers.bsl`
3. Generator outputs XML or EPF

---

## YAML Structure (Essential)

```yaml
processor:
  name: МояОбробка              # Internal name (Latin or Cyrillic)
  synonym_ru: Моя обработка     # Display name Russian
  synonym_uk: Моя обробка       # Display name Ukrainian

attributes:                      # Processor-level data
  - name: Поле1
    type: string
    length: 100

forms:
  - name: Форма
    default: true
    elements: []                 # UI elements
    commands: []                 # Actions
```

---

## Data Types

| Type | YAML | Notes |
|------|------|-------|
| String | `type: string, length: 100` | `length: 0` = unlimited |
| Number | `type: number, digits: 15, fraction_digits: 2` | |
| Boolean | `type: boolean` | |
| Date | `type: date` | |
| CatalogRef | `type: CatalogRef.Контрагенты` | Reference to catalog |
| DocumentRef | `type: DocumentRef.Заказ` | Reference to document |

---

## Form Elements

| Element | Key Properties |
|---------|---------------|
| `InputField` | `attribute`, `width`, `multiline`, `read_only` |
| `Table` | `tabular_section`, `is_value_table`, `columns` |
| `Button` | `command` |
| `LabelDecoration` | `title`, `font` |
| `UsualGroup` | `child_items`, `group_direction` |
| `Pages` | `pages` |

**Example:**
```yaml
elements:
  - type: InputField
    name: Поле1Поле
    attribute: Поле1
    width: 30
  - type: Button
    name: ВыполнитьКнопка
    command: Выполнить
```

---

## Pattern 1: Simple Form

**Use:** Data entry, settings, simple actions

```yaml
processor:
  name: ПростаяОбробка
  synonym_ru: Простая обработка

attributes:
  - name: Имя
    type: string
    length: 150
  - name: Дата
    type: date
  - name: Сумма
    type: number
    digits: 15
    fraction_digits: 2

forms:
  - name: Форма
    default: true
    elements:
      - type: InputField
        name: ИмяПоле
        attribute: Имя
      - type: InputField
        name: ДатаПоле
        attribute: Дата
      - type: InputField
        name: СуммаПоле
        attribute: Сумма
      - type: Button
        name: ВыполнитьКнопка
        command: Выполнить
    commands:
      - name: Выполнить
        title_ru: Выполнить
        title_uk: Виконати
        handler: Выполнить
```

**handlers.bsl:**
```bsl
&НаКлиенте
Процедура Выполнить(Команда)
    Если НЕ ЗначениеЗаполнено(Объект.Имя) Тогда
        Сообщить("Заполните имя!");
        Возврат;
    КонецЕсли;

    Сообщить("Имя: " + Объект.Имя + ", Сумма: " + Объект.Сумма);
КонецПроцедуры
```

---

## Pattern 2: Report with Table

**Use:** Data display, reports, lists

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
    value_tables:                    # Temporary table (not saved)
      - name: Результаты
        columns:
          - name: Товар
            type: string
            length: 150
          - name: Количество
            type: number
            digits: 10
          - name: Сумма
            type: number
            digits: 15
            fraction_digits: 2
    elements:
      - type: UsualGroup
        name: ФильтрыГруппа
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
        title_uk: Сформувати
        handler: Сформировать
```

**handlers.bsl:**
```bsl
&НаКлиенте
Процедура Сформировать(Команда)
    Если НЕ ЗначениеЗаполнено(Объект.НачалоПериода) Тогда
        Сообщить("Укажите начало периода!");
        Возврат;
    КонецЕсли;

    СформироватьНаСервере();
КонецПроцедуры

&НаСервере
Процедура СформироватьНаСервере()
    Результаты.Очистить();

    Запрос = Новый Запрос;
    Запрос.Текст = "
    |ВЫБРАТЬ
    |    Товары.Наименование КАК Товар,
    |    СУММА(Продажи.Количество) КАК Количество,
    |    СУММА(Продажи.Сумма) КАК Сумма
    |ИЗ
    |    РегистрНакопления.Продажи КАК Продажи
    |ЛЕВОЕ СОЕДИНЕНИЕ Справочник.Товары КАК Товары
    |    ПО Продажи.Товар = Товары.Ссылка
    |ГДЕ
    |    Продажи.Период МЕЖДУ &Начало И &Конец
    |СГРУППИРОВАТЬ ПО Товары.Наименование";

    Запрос.УстановитьПараметр("Начало", Объект.НачалоПериода);
    Запрос.УстановитьПараметр("Конец", Объект.КонецПериода);

    Выборка = Запрос.Выполнить().Выбрать();
    Пока Выборка.Следующий() Цикл
        НоваяСтрока = Результаты.Добавить();
        ЗаполнитьЗначенияСвойств(НоваяСтрока, Выборка);
    КонецЦикла;
КонецПроцедуры
```

---

## Pattern 3: Master-Detail

**Use:** Parent-child relationships (roles→users, categories→items)

```yaml
processor:
  name: УстановкаРолей
  synonym_ru: Установка ролей пользователей

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
          - name: ПолноеИмя
            type: string
            length: 200
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

**handlers.bsl:**
```bsl
&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
    // Load roles on form open
    Запрос = Новый Запрос("ВЫБРАТЬ Наименование ИЗ Справочник.Роли");
    Выборка = Запрос.Выполнить().Выбрать();
    Пока Выборка.Следующий() Цикл
        НоваяСтрока = Роли.Добавить();
        НоваяСтрока.Наименование = Выборка.Наименование;
    КонецЦикла;
КонецПроцедуры

&НаКлиенте
Процедура РолиПриАктивизацииСтроки(Элемент)
    ТекущиеДанные = Элементы.РолиТаблица.ТекущиеДанные;
    Если ТекущиеДанные = Неопределено Тогда
        Возврат;
    КонецЕсли;

    РолиПриАктивизацииСтрокиНаСервере(ТекущиеДанные.Наименование);
КонецПроцедуры

&НаСервере
Процедура РолиПриАктивизацииСтрокиНаСервере(Роль)
    // Load users for selected role
    Пользователи.Очистить();

    Если НЕ ЗначениеЗаполнено(Роль) Тогда
        Возврат;
    КонецЕсли;

    Запрос = Новый Запрос;
    Запрос.Текст = "
    |ВЫБРАТЬ Логин, ПолноеИмя
    |ИЗ Справочник.Пользователи
    |ГДЕ Роль.Наименование = &Роль";
    Запрос.УстановитьПараметр("Роль", Роль);

    Выборка = Запрос.Выполнить().Выбрать();
    Пока Выборка.Следующий() Цикл
        НоваяСтрока = Пользователи.Добавить();
        ЗаполнитьЗначенияСвойств(НоваяСтрока, Выборка);
    КонецЦикла;
КонецПроцедуры
```

---

## BSL Rules

### Handler Format
Put ALL handlers in one `handlers.bsl` file. Each handler is a procedure with directive:

```bsl
&НаКлиенте
Процедура HandlerName(Команда)
    // Client code here
КонецПроцедуры

&НаСервере
Процедура HandlerNameНаСервере()
    // Server code here
КонецПроцедуры
```

### Client-Server Pattern
Client procedure calls server procedure with `НаСервере` suffix:
```bsl
&НаКлиенте
Процедура Загрузить(Команда)
    ЗагрузитьНаСервере();  // Calls server procedure
КонецПроцедуры

&НаСервере
Процедура ЗагрузитьНаСервере()
    // Database queries, file operations
КонецПроцедуры
```

### Access Patterns

| Where | How | Example |
|-------|-----|---------|
| Processor attribute | `Объект.AttrName` | `Объект.Сумма` |
| ValueTable | `TableName` | `Результаты.Добавить()` |
| Form element | `Элементы.ElemName` | `Элементы.Таблица.ТекущиеДанные` |

---

## Common Errors

| Error | Fix |
|-------|-----|
| `attribute: X` not found | Declare in `attributes:` section |
| `tabular_section: X` not found | Declare in `value_tables:` or `tabular_sections:` |
| Table not showing data | Add `is_value_table: true` for ValueTable |
| Server code in client | Use `&НаСервере` directive for DB queries |
| Form doesn't open | Add `default: true` to form |

---

## Command Template

```yaml
commands:
  - name: CommandName
    title_ru: Русский заголовок
    title_uk: Український заголовок
    handler: CommandName          # References handlers.bsl procedure
    picture: StdPicture.ExecuteTask  # Optional icon
    shortcut: F5                  # Optional hotkey
```

**Popular pictures:** `ExecuteTask`, `SaveFile`, `OpenFile`, `Refresh`, `InputFieldClear`

---

## Generation Command

```bash
# Generate XML (always works)
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output output_dir

# Generate EPF (requires 1C Designer)
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output output_dir \
  --output-format epf
```

---

## Checklist Before Generation

- [ ] All `attribute:` values exist in `attributes:`
- [ ] All `tabular_section:` values exist in `value_tables:` or `tabular_sections:`
- [ ] All `command:` values exist in `commands:`
- [ ] All `handler:` values have procedures in `handlers.bsl`
- [ ] ValueTables have `is_value_table: true` on Table element
- [ ] Server procedures have `&НаСервере` directive
- [ ] Form has `default: true`

---

*Version: 2.58.0 | Full docs: [LLM_CORE.md](LLM_CORE.md)*
