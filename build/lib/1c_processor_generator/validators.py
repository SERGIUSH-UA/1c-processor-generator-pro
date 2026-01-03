   

import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Set
from difflib import get_close_matches
from .constants import VALID_STD_PICTURES, BSL_RESERVED_KEYWORDS, FORM_BUILTIN_METHODS

                                                                                                   
RESERVED_METADATA_NAMES = {
                                                     
    "Документы",
    "Справочники",
    "Регистры",
    "Перечисления",
    "Отчеты",
    "Обработки",
    "ПланыВидовХарактеристик",
    "ПланыСчетов",
    "ПланыВидовРасчета",
    "БизнесПроцессы",
    "Задачи",
    "ОбменДанными",
    "ХранилищаНастроек",
                        
    "Параметры",
    "ДополнительныеСвойства",
    "Ссылка",                                                
    "ПометкаУдаления",
    "Предопределенный",
    "Владелец",
    "Родитель",
}


class ValidationError(Exception):
                           
    pass


def validate_uuid(uuid: str) -> Tuple[bool, str]:
           
                                                           
                                 
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

    if not re.match(uuid_pattern, uuid.lower()):
                                        
        invalid_chars = set(re.findall(r'[^0-9a-f\-]', uuid.lower()))
        if invalid_chars:
            return False, f"UUID містить невалідні символи: {', '.join(invalid_chars)}. Дозволені тільки 0-9, a-f"
        return False, "UUID має невірний формат. Очікується: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    return True, ""


def validate_identifier(name: str) -> Tuple[bool, str]:
           
    if not name:
        return False, "Ім'я не може бути порожнім"

                               
    if not re.match(r'^[а-яА-ЯёЁa-zA-Z_]', name):
        return False, f"Ім'я '{name}' повинно починатися з букви або підкреслення"

                              
    if not re.match(r'^[а-яА-ЯёЁa-zA-Z0-9_]+$', name):
        invalid_chars = set(re.findall(r'[^а-яА-ЯёЁa-zA-Z0-9_]', name))
        return False, f"Ім'я '{name}' містить невалідні символи: {', '.join(invalid_chars)}"

    return True, ""


def validate_id_sequence(ids: List[int]) -> Tuple[bool, str]:
           
    if -1 not in ids:
        return False, "Відсутній AutoCommandBar з id=-1"

    positive_ids = [id for id in ids if id > 0]

    if len(positive_ids) != len(set(positive_ids)):
        duplicates = [id for id in positive_ids if positive_ids.count(id) > 1]
        return False, f"Знайдені дубльовані ID: {set(duplicates)}"

    return True, ""


def validate_type(type_str: str) -> Tuple[bool, str]:
           
    valid_base_types = ["xs:string", "xs:boolean", "xs:decimal", "xs:dateTime"]

                 
    if type_str in valid_base_types:
        return True, ""

                                                                                          
    if type_str in ["string", "boolean", "number", "date", "spreadsheet_document"]:
        return True, ""

                      
    if type_str.startswith("cfg:CatalogRef.") or type_str.startswith("CatalogRef."):
        return True, ""

               
    if type_str.startswith("cfg:DocumentRef.") or type_str.startswith("DocumentRef."):
        return True, ""

    return False, f"Невідомий тип даних: {type_str}"


def validate_processor_name(name: str) -> Tuple[bool, str]:
           
    is_valid, error = validate_identifier(name)
    if not is_valid:
        return False, error

                          
    if ' ' in name:
        return False, f"Назва обробки '{name}' не повинна містити пробіли. Використовуйте PascalCase"

                                                   
    if not name[0].isupper():
        return False, f"Назва обробки '{name}' має починатися з великої літери (PascalCase)"

    return True, ""


def validate_all_uuids(uuids: List[str]) -> List[str]:
           
    errors = []

    for i, uuid in enumerate(uuids):
        is_valid, error = validate_uuid(uuid)
        if not is_valid:
            errors.append(f"UUID #{i+1}: {error}")

                               
    if len(uuids) != len(set(uuids)):
        duplicates = [uuid for uuid in uuids if uuids.count(uuid) > 1]
        errors.append(f"Знайдені дубльовані UUID: {set(duplicates)}")

    return errors


def validate_length_for_string(length: int) -> Tuple[bool, str]:
                                            
    if length <= 0:
        return False, "Довжина рядка має бути > 0"
    if length > 1024:
        return False, "Довжина рядка не може перевищувати 1024 (рекомендація 1C)"
    return True, ""


def validate_number_qualifiers(digits: int, fraction_digits: int) -> Tuple[bool, str]:
                                                  
    if digits <= 0:
        return False, "Загальна кількість цифр має бути > 0"
    if fraction_digits < 0:
        return False, "Кількість десяткових знаків не може бути < 0"
    if fraction_digits >= digits:
        return False, "Кількість десяткових знаків має бути < загальної кількості цифр"
    if digits > 38:
        return False, "Загальна кількість цифр не може перевищувати 38 (обмеження 1C)"
    return True, ""


def validate_picture(picture: str) -> Tuple[bool, str]:
           
    if not picture:
        return True, ""                        

                          
    if picture.startswith("StdPicture."):
        if picture in VALID_STD_PICTURES:
            return True, ""

                                                        
        suggestions = get_close_matches(
            picture,
            VALID_STD_PICTURES,
            n=5,                              
            cutoff=0.4                                          
        )

        if suggestions:
                                                          
            suggestions_str = "\n    ".join(suggestions)
            return False, (
                f"Невідома стандартна картинка: {picture}\n\n"
                f"💡 Схожі валідні картинки:\n"
                f"    {suggestions_str}\n\n"
                f"Повний список: docs/VALID_PICTURES.md або constants.VALID_STD_PICTURES"
            )
        else:
                                                     
            return False, (
                f"Невідома стандартна картинка: {picture}\n\n"
                f"Не знайдено схожих варіантів. Можливо, ви мали на увазі:\n"
                f"    StdPicture.ExecuteTask (виконати)\n"
                f"    StdPicture.SaveFile (зберегти)\n"
                f"    StdPicture.OpenFile (відкрити)\n"
                f"    StdPicture.Refresh (оновити)\n\n"
                f"Повний список: docs/VALID_PICTURES.md"
            )

                                                                                       
    if picture.startswith("CommonPicture."):
        return True, ""

    return False, (
        f"Невірний формат картинки: {picture}. "
        f"Очікується StdPicture.* або CommonPicture.*"
    )


def validate_choice_list(choice_list: list, context: str) -> Tuple[bool, str]:
           
    if not choice_list:
        return True, ""

    if not isinstance(choice_list, list):
        return False, (
            f"{context}: choice_list має бути списком, отримано {type(choice_list).__name__}"
        )

    for i, item in enumerate(choice_list):
        if isinstance(item, str):
            return False, (
                f"{context}: choice_list[{i}] має бути об'єктом { v, ru} , отримано рядок \"{item}\"\n\n"
                f"💡 Правильний формат (v2.69.0+):\n"
                f"    choice_list:\n"
                f"      - v: \"Value\"     # значення (без пробілів)\n"
                f"        ru: \"Опис\"     # відображення\n"
                f"        uk: \"Опис\"     # опціонально"
            )

        if not isinstance(item, dict):
            return False, (
                f"{context}: choice_list[{i}] має бути об'єктом, отримано {type(item).__name__}"
            )

                                       
        if 'v' not in item:
                                             
            if 'value' in item:
                return False, (
                    f"{context}: choice_list[{i}] використовує застарілий ключ 'value'\n\n"
                    f"💡 Новий формат (v2.69.0+):\n"
                    f"    - v: \"{item.get('value', '')}\"     # замість 'value'\n"
                    f"      ru: \"...\"                        # замість 'presentation_ru'"
                )
            return False, (
                f"{context}: choice_list[{i}] відсутній обов'язковий ключ 'v' (value)"
            )

                                                
        has_lang = any(item.get(lang) for lang in ['ru', 'uk', 'en'])
        if not has_lang:
                                                       
            if item.get('presentation_ru') or item.get('presentation'):
                return False, (
                    f"{context}: choice_list[{i}] використовує застарілі ключі\n\n"
                    f"💡 Новий формат (v2.69.0+):\n"
                    f"    - v: \"{item.get('v', '')}\"     # value\n"
                    f"      ru: \"...\"                   # замість 'presentation_ru'"
                )
            return False, (
                f"{context}: choice_list[{i}] потрібен мінімум один ключ мови: ru, uk, або en"
            )

                                      
        if not item.get('v') and item.get('v') != 0:                                  
            return False, (
                f"{context}: choice_list[{i}] значення 'v' не може бути порожнім"
            )

    return True, ""


                                              
                                
                                              

                                          
VALID_HORIZONTAL_ALIGN = {"Left", "Right", "Center", "Auto"}
VALID_VERTICAL_ALIGN = {"Top", "Bottom", "Center", "Auto"}
VALID_TITLE_LOCATION = {"None", "Left", "Right", "Top", "Bottom", "Auto"}
VALID_GROUP_DIRECTION = {"Horizontal", "Vertical"}
VALID_REPRESENTATION = {"None", "NormalSeparation", "WeakSeparation", "StrongSeparation"}             
VALID_TABLE_REPRESENTATION = {"list", "tree"}                        
VALID_BEHAVIOR = {"Usual", "Collapsible"}
VALID_RADIO_BUTTON_TYPE = {"RadioButton", "Tumbler"}
VALID_PICTURE_SIZE = {"Proportionally", "Stretch", "AutoSize", "Tile", "RealSize"}
VALID_CHART_TYPE = {"Line", "Area", "StackedArea", "Bar", "Bar3D", "Pie", "Pie3D", "Doughnut", "Radar", "Stock", "Funnel"}

                                 
ENUM_ALIASES = {
                      
    "center": "Center", "middle": "Center", "left": "Left", "right": "Right",
                    
    "top": "Top", "bottom": "Bottom",
                    
    "none": "None", "above": "Top", "below": "Bottom",
                     
    "horizontal": "Horizontal", "vertical": "Vertical", "row": "Horizontal", "column": "Vertical",
                    
    "normal": "NormalSeparation", "weak": "WeakSeparation", "strong": "StrongSeparation",
    "border": "NormalSeparation", "frame": "NormalSeparation",
              
    "collapsible": "Collapsible", "expandable": "Collapsible", "collapse": "Collapsible",
                       
    "radio": "RadioButton", "tumbler": "Tumbler", "switch": "Tumbler", "toggle": "Tumbler",
                  
    "proportionally": "Proportionally", "stretch": "Stretch", "auto": "AutoSize",
    "fit": "Proportionally", "fill": "Stretch", "tile": "Tile",
}


def validate_enum(value: str, valid_values: set, property_name: str, context: str) -> Tuple[bool, str]:
           
    if not value:
        return True, ""

                       
    if value in valid_values:
        return True, ""

                                         
    if value.lower() in ENUM_ALIASES:
        suggested = ENUM_ALIASES[value.lower()]
        if suggested in valid_values:
            return False, (
                f"{context}: {property_name}=\"{value}\" невірне значення\n\n"
                f"💡 Можливо ви мали на увазі: {suggested}\n"
                f"   {property_name}: {suggested}"
            )

                    
    suggestions = get_close_matches(value, valid_values, n=3, cutoff=0.4)
    if suggestions:
        suggestions_str = ", ".join(suggestions)
        return False, (
            f"{context}: {property_name}=\"{value}\" невірне значення\n\n"
            f"💡 Схожі варіанти: {suggestions_str}\n"
            f"   Доступні: {', '.join(sorted(valid_values))}"
        )

    return False, (
        f"{context}: {property_name}=\"{value}\" невірне значення\n\n"
        f"💡 Доступні значення: {', '.join(sorted(valid_values))}"
    )


def validate_font(font, context: str) -> Tuple[bool, str]:
           
    if not font:
        return True, ""

    if isinstance(font, str):
        return False, (
            f"{context}: font має бути об'єктом, отримано рядок \"{font}\"\n\n"
            f"💡 Правильний формат:\n"
            f"    font:\n"
            f"      size: 14\n"
            f"      bold: true"
        )

    if not isinstance(font, dict):
        return False, (
            f"{context}: font має бути об'єктом, отримано {type(font).__name__}"
        )

    valid_keys = {"size", "height", "bold", "italic", "underline", "strikethrough",
                  "scale", "face_name", "faceName", "kind", "ref"}
    unknown_keys = set(font.keys()) - valid_keys
    if unknown_keys:
        suggestions = []
        for key in unknown_keys:
            matches = get_close_matches(key, valid_keys, n=1, cutoff=0.5)
            if matches:
                suggestions.append(f"'{key}' → '{matches[0]}'")

        if suggestions:
            return False, (
                f"{context}: font містить невідомі ключі: {unknown_keys}\n\n"
                f"💡 Можливо ви мали на увазі: {', '.join(suggestions)}\n"
                f"   Доступні: {', '.join(sorted(valid_keys))}"
            )
        return False, (
            f"{context}: font містить невідомі ключі: {unknown_keys}\n\n"
            f"💡 Доступні ключі: {', '.join(sorted(valid_keys))}"
        )

                             
    for bool_key in ["bold", "italic", "underline", "strikethrough"]:
        if bool_key in font and not isinstance(font[bool_key], bool):
            return False, (
                f"{context}: font.{bool_key} має бути boolean (true/false), "
                f"отримано {type(font[bool_key]).__name__}"
            )

    return True, ""


def validate_color(color: str, property_name: str, context: str) -> Tuple[bool, str]:
           
    if not color:
        return True, ""

    if not isinstance(color, str):
        return False, (
            f"{context}: {property_name} має бути рядком у форматі #RRGGBB, "
            f"отримано {type(color).__name__}"
        )

                                    
    named_colors = {"red", "green", "blue", "white", "black", "yellow", "orange", "gray", "grey"}
    if color.lower() in named_colors:
                                 
        color_map = {
            "red": "#FF0000", "green": "#00FF00", "blue": "#0000FF",
            "white": "#FFFFFF", "black": "#000000", "yellow": "#FFFF00",
            "orange": "#FFA500", "gray": "#808080", "grey": "#808080"
        }
        hex_color = color_map.get(color.lower(), "#RRGGBB")
        return False, (
            f"{context}: {property_name}=\"{color}\" - іменовані кольори не підтримуються\n\n"
            f"💡 Використовуйте HEX формат: {hex_color}"
        )

                      
    import re
    if not re.match(r'^#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})$', color):
        return False, (
            f"{context}: {property_name}=\"{color}\" невірний формат кольору\n\n"
            f"💡 Використовуйте HEX формат:\n"
            f"    {property_name}: \"#RRGGBB\"   # повний (напр. #FF5500)\n"
            f"    {property_name}: \"#RGB\"      # скорочений (напр. #F50)"
        )

    return True, ""


def validate_conditional_appearance(ca: dict, index: int, context: str) -> Tuple[bool, str]:
           
    if not ca:
        return True, ""

    if not isinstance(ca, dict):
        return False, (
            f"{context}: conditional_appearances[{index}] має бути об'єктом, "
            f"отримано {type(ca).__name__}"
        )

                         
    if 'filter' not in ca and 'appearance' not in ca:
        return False, (
            f"{context}: conditional_appearances[{index}] потрібен 'filter' або 'appearance'\n\n"
            f"💡 Формат:\n"
            f"    conditional_appearances:\n"
            f"      - filter:\n"
            f"          field: \"Статус\"\n"
            f"          comparison: Equal\n"
            f"          value: \"Ошибка\"\n"
            f"        appearance:\n"
            f"          text_color: \"#FF0000\""
        )

                     
    if 'filter' in ca:
        flt = ca['filter']
        if not isinstance(flt, dict):
            return False, (
                f"{context}: conditional_appearances[{index}].filter має бути об'єктом"
            )

        valid_comparisons = {"Equal", "NotEqual", "Greater", "GreaterOrEqual",
                           "Less", "LessOrEqual", "Contains", "InList", "Filled"}
        if 'comparison' in flt and flt['comparison'] not in valid_comparisons:
            suggestions = get_close_matches(flt['comparison'], valid_comparisons, n=2, cutoff=0.4)
            if suggestions:
                return False, (
                    f"{context}: conditional_appearances[{index}].filter.comparison=\"{flt['comparison']}\" невірне\n\n"
                    f"💡 Можливо: {', '.join(suggestions)}\n"
                    f"   Доступні: {', '.join(sorted(valid_comparisons))}"
                )
            return False, (
                f"{context}: conditional_appearances[{index}].filter.comparison=\"{flt['comparison']}\" невірне\n\n"
                f"💡 Доступні: {', '.join(sorted(valid_comparisons))}"
            )

                         
    if 'appearance' in ca:
        app = ca['appearance']
        if not isinstance(app, dict):
            return False, (
                f"{context}: conditional_appearances[{index}].appearance має бути об'єктом"
            )

                                       
        for color_key in ['text_color', 'back_color', 'border_color']:
            if color_key in app:
                is_valid, error = validate_color(
                    app[color_key],
                    f"appearance.{color_key}",
                    f"{context}: conditional_appearances[{index}]"
                )
                if not is_valid:
                    return False, error

    return True, ""


def validate_handler_name(handler_name: str) -> Tuple[bool, str]:
           
    if not handler_name:
        return True, ""                        

                                                                  
    if handler_name in BSL_RESERVED_KEYWORDS:
        return False, (
            f"Ім'я обробника '{handler_name}' є зарезервованим ключовим словом BSL і не може "
            f"використовуватися як ім'я процедури. "
            f"Використовуйте інше ім'я, наприклад: 'Команда{handler_name}', '{handler_name}Команда', "
            f"'{handler_name}Обработчик', тощо."
        )

                                                                 
    if handler_name in FORM_BUILTIN_METHODS:
        return False, (
            f"Ім'я обробника '{handler_name}' конфліктує з вбудованим методом керованої форми 1C і не може "
            f"використовуватися як ім'я процедури. "
            f"Використовуйте інше ім'я, наприклад: '{handler_name}Форму', '{handler_name}Обработчик', "
            f"'Команда{handler_name}', тощо."
        )

    return True, ""


def validate_reserved_metadata_name(name: str, object_type: str = "об'єкт") -> Tuple[bool, str]:
           
    if not name:
        return True, ""

                                 
    if name in RESERVED_METADATA_NAMES:
        return False, (
            f"Ім'я '{name}' є зарезервованим системним іменем метаданих 1C і не може "
            f"використовуватися як ім'я {object_type}а. "
            f"Використовуйте інше ім'я, наприклад: '{name}Список', 'Мои{name}', "
            f"'{name}Таблица', тощо."
        )

    return True, ""


class ProcessorValidator:
                                                

    def __init__(self, processor):
        self.processor = processor
        self.errors = []
        self.warnings = []

    def _validate_name_and_reserved(self, name: str, context: str, object_type: str = "об'єкт") -> None:
                   
        is_valid, error = validate_identifier(name)
        if not is_valid:
            self.errors.append(f"{context}: {error}")

        is_valid, error = validate_reserved_metadata_name(name, object_type)
        if not is_valid:
            self.errors.append(f"{context}: {error}")

    def _validate_column(self, col_name: str, col_type: str, context: str) -> None:
                   
        is_valid, error = validate_identifier(col_name)
        if not is_valid:
            self.errors.append(f"{context}: {error}")

        is_valid, error = validate_type(col_type)
        if not is_valid:
            self.errors.append(f"{context}: {error}")

    def _validate_handler(self, handler_name: str, context: str) -> None:
                   
        is_valid, error = validate_handler_name(handler_name)
        if not is_valid:
            self.errors.append(f"{context}: {error}")

    def _validate_long_operations(self) -> None:
                   
        for form in self.processor.forms:
            for cmd in form.commands:
                if not cmd.long_operation:
                    continue

                context = f"Форма '{form.name}' - Long operation команда '{cmd.name}'"
                settings = cmd.long_operation_settings

                                          
                if settings and settings.timeout_seconds:
                    if settings.timeout_seconds < 1:
                        self.errors.append(f"{context}: timeout_seconds має бути >= 1 (поточне: {settings.timeout_seconds})")
                    elif settings.timeout_seconds > 3600:
                        self.errors.append(f"{context}: timeout_seconds надто великий (max 3600, поточне: {settings.timeout_seconds})")

                                           
                if settings and settings.show_progress:
                    msg = settings.progress_message
                                                                   
                    is_empty = not msg or (isinstance(msg, str) and msg.strip() == "") or (isinstance(msg, dict) and not any(msg.values()))
                    if is_empty:
                        self.warnings.append(f"{context}: show_progress=True але progress_message порожній")

                                                            
                has_button = any(
                    elem.element_type == "Button" and elem.command == cmd.name
                    for elem in form.elements
                )
                if not has_button:
                    self.warnings.append(
                        f"{context}: long_operation=True але немає Button на формі. "
                        f"Додайте Button з command='{cmd.name}' для виклику операції."
                    )

    def validate(self) -> Tuple[bool, List[str], List[str]]:
                   
        self.errors = []
        self.warnings = []

                         
        is_valid, error = validate_processor_name(self.processor.name)
        if not is_valid:
            self.errors.append(f"Назва обробки: {error}")

                        
        all_uuids = [
            self.processor.main_uuid,
            self.processor.object_id,
            self.processor.type_id,
            self.processor.value_id,
            self.processor.form_uuid,
        ]

                                
        for attr in self.processor.attributes:
            all_uuids.append(attr.uuid)

                                       
        for ts in self.processor.tabular_sections:
            all_uuids.extend([
                ts.uuid,
                ts.type_id,
                ts.value_id,
                ts.row_type_id,
                ts.row_value_id,
            ])
            for col in ts.columns:
                all_uuids.append(col.uuid)

                                     
        for form in self.processor.forms:
            all_uuids.append(form.uuid)
                                       
            for cmd in form.commands:
                all_uuids.append(cmd.uuid)

        uuid_errors = validate_all_uuids(all_uuids)
        self.errors.extend(uuid_errors)

                             
        for attr in self.processor.attributes:
            self._validate_name_and_reserved(attr.name, f"Атрибут '{attr.name}'", "атрибут")

            is_valid, error = validate_type(attr.type)
            if not is_valid:
                self.errors.append(f"Атрибут '{attr.name}': {error}")

                                    
        for ts in self.processor.tabular_sections:
            self._validate_name_and_reserved(ts.name, f"Таблична частина '{ts.name}'", "таблична частин")

            for col in ts.columns:
                self._validate_column(col.name, col.type, f"Колонка '{ts.name}.{col.name}'")

                                                   
        for form in self.processor.forms:
            for vt in form.value_table_attributes:
                self._validate_name_and_reserved(vt.name, f"Форма '{form.name}' - ValueTable '{vt.name}'", "ValueTable атрибут")

                for col in vt.columns:
                    self._validate_column(col.name, col.type, f"Форма '{form.name}' - ValueTable колонка '{vt.name}.{col.name}'")

                                                    
        for form in self.processor.forms:
            for dl in form.dynamic_list_attributes:
                self._validate_name_and_reserved(dl.name, f"Форма '{form.name}' - DynamicList '{dl.name}'", "DynamicList атрибут")

                                                                       
                if dl.use_always_fields:
                                                              
                    has_table = any(
                        elem.element_type == "Table"
                        and elem.properties.get("is_dynamic_list", False)
                        and elem.tabular_section == dl.name
                        for elem in form.elements
                    )
                    if not has_table:
                        self.warnings.append(
                            f"Форма '{form.name}' - DynamicList '{dl.name}': use_always_fields визначено, але немає Table "
                            f"на формі для відображення цього списку. UseAlways буде проігноровано."
                        )

                                                               
        for form in self.processor.forms:
                                       
            for elem in form.elements:
                                                                                        
                if elem.element_type == "Popup":
                    self.warnings.append(
                        f"Форма '{form.name}' - Елемент '{elem.name}': Popup в form.elements буде проігноровано. "
                        "Використовуйте form.auto_command_bar для Popup елементів."
                    )

                                                  
                if 'svg_source' in elem.properties:
                    svg_path = elem.properties['svg_source']
                    context = f"Форма '{form.name}' - Елемент '{elem.name}'"

                                                                                
                    from pathlib import Path
                    svg_file = Path(svg_path)
                    if not svg_file.is_absolute():
                                                                 
                        if hasattr(self.processor, 'config_dir') and self.processor.config_dir:
                            svg_file = Path(self.processor.config_dir) / svg_path

                    if not svg_file.exists():
                        self.errors.append(f"{context}: SVG file not found: {svg_path}")
                    else:
                                                
                        try:
                            from .svg_converter import SVGConverter
                            converter = SVGConverter()
                            converter.validate_svg(str(svg_file))
                        except Exception as e:
                            self.errors.append(f"{context}: Invalid SVG file: {e}")

                                           
            for cmd in form.commands:
                if hasattr(cmd, 'picture') and cmd.picture:
                    is_valid, error = validate_picture(cmd.picture)
                    if not is_valid:
                        self.errors.append(f"Форма '{form.name}' - Команда '{cmd.name}': {error}")

                                                                                         
            self._validate_element_pictures(form.elements, form.name)

                                                                
            self._validate_element_choice_lists(form.elements, form.name)

                                                                                                      
            self._validate_element_properties(form.elements, form.name)

                                                                     
            if hasattr(form, 'conditional_appearances') and form.conditional_appearances:
                context = f"Форма '{form.name}'"
                for i, ca in enumerate(form.conditional_appearances):
                                                                                                
                    if hasattr(ca, 'appearance') and ca.appearance:
                        app = ca.appearance
                        for color_attr in ['text_color', 'back_color', 'border_color']:
                            color_val = getattr(app, color_attr, None)
                            if color_val:
                                is_valid, error = validate_color(
                                    color_val, color_attr,
                                    f"{context}: conditional_appearances[{i}].appearance"
                                )
                                if not is_valid:
                                    self.errors.append(error)

                                                   
        self._validate_long_operations()

                                                         
        for form in self.processor.forms:
                                                                  
            if hasattr(form, 'auto_command_bar') and form.auto_command_bar:
                for elem in form.auto_command_bar:
                    if elem.element_type == "Popup" and hasattr(elem, 'picture') and elem.picture:
                        is_valid, error = validate_picture(elem.picture)
                        if not is_valid:
                            self.errors.append(f"Форма '{form.name}' - Popup '{elem.name}': {error}")

                         
                                          
        form_names = [form.name for form in self.processor.forms]
        if len(form_names) != len(set(form_names)):
            duplicates = [name for name in form_names if form_names.count(name) > 1]
            self.errors.append(
                f"Знайдено дублікати імен форм: {set(duplicates)}. "
                f"Кожна форма повинна мати унікальне ім'я."
            )

                                
        default_forms = [form for form in self.processor.forms if form.default]
        if len(default_forms) == 0:
            self.warnings.append(
                "Жодна форма не позначена як default=True. "
                "Рекомендується позначити одну форму як default."
            )
        elif len(default_forms) > 1:
            default_names = [form.name for form in default_forms]
            self.errors.append(
                f"Декілька форм позначені як default=True: {default_names}. "
                f"Тільки одна форма може бути default."
            )

                                                      
        from pathlib import Path
        for form in self.processor.forms:
            if form.handlers_dir:
                handlers_path = Path(form.handlers_dir)
                if not handlers_path.exists():
                    self.errors.append(
                        f"Форма '{form.name}': handlers_dir не існує: {form.handlers_dir}"
                    )
                elif not handlers_path.is_dir():
                    self.errors.append(
                        f"Форма '{form.name}': handlers_dir не є директорією: {form.handlers_dir}"
                    )

        for form in self.processor.forms:
                                    
            for cmd in form.commands:
                                                                  
                from .constants import STANDARD_FORM_COMMANDS
                if cmd.name in STANDARD_FORM_COMMANDS:
                    self.errors.append(
                        f"Форма '{form.name}' - Команда '{cmd.name}': не можна визначати стандартні команди 1C "
                        f"({', '.join(sorted(STANDARD_FORM_COMMANDS))}). "
                        f"Стандартні команди доступні автоматично і не потребують визначення."
                    )

                self._validate_handler(cmd.action, f"Форма '{form.name}' - Команда '{cmd.name}'")

                                   
            for event_name, handler_name in form.events.items():
                self._validate_handler(handler_name, f"Форма '{form.name}' - Подія '{event_name}'")

                                             
            for elem in form.elements:
                if hasattr(elem, 'event_handlers') and elem.event_handlers:
                    for event_name, handler_name in elem.event_handlers.items():
                        self._validate_handler(handler_name, f"Форма '{form.name}' - Елемент '{elem.name}.{event_name}'")

                                
        om_errors, om_warnings = self._validate_object_module()
        self.errors.extend(om_errors)
        self.warnings.extend(om_warnings)

                                           
        fm_errors, fm_warnings = self._validate_form_modules()
        self.errors.extend(fm_errors)
        self.warnings.extend(fm_warnings)

                      
        if not self.processor.attributes and not self.processor.tabular_sections:
            self.warnings.append("Обробка не має жодного реквізиту або табличної частини")

                                                       
        has_any_elements = any(form.elements for form in self.processor.forms)
        if not has_any_elements:
            self.warnings.append("Форма не має жодного елемента")

        return len(self.errors) == 0, self.errors, self.warnings

    def _validate_bsl_code(self, code: str, module_name: str) -> Tuple[List[str], List[str]]:
                   
        errors = []
        warnings = []

        if not code or not code.strip():
            return errors, warnings

                                              
        pattern = re.compile(
            r'^\s*(?:&\w+\s+)?(?:Процедура|Функция|Procedure|Function|Асинх|Async)\s+(\w+)',
            re.MULTILINE | re.IGNORECASE
        )
        procedures = pattern.findall(code)

                                            
        for proc_name in procedures:
            if proc_name in BSL_RESERVED_KEYWORDS:
                errors.append(
                    f"{module_name}: процедура '{proc_name}' конфліктує з зарезервованим словом BSL"
                )

                                                                  
                                                                              
        ukrainian_pattern = re.compile(r'[іІїЇєЄґҐ]')
        for proc_name in procedures:
            if ukrainian_pattern.search(proc_name):
                errors.append(
                    f"{module_name}: процедура '{proc_name}' містить українські літери (і, ї, є, ґ). "
                    f"Використовуйте тільки латиницю або російську кирилицю для назв процедур."
                )

        return errors, warnings

    def _validate_object_module(self) -> Tuple[List[str], List[str]]:
                   
        errors = []
        warnings = []

        if not self.processor.object_module_bsl:
            return errors, warnings

        code = self.processor.object_module_bsl

                                     
        if not code.strip():
            errors.append("ObjectModule.bsl порожній")
            return errors, warnings

                                                                      
        bsl_errors, bsl_warnings = self._validate_bsl_code(code, "ObjectModule")
        errors.extend(bsl_errors)
        warnings.extend(bsl_warnings)

                                                          
        if "#Если" not in code and "#If" not in code:
            warnings.append(
                "ObjectModule: немає умовної компіляції (#Если Сервер Або ТолстыйКлиентОбычноеПриложение Или ВнешнееСоединение Тогда). "
                "Рекомендується додати для коректної роботи."
            )

                                             
        if "#Область" not in code and "#Region" not in code:
            warnings.append(
                "ObjectModule: немає регіонів (#Область). "
                "Рекомендується структурувати код за регіонами (#Область ПрограммныйИнтерфейс, #Область СлужебныеПроцедурыИФункции)."
            )

        return errors, warnings

    def _validate_element_pictures(self, elements, form_name: str, parent_path: str = "") -> None:
                   
        if not elements:
            return

        for elem in elements:
            elem_path = f"{parent_path}/{elem.name}" if parent_path else elem.name

                                                              
            if elem.element_type in ("PictureDecoration", "Button"):
                picture = elem.properties.get('picture') if elem.properties else None
                if picture:
                    is_valid, error = validate_picture(picture)
                    if not is_valid:
                        self.errors.append(f"Форма '{form_name}' - {elem.element_type} '{elem_path}': {error}")

                                                              
            if elem.child_items:
                self._validate_element_pictures(elem.child_items, form_name, elem_path)

    def _validate_element_choice_lists(self, elements, form_name: str, parent_path: str = "") -> None:
                   
        if not elements:
            return

        for elem in elements:
            elem_path = f"{parent_path}/{elem.name}" if parent_path else elem.name

                                                                    
            if elem.element_type in ("InputField", "RadioButtonField"):
                choice_list = elem.properties.get('choice_list') if elem.properties else None
                if choice_list:
                    context = f"Форма '{form_name}' - {elem.element_type} '{elem_path}'"
                    is_valid, error = validate_choice_list(choice_list, context)
                    if not is_valid:
                        self.errors.append(error)

                                             
            if elem.child_items:
                self._validate_element_choice_lists(elem.child_items, form_name, elem_path)

    def _validate_element_properties(self, elements, form_name: str, parent_path: str = "") -> None:
                   
        if not elements:
            return

        for elem in elements:
            elem_path = f"{parent_path}/{elem.name}" if parent_path else elem.name
            context = f"Форма '{form_name}' - {elem.element_type} '{elem_path}'"
            props = elem.properties or {}

                                      
            enum_checks = [
                ('horizontal_align', VALID_HORIZONTAL_ALIGN),
                ('vertical_align', VALID_VERTICAL_ALIGN),
                ('title_location', VALID_TITLE_LOCATION),
                ('group_direction', VALID_GROUP_DIRECTION),
                ('behavior', VALID_BEHAVIOR),
                ('radio_button_type', VALID_RADIO_BUTTON_TYPE),
                ('picture_size', VALID_PICTURE_SIZE),
            ]
            for prop_name, valid_values in enum_checks:
                if prop_name in props:
                    is_valid, error = validate_enum(
                        props[prop_name], valid_values, prop_name, context
                    )
                    if not is_valid:
                        self.errors.append(error)

                                                                              
            if 'representation' in props:
                if elem.element_type == 'Table':
                    valid_repr = VALID_TABLE_REPRESENTATION
                else:
                    valid_repr = VALID_REPRESENTATION
                is_valid, error = validate_enum(
                    props['representation'], valid_repr, 'representation', context
                )
                if not is_valid:
                    self.errors.append(error)

                                     
            if 'font' in props:
                is_valid, error = validate_font(props['font'], context)
                if not is_valid:
                    self.errors.append(error)

                                       
            color_props = ['text_color', 'back_color', 'border_color']
            for color_prop in color_props:
                if color_prop in props:
                    is_valid, error = validate_color(
                        props[color_prop], color_prop, context
                    )
                    if not is_valid:
                        self.errors.append(error)

                                                                      
            if hasattr(elem, 'conditional_appearances') and elem.conditional_appearances:
                for i, ca in enumerate(elem.conditional_appearances):
                                                                                                
                    if hasattr(ca, 'appearance') and ca.appearance:
                        app = ca.appearance
                        for color_attr in ['text_color', 'back_color', 'border_color']:
                            color_val = getattr(app, color_attr, None)
                            if color_val:
                                is_valid, error = validate_color(
                                    color_val, color_attr,
                                    f"{context}: conditional_appearances[{i}].appearance"
                                )
                                if not is_valid:
                                    self.errors.append(error)

                                             
            if elem.child_items:
                self._validate_element_properties(elem.child_items, form_name, elem_path)

    def _validate_form_modules(self) -> Tuple[List[str], List[str]]:
                   
        errors = []
        warnings = []

        for form in self.processor.forms:
            module_name = f"Форма.{form.name}"

                                                          
            if hasattr(form, 'events_bsl') and form.events_bsl:
                for event_name, event_code in form.events_bsl.items():
                    bsl_errors, bsl_warnings = self._validate_bsl_code(
                        event_code,
                        f"{module_name}.{event_name}"
                    )
                    errors.extend(bsl_errors)
                    warnings.extend(bsl_warnings)

                                        
            for cmd in form.commands:
                if hasattr(cmd, 'bsl_code') and cmd.bsl_code:
                    bsl_errors, bsl_warnings = self._validate_bsl_code(
                        cmd.bsl_code,
                        f"{module_name}.Команда.{cmd.name}"
                    )
                    errors.extend(bsl_errors)
                    warnings.extend(bsl_warnings)

                                                                           
            if hasattr(form, 'helper_procedures') and form.helper_procedures:
                for proc_name, proc_code in form.helper_procedures.items():
                    bsl_errors, bsl_warnings = self._validate_bsl_code(
                        proc_code,
                        f"{module_name}.Helper.{proc_name}"
                    )
                    errors.extend(bsl_errors)
                    warnings.extend(bsl_warnings)

        return errors, warnings


class HandlerValidator:
           

                                                     
    SIGNATURE_PATTERN = re.compile(
        r'^(\s*&\w+\s*\n)?\s*(Процедура|Функция|Procedure|Function|Асинх|Async)\s+(\w+)',
        re.MULTILINE | re.IGNORECASE
    )

                                  
    DIRECTIVE_PATTERN = re.compile(
        r'^\s*&(НаКлиенте|НаСервере|НаСервереБезКонтекста|НаКлиентеНаСервереБезКонтекста|'
        r'OnClient|OnServer|AtServerNoContext|AtClientAtServerNoContext)',
        re.MULTILINE | re.IGNORECASE
    )

                                           
    END_PROCEDURE_PATTERN = re.compile(
        r'(КонецПроцедуры|КонецФункции|EndProcedure|EndFunction)',
        re.IGNORECASE
    )

                                                                      
                                                       
    OBJECT_ACCESS_PATTERN = re.compile(
        r'Объект\.(\w+)|Объект\["(\w+)"\]',
        re.IGNORECASE
    )

    def __init__(
        self,
        processor,
        loaded_handlers: Optional[Dict[str, str]] = None,
        handlers_file: Optional[Path] = None,
    ):
                   
        self.processor = processor
        self.errors: List[str] = []
        self.warnings: List[str] = []

                                                
        if loaded_handlers:
            self._loaded_handlers = loaded_handlers
        elif handlers_file and handlers_file.exists():
            self._loaded_handlers = self._load_handlers(handlers_file)
        else:
            self._loaded_handlers = {}

                                          
        self._value_table_names: Set[str] = set()
        for form in processor.forms:
            for vt in form.value_table_attributes:
                self._value_table_names.add(vt.name)

    def _load_handlers(self, handlers_file: Path) -> Dict[str, str]:
                                             
        from .bsl_splitter import BSLSplitter

        try:
            splitter = BSLSplitter(handlers_file)
            return splitter.extract_procedures()
        except Exception as e:
            self.errors.append(f"Помилка завантаження handlers.bsl: {e}")
            return {}

    def _collect_required_handlers(self) -> Set[str]:
                   
        required = set()

        for form in self.processor.forms:
                                   
            for event_name, handler_name in form.events.items():
                required.add(handler_name)
                                                                           
                if event_name == "OnCreateAtServer":
                    required.add(f"{handler_name}НаСервере")

                              
            for cmd in form.commands:
                if cmd.action:
                                                                          
                                                            
                    if cmd.long_operation:
                        continue
                    required.add(cmd.action)
                                                 
                    required.add(f"{cmd.action}НаСервере")

                                       
            for elem in form.elements:
                if elem.event_handlers:
                    for event_name, handler_name in elem.event_handlers.items():
                        required.add(handler_name)
                                                                               
                        required.add(f"{handler_name}НаСервере")

                                            
                required.update(self._collect_element_handlers(elem.child_items))

        return required

    def _collect_element_handlers(self, elements) -> Set[str]:
                                                              
        handlers = set()
        if not elements:
            return handlers

        for elem in elements:
            if elem.event_handlers:
                for handler_name in elem.event_handlers.values():
                    handlers.add(handler_name)
                    handlers.add(f"{handler_name}НаСервере")

            if elem.child_items:
                handlers.update(self._collect_element_handlers(elem.child_items))

        return handlers

    def validate_handler_names_match(self) -> Tuple[List[str], List[str]]:
                   
        errors = []
        warnings = []

        if not self._loaded_handlers:
                                              
            return errors, warnings

        required_handlers = self._collect_required_handlers()
        available_handlers = set(self._loaded_handlers.keys())

                                   
        for handler_name in required_handlers:
                                                       
            if handler_name.endswith("НаСервере"):
                continue

            if handler_name not in available_handlers:
                                                     
                similar = get_close_matches(
                    handler_name,
                    available_handlers,
                    n=3,
                    cutoff=0.6
                )

                if similar:
                    errors.append(
                        f"Handler '{handler_name}' не знайдено в handlers.bsl. "
                        f"Схожі: {', '.join(similar)}"
                    )
                else:
                    errors.append(
                        f"Handler '{handler_name}' не знайдено в handlers.bsl"
                    )

        return errors, warnings

    def validate_handler_signatures(self) -> Tuple[List[str], List[str]]:
                   
        errors = []
        warnings = []

        for handler_name, handler_code in self._loaded_handlers.items():
                                              
            if not self.DIRECTIVE_PATTERN.search(handler_code):
                errors.append(
                    f"Handler '{handler_name}' не має директиви компіляції "
                    f"(&НаКлиенте, &НаСервере, тощо). "
                    f"Додайте директиву на початок процедури."
                )

                                                                
            sig_match = self.SIGNATURE_PATTERN.search(handler_code)
            if not sig_match:
                errors.append(
                    f"Handler '{handler_name}' не має коректної сигнатури. "
                    f"Очікується: Процедура {handler_name}(...) або Функция {handler_name}(...)"
                )
            else:
                                                                         
                proc_name = sig_match.group(3)
                if proc_name != handler_name:
                    warnings.append(
                        f"Handler '{handler_name}' має іншу назву в сигнатурі: '{proc_name}'. "
                        f"Рекомендується використовувати однакові імена."
                    )

                                                      
            if not self.END_PROCEDURE_PATTERN.search(handler_code):
                errors.append(
                    f"Handler '{handler_name}' не має закриваючого тегу "
                    f"(КонецПроцедуры/КонецФункции). "
                    f"Додайте закриваючий тег в кінці процедури."
                )

        return errors, warnings

    def validate_valuetable_access(self) -> Tuple[List[str], List[str]]:
                   
        errors = []
        warnings = []

        if not self._value_table_names:
            return errors, warnings

        for handler_name, handler_code in self._loaded_handlers.items():
                                               
            for match in self.OBJECT_ACCESS_PATTERN.finditer(handler_code):
                accessed_name = match.group(1) or match.group(2)

                if accessed_name in self._value_table_names:
                    warnings.append(
                        f"Handler '{handler_name}': використано Объект.{accessed_name}, "
                        f"але '{accessed_name}' - це ValueTable на рівні форми. "
                        f"Доступ напряму: {accessed_name} (без Объект.)"
                    )

        return errors, warnings

    def validate(self) -> Tuple[bool, List[str], List[str]]:
                   
        self.errors = []
        self.warnings = []

                                    
        name_errors, name_warnings = self.validate_handler_names_match()
        self.errors.extend(name_errors)
        self.warnings.extend(name_warnings)

                                        
        sig_errors, sig_warnings = self.validate_handler_signatures()
        self.errors.extend(sig_errors)
        self.warnings.extend(sig_warnings)

                                            
        vt_errors, vt_warnings = self.validate_valuetable_access()
        self.errors.extend(vt_errors)
        self.warnings.extend(vt_warnings)

        return len(self.errors) == 0, self.errors, self.warnings
