// ============================================================================
// Form Parameters Example (v2.36.0+ Phase 2)
// Demonstrates:
// 1. Opening form with parameters (OpenFilter command)
// 2. Receiving parameters in form (FilterFormOnOpen event)
// 3. Returning data back to main form (ApplyFilter command)
// ============================================================================

// ============ Main Form Commands ============

&НаКлиенте
Процедура OpenFilter(Команда)
	// Open filter form with parameters
	// Form parameters are passed as structure

	ПараметрыФормы = Новый Структура;
	ПараметрыФормы.Вставить("ПараметрДата", ТекущаяДата());
	ПараметрыФормы.Вставить("ПараметрРежим", Истина);
	ПараметрыФормы.Вставить("ПараметрРегион", "Центральный");

	// Open form and handle result
	ОписаниеОповещения = Новый ОписаниеОповещения("FilterFormClosed", ЭтотОбъект);

	ОткрытьФорму(
		"ВнешняяОбработка." + Объект.Ссылка + ".Форма.ФормаФильтра",
		ПараметрыФормы,
		ЭтаФорма,
		,
		,
		,
		ОписаниеОповещения
	);
КонецПроцедуры

&НаКлиенте
Процедура FilterFormClosed(Результат, ДополнительныеПараметры) Экспорт
	// Called when filter form is closed
	Если Результат <> Неопределено Тогда
		// Display result
		Объект.ReportData = "Фильтр применен!" + Символы.ПС +
			"Дата: " + Формат(Результат.FilterDate, "ДФ=dd.MM.yyyy") + Символы.ПС +
			"Режим просмотра: " + ?(Результат.ViewMode, "Да", "Нет") + Символы.ПС +
			"Регион: " + Результат.DefaultRegion;
	Иначе
		Объект.ReportData = "Отмена";
	КонецЕсли;
КонецПроцедуры

// ============ Filter Form Events ============

&НаСервере
Процедура FilterFormOnCreateAtServer(Отказ, СтандартнаяОбработка)
	// Copy parameters to form attributes
	// Parameters are read-only, so we copy them to editable attributes
	FilterDate = Параметры.ПараметрДата;
	ViewMode = Параметры.ПараметрРежим;
	DefaultRegion = Параметры.ПараметрРегион;
КонецПроцедуры

&НаКлиенте
Процедура FilterFormOnOpen(Отказ)
	// ✨ NEW (v2.36.0+): Parameters are available as form attributes
	// They were passed when opening the form

	// Display received parameters
	Сообщить("Форма фильтра открыта с параметрами:");
	Сообщить("  FilterDate (key parameter): " + Формат(FilterDate, "ДФ=dd.MM.yyyy"));
	Сообщить("  ViewMode: " + ?(ViewMode, "Да", "Нет"));
	Сообщить("  DefaultRegion: " + DefaultRegion);

	// Parameters are automatically mapped to form attributes
	// No manual assignment needed!
КонецПроцедуры

// ============ Filter Form Commands ============

&НаКлиенте
Процедура ApplyFilter(Команда)
	// Return selected values to main form
	РезультатВыбора = Новый Структура;
	РезультатВыбора.Вставить("FilterDate", FilterDate);
	РезультатВыбора.Вставить("ViewMode", ViewMode);
	РезультатВыбора.Вставить("DefaultRegion", DefaultRegion);

	Закрыть(РезультатВыбора);
КонецПроцедуры

&НаКлиенте
Процедура CancelFilter(Команда)
	// Cancel - close without result
	Закрыть(Неопределено);
КонецПроцедуры
