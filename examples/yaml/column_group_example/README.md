# ColumnGroup Example (v2.37.0+ Phase 2 Complete)

Демонструє використання **ColumnGroup** - елемента для групування колонок таблиці під одним заголовком.

## Що таке ColumnGroup?

**ColumnGroup** - це контейнерний елемент, який групує кілька колонок таблиці під одним багаторівневим заголовком. Використовується для:

- **Логічного групування** пов'язаних даних (Дата + Час, Кількість + Ціна + Сума)
- **Візуальної організації** складних таблиць з багатьма колонками
- **Багаторівневих заголовків** (header + sub-headers)
- **Професійного вигляду** звітів та форм списків

## Структура прикладу

### Таблиця з 3 групами колонок:

```
| Операція | ┌─ Дата і час ─┐ | ┌───── Суми ──────┐ | Статус |
|          | Дата    | Час  | Дебет | Кредит | Підсумок |        |
|----------|---------|------|-------|--------|----------|--------|
| ...      | ...     | ...  | ...   | ...    | ...      | ...    |
```

1. **DateTimeGroup** - Горизонтальна група з 2 колонок (Date + Time)
   - Вирівнювання: Center
   - Tooltip: "Дата і час операції"

2. **AmountsGroup** - Горизонтальна група з 3 колонок (Debit + Credit + Total)
   - Вирівнювання: Right
   - Tooltip: "Дебет, Кредит та Підсумок"

3. **Operation і Status** - Окремі колонки поза групами

## Ключові особливості ColumnGroup

### 1. Властивості ColumnGroup

```yaml
- type: ColumnGroup
  name: DateTimeGroup

  # Багатомовний заголовок (обов'язково)
  title_ru: Дата и время
  title_uk: Дата і час
  title_en: Date & Time

  # Багатомовний tooltip (опціонально)
  tooltip_ru: Дата и время операции
  tooltip_uk: Дата і час операції
  tooltip_en: Operation date and time

  # Напрямок розміщення (Horizontal | Vertical)
  group_layout: Horizontal  # default

  # Показувати заголовок групи
  show_in_header: true  # default

  # Вирівнювання (v2.36.0+ Phase 2)
  horizontal_align: Center  # Left | Center | Right
  vertical_align: Center    # Top | Center | Bottom

  # Вкладені колонки (тільки field-типи!)
  elements:
    - type: LabelField
      name: Date
      attribute: Date
    - type: LabelField
      name: Time
      attribute: Time
```

### 2. Дозволені дочірні елементи

ColumnGroup може містити **ТІЛЬКИ field-типи**:
- ✅ **LabelField** - Для відображення даних (найчастіше)
- ✅ **InputField** - Для редагування даних
- ✅ **CheckBoxField** - Для boolean полів
- ✅ **PictureField** - Для іконок/індикаторів (v2.36.0+)

❌ **НЕ дозволено**: Button, UsualGroup, Pages, інші ColumnGroup

### 3. Валідація при парсингу

```python
# yaml_parser.py автоматично перевіряє типи дітей
allowed_child_types = {"LabelField", "InputField", "CheckBoxField", "PictureField"}

if child_type not in allowed_child_types:
    print(f"⚠️  ColumnGroup '{name}' може містити тільки field елементи")
```

## Use Cases (Реальні застосування)

### 1. Фінансові звіти

```yaml
# Групування колонок за періодами
- type: ColumnGroup
  name: Q1Group
  title: "1 квартал"
  elements:
    - {type: LabelField, name: Jan, attribute: January}
    - {type: LabelField, name: Feb, attribute: February}
    - {type: LabelField, name: Mar, attribute: March}

- type: ColumnGroup
  name: Q2Group
  title: "2 квартал"
  elements:
    - {type: LabelField, name: Apr, attribute: April}
    - {type: LabelField, name: May, attribute: May}
    - {type: LabelField, name: Jun, attribute: June}
```

**Результат:**
```
| Товар | ┌─── 1 квартал ───┐ | ┌─── 2 квартал ───┐ |
|       | Січ | Лют | Бер  | Кві | Тра | Чер  |
```

### 2. План vs Факт

```yaml
- type: ColumnGroup
  name: PlanGroup
  title: "План"
  elements:
    - {type: LabelField, name: PlanQuantity, attribute: PlanQty}
    - {type: LabelField, name: PlanAmount, attribute: PlanAmt}

- type: ColumnGroup
  name: FactGroup
  title: "Факт"
  elements:
    - {type: LabelField, name: FactQuantity, attribute: FactQty}
    - {type: LabelField, name: FactAmount, attribute: FactAmt}
```

**Результат:**
```
| Продукт | ┌──── План ────┐ | ┌──── Факт ────┐ |
|         | Кіл-ть | Сума | Кіл-ть | Сума |
```

### 3. Адреса (декомпозиція на частини)

```yaml
- type: ColumnGroup
  name: AddressGroup
  title: "Адреса доставки"
  elements:
    - {type: InputField, name: City, attribute: City}
    - {type: InputField, name: Street, attribute: Street}
    - {type: InputField, name: Building, attribute: Building}
```

### 4. Багаторівневі категорії

```yaml
# Категорія → Підкатегорія → Товар
- type: ColumnGroup
  name: CategoryGroup
  title: "Класифікація"
  elements:
    - {type: LabelField, name: Category, attribute: Category}
    - {type: LabelField, name: Subcategory, attribute: Subcategory}
    - {type: LabelField, name: Product, attribute: Product}
```

## Архітектура і ID allocation

### ID Increment Pattern

```python
# constants.py
ELEMENT_ID_INCREMENTS = {
    "ColumnGroup": 2,  # Element + ExtendedTooltip
}
```

**Приклад ID послідовності:**

```
Table id=10
├─ ContextMenu id=11
├─ CommandBar id=12
├─ ExtendedTooltip id=13
└─ ChildItems
    ├─ LabelField id=14 (Operation, окрема колонка)
    │   ├─ ContextMenu id=15
    │   └─ ExtendedTooltip id=16
    ├─ ColumnGroup id=17 (DateTimeGroup)
    │   ├─ ExtendedTooltip id=18
    │   └─ ChildItems
    │       ├─ LabelField id=19 (Date)
    │       │   ├─ ContextMenu id=20
    │       │   └─ ExtendedTooltip id=21
    │       └─ LabelField id=22 (Time)
    │           ├─ ContextMenu id=23
    │           └─ ExtendedTooltip id=24
    └─ ColumnGroup id=25 (AmountsGroup)
        ├─ ExtendedTooltip id=26
        └─ ChildItems
            ├─ LabelField id=27 (Debit)
            │   ├─ ContextMenu id=28
            │   └─ ExtendedTooltip id=29
            ├─ LabelField id=30 (Credit)
            │   ├─ ContextMenu id=31
            │   └─ ExtendedTooltip id=32
            └─ LabelField id=33 (Total)
                ├─ ContextMenu id=34
                └─ ExtendedTooltip id=35
```

**Рекурсивна обробка** (v2.7.3+):
- `generator._process_form_element()` автоматично обробляє вкладені елементи
- Жодних змін до generator.py не потрібно - інфраструктура вже готова

## XML Structure (Generated)

```xml
<ColumnGroup name="DateTimeGroup" id="17">
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Дата и время</v8:content>
        </v8:item>
        <v8:item>
            <v8:lang>uk</v8:lang>
            <v8:content>Дата і час</v8:content>
        </v8:item>
        <v8:item>
            <v8:lang>en</v8:lang>
            <v8:content>Date & Time</v8:content>
        </v8:item>
    </Title>
    <ToolTip>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Дата и время операции</v8:content>
        </v8:item>
        <!-- ... -->
    </ToolTip>
    <Group>Horizontal</Group>
    <ShowInHeader>true</ShowInHeader>
    <HorizontalAlign>Center</HorizontalAlign>
    <ExtendedTooltip name="DateTimeGroupРасширеннаяПодсказка" id="18"/>
    <ChildItems>
        <LabelField name="Date" id="19">
            <DataPath>Объект.Operations.Date</DataPath>
            <TitleLocation>None</TitleLocation>
            <Width>12</Width>
            <ContextMenu name="DateКонтекстноеМеню" id="20"/>
            <ExtendedTooltip name="DateРасширеннаяПодсказка" id="21"/>
        </LabelField>
        <LabelField name="Time" id="22">
            <DataPath>Объект.Operations.Time</DataPath>
            <TitleLocation>None</TitleLocation>
            <Width>10</Width>
            <ContextMenu name="TimeКонтекстноеМеню" id="23"/>
            <ExtendedTooltip name="TimeРасширеннаяПодсказка" id="24"/>
        </LabelField>
    </ChildItems>
</ColumnGroup>
```

## Генерація і тестування

### Крок 1: Генерація XML

```bash
cd ~/project

python -m 1c_processor_generator yaml \
  --config examples/yaml/column_group_example/config.yaml \
  --handlers-file examples/yaml/column_group_example/handlers.bsl \
  --output tmp/column_group_example
```

### Крок 2: Компіляція в EPF (опціонально)

```bash
python -m 1c_processor_generator yaml \
  --config examples/yaml/column_group_example/config.yaml \
  --handlers-file examples/yaml/column_group_example/handlers.bsl \
  --output tmp/column_group_example \
  --output-format epf
```

### Крок 3: Відкриття в 1C

1. Відкрити Configurator
2. File → Open → tmp/column_group_example/ПримерГрупповКолонок.xml (або .epf)
3. Відкрити форму "Форма"
4. Натиснути "Завантажити дані" → Таблиця заповниться 7 операціями
5. Натиснути "Розрахувати підсумки" → Відобразяться загальні суми

## Що очікувати

### UI Вигляд

```
┌──────────────────────────────────────────────────────────────────┐
│ Групування колонок таблиці                                       │
├──────────────────────────────────────────────────────────────────┤
│ Пример групування колонок таблиці:                               │
│ 1. "Дата і час" - горизонтальна група з 2 колонок                │
│ 2. "Суми" - горизонтальна група з 3 колонок, вирівнювання Right  │
│ 3. "Статус" - окрема колонка поза групами                        │
├──────────────────────────────────────────────────────────────────┤
│ ┌─────────────┬────────────────────┬─────────────────────────────┬──────────┐
│ │ Операція    │  ┌─ Дата і час ─┐ │  ┌─────── Суми ────────┐    │ Статус   │
│ │             │  Дата      Час    │  Дебет  Кредит  Підсумок   │          │
│ ├─────────────┼───────────────────┼─────────────────────────────┼──────────┤
│ │Оплата від...│ 15.01.2025 10:30:0│ 15000        0     15000    │Проведено │
│ │Оплата поста.│ 15.01.2025 14:15:0│     0     8000    -8000    │Проведено │
│ │Оплата від...│ 16.01.2025 09:00:0│ 22000        0     22000    │Проведено │
│ │Виплата зарп.│ 16.01.2025 16:30:0│     0    12000   -12000    │Проведено │
│ │Оплата від...│ 17.01.2025 11:45:0│ 18500        0     18500    │В обробці │
│ │Оплата комун.│ 17.01.2025 15:00:0│     0     3500    -3500    │Проведено │
│ └─────────────┴───────────────────┴─────────────────────────────┴──────────┘
│
│ ┌─ Підсумки ──────────────────────────────────────────┐
│ │ Всього дебет: [  55500.00 ]  Всього кредит: [  23500.00 ]│
│ └────────────────────────────────────────────────────┘
│
│ [Завантажити дані]  [Розрахувати підсумки]
└──────────────────────────────────────────────────────────────────┘
```

### Повідомлення при роботі

1. **LoadData** → "Данные загружены: 7 операций"
2. **Calculate** → "Всього дебет: 55500.00", "Всього кредит: 23500.00", "Прибуток: 32000.00"
3. **OnActivateRow** → "Операція: Оплата від покупця №1, Дата: 15.01.2025, Дебет: 15000, Кредит: 0"

## Обмеження і Best Practices

### ❌ НЕ можна:
1. **Вкладені ColumnGroup** (ColumnGroup всередині ColumnGroup) - не підтримується платформою
2. **Button/UsualGroup в ColumnGroup** - тільки field-типи дозволені
3. **ColumnGroup поза Table** - має сенс тільки в контексті таблиці

### ✅ Best Practices:
1. **Логічне групування** - об'єднуйте пов'язані колонки (Дата+Час, Кількість+Ціна+Сума)
2. **Не більше 3-4 колонок в групі** - для читабельності
3. **Використовуйте tooltip** - поясніть призначення групи
4. **Вирівнювання** - Right для чисел, Center для дат, Left для тексту
5. **TitleLocation=None** для вкладених полів - заголовки в header групи

## Версія і сумісність

- **Версія:** v2.37.0+ (Phase 2 Complete)
- **Платформа:** 1C:Enterprise 8.3.23+ (всі версії з підтримкою керованих форм)
- **Формат XML:** 2.11+ (рекомендовано), 2.10+ (сумісно)

## Пов'язані фічі

- **v2.36.0+** - horizontal_align/vertical_align для всіх елементів
- **v2.7.3+** - Рекурсивна обробка вкладених елементів (infrastructure готова)
- **v2.25.0+** - Sync tool автоматично розпізнає ColumnGroup (HierarchicalExtractor)

## Документація

- [QUICK_REFERENCE.md](../../../docs/QUICK_REFERENCE.md) - Швидкий довідник
- [docs/reference/API_REFERENCE.md](../../../docs/reference/API_REFERENCE.md) - Повний API опис
- [CHANGELOG.md](../../../CHANGELOG.md) - v2.37.0 release notes
