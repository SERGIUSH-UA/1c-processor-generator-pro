   

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
import logging
from ruamel.yaml import YAML

from .xml_differ import XMLChange, ChangeType, ElementType
from .bsl_differ import BSLChange, BSLChangeType

logger = logging.getLogger(__name__)


@dataclass
class YAMLUpdate:
           
    path: str                               
    old_value: Any
    new_value: Any
    section: str                                                    
    element_name: Optional[str] = None                                 

    def __str__(self) -> str:
        return f"YAML: {self.path}: '{self.old_value}' → '{self.new_value}'"


@dataclass
class BSLUpdate:
           
    update_type: str                             
    procedure_name: str
    old_code: Optional[str] = None
    new_code: Optional[str] = None

    def __str__(self) -> str:
        if self.update_type == "add":
            return f"BSL: Add procedure '{self.procedure_name}'"
        elif self.update_type == "delete":
            return f"BSL: Delete procedure '{self.procedure_name}'"
        else:
            return f"BSL: Modify procedure '{self.procedure_name}'"


@dataclass
class StructuralUpdate:
           
    operation: str                   
    element_type: str                                                            
    element_data: Dict[str, Any]                                                             
    references: Optional[List[str]] = None                                 

                                                     
    parent_path: Optional[str] = None                                                      
    insertion_index: Optional[int] = None                         
    depth: int = 0                                 

    def __str__(self) -> str:
        if self.operation == "add":
            name = self.element_data.get('name', 'unknown')
            return f"STRUCTURAL: Add {self.element_type} '{name}'"
        else:
            name = self.element_data.get('name', 'unknown')
            ref_count = len(self.references) if self.references else 0
            return f"STRUCTURAL: Delete {self.element_type} '{name}' ({ref_count} references)"


class ChangeMapper:
           

    def __init__(self, config_path: str):
                   
        self.config_path = config_path
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: str) -> dict:
                                    
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.default_flow_style = False
                                                         
        yaml.map_indent = 2
        yaml.sequence_indent = 2
        yaml.sequence_dash_offset = 0

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.load(f)
        except Exception as e:
            logger.error(f"Failed to load config {config_path}: {e}")
            raise

    def map_xml_changes(self, xml_changes: List[XMLChange]) -> List[YAMLUpdate]:
                   
        updates = []

        for change in xml_changes:
            mapped = self._map_single_xml_change(change)
            if mapped:
                if isinstance(mapped, list):
                    updates.extend(mapped)
                else:
                    updates.append(mapped)

        return updates

    def map_bsl_changes(self, bsl_changes: List[BSLChange]) -> List[BSLUpdate]:
                   
        updates = []

        for change in bsl_changes:
            mapped = self._map_single_bsl_change(change)
            if mapped:
                updates.append(mapped)

        return updates

    def _map_single_xml_change(self, change: XMLChange) -> Optional[Union[YAMLUpdate, List[YAMLUpdate]]]:
                                                        

        if change.element_type == ElementType.ATTRIBUTE:
            return self._map_attribute_change(change)

        elif change.element_type == ElementType.FORM_ELEMENT:
            return self._map_form_element_change(change)

        elif change.element_type == ElementType.COMMAND:
            return self._map_command_change(change)

        elif change.element_type == ElementType.TABULAR_SECTION:
            return self._map_tabular_section_change(change)

        elif change.element_type == ElementType.TABULAR_SECTION_COLUMN:
            return self._map_tabular_column_change(change)

        elif change.element_type == ElementType.FORM:
            return self._map_form_change(change)

        return None

    def _map_single_bsl_change(self, change: BSLChange) -> Optional[BSLUpdate]:
                                                    

        if change.change_type == BSLChangeType.PROCEDURE_ADDED:
            return BSLUpdate(
                update_type="add",
                procedure_name=change.procedure_name,
                new_code=change.new_code
            )

        elif change.change_type == BSLChangeType.PROCEDURE_DELETED:
            return BSLUpdate(
                update_type="delete",
                procedure_name=change.procedure_name,
                old_code=change.old_code
            )

        elif change.change_type == BSLChangeType.PROCEDURE_MODIFIED:
            return BSLUpdate(
                update_type="modify",
                procedure_name=change.procedure_name,
                old_code=change.old_code,
                new_code=change.new_code
            )

        return None

                                                                 

    def _map_attribute_change(self, change: XMLChange) -> Optional[Union[YAMLUpdate, List[YAMLUpdate]]]:
                                                            

        if change.change_type == ChangeType.RENAME:
                                                                
            return self._handle_attribute_rename(change.old_value, change.new_value)

        elif change.change_type == ChangeType.PROPERTY_CHANGE:
                                                       
            attr_name = change.element_name
            property_name = change.property_name

                                          
            attr_idx = self._find_attribute_index(attr_name)
            if attr_idx is None:
                logger.warning(f"Attribute '{attr_name}' not found in YAML")
                return None

                                             
            yaml_field = self._map_property_to_yaml_field(property_name)

            path = f"attributes[{attr_idx}].{yaml_field}"

            return YAMLUpdate(
                path=path,
                old_value=change.old_value,
                new_value=change.new_value,
                section="attributes",
                element_name=attr_name
            )

        elif change.change_type == ChangeType.TYPE_CHANGE:
                          
            attr_name = change.element_name
            attr_idx = self._find_attribute_index(attr_name)
            if attr_idx is None:
                return None

            path = f"attributes[{attr_idx}].type"

            return YAMLUpdate(
                path=path,
                old_value=change.old_value,
                new_value=change.new_value,
                section="attributes",
                element_name=attr_name
            )

        elif change.change_type == ChangeType.ADD:
                                                         
            logger.info(f"Attribute added: {change.new_value}")
                                                           
                                                                               
            return None                                                                                     

        elif change.change_type == ChangeType.DELETE:
                                                            
            logger.info(f"Attribute deleted: {change.old_value}")
            return None                                               

        return None

    def _handle_attribute_rename(self, old_name: str, new_name: str) -> List[YAMLUpdate]:
                   
        updates = []

                                         
        attr_idx = self._find_attribute_index(old_name)
        if attr_idx is not None:
            updates.append(YAMLUpdate(
                path=f"attributes[{attr_idx}].name",
                old_value=old_name,
                new_value=new_name,
                section="attributes",
                element_name=old_name
            ))

                                                               
        form_updates = self._find_form_element_references(old_name, new_name)
        updates.extend(form_updates)

        return updates

    def _find_form_element_references(self, old_attr_name: str, new_attr_name: str) -> List[YAMLUpdate]:
                                                                                    
        updates = []

                             
        if 'forms' not in self.config:
            return updates

        for form_idx, form in enumerate(self.config['forms']):
            if 'elements' not in form:
                continue

            for elem_idx, element in enumerate(form['elements']):
                                                           
                if element.get('attribute') == old_attr_name:
                    path = f"forms[{form_idx}].elements[{elem_idx}].attribute"
                    updates.append(YAMLUpdate(
                        path=path,
                        old_value=old_attr_name,
                        new_value=new_attr_name,
                        section="forms",
                        element_name=element.get('name', 'unknown')
                    ))

        return updates

                                                                    

    def _map_form_element_change(self, change: XMLChange) -> Optional[YAMLUpdate]:
                                                     

        if change.change_type == ChangeType.RENAME:
                                  
            elem_name = change.old_value
            new_name = change.new_value

            elem_path = self._find_form_element_path(elem_name)
            if elem_path is None:
                logger.warning(f"Form element '{elem_name}' not found in YAML")
                return None

            path = f"{elem_path}.name"

            return YAMLUpdate(
                path=path,
                old_value=elem_name,
                new_value=new_name,
                section="forms",
                element_name=elem_name
            )

        elif change.change_type == ChangeType.PROPERTY_CHANGE:
                                                            
            elem_name = change.element_name
            property_name = change.property_name

            elem_path = self._find_form_element_path(elem_name)
            if elem_path is None:
                return None

            yaml_field = self._map_property_to_yaml_field(property_name)
            path = f"{elem_path}.{yaml_field}"

            return YAMLUpdate(
                path=path,
                old_value=change.old_value,
                new_value=change.new_value,
                section="forms",
                element_name=elem_name
            )

        return None

                                                               

    def _map_command_change(self, change: XMLChange) -> Optional[YAMLUpdate]:
                                                

        if change.change_type == ChangeType.RENAME:
            cmd_name = change.old_value
            new_name = change.new_value

            cmd_path = self._find_command_path(cmd_name)
            if cmd_path is None:
                return None

            path = f"{cmd_path}.name"

            return YAMLUpdate(
                path=path,
                old_value=cmd_name,
                new_value=new_name,
                section="forms",
                element_name=cmd_name
            )

        elif change.change_type == ChangeType.PROPERTY_CHANGE:
            cmd_name = change.element_name
            property_name = change.property_name

            cmd_path = self._find_command_path(cmd_name)
            if cmd_path is None:
                return None

            yaml_field = self._map_property_to_yaml_field(property_name)
            path = f"{cmd_path}.{yaml_field}"

            return YAMLUpdate(
                path=path,
                old_value=change.old_value,
                new_value=change.new_value,
                section="forms",
                element_name=cmd_name
            )

        return None

                                                                       

    def _map_tabular_section_change(self, change: XMLChange) -> Optional[YAMLUpdate]:
                                                        

        if change.change_type == ChangeType.RENAME:
            section_name = change.old_value
            new_name = change.new_value

            section_idx = self._find_tabular_section_index(section_name)
            if section_idx is None:
                return None

            path = f"tabular_sections[{section_idx}].name"

            return YAMLUpdate(
                path=path,
                old_value=section_name,
                new_value=new_name,
                section="tabular_sections",
                element_name=section_name
            )

        return None

    def _map_tabular_column_change(self, change: XMLChange) -> Optional[YAMLUpdate]:
                                                               

                                                                                  
        section_name = change.element_name

        if change.change_type == ChangeType.RENAME:
            col_name = change.old_value
            new_name = change.new_value

            col_path = self._find_tabular_column_path(section_name, col_name)
            if col_path is None:
                return None

            path = f"{col_path}.name"

            return YAMLUpdate(
                path=path,
                old_value=col_name,
                new_value=new_name,
                section="tabular_sections",
                element_name=f"{section_name}.{col_name}"
            )

        elif change.change_type == ChangeType.TYPE_CHANGE:
            col_name = change.element_name

            col_path = self._find_tabular_column_path(section_name, col_name)
            if col_path is None:
                return None

            path = f"{col_path}.type"

            return YAMLUpdate(
                path=path,
                old_value=change.old_value,
                new_value=change.new_value,
                section="tabular_sections",
                element_name=f"{section_name}.{col_name}"
            )

        return None

                                                            

    def _map_form_change(self, change: XMLChange) -> Optional[YAMLUpdate]:
                   
                                                                                    
                                                                       
                                                                              
                                         
        return None

                                                                                           

    def _find_attribute_index(self, attr_name: str) -> Optional[int]:
                                                     
        if 'attributes' not in self.config:
            return None

        for idx, attr in enumerate(self.config['attributes']):
            if attr.get('name') == attr_name:
                return idx

        return None

    def _find_form_element_path(self, elem_name: str) -> Optional[str]:
                                                       
        if 'forms' not in self.config:
            return None

        for form_idx, form in enumerate(self.config['forms']):
            if 'elements' not in form:
                continue

            for elem_idx, element in enumerate(form['elements']):
                if element.get('name') == elem_name:
                    return f"forms[{form_idx}].elements[{elem_idx}]"

        return None

    def _find_command_path(self, cmd_name: str) -> Optional[str]:
                                                  
        if 'forms' not in self.config:
            return None

        for form_idx, form in enumerate(self.config['forms']):
            if 'commands' not in form:
                continue

            for cmd_idx, command in enumerate(form['commands']):
                if command.get('name') == cmd_name:
                    return f"forms[{form_idx}].commands[{cmd_idx}]"

        return None

    def _find_tabular_section_index(self, section_name: str) -> Optional[int]:
                                                           
        if 'tabular_sections' not in self.config:
            return None

        for idx, section in enumerate(self.config['tabular_sections']):
            if section.get('name') == section_name:
                return idx

        return None

    def _find_tabular_column_path(self, section_name: str, col_name: str) -> Optional[str]:
                                                                 
        section_idx = self._find_tabular_section_index(section_name)
        if section_idx is None:
            return None

        section = self.config['tabular_sections'][section_idx]
        if 'columns' not in section:
            return None

        for col_idx, column in enumerate(section['columns']):
            if column.get('name') == col_name:
                return f"tabular_sections[{section_idx}].columns[{col_idx}]"

        return None

    def _map_property_to_yaml_field(self, property_name: str) -> str:
                   
        mapping = {
            'synonym': 'synonym',
            'title': 'title',
            'tooltip': 'tooltip',
            'width': 'width',
            'height': 'height',
        }

        return mapping.get(property_name.lower(), property_name.lower())
