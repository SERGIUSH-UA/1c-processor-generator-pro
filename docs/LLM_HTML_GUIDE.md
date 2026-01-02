# HTML Projects in 1C - LLM Guide

**Version:** 2.42.0+
**Purpose:** Complete guide for LLMs to create HTML/CSS/JS interfaces in 1C:Enterprise processors

---

## Quick Start

### Minimum Required Files

```
my_html_project/
├── config.yaml              # Main configuration
├── handlers.bsl             # BSL handlers
└── templates/
    ├── dashboard.html       # HTML template
    ├── dashboard.automation.yaml  # Placeholders + assets (optional)
    ├── styles.css           # CSS styles (optional)
    └── scripts.js           # JavaScript (optional)
```

### Minimal config.yaml (v2.42.0+ recommended approach)

```yaml
processor:
  name: HTMLDashboard
  synonym_ru: HTML Дашборд

templates:
  - name: Dashboard
    type: HTMLDocument
    file: templates/dashboard.html
    # NO auto_field - use template: on HTMLDocumentField instead
    automation: templates/dashboard.automation.yaml  # Optional: placeholders + assets

forms:
  - name: Форма
    default: true
    elements:
      # Position HTML field exactly where you want it
      - type: HTMLDocumentField
        name: DashboardField
        template: Dashboard    # Links to template, auto-creates DashboardHTML attribute
        stretch: HorizontalAndVertically
    events:
      OnCreateAtServer: ПриСозданииНаСервере  # Load HTML on form open
```

### Minimal handlers.bsl

```bsl
&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
    // Auto-generated helper function loads HTML with placeholders
    DashboardHTML = ПолучитьТекстМакетаDashboard();
КонецПроцедуры
```

---

## Template Automation

### RECOMMENDED: template: property (v2.42.0+)

Use `template:` property on `HTMLDocumentField` for **full control** over element positioning:

```yaml
templates:
  - name: Dashboard
    type: HTMLDocument
    file: templates/dashboard.html
    automation: templates/dashboard.automation.yaml  # Optional

forms:
  - name: Форма
    elements:
      - type: UsualGroup
        name: PreviewGroup
        title_ru: Предпросмотр
        representation: WeakSeparation
        child_items:
          # NEW: template: links to template, auto-creates attribute
          - type: HTMLDocumentField
            name: DashboardPreview
            template: Dashboard        # Links to template by name
            width: 100
            height: 25
            stretch: HorizontalAndVertically
```

**When parser sees `template: Dashboard`:**
1. Creates FormAttribute `DashboardHTML` (type: string)
2. Sets element's `attribute: DashboardHTML`
3. Uses template's placeholders for BSL helper generation

**Advantages:**
- **Full positioning control** - place in any group, any form
- **Size control** - set width, height, stretch
- **Multiple instances** - same template in different positions

---

### DEPRECATED: auto_field: true (v2.41.0)

> **⚠️ DEPRECATED in v2.42.0+** - Use `template:` property instead for better positioning control.

When you set `auto_field: true`, the generator automatically creates:

1. **Form attribute** `{TemplateName}HTML` (type: string) - stores HTML content
2. **HTMLDocumentField** element `{TemplateName}Field` - displays HTML in form
3. **BSL helper function** `ПолучитьТекстМакета{TemplateName}()` - if placeholders defined

**Example (deprecated):**
```yaml
templates:
  - name: EmailPreview
    type: HTMLDocument
    file: templates/email.html
    auto_field: true                 # DEPRECATED - element added at end of form
    field_name: CustomField          # Optional
    target_form: Форма               # Optional
```

### Placeholders

Define dynamic values in `automation` file:

```yaml
# templates/email.automation.yaml
placeholders:
  - name: "{{UserName}}"              # Mustache-style: {{Name}}
    bsl_value: "СокрЛП(ИмяПользователя())"  # Direct BSL expression

  - name: "{{CurrentDate}}"
    bsl_value: 'Формат(ТекущаяДата(), "ДФ=''dd MMMM yyyy''")'

  - name: "{{CompanyName}}"
    attribute: CompanyName            # Reference to form attribute (adds "Объект." prefix)
```

**Generated BSL:**
```bsl
&НаСервере
Функция ПолучитьТекстМакетаEmailPreview()
    Макет = РеквизитФормыВЗначение("Объект").ПолучитьМакет("EmailPreview");
    Результат = Макет.ПолучитьТекст();

    // Заміна placeholders
    Результат = СтрЗаменить(Результат, "{{UserName}}", СокрЛП(ИмяПользователя()));
    Результат = СтрЗаменить(Результат, "{{CurrentDate}}", Формат(ТекущаяДата(), "ДФ='dd MMMM yyyy'"));
    Результат = СтрЗаменить(Результат, "{{CompanyName}}", Объект.CompanyName);

    Возврат Результат;
КонецФункции
```

### Assets Injection

CSS and JS files are automatically injected into HTML:

```yaml
# templates/dashboard.automation.yaml
assets:
  styles:
    - file: styles.css           # Injected into <head><style>...</style></head>
    - inline: ".custom { color: red; }"  # Inline CSS

  scripts:
    - file: scripts.js           # Injected before </body>
```

---

## HTML Best Practices for 1C

### 1. NO EMOJI - Use SVG Icons

**CRITICAL:** 1C HTMLDocumentField has limited Unicode support. Emoji display as squares.

**BAD:**
```html
<div class="icon">📊</div>  <!-- Will show as square! -->
```

**GOOD:**
```html
<div class="icon">
    <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
        <path d="M3 13h2v8H3v-8zm4-5h2v13H7V8zm4-5h2v18h-2V3zm4 9h2v9h-2v-9zm4-4h2v13h-2V8z"/>
    </svg>
</div>
```

### 2. Self-Contained HTML

All CSS and JS should be inline or injected via `assets:`. External CDN links won't work in offline 1C environments.

**BAD:**
```html
<link href="https://cdn.example.com/styles.css" rel="stylesheet">
```

**GOOD:**
```html
<style>
    /* All styles inline or injected via automation */
    .dashboard { padding: 20px; }
</style>
```

### 3. JavaScript Limitations

- **No ES6 modules** - use classic script tags
- **No external APIs** - no fetch to external services
- **No localStorage** - use 1C attributes for state
- **onclick handlers work** - inline event handlers are supported

**Working JavaScript:**
```javascript
// Counter example - works in 1C HTMLDocumentField
let counter = 0;

function increment() {
    counter++;
    document.getElementById('counter').textContent = counter;
}

function reset() {
    counter = 0;
    document.getElementById('counter').textContent = counter;
}
```

### 4. Recommended HTML Structure

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Dashboard</title>
    <!-- Styles injected here by generator -->
</head>
<body>
    <div class="container">
        <!-- Your content with {{placeholders}} -->
        <h1>Привет, {{UserName}}!</h1>
        <p>Дата: {{CurrentDate}}</p>

        <!-- Interactive elements -->
        <button onclick="doSomething()">Click me</button>
    </div>
    <!-- Scripts injected here by generator -->
</body>
</html>
```

---

## Complete Example: Dashboard

### File Structure

```
html_dashboard_demo/
├── config.yaml
├── handlers.bsl
└── templates/
    ├── dashboard.html
    ├── dashboard.automation.yaml
    ├── styles.css
    └── scripts.js
```

### config.yaml

```yaml
processor:
  name: HTMLDashboard
  synonym_ru: HTML Дашборд
  synonym_uk: HTML Дашборд

templates:
  - name: Dashboard
    type: HTMLDocument
    file: templates/dashboard.html
    auto_field: true
    field_name: DashboardField
    automation: templates/dashboard.automation.yaml

forms:
  - name: Форма
    default: true

    elements:
      - type: Button
        name: RefreshButton
        command: RefreshDashboard
        parent: ФормаКоманднаяПанель

    commands:
      - name: RefreshDashboard
        title_ru: Обновить
        title_uk: Оновити
        handler: RefreshDashboard
        picture: StdPicture.Refresh

    events:
      OnCreateAtServer: ПриСозданииНаСервере
```

### handlers.bsl

```bsl
// Event: OnCreateAtServer - auto-load HTML when form opens
&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
    ОбновитьДашбордНаСервере();
КонецПроцедуры

// Command: RefreshDashboard - manual refresh
&НаКлиенте
Процедура RefreshDashboard(Команда)
    ОбновитьДашбордНаСервереКлиент();
КонецПроцедуры

&НаКлиенте
Процедура ОбновитьДашбордНаСервереКлиент()
    ОбновитьДашбордНаСервере();
КонецПроцедуры

&НаСервере
Процедура ОбновитьДашбордНаСервере()
    // ПолучитьТекстМакетаDashboard() is auto-generated by template automation
    DashboardHTML = ПолучитьТекстМакетаDashboard();
КонецПроцедуры
```

### templates/dashboard.html

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Dashboard</title>
</head>
<body>
    <div class="dashboard">
        <header class="header">
            <h1>Привет, {{UserName}}!</h1>
            <span class="date">{{CurrentDate}}</span>
        </header>

        <div class="cards">
            <div class="card">
                <div class="card-icon">
                    <!-- SVG icon instead of emoji -->
                    <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z"/>
                    </svg>
                </div>
                <div class="card-content">
                    <h3>Время</h3>
                    <p>{{CurrentTime}}</p>
                </div>
            </div>
        </div>

        <div class="counter-section">
            <h2>Интерактивный счётчик</h2>
            <div class="counter">
                <button class="btn" onclick="changeCounter(-1)">-</button>
                <span id="counterValue">0</span>
                <button class="btn" onclick="changeCounter(1)">+</button>
            </div>
            <button class="btn" onclick="resetCounter()">Сбросить</button>
        </div>
    </div>
</body>
</html>
```

### templates/dashboard.automation.yaml

```yaml
placeholders:
  - name: "{{UserName}}"
    bsl_value: "СокрЛП(ИмяПользователя())"

  - name: "{{CurrentDate}}"
    bsl_value: 'Формат(ТекущаяДата(), "ДФ=''dd MMMM yyyy''")'

  - name: "{{CurrentTime}}"
    bsl_value: 'Формат(ТекущаяДата(), "ДФ=''HH:mm:ss''")'

assets:
  styles:
    - file: styles.css
  scripts:
    - file: scripts.js
```

### templates/styles.css

```css
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Segoe UI', Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.dashboard {
    max-width: 800px;
    margin: 0 auto;
}

.header {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header h1 { color: #333; font-size: 1.5rem; }
.header .date { color: #666; }

.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
}

.card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.card-icon { color: #667eea; }
.card-content h3 { color: #333; font-size: 0.9rem; }
.card-content p { color: #667eea; font-size: 1.2rem; font-weight: bold; }

.counter-section {
    background: white;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.counter-section h2 { margin-bottom: 15px; color: #333; }

.counter {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
    margin-bottom: 15px;
}

.counter span { font-size: 2rem; font-weight: bold; color: #667eea; }

.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 8px;
    background: #667eea;
    color: white;
    cursor: pointer;
    font-size: 1rem;
    transition: background 0.2s;
}

.btn:hover { background: #5a6fd6; }
```

### templates/scripts.js

```javascript
// Counter state
let counter = 0;

function changeCounter(delta) {
    counter += delta;
    document.getElementById('counterValue').textContent = counter;
}

function resetCounter() {
    counter = 0;
    document.getElementById('counterValue').textContent = counter;
}
```

---

## Generation Command

```bash
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output output \
  --output-format epf
```

**Output:** `output/HTMLDashboard.epf` ready to open in 1C

---

## Common Patterns

### Pattern 1: Display-Only Dashboard

No refresh button, just auto-load on form open.

```yaml
forms:
  - name: Форма
    default: true
    events:
      OnCreateAtServer: ПриСозданииНаСервере
```

### Pattern 2: Refreshable Content

Button to manually refresh HTML content.

```yaml
forms:
  - name: Форма
    default: true
    elements:
      - type: Button
        name: RefreshButton
        command: Refresh
        parent: ФормаКоманднаяПанель
    commands:
      - name: Refresh
        title_ru: Обновить
        picture: StdPicture.Refresh
        handler: Refresh
    events:
      OnCreateAtServer: ПриСозданииНаСервере
```

### Pattern 3: Data Input + HTML Preview

Form attributes for input, HTML shows preview.

```yaml
attributes:
  - name: RecipientName
    type: string
  - name: Subject
    type: string

templates:
  - name: EmailPreview
    type: HTMLDocument
    file: templates/email.html
    auto_field: true
    automation: templates/email.automation.yaml

forms:
  - name: Форма
    elements:
      - type: InputField
        name: RecipientNameField
        attribute: RecipientName
      - type: InputField
        name: SubjectField
        attribute: Subject
      - type: Button
        name: PreviewButton
        command: Preview
```

```yaml
# automation file
placeholders:
  - name: "{{RecipientName}}"
    attribute: RecipientName     # Reads from Объект.RecipientName
  - name: "{{Subject}}"
    attribute: Subject
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Emoji shows as square | 1C limited Unicode support | Use SVG icons |
| CSS not applied | External CSS link | Use inline styles or `assets:` |
| JS not working | ES6 syntax | Use ES5 compatible code |
| HTML not loading | Missing event handler | Add `OnCreateAtServer` event |
| Blank page | Wrong attribute name | Check `auto_field` creates `{Name}HTML` |

---

## Advanced: SPA Web Applications

For **full single-page application** patterns (mobile apps, kiosks, complex dashboards with navigation):

See **[WEB_PATTERNS.md](reference/WEB_PATTERNS.md)** which covers:
- **Event Queue Pattern** - JS to BSL communication
- **DOM Manipulation Helpers** - BSL functions for DOM operations
- **Screen Router Pattern** - Navigation between screens
- **Bootstrap 5 Integration** - Responsive mobile-friendly UI
- **Complete SPA Skeleton** - Full working example

---

## See Also

- [WEB_PATTERNS.md](reference/WEB_PATTERNS.md) - SPA patterns for complex web interfaces
- [API_REFERENCE.md](reference/API_REFERENCE.md) - Templates section
- [examples/yaml/html_dashboard_demo/](../examples/yaml/html_dashboard_demo/) - Complete working example
- [VALID_PICTURES.md](VALID_PICTURES.md) - StdPicture icons for buttons
