# English Language Support Demo

**Version:** 2.13.0
**Last updated:** 2025-11-13

This example demonstrates trilingual (Russian/Ukrainian/English) support in 1C Processor Generator.

## Features Demonstrated

### 1. **Processor synonym in 3 languages**
```yaml
processor:
  name: ТестАнглійськоїМови
  synonym:
    ru: Тест английского языка
    uk: Тест англійської мови
    en: English Language Test  # NEW in v2.13.0
```

### 2. **Attribute synonyms**
```yaml
attributes:
  - name: Товар
    type: string
    synonym:
      ru: Товар
      uk: Товар
      en: Product  # English synonym
```

### 3. **Form element titles and input hints**
```yaml
elements:
  - type: InputField
    name: Товар
    title:
      ru: Товар
      uk: Товар
      en: Product  # English title
    input_hint:
      ru: Введите название товара
      uk: Введіть назву товару
      en: Enter product name  # English input hint
```

### 4. **Command titles and tooltips**
```yaml
commands:
  - name: Розрахувати
    title:
      ru: Рассчитать
      uk: Розрахувати
      en: Calculate  # English command title
    tooltip:
      ru: Рассчитать общую сумму
      uk: Розрахувати загальну суму
      en: Calculate total amount  # English tooltip
```

## Generated Output

When you generate this processor, it will create:

### XML Mode:
- `ТестАнглійськоїМови.xml` - with trilingual synonyms in all `<Synonym>` blocks
- `Форма.xml` - with trilingual titles, input hints, and tooltips

### EPF Mode with Configuration:
- `Languages/Русский.xml` - Russian language metadata
- `Languages/English.xml` - English language metadata (**NEW in v2.13.0**)

## Key Features (v2.13.0)

- ✅ **Backward compatible** - `*_en` fields are optional
- ✅ **Auto-defaults** - If `en` not specified, defaults to name (like `ru`/`uk`)
- ✅ **Consistent behavior** - English follows same pattern as Russian/Ukrainian
- ✅ **DEFAULT_LANGUAGE = "ru"** - Russian is now default (changed from "uk")

## How to Generate

### XML format:
```bash
python -m 1c_processor_generator yaml \\
  --config examples/yaml/english_language_demo/config.yaml \\
  --handlers-file examples/yaml/english_language_demo/handlers.bsl \\
  --output output/english_demo
```

### EPF format (with Configuration + Languages/English.xml):
```bash
python -m 1c_processor_generator yaml \\
  --config examples/yaml/english_language_demo/config.yaml \\
  --handlers-file examples/yaml/english_language_demo/handlers.bsl \\
  --output output/english_demo \\
  --output-format epf
```

## What This Example Does

This processor calculates total amount (Quantity × Price) and outputs results in both Ukrainian and English:

```
Товар / Product: Laptop
Кількість / Quantity: 5
Ціна / Price: 1000.00
Загальна сума / Total amount: 5000.00
```

## Verification

Open generated XML and check that `<Synonym>` blocks contain 3 languages:

```xml
<Synonym>
    <v8:item>
        <v8:lang>ru</v8:lang>
        <v8:content>Товар</v8:content>
    </v8:item>
    <v8:item>
        <v8:lang>uk</v8:lang>
        <v8:content>Товар</v8:content>
    </v8:item>
    <v8:item>
        <v8:lang>en</v8:lang>
        <v8:content>Product</v8:content>
    </v8:item>
</Synonym>
```

## See Also

- **YAML_GUIDE.md** - Complete reference for `*_en` fields
- **CHANGELOG.md** - Version 2.13.0 release notes
- **constants.py** - LANGUAGES list now includes "en"
