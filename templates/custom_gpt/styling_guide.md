# 1C Processor Generator - Styling Guide

> **Target:** ~4K tokens | **Focus:** UI styling | **For:** ChatGPT, Gemini, Claude Web
> **Requires:** v2.43.0+ for colors/fonts, v2.68.0+ for ConditionalAppearance & Table Heights

---

## Quick Reference

| Feature | Version | Property |
|---------|---------|----------|
| Text colors | 2.43.0+ | `text_color`, `title_text_color` |
| Background | 2.43.0+ | `back_color`, `border_color` |
| Fonts | 2.43.0+ | `font`, `title_font`, `footer_font` |
| Font size/family | 2.68.0+ | `size`, `face_name` |
| Formatted text | 2.45.0+ | `formatted: true` |
| Table heights | 2.68.0+ | `height_in_table_rows`, `header_height`, `footer_height` |
| Column title height | 2.68.0+ | `title_height` (InputField in Table) |
| Conditional styling | 2.68.0+ | `conditional_appearances` |
| Column groups | 2.37.0+ | `type: ColumnGroup` |
| Tree tables | 2.64.0+ | `representation: tree` |

---

## 1. Colors (HEX format)

```yaml
elements:
  - type: InputField
    name: ВажноеПоле
    attribute: ВажныеДанные

    # Text colors
    text_color: "#333333"           # Field text
    title_text_color: "#0066CC"     # Label text

    # Background
    back_color: "#FFFDE7"           # Field background
    border_color: "#FF6600"         # Border
```

### Color Palettes

**Success (green):**
```yaml
back_color: "#E8F5E9"
text_color: "#2E7D32"
```

**Error (red):**
```yaml
back_color: "#FFEBEE"
text_color: "#C62828"
```

**Warning (orange):**
```yaml
back_color: "#FFF3E0"
text_color: "#E65100"
```

**Info (blue):**
```yaml
back_color: "#E3F2FD"
text_color: "#0D47A1"
```

**Neutral (gray):**
```yaml
back_color: "#F5F5F5"
text_color: "#616161"
```

---

## 2. Fonts

### Simple font (size only - v2.68.0+)
```yaml
font:
  size: 20              # Font size in points
  bold: true
  italic: false
```
**Auto-generates:** `ref="sys:DefaultGUIFont"` + `kind="WindowsFont"`

### Font with family (v2.68.0+)
```yaml
font:
  size: 16
  face_name: Arial      # Font family
  bold: true
```

### Style-based font (classic)
```yaml
font:
  ref: "style:LargeTextFont"
  bold: true
  height: 14            # Note: 'height' not 'size' for style refs
  kind: StyleItem
```

### InputField fonts
```yaml
- type: InputField
  name: ЗаголовокПоле
  attribute: Данные

  # Label font
  title_font:
    size: 12
    bold: true

  # Field text font
  font:
    size: 10
    face_name: Arial
```

### LabelDecoration fonts
```yaml
- type: LabelDecoration
  name: Заголовок
  title_ru: "Section Header"
  font:
    size: 16
    bold: true
```

### Font properties reference
| Property | Description |
|----------|-------------|
| `size` | Font size in points (auto: sys:DefaultGUIFont) |
| `face_name` | Font family (Arial, Tahoma, etc.) |
| `bold` | Bold weight |
| `italic` | Italic style |
| `underline` | Underline decoration |
| `strikethrough` | Strikethrough decoration |
| `scale` | Scale percentage |

### Standard style references
| Reference | Use case |
|-----------|----------|
| `style:NormalTextFont` | Regular text |
| `style:LargeTextFont` | Headers, titles |
| `style:SmallTextFont` | Captions, hints |
| `style:ExtraLargeTextFont` | Main headers |
| `sys:DefaultGUIFont` | System default (auto with `size`) |

---

## 3. Formatted Text (HTML)

```yaml
- type: LabelDecoration
  name: Предупреждение
  formatted: true
  title: "<b>WARNING:</b> This action is <font color='red'>irreversible</font>!"
```

**Supported tags:**
- `<b>text</b>` - bold
- `<i>text</i>` - italic
- `<u>text</u>` - underline
- `<font color='#FF0000'>text</font>` - color

---

## 4. Conditional Appearance (v2.68.0+)

Dynamic row styling based on data. **CRITICAL:** Must be at form level!

### Basic structure
```yaml
forms:
  - name: Форма
    default: true

    conditional_appearances:
      - name: RuleName
        selection: [ElementName]       # Target element names
        filter:                        # Condition
          field: TableName.ColumnName  # Data path
          comparison: Equal            # Equal or NotEqual
          value: true                  # Value to compare
          value_type: boolean          # boolean, string, number
        appearance:                    # Styling
          back_color: "#FF0000"
          text_color: "#FFFFFF"
          font_bold: true
          font_italic: false
```

### Data path format
```yaml
# For TabularSection:
field: Объект.TableName.ColumnName

# For ValueTable:
field: TableName.ColumnName

# For form attribute:
field: AttributeName
```

### Complete example
```yaml
conditional_appearances:
  # Highlight errors in red
  - name: ВыделитьОшибки
    selection: [СтатусКолонка, СуммаКолонка]
    filter:
      field: Результаты.Статус
      comparison: Equal
      value: "Ошибка"
      value_type: string
    appearance:
      back_color: "#FFEBEE"
      text_color: "#C62828"
      font_bold: true

  # Highlight success in green
  - name: ВыделитьУспех
    selection: [СтатусКолонка, СуммаКолонка]
    filter:
      field: Результаты.Статус
      comparison: Equal
      value: "Выполнено"
      value_type: string
    appearance:
      back_color: "#E8F5E9"
      text_color: "#2E7D32"

  # Hide inactive rows
  - name: СкрытьНеактивные
    selection: [СтрокаТаблицы]
    filter:
      field: Объект.Данные.Активен
      comparison: Equal
      value: false
      value_type: boolean
    appearance:
      visible: false
```

### Appearance properties
| Property | Description |
|----------|-------------|
| `back_color` | Background color (#RRGGBB) |
| `text_color` | Text color (#RRGGBB) |
| `font_bold` | Bold text (true/false) |
| `font_italic` | Italic text (true/false) |
| `visible` | Element visibility (true/false) |
| `enabled` | Element enabled state (true/false) |

---

## 5. Alignment

```yaml
# Horizontal alignment
horizontal_align: Right    # Left, Center, Right

# Vertical alignment
vertical_align: Center     # Top, Center, Bottom

# Label position
title_location: Left       # Left, Top, Right, None
```

**Common patterns:**
```yaml
# Numbers - right align
- type: InputField
  name: СуммаПоле
  attribute: Сумма
  horizontal_align: Right

# Centered header
- type: LabelDecoration
  name: Заголовок
  title_ru: "CENTER"
  horizontal_align: Center

# Table column - right for numbers
columns:
  - name: Сумма
    attribute: Сумма
    horizontal_align: Right
```

---

## 6. Sizing

### Width/Height
```yaml
# InputField
- type: InputField
  name: Поле
  attribute: Attr
  width: 30                 # Characters
  height: 5                 # Lines (multiline only)
  multiline: true

# Table columns
columns:
  - name: Код
    attribute: Код
    width: 8                # Short field
  - name: Наименование
    attribute: Наименование
    width: 30               # Standard field
  - name: Описание
    attribute: Описание
    width: 50               # Wide field
```

### Table Height Properties (v2.68.0+)
```yaml
- type: Table
  name: Таблица
  tabular_section: Данные
  height: 20                    # Overall form height
  height_in_table_rows: 8       # Number of visible data rows
  header_height: 3              # Column headers height
  title_height: 2               # Table title height
  footer_height: 2              # Footer area height
  horizontal_stretch: true
```

| Property | Description |
|----------|-------------|
| `height` | Overall table height in form units |
| `height_in_table_rows` | Number of visible data rows |
| `header_height` | Height of column header row |
| `title_height` | Height of table title |
| `footer_height` | Height of footer area |

### InputField in Table columns (v2.68.0+)
```yaml
elements:
  - type: InputField
    name: КолонкаТовар
    attribute: Товар
    width: 20
    height: 3                   # Cell height
    title_height: 2             # Column header height
    back_color: "#F5F5F5"
    font:
      size: 14
    title_font:
      size: 12
      bold: true
    footer_font:                # Footer font
      size: 10
      italic: true
```

### Stretch properties
```yaml
horizontal_stretch: true    # Fill available width
vertical_stretch: true      # Fill available height
auto_max_width: true        # Auto-adjust width
```

**Typical sizes:**
| Field type | Width |
|------------|-------|
| Code, ID | 8-12 |
| Name, standard | 20-30 |
| Description, wide | 40-50 |
| Buttons | 12-20 |

---

## 7. Group Styling

### Representation (separation style)
```yaml
- type: UsualGroup
  name: Фильтры
  title_ru: "Filters"
  show_title: true
  representation: NormalSeparation   # None, WeakSeparation, NormalSeparation, StrongSeparation
  group_direction: Horizontal
```

| Value | Visual |
|-------|--------|
| `None` | No border |
| `WeakSeparation` | Light line |
| `NormalSeparation` | Standard frame |
| `StrongSeparation` | Bold frame |

### Collapsible groups
```yaml
- type: UsualGroup
  name: ДополнительноГруппа
  title_ru: "Advanced"
  behavior: Collapsible              # Usual or Collapsible
  collapsed: true                    # Initial state
```

### Nested groups
```yaml
- type: UsualGroup
  name: ВнешняяГруппа
  group_direction: Vertical
  child_items:
    - type: InputField
      attribute: Поле1

    # Nested group
    - type: UsualGroup
      name: КнопкиГруппа
      group_direction: Horizontal
      child_items:
        - type: Button
          command: Команда1
        - type: Button
          command: Команда2
```

---

## 8. Table Styling

### Column groups (multi-level headers)
```yaml
- type: Table
  name: ФинансыТаблица
  tabular_section: Данные
  columns:
    - name: Дата
      attribute: Дата
      width: 12

    # Grouped columns
    - type: ColumnGroup
      name: ПланГруппа
      title_ru: "PLAN"
      horizontal_align: Center
      elements:
        - name: ПланКоличество
          attribute: ПланКоличество
          width: 10
          horizontal_align: Right
        - name: ПланСумма
          attribute: ПланСумма
          width: 12
          horizontal_align: Right

    - type: ColumnGroup
      name: ФактГруппа
      title_ru: "FACT"
      elements:
        - name: ФактКоличество
          attribute: ФактКоличество
          horizontal_align: Right
        - name: ФактСумма
          attribute: ФактСумма
          horizontal_align: Right
```

### Tree representation (v2.64.0+)
```yaml
- type: Table
  name: ДеревоТаблица
  tabular_section: Дерево
  representation: tree               # list or tree
  initial_tree_view: expand_top_level  # no_expand, expand_top_level, expand_all_levels
  show_root: false
```

---

## 9. Pages/Tabs Styling

```yaml
- type: Pages
  name: СтраницыОсновные
  pages_representation: TabsOnTop    # TabsOnTop, TabsOnBottom, None

  pages:
    - name: СтраницаДанные
      title_ru: "Data"
      picture: StdPicture.Information  # Tab icon
      child_items:
        - type: InputField
          attribute: Поле1

    - name: СтраницаНастройки
      title_ru: "Settings"
      picture: StdPicture.CustomizeForm
      child_items:
        - type: InputField
          attribute: Настройка1
```

---

## Style Checklist

- [ ] Colors in HEX format (`#RRGGBB`)
- [ ] Font uses `size` (auto: sys:DefaultGUIFont) or `ref` (style:*)
- [ ] `formatted: true` for HTML in LabelDecoration
- [ ] `horizontal_align: Right` for numeric columns
- [ ] ConditionalAppearance at form level (not in elements!)
- [ ] Filter `field` uses correct data path format
- [ ] Filter `value_type` matches actual value (boolean/string/number)
- [ ] `selection` element names match actual element names
- [ ] Table `height_in_table_rows` for precise row count control
- [ ] Width values are reasonable (8-50 characters)

---

*Version: 2.68.0 | Companion to: LLM_WEB_LITE.md, knowledge_base.md*
