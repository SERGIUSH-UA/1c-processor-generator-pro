# Task Manager Example

Task management processor demonstrating Master-Detail pattern with CRUD operations.

## Features Demonstrated

- **Master-Detail Pattern** - Task list (Master) + Detail panel with selected task info
- **ValueTable** - Tasks stored in form-level ValueTable
- **CRUD Operations** - Add, Edit, Delete commands with StdPictures
- **Row Filtering** - ChoiceList-based status and priority filters
- **OnActivateRow Event** - Auto-update detail panel on row selection
- **Statistics Panel** - Real-time task counters

## Key Patterns

### Master-Detail Layout
```yaml
- type: UsualGroup
  name: ГруппаОсновная
  group_direction: Horizontal
  child_items:
    # Master: Task list
    - type: UsualGroup
      name: ГруппаСписок
      width: 50
      child_items:
        - type: Table
          name: ТаблицаЗадачи
          attribute: Задачи
          events:
            OnActivateRow: ЗадачиПриАктивизацииСтроки

    # Detail: Selected task info
    - type: UsualGroup
      name: ГруппаДетали
      representation: StrongSeparation
      child_items:
        - type: InputField
          attribute: ВыбраннаяЗадачаНазвание
          read_only: true
```

### OnActivateRow Handler
```bsl
//# ЗадачиПриАктивизацииСтроки
    // Update detail panel when row changes
    ОбновитьДеталиЗадачиНаСервере();
```

### ChoiceList Filter
```yaml
- type: InputField
  name: ФильтрСтатус
  attribute: ФильтрСтатус
  list_choice_mode: true
  choice_list:
    - value: ""
      presentation_ru: "Все"
    - value: "Новая"
      presentation_ru: "Новая"
    - value: "В работе"
      presentation_ru: "В работе"
  events:
    OnChange: ФильтрИзменен
```

### CRUD Commands
```yaml
commands:
  - name: ДобавитьЗадачу
    handler: ДобавитьЗадачуКоманда
    picture: StdPicture.CreateListItem

  - name: УдалитьЗадачу
    handler: УдалитьЗадачуКоманда
    picture: StdPicture.Delete
```

## Usage

```bash
python -m 1c_processor_generator yaml \
  --config examples/yaml/task_manager/config.yaml \
  --handlers-file examples/yaml/task_manager/handlers.bsl \
  --output tmp/task_manager \
  --output-format epf
```

## Screenshot

```
┌─────────────────────────────────────────────────────────────┐
│                    МЕНЕДЖЕР ЗАДАЧ                           │
├─────────────────────────────────────────────────────────────┤
│ [+Добавить] [✏Редактировать] [×Удалить] | Статус:[▼Все]     │
│                                           Приоритет:[▼Все]  │
│                                           ☐ Показывать завершенные │
├───────────────────────────────┬─────────────────────────────┤
│ Список задач                  │ ┌─────────────────────────┐ │
│ ┌───────────────────────────┐ │ │ Детали задачи           │ │
│ │ # │ Название        │ Ст  │ │ │                         │ │
│ ├───┼─────────────────┼─────┤ │ │ Название:               │ │
│ │ 1 │ Подготовить от..│В раб│ │ │ [Подготовить отчет...] │ │
│ │ 2 │ Провести встр...│Новая│ │ │                         │ │
│ │ 3 │ Обновить докум..│Новая│ │ │ Описание:               │ │
│ │ 4 │ Оптимизировать..│В раб│ │ │ [Собрать данные...]    │ │
│ └───┴─────────────────┴─────┘ │ │                         │ │
│                               │ │ Статус: [В работе]      │ │
│                               │ │ Приоритет: [Высокий]    │ │
│                               │ │ Срок: [07.12.2025]      │ │
│                               │ │                         │ │
│                               │ │ [В работу] [Завершить]  │ │
│                               │ └─────────────────────────┘ │
├───────────────────────────────┴─────────────────────────────┤
│ Всего задач: 6  |  Активных: 4  |  Завершенных: 2           │
└─────────────────────────────────────────────────────────────┘
```

## Data Structure

### ValueTable: Задачи
| Column | Type | Description |
|--------|------|-------------|
| Номер | number | Task ID |
| Название | string | Task title |
| Описание | string | Task description |
| Статус | string | Status (Новая/В работе/Завершена) |
| Приоритет | string | Priority (Высокий/Средний/Низкий) |
| Срок | date | Due date |
| Создана | date | Created date |
| Завершена | date | Completed date |

## Version

Requires generator v2.46.0+ for full feature support.
