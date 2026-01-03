# Table Styling Reference (v2.68.0+)

LLM reference for styling Tables and their columns in 1C forms.

## Table Height Properties

Control how many rows are visible and the heights of different table sections.

```yaml
- type: Table
  name: DataTable
  tabular_section: Data
  height: 20                    # Overall form height
  height_in_table_rows: 8       # Number of visible data rows
  header_height: 3              # Column headers height
  title_height: 2               # Table title height (if shown)
  footer_height: 2              # Footer area height
  horizontal_stretch: true
```

### Properties Reference

| YAML Property | XML Element | Description |
|---------------|-------------|-------------|
| `height` | `<Height>` | Overall table height in form units |
| `height_in_table_rows` | `<HeightInTableRows>` | Number of visible data rows |
| `header_height` | `<HeaderHeight>` | Height of column header row |
| `title_height` | `<TitleHeight>` | Height of table title |
| `footer_height` | `<FooterHeight>` | Height of footer area |

**Note:** When `height_in_table_rows` is specified, `<HeightControlVariant>UseHeightInFormRows</HeightControlVariant>` is auto-generated.

## Font Styling

### Font Size

Use `size` to set font point size:

```yaml
font:
  size: 20          # Font size in points (generates height="20")
  bold: true        # Bold text
  italic: false     # Italic text
```

**Generated XML:**
```xml
<Font ref="sys:DefaultGUIFont" height="20" bold="true" kind="WindowsFont"/>
```

### Font Family

Use `face_name` to specify font family:

```yaml
font:
  size: 16
  face_name: Arial    # Font family (generates faceName="Arial")
  bold: true
```

**Generated XML:**
```xml
<Font ref="sys:DefaultGUIFont" faceName="Arial" height="16" bold="true" kind="WindowsFont"/>
```

### Font Properties Reference

| YAML Property | XML Attribute | Description |
|---------------|---------------|-------------|
| `size` | `height` | Font size in points |
| `face_name` | `faceName` | Font family name |
| `bold` | `bold` | Bold weight |
| `italic` | `italic` | Italic style |
| `underline` | `underline` | Underline decoration |
| `strikethrough` | `strikeout` | Strikethrough decoration |
| `scale` | `scale` | Font scale percentage |

**Auto-detection:** When `size` is specified, the font automatically uses:
- `ref="sys:DefaultGUIFont"` (system font)
- `kind="WindowsFont"` (font type)

Without size (style-only fonts):
- `ref="style:NormalTextFont"` (style reference)
- `kind="StyleItem"` (style type)

## InputField Column Styling

InputField elements inside Tables support additional styling properties.

### Full Example

```yaml
- type: Table
  name: Board
  tabular_section: Board
  height: 20
  height_in_table_rows: 8
  header_height: 3
  elements:
    - type: InputField
      name: Col1
      attribute: Col1
      width: 6
      height: 3                 # Column cell height
      title_height: 2           # Column header height
      back_color: "#F5F5DC"     # Cell background color
      border_color: "#8B4513"   # Cell border color
      text_color: "#333333"     # Text color
      font:                     # Cell text font
        size: 20
        bold: true
      title_font:               # Column header font
        size: 14
        face_name: Arial
        bold: true
      footer_font:              # Footer font
        size: 12
        italic: true
```

### InputField Properties Reference

| YAML Property | XML Element | Description |
|---------------|-------------|-------------|
| `width` | `<Width>` | Column width |
| `height` | `<Height>` | Cell height |
| `title_height` | `<TitleHeight>` | Column header height |
| `back_color` | `<BackColor>` | Cell background (#RRGGBB) |
| `border_color` | `<BorderColor>` | Cell border (#RRGGBB) |
| `text_color` | `<TextColor>` | Text color (#RRGGBB) |
| `title_text_color` | `<TitleTextColor>` | Header text color |
| `font` | `<Font>` | Cell text font |
| `title_font` | `<TitleFont>` | Column header font |
| `footer_font` | `<FooterFont>` | Footer font |

## Complete Chess Board Example

```yaml
# Chess board with 8 uniform columns and large font
- type: Table
  name: Board
  tabular_section: Board
  height: 20
  height_in_table_rows: 8       # 8 rows for chess
  header_height: 3              # Tall headers for A-H labels
  horizontal_stretch: false
  elements:
    - type: InputField
      name: BoardRowNum
      attribute: RowNum
      width: 4
      height: 3
      read_only: true
      title: {ru: "#", uk: "#"}
      font:
        size: 18
        bold: true
    - type: InputField
      name: BoardCol1
      attribute: Col1
      width: 6
      height: 3
      title: {ru: "A", uk: "A"}
      font:
        size: 20
        bold: true
    # ... repeat for Col2-Col8 ...
```

## See Also

- [CONDITIONAL_APPEARANCE.md](CONDITIONAL_APPEARANCE.md) - Row coloring based on conditions
- [API_REFERENCE.md](API_REFERENCE.md) - Complete YAML API
- [ALL_PATTERNS.md](ALL_PATTERNS.md) - Common UI patterns
