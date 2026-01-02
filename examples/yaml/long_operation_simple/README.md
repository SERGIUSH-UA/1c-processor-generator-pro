# Simple Long Operation Example

**Версія:** v3.0.0+
**Призначення:** Демонстрація базового використання background jobs (довгих операцій)

## Що демонструє цей приклад

✅ Мінімальна конфігурація long operation
✅ Автоматична генерація 4 handlers (Кнопка, ВФоне, Завершение, НаСервере)
✅ Progress reporting через ДлительныеОперации.СообщитьПрогресс()
✅ Повернення результату через temporary storage

## Структура

```
long_operation_simple/
├── config.yaml         # YAML конфігурація
├── handlers.bsl        # ImportНаСервере - єдиний handler який пише user
└── README.md           # Цей файл
```

## Як працює

### 1. LLM пише тільки 1 handler (business logic):

**handlers.bsl:**
```bsl
&НаСервере
Процедура ImportНаСервере(Параметры, АдресРезультата) Экспорт
    // Your business logic here
    Результат = ...;
    ПоместитьВоВременноеХранилище(Результат, АдресРезультата);
КонецПроцедуры
```

### 2. Generator створює 3 wrapper handlers автоматично:

- **ImportКнопка()** - client entry point (validation)
- **ImportВФоне()** - server starter (calls ДлительныеОперации.ВыполнитьВФоне)
- **ImportЗавершение()** - client completion (processes result)

### 3. Результат: 4 handlers в Module.bsl

```bsl
#Область ОбработчикиКомандФормы
&НаКлиенте
Процедура ImportКнопка(Команда)
    ImportВФоне();
КонецПроцедуры
#КонецОбласти

#Область ДлительныеОперации
&НаСервере
Процедура ImportВФоне()
    // ... wrapper code ...
    Результат = ДлительныеОперации.ВыполнитьВФоне(...);
    ДлительныеОперацииКлиент.ОжидатьЗавершение(Результат, ...);
КонецПроцедуры

&НаКлиенте
Процедура ImportЗавершение(Результат, ДополнительныеПараметры) Экспорт
    // ... wrapper code ...
    РезультатОперации = ПолучитьИзВременногоХранилища(...);
КонецПроцедуры

&НаСервере
Процедура ImportНаСервере(Параметры, АдресРезультата) Экспорт
    // User's business logic (from handlers.bsl)
КонецПроцедуры
#КонецОбласти
```

## Генерація

```bash
# Single file approach (recommended)
python -m 1c_processor_generator yaml \
  --config examples/yaml/long_operation_simple/config.yaml \
  --handlers-file examples/yaml/long_operation_simple/handlers.bsl \
  --output tmp/long_operation_simple
```

## YAML Конфігурація

### Мінімальна (defaults):
```yaml
commands:
  - name: Import
    long_operation: true  # Все решта - defaults
```

### Повна (custom settings):
```yaml
commands:
  - name: Import
    long_operation: true
    long_operation_settings:
      show_progress: true              # Показувати вікно прогресу
      allow_cancel: true               # Дозволити скасування
      timeout_seconds: 300             # Таймаут (5 хвилин)
      progress_message: "Importing..." # Текст повідомлення
      use_additional_parameters: false # Не передавати всі атрибути
      output_messages: true
      output_progress: false
```

## Key Features (v3.0.0)

| Feature | Description |
|---------|-------------|
| **1 file approach** | User writes ONLY ImportНаСервере.bsl |
| **3 auto-generated wrappers** | Кнопка, ВФоне, Завершение |
| **Progress reporting** | ДлительныеОперации.СообщитьПрогресс() |
| **Cancellation** | User can cancel operation |
| **Result handling** | Temporary storage → completion handler |
| **Error handling** | Automatic error display |

## Best Practices

✅ **DO:**
- Use for operations >3-5 seconds
- Report progress every 50-100 items
- Return structured result (Структура)
- Handle errors gracefully

❌ **DON'T:**
- Use for quick operations (<1 second)
- Forget to call ПоместитьВоВременноеХранилище
- Block UI in НаСервере handler
- Use for simple calculations

## Real-world Use Cases

- **Data Import:** CSV, Excel, JSON (1000+ rows)
- **Report Generation:** Complex calculations (5000+ rows)
- **Batch Processing:** Document posting (100+ documents)
- **File Processing:** Image conversion, PDF generation
- **API Calls:** External service integration (slow network)

## Technical Details

**LLM Responsibility:**
- Write business logic in `ImportНаСервере(Параметры, АдресРезультата)`
- Call `ДлительныеОперации.СообщитьПрогресс()` for progress
- Store result to `АдресРезультата` temporary storage

**Generator Responsibility:**
- Generate client button handler (validation placeholder)
- Generate server starter (ДлительныеОперации.ВыполнитьВФoне setup)
- Generate completion handler (result extraction + UI update placeholder)
- Load user's НаСервере handler

**Platform Responsibility (1C):**
- Background job execution
- Progress window display
- Cancellation handling
- Temporary storage lifecycle
