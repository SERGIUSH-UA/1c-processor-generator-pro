   

from typing import List, Optional
from .models import Processor, Template, TemplatePlaceholder


def generate_template_helpers(processor: Processor) -> str:
           
    if not processor.templates:
        return ""

    helpers = []

    for template in processor.templates:
        if not template.placeholders:
            continue

        helper_code = _generate_single_template_helper(template)
        if helper_code:
            helpers.append(helper_code)

    return "\n\n".join(helpers)


def _generate_single_template_helper(template: Template) -> str:
           
    if not template.placeholders:
        return ""

    function_name = f"ПолучитьТекстМакета{template.name}"

                                                         
    replacements = []
    for ph in template.placeholders:
        replacement_value = _get_placeholder_bsl_value(ph)
        replacements.append(
            f'\tРезультат = СтрЗаменить(Результат, "{ph.name}", {replacement_value});'
        )

    replacements_code = "\n".join(replacements)

                            
    bsl_code = f"""&НаСервере
Функция {function_name}()
\t// Автогенерована функція для template "{template.name}" (v2.41.0+)
\tМакет = РеквизитФормыВЗначение("Объект").ПолучитьМакет("{template.name}");
\tРезультат = Макет.ПолучитьТекст();

\t// Заміна placeholders
{replacements_code}

\tВозврат Результат;
КонецФункции"""

    return bsl_code


def _get_placeholder_bsl_value(placeholder: TemplatePlaceholder) -> str:
           
    if placeholder.bsl_value:
                                         
        return placeholder.bsl_value
    elif placeholder.attribute:
                                            
                                                                 
        if "." in placeholder.attribute:
                                                      
            return placeholder.attribute
        else:
                                                 
            return f"Объект.{placeholder.attribute}"
    else:
                                   
        return '""'


def get_template_helper_names(processor: Processor) -> List[str]:
           
    if not processor.templates:
        return []

    names = []
    for template in processor.templates:
        if template.placeholders:
            names.append(f"ПолучитьТекстМакета{template.name}")

    return names
