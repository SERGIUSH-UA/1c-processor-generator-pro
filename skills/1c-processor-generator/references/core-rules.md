# Core Rules - Critical Validation Rules for 1C Processor Generation

Extracted from LLM_CORE.md. These rules prevent compilation errors.

---

## Rule 1: Russian Cyrillic ONLY in Identifiers

**Forbidden Unicode characters in names:**
- Ukrainian `i` (U+0456) - use Russian `и` (U+0438)
- Ukrainian `yi` (U+0457) - no direct equivalent
- Ukrainian `ye` (U+0454) - use Russian `е` (U+0435)
- Ukrainian `g` (U+0491) - use Russian `г` (U+0433)
- Also uppercase variants: `I Yi Ye G`

**1C identifier regex:** `^[а-яА-ЯёЁa-zA-Z_][а-яА-ЯёЁa-zA-Z0-9_]*$`

**Allowed in identifiers:** `а-я А-Я ё Ё a-z A-Z 0-9 _`

**Ukrainian IS allowed in:** synonyms, titles, tooltips, messages, BSL string literals.

**Real-world fix examples:**

| Ukrainian (ERROR) | Russian (FIXED) | Letter changed |
|-------------------|-----------------|----------------|
| ПрофесійнаФорма | ПрофессиональнаяФорма | і->и |
| НазваКомпанії | НазваниеКомпании | і->и |
| ОписДіяльності | ОписаниеДеятельности | і->и |
| Підтверджено | Подтверждено | і->о |
| Результати | Результаты | і->ы |
| Операція | Операция | і->и |

**Detection strategy:** When user request contains Ukrainian words, scan for і/ї/є/ґ in generated identifiers. Translate identifier to Russian, preserve Ukrainian in synonym_uk.

---

## Rule 2: BSL Reserved Keywords

**NEVER use these as handler names, attribute names, or command names:**

### Control Flow
```
Если, Тогда, ИначеЕсли, Иначе, КонецЕсли
Для, По, Пока, Цикл, КонецЦикла, Каждого, Из
Попытка, Исключение, ВызватьИсключение, КонецПопытки
Прервать, Продолжить, Возврат
```

### Declarations
```
Процедура, КонецПроцедуры, Функция, КонецФункции
Перем, Знач, Экспорт, Импорт, Новый
```

### Operators & Literals
```
И, Или, Не, Истина, Ложь, Неопределено, NULL
```

### Built-in Functions (commonly confused)
```
Выполнить, Найти
```

### English Equivalents (also reserved)
```
If, Then, ElsIf, Else, EndIf, For, To, While, Do, EndDo,
Each, In, Try, Except, Raise, EndTry, Break, Continue, Return,
Procedure, EndProcedure, Function, EndFunction, Var, Val,
Export, Import, New, And, Or, Not, True, False, Undefined, NULL,
Execute, Find
```

**Fix pattern:** Add context noun to make unique identifier:

| Reserved | Fixed |
|----------|-------|
| Выполнить | ВыполнитьОбработку |
| Экспорт | ЭкспортироватьДанные |
| Импорт | ИмпортироватьФайл |
| Возврат | ВернутьРезультат |
| Найти | НайтиЗаписи |

---

## Rule 3: Valid StdPicture Names

Only use names from the valid list (130+ names). Common valid names:

**Actions:** ExecuteTask, SaveFile, OpenFile, Refresh, Delete, Change, Write, Print, Copy, Paste, Cut
**UI:** CreateListItem, InputFieldClear, Check, CheckAll, UncheckAll
**Reports:** GenerateReport, ReportSettings
**Navigation:** GoToNext, GoToPrevious, MoveUp, MoveDown
**Status:** Information, Warning, Error, Question, Stop

**Common mistakes:**
- `Save` -> `SaveFile`
- `CheckMark` -> `Check`
- `Run` -> `ExecuteTask`
- `New` -> `CreateListItem`

**When unsure:** Omit picture (it's optional) rather than guessing.

Full validated list: `valid-pictures.md`

---

## Rule 4: forms: Section Placement

When using `forms:` array, ALL of these MUST be INSIDE the form definition:
- `value_tables` - temporary tables
- `form_attributes` - form-level attributes
- `dynamic_lists` - live DB queries
- `commands` - action commands
- `events` - form events

Root-level definitions are SILENTLY IGNORED when `forms:` section exists.

```yaml
# WRONG - root level (ignored!)
value_tables:
  - name: Results
    columns: [...]

forms:
  - name: Форма
    default: true
    # Results table not found here!

# CORRECT - inside form
forms:
  - name: Форма
    default: true
    value_tables:
      - name: Results
        columns: [...]
```

---

## Rule 5: Type Placement

| Type | Section | Access in BSL |
|------|---------|---------------|
| string, number, boolean, date | `attributes:` | `Объект.Name` |
| CatalogRef.*, DocumentRef.* | `attributes:` | `Объект.Name` |
| spreadsheet_document | `form_attributes:` (MUST) | `Name` (no Объект.) |
| binary_data | `form_attributes:` (MUST) | `Name` (no Объект.) |
| string (for HTML) | `form_attributes:` | `Name` (no Объект.) |

Wrong section -> "Attribute not found" runtime error.

---

## Hallucination Prevention

### DO NOT hallucinate:
1. **BSL functions** - Only use real 1C platform functions. Common real ones: `Сообщить()`, `ЗначениеЗаполнено()`, `ТекущаяДата()`, `Формат()`, `ТипЗнч()`, `Тип()`, `ОписаниеОшибки()`.
2. **Random numbers** - `СлучайноеЧисло()` does NOT exist. Use `Новый ГенераторСлучайныхЧисел()`.
3. **StdPicture names** - Only use validated names from the list.
4. **YAML properties** - Only use properties documented in the API reference.
5. **Event signatures** - Use exact signatures. Wrong parameters cause silent failures.

### Event Signatures (exact):
```
OnOpen: ПриОткрытии(Отказ)
OnCreateAtServer: ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
OnClose: ПриЗакрытии(ЗавершениеРаботы)
OnChange: ПриИзменении(Элемент)
OnActivateRow: ПриАктивизацииСтроки(Элемент)
Selection: Выбор(Элемент, ВыбраннаяСтрока, Поле, СтандартнаяОбработка)
StartChoice: НачалоВыбора(Элемент, ДанныеВыбора, СтандартнаяОбработка)
Command handler: ИмяКоманды(Команда)
```

---

## Quick Validation Checklist (Run Before Generation)

1. **Cyrillic** (30s) - Scan all `name:` fields for Ukrainian letters
2. **Reserved keywords** (15s) - Check handler names against keyword list
3. **Types** (10s) - spreadsheet_document/binary_data in form_attributes only
4. **File naming** (5s) - Handler names in BSL match YAML exactly
5. **forms: placement** (10s) - value_tables, commands, events INSIDE form
6. **StdPicture** (5s) - Verify picture names or omit if unsure
7. **is_value_table** (5s) - ValueTable tables have `is_value_table: true`
8. **default: true** (2s) - One form has `default: true`
