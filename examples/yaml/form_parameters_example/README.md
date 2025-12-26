# Form Parameters Example (v2.36.0+)

This example demonstrates **Form Parameters** - passing data when opening forms in 1C:Enterprise.

## What are Form Parameters?

Form parameters allow you to pass data **from outside** when opening a form:
- Filter settings (date range, category, etc.)
- Context information (selected document, mode)
- Wizard step data (multi-step processes)

**Key difference from FormAttributes:**
- **FormParameter**: Passed FROM outside TO form (input)
- **FormAttribute**: Exists INSIDE form (internal state)

## Features Demonstrated

### 1. Key Parameter
```yaml
parameters:
  - name: FilterDate
    type: date
    key_parameter: true  # ✅ Marked as key parameter
```

**KeyParameter** in 1C XML marks the parameter as essential for form identification.

### 2. Multiple Parameter Types
```yaml
parameters:
  - name: FilterDate
    type: date            # Date parameter
  - name: ViewMode
    type: boolean         # Boolean parameter
  - name: DefaultRegion
    type: string          # String parameter
```

Supported types: `string`, `number`, `boolean`, `date`, `CatalogRef.*`, `DocumentRef.*`

### 3. Multi-language Support
```yaml
parameters:
  - name: FilterDate
    synonym_ru: Дата фильтра
    synonym_uk: Дата фільтру
    synonym_en: Filter Date
```

## Usage Workflow

### Step 1: Define Parameters in Form
```yaml
forms:
  - name: ФормаФильтра
    parameters:
      - name: FilterDate
        type: date
        key_parameter: true
```

### Step 2: Open Form with Parameters (BSL)
```bsl
ПараметрыФормы = Новый Структура;
ПараметрыФормы.Вставить("FilterDate", ТекущаяДата());
ПараметрыФормы.Вставить("ViewMode", Истина);

ОткрытьФорму(
    "ВнешняяОбработка.ПроцессорИмя.Форма.ФормаФильтра",
    ПараметрыФормы,  // ← Parameters structure
    ЭтаФорма
);
```

### Step 3: Receive Parameters in Form (BSL)
```bsl
&НаКлиенте
Процедура FilterFormOnOpen(Отказ)
    // Parameters automatically available as form attributes
    Сообщить("Date: " + FilterDate);
    Сообщить("Mode: " + ViewMode);
КонецПроцедуры
```

**No manual mapping needed!** 1C automatically maps parameters to form attributes.

## Testing the Example

### Generate XML
```bash
python -m 1c_processor_generator yaml \
  --config examples/yaml/form_parameters_example/config.yaml \
  --handlers-file examples/yaml/form_parameters_example/handlers.bsl \
  --output tmp/form_parameters_example
```

### Generate EPF (if Designer available)
```bash
python -m 1c_processor_generator yaml \
  --config examples/yaml/form_parameters_example/config.yaml \
  --handlers-file examples/yaml/form_parameters_example/handlers.bsl \
  --output tmp/form_parameters_example \
  --output-format epf
```

### Run in 1C
1. Open generated EPF in 1C:Enterprise
2. Click "Открыть фильтр" button
3. Filter form opens with pre-filled values (from parameters)
4. Modify values and click "Применить"
5. Main form displays selected values

## Generated XML Structure

### Form Metadata (Форма.xml)
```xml
<Parameters>
    <Parameter name="FilterDate" uuid="...">
        <Title>
            <v8:item><v8:lang>ru</v8:lang><v8:content>Дата фильтра</v8:content></v8:item>
        </Title>
        <Type>
            <v8:Type>xs:dateTime</v8:Type>
            <v8:DateQualifiers>
                <v8:DateFractions>DateTime</v8:DateFractions>
            </v8:DateQualifiers>
        </Type>
        <KeyParameter>true</KeyParameter>
    </Parameter>
    <!-- More parameters... -->
</Parameters>
```

## Real-World Use Cases

### 1. Filter Forms
Pass filter criteria:
- Date range (StartDate, EndDate)
- Category selection
- User/department filter

### 2. Wizard Flows
Multi-step processes:
- Step 1 → collect basic info → pass to Step 2
- Step 2 → receive Step1 data → collect additional info
- Step 3 → receive all data → finalize

### 3. Document Editing
Pass document context:
- DocumentRef (which document to edit)
- EditMode (view/edit)
- Template (which template to use)

### 4. Report Configuration
Pass report settings:
- ReportDate
- Grouping options
- Detail level

## Common Patterns

### Pattern 1: Filter + Apply
```yaml
# Main form opens filter
commands:
  - name: OpenFilter
    handler: OpenFilter

# Filter form has parameters
forms:
  - name: FilterForm
    parameters:
      - name: FilterDate
        type: date
```

### Pattern 2: Wizard Steps
```yaml
# Step 1 → Step 2 with data
forms:
  - name: Step1
    # Collect data, pass to Step 2

  - name: Step 2
    parameters:
      - name: Step1Data
        type: string  # JSON or serialized data
```

### Pattern 3: Master-Detail Editing
```yaml
# Open detail form with master ID
forms:
  - name: DetailForm
    parameters:
      - name: MasterID
        type: string
        key_parameter: true
```

## Troubleshooting

### Issue: Parameters not received
**Symptom:** Form opens but parameters are Undefined

**Solution:** Check parameter names match exactly:
```yaml
parameters:
  - name: FilterDate  # ← Must match BSL structure key
```
```bsl
ПараметрыФормы.Вставить("FilterDate", ...);  // ← Exact match
```

### Issue: Type mismatch
**Symptom:** Runtime error when opening form

**Solution:** Ensure BSL value type matches YAML parameter type:
```yaml
type: date  # ← Expects Date type
```
```bsl
ПараметрыФормы.Вставить("FilterDate", ТекущаяДата());  // ← Date value
```

## Version Info

- **Added in:** v2.36.0 (Phase 2)
- **Frequency:** 128 forms (30% of real-world processors)
- **Complexity:** MEDIUM
- **Priority:** P0 (CRITICAL - blocks multi-form patterns)

## See Also

- **FormAttribute** - For form-internal attributes (SpreadsheetDocument, BinaryData)
- **Multi-form processors** - Using multiple forms in one processor
- **Wizard patterns** - Multi-step workflows with form parameters
