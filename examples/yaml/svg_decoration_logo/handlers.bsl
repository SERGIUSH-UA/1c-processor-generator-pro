//=============================================================================
// Handlers for SVG Logo Example
//=============================================================================

#Область Документация
// Пример использования PictureDecoration с SVG файлами
//
// v2.23.0+: SVG files automatically converted to local PNG pictures
// Structure: Forms/{FormName}/Ext/Form/Items/{ElementName}/Picture.png
#КонецОбласти

#Область ОбработчикиКоманд

&НаКлиенте
Процедура ShowMessageHandler(Команда)
	Если ПустаяСтрока(Объект.Message) Тогда
		Сообщить("Введите сообщение!");
	Иначе
		Сообщить(Объект.Message);
	КонецЕсли;
КонецПроцедуры

#КонецОбласти
