#Область ОбработчикиСобытийФормы

// Обработчики событий формы

#КонецОбласти

#Область ОбработчикиСобытийЭлементовШапкиФормы

// Обработчики событий элементов формы

#КонецОбласти

#Область ОбработчикиКомандФормы

&НаКлиенте
Процедура MoveUpHandler(Команда)

    Direction = "Up";
    UpdateStatus("Moving Up");

КонецПроцедуры

&НаКлиенте
Процедура MoveDownHandler(Команда)

    Direction = "Down";
    UpdateStatus("Moving Down");

КонецПроцедуры

&НаКлиенте
Процедура MoveLeftHandler(Команда)

    Direction = "Left";
    UpdateStatus("Moving Left");

КонецПроцедуры

&НаКлиенте
Процедура MoveRightHandler(Команда)

    Direction = "Right";
    UpdateStatus("Moving Right");

КонецПроцедуры

&НаКлиенте
Процедура StartGameHandler(Команда)

    Status = "Running";
    Score = 0;
    UpdateStatus("Game Started");

КонецПроцедуры

&НаКлиенте
Процедура PauseGameHandler(Команда)

    Если Status = "Running" Тогда
        Status = "Paused";
        UpdateStatus("Game Paused");
    ИначеЕсли Status = "Paused" Тогда
        Status = "Running";
        UpdateStatus("Game Resumed");
    КонецЕсли;

КонецПроцедуры

&НаКлиенте
Процедура RestartGameHandler(Команда)

    Direction = "";
    Status = "Ready";
    Score = 0;
    UpdateStatus("Game Reset");

КонецПроцедуры

&НаКлиенте
Процедура SaveStateHandler(Команда)

    // In real app: save state to file or database
    UpdateStatus("State Saved");
    Сообщить("Состояние сохранено / State saved");

КонецПроцедуры

&НаКлиенте
Процедура LoadStateHandler(Команда)

    // In real app: load state from file or database
    UpdateStatus("State Loaded");
    Сообщить("Состояние загружено / State loaded");

КонецПроцедуры

#КонецОбласти


#Область СлужебныеПроцедурыИФункции

&НаКлиенте
Процедура UpdateStatus(Message)

    // Update UI or show message
    Сообщить(Message);

КонецПроцедуры

#КонецОбласти