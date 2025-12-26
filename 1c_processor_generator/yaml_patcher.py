   

import re
from typing import Any, Dict, List, Optional, Set
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
import logging

                                            
from .yaml_comment_utils import (
    update_value_preserving_comments,
    insert_preserving_comments,
    delete_preserving_comments,
)

logger = logging.getLogger(__name__)


class ReferenceChecker:
           

    def __init__(self, config: dict, bsl_code: str):
                   
        self.config = config
        self.bsl_code = bsl_code

    def check_attribute_references(self, attribute_name: str) -> List[str]:
                   
        references = []

                                       
        if f"Объект.{attribute_name}" in self.bsl_code:
            references.append(f"BSL code: Объект.{attribute_name}")

        if f"Object.{attribute_name}" in self.bsl_code:
            references.append(f"BSL code: Object.{attribute_name}")

                             
        if 'forms' in self.config:
            for form_idx, form in enumerate(self.config['forms']):
                if 'elements' not in form:
                    continue

                for elem_idx, element in enumerate(form['elements']):
                    if element.get('attribute') == attribute_name:
                        references.append(
                            f"Form element: forms[{form_idx}].elements[{elem_idx}] "
                            f"(name={element.get('name')})"
                        )

        return references

    def check_form_element_references(self, element_name: str) -> List[str]:
                   
        references = []

                                             
        patterns = [
            f"Элементы.{element_name}",
            f"Items.{element_name}",
            f'"{element_name}"',
            f"'{element_name}'"
        ]

        for pattern in patterns:
            if pattern in self.bsl_code:
                references.append(f"BSL code: {pattern}")

        return references

    def check_command_references(self, command_name: str) -> List[str]:
                   
        references = []

                                                                         
                                                   
        if command_name in self.bsl_code:
            references.append(f"BSL code: {command_name}")

        return references

    def check_value_table_references(self, table_name: str) -> List[str]:
                   
        references = []

                                                                  
        patterns = [
            f"Объект.{table_name}",
            f"Object.{table_name}",
            f"Элементы.{table_name}",
            f"Items.{table_name}",
            f'"{table_name}"',
            f"'{table_name}'"
        ]

        for pattern in patterns:
            if pattern in self.bsl_code:
                references.append(f"BSL code: {pattern}")

                                                     
        if 'forms' in self.config:
            for form_idx, form in enumerate(self.config['forms']):
                if 'elements' not in form:
                    continue

                for elem_idx, element in enumerate(form['elements']):
                                                                          
                    if element.get('type') == 'Table':
                        if element.get('value_table') == table_name:
                            references.append(
                                f"Form element: forms[{form_idx}].elements[{elem_idx}] "
                                f"(name={element.get('name')}) references value_table"
                            )

        return references

    def check_form_attribute_references(self, attribute_name: str) -> List[str]:
                   
        references = []

                                                                  
        patterns = [
            f"Элементы.{attribute_name}",
            f"Items.{attribute_name}",
            f'"{attribute_name}"',
            f"'{attribute_name}'"
        ]

        for pattern in patterns:
            if pattern in self.bsl_code:
                references.append(f"BSL code: {pattern}")

                                                              
        if 'forms' in self.config:
            for form_idx, form in enumerate(self.config['forms']):
                if 'elements' not in form:
                    continue

                for elem_idx, element in enumerate(form['elements']):
                                                                        
                    if element.get('attribute') == attribute_name:
                        references.append(
                            f"Form element: forms[{form_idx}].elements[{elem_idx}] "
                            f"(name={element.get('name')}) references attribute"
                        )

        return references

    def check_form_references(self, form_name: str) -> List[str]:
                   
        references = []

                                            
        if 'forms' in self.config:
            for form_idx, form in enumerate(self.config['forms']):
                if form.get('name') == form_name and form.get('default'):
                    references.append(
                        f"Form is marked as default (forms[{form_idx}].default=true)"
                    )

                                                      
        if self.bsl_code:
            form_patterns = [
                f'GetForm.*"{form_name}"',
                f'OpenForm.*"{form_name}"',
                f'ПолучитьФорму.*"{form_name}"',
                f'ОткрытьФорму.*"{form_name}"',
            ]
            for pattern in form_patterns:
                matches = re.findall(pattern, self.bsl_code, re.IGNORECASE)
                if matches:
                    references.append(
                        f"BSL code references form: {pattern} ({len(matches)} occurrences)"
                    )

        return references

    def check_template_references(self, template_name: str) -> List[str]:
                   
        references = []

                                                               
        if self.bsl_code:
            patterns = [
                f'GetTemplate.*"{template_name}"',
                f'ПолучитьМакет.*"{template_name}"',
                f"GetTemplate.*'{template_name}'",
                f"ПолучитьМакет.*'{template_name}'",
            ]
            for pattern in patterns:
                matches = re.findall(pattern, self.bsl_code, re.IGNORECASE)
                if matches:
                    references.append(
                        f"BSL code references template: {pattern} ({len(matches)} occurrences)"
                    )

                                                                       
        if 'templates' in self.config:
            for tmpl in self.config['templates']:
                if tmpl.get('name') == template_name and tmpl.get('auto_field'):
                    field_name = tmpl.get('field_name', f'{template_name}Field')
                    references.append(
                        f"Template has auto_field=true, generates form element: {field_name}"
                    )

        return references

    def check_form_parameter_references(self, param_name: str) -> List[str]:
                   
        references = []

                                                                              
        if self.bsl_code:
            patterns = [
                f"Parameters\\.{param_name}",
                f"Параметры\\.{param_name}",
            ]
            for pattern in patterns:
                matches = re.findall(pattern, self.bsl_code, re.IGNORECASE)
                if matches:
                    references.append(
                        f"BSL code references parameter: {pattern} ({len(matches)} occurrences)"
                    )

        return references


class YAMLPatcher:
           

    def __init__(self, config_path: str, bsl_code: str = ""):
                   
        self.config_path = config_path
        self.bsl_code = bsl_code

                                                
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
        self.yaml.indent(mapping=2, sequence=2, offset=0)
                                                         
        self.yaml.map_indent = 2
        self.yaml.sequence_indent = 2
        self.yaml.sequence_dash_offset = 0
                                                                                        
                                                                       

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = self.yaml.load(f)

        self.ref_checker = ReferenceChecker(self.config, bsl_code)
        self.warnings: List[str] = []

    def add_attribute(self, attribute_data: Dict[str, Any]) -> bool:
                   
        if 'attributes' not in self.config:
            self.config['attributes'] = CommentedSeq()

                                           
        existing_names = [attr['name'] for attr in self.config['attributes']]
        if attribute_data['name'] in existing_names:
            logger.warning(f"Attribute '{attribute_data['name']}' already exists")
            return False

                                                    
        insert_preserving_comments(
            self.config['attributes'],
            len(self.config['attributes']),                 
            attribute_data
        )
        logger.info(f"Added attribute: {attribute_data['name']}")
        return True

    def delete_attribute(self, attribute_name: str, force: bool = False) -> bool:
                   
        if 'attributes' not in self.config:
            return False

                              
        references = self.ref_checker.check_attribute_references(attribute_name)
        if references and not force:
            self.warnings.append(
                f"Cannot delete attribute '{attribute_name}' - found references:\n" +
                "\n".join(f"  - {ref}" for ref in references)
            )
            return False

                                                                
        attributes = self.config['attributes']
        for idx, attr in enumerate(attributes):
            if attr['name'] == attribute_name:
                delete_preserving_comments(attributes, idx, preserve_orphaned_comments=True)
                logger.info(f"Deleted attribute: {attribute_name}")

                if references:
                    self.warnings.append(
                        f"Deleted attribute '{attribute_name}' but found references (force=True):\n" +
                        "\n".join(f"  - {ref}" for ref in references)
                    )
                return True

        logger.warning(f"Attribute '{attribute_name}' not found")
        return False

    def add_form_element(self, form_index: int, element_data: Dict[str, Any],
                        position: Optional[int] = None) -> bool:
                   
        if 'forms' not in self.config or form_index >= len(self.config['forms']):
            return False

        form = self.config['forms'][form_index]

        if 'elements' not in form:
            form['elements'] = CommentedSeq()

                                         
        existing_names = [elem['name'] for elem in form['elements']]
        if element_data['name'] in existing_names:
            logger.warning(f"Form element '{element_data['name']}' already exists")
            return False

                                                  
        if position is None:
            insert_preserving_comments(form['elements'], len(form['elements']), element_data)
        else:
            insert_preserving_comments(form['elements'], position, element_data)

        logger.info(f"Added form element: {element_data['name']}")
        return True

    def delete_form_element(self, form_index: int, element_name: str,
                           force: bool = False) -> bool:
                   
        if 'forms' not in self.config or form_index >= len(self.config['forms']):
            return False

        form = self.config['forms'][form_index]

        if 'elements' not in form:
            return False

                              
        references = self.ref_checker.check_form_element_references(element_name)
        if references and not force:
            self.warnings.append(
                f"Cannot delete form element '{element_name}' - found references:\n" +
                "\n".join(f"  - {ref}" for ref in references)
            )
            return False

                                                              
        elements = form['elements']
        for idx, elem in enumerate(elements):
            if elem['name'] == element_name:
                delete_preserving_comments(elements, idx, preserve_orphaned_comments=True)
                logger.info(f"Deleted form element: {element_name}")

                if references:
                    self.warnings.append(
                        f"Deleted form element '{element_name}' but found references (force=True):\n" +
                        "\n".join(f"  - {ref}" for ref in references)
                    )
                return True

        logger.warning(f"Form element '{element_name}' not found")
        return False

                                     

    def add_form_element_nested(
        self,
        form_index: int,
        element_data: Dict[str, Any],
        parent_path: Optional[str] = None,
        insertion_index: Optional[int] = None
    ) -> bool:
                   
        if 'forms' not in self.config or form_index >= len(self.config['forms']):
            return False

        form = self.config['forms'][form_index]

                                              
        if parent_path is None:
            return self.add_form_element(form_index, element_data, insertion_index)

                             
        parent = self._get_element_by_path(form, parent_path)
        if parent is None:
            logger.warning(f"Parent element not found at path: {parent_path}")
            return False

                                       
        if 'child_items' not in parent:
            parent['child_items'] = CommentedSeq()

                                                        
        existing_names = [elem['name'] for elem in parent['child_items']]
        if element_data['name'] in existing_names:
            logger.warning(f"Form element '{element_data['name']}' already exists in parent's child_items")
            return False

                                                  
        if insertion_index is None:
            insert_preserving_comments(parent['child_items'], len(parent['child_items']), element_data)
        else:
            insert_preserving_comments(parent['child_items'], insertion_index, element_data)

        logger.info(f"Added nested form element: {element_data['name']} to {parent_path}")
        return True

    def delete_form_element_nested(
        self,
        form_index: int,
        element_name: str,
        parent_path: Optional[str] = None,
        force: bool = False
    ) -> bool:
                   
        if 'forms' not in self.config or form_index >= len(self.config['forms']):
            return False

        form = self.config['forms'][form_index]

                                                 
        if parent_path is None:
            return self.delete_form_element(form_index, element_name, force)

                             
        parent = self._get_element_by_path(form, parent_path)
        if parent is None:
            logger.warning(f"Parent element not found at path: {parent_path}")
            return False

        if 'child_items' not in parent:
            logger.warning(f"Parent element has no child_items")
            return False

                              
        references = self.ref_checker.check_form_element_references(element_name)
        if references and not force:
            self.warnings.append(
                f"Cannot delete nested form element '{element_name}' - found references:\n" +
                "\n".join(f"  - {ref}" for ref in references)
            )
            return False

                                                                               
        child_items = parent['child_items']
        for idx, elem in enumerate(child_items):
            if elem['name'] == element_name:
                delete_preserving_comments(child_items, idx, preserve_orphaned_comments=True)
                logger.info(f"Deleted nested form element: {element_name} from {parent_path}")

                if references:
                    self.warnings.append(
                        f"Deleted nested form element '{element_name}' but found references (force=True):\n" +
                        "\n".join(f"  - {ref}" for ref in references)
                    )
                return True

        logger.warning(f"Form element '{element_name}' not found in parent's child_items")
        return False

    def _get_element_by_path(self, form: Dict, path: str) -> Optional[Dict]:
                   
                                           
                                                        
        parts = path.replace('[', '.').replace(']', '').split('.')
        current = {'forms': [form]}                                        

        for part in parts:
            if not part:
                continue

            if part.isdigit():
                             
                index = int(part)
                if isinstance(current, list):
                    if index < len(current):
                        current = current[index]
                    else:
                        return None
                else:
                    return None
            else:
                                        
                if isinstance(current, dict):
                    current = current.get(part)
                    if current is None:
                        return None
                else:
                    return None

        return current if isinstance(current, dict) else None

    def _find_element_by_name(
        self,
        elements: List[Dict],
        name: str,
        recursive: bool = True
    ) -> Optional[Dict]:
                   
        for elem in elements:
            if elem.get('name') == name:
                return elem

                                                
            if recursive and 'child_items' in elem:
                found = self._find_element_by_name(elem['child_items'], name, recursive=True)
                if found:
                    return found

        return None

    def add_command(self, form_index: int, command_data: Dict[str, Any]) -> bool:
                   
        if 'forms' not in self.config or form_index >= len(self.config['forms']):
            return False

        form = self.config['forms'][form_index]

        if 'commands' not in form:
            form['commands'] = CommentedSeq()

                                         
        existing_names = [cmd['name'] for cmd in form['commands']]
        if command_data['name'] in existing_names:
            logger.warning(f"Command '{command_data['name']}' already exists")
            return False

                                                  
        insert_preserving_comments(form['commands'], len(form['commands']), command_data)
        logger.info(f"Added command: {command_data['name']}")
        return True

    def delete_command(self, form_index: int, command_name: str,
                      force: bool = False) -> bool:
                   
        if 'forms' not in self.config or form_index >= len(self.config['forms']):
            return False

        form = self.config['forms'][form_index]

        if 'commands' not in form:
            return False

                              
        references = self.ref_checker.check_command_references(command_name)
        if references and not force:
            self.warnings.append(
                f"Cannot delete command '{command_name}' - found references:\n" +
                "\n".join(f"  - {ref}" for ref in references)
            )
            return False

                                                              
        commands = form['commands']
        for idx, cmd in enumerate(commands):
            if cmd['name'] == command_name:
                delete_preserving_comments(commands, idx, preserve_orphaned_comments=True)
                logger.info(f"Deleted command: {command_name}")

                if references:
                    self.warnings.append(
                        f"Deleted command '{command_name}' but found references (force=True):\n" +
                        "\n".join(f"  - {ref}" for ref in references)
                    )
                return True

        logger.warning(f"Command '{command_name}' not found")
        return False

    def add_tabular_section(self, tabular_data: Dict[str, Any]) -> bool:
                   
        if 'tabular_sections' not in self.config:
            self.config['tabular_sections'] = CommentedSeq()

                                                 
        existing_names = [ts['name'] for ts in self.config['tabular_sections']]
        if tabular_data['name'] in existing_names:
            logger.warning(f"Tabular section '{tabular_data['name']}' already exists")
            return False

                                                          
        insert_preserving_comments(self.config['tabular_sections'], len(self.config['tabular_sections']), tabular_data)
        logger.info(f"Added tabular section: {tabular_data['name']}")
        return True

    def delete_tabular_section(self, tabular_name: str, force: bool = False) -> bool:
                   
        if 'tabular_sections' not in self.config:
            return False

                                                                          
        references = []
        if tabular_name in self.bsl_code:
            references.append(f"BSL code: {tabular_name}")

        if references and not force:
            self.warnings.append(
                f"Cannot delete tabular section '{tabular_name}' - found references:\n" +
                "\n".join(f"  - {ref}" for ref in references)
            )
            return False

                                                                      
        tabular_sections = self.config['tabular_sections']
        for idx, ts in enumerate(tabular_sections):
            if ts['name'] == tabular_name:
                delete_preserving_comments(tabular_sections, idx, preserve_orphaned_comments=True)
                logger.info(f"Deleted tabular section: {tabular_name}")

                if references:
                    self.warnings.append(
                        f"Deleted tabular section '{tabular_name}' but found references (force=True):\n" +
                        "\n".join(f"  - {ref}" for ref in references)
                    )
                return True

        logger.warning(f"Tabular section '{tabular_name}' not found")
        return False

    def add_value_table(self, form_index: int, value_table_data: Dict[str, Any]) -> bool:
                   
        if 'forms' not in self.config or form_index >= len(self.config['forms']):
            return False

        form = self.config['forms'][form_index]

        if 'value_tables' not in form:
            form['value_tables'] = CommentedSeq()

                                             
        existing_names = [vt['name'] for vt in form['value_tables']]
        if value_table_data['name'] in existing_names:
            logger.warning(f"ValueTable '{value_table_data['name']}' already exists")
            return False

                                                      
        insert_preserving_comments(form['value_tables'], len(form['value_tables']), value_table_data)
        logger.info(f"Added value table: {value_table_data['name']}")
        return True

    def delete_value_table(self, form_index: int, table_name: str, force: bool = False) -> bool:
                   
        if 'forms' not in self.config or form_index >= len(self.config['forms']):
            return False

        form = self.config['forms'][form_index]

        if 'value_tables' not in form:
            return False

                              
        references = self.ref_checker.check_value_table_references(table_name)
        if references and not force:
            self.warnings.append(
                f"Cannot delete value table '{table_name}' - found references:\n" +
                "\n".join(f"  - {ref}" for ref in references)
            )
            return False

                                                                  
        value_tables = form['value_tables']
        for idx, vt in enumerate(value_tables):
            if vt['name'] == table_name:
                delete_preserving_comments(value_tables, idx, preserve_orphaned_comments=True)
                logger.info(f"Deleted value table: {table_name}")

                if references:
                    self.warnings.append(
                        f"Deleted value table '{table_name}' but found references (force=True):\n" +
                        "\n".join(f"  - {ref}" for ref in references)
                    )
                return True

        logger.warning(f"ValueTable '{table_name}' not found")
        return False

    def add_form_attribute(self, form_index: int, form_attr_data: Dict[str, Any]) -> bool:
                   
        if 'forms' not in self.config or form_index >= len(self.config['forms']):
            return False

        form = self.config['forms'][form_index]

        if 'form_attributes' not in form:
            form['form_attributes'] = CommentedSeq()

                                                
        existing_names = [fa['name'] for fa in form['form_attributes']]
        if form_attr_data['name'] in existing_names:
            logger.warning(f"Form attribute '{form_attr_data['name']}' already exists")
            return False

                                                         
        insert_preserving_comments(form['form_attributes'], len(form['form_attributes']), form_attr_data)
        logger.info(f"Added form attribute: {form_attr_data['name']}")
        return True

    def delete_form_attribute(self, form_index: int, attr_name: str, force: bool = False) -> bool:
                   
        if 'forms' not in self.config or form_index >= len(self.config['forms']):
            return False

        form = self.config['forms'][form_index]

        if 'form_attributes' not in form:
            return False

                              
        references = self.ref_checker.check_form_attribute_references(attr_name)
        if references and not force:
            self.warnings.append(
                f"Cannot delete form attribute '{attr_name}' - found references:\n" +
                "\n".join(f"  - {ref}" for ref in references)
            )
            return False

                                                                     
        form_attributes = form['form_attributes']
        for idx, fa in enumerate(form_attributes):
            if fa['name'] == attr_name:
                delete_preserving_comments(form_attributes, idx, preserve_orphaned_comments=True)
                logger.info(f"Deleted form attribute: {attr_name}")

                if references:
                    self.warnings.append(
                        f"Deleted form attribute '{attr_name}' but found references (force=True):\n" +
                        "\n".join(f"  - {ref}" for ref in references)
                    )
                return True

        logger.warning(f"Form attribute '{attr_name}' not found")
        return False

    def save(self) -> bool:
                   
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.yaml.dump(self.config, f)
            logger.info(f"Saved patched YAML: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save YAML: {e}")
            return False

    def add_form(self, form_data: Dict[str, Any]) -> bool:
                   
                                     
        if 'forms' not in self.config:
            self.config['forms'] = CommentedSeq()

                             
        existing_names = [f.get('name') for f in self.config['forms']]
        if form_data['name'] in existing_names:
            logger.warning(f"Form '{form_data['name']}' already exists")
            return False

                                                      
        insert_preserving_comments(self.config['forms'], len(self.config['forms']), form_data)
        logger.info(f"Added form: {form_data['name']}")
        return True

    def delete_form(self, form_name: str, force: bool = False) -> bool:
                   
        if 'forms' not in self.config:
            logger.warning("No forms section in config")
            return False

                         
        form_idx = None
        for idx, form in enumerate(self.config['forms']):
            if form.get('name') == form_name:
                form_idx = idx
                break

        if form_idx is None:
            logger.warning(f"Form '{form_name}' not found")
            return False

                          
        references = self.ref_checker.check_form_references(form_name)
        if references and not force:
            self.warnings.append(
                f"Cannot delete form '{form_name}' - found references:\n" +
                "\n".join(f"  - {ref}" for ref in references)
            )
            return False

                                                  
        delete_preserving_comments(self.config['forms'], form_idx)
        logger.info(f"Deleted form: {form_name}")
        return True

                                                                  

    def add_template(self, template_data: Dict[str, Any]) -> bool:
                   
        if 'templates' not in self.config:
            self.config['templates'] = CommentedSeq()

                                          
        existing_names = [t.get('name') for t in self.config['templates']]
        if template_data.get('name') in existing_names:
            logger.warning(f"Template '{template_data.get('name')}' already exists")
            return False

                      
        insert_preserving_comments(
            self.config['templates'],
            len(self.config['templates']),
            template_data
        )
        logger.info(f"Added template: {template_data.get('name')}")
        return True

    def delete_template(self, template_name: str, force: bool = False) -> bool:
                   
        if 'templates' not in self.config:
            return False

                              
        references = self.ref_checker.check_template_references(template_name)
        if references and not force:
            self.warnings.append(
                f"Cannot delete template '{template_name}' - found references:\n" +
                "\n".join(f"  - {ref}" for ref in references)
            )
            return False

                                  
        templates = self.config['templates']
        for idx, tmpl in enumerate(templates):
            if tmpl.get('name') == template_name:
                delete_preserving_comments(templates, idx)
                logger.info(f"Deleted template: {template_name}")
                return True

        logger.warning(f"Template '{template_name}' not found")
        return False

                                                                        

    def add_form_parameter(self, form_index: int, param_data: Dict[str, Any]) -> bool:
                   
        if 'forms' not in self.config or form_index >= len(self.config['forms']):
            logger.warning(f"Invalid form index: {form_index}")
            return False

        form = self.config['forms'][form_index]
        if 'parameters' not in form:
            form['parameters'] = CommentedSeq()

                                           
        existing_names = [p.get('name') for p in form['parameters']]
        if param_data.get('name') in existing_names:
            logger.warning(f"Form parameter '{param_data.get('name')}' already exists")
            return False

                       
        insert_preserving_comments(
            form['parameters'],
            len(form['parameters']),
            param_data
        )
        logger.info(f"Added form parameter: {param_data.get('name')}")
        return True

    def delete_form_parameter(self, form_index: int, param_name: str, force: bool = False) -> bool:
                   
        if 'forms' not in self.config or form_index >= len(self.config['forms']):
            return False

        form = self.config['forms'][form_index]
        if 'parameters' not in form:
            return False

                              
        references = self.ref_checker.check_form_parameter_references(param_name)
        if references and not force:
            self.warnings.append(
                f"Cannot delete form parameter '{param_name}' - found references:\n" +
                "\n".join(f"  - {ref}" for ref in references)
            )
            return False

                                   
        params = form['parameters']
        for idx, param in enumerate(params):
            if param.get('name') == param_name:
                delete_preserving_comments(params, idx)
                logger.info(f"Deleted form parameter: {param_name}")
                return True

        logger.warning(f"Form parameter '{param_name}' not found")
        return False

    def get_warnings(self) -> List[str]:
                                                        
        return self.warnings

    def clear_warnings(self):
                                 
        self.warnings = []
