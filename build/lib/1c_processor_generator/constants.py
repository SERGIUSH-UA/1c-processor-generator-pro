   

                                                                              
                                                            
                                                               
                                                                              

from ._protected import (
                                              
    CLASS_ID_EXTERNAL_DATA_PROCESSOR,
    CLASS_ID_EXTERNAL_REPORT,
                                          
    get_xml_namespaces,
    get_form_xml_namespaces,
    get_type_mapping,
    get_element_suffixes,
    get_class_id,
                                          
    get_element_submenu_xml,
    get_data_path_xml,
    get_table_data_path_xml,
    get_line_number_data_path_xml,
    get_element_id_increment,
    get_element_structure,
                                            
    get_embedded_template,
    has_embedded_templates,
                                
    is_bsp_pro_feature,
)

                                                 
                                           
XML_NAMESPACES = get_xml_namespaces()
FORM_XML_NAMESPACES = get_form_xml_namespaces()
TYPE_MAPPING = get_type_mapping()
ELEMENT_SUFFIXES = get_element_suffixes()

                                                                              
                           
                                                                              
                                                                       
                         
                         
                            
                          
                        
                             
                                         
                                        
                                             
 
                                                                 
                                     
                                                                       
                                                                              

                    
AUTO_COMMAND_BAR_ID = -1             

                                                                     
                                                                

                     
                                                                              
                                                                                 
PLATFORM_VERSIONS = {
    "8.3.23": "2.10",                            
    "8.3.24": "2.10",
    "8.3.25": "2.11",                                        
    "8.3.26": "2.18",                         
    "8.3.27": "2.18",
                                                                            
                                                               
}

                  
ENCODING_UTF8_BOM = "utf-8-sig"                              

                                 
EMPTY_BSL_TEMPLATE = "//ПУСТО"

                               
OBJECT_MODULE_TEMPLATE = """
#Область ПрограммныйИнтерфейс

// Публичные функции

#КонецОбласти

#Область СлужебныеПроцедурыИФункции

// Вспомогательные функции

#КонецОбласти
""".strip()

                             
FORM_MODULE_TEMPLATE = """
#Область ОбработчикиСобытийФормы

// Обработчики событий формы

#КонецОбласти

#Область ОбработчикиСобытийЭлементовШапкиФормы

// Обработчики событий элементов формы

#КонецОбласти

#Область ОбработчикиКомандФормы

// Обработчики команд формы

#КонецОбласти

#Область СлужебныеПроцедурыИФункции

// Вспомогательные функции

#КонецОбласти
""".strip()

                              
DEFAULT_FORM_NAME = "Форма"

      
LANGUAGES = ["ru", "uk", "en"]
DEFAULT_LANGUAGE = "ru"

                                                                    
VALID_STD_PICTURES = {
    "StdPicture.AccumulationRegister",
    "StdPicture.ActiveUsers",
    "StdPicture.AddToFavorites",
    "StdPicture.AppearanceExclamationMarkIcon",
    "StdPicture.Attach",
    "StdPicture.Attribute",
    "StdPicture.Back",
    "StdPicture.BusinessProcessStart",
    "StdPicture.CancelSearch",
    "StdPicture.Catalog",
    "StdPicture.Change",
    "StdPicture.ChangeListItem",
    "StdPicture.CheckAll",
    "StdPicture.CheckSyntax",
    "StdPicture.ChooseValue",
    "StdPicture.ClearFilter",
    "StdPicture.CloneListItem",
    "StdPicture.CloneObject",
    "StdPicture.Close",
    "StdPicture.CollaborationSystemUser",
    "StdPicture.CollapseAll",
    "StdPicture.CreateFolder",
    "StdPicture.CreateInitialImage",
    "StdPicture.CreateListItem",
    "StdPicture.CustomizeForm",
    "StdPicture.CustomizeList",
    "StdPicture.DataCompositionConditionalAppearance",
    "StdPicture.DataCompositionDataParameters",
    "StdPicture.DataCompositionFilter",
    "StdPicture.DataCompositionGroupFields",
    "StdPicture.DataCompositionNewChart",
    "StdPicture.DataCompositionNewGroup",
    "StdPicture.DataCompositionNewNestedScheme",
    "StdPicture.DataCompositionNewTable",
    "StdPicture.DataCompositionOrder",
    "StdPicture.DataCompositionOutputParameters",
    "StdPicture.DataCompositionSelection",
    "StdPicture.DataCompositionSettingsWizard",
    "StdPicture.DataCompositionStandardSettings",
    "StdPicture.DataCompositionUserFields",
    "StdPicture.DataHistory",
    "StdPicture.DebitCredit",
    "StdPicture.Delete",
    "StdPicture.DeleteDirectly",
    "StdPicture.Document",
    "StdPicture.DocumentJournal",
    "StdPicture.EndEdit",
    "StdPicture.EventLog",
    "StdPicture.EventLogByUser",
    "StdPicture.ExchangePlan",
    "StdPicture.ExecuteTask",
    "StdPicture.ExpandAll",
    "StdPicture.ExternalDataSourceTable",
    "StdPicture.FilterByCurrentValue",
    "StdPicture.FilterCriterion",
    "StdPicture.Find",
    "StdPicture.FindInList",
    "StdPicture.FindNext",
    "StdPicture.FindPrevious",
    "StdPicture.Form",
    "StdPicture.FormHelp",
    "StdPicture.Forward",
    "StdPicture.GenerateReport",
    "StdPicture.GetURL",
    "StdPicture.GoBack",
    "StdPicture.GroupConversation",
    "StdPicture.Information",
    "StdPicture.InformationRegister",
    "StdPicture.InputFieldCalculator",
    "StdPicture.InputFieldCalendar",
    "StdPicture.InputFieldChooseType",
    "StdPicture.InputFieldClear",
    "StdPicture.InputFieldOpen",
    "StdPicture.InputFieldSelect",
    "StdPicture.InputOnBasis",
    "StdPicture.ListSettings",
    "StdPicture.ListViewMode",
    "StdPicture.ListViewModeHierarchicalList",
    "StdPicture.ListViewModeList",
    "StdPicture.ListViewModeTree",
    "StdPicture.LoadReportSettings",
    "StdPicture.MarkToDelete",
    "StdPicture.MoveDown",
    "StdPicture.MoveItem",
    "StdPicture.MoveLeft",
    "StdPicture.MoveRight",
    "StdPicture.MoveUp",
    "StdPicture.Notifications",
    "StdPicture.OpenFile",
    "StdPicture.Picture",
    "StdPicture.Post",
    "StdPicture.Print",
    "StdPicture.PrintImmediately",
    "StdPicture.Properties",
    "StdPicture.QueryWizard",
    "StdPicture.QueryWizardCreateTempTableDropQuery",
    "StdPicture.ReadChanges",
    "StdPicture.Refresh",
    "StdPicture.Replace",
    "StdPicture.Report",
    "StdPicture.ReportSettings",
    "StdPicture.Reread",
    "StdPicture.RestoreValues",
    "StdPicture.SaveFile",
    "StdPicture.SaveReportSettings",
    "StdPicture.SaveValues",
    "StdPicture.ScheduledJob",
    "StdPicture.ScheduledJobs",
    "StdPicture.SelectAll",
    "StdPicture.SetDateInterval",
    "StdPicture.SetListItemDeletionMark",
    "StdPicture.SetTime",
    "StdPicture.SettingsStorage",
    "StdPicture.ShowData",
    "StdPicture.ShowInList",
    "StdPicture.SortListAsc",
    "StdPicture.SortListDesc",
    "StdPicture.SpreadsheetReadOnly",
    "StdPicture.Stop",
    "StdPicture.SyncContents",
    "StdPicture.UncheckAll",
    "StdPicture.UndoPosting",
    "StdPicture.UnselectAll",
    "StdPicture.User",
    "StdPicture.UserWithAuthentication",
    "StdPicture.UserWithoutNecessaryProperties",
    "StdPicture.Write",
    "StdPicture.WriteAndClose",
    "StdPicture.WriteChanges",
}

                                                                           
                                                  
BSL_RESERVED_KEYWORDS = {
                                  
    "Процедура", "Функция", "КонецПроцедуры", "КонецФункции",
    "Procedure", "Function", "EndProcedure", "EndFunction",

                      
    "Если", "Тогда", "Иначе", "ИначеЕсли", "КонецЕсли",
    "If", "Then", "Else", "ElsIf", "EndIf",

           
    "Для", "Каждого", "Из", "По", "Цикл", "КонецЦикла",
    "Пока",
    "For", "Each", "In", "To", "Do", "While", "EndDo",

                      
    "Попытка", "Исключение", "КонецПопытки", "ВызватьИсключение",
    "Try", "Except", "EndTry", "Raise",

                          
    "Прервать", "Продолжить", "Возврат",
    "Break", "Continue", "Return",

                      
    "Новый", "Неопределено", "Истина", "Ложь", "NULL",
    "New", "Undefined", "True", "False",

                  
    "Экспорт", "Знач", "Перем",
    "Export", "Val", "Var",

                       
    "И", "Или", "Не",
    "And", "Or", "Not",

                                                                   
    "Выполнить",                                         
    "Вычислить",                                
    "Execute",
    "Eval",

                         
    "Перейти", "Goto",
}

                                                                    
                                                        
FORM_BUILTIN_METHODS = {
                             
    "Закрыть", "Close",                                   
    "Открыть", "Open",                                     
    "ОткрытьМодально", "OpenModal",                           
    "Модифицированность", "Modified",                             
    "ПолучитьФорму", "GetForm",                            
    "Активизировать", "Activate",                            
    "ОбновитьОтображениеДанных", "RefreshDataRepresentation",                        
    "ПоказатьЗначение", "ShowValue",                          
    "ПоказатьВводЧисла", "ShowInputNumber",                          
    "ПоказатьВводДаты", "ShowInputDate",                           
    "ПоказатьВводСтроки", "ShowInputString",                          
    "УстановитьВидимость", "SetVisible",                         
    "УстановитьДоступность", "SetEnabled",                         
}

                                       
                                                                              
                                                                    
STANDARD_FORM_COMMANDS = {
    "Close",                    
    "Cancel",               
    "Help",               
    "OK",            
                                                          
}

                                                                              
                                                    
                                                                              
                                                                                     
                                            
 
                                                                      
                                                                   
