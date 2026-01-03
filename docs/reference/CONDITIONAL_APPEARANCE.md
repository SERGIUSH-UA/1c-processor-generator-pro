# Conditional Appearance Reference (v2.68.0+)

LLM reference for conditional styling of table rows and form elements in 1C forms.

## Overview

ConditionalAppearance allows you to dynamically change the appearance of form elements based on data values. Common use cases:
- Highlight error rows in red
- Color-code status fields (green=success, yellow=warning, red=error)
- Show/hide elements based on conditions
- Bold or italic text for important values

**CRITICAL:** ConditionalAppearance is defined at **form level**, not element level. This is a 1C platform requirement.

## Basic Structure

```yaml
forms:
  - name: FormName

    # ConditionalAppearance - MUST be at form level!
    conditional_appearances:
      - name: RuleName
        selection: [ElementName1, ElementName2]   # Target elements
        filter:                                    # Condition
          field: DataPath.FieldName
          comparison: Equal
          value: true
          value_type: boolean
        appearance:                                # Styling to apply
          back_color: "#FF0000"
          text_color: "#FFFFFF"

    elements:
      # ... form elements ...
```

## Selection

Specifies which form elements the appearance applies to.

```yaml
selection: [TableColumn1, TableColumn2]   # Multiple elements
selection: [InputFieldName]               # Single element
```

**Element names must match** the `name` property of form elements.

## Filter

Defines the condition for when the appearance applies.

### Filter Properties

| Property | Required | Description |
|----------|----------|-------------|
| `field` | Yes | Data path to the field being evaluated |
| `comparison` | Yes | Comparison operator |
| `value` | Yes | Value to compare against |
| `value_type` | Yes | Type of the value |

### Data Path Format

For tabular section columns:
```yaml
field: Объект.TableName.ColumnName    # TabularSection
field: TableName.ColumnName           # ValueTable
```

For form attributes:
```yaml
field: AttributeName
```

### Comparison Operators

| Comparison | Description |
|------------|-------------|
| `Equal` | Field equals value |
| `NotEqual` | Field not equals value |

### Value Types

| value_type | YAML Value | Description |
|------------|------------|-------------|
| `boolean` | `true` / `false` | Boolean comparison |
| `string` | `"text"` | String comparison |
| `number` | `123` | Numeric comparison |

## Appearance

Specifies the styling to apply when the condition is met.

### Appearance Properties

| Property | XML Element | Example | Description |
|----------|-------------|---------|-------------|
| `back_color` | `BackColor` | `"#FF0000"` | Background color (hex) |
| `text_color` | `TextColor` | `"#FFFFFF"` | Text color (hex) |
| `font_bold` | Font bold | `true` | Bold text |
| `font_italic` | Font italic | `true` | Italic text |
| `visible` | `Visible` | `false` | Element visibility |
| `enabled` | `Enabled` | `false` | Element enabled state |

### Color Format

Use hex colors with `#` prefix:
```yaml
back_color: "#FF0000"    # Red
back_color: "#00FF00"    # Green
back_color: "#0000FF"    # Blue
back_color: "#F5F5DC"    # Beige
back_color: "#8B4513"    # SaddleBrown
```

## Complete Example: Chess Board

```yaml
processor:
  name: ChessBoard

tabular_sections:
  - name: Board
    columns:
      - name: Col1
        type: string
      - name: Col1White      # Boolean flag for cell color
        type: boolean
      # ... repeat for Col2-Col8 ...

forms:
  - name: Form

    # ConditionalAppearance for each column
    conditional_appearances:
      # Column 1 - White cells
      - name: Col1White
        selection: [BoardCol1]
        filter:
          field: Объект.Board.Col1White
          comparison: Equal
          value: true
          value_type: boolean
        appearance:
          back_color: "#F5F5DC"      # Beige (white cell)

      # Column 1 - Black cells
      - name: Col1Black
        selection: [BoardCol1]
        filter:
          field: Объект.Board.Col1White
          comparison: Equal
          value: false
          value_type: boolean
        appearance:
          back_color: "#8B4513"      # SaddleBrown (black cell)
          text_color: "#FFFFFF"      # White text on dark background

      # ... repeat pattern for Col2-Col8 ...

    elements:
      - type: Table
        name: Board
        tabular_section: Board
        elements:
          - type: InputField
            name: BoardCol1          # Must match selection!
            attribute: Col1
            width: 6
```

## Status Highlighting Example

```yaml
conditional_appearances:
  # Success status - green
  - name: StatusSuccess
    selection: [StatusField, AmountField]
    filter:
      field: Status
      comparison: Equal
      value: "Success"
      value_type: string
    appearance:
      back_color: "#90EE90"          # LightGreen

  # Warning status - yellow
  - name: StatusWarning
    selection: [StatusField, AmountField]
    filter:
      field: Status
      comparison: Equal
      value: "Warning"
      value_type: string
    appearance:
      back_color: "#FFD700"          # Gold

  # Error status - red
  - name: StatusError
    selection: [StatusField, AmountField]
    filter:
      field: Status
      comparison: Equal
      value: "Error"
      value_type: string
    appearance:
      back_color: "#FF6347"          # Tomato
      text_color: "#FFFFFF"
      font_bold: true
```

## Error Row Highlighting

```yaml
conditional_appearances:
  - name: ErrorRows
    selection: [ErrorMessage, LineNumber, DataColumn]
    filter:
      field: Объект.ValidationResults.HasError
      comparison: Equal
      value: true
      value_type: boolean
    appearance:
      back_color: "#FFCCCC"          # Light red
      font_bold: true
```

## Common Patterns

### Boolean Flag Pattern

Add a boolean column to control styling:

```yaml
tabular_sections:
  - name: Items
    columns:
      - name: Name
        type: string
      - name: IsHighlighted        # Control column
        type: boolean

conditional_appearances:
  - name: Highlighted
    selection: [ItemName]
    filter:
      field: Объект.Items.IsHighlighted
      comparison: Equal
      value: true
      value_type: boolean
    appearance:
      back_color: "#FFFACD"
      font_bold: true
```

### Alternating Rows Pattern

Use row number modulo:

```yaml
# In BSL handler, set IsEvenRow = (LineNumber % 2 = 0)

conditional_appearances:
  - name: EvenRows
    selection: [Col1, Col2, Col3]
    filter:
      field: Объект.Data.IsEvenRow
      comparison: Equal
      value: true
      value_type: boolean
    appearance:
      back_color: "#F0F0F0"
```

## Important Notes

1. **Form level only** - ConditionalAppearance must be defined at form level, not inside elements
2. **Selection names must match** - Element names in `selection` must exactly match form element names
3. **Data path format** - Use `Объект.TableName.Column` for TabularSection, `TableName.Column` for ValueTable
4. **Multiple rules** - Multiple rules can target the same element; all matching rules apply
5. **Order matters** - Later rules override earlier ones for the same properties

## Generated XML Structure

```xml
<Form>
  <Attributes>
    <!-- ConditionalAppearance is generated inside Attributes section -->
    <ConditionalAppearance>
      <Item>
        <Appearance>
          <Item>
            <Values>
              <Item xsi:type="dcscor:DataCompositionConditionalAppearanceColorValue">
                <Use>true</Use>
                <Value>#FF0000</Value>
              </Item>
            </Values>
            <Parameter>BackColor</Parameter>
            <Use>true</Use>
          </Item>
        </Appearance>
        <Selection>
          <Item>ElementName</Item>
        </Selection>
        <Filter>
          <Item>
            <LeftValue>DataPath</LeftValue>
            <ComparisonType>Equal</ComparisonType>
            <RightValue xsi:type="xs:boolean">true</RightValue>
            <Use>true</Use>
          </Item>
        </Filter>
      </Item>
    </ConditionalAppearance>
  </Attributes>
</Form>
```

## See Also

- [TABLE_STYLING.md](TABLE_STYLING.md) - Table heights and font styling
- [API_REFERENCE.md](API_REFERENCE.md) - Complete YAML API
- [ALL_PATTERNS.md](ALL_PATTERNS.md) - Common UI patterns
