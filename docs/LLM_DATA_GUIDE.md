# 1C Processor Generator - Data Models Decision Guide

**Target:** LLMs generating 1C processors
**Core guide:** [LLM_CORE.md](LLM_CORE.md)

---

## 🧠 Mental Model: Persistent vs Temporary Data

**Before choosing between TabularSection, ValueTable, and ValueTree, understand the fundamental principle:**

```
┌────────────────────────────────────────────────────┐
│  PERSISTENT DATA (survives form close)            │
│  - Saved to database automatically                │
│  - Part of processor metadata                     │
│  → Use: TabularSection                            │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│  TEMPORARY FLAT DATA (exists only while form open) │
│  - Exists in memory only                           │
│  - Lost when form closes (unless manually saved)   │
│  → Use: ValueTable                                 │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│  TEMPORARY HIERARCHICAL DATA (parent-child)        │
│  - Tree structure (nested levels)                  │
│  - JSON visualization, catalog trees               │
│  → Use: ValueTree (v2.64.0+)                       │
└────────────────────────────────────────────────────┘
```

**Key insight:** This is NOT about "which is better" — it's about **data lifetime and structure requirements**.

---

## 🎯 Decision Framework

### Step 1: Ask the Lifetime Question

**Does this data need to exist after the form closes?**

```
YES → Go to Step 2
NO  → Use ValueTable ✅ (reports, calculations, previews)
```

### Step 2: Ask the Business Data Question

**Is this core business data (documents, master records)?**

```
YES → Use TabularSection ✅ (invoice lines, order items, persistent relationships)

NO  → Go to Step 3
```

### Step 3: Ask the Manual Save Question

**Will you save this data manually (to JSON, file, external system)?**

```
YES → Use ValueTable + manual save ✅ (saved searches, user preferences, exports)

NO  → Use TabularSection ✅ (should auto-save with processor)
```

### Visual Decision Tree

```
User request: "Create table for [data description]"
    ↓
┌──────────────────────────────────────┐
│ Does data survive form close?       │
└────────┬─────────────────────────────┘
         │
    NO   │   YES
         ↓        ↓
    ┌────────┐  ┌─────────────────────────────┐
    │Value   │  │ Is this core business data? │
    │Table ✅ │  │ (invoices, orders, etc.)   │
    └────────┘  └────────┬────────────────────┘
                         │
                   YES   │   NO
                         ↓        ↓
                    ┌────────┐  ┌──────────────────────┐
                    │Tabular │  │ Manual save needed?  │
                    │Section │  │ (JSON, files, etc.)  │
                    │✅      │  └────────┬─────────────┘
                    └────────┘           │
                                   YES   │   NO
                                         ↓        ↓
                                    ┌────────┐  ┌────────┐
                                    │Value   │  │Tabular │
                                    │Table ✅ │  │Section │
                                    └────────┘  │✅      │
                                                └────────┘
```

---

## 📊 TabularSection: Deep Dive

### What It Is

**TabularSection** = processor-level metadata for **persistent** data storage

**Technical details:**
- Defined in `processor.xml` (ChildObjects section)
- Creates database table structure
- Auto-saves when processor object is saved
- Accessed via `Объект.TableName` in BSL code
- Survives between sessions (persisted to DB)

### When to Use TabularSection

**✅ Use TabularSection for:**

1. **Document lines** (invoices, orders, receipts)
   ```yaml
   tabular_sections:
     - name: Lines
       columns:
         - name: Product
           type: CatalogRef.Products
         - name: Quantity
           type: number
           digits: 10
           fraction_digits: 2
         - name: Price
           type: number
           digits: 15
           fraction_digits: 2
         - name: Total
           type: number
           digits: 15
           fraction_digits: 2
           read_only: true  # Calculated field (v2.13.1+)
   ```

2. **Persistent relationships** (configuration entries, master data)
   ```yaml
   tabular_sections:
     - name: UserRoles
       columns:
         - name: User
           type: CatalogRef.Users
         - name: Role
           type: CatalogRef.Roles
   ```

3. **Historical records** (audit logs, change tracking)

### TabularSection Code Example

```yaml
# YAML
processor:
  name: OrderProcessor

tabular_sections:
  - name: OrderLines
    columns:
      - {name: Product, type: CatalogRef.Products}
      - {name: Quantity, type: number}
```

```bsl
// BSL - auto-saved when processor is saved
&НаСервере
Процедура AddLineНаСервере(ProductRef, Qty)
    НоваяСтрока = Объект.OrderLines.Add();  // ← Saved to DB
    НоваяСтрока.Product = ProductRef;
    НоваяСтрока.Quantity = Qty;
    // No explicit save needed - auto-saves with Объект
КонецПроцедуры
```

**Key characteristics:**
- ✅ Auto-persisted (no manual save code)
- ✅ Database-backed (can query with SQL)
- ✅ Transactional (saves/rolls back with processor)
- ⚠️ Slower (DB overhead)
- ⚠️ Not for large temporary datasets

---

## 📋 ValueTable: Deep Dive

### What It Is

**ValueTable** = form-level attribute for **temporary** data display

**Technical details:**
- Defined in `form.xml` (Attributes section)
- Exists in memory only (no database table)
- Cleared when form closes (unless manually saved)
- Accessed directly via `TableName` in BSL code (no `Объект.` prefix)
- Fast (no DB overhead)

### When to Use ValueTable

**✅ Use ValueTable for:**

1. **Report results** (temporary calculations/aggregations)
   ```yaml
   forms:
     - name: Форма
       value_tables:
         - name: ReportResults
           columns:
             - {name: Period, type: string, length: 50}
             - {name: Amount, type: number, digits: 15, fraction_digits: 2}
   ```

2. **Search results** (no need to persist every search)
   ```yaml
   forms:
     - name: Форма
       value_tables:
         - name: SearchResults
           columns:
             - {name: Title, type: string, length: 300}
             - {name: URL, type: string, length: 500}
   ```

3. **Calculation previews** (show before applying)
   ```yaml
   forms:
     - name: Форма
       value_tables:
         - name: ImportPreview
           columns:
             - {name: FileName, type: string, length: 200}
             - {name: Status, type: string, length: 50}
   ```

4. **Temporary transformations** (intermediate processing)

### ValueTable Code Example

```yaml
# YAML
forms:
  - name: Форма
    value_tables:
      - name: Results
        columns:
          - {name: Product, type: string, length: 200}
          - {name: Total, type: number}
```

```bsl
// BSL - memory only, NOT saved
&НаСервере
Процедура LoadReportDataНаСервере()
    Results.Clear();  // ← Always clear before loading

    // Query database
    Запрос = Новый Запрос;
    Запрос.Текст = "SELECT ...";
    Выборка = Запрос.Выполнить().Выбрать();

    // Load into ValueTable
    Пока Выборка.Следующий() Цикл
        НоваяСтрока = Results.Add();  // ← NOT saved to DB, memory only
        НоваяСтрока.Product = Выборка.Product;
        НоваяСтрока.Total = Выборка.Total;
    КонецЦикла;

    // Data exists until form closes (or manual export)
КонецПроцедуры
```

**Key characteristics:**
- ✅ Fast (memory only, no DB)
- ✅ Flexible (any structure, no schema)
- ✅ No database overhead
- ⚠️ Lost on form close (must save manually if needed)
- ⚠️ Direct access (`Results` not `Объект.Results`)

---

## 🌳 ValueTree: Deep Dive (v2.64.0+)

### What It Is

**ValueTree** = form-level attribute for **temporary hierarchical** data display

**Technical details:**
- Defined in `form.xml` (Attributes section with `v8:ValueTree` type)
- Displays as tree with expandable/collapsible nodes
- Parent-child relationships via `.ПолучитьЭлементы()` method
- Cleared when form closes (like ValueTable)
- Accessed directly via `TreeName` in BSL code (no `Объект.` prefix)

### When to Use ValueTree

**✅ Use ValueTree for:**

1. **JSON/XML visualization** (nested structure display)
   ```yaml
   forms:
     - name: Форма
       value_trees:
         - name: JSONTree
           columns:
             - {name: Key, type: string}
             - {name: Value, type: string}
             - {name: Type, type: string, length: 50}
   ```

2. **Hierarchical catalogs** (folder structures, org charts)
   ```yaml
   forms:
     - name: Форма
       value_trees:
         - name: FolderTree
           columns:
             - {name: Name, type: string}
             - {name: Path, type: string}
             - {name: IsFolder, type: boolean}
   ```

3. **Configuration trees** (settings with sections)
4. **Bill of Materials** (products with sub-components)
5. **Organization structures** (departments → teams → employees)

### ValueTree YAML Example

```yaml
# YAML
forms:
  - name: Форма

    value_trees:
      - name: DataTree
        title:
          ru: Дерево данных
          uk: Дерево даних
        columns:
          - name: Name
            type: string
            synonym:
              ru: Наименование
          - name: Value
            type: string
          - name: Type
            type: string
            length: 50

    elements:
      - type: Table
        name: TreeTable
        tabular_section: DataTree
        representation: tree                    # ← Key property!
        initial_tree_view: expand_top_level     # no_expand | expand_top_level | expand_all_levels
        show_root: false
        allow_root_choice: false
        choice_folders_and_items: folders_and_items
        height: 15
        events:
          OnActivateRow: TreeTableOnActivateRow
        columns:
          - name: Name
          - name: Value
          - name: Type
```

### ValueTree BSL Example

```bsl
// BSL - building tree structure
&НаСервере
Процедура FillTreeНаСервере()
    DataTree.ПолучитьЭлементы().Очистить();  // ← Clear root level

    // Add root node
    RootNode = DataTree.ПолучитьЭлементы().Добавить();
    RootNode.Name = "Settings";
    RootNode.Type = "Object";

    // Add child nodes (Level 2)
    ChildNode = RootNode.ПолучитьЭлементы().Добавить();  // ← Add to parent!
    ChildNode.Name = "Database";
    ChildNode.Type = "Object";

    // Add grandchild nodes (Level 3)
    LeafNode = ChildNode.ПолучитьЭлементы().Добавить();
    LeafNode.Name = "Host";
    LeafNode.Value = "localhost";
    LeafNode.Type = "Value";
КонецПроцедуры
```

### Tree-Specific Properties

| Property | Values | Description |
|----------|--------|-------------|
| `representation` | `list`, `tree` | Display mode (tree enables hierarchy) |
| `initial_tree_view` | `no_expand`, `expand_top_level`, `expand_all_levels` | Initial expansion state |
| `show_root` | `true`, `false` | Show/hide root element |
| `allow_root_choice` | `true`, `false` | Can user select root? |
| `choice_folders_and_items` | `folders`, `items`, `folders_and_items` | What can be selected |

### Tree Navigation in BSL

```bsl
// Navigate UP (to parent)
&НаКлиенте
Процедура NavigateUp(CurrentRow)
    Parent = CurrentRow.ПолучитьРодителя();
    Если Parent <> Неопределено Тогда
        // Process parent
    КонецЕсли;
КонецПроцедуры

// Navigate DOWN (to children)
&НаКлиенте
Процедура NavigateDown(CurrentRow)
    Children = CurrentRow.ПолучитьЭлементы();
    Для Каждого Child Из Children Цикл
        // Process each child
        NavigateDown(Child);  // Recursive!
    КонецЦикла;
КонецПроцедуры
```

### JSON to Tree Conversion Pattern

```bsl
// Recursive function to build tree from JSON
&НаСервере
Процедура JSONToTree(ParentItems, Key, Value)
    TypeOfValue = ТипЗнч(Value);

    Если TypeOfValue = Тип("Структура") ИЛИ TypeOfValue = Тип("Соответствие") Тогда
        // Object
        Node = ParentItems.Добавить();
        Node.Name = Key;
        Node.Type = "Object";

        Для Каждого Item Из Value Цикл
            JSONToTree(Node.ПолучитьЭлементы(), Item.Ключ, Item.Значение);
        КонецЦикла;

    ИначеЕсли TypeOfValue = Тип("Массив") Тогда
        // Array
        Node = ParentItems.Добавить();
        Node.Name = Key;
        Node.Type = "Array";

        Для Index = 0 По Value.ВГраница() Цикл
            JSONToTree(Node.ПолучитьЭлементы(), "[" + Index + "]", Value[Index]);
        КонецЦикла;

    Иначе
        // Primitive value
        Node = ParentItems.Добавить();
        Node.Name = Key;
        Node.Value = Строка(Value);
        Node.Type = "Value";
    КонецЕсли;
КонецПроцедуры
```

**Key characteristics:**
- ✅ Hierarchical structure (parent-child)
- ✅ Expandable/collapsible nodes in UI
- ✅ Same performance as ValueTable (memory only)
- ✅ Direct access (`DataTree` not `Объект.DataTree`)
- ⚠️ Lost on form close (like ValueTable)
- ⚠️ Requires `representation: tree` on Table element

---

## 🔄 Manual Save: When ValueTable Needs Persistence

**Scenario:** User wants to save ValueTable data (e.g., saved search results)

**Solution:** Manual export to JSON, file, or database

### Example: Export ValueTable to JSON

```bsl
&НаСервере
Процедура ExportToJSONНаСервере(ФайлПуть)
    ЗаписьJSON = Новый ЗаписьJSON;
    ЗаписьJSON.ОткрытьФайл(ФайлПуть);

    МассивДанных = Новый Массив;
    Для Каждого Строка Из SavedResults Цикл
        Элемент = Новый Структура;
        Элемент.Вставить("Title", Строка.Title);
        Элемент.Вставить("URL", Строка.URL);
        МассивДанных.Добавить(Элемент);
    КонецЦикла;

    ЗаписатьJSON(ЗаписьJSON, МассивДанных);
    ЗаписьJSON.Закрыть();

    Сообщить("Экспортировано записей: " + SavedResults.Количество());
КонецПроцедуры
```

**When to use manual save:**
- User-selected items from search results
- Exported reports (Excel, CSV, JSON)
- User preferences/settings
- Temporary drafts

---

## 📐 Common Mistakes & Fixes

### Mistake 1: TabularSection for Reports

```yaml
# ❌ WRONG - Report data doesn't need database persistence
tabular_sections:
  - name: ReportResults
    columns:
      - {name: Product, type: string, length: 200}
```

**Problem:** Every report generation creates database records → wasted space, slow performance

**✅ FIX:**
```yaml
# ✅ CORRECT - Temporary in-memory results
forms:
  - name: Форма
    value_tables:
      - name: ReportResults
        columns:
          - {name: Product, type: string, length: 200}
```

---

### Mistake 2: ValueTable for Document Lines

```yaml
# ❌ WRONG - Document lines must persist
forms:
  - name: Форма
    value_tables:
      - name: InvoiceLines
        columns:
          - {name: Product, type: CatalogRef.Products}
```

**Problem:** Data lost when form closes → can't save invoice properly

**✅ FIX:**
```yaml
# ✅ CORRECT - Persistent document lines
tabular_sections:
  - name: InvoiceLines
    columns:
      - {name: Product, type: CatalogRef.Products}
      - {name: Quantity, type: number}
```

---

### Mistake 3: Accessing ValueTable with `Объект.` Prefix

```bsl
// ❌ WRONG - ValueTable is NOT on Объект
НоваяСтрока = Объект.Results.Add();  // ERROR!
```

**✅ FIX:**
```bsl
// ✅ CORRECT - ValueTable is accessed directly
НоваяСтрока = Results.Add();  // ✅ Works
```

---

## 🎮 Table Events

### Available Events

| Event | When Triggered | Use Case | Handler Type |
|-------|----------------|----------|--------------|
| **OnActivateRow** | User selects row | Load detail data | Client + Server |
| **Selection** | Double-click or Enter | Open detailed form | Client |
| **OnStartEdit** | User starts editing cell | Validate before edit | Client |
| **BeforeAddRow** | User adds new row | Pre-fill defaults, validate | Client (v2.35.0+) |
| **BeforeDeleteRow** | User deletes row | Confirm deletion | Client (v2.35.0+) |
| **BeforeRowChange** | User starts editing | Validate permissions | Client (v2.35.0+) |

### OnActivateRow: Master-Detail Pattern

**Most common:** Selecting master table row → auto-loads detail data

```yaml
elements:
  - type: Table
    name: MasterTable
    tabular_section: MasterData
    properties:
      is_value_table: true
    events:
      OnActivateRow: MasterTableOnActivateRow  # ← Triggers on row selection
```

**Client handler** (gets current row):
```bsl
&НаКлиенте
Процедура MasterTableOnActivateRow(Элемент)
    ТекущаяСтрока = Элементы.MasterTable.ТекущиеДанные;

    Если ТекущаяСтрока = Неопределено Тогда
        DetailData.Clear();
        Возврат;
    КонецЕсли;

    // Call server with parameters
    MasterTableOnActivateRowНаСервере(ТекущаяСтрока.ID);
КонецПроцедуры
```

**Server handler** (loads detail data):
```bsl
&НаСервере
Процедура MasterTableOnActivateRowНаСервере(МастерID)
    DetailData.Clear();

    // Load detail data based on master ID
    // ... query/calculations ...

    Для Каждого Строка Из Результат Цикл
        НоваяСтрока = DetailData.Add();
        // ... populate detail row ...
    КонецЦикла;
КонецПроцедуры
```

**See also:** [LLM_PATTERNS_ESSENTIAL.md](LLM_PATTERNS_ESSENTIAL.md) Pattern 3 for complete example

### BeforeAddRow: Pre-fill and Validation (v2.35.0+)

**Use case:** Set default values in new row, validate conditions before adding

```yaml
elements:
  - type: Table
    name: Items
    tabular_section: Items
    events:
      BeforeAddRow: ItemsBeforeAddRow
```

**Handler signature:**
```bsl
&НаКлиенте
Процедура ItemsBeforeAddRow(Элемент, Отказ, Копирование, Родитель, Группа)
    // Отказ = Истина - prevents row addition
    // Копирование - true if user is copying existing row

    // Example 1: Pre-fill with default values
    Если НЕ Копирование Тогда
        НоваяСтрока = Элементы.Items.ТекущиеДанные;
        Если НоваяСтрока <> Неопределено Тогда
            НоваяСтрока.Quantity = 1;
            НоваяСтрока.Price = 0;
        КонецЕсли;
    КонецЕсли;

    // Example 2: Prevent adding if condition not met
    Если Объект.Items.Count() >= 100 Тогда
        Сообщить("Maximum 100 items allowed!");
        Отказ = Истина;
    КонецЕсли;
КонецПроцедуры
```

**Key points:**
- Fires **before** row is added to table
- Set `Отказ = Истина` to cancel row addition
- Check `Копирование` to distinguish between new row and copied row
- Pre-fill default values for better UX

### BeforeDeleteRow: Confirmation and Validation (v2.35.0+)

**Use case:** Confirm deletion with user, prevent deletion under certain conditions

```yaml
elements:
  - type: Table
    name: Items
    tabular_section: Items
    events:
      BeforeDeleteRow: ItemsBeforeDeleteRow
```

**Handler signature:**
```bsl
&НаКлиенте
Процедура ItemsBeforeDeleteRow(Элемент, Отказ)
    ТекущиеДанные = Элемент.ТекущиеДанные;

    Если ТекущиеДанные = Неопределено Тогда
        Возврат;
    КонецЕсли;

    // Example 1: Confirmation dialog
    Ответ = Вопрос(
        "Удалить товар '" + ТекущиеДанные.Product + "'?",
        РежимДиалогаВопрос.ДаНет
    );

    Если Ответ = КодВозвратаДиалога.Нет Тогда
        Отказ = Истина;  // Cancel deletion
    КонецЕсли;

    // Example 2: Prevent deletion based on business rules
    Если ТекущиеДанные.Shipped = Истина Тогда
        Сообщить("Cannot delete shipped items!");
        Отказ = Истина;
    КонецЕсли;
КонецПроцедуры
```

**Key points:**
- Fires **before** row is deleted
- Set `Отказ = Истина` to cancel deletion
- Get current row data via `Элемент.ТекущиеДанные`
- Good practice: always confirm destructive actions

### BeforeRowChange: Edit Validation (v2.35.0+)

**Use case:** Validate permissions before editing, check business rules

```yaml
elements:
  - type: Table
    name: Items
    tabular_section: Items
    events:
      BeforeRowChange: ItemsBeforeRowChange
```

**Handler signature:**
```bsl
&НаКлиенте
Процедура ItemsBeforeRowChange(Элемент, Отказ)
    ТекущиеДанные = Элемент.ТекущиеДанные;

    Если ТекущиеДанные = Неопределено Тогда
        Возврат;
    КонецЕсли;

    // Example 1: Prevent editing of processed items
    Если ТекущиеДанные.Status = "Processed" Тогда
        Сообщить("Cannot edit processed items!");
        Отказ = Истина;
    КонецЕсли;

    // Example 2: Check user permissions (requires server call)
    Если НЕ ПроверитьПраваРедактированияНаСервере() Тогда
        Сообщить("You don't have permission to edit!");
        Отказ = Истина;
    КонецЕсли;
КонецПроцедуры
```

**Key points:**
- Fires **before** user starts editing row
- Set `Отказ = Истина` to prevent editing
- Good for: permission checks, status validation, locking rules
- Different from `OnStartEdit` (which fires when entering specific cell)

### Event Combinations

**Real-world pattern:** Combine multiple events for complete table control

```yaml
elements:
  - type: Table
    name: OrderItems
    tabular_section: Items
    events:
      BeforeAddRow: OrderItemsBeforeAddRow          # Pre-fill defaults
      BeforeDeleteRow: OrderItemsBeforeDeleteRow    # Confirm deletion
      BeforeRowChange: OrderItemsBeforeRowChange    # Check if order is locked
      OnActivateRow: OrderItemsOnActivateRow        # Load item details
```

**Pattern benefits:**
- **BeforeAddRow**: Ensures new rows have valid defaults (Quantity=1, Price=0)
- **BeforeDeleteRow**: Prevents accidental deletions (confirmation dialog)
- **BeforeRowChange**: Enforces business rules (can't edit completed orders)
- **OnActivateRow**: Shows additional info (item description, stock levels)

---

## 📏 String Types: Unlimited vs Limited

### Default: Unlimited Strings

**By default, strings are unlimited** (no length restriction):

```yaml
attributes:
  - name: Description
    type: string  # length not specified → unlimited (length=0)
```

**In 1C XML:**
```xml
<v8:Length>0</v8:Length>  <!-- 0 = unlimited -->
```

### Limited Strings

**Specify `length:` parameter for limited strings:**

```yaml
attributes:
  - name: ShortCode
    type: string
    length: 100  # Limited to 100 characters
```

**In 1C XML:**
```xml
<v8:Length>100</v8:Length>  <!-- Explicit limit -->
```

### When to Use Each

**✅ Use unlimited (default):**
- Descriptions, notes, comments
- Text fields with unknown max length
- User-generated content

**✅ Use limited:**
- Codes (product code: 20 chars)
- Status values (10-50 chars)
- Known-length fields (phone: 20 chars, email: 100 chars)
- Performance-critical fields (indexes work better with limits)

**Rule of thumb:** If you know the max length, specify it. Otherwise, use unlimited (default).

---

## 📖 Summary Checklist

**When designing data structure, ask:**

1. **Lifetime:** Does data survive form close?
   - YES → TabularSection or ValueTable + manual save
   - NO → ValueTable or ValueTree

2. **Structure:** Is data hierarchical (parent-child, nested)?
   - YES → ValueTree (v2.64.0+)
   - NO → ValueTable or TabularSection

3. **Business Data:** Is this core business data (invoices, orders)?
   - YES → TabularSection
   - NO → Consider ValueTable/ValueTree

4. **Manual Save:** Will you export/save manually (JSON, files)?
   - YES → ValueTable/ValueTree + export logic
   - NO → TabularSection

5. **Performance:** Is this large temporary dataset (>1000 rows)?
   - YES → ValueTable/ValueTree (avoid DB overhead)
   - NO → Either works

6. **String Length:** Know max length?
   - YES → Specify `length: N`
   - NO → Omit (unlimited by default)

### Quick Reference: Data Type Selection

| Scenario | Use | Why |
|----------|-----|-----|
| Invoice lines | TabularSection | Must persist to DB |
| Report results | ValueTable | Temporary, flat data |
| JSON visualization | ValueTree | Hierarchical, nested |
| Search results | ValueTable | Temporary, flat list |
| Folder tree | ValueTree | Hierarchical structure |
| User preferences | ValueTable + save | Temporary + manual export |
| Config settings | ValueTree | Nested sections |

---

**Last updated:** 2025-12-28
**Generator version:** 2.64.0+
