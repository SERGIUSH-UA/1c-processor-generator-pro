# 1C Processor Generator - Knowledge Base

> For Custom GPT knowledge upload

---

## Complete YAML Reference

### Processor Section
```yaml
processor:
  name: ProcessorName         # Required, Latin or Cyrillic
  synonym_ru: Русское название
  synonym_uk: Українська назва
  synonym_en: English name    # Optional
  comment: Description        # Optional
```

### Attributes Section
```yaml
attributes:
  # String
  - name: StringField
    type: string
    length: 100               # 0 = unlimited

  # Number
  - name: NumberField
    type: number
    digits: 15                # Total digits
    fraction_digits: 2        # Decimal places

  # Date
  - name: DateField
    type: date

  # Boolean
  - name: BoolField
    type: boolean

  # Reference types
  - name: ClientRef
    type: CatalogRef.Контрагенты
  - name: DocRef
    type: DocumentRef.ЗаказКлиента
```

### Forms Section
```yaml
forms:
  - name: Форма
    default: true             # Main form

    # Events
    events:
      OnOpen: ПриОткрытии
      OnCreateAtServer: ПриСозданииНаСервере
      OnClose: ПриЗакрытии

    # Form properties
    properties:
      window_opening_mode: LockOwnerWindow  # Modal
      command_bar_location: Bottom
      auto_title: false
      title_ru: Заголовок

    # Temporary tables
    value_tables:
      - name: Results
        columns:
          - {name: Col1, type: string, length: 100}
          - {name: Col2, type: number, digits: 15, fraction_digits: 2}

    # UI elements
    elements: []

    # Commands (buttons)
    commands: []
```

---

## Form Elements Reference

### InputField
```yaml
- type: InputField
  name: FieldNameПоле
  attribute: FieldName
  width: 30                   # Characters
  height: 5                   # Rows (multiline)
  multiline: true
  read_only: true
  title_location: Left        # Left, Top, None
  events:
    OnChange: FieldOnChange
    StartChoice: FieldStartChoice
```

### Table
```yaml
- type: Table
  name: DataTable
  tabular_section: Data       # References value_tables.name
  is_value_table: true        # REQUIRED for ValueTable!
  height: 10                  # Rows
  horizontal_stretch: true
  read_only: true
  columns:                    # Override columns
    - name: Col1
      width: 20
      read_only: true
  events:
    OnActivateRow: TableOnActivateRow
    Selection: TableSelection
```

### Button
```yaml
- type: Button
  name: ActionButton
  command: Action             # References commands.name
  width: 15
  representation: PictureAndText  # Text, Picture, PictureAndText
```

### LabelDecoration
```yaml
- type: LabelDecoration
  name: TitleLabel
  title: "Title Text"
  font:
    bold: true
    italic: true
  horizontal_align: Center
```

### UsualGroup
```yaml
- type: UsualGroup
  name: FilterGroup
  title: Фильтры
  show_title: true
  group_direction: Horizontal # Vertical, Horizontal
  behavior: Collapsible       # Usual, Collapsible
  child_items:
    - type: InputField
      attribute: Filter1
    - type: InputField
      attribute: Filter2
```

### Pages
```yaml
- type: Pages
  name: MainPages
  pages_representation: TabsOnTop  # TabsOnTop, TabsOnBottom, None
  pages:
    - name: Page1
      title: Страница 1
      child_items:
        - type: InputField
          attribute: Field1
    - name: Page2
      title: Страница 2
      child_items:
        - type: Table
          tabular_section: Data
```

---

## Commands Reference

```yaml
commands:
  - name: Execute
    title_ru: Выполнить
    title_uk: Виконати
    handler: Execute           # BSL procedure name
    picture: StdPicture.ExecuteTask
    shortcut: F5
    tooltip_ru: Выполнить действие
```

### Common StdPicture Icons
| Icon | Use |
|------|-----|
| `StdPicture.ExecuteTask` | Execute, Run |
| `StdPicture.SaveFile` | Save, Export |
| `StdPicture.OpenFile` | Open, Import |
| `StdPicture.Refresh` | Refresh, Reload |
| `StdPicture.InputFieldClear` | Clear |
| `StdPicture.Find` | Search |
| `StdPicture.Delete` | Delete |
| `StdPicture.Add` | Add |
| `StdPicture.Edit` | Edit |
| `StdPicture.Print` | Print |

### Common Shortcuts
| Key | Use |
|-----|-----|
| `F5` | Execute |
| `Ctrl+S` | Save |
| `Ctrl+N` | New |
| `Delete` | Delete |
| `F1` | Help |

---

## BSL Handler Format

### Simple Procedure
```bsl
&НаКлиенте
Процедура Execute(Команда)
    Если НЕ ЗначениеЗаполнено(Объект.Field) Тогда
        Сообщить("Заполните поле!");
        Возврат;
    КонецЕсли;
    Сообщить("Готово!");
КонецПроцедуры
```

### Client + Server Pattern
```bsl
&НаКлиенте
Процедура LoadData(Команда)
    LoadDataНаСервере();
КонецПроцедуры

&НаСервере
Процедура LoadDataНаСервере()
    Results.Очистить();

    Запрос = Новый Запрос;
    Запрос.Текст = "ВЫБРАТЬ Наименование, Цена ИЗ Справочник.Товары";

    Выборка = Запрос.Выполнить().Выбрать();
    Пока Выборка.Следующий() Цикл
        НоваяСтрока = Results.Добавить();
        ЗаполнитьЗначенияСвойств(НоваяСтрока, Выборка);
    КонецЦикла;
КонецПроцедуры
```

### OnCreateAtServer
```bsl
&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
    // Initialize form data on server
    Объект.Date = ТекущаяДата();

    // Load initial data
    LoadInitialData();
КонецПроцедуры
```

### Table OnActivateRow (Master-Detail)
```bsl
&НаКлиенте
Процедура MasterTableOnActivateRow(Элемент)
    ТекущиеДанные = Элементы.MasterTable.ТекущиеДанные;
    Если ТекущиеДанные = Неопределено Тогда
        Возврат;
    КонецЕсли;

    MasterTableOnActivateRowНаСервере(ТекущиеДанные.ID);
КонецПроцедуры

&НаСервере
Процедура MasterTableOnActivateRowНаСервере(MasterID)
    DetailTable.Очистить();

    Если НЕ ЗначениеЗаполнено(MasterID) Тогда
        Возврат;
    КонецЕсли;

    Запрос = Новый Запрос;
    Запрос.Текст = "ВЫБРАТЬ * ИЗ Table WHERE MasterID = &ID";
    Запрос.УстановитьПараметр("ID", MasterID);

    Выборка = Запрос.Выполнить().Выбрать();
    Пока Выборка.Следующий() Цикл
        НоваяСтрока = DetailTable.Добавить();
        ЗаполнитьЗначенияСвойств(НоваяСтрока, Выборка);
    КонецЦикла;
КонецПроцедуры
```

### Try-Catch
```bsl
Попытка
    // Risky operation
    DoSomething();
Исключение
    Сообщить("Ошибка: " + ОписаниеОшибки());
КонецПопытки;
```

---

## Complete Examples

### Example 1: Simple Form
```yaml
processor:
  name: КалькуляторНДС
  synonym_ru: Калькулятор НДС
  synonym_uk: Калькулятор ПДВ

attributes:
  - name: Сумма
    type: number
    digits: 15
    fraction_digits: 2
  - name: Ставка
    type: number
    digits: 5
    fraction_digits: 2
  - name: СуммаНДС
    type: number
    digits: 15
    fraction_digits: 2

forms:
  - name: Форма
    default: true
    elements:
      - type: InputField
        name: СуммаПоле
        attribute: Сумма
        width: 15
      - type: InputField
        name: СтавкаПоле
        attribute: Ставка
        width: 10
      - type: InputField
        name: СуммаНДСПоле
        attribute: СуммаНДС
        read_only: true
        width: 15
      - type: Button
        name: РассчитатьКнопка
        command: Рассчитать
    commands:
      - name: Рассчитать
        title_ru: Рассчитать
        title_uk: Розрахувати
        handler: Рассчитать
        picture: StdPicture.ExecuteTask
```

**handlers.bsl:**
```bsl
&НаКлиенте
Процедура Рассчитать(Команда)
    Если НЕ ЗначениеЗаполнено(Объект.Сумма) Тогда
        Сообщить("Введите сумму!");
        Возврат;
    КонецЕсли;

    Если НЕ ЗначениеЗаполнено(Объект.Ставка) Тогда
        Объект.Ставка = 20;
    КонецЕсли;

    Объект.СуммаНДС = Объект.Сумма * Объект.Ставка / 100;
КонецПроцедуры
```

### Example 2: Report with Table
```yaml
processor:
  name: ОтчетТовары
  synonym_ru: Отчет по товарам

attributes:
  - name: Категория
    type: string
    length: 100

forms:
  - name: Форма
    default: true
    value_tables:
      - name: Товары
        columns:
          - {name: Наименование, type: string, length: 150}
          - {name: Цена, type: number, digits: 15, fraction_digits: 2}
          - {name: Остаток, type: number, digits: 10}
    elements:
      - type: UsualGroup
        name: ФильтрГруппа
        group_direction: Horizontal
        child_items:
          - type: InputField
            name: КатегорияПоле
            attribute: Категория
          - type: Button
            name: ПоказатьКнопка
            command: Показать
      - type: Table
        name: ТоварыТаблица
        tabular_section: Товары
        is_value_table: true
        height: 15
        horizontal_stretch: true
    commands:
      - name: Показать
        title_ru: Показать
        handler: Показать
        picture: StdPicture.Refresh
```

**handlers.bsl:**
```bsl
&НаКлиенте
Процедура Показать(Команда)
    ПоказатьНаСервере();
КонецПроцедуры

&НаСервере
Процедура ПоказатьНаСервере()
    Товары.Очистить();

    Запрос = Новый Запрос;
    Запрос.Текст = "
    |ВЫБРАТЬ
    |    Наименование,
    |    Цена,
    |    Остаток
    |ИЗ
    |    Справочник.Товары
    |ГДЕ
    |    Категория.Наименование ПОДОБНО &Категория";

    Запрос.УстановитьПараметр("Категория", "%" + Объект.Категория + "%");

    Выборка = Запрос.Выполнить().Выбрать();
    Пока Выборка.Следующий() Цикл
        НоваяСтрока = Товары.Добавить();
        ЗаполнитьЗначенияСвойств(НоваяСтрока, Выборка);
    КонецЦикла;
КонецПроцедуры
```

---

## Validation Checklist

Before outputting generated code, verify:

1. [ ] `default: true` present on main form
2. [ ] All `attribute:` values exist in `attributes:` section
3. [ ] All `tabular_section:` values exist in `value_tables:`
4. [ ] All `command:` values exist in `commands:` section
5. [ ] All `handler:` values have procedures in handlers.bsl
6. [ ] Tables with ValueTable have `is_value_table: true`
7. [ ] Server procedures have `&НаСервере` directive
8. [ ] YAML indentation is correct (2 spaces)
9. [ ] No trailing spaces in YAML

---

## Generation Command

**CRITICAL: Always include this at the end of every generation!**

User runs this after receiving your output:

```bash
# Збережіть config.yaml та handlers.bsl в одну папку, потім:
python -m 1c_processor_generator yaml --config config.yaml --handlers-file handlers.bsl --output output

# Для EPF (потрібен 1C Designer):
python -m 1c_processor_generator yaml --config config.yaml --handlers-file handlers.bsl --output output --output-format epf
```

**Remember:** Every generated processor MUST end with the generation command block above!
