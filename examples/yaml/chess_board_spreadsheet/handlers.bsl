// Chess Board - SpreadsheetDocument variant
// Programmatic cell-by-cell coloring

#Область ОбработчикиСобытийФормы

&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
    InitBoard();
КонецПроцедуры

#КонецОбласти

#Область ОбработчикиКомандФормы

&НаКлиенте
Процедура NewGame(Команда)
    InitBoardНаСервере();
КонецПроцедуры

#КонецОбласти

#Область СлужебныеПроцедурыИФункции

&НаСервере
Процедура InitBoard()
    Doc = Новый ТабличныйДокумент;

    // Colors
    WhiteColor = Новый Цвет(245, 245, 220);  // Beige
    BlackColor = Новый Цвет(139, 69, 19);    // SaddleBrown
    WhiteText = Новый Цвет(0, 0, 0);         // Black text
    BlackText = Новый Цвет(255, 255, 255);   // White text

    // Font for pieces
    PieceFont = Новый Шрифт(, 24, Истина);

    // Column headers (A-H)
    Для Col = 1 По 8 Цикл
        Cell = Doc.Область(1, Col + 1);
        Cell.Текст = Сред("ABCDEFGH", Col, 1);
        Cell.ГоризонтальноеПоложение = ГоризонтальноеПоложение.Центр;
        Cell.ШиринаКолонки = 6;
    КонецЦикла;

    // Row headers (8-1) and board cells
    Для Row = 1 По 8 Цикл
        RowNum = 9 - Row;  // 8,7,6,5,4,3,2,1

        // Row number header
        Cell = Doc.Область(Row + 1, 1);
        Cell.Текст = Строка(RowNum);
        Cell.ГоризонтальноеПоложение = ГоризонтальноеПоложение.Центр;
        Cell.ВысотаСтроки = 25;

        // Board cells
        Для Col = 1 По 8 Цикл
            Cell = Doc.Область(Row + 1, Col + 1);

            // Alternating colors
            IsWhite = ((Row + Col) % 2 = 0);
            Если IsWhite Тогда
                Cell.ЦветФона = WhiteColor;
                Cell.ЦветТекста = WhiteText;
            Иначе
                Cell.ЦветФона = BlackColor;
                Cell.ЦветТекста = BlackText;
            КонецЕсли;

            Cell.Шрифт = PieceFont;
            Cell.ГоризонтальноеПоложение = ГоризонтальноеПоложение.Центр;
            Cell.ВертикальноеПоложение = ВертикальноеПоложение.Центр;
        КонецЦикла;
    КонецЦикла;

    // Place pieces
    // Black pieces (row 8 = doc row 2)
    SetCell(Doc, 2, 2, "♜");  // A8 Rook
    SetCell(Doc, 2, 3, "♞");  // B8 Knight
    SetCell(Doc, 2, 4, "♝");  // C8 Bishop
    SetCell(Doc, 2, 5, "♛");  // D8 Queen
    SetCell(Doc, 2, 6, "♚");  // E8 King
    SetCell(Doc, 2, 7, "♝");  // F8 Bishop
    SetCell(Doc, 2, 8, "♞");  // G8 Knight
    SetCell(Doc, 2, 9, "♜");  // H8 Rook

    // Black pawns (row 7 = doc row 3)
    Для Col = 2 По 9 Цикл
        SetCell(Doc, 3, Col, "♟");
    КонецЦикла;

    // White pawns (row 2 = doc row 8)
    Для Col = 2 По 9 Цикл
        SetCell(Doc, 8, Col, "♙");
    КонецЦикла;

    // White pieces (row 1 = doc row 9)
    SetCell(Doc, 9, 2, "♖");  // A1 Rook
    SetCell(Doc, 9, 3, "♘");  // B1 Knight
    SetCell(Doc, 9, 4, "♗");  // C1 Bishop
    SetCell(Doc, 9, 5, "♕");  // D1 Queen
    SetCell(Doc, 9, 6, "♔");  // E1 King
    SetCell(Doc, 9, 7, "♗");  // F1 Bishop
    SetCell(Doc, 9, 8, "♘");  // G1 Knight
    SetCell(Doc, 9, 9, "♖");  // H1 Rook

    BoardDoc = Doc;
КонецПроцедуры

&НаСервере
Процедура InitBoardНаСервере()
    InitBoard();
КонецПроцедуры

&НаСервере
Процедура SetCell(Doc, Row, Col, Piece)
    Cell = Doc.Область(Row, Col);
    Cell.Текст = Piece;
КонецПроцедуры

#КонецОбласти
