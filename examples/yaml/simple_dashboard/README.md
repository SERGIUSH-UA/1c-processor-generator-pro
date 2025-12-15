# Simple Dashboard Example

KPI Dashboard demonstrating Loading State pattern and colored trend indicators.

## Features Demonstrated

- **Loading State Pattern** - Pages with `pages_representation: None` for showing loading spinner
- **KPI Cards** - UsualGroup with `representation: StrongSeparation` for card-like appearance
- **Colored Trends** - LabelDecoration with `formatted: true` for HTML-styled trends (↑↓→)
- **Period Navigation** - Date InputFields for filtering data

## Key Patterns

### Loading State
```yaml
- type: Pages
  name: СтраницыКонтент
  pages_representation: None  # Hidden tabs
  pages:
    - name: СтраницаЗагрузка
      # Loading spinner + text
    - name: СтраницаПоказатели
      # Actual content
```

Switch pages in BSL:
```bsl
// Show loading
Элементы.СтраницыКонтент.ТекущаяСтраница = Элементы.СтраницаЗагрузка;

// ... do work ...

// Show content
Элементы.СтраницыКонтент.ТекущаяСтраница = Элементы.СтраницаПоказатели;
```

### KPI Card with Trend
```yaml
- type: UsualGroup
  name: КарточкаПродажи
  group_direction: Vertical
  representation: StrongSeparation  # Card border
  child_items:
    - type: LabelDecoration
      name: ЗаголовокПродажи
      title_ru: "ПРОДАЖИ"
      font: {bold: true, height: 10}
    - type: LabelField
      name: ЗначениеПродажи
      attribute: ВсегоПродаж
    - type: LabelDecoration
      name: ТрендПродажи
      formatted: true  # Enable HTML tags
```

Update trend with color in BSL:
```bsl
ТекстТренда = "<font color='green'>↑ +12.5%</font>";
Элементы.ТрендПродажи.Заголовок = ТекстТренда;
```

## Usage

```bash
python -m 1c_processor_generator yaml \
  --config examples/yaml/simple_dashboard/config.yaml \
  --handlers-file examples/yaml/simple_dashboard/handlers.bsl \
  --output tmp/simple_dashboard \
  --output-format epf
```

## Screenshot

```
┌─────────────────────────────────────────────┐
│           ПАНЕЛЬ ПОКАЗАТЕЛЕЙ                │
├─────────────────────────────────────────────┤
│ с [01.12.2025] по [31.12.2025] [Обновить]   │
├─────────────────────────────────────────────┤
│ ┌──────────────┐  ┌──────────────┐          │
│ │   ПРОДАЖИ    │  │    ЗАКАЗЫ    │          │
│ │ 1 234 567,89 │  │     456      │          │
│ │  ↑ +12.5%    │  │   ↓ -3.2%    │          │
│ └──────────────┘  └──────────────┘          │
│ ┌──────────────┐  ┌──────────────┐          │
│ │ СРЕДНИЙ ЧЕК  │  │  КОНВЕРСИЯ   │          │
│ │  2 706,95    │  │    3,45%     │          │
│ │   → 0.0%     │  │   ↑ +5.8%    │          │
│ └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────┘
```

## Version

Requires generator v2.45.0+ for FormattedString support.
