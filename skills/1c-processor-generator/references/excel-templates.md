# LLM Guide: Excel Templates for 1C Print Forms

> **For AI/LLM agents creating Excel templates that auto-convert to MXL format**

## Quick Start

Excel files (`.xlsx`) are auto-converted to 1C MXL format when specified in `templates:` section:

```yaml
templates:
  - name: ПФ_MXL_Invoice
    type: SpreadsheetDocument
    file: templates/invoice.xlsx  # Auto-converted!
```

**Requirements:** `pip install openpyxl>=3.1.0`

---

## Excel Conventions

### Named Ranges (Critical!)

Named Ranges in Excel become named areas (`namedItem`) in MXL. BSP print forms use these areas for repeating sections.

| Excel Named Range | MXL Area | Purpose |
|-------------------|----------|---------|
| `Header` / `Заголовок` / `Шапка` | `Заголовок` | Document header (company, title) |
| `TableHeader` / `ШапкаТаблицы` | `ШапкаТаблицы` | Table column headers |
| `Row` / `Строка` / `СтрокаТаблицы` | `СтрокаТаблицы` | Repeating data row |
| `Footer` / `Подвал` / `Итого` | `Подвал` | Totals, signatures |

**How to create Named Range in Excel:**
1. Select cells (e.g., A1:C3)
2. Formulas → Define Name
3. Enter name: `Header` or `Заголовок`

### Parameters

Use `{ParameterName}` syntax in cells. They become MXL parameters filled at runtime:

| Cell Content | MXL Parameter | BSL Access |
|--------------|---------------|------------|
| `{НомерДокумента}` | `<parameter>НомерДокумента</parameter>` | `Область.Параметры.НомерДокумента` |
| `{Дата}` | `<parameter>Дата</parameter>` | `Область.Параметры.Дата` |
| `{Контрагент}` | `<parameter>Контрагент</parameter>` | `Область.Параметры.Контрагент` |
| `{Сумма}` | `<parameter>Сумма</parameter>` | `Область.Параметры.Сумма` |

**Rules:**
- Parameter name: Cyrillic/Latin letters, digits, underscore
- Pattern: `{[А-Яа-яA-Za-z_][А-Яа-яA-Za-z0-9_]*}`
- Cell with ONLY `{Name}` becomes a "fill cell" (for data)

### Supported Formatting

| Feature | Excel | MXL | Notes |
|---------|-------|-----|-------|
| Font name | ✅ | ✅ | Arial, Times New Roman, etc. |
| Font size | ✅ | ✅ | Points |
| Bold | ✅ | ✅ | |
| Italic | ✅ | ✅ | |
| Alignment (H) | ✅ | ✅ | Left, Center, Right |
| Alignment (V) | ✅ | ✅ | Top, Center, Bottom |
| Borders | ✅ | ✅ | Left, Right, Top, Bottom |
| Column width | ✅ | ✅ | Converted to 1C units |
| Row height | ✅ | ✅ | Non-default heights |
| Merged cells | ✅ | ✅ | |
| Text wrap | ✅ | ✅ | |

**Not yet supported:**
- Background colors
- Font colors
- Images/logos
- Number formats (coming soon)

---

## Complete Example

### Invoice Print Form

**Excel structure (`templates/invoice.xlsx`):**

```
Row 1-3: Named Range "Заголовок"
  A1: "РАХУНОК-ФАКТУРА"  (merged A1:D1, bold, 16pt, center)
  A2: "№ {НомерДокумента} від {Дата}"  (merged A2:D2, center)
  A3: "Покупець: {Контрагент}"  (merged A3:D3)

Row 4: Named Range "ШапкаТаблицы"
  A4: "№"  (bold, border)
  B4: "Товар"  (bold, border)
  C4: "Кількість"  (bold, border)
  D4: "Сума"  (bold, border)

Row 5: Named Range "СтрокаТаблицы"
  A5: "{НомерРядка}"  (border)
  B5: "{Номенклатура}"  (border)
  C5: "{Кількість}"  (border, right align)
  D5: "{Сумма}"  (border, right align)

Row 6: Named Range "Подвал"
  C6: "РАЗОМ:"  (bold, right align)
  D6: "{ІтогоСумма}"  (bold, border)
```

**config.yaml:**
```yaml
languages: [ru, uk]

processor:
  name: ПечатьРахунку

bsp:
  type: print_form
  version: "1.0"
  targets:
    - Документ.РеализацияТоваровУслуг
  commands:
    - id: Рахунок
      title: "Рахунок-фактура | Рахунок-фактура"
      usage: server_method
      modifier: ПечатьMXL

templates:
  - name: ПФ_MXL_Рахунок
    type: SpreadsheetDocument
    file: templates/invoice.xlsx
```

**handlers.bsl:**
```bsl
// ПечатьРахунок
// Параметри: МассивОбъектов, ТабличныйДокумент

Макет = ПолучитьМакет("ПФ_MXL_Рахунок");
ОбластьЗаголовок = Макет.ПолучитьОбласть("Заголовок");
ОбластьШапкаТаблицы = Макет.ПолучитьОбласть("ШапкаТаблицы");
ОбластьСтрока = Макет.ПолучитьОбласть("СтрокаТаблицы");
ОбластьПодвал = Макет.ПолучитьОбласть("Подвал");

Для Каждого Ссылка Из МассивОбъектов Цикл

    // Розділювач сторінок
    Если ТабличныйДокумент.ВысотаТаблицы > 0 Тогда
        ТабличныйДокумент.ВывестиГоризонтальныйРазделительСтраниц();
    КонецЕсли;

    // Заголовок
    ОбластьЗаголовок.Параметры.НомерДокумента = Ссылка.Номер;
    ОбластьЗаголовок.Параметры.Дата = Формат(Ссылка.Дата, "ДЛФ=D");
    ОбластьЗаголовок.Параметры.Контрагент = Ссылка.Контрагент;
    ТабличныйДокумент.Вывести(ОбластьЗаголовок);

    // Шапка таблиці
    ТабличныйДокумент.Вывести(ОбластьШапкаТаблицы);

    // Рядки товарів
    НомерРядка = 0;
    ІтогоСумма = 0;
    Для Каждого СтрокаТовара Із Ссылка.Товары Цикл
        НомерРядка = НомерРядка + 1;
        ОбластьСтрока.Параметры.НомерРядка = НомерРядка;
        ОбластьСтрока.Параметры.Номенклатура = СтрокаТовара.Номенклатура;
        ОбластьСтрока.Параметры.Кількість = СтрокаТовара.Количество;
        ОбластьСтрока.Параметры.Сумма = СтрокаТовара.Сумма;
        ІтогоСумма = ІтогоСумма + СтрокаТовара.Сумма;
        ТабличныйДокумент.Вывести(ОбластьСтрока);
    КонецЦикла;

    // Підсумок
    ОбластьПодвал.Параметры.ІтогоСумма = ІтогоСумма;
    ТабличныйДокумент.Вывести(ОбластьПодвал);

КонецЦикла;

ТабличныйДокумент.АвтоМасштаб = Истина;
```

---

## CLI Conversion

You can also convert Excel to MXL manually:

```bash
# Basic conversion
python -m 1c_processor_generator excel2mxl template.xlsx

# With options
python -m 1c_processor_generator excel2mxl template.xlsx -o output.mxl -l ru uk

# Specific sheet
python -m 1c_processor_generator excel2mxl template.xlsx -s "Рахунок"
```

**CLI Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output MXL file path | `input.mxl` |
| `-s, --sheet` | Excel sheet name | Active sheet |
| `-l, --languages` | Languages for localization | `ru uk` |

---

## Tips for LLMs

### Creating Excel via Python (openpyxl)

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side

wb = Workbook()
ws = wb.active

# Header area
ws.merge_cells('A1:D1')
ws['A1'] = "РАХУНОК-ФАКТУРА"
ws['A1'].font = Font(bold=True, size=16)
ws['A1'].alignment = Alignment(horizontal='center')

ws.merge_cells('A2:D2')
ws['A2'] = "№ {НомерДокумента} від {Дата}"
ws['A2'].alignment = Alignment(horizontal='center')

ws.merge_cells('A3:D3')
ws['A3'] = "Покупець: {Контрагент}"

# Create Named Range for header
from openpyxl.workbook.defined_name import DefinedName
ws.parent.defined_names.add(DefinedName("Заголовок", attr_text="Sheet!$A$1:$D$3"))

# Table header
thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

headers = ["№", "Товар", "Кількість", "Сума"]
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=4, column=col, value=header)
    cell.font = Font(bold=True)
    cell.border = thin_border

ws.parent.defined_names.add(DefinedName("ШапкаТаблицы", attr_text="Sheet!$A$4:$D$4"))

# Data row template
params = ["{НомерРядка}", "{Номенклатура}", "{Кількість}", "{Сумма}"]
for col, param in enumerate(params, 1):
    cell = ws.cell(row=5, column=col, value=param)
    cell.border = thin_border

ws.parent.defined_names.add(DefinedName("СтрокаТаблицы", attr_text="Sheet!$A$5:$D$5"))

# Save
wb.save("templates/invoice.xlsx")
```

### Best Practices

1. **Use meaningful parameter names** - `{НомерДокумента}` not `{N}`
2. **Keep named ranges simple** - one continuous rectangular area
3. **Test with CLI first** - `python -m 1c_processor_generator excel2mxl test.xlsx`
4. **Check generated MXL** - open in 1C Designer to verify

---

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `openpyxl not found` | Missing dependency | `pip install openpyxl>=3.1.0` |
| `Named range not found` | Wrong range name | Use standard names: `Заголовок`, `СтрокаТаблицы` |
| `Parameter not filled` | Typo in parameter name | Check exact match with BSL code |
| `Empty output` | No data in selected sheet | Specify sheet with `-s` option |

---

## See Also

- [LLM_BSP_PRINT_FORMS.md](LLM_BSP_PRINT_FORMS.md) - BSP Print Forms guide
- [LLM_CORE.md](LLM_CORE.md) - Core LLM instructions
- [examples/yaml/bsp_print_form_excel/](../examples/yaml/bsp_print_form_excel/) - Working example
