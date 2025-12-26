# Демо новых элементов формы (v2.2.0)

Пример демонстрирует использование новых элементов форм, добавленных в версии 2.2.0.

## Новые возможности

### 1. RadioButtonField (Переключатель)
Используется для выбора одного варианта из нескольких:

```yaml
- type: RadioButtonField
  name: ТипОперацииПоле
  attribute: ТипОперации
  title_location: None
  radio_button_type: Tumbler  # или RadioButton
  choice_list:
    - value: "Импорт"
      value_type: "xs:string"
      presentation_ru: "Импорт данных"
      presentation_uk: "Імпорт даних"
```

**Параметры:**
- `radio_button_type`: `Tumbler` (переключатель) или `RadioButton` (радиокнопки)
- `choice_list`: Обязательный - список вариантов выбора
- `title_location`: Расположение заголовка (None, Left, Right, Top, Bottom)

### 2. CheckBoxField (Флажок)
Используется для включения/отключения опций:

```yaml
- type: CheckBoxField
  name: ВыполнитьПроверкуПоле
  attribute: ВыполнитьПроверку
  title_location: Right
  width: 30
  events:
    OnChange: ВыполнитьПроверкуПриИзменении
```

**Параметры:**
- `width`: Ширина элемента
- `title_location`: Расположение заголовка (обычно Right для флажков)

### 3. InputField с ChoiceList (Выпадающий список)
Поле ввода с предопределенными значениями:

```yaml
- type: InputField
  name: РежимРаботыПоле
  attribute: РежимРаботы
  width: 40
  horizontal_stretch: false
  choice_list:
    - value: "Автоматический"
      value_type: "xs:string"
      presentation_ru: "Автоматический"
      presentation_uk: "Автоматичний"
```

**Параметры:**
- `choice_list`: Список предопределенных значений (dropdown)
- `width`: Ширина элемента
- `horizontal_stretch`: Растягивать по горизонтали (true/false)

### 4. InputField с InputHint (Подсказка ввода)
Поле ввода с текстом-подсказкой (placeholder):

```yaml
- type: InputField
  name: ПоискСтрокиПоле
  attribute: ПоискСтроки
  width: 50
  input_hint_ru: "Введите текст для поиска..."
  input_hint_uk: "Введіть текст для пошуку..."
```

**Параметры:**
- `input_hint_ru`: Подсказка на русском
- `input_hint_uk`: Подсказка на украинском

## Структура файлов

```
form_elements_demo/
├── config.yaml                           # YAML конфигурация
└── handlers/
    ├── ПриОткрытии.bsl                  # Инициализация формы
    ├── ТипОперацииПриИзменении.bsl      # RadioButtonField handler
    ├── ВыполнитьПроверкуПриИзменении.bsl # CheckBoxField handler
    ├── РежимРаботыПриИзменении.bsl      # InputField + ChoiceList handler
    ├── ПоискСтрокиПриИзменении.bsl      # InputField + InputHint handler
    ├── Выполнить.bsl                    # Команда выполнения
    ├── ВыполнитьНаСервере.bsl          # Серверный обработчик
    └── Очистить.bsl                     # Команда очистки
```

## Генерация обработки

```bash
cd examples/yaml/form_elements_demo
python -m 1c_processor_generator yaml --config config.yaml --handlers handlers/
```

Результат: `ДемоЭлементовФормы.xml` готов к открытию в 1C:Enterprise 8.3

## Что происходит в примере

1. **При открытии формы** (`ПриОткрытии.bsl`):
   - Устанавливаются значения по умолчанию
   - Статус: "Готов к работе"

2. **Выбор типа операции** (RadioButtonField):
   - Изменение переключателя обновляет статус
   - Показывает выбранный тип операции

3. **Настройка опций** (CheckBoxField):
   - Флажки включают/отключают проверку и обработку
   - Обработчик OnChange обновляет статус

4. **Выбор режима работы** (InputField + ChoiceList):
   - Выпадающий список с тремя вариантами
   - Автоматическая настройка флажков в зависимости от режима

5. **Поиск** (InputField + InputHint):
   - Текстовое поле с подсказкой
   - Показывает введенный текст в статусе

6. **Кнопка "Выполнить"**:
   - Валидация заполненных полей
   - Вызов серверного обработчика
   - Отображение результата

7. **Кнопка "Очистить"**:
   - Очистка всех полей формы

## Ключевые паттерны

### ID Sequencing
- **RadioButtonField**: +3 (Element + ContextMenu + ExtendedTooltip)
- **CheckBoxField**: +3 (Element + ContextMenu + ExtendedTooltip)

### ChoiceList структура
```xml
<ChoiceList>
  <xr:Item>
    <xr:Presentation/>
    <xr:CheckState>0</xr:CheckState>
    <xr:Value xsi:type="FormChoiceListDesTimeValue">
      <Presentation>
        <v8:item>
          <v8:lang>ru</v8:lang>
          <v8:content>Текст</v8:content>
        </v8:item>
      </Presentation>
      <Value xsi:type="xs:string">Значение</Value>
    </xr:Value>
  </xr:Item>
</ChoiceList>
```

### InputHint структура
```xml
<InputHint>
  <v8:item>
    <v8:lang>ru</v8:lang>
    <v8:content>Введите текст...</v8:content>
  </v8:item>
  <v8:item>
    <v8:lang>uk</v8:lang>
    <v8:content>Введіть текст...</v8:content>
  </v8:item>
</InputHint>
```

## Полезные ссылки

- [YAML_GUIDE.md](../../../YAML_GUIDE.md) - Полная документация YAML API
- [LLM_PROMPT.md](../../../LLM_PROMPT.md) - Инструкции для LLM
- [UI_PATTERNS.md](../../../UI_PATTERNS.md) - Библиотека UI паттернов
