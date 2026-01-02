# Калькулятор з автоматичними тестами (v2.16.0+)

Приклад обробки з повною підтримкою автоматичного тестування через COM.

## Структура

```
calculator_with_tests/
├── config.yaml                    # Конфігурація обробки
├── handlers.bsl                   # BSL код (single file approach)
├── tests/
│   ├── calculator_tests.yaml      # Конфігурація тестів
│   └── custom_tests.bsl           # Процедурні тести (складні сценарії)
└── README.md                      # Ця інструкція
```

## Особливості

✅ **Декларативні тести** - прості сценарії описані в YAML
✅ **Процедурні тести** - складна логіка в BSL файлі
✅ **External Connection** - швидке тестування без UI
✅ **Wrapper для повідомлень** - автоматичне перехоплення `Сообщить()`

## Генерація

```bash
# Генерація XML + EPF + pytest тести
python -m 1c_processor_generator yaml \
  --config examples/yaml/calculator_with_tests/config.yaml \
  --handlers-file examples/yaml/calculator_with_tests/handlers.bsl \
  --output-format epf
```

## Що відбувається

1. **Генерує XML структуру** обробки
2. **Компілює в EPF** через Designer
3. **Автоматично генерує pytest тести** в `tmp/Калькулятор/tests/`:
   - `test_Калькулятор.py` - згенеровані pytest тести
   - `conftest.py` - fixtures для COM підключення
   - `custom_tests.bsl` - скопійовані процедурні тести

4. **Додає BSL wrapper** для тестування:
   - `НачатьЗаписьСообщений()` - увімкнути запис
   - `ПолучитьТестовыеСообщения()` - отримати повідомлення
   - `ОтправитьСообщение()` - wrapper для `Сообщить()`

## Запуск тестів

### Попередні вимоги

```bash
# Встановити pywin32 (Windows only)
pip install pywin32>=305
```

### Виконання

```bash
# Запустити всі тести
pytest tmp/Калькулятор/tests/

# Детальний вивід
pytest tmp/Калькулятор/tests/ -v

# З покриттям
pytest tmp/Калькулятор/tests/ --cov
```

## Структура тестів

### Декларативні (YAML)

```yaml
- name: test_addition
  setup:
    attributes: {Число1: 10, Число2: 20}
  execute_command: Додати
  assert:
    attributes: {Результат: 30}
    messages: [{contains: "Додавання виконано"}]
```

Генерується в pytest:
```python
def test_addition(self, processor):
    # setup
    processor.set_attribute("Число1", 10)
    processor.set_attribute("Число2", 20)

    # execute
    processor.execute_command("Додати")

    # assert
    assert processor.get_attribute("Результат") == 30
```

### Процедурні (BSL)

```bsl
Процедура Тест_ПослідовніОперації() Экспорт
    // Складна логіка з кількома операціями
    Объект.Число1 = 10;
    Объект.Число2 = 5;
    ДодатиНаСервере();

    Если Объект.Результат <> 15 Тогда
        ВызватьИсключение "Помилка!";
    КонецЕсли;
КонецПроцедуры
```

Генерується wrapper:
```python
def test_послідовні_операції(self, processor):
    result = processor.run_procedural_test("Тест_ПослідовніОперації")
    assert result.passed
```

## Що тестується

✅ **Команди** - виконання через COM
✅ **Атрибути** - читання/запис значень
✅ **Повідомлення** - перехоплення через wrapper
✅ **Виключення** - перевірка помилок валідації

## Архітектура тестування

```
pytest tests/
    ↓
conftest.py (fixtures)
    ↓
EPFTester (COM connection)
    ↓ External Connection
1C persistent_ib
    ↓ Завантажує
Calculator.epf
    ↓ Викликає
BSL процедури + wrapper
```

## Переваги

- **Швидко**: External Connection ~10x швидше Automation Server
- **Ізольовано**: Кожен тест в окремому контексті
- **Читабельно**: YAML для простих сценаріїв
- **Потужно**: BSL для складної логіки
- **Автоматично**: Генерація pytest з YAML

## Обмеження

⚠️ **Windows only** - pywin32 працює тільки на Windows
⚠️ **Потрібен 1C** - тести виконуються в реальній 1C runtime
⚠️ **Без UI** - External Connection не підтримує форми

## Розширення

### Додати новий декларативний тест

Відредагуйте `tests/calculator_tests.yaml`:

```yaml
declarative_tests:
  - name: test_my_scenario
    description: "Опис тесту"
    setup:
      attributes: {...}
    execute_command: МояКоманда
    assert:
      attributes: {...}
```

### Додати процедурний тест

Додайте в `tests/custom_tests.bsl`:

```bsl
Процедура Тест_МійСкладнийСценарій() Экспорт
    // Складна логіка
КонецПроцедуры
```

Та в `tests/calculator_tests.yaml`:

```yaml
procedural_tests:
  procedures:
    - Тест_МійСкладнийСценарій
```

## Дивіться також

- [TESTING_GUIDE.md](../../../docs/TESTING_GUIDE.md) - Повний гайд по тестуванню
- [LLM_PROMPT.md](../../../docs/LLM_PROMPT.md) - Документація для LLM
