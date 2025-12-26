// Phase 1 Features Demo - All Event Handlers
// Demonstrates: New events from v2.35.0

// ========================================
// Form Events
// ========================================

// OnOpen - Form event (already supported)
&НаКлиенте
Процедура ПриОткрытии(Отказ)
    Сообщить("Form opened!");
КонецПроцедуры

// BeforeClose - Form event (v2.35.0+)
&НаКлиенте
Процедура ПередЗакрытием(Отказ, ЗавершениеРаботы, ТекстПредупреждения, СтандартнаяОбработка)
    Ответ = Вопрос("Вы действительно хотите закрыть форму?", РежимДиалогаВопрос.ДаНет);
    Если Ответ = КодВозвратаДиалога.Нет Тогда
        Отказ = Истина;
    КонецЕсли;
КонецПроцедуры

// ========================================
// Element Events
// ========================================

// HelpLinkClick - LabelDecoration с Hyperlink (v2.35.0+)
&НаКлиенте
Процедура HelpLinkClickНажатие(Элемент)
    Сообщить("Help link clicked! This demonstrates hyperlink property for LabelDecoration.");
    ПоказатьПредупреждение(, "This form demonstrates all new features from Phase 1:
    |
    |Properties:
    |  - MultiLine (DescriptionField)
    |  - PasswordMode (PasswordField)
    |  - TextEdit (UsernameField)
    |  - AutoMaxWidth (DescriptionField)
    |  - Hyperlink (this label!)
    |  - WindowOpeningMode (form property)
    |  - CommandBarLocation (form property)
    |
    |Events:
    |  - BeforeClose (this form)
    |  - ChoiceProcessing (SelectedValueField)
    |  - StartChoice (SelectedValueField)
    |  - BeforeAddRow (ItemsTable)
    |  - BeforeDeleteRow (ItemsTable)
    |  - BeforeRowChange (ItemsTable)");
КонецПроцедуры

// SelectedValueChoiceProcessing - ChoiceProcessing event (v2.35.0+)
&НаКлиенте
Процедура SelectedValueFieldОбработкаВыбора(Элемент, ВыбранноеЗначение, СтандартнаяОбработка)
    Сообщить("ChoiceProcessing event fired! Selected value: " + СокрЛП(ВыбранноеЗначение));

    // Custom validation
    Если ПустаяСтрока(ВыбранноеЗначение) Тогда
        Сообщить("Warning: Empty value selected!");
        СтандартнаяОбработка = Ложь;
    КонецЕсли;
КонецПроцедуры

// SelectedValueStartChoice - StartChoice event (already supported, but part of demo)
&НаКлиенте
Процедура SelectedValueFieldНачалоВыбора(Элемент, ДанныеВыбора, СтандартнаяОбработка)
    Сообщить("StartChoice event fired! Opening custom selection dialog...");

    // Example: Add custom choice items
    ДанныеВыбора = Новый СписокЗначений;
    ДанныеВыбора.Добавить("Option 1", "First option");
    ДанныеВыбора.Добавить("Option 2", "Second option");
    ДанныеВыбора.Добавить("Option 3", "Third option");

    СтандартнаяОбработка = Ложь;
КонецПроцедуры

// ========================================
// Table Events
// ========================================

// ItemsTableBeforeAddRow - BeforeAddRow event (v2.35.0+)
&НаКлиенте
Процедура ItemsTableПередДобавлениемСтроки(Элемент, Отказ, Копирование, Родитель, Группа)
    Сообщить("BeforeAddRow event fired!");

    // Example: Pre-fill new row
    Если НЕ Копирование Тогда
        // This would pre-fill the new row after it's created
        // ТекущиеДанные = Элемент.ТекущиеДанные;
        // ТекущиеДанные.Product = "New Product";
        Сообщить("New row will be added (not copying)");
    Иначе
        Сообщить("Row will be copied");
    КонецЕсли;

    // Example: Cancel addition conditionally
    // Отказ = Истина; // Uncomment to prevent row addition
КонецПроцедуры

// ItemsTableBeforeDeleteRow - BeforeDeleteRow event (v2.35.0+)
&НаКлиенте
Процедура ItemsTableПередУдалениемСтроки(Элемент, Отказ)
    Сообщить("BeforeDeleteRow event fired!");

    // Example: Confirm deletion
    ТекущиеДанные = Элемент.ТекущиеДанные;
    Если ТекущиеДанные <> Неопределено Тогда
        Ответ = Вопрос("Удалить товар '" + ТекущиеДанные.Product + "'?", РежимДиалогаВопрос.ДаНет);
        Если Ответ = КодВозвратаДиалога.Нет Тогда
            Отказ = Истина;
            Сообщить("Deletion cancelled by user");
        КонецЕсли;
    КонецЕсли;
КонецПроцедуры

// ItemsTableBeforeRowChange - BeforeRowChange event (v2.35.0+)
&НаКлиенте
Процедура ItemsTableПередИзменениемСтроки(Элемент, Отказ)
    Сообщить("BeforeRowChange event fired!");

    // Example: Validate before allowing edit
    ТекущиеДанные = Элемент.ТекущиеДанные;
    Если ТекущиеДанные <> Неопределено Тогда
        Сообщить("Starting to edit row: " + ТекущиеДанные.Product);
    КонецЕсли;

    // Example: Cancel editing conditionally
    // Отказ = Истина; // Uncomment to prevent row editing
КонецПроцедуры

// ========================================
// Command Handlers
// ========================================

// TestCommand - Test button command
&НаКлиенте
Процедура TestCommandКнопка(Команда)
    Сообщить("Test button clicked!");
    Сообщить("Username: " + Объект.Username);
    Сообщить("Description (multi-line): " + Объект.Description);
    Сообщить("Password: " + Строка(СтрДлина(Объект.Password)) + " characters");
    Сообщить("Selected value: " + Объект.SelectedValue);
    Сообщить("Items count: " + Строка(Объект.Items.Количество()));
КонецПроцедуры
