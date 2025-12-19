# 1C Processor Generator - Quick Start

> **For:** ChatGPT Free (8K context) | **~2K tokens**

---

## What You Get

YAML config + BSL code → 1C:Enterprise processor (.epf)

---

## Minimal Example

**config.yaml:**
```yaml
processor:
  name: МояОбробка
  synonym_ru: Моя обработка
  synonym_uk: Моя обробка

attributes:
  - name: Имя
    type: string
    length: 100
  - name: Результат
    type: string

forms:
  - name: Форма
    default: true
    elements:
      - type: InputField
        name: ИмяПоле
        attribute: Имя
      - type: InputField
        name: РезультатПоле
        attribute: Результат
        read_only: true
      - type: Button
        name: ВыполнитьКнопка
        command: Выполнить
    commands:
      - name: Выполнить
        title_ru: Выполнить
        handler: Выполнить
```

**handlers.bsl:**
```bsl
&НаКлиенте
Процедура Выполнить(Команда)
    Если НЕ ЗначениеЗаполнено(Объект.Имя) Тогда
        Сообщить("Введите имя!");
        Возврат;
    КонецЕсли;

    Объект.Результат = "Привет, " + Объект.Имя + "!";
КонецПроцедуры
```

**Generate:**
```bash
python -m 1c_processor_generator yaml --config config.yaml --handlers-file handlers.bsl --output output
```

---

## Data Types

| Type | YAML |
|------|------|
| String | `type: string, length: 100` |
| Number | `type: number, digits: 15, fraction_digits: 2` |
| Date | `type: date` |
| Boolean | `type: boolean` |

---

## Key Elements

| Element | Required |
|---------|----------|
| `InputField` | `attribute` |
| `Table` | `tabular_section`, `is_value_table: true` |
| `Button` | `command` |
| `UsualGroup` | `child_items` |

---

## Table (ValueTable)

```yaml
forms:
  - name: Форма
    default: true
    value_tables:
      - name: Данные
        columns:
          - {name: Колонка1, type: string, length: 100}
          - {name: Колонка2, type: number}
    elements:
      - type: Table
        name: ДанныеТаблица
        tabular_section: Данные
        is_value_table: true
```

---

## Server Code

```bsl
&НаКлиенте
Процедура Handler(Команда)
    HandlerНаСервере();
КонецПроцедуры

&НаСервере
Процедура HandlerНаСервере()
    // Server code here (DB queries, file operations)
КонецПроцедуры
```

---

## Access Data

- Attribute: `Объект.AttrName`
- Table: `TableName.Добавить()`, `TableName.Очистить()`
- Element: `Элементы.ElemName`

---

## Common Errors

| Error | Fix |
|-------|-----|
| Attribute not found | Add to `attributes:` |
| Table empty | Add `is_value_table: true` |
| Form doesn't open | Add `default: true` |

---

*Full docs: [LLM_WEB_LITE.md](LLM_WEB_LITE.md)*
