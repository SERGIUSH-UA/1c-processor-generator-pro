# ContactCenterLite - PlannerField Showcase

Comprehensive example demonstrating **PlannerField** (Scheduler/Planner control) with all its features.

## Features Demonstrated

### PlannerField Core Features
- **Dimensions** (`Измерения`) - operators as rows
- **Display Periods** (`ТекущиеПериодыОтображения`) - time range display
- **Items** (`Элементы`) - schedule items with start/end times
- **Dimension Values** (`ЗначенияИзмерений`) - assigning items to dimension rows
- **Colors** (`ЦветФона`, `ЦветТекста`) - color-coded shift types
- **Item Data** (`Значение`) - storing custom data in items

### Shift Types with Color Coding
| Shift Type | Background Color | Text Color |
|------------|-----------------|------------|
| Day (Дневная) | Light Green | Dark Green |
| Evening (Вечерняя) | Light Blue | Dark Blue |
| Night (Ночная) | Plum | Indigo |
| Morning (Утренняя) | Peach | Brown |

### Events Demonstrated
- `Selection` - click on planner item to show details
- `Drag` - move item to new time slot
- `DragCheck` - validate drag operation

### Additional Features
- **CalendarField** for date selection
- **Navigation buttons** (prev/next day)
- **Statistics panel** (total shifts, operators online, avg duration)
- **Table view** (collapsible secondary view)

## Key Planner API Patterns

```bsl
// 1. Set display period (time range to show)
Планировщик.ТекущиеПериодыОтображения.Очистить();
Планировщик.ТекущиеПериодыОтображения.Добавить(НачалоПериода, КонецПериода);

// 2. Add dimension with elements (creates rows)
// Structure: Измерения -> ИзмерениеПланировщика.Элементы -> ЭлементИзмерения
ИзмерениеОператор = Планировщик.Измерения.Добавить("Оператор");

// Add operator rows as dimension elements
ЭлементИзмерения = ИзмерениеОператор.Элементы.Добавить("Иванов И.И.");
ЭлементИзмерения.Текст = "Иванов И.И.";

ЭлементИзмерения = ИзмерениеОператор.Элементы.Добавить("Петров П.П.");
ЭлементИзмерения.Текст = "Петров П.П.";

// 3. Create schedule item
ЭлементПланировщика = Планировщик.Элементы.Добавить(ДатаНачала, ДатаОкончания);

// 4. CRITICAL: Assign item to dimension row using ФиксированноеСоответствие
СоответствиеИзмерений = Новый Соответствие;
СоответствиеИзмерений.Вставить("Оператор", "Иванов И.И.");
ЭлементПланировщика.ЗначенияИзмерений = Новый ФиксированноеСоответствие(СоответствиеИзмерений);

// 5. Set item appearance
ЭлементПланировщика.Текст = "Дневная смена";
ЭлементПланировщика.ЦветФона = Новый Цвет(144, 238, 144);  // Light green
ЭлементПланировщика.ЦветТекста = Новый Цвет(0, 100, 0);    // Dark green

// 6. Store custom data for later retrieval
ДанныеСмены = Новый Структура("Оператор, ТипСмены", "Иванов И.И.", "Дневная");
ЭлементПланировщика.Значение = ДанныеСмены;

// 7. Access selected item data in Selection event
Процедура ПланировщикВыбор(Элемент, ВыделенныеЭлементы, СтандартнаяОбработка)
    ВыбранныйЭлемент = ВыделенныеЭлементы[0];
    ДанныеСмены = ВыбранныйЭлемент.Значение;  // Get our structure
    ВремяНачала = ВыбранныйЭлемент.Начало;
    ВремяОкончания = ВыбранныйЭлемент.Конец;
КонецПроцедуры
```

## YAML Configuration

### PlannerField Definition
```yaml
form_attributes:
  - name: Планировщик
    type: planner           # Special type for Planner
    time_scale: Hour        # Hour, Day, Week, Month
    time_scale_interval: 1
    display_current_date: true
    show_weekends: true

elements:
  - type: PlannerField
    name: ПланировщикОператоров
    attribute: Планировщик
    width: 60
    height: 18
    enable_drag: true
    events:
      Selection: ПланировщикВыбор
      Drag: ПланировщикПеретаскивание
      DragCheck: ПланировщикПроверкаПеретаскивания
```

## Generate EPF

```bash
python -m 1c_processor_generator yaml \
  --config examples/yaml/contact_center_lite/config.yaml \
  --handlers-file examples/yaml/contact_center_lite/handlers.bsl \
  --output output \
  --output-format epf
```

## Files

- `config.yaml` - Processor configuration with PlannerField, CalendarField, Table
- `handlers.bsl` - Event handlers with full Planner initialization logic
- `README.md` - This documentation

## Version Requirements

- 1c-processor-generator v2.47.0+
- PlannerField with pl:Planner type support
