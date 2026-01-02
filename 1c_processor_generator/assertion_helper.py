   

import re
import logging
from typing import Any, Optional, Tuple, List
from datetime import datetime, date

logger = logging.getLogger(__name__)

                                     
TEST_INFRASTRUCTURE_BSL = """// Автоматично згенерована тестова інфраструктура (v2.16.0+)
// Використовується для перехоплення повідомлень при тестуванні через COM

Перем ТестовыеСообщения;

&НаСервере
Процедура НачатьЗаписьСообщений() Экспорт
\t// Увімкнути режим запису повідомлень для тестування
\tТестовыеСообщения = Новый Массив;
КонецПроцедуры

&НаСервере
Функция ПолучитьТестовыеСообщения() Экспорт
\t// Отримати збережені тестові повідомлення
\tВозврат ТестовыеСообщения;
КонецФункции

&НаСервере
Процедура ОтправитьСообщение(Текст)
\t// Wrapper для Сообщить() який можна використовувати в тестах
\t// В тестовому режимі - збирає повідомлення в масив
\t// В звичайному режимі - викликає Сообщить()
\t
\t// ПРИМІТКА: Використовуйте цю функцію замість Сообщить()
\t// у вашому BSL коді, щоб тести могли перехоплювати повідомлення
\t
\tЕсли ЗначениеЗаполнено(ТестовыеСообщения) Тогда
\t\tТестовыеСообщения.Добавить(Текст);
\tИначе
\t\tСообщить(Текст);
\tКонецЕсли;
КонецПроцедуры"""


def get_test_infrastructure_bsl() -> str:
           
    return TEST_INFRASTRUCTURE_BSL


def should_add_test_infrastructure(processor) -> bool:
           
    return hasattr(processor, "tests_config") and processor.tests_config is not None


                                                    


def check_numeric_assertion(actual: Any, expected: dict, attr_name: str) -> Tuple[bool, Optional[str]]:
           
    try:
        if isinstance(actual, str):
            actual = float(actual)

        if "greater_than" in expected or "gt" in expected:
            threshold = expected.get("greater_than") or expected.get("gt")
            if not (actual > threshold):
                return False, f"{attr_name}: expected > {threshold}, got {actual}"

        if "less_than" in expected or "lt" in expected:
            threshold = expected.get("less_than") or expected.get("lt")
            if not (actual < threshold):
                return False, f"{attr_name}: expected < {threshold}, got {actual}"

        if "greater_or_equal" in expected or "gte" in expected:
            threshold = expected.get("greater_or_equal") or expected.get("gte")
            if not (actual >= threshold):
                return False, f"{attr_name}: expected >= {threshold}, got {actual}"

        if "less_or_equal" in expected or "lte" in expected:
            threshold = expected.get("less_or_equal") or expected.get("lte")
            if not (actual <= threshold):
                return False, f"{attr_name}: expected <= {threshold}, got {actual}"

        if "between" in expected:
            min_val, max_val = expected["between"]
            if not (min_val <= actual <= max_val):
                return False, f"{attr_name}: expected between {min_val} and {max_val}, got {actual}"

        if "not_equal" in expected or "ne" in expected:
            value = expected.get("not_equal") or expected.get("ne")
            if actual == value:
                return False, f"{attr_name}: expected != {value}, got {actual}"

        return True, None
    except (ValueError, TypeError) as e:
        return False, f"{attr_name}: numeric assertion failed - {e}"


def check_string_assertion(actual: Any, expected: dict, attr_name: str) -> Tuple[bool, Optional[str]]:
           
    try:
        actual_str = str(actual)

        if "matches" in expected:
            pattern = expected["matches"]
            if not re.search(pattern, actual_str):
                return False, f"{attr_name}: '{actual_str}' does not match pattern '{pattern}'"

        if "starts_with" in expected:
            prefix = expected["starts_with"]
            if not actual_str.startswith(prefix):
                return False, f"{attr_name}: '{actual_str}' does not start with '{prefix}'"

        if "ends_with" in expected:
            suffix = expected["ends_with"]
            if not actual_str.endswith(suffix):
                return False, f"{attr_name}: '{actual_str}' does not end with '{suffix}'"

        if "contains" in expected:
            substring = expected["contains"]
            if substring not in actual_str:
                return False, f"{attr_name}: '{actual_str}' does not contain '{substring}'"

        if "length" in expected:
            expected_length = expected["length"]
            if len(actual_str) != expected_length:
                return False, f"{attr_name}: expected length {expected_length}, got {len(actual_str)}"

        return True, None
    except Exception as e:
        return False, f"{attr_name}: string assertion failed - {e}"


def check_type_assertion(actual: Any, expected: dict, attr_name: str) -> Tuple[bool, Optional[str]]:
           
    try:
        if "is_null" in expected and expected["is_null"]:
            if actual is not None:
                return False, f"{attr_name}: expected null, got {actual}"

        if "not_null" in expected and expected["not_null"]:
            if actual is None:
                return False, f"{attr_name}: expected not null, got null"

        if "type" in expected:
            expected_type = expected["type"].lower()

            if expected_type == "string":
                if not isinstance(actual, str):
                    return False, f"{attr_name}: expected string, got {type(actual).__name__}"
            elif expected_type == "number":
                if not isinstance(actual, (int, float)):
                    return False, f"{attr_name}: expected number, got {type(actual).__name__}"
            elif expected_type == "date":
                if not isinstance(actual, (datetime, date)):
                    return False, f"{attr_name}: expected date, got {type(actual).__name__}"
            elif expected_type in ("boolean", "bool"):
                if not isinstance(actual, bool):
                    return False, f"{attr_name}: expected boolean, got {type(actual).__name__}"
            elif expected_type in ("null", "none"):
                if actual is not None:
                    return False, f"{attr_name}: expected null, got {actual}"

        return True, None
    except Exception as e:
        return False, f"{attr_name}: type assertion failed - {e}"


def check_collection_assertion(actual: Any, expected: dict, attr_name: str) -> Tuple[bool, Optional[str]]:
           
    try:
        if "in" in expected:
            allowed_values = expected["in"]
            if actual not in allowed_values:
                return False, f"{attr_name}: '{actual}' not in {allowed_values}"

        if "not_in" in expected:
            forbidden_values = expected["not_in"]
            if actual in forbidden_values:
                return False, f"{attr_name}: '{actual}' should not be in {forbidden_values}"

        return True, None
    except Exception as e:
        return False, f"{attr_name}: collection assertion failed - {e}"


def check_extended_assertion(actual: Any, expected: Any, attr_name: str) -> Tuple[bool, Optional[str]]:
           
                     
    if not isinstance(expected, dict):
        if actual != expected:
            return False, f"{attr_name}: expected {expected}, got {actual}"
        return True, None

                                      
    numeric_keys = {"greater_than", "gt", "less_than", "lt", "greater_or_equal", "gte",
                    "less_or_equal", "lte", "between", "not_equal", "ne"}
    string_keys = {"matches", "starts_with", "ends_with", "contains", "length"}
    type_keys = {"type", "is_null", "not_null"}
    collection_keys = {"in", "not_in"}

    all_keys = numeric_keys | string_keys | type_keys | collection_keys

    if not any(key in expected for key in all_keys):
                                                
        if actual != expected:
            return False, f"{attr_name}: expected {expected}, got {actual}"
        return True, None

                          
    if any(key in expected for key in numeric_keys):
        passed, error = check_numeric_assertion(actual, expected, attr_name)
        if not passed:
            return False, error

    if any(key in expected for key in string_keys):
        passed, error = check_string_assertion(actual, expected, attr_name)
        if not passed:
            return False, error

    if any(key in expected for key in type_keys):
        passed, error = check_type_assertion(actual, expected, attr_name)
        if not passed:
            return False, error

    if any(key in expected for key in collection_keys):
        passed, error = check_collection_assertion(actual, expected, attr_name)
        if not passed:
            return False, error

    return True, None


def check_message_assertion_extended(messages: List[str], assertion: Any) -> Tuple[bool, Optional[str]]:
           
    from .models import MessageAssertion

    if isinstance(assertion, dict):
        assertion = MessageAssertion(**assertion)

    if assertion.count is not None:
        if len(messages) != assertion.count:
            return False, f"Message count: expected {assertion.count}, got {len(messages)}"

    if assertion.contains:
        found = any(assertion.contains in msg for msg in messages)
        if not found:
            return False, f"No message contains '{assertion.contains}'. Messages: {messages}"

    if assertion.equals:
        found = any(assertion.equals == msg for msg in messages)
        if not found:
            return False, f"No message equals '{assertion.equals}'. Messages: {messages}"

                         
    if assertion.matches:
        found = any(re.search(assertion.matches, msg) for msg in messages)
        if not found:
            return False, f"No message matches '{assertion.matches}'. Messages: {messages}"

    if assertion.starts_with:
        found = any(msg.startswith(assertion.starts_with) for msg in messages)
        if not found:
            return False, f"No message starts with '{assertion.starts_with}'. Messages: {messages}"

    if assertion.ends_with:
        found = any(msg.endswith(assertion.ends_with) for msg in messages)
        if not found:
            return False, f"No message ends with '{assertion.ends_with}'. Messages: {messages}"

    return True, None
