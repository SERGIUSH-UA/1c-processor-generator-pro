# Patcher Guide for GPT

Цей документ описує як використовувати `patchSessionCode` action для часткових змін YAML та BSL.

## Коли використовувати Patch API

**Використовуй patchSessionCode замість submitSessionCode коли:**
- Потрібно додати одну подію/команду без перезапису всього коду
- Треба виправити конкретний рядок (наприклад, параметр таймера)
- Додати нову процедуру до існуючого коду
- Видалити/замінити існуючу процедуру

**Переваги:**
- Менше токенів в запиті
- Менший ризик втратити існуючий код
- Точкові зміни без повної заміни

## YAML Patches (JSON Patch style)

Використовує JSON Pointer paths (RFC 6901) для навігації по YAML структурі.

### Операції

| op | Опис | Коли використовувати |
|----|------|---------------------|
| `add` | Додати секцію/елемент | Нова подія, команда, елемент |
| `replace` | Замінити значення | Змінити тип, параметр |
| `remove` | Видалити секцію | Видалити елемент, подію |
| `merge` | Злити з існуючим об'єктом | Додати поля до events |

### Path Syntax (JSON Pointer)

```
/forms/0              - перша форма (індекс 0)
/forms/0/events       - секція events першої форми
/forms/0/commands/-   - додати в КІНЕЦЬ масиву commands
/forms/0/commands/1   - друга команда (індекс 1)
/forms/0/form_attributes/0/type - тип першого form_attribute
/processor/name       - ім'я процесора
```

### Приклади YAML Patches

#### Додати команду з shortcut

```json
{
  "yaml_patches": [
    {
      "op": "add",
      "path": "/forms/0/commands/-",
      "value": {
        "name": "MoveUp",
        "handler": "ВгоруНатиснуто",
        "shortcut": "F5"
      }
    }
  ]
}
```

#### Додати подію до існуючої секції events

```json
{
  "yaml_patches": [
    {
      "op": "merge",
      "path": "/forms/0/events",
      "value": {
        "OnActivateRow": "ПриАктивизацииСтроки"
      }
    }
  ]
}
```

#### Додати команду в кінець масиву

```json
{
  "yaml_patches": [
    {
      "op": "add",
      "path": "/forms/0/commands/-",
      "value": {
        "name": "Pause",
        "title_ru": "Пауза",
        "title_uk": "Пауза",
        "handler": "ПаузаИгры"
      }
    }
  ]
}
```

#### Замінити тип атрибута

```json
{
  "yaml_patches": [
    {
      "op": "replace",
      "path": "/forms/0/form_attributes/0/type",
      "value": "string"
    }
  ]
}
```

#### Видалити елемент

```json
{
  "yaml_patches": [
    {
      "op": "remove",
      "path": "/forms/0/elements/2"
    }
  ]
}
```

---

## BSL Patches (Procedure-level)

Операції на рівні процедур та рядків BSL коду.

### Операції

| op | Опис | Обов'язкові поля |
|----|------|------------------|
| `add_procedure` | Додати нову процедуру/функцію | name, body |
| `replace_procedure` | Замінити тіло процедури | name, body |
| `remove_procedure` | Видалити процедуру | name |
| `replace_line` | Замінити рядок за патерном | line_pattern, new_line |
| `add_variable` | Додати змінну (Перем) | declaration |
| `add_code_block` | Додати код в кінець | code |

### add_procedure

Додає нову процедуру в кінець модуля.

```json
{
  "bsl_patches": [
    {
      "op": "add_procedure",
      "name": "ПриНажатииКлавиши",
      "directive": "&НаКлиенте",
      "params": "Клавиша, СтандартнаяОбработка",
      "body": "    СтандартнаяОбработка = Ложь;\n    \n    Если Клавиша = Клавиша.Вверх Тогда\n        Направление = \"Вверх\";\n    ИначеЕсли Клавиша = Клавиша.Вниз Тогда\n        Направление = \"Вниз\";\n    КонецЕсли;"
    }
  ]
}
```

**Параметри:**
- `name` (обов'язковий) - ім'я процедури
- `directive` (опціонально, default: `&НаКлиенте`) - директива
- `params` (опціонально) - параметри через кому
- `body` (обов'язковий) - тіло процедури (без Процедура/КонецПроцедуры)
- `is_function` (опціонально) - якщо true, створює Функція замість Процедура
- `export` (опціонально) - якщо true, додає Экспорт

### replace_procedure

Замінює тіло існуючої процедури.

```json
{
  "bsl_patches": [
    {
      "op": "replace_procedure",
      "name": "ВыполнитьШаг",
      "body": "    // Новий код\n    ПереместитьЗмейку();\n    ПроверитьСтолкновение();"
    }
  ]
}
```

### remove_procedure

Видаляє процедуру повністю (з директивою).

```json
{
  "bsl_patches": [
    {
      "op": "remove_procedure",
      "name": "СтараяПроцедура"
    }
  ]
}
```

### replace_line

**ВАЖЛИВО:** Патерн знаходить рядок, потім ВЕСЬ РЯДОК замінюється на new_line.

```json
{
  "bsl_patches": [
    {
      "op": "replace_line",
      "line_pattern": "ПодключитьОбработчикОжидания.*0[.]3",
      "new_line": "    ПодключитьОбработчикОжидания(\"ВыполнитьШаг\", 1);"
    }
  ]
}
```

**Параметри:**
- `line_pattern` (обов'язковий) - regex патерн для пошуку рядка
- `new_line` (обов'язковий) - повний новий рядок (включаючи відступи!)
- `procedure` (опціонально) - обмежити заміну конкретною процедурою

**Regex tips:**
- Використовуй `[.]` замість `\.` для точки (уникнення escape проблем)
- Використовуй `.*` для будь-яких символів
- `\d+` для чисел

### add_variable

Додає змінну на початок модуля.

```json
{
  "bsl_patches": [
    {
      "op": "add_variable",
      "directive": "&НаКлиенте",
      "declaration": "Перем НоваяПеременная, ЕщеОдна;"
    }
  ]
}
```

### add_code_block

Додає код в кінець модуля.

```json
{
  "bsl_patches": [
    {
      "op": "add_code_block",
      "code": "// Ініціалізація\nИнициализация();"
    }
  ]
}
```

---

## Комбіновані Patches

Можна застосовувати YAML і BSL патчі в одному запиті:

```json
{
  "yaml_patches": [
    {
      "op": "add",
      "path": "/forms/0/commands/-",
      "value": {"name": "MoveUp", "handler": "ВгоруНатиснуто", "shortcut": "F5"}
    }
  ],
  "bsl_patches": [
    {
      "op": "add_procedure",
      "name": "ВгоруНатиснуто",
      "directive": "&НаКлиенте",
      "body": "Направление = \"Вверх\";"
    }
  ]
}
```

---

## Response Format

```json
{
  "success": true,
  "message": "Applied 2 patches successfully",
  "version": 3,
  "changes": {
    "yaml_applied": 1,
    "bsl_applied": 1,
    "yaml_failed": [],
    "bsl_failed": []
  },
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": []
  },
  "result_preview": {
    "yaml_config": "processor:\n  name: ...",
    "handlers_content": "&НаКлиенте\n..."
  }
}
```

**Поля:**
- `success` - true якщо хоча б один патч застосовано
- `changes.yaml_applied` / `bsl_applied` - кількість успішних патчів
- `changes.yaml_failed` / `bsl_failed` - помилки патчів
- `validation` - результат валідації (якщо validate=true)
- `result_preview` - preview зміненого коду (truncated до 2000 chars)

---

## Типові сценарії

### Виправити інтервал таймера (тонкий клієнт: мінімум 1 секунда)

```json
{
  "bsl_patches": [
    {
      "op": "replace_line",
      "line_pattern": "ПодключитьОбработчикОжидания.*0[.]\\d+",
      "new_line": "    ПодключитьОбработчикОжидания(\"ВыполнитьШаг\", 1);"
    }
  ]
}
```

### Додати клавіатурні скорочення

```json
{
  "yaml_patches": [
    {"op": "add", "path": "/forms/0/commands/-", "value": {"name": "MoveUp", "handler": "ВгоруНатиснуто", "shortcut": "F5"}},
    {"op": "add", "path": "/forms/0/commands/-", "value": {"name": "MoveDown", "handler": "ВнизНатиснуто", "shortcut": "F6"}}
  ],
  "bsl_patches": [
    {
      "op": "add_procedure",
      "name": "ВгоруНатиснуто",
      "directive": "&НаКлиенте",
      "body": "Направление = \"Вверх\";"
    },
    {
      "op": "add_procedure",
      "name": "ВнизНатиснуто",
      "directive": "&НаКлиенте",
      "body": "Направление = \"Вниз\";"
    }
  ]
}
```

### Додати нову команду з обробником

```json
{
  "yaml_patches": [
    {
      "op": "add",
      "path": "/forms/0/commands/-",
      "value": {
        "name": "NewCommand",
        "title_ru": "Нова команда",
        "handler": "НоваКомандаОбработка"
      }
    }
  ],
  "bsl_patches": [
    {
      "op": "add_procedure",
      "name": "НоваКомандаОбработка",
      "params": "Команда",
      "body": "    // Логіка команди"
    }
  ]
}
```

### Замінити забороненого методу на тонкому клієнті

Наприклад, `ТабличныйДокумент.Очистить()` заборонений:

```json
{
  "bsl_patches": [
    {
      "op": "replace_line",
      "procedure": "ОбновитьПоле",
      "line_pattern": "ТабДок[.]Очистить",
      "new_line": "    ТабДок = Новый ТабличныйДокумент;"
    }
  ]
}
```

---

## Помилки та їх вирішення

| Помилка | Причина | Рішення |
|---------|---------|---------|
| `Session has no data` | Сесія порожня | Спочатку відправ код через submitSessionCode |
| `Procedure 'X' not found` | Процедура не існує | Перевір ім'я або використай add_procedure |
| `Procedure 'X' already exists` | Дублікат | Використай replace_procedure замість add |
| `Pattern not found` | Патерн не знайдено | Перевір regex патерн |
| `Invalid path` | Неправильний JSON Pointer | Перевір структуру YAML |

---

## Обмеження

- Патчі застосовуються послідовно
- Якщо патч провалився, наступні все одно виконуються
- `result_preview` обрізається до 2000 символів
- validate=true за замовчуванням
