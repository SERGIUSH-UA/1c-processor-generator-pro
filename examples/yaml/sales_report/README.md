# Sales Report Example / Приклад звіту по продажах

**Purpose:** Complete example of a monthly sales report with date range filters and results table

**Демонструє:**
- Date range input fields (ДатаНачала, ДатаОкончания)
- Optional catalog reference filter (Организация)
- ValueTable for displaying results
- UsualGroup for organizing UI elements
- Client-side validation + server-side query
- BSL query with aggregation (GROUP BY month)
- Error handling with try-catch

---

## Use Case / Випадок використання

User requests: *"Generate a processor that calculates sales by month and displays a table with monthly columns"*

This example shows exactly that pattern - filtering by date range and displaying aggregated monthly data.

---

## Structure / Структура

```
sales_report/
├── config.yaml              # Processor configuration
└── handlers/
    ├── ПриОткрытии.bsl      # Form initialization (set default dates)
    ├── Сформировать.bsl     # Client validation
    └── СформироватьНаСервере.bsl  # Server query and data loading
```

---

## Key Features / Ключові можливості

### 1. Form Layout

```yaml
form:
  elements:
    - UsualGroup (Filters)
      - UsualGroup (Horizontal date range)
        - InputField (StartDate)
        - InputField (EndDate)
      - InputField (Organization)
      - Button (Generate)
    - Table (Results)
```

**Why this layout?**
- Filters grouped together at the top
- Date range in horizontal group for compact display
- Generate button in filter group
- Table takes remaining space

### 2. Client-Server Split

**Client (Сформировать.bsl):**
- Validates required fields
- Checks date range logic (end >= start)
- Shows user messages
- Calls server handler

**Server (СформироватьНаСервере.bsl):**
- Builds SQL query
- Aggregates data by month using `НАЧАЛОПЕРИОДА(Дата, МЕСЯЦ)`
- Handles optional filters (Organization)
- Error handling with try-catch
- Fills results table

### 3. Data Types

**Attributes:**
- `date` - For date range filters
- `CatalogRef.Организации` - Reference to Organizations catalog

**ValueTable columns:**
- `date` - Period (first day of month)
- `string` - Month name formatted (e.g., "Январь 2025")
- `number` - Quantities and amounts with precision

---

## Query Pattern / Паттерн запиту

The server handler demonstrates a complete 1C query pattern:

```bsl
Запрос = Новый Запрос;
Запрос.Текст = "...";
Запрос.УстановитьПараметр("Param", Value);

РезультатЗапроса = Запрос.Выполнить();
Выборка = РезультатЗапроса.Выбрать();

Пока Выборка.Следующий() Цикл
    // Process each row
КонецЦикла;
```

**Key query features:**
- `НАЧАЛОПЕРИОДА(Дата, МЕСЯЦ)` - Group by month start
- `СУММА()` - Aggregate function
- `МЕЖДУ &Start И &End` - Date range filter
- Conditional filter: `?(Condition, TrueSQL, FalseSQL)`
- `СГРУППИРОВАТЬ ПО` - GROUP BY clause
- `УПОРЯДОЧИТЬ ПО` - ORDER BY clause

---

## Generation Command / Команда генерації

```bash
cd ~/SmallBusiness\.claude\tools\1c_processor_generator\examples\yaml\sales_report

python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers handlers/
```

---

## Learning Points for LLMs / Уроки для ЛЛМ

1. **Report Pattern = Filters + Table**
   - Input section (UsualGroup with filters)
   - Generate button
   - Results table (ValueTable)

2. **Always validate on client before calling server**
   - Check required fields: `ЗначениеЗаполнено()`
   - Check business logic: date range, amounts > 0, etc.
   - Show clear messages: `Сообщить()`

3. **Server queries must use parameters**
   - Never concatenate values into SQL text
   - Use `&ParameterName` and `УстановитьПараметр()`

4. **Handle errors gracefully**
   - Wrap risky operations in `Попытка...Исключение`
   - Show user-friendly error messages

5. **Format dates for display**
   - Store date value in one column (Период)
   - Format for display in another column (МесяцСтрокой)
   - Use `Формат()` function

---

## Variations / Варіації

This pattern can be adapted for:
- Daily/weekly/yearly reports (change `МЕСЯЦ` to `ДЕНЬ`/`НЕДЕЛЯ`/`ГОД`)
- Different document types (purchases, transfers, etc.)
- Multiple grouping levels (month + product, month + customer)
- Charts (add Chart element to form)

---

**Version:** 2.7.3
**Last updated:** 2025-10-14
