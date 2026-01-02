// Chess Board - Table variant
// 8 columns representing chess board cells

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
    Объект.Board.Очистить();

    // Create 8 rows (chess board rows 8 to 1, top to bottom)
    Для RowIdx = 1 По 8 Цикл
        NewRow = Объект.Board.Добавить();
        NewRow.RowNum = 9 - RowIdx; // 8,7,6,5,4,3,2,1

        // Set cell colors (alternating pattern)
        // Row 8: white starts at A8, Row 7: black starts at A7, etc.
        BaseWhite = (RowIdx % 2 = 1);

        NewRow.Col1White = BaseWhite;
        NewRow.Col2White = НЕ BaseWhite;
        NewRow.Col3White = BaseWhite;
        NewRow.Col4White = НЕ BaseWhite;
        NewRow.Col5White = BaseWhite;
        NewRow.Col6White = НЕ BaseWhite;
        NewRow.Col7White = BaseWhite;
        NewRow.Col8White = НЕ BaseWhite;

        // Initialize empty cells
        NewRow.Col1 = "";
        NewRow.Col2 = "";
        NewRow.Col3 = "";
        NewRow.Col4 = "";
        NewRow.Col5 = "";
        NewRow.Col6 = "";
        NewRow.Col7 = "";
        NewRow.Col8 = "";
    КонецЦикла;

    // Place pieces
    // Row 8 (index 0): Black pieces
    SetPieces(0, "♜", "♞", "♝", "♛", "♚", "♝", "♞", "♜");
    // Row 7 (index 1): Black pawns
    SetPawns(1, "♟");
    // Row 2 (index 6): White pawns
    SetPawns(6, "♙");
    // Row 1 (index 7): White pieces
    SetPieces(7, "♖", "♘", "♗", "♕", "♔", "♗", "♘", "♖");
КонецПроцедуры

&НаСервере
Процедура InitBoardНаСервере()
    InitBoard();
КонецПроцедуры

&НаСервере
Процедура SetPieces(RowIndex, P1, P2, P3, P4, P5, P6, P7, P8)
    Row = Объект.Board[RowIndex];
    Row.Col1 = P1;
    Row.Col2 = P2;
    Row.Col3 = P3;
    Row.Col4 = P4;
    Row.Col5 = P5;
    Row.Col6 = P6;
    Row.Col7 = P7;
    Row.Col8 = P8;
КонецПроцедуры

&НаСервере
Процедура SetPawns(RowIndex, Pawn)
    Row = Объект.Board[RowIndex];
    Row.Col1 = Pawn;
    Row.Col2 = Pawn;
    Row.Col3 = Pawn;
    Row.Col4 = Pawn;
    Row.Col5 = Pawn;
    Row.Col6 = Pawn;
    Row.Col7 = Pawn;
    Row.Col8 = Pawn;
КонецПроцедуры

#КонецОбласти
