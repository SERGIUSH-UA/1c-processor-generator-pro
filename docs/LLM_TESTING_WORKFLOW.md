# LLM Testing Workflow (v2.23.2)

Complete guide for LLMs on how to test 1C processors automatically with auto-detection architecture.

## Overview

```
User Request → LLM Generates → Compile EPF → Run Tests → Analyze Results → Fix & Repeat
```

## Step-by-Step Workflow

### Step 1: User Request

```
User: "Створи калькулятор, який може додавати, віднімати і множити числа.
       Додай тести для всіх операцій."
```

### Step 2: LLM Generates Files

**config.yaml** (structure):
```yaml
processor:
  name: Калькулятор
  tests_file: tests/calculator_tests.yaml

attributes:
  - name: Число1
    type: number
  - name: Число2
    type: number
  - name: Результат
    type: number

forms:
  - name: Форма
    elements:
      - type: InputField
        name: Число1
      - type: InputField
        name: Число2
      - type: InputField
        name: Результат
    commands:
      - name: Добавить
      - name: Вычесть
      - name: Умножить
```

**handlers.bsl** (business logic):
```bsl
Процедура Добавить() Экспорт
    Результат = Число1 + Число2;
КонецПроцедуры

Процедура Вычесть() Экспорт
    Результат = Число1 - Число2;
КонецПроцедуры

Процедура Умножить() Экспорт
    Результат = Число1 * Число2;
КонецПроцедуры
```

**tests/calculator_tests.yaml** (v2.23.2 structure):
```yaml
# ObjectModule tests (via External Connection - fast, no UI)
objectmodule_tests:
  declarative:
    - name: test_addition
      setup:
        attributes:
          Число1: 10
          Число2: 20
      execute_command: Добавить
      assert:
        attributes:
          Результат: 30

    - name: test_subtraction
      setup:
        attributes:
          Число1: 50
          Число2: 15
      execute_command: Вычесть
      assert:
        attributes:
          Результат: 35

    - name: test_multiplication
      setup:
        attributes:
          Число1: 5
          Число2: 7
      execute_command: Умножить
      assert:
        attributes:
          Результат: 35

  procedural:
    file: custom_tests.bsl
    procedures:
      - Тест_ПоследовательныеОперації

# Налаштування виконання
timeout: 300
```

**tests/custom_tests.bsl** (procedural tests - ObjectModule style):
```bsl
// ВАЖЛИВО: ObjectModule style (no Объект., no &НаСервере)

Процедура Тест_ПоследовательныеОперації() Экспорт
    // Тест: послідовне виконання операцій

    // 10 + 5 = 15
    Число1 = 10;
    Число2 = 5;
    Добавить();

    Если Результат <> 15 Тогда
        ВызватьИсключение "Помилка додавання: очікувалось 15, отримано " + Результат;
    КонецЕсли;

    // 15 - 5 = 10
    Число1 = Результат;
    Число2 = 5;
    Вычесть();

    Если Результат <> 10 Тогда
        ВызватьИсключение "Помилка віднімання: очікувалось 10, отримано " + Результат;
    КонецЕсли;

    // 10 * 3 = 30
    Число1 = Результат;
    Число2 = 3;
    Умножить();

    Если Результат <> 30 Тогда
        ВызватьИсключение "Помилка множення: очікувалось 30, отримано " + Результат;
    КонецЕсли;
КонецПроцедуры
```

### Step 3: LLM Compiles EPF

**Command:**
```bash
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output-format epf
```

**Output:**
```
✅ Обробка 'Калькулятор' успішно згенерована!
🎉 Готово! EPF створено: tmp/Калькулятор.epf (7,575 bytes)

🧪 Генерація автоматичних тестів...
   ✅ Тести згенеровано: tmp/Калькулятор/tests
   Declarative: 3
   Procedural: 1

💉 Інжектування procedural tests в ObjectModule...
   ✅ Procedural tests інжектовано в ObjectModule
   ✅ Test EPF створено: tmp/Калькулятор_Tests.epf (8,053 bytes)
```

**Generated files:**
- `tmp/Калькулятор.epf` - Production EPF (clean, no tests)
- `tmp/Калькулятор_Tests.epf` - Test EPF (with injected procedural tests)
- `tmp/Калькулятор/tests.yaml` - Test configuration for test_runner

### Step 4: LLM Runs Tests

**Command (v2.23.2 - auto-detection, no flags needed!):**
```bash
python -m 1c_processor_generator.test_runner \
  --tests-config tmp/Калькулятор/tests/calculator_tests.yaml \
  --epf-path tmp/Калькулятор.epf \
  --ib-path "C:\Users\...\persistent_ib" \
  --processor-name Калькулятор
```

**Output (first run - all pass):**
```
Loading tests from tmp/Калькулятор/tests/calculator_tests.yaml...
✅ Tests loaded: objectmodule_tests (3 declarative + 1 procedural)

================================================================================
🔧 SETUP: Connecting to 1C...
================================================================================
✅ Successfully connected to 1C

================================================================================
📋 OBJECTMODULE TESTS - External Connection (fast, no UI)
================================================================================

[DECLARATIVE] test_addition
--------------------------------------------------------------------------------
✅ PASSED (0.00s)

[DECLARATIVE] test_subtraction
--------------------------------------------------------------------------------
✅ PASSED (0.00s)

[DECLARATIVE] test_multiplication
--------------------------------------------------------------------------------
✅ PASSED (0.00s)

[PROCEDURAL] Тест_ПоследовательныеОперації
--------------------------------------------------------------------------------
✅ PASSED (0.00s)

================================================================================
📊 SUMMARY
================================================================================

Total tests: 4
✅ Passed: 4
❌ Failed: 0
⏱️  Execution time: 0.02s

================================================================================
🎉 ALL TESTS PASSED!
================================================================================
✅ Disconnected from 1C
```

### Step 5: LLM Analyzes Results

**Scenario A: All tests pass** ✅
```
LLM: "Всі тести пройшли! Процесор готовий.
      Production EPF: tmp/Калькулятор.epf"
```

**Scenario B: Some tests fail** ❌
```
❌ FAILED TESTS:
   - test_addition: Expected 30, got 20
```

**LLM Analysis:**
```
LLM: "Тест test_addition failed - очікувалось 30, отримано 20.
      Проблема: в handlers.bsl процедура Добавить() помилково віднімає.

      FIX:
      - Було: Результат = Число1 - Число2;
      - Має бути: Результат = Число1 + Число2;"
```

### Step 6: LLM Fixes & Repeats

**LLM fixes handlers.bsl:**
```bsl
Процедура Добавить() Экспорт
    Результат = Число1 + Число2;  // ← виправив
КонецПроцедуры
```

**LLM repeats:**
1. Regenerate EPF
2. Run tests again
3. **All tests pass!** ✅

---

## Three Types of Tests (v2.23.2)

### 1. ObjectModule Declarative Tests - Fast, No UI

**Location:** `objectmodule_tests.declarative`

**Use when:**
- Simple business logic scenarios
- Single command execution
- Attribute and message verification

**Example:**
```yaml
objectmodule_tests:
  declarative:
    - name: test_addition
      description: "Test addition of two numbers"
      setup:
        attributes:
          Число1: 10
          Число2: 20
      execute_command: Добавить
      assert:
        attributes:
          Результат: 30
        messages:
          - contains: "Додавання виконано"
```

**Connection:** External Connection (fast, no UI)

### 2. ObjectModule Procedural Tests - Complex Logic, No UI

**Location:** `objectmodule_tests.procedural`

**Use when:**
- Complex scenarios (sequential operations)
- Conditional logic, loops
- Tabular section manipulation
- Custom validation logic

**Example:**
```bsl
// ObjectModule style (no Объект., no &НаСервере)
Процедура Тест_ПоследовательныеОперації() Экспорт
    // Sequential operations: 10 + 5 = 15, 15 - 5 = 10, 10 * 3 = 30
    Число1 = 10;
    Число2 = 5;
    Добавить();

    Если Результат <> 15 Тогда
        ВызватьИсключение "Помилка додавання";
    КонецЕсли;

    // Use previous result as input
    Число1 = Результат;
    Число2 = 5;
    Вычесть();

    // ... more operations
КонецПроцедуры
```

**Connection:** External Connection (fast, no UI)
**Style:** ObjectModule (direct access, no Объект., no &НаСервере)

### ❌ Form Tests - NOT AVAILABLE

**⚠️ CRITICAL: Form testing is NOT POSSIBLE (v2.23.2+)**

After extensive COM investigation (2025-11-18), form testing via Automation Server cannot be implemented due to fundamental COM limitations.

**Why it doesn't work:**
- ❌ V83.Application inaccessible from Python (RPC_E_DISCONNECTED)
- ❌ V83.COMConnector.ПолучитьФорму() fails ("Интерактивные операции недоступны")
- ❌ External Connection is headless by design

**What this means:**
- ❌ `forms[]` section will NOT execute
- ❌ UI interaction testing not possible
- ❌ Form events testing not possible
- ✅ Use ObjectModule tests instead (Types #1 and #2 above)

**Alternatives:**
- ✅ ObjectModule procedural tests (complex logic, full access)
- Manual form testing through 1C Configurator
- Future: Web client + Selenium

**Technical details:** `docs/research/V83_INVESTIGATION_REPORT.md`

---

## Extended Assertions (v2.20.0+)

### Numeric Assertions
```yaml
assert:
  attributes:
    Результат:
      gt: 10         # greater than
      lt: 100        # less than
      gte: 30        # greater than or equal
      lte: 30        # less than or equal
      between: [20, 40]
      ne: 0          # not equal
```

### String Assertions
```yaml
assert:
  attributes:
    Коментар:
      matches: "^Результат: \\d+$"  # regex match
      starts_with: "Результат:"
      ends_with: "виконано"
      length: 20
```

### Type Assertions
```yaml
assert:
  attributes:
    Значення:
      type: "Number"
      is_null: false
      not_null: true
```

### Collection Assertions
```yaml
assert:
  attributes:
    Статус:
      in: ["Новий", "В роботі", "Завершено"]
      not_in: ["Видалено", "Архів"]
```

---

## Fixtures Support (v2.21.0+)

**Use when:** Need reusable test data across multiple tests

**fixtures.yaml:**
```yaml
fixtures:
  default_numbers:
    Число1: 100
    Число2: 50

  large_numbers:
    Число1: 999999999
    Число2: 1
```

**tests.yaml:**
```yaml
declarative_tests:
  - name: test_with_fixture
    fixture: default_numbers  # Loads Число1=100, Число2=50
    execute_command: Добавить
    assert:
      attributes:
        Результат: 150
```

---

## Timeout Support (v2.21.0+)

**For long-running tests:**
```yaml
settings:
  timeout: 600  # 10 minutes (default: 300)

declarative_tests:
  - name: test_long_operation
    timeout: 120  # Override for specific test
    setup:
      # ...
```

---

## Best Practices for LLMs

### 1. Start with Declarative Tests
```
✅ DO: Write simple scenarios in YAML first
❌ DON'T: Jump to procedural tests for simple cases
```

### 2. Use Procedural Tests for Complex Logic
```
✅ DO: Use BSL when you need loops, conditions, sequential operations
❌ DON'T: Use BSL for simple attribute checks
```

### 3. Test Edge Cases
```yaml
# Test zero values
- name: test_zero
  setup: {Число1: 0, Число2: 0}
  assert: {Результат: 0}

# Test negative numbers
- name: test_negative
  setup: {Число1: -10, Число2: 5}
  assert: {Результат: -5}

# Test large numbers (procedural)
Процедура Тест_БольшиеЧисла() Экспорт
    Число1 = 999999999;
    Число2 = 1;
    Добавить();

    Если Результат <> 1000000000 Тогда
        ВызватьИсключение "Помилка";
    КонецЕсли;
КонецПроцедуры
```

### 4. Write Clear Error Messages
```bsl
✅ GOOD:
Если Результат <> 15 Тогда
    ВызватьИсключение "Помилка додавання: очікувалось 15, отримано " + Результат;
КонецЕсли;

❌ BAD:
Если Результат <> 15 Тогда
    ВызватьИсключение "Помилка";  // Not clear what failed
КонецЕсли;
```

### 5. Iterate Based on Test Results
```
1. Generate processor + tests
2. Compile EPF
3. Run tests
4. IF tests fail:
   - Analyze error messages
   - Fix handlers.bsl
   - GOTO step 2
5. IF all tests pass:
   - Processor ready!
```

---

## Common Patterns

### Pattern 1: Sequential Operations Test
```bsl
Процедура Тест_Послідовність() Экспорт
    // Test that result of one operation can be used as input for next
    Число1 = 10;
    Число2 = 5;
    Добавить();  // 10 + 5 = 15

    Число1 = Результат;  // Use 15
    Число2 = 3;
    Умножить();  // 15 * 3 = 45

    Если Результат <> 45 Тогда
        ВызватьИсключение "Очікувалось 45, отримано " + Результат;
    КонецЕсли;
КонецПроцедуры
```

### Pattern 2: Tabular Section Test
```bsl
Процедура Тест_ТабличнаЧастина() Экспорт
    // Add multiple rows and calculate sum
    НоваСтрока = Lines.Add();
    НоваСтрока.Quantity = 10;
    НоваСтрока.Price = 100;

    НоваСтрока = Lines.Add();
    НоваСтрока.Quantity = 5;
    НоваСтрока.Price = 200;

    CalculateTotal();  // Should calculate: 10*100 + 5*200 = 2000

    Если Total <> 2000 Тогда
        ВызватьИсключение "Очікувалось 2000, отримано " + Total;
    КонецЕсли;
КонецПроцедуры
```

### Pattern 3: Error Handling Test
```bsl
Процедура Тест_ДіленняНаНуль() Экспорт
    Число1 = 10;
    Число2 = 0;

    Попытка
        Divide();  // Should throw error
        ВызватьИсключение "Очікувалась помилка ділення на нуль";
    Исключение
        // Expected error - test passes
    КонецПопытки;
КонецПроцедуры
```

---

## Architecture: Auto-Detection (v2.23.2)

### How Auto-Detection Works

The test runner automatically selects connection type based on test location:

```
tests.yaml
├── objectmodule_tests:       → External Connection (fast)
│   ├── declarative: [...]
│   └── procedural: {...}
│
└── forms:                    → Automation Server (slow, per-form)
    ├── name: Форма
    │   ├── declarative: [...]
    │   └── procedural: {...}
    └── name: ФормаНалаштувань
        └── declarative: [...]
```

**Key principle:** No flags needed - system detects and uses appropriate connection automatically!

### External Connection - ObjectModule Tests

**Automatically used for:** `objectmodule_tests` section

**Characteristics:**
- ✅ **Fast** (no UI overhead)
- ✅ **ObjectModule style** (direct attribute access)
- ✅ **Procedural tests** in ObjectModule
- ❌ No form access
- ❌ No UI testing

**Use for:** Business logic tests, attribute manipulation, calculations

**BSL Style:**
```bsl
// Direct access (no Объект. prefix)
Число1 = 10;
Добавить();  // No НаСервере suffix
```

### ❌ Automation Server - NOT AVAILABLE

**⚠️ Form testing cannot be implemented (v2.23.2+)**

**Intended use:** `forms[]` section (currently non-functional)

**Why it doesn't work:**
- ❌ V83.Application inaccessible from Python/PowerShell
- ❌ COM limitation, not a framework bug
- ❌ `forms[]` section will not execute

**Alternatives:**
- ✅ Use ObjectModule procedural tests (see above)
- Manual form testing

**See:** `docs/research/V83_INVESTIGATION_REPORT.md`

---

## Troubleshooting

### Issue: Procedural test fails with "Variable not defined (Объект)"
**Cause:** Test uses Form Module style in ObjectModule context
**Fix:** Remove `Объект.` prefix
```bsl
❌ BAD:  Объект.Число1 = 10;
✅ GOOD: Число1 = 10;
```

### Issue: Procedural test fails with "Procedure not found (ДобавитьНаСервере)"
**Cause:** Test uses Form Module style procedure names
**Fix:** Remove `НаСервере` suffix
```bsl
❌ BAD:  ДобавитьНаСервере();
✅ GOOD: Добавить();
```

### Issue: Declarative test fails with "No message contains ..."
**Cause:** Handler doesn't call `Сообщить()`
**Fix:** Add message to handler
```bsl
Процедура Добавить() Экспорт
    Результат = Число1 + Число2;
    Сообщить("Додавання виконано: " + Результат);  // ← Add this
КонецПроцедуры
```

### Issue: Test EPF not detected
**Cause:** Test EPF not generated or wrong path
**Fix:** Ensure `--output-format epf` and tests_file in config.yaml

---

## Summary

**LLM testing workflow:**
1. ✅ Generate processor + tests
2. ✅ Compile EPF (dual compilation: clean + test)
3. ✅ Run test_runner
4. ✅ Analyze results
5. ✅ Fix handlers based on failures
6. ✅ Repeat until all pass

**Key principles:**
- Declarative tests for simple scenarios
- Procedural tests for complex logic
- ObjectModule style for procedural tests
- Clear error messages
- Iterate based on test results

**Result:** LLM can fully test 1C processors automatically without manual intervention! 🎉
