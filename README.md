<div align="center">

# 1C Processor Generator

### Генерація обробок 1С за допомогою AI — від ідеї до .epf за 30 секунд

[![GitHub stars](https://img.shields.io/github/stars/SERGIUSH-UA/1c-processor-generator-pro?style=social)](https://github.com/SERGIUSH-UA/1c-processor-generator-pro/stargazers)
[![Version](https://img.shields.io/badge/version-2.58.0-blue.svg)](https://github.com/SERGIUSH-UA/1c-processor-generator-pro/releases)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-3776ab.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

[**Документація**](docs/LLM_CORE.md) · [**Приклади**](examples/yaml/) · [**PRO версія**](https://itdeo.tech/1c-processor-generator/?utm_source=github&utm_medium=referral&utm_campaign=readme&utm_content=header)

<img src="docs/marketing/Hello world 1C short final.gif" alt="Demo: AI generates 1C processor in 30 seconds" width="750">

### 🎬 Відео-туторіал: Monobank API інтеграція за 10 хвилин

[![YouTube Tutorial](https://img.shields.io/badge/YouTube-Дивитись_туторіал-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/watch?v=4RpeyCzV1po)

3 рівні AI для 1С-розробника — FREE → MID → PRO

</div>

---

## Проблема → Рішення

| Проблема | Рішення |
|----------|---------|
| LLM не можуть генерувати валідний 1C XML | Генератор обробляє всю складність |
| UUID, ID, вкладені структури — 100% помилок | YAML простий для AI та людей |
| 20-40 хвилин ручної роботи | **30 секунд** з генератором |

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ YAML config │ ──► │  Generator  │ ──► │  .epf file  │
│ + BSL code  │     │   (magic)   │     │   (ready!)  │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## Швидкий старт

```bash
# Встановлення
pip install git+https://github.com/SERGIUSH-UA/1c-processor-generator-pro.git

# Мінімальна обробка
python -m 1c_processor_generator minimal МояОбробка

# З YAML конфігурації
python -m 1c_processor_generator yaml \
  --config config.yaml \
  --handlers-file handlers.bsl \
  --output output/ \
  --output-format epf
```

---

## Приклад

**config.yaml** (20 рядків):
```yaml
processor:
  name: InvoiceGen
  synonym:
    uk: Генератор рахунків

attributes:
  - name: Client
    type: string
  - name: Amount
    type: number

forms:
  - name: Form
    default: true
    elements:
      - type: InputField
        name: ClientField
        attribute: Client
      - type: InputField
        name: AmountField
        attribute: Amount
      - type: Button
        name: GenerateBtn
        command: Generate
    commands:
      - name: Generate
        handler: Generate
```

**handlers.bsl** (5 рядків):
```bsl
#Region Generate
&AtClient
Procedure Generate(Command)
    ShowMessageBox(, "Invoice created!");
EndProcedure
#EndRegion
```

**Результат:** Повноцінна .epf обробка з формою, полями вводу та кнопкою.

---

## Можливості

| Категорія | Підтримка |
|-----------|-----------|
| **Елементи форми** | InputField, Button, Table, CheckBox, RadioButton, Pages, Groups, Labels |
| **Дані** | Атрибути, TabularSection, ValueTable, DynamicList |
| **Типи** | string, number, date, boolean, CatalogRef, DocumentRef |
| **BSL** | Автоматичні client-server пари, події форми та елементів |
| **Валідація** | YAML schema, BSL синтаксис, StdPicture |
| **Вивід** | XML (імпорт в конфігуратор) або EPF (готова обробка) |

---

## FREE vs PRO

| Функція | FREE | PRO |
|---------|:----:|:---:|
| Генерація XML | ✓ | ✓ |
| YAML валідація | ✓ | ✓ |
| Sync Tool | ✓ | ✓ |
| **Компіляція в EPF** | — | ✓ |
| **BSL валідація** | — | ✓ |
| **Без водяного знаку** | — | ✓ |

<p align="center">
  <a href="https://itdeo.tech/1c-processor-generator/?utm_source=github&utm_medium=referral&utm_campaign=readme&utm_content=badge">
    <img src="https://img.shields.io/badge/GET_PRO-itdeo.tech-orange?style=for-the-badge" alt="Get PRO">
  </a>
</p>

---

## Для LLM / AI агентів

Якщо ви LLM — почніть тут: **[docs/LLM_CORE.md](docs/LLM_CORE.md)**

Документація оптимізована для Claude/GPT:
- **LLM_CORE.md** — критичні правила, навігація
- **LLM_PATTERNS_ESSENTIAL.md** — 3 основні патерни (80% задач)
- **LLM_DATA_GUIDE.md** — вибір структур даних
- **QUICK_REFERENCE.md** — шпаргалка на 1 сторінку

---

## AI Асистенти (Web)

### ChatGPT Custom GPT

Готовий асистент для генерації обробок прямо в ChatGPT:

<p align="center">
  <a href="https://chatgpt.com/g/g-69441faa0c8081919bcf14fb6b038bc3-1c-processor-generator">
    <img src="https://img.shields.io/badge/ChatGPT-1C_Processor_Generator-10a37f?style=for-the-badge&logo=openai&logoColor=white" alt="ChatGPT Custom GPT">
  </a>
</p>

**Що вміє:**
- Генерує `config.yaml` + `handlers.bsl` за описом українською/російською
- Знає всі елементи форми, типи даних, патерни
- Видає команду для запуску генератора

**Як використовувати:**
1. Відкрийте [Custom GPT](https://chatgpt.com/g/g-69441faa0c8081919bcf14fb6b038bc3-1c-processor-generator)
2. Опишіть обробку: *"Створи форму для розрахунку знижки"*
3. Скопіюйте згенеровані файли
4. Запустіть: `python -m 1c_processor_generator yaml --config config.yaml --handlers-file handlers.bsl`

### Інші платформи

| Платформа | Як використовувати |
|-----------|-------------------|
| **Claude.ai** | Підключіть GitHub репозиторій або завантажте [LLM_WEB_LITE.md](docs/LLM_WEB_LITE.md) |
| **Gemini** | Завантажте [LLM_WEB_LITE.md](docs/LLM_WEB_LITE.md) у чат |

Детальний гайд: **[docs/WEB_CHAT_GUIDE.md](docs/WEB_CHAT_GUIDE.md)**

Шаблони для створення власних асистентів: **[templates/](templates/)**

---

## Документація

| Документ | Опис |
|----------|------|
| [LLM_CORE.md](docs/LLM_CORE.md) | Головний гайд для AI |
| [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) | Шпаргалка |
| [YAML_GUIDE.md](docs/YAML_GUIDE.md) | Повний API |
| [CHANGELOG.md](CHANGELOG.md) | Історія версій |

**Приклади:** [examples/yaml/](examples/yaml/)

---

## Вимоги

- Python 3.8+
- 1C:Підприємство 8.3 (для компіляції EPF)

```bash
pip install -r requirements.txt
```

---

## Ліцензія

- **FREE** — MIT License (open source)
- **PRO** — [Комерційна ліцензія](https://itdeo.tech/1c-processor-generator/?utm_source=github&utm_medium=referral&utm_campaign=readme&utm_content=license)

---

<div align="center">

**[Документація](docs/LLM_CORE.md)** · **[Приклади](examples/yaml/)** · **[PRO версія](https://itdeo.tech/1c-processor-generator/?utm_source=github&utm_medium=referral&utm_campaign=readme&utm_content=footer)** · **[Підтримка](https://github.com/SERGIUSH-UA/1c-processor-generator-pro/issues)**

Made with ❤️ by [SERGIUSH](https://github.com/SERGIUSH-UA)

**v2.58.0** · 1C:Enterprise 8.3.25+

</div>
