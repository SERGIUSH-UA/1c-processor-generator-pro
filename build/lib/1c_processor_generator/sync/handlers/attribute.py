   

import re
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..base_handler import BaseElementHandler, ChangeType, ElementChange

if TYPE_CHECKING:
    from lxml import etree


class AttributeHandler(BaseElementHandler):
           

    @property
    def element_type_name(self) -> str:
        return "attribute"

    @property
    def yaml_section(self) -> str:
        return "attributes"

    @property
    def is_form_level(self) -> bool:
        return False                   

    def extract_from_xml(
        self,
        elem: "etree._Element",
        namespaces: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
                                                      
        ns = namespaces or self.NAMESPACES
        data: Dict[str, Any] = {}

              
        name_elem = elem.find(".//ns:Properties/ns:Name", namespaces=ns)
        data['name'] = name_elem.text if name_elem is not None and name_elem.text else "UnknownAttribute"

              
        type_elem = elem.find(".//ns:Type/v8:Type", namespaces=ns)
        if type_elem is not None and type_elem.text:
            type_text = type_elem.text
                                                                 
            if ':' in type_text:
                type_name = type_text.split(':')[-1]
            else:
                type_name = type_text
            data['type'] = self._normalize_type(type_name)

                                
        synonym = self.get_multilang_text(elem, "Synonym", ns)
        if synonym:
            if 'ru' in synonym:
                data['synonym_ru'] = synonym['ru']
            if 'uk' in synonym:
                data['synonym_uk'] = synonym['uk']
            if 'en' in synonym:
                data['synonym_en'] = synonym['en']

                                
        tooltip = self.get_multilang_text(elem, "ToolTip", ns)
        if tooltip:
            if 'ru' in tooltip:
                data['tooltip_ru'] = tooltip['ru']
            if 'uk' in tooltip:
                data['tooltip_uk'] = tooltip['uk']
            if 'en' in tooltip:
                data['tooltip_en'] = tooltip['en']

                       
        length_elem = elem.find(".//ns:Type/v8:StringQualifiers/v8:Length", namespaces=ns)
        if length_elem is not None and length_elem.text:
            data['length'] = int(length_elem.text)

                            
        precision_elem = elem.find(".//ns:Type/v8:NumberQualifiers/v8:Precision", namespaces=ns)
        if precision_elem is not None and precision_elem.text:
            data['precision'] = int(precision_elem.text)

        scale_elem = elem.find(".//ns:Type/v8:NumberQualifiers/v8:Scale", namespaces=ns)
        if scale_elem is not None and scale_elem.text:
            data['scale'] = int(scale_elem.text)

        return data

    def get_elements_from_tree(
        self,
        tree: "etree._ElementTree",
        namespaces: Optional[Dict[str, str]] = None,
        form_root: Optional["etree._Element"] = None
    ) -> Dict[str, "etree._Element"]:
                                                    
        ns = namespaces or self.NAMESPACES
        attrs = {}

                                        
        for attr in tree.xpath("//ns:Attribute", namespaces=ns):
            name_elem = attr.find(".//ns:Properties/ns:Name", namespaces=ns)
            if name_elem is not None and name_elem.text:
                attrs[name_elem.text] = attr

        return attrs

    def compare_element_details(
        self,
        name: str,
        original: "etree._Element",
        modified: "etree._Element",
        namespaces: Optional[Dict[str, str]] = None
    ) -> List[ElementChange]:
                                                                 
        ns = namespaces or self.NAMESPACES
        changes = []

                      
        orig_type = self._get_type(original, ns)
        mod_type = self._get_type(modified, ns)
        if orig_type != mod_type:
            changes.append(self._create_change(
                ChangeType.TYPE_CHANGE,
                self.get_xpath(modified) + "/Type",
                orig_type,
                mod_type,
                element_name=name
            ))

                                        
        orig_synonym = self.get_multilang_text(original, "Synonym", ns)
        mod_synonym = self.get_multilang_text(modified, "Synonym", ns)
        if orig_synonym != mod_synonym:
            changes.append(self._create_change(
                ChangeType.PROPERTY_CHANGE,
                self.get_xpath(modified) + "/Synonym",
                orig_synonym,
                mod_synonym,
                element_name=name,
                property_name="synonym"
            ))

                                        
        orig_tooltip = self.get_multilang_text(original, "ToolTip", ns)
        mod_tooltip = self.get_multilang_text(modified, "ToolTip", ns)
        if orig_tooltip != mod_tooltip:
            changes.append(self._create_change(
                ChangeType.PROPERTY_CHANGE,
                self.get_xpath(modified) + "/ToolTip",
                orig_tooltip,
                mod_tooltip,
                element_name=name,
                property_name="tooltip"
            ))

        return changes

    def add_to_yaml(
        self,
        config: Dict,
        data: Dict,
        form_index: int = 0,
        parent_path: Optional[str] = None,
        insertion_index: Optional[int] = None
    ) -> bool:
                                           
        if 'attributes' not in config:
            config['attributes'] = []

                                           
        existing_names = [attr.get('name') for attr in config['attributes']]
        if data.get('name') in existing_names:
            return False

                                       
        if insertion_index is not None and 0 <= insertion_index <= len(config['attributes']):
            config['attributes'].insert(insertion_index, data)
        else:
            config['attributes'].append(data)

        return True

    def delete_from_yaml(
        self,
        config: Dict,
        name: str,
        form_index: int = 0,
        parent_path: Optional[str] = None,
        force: bool = False
    ) -> bool:
                                                
        if 'attributes' not in config:
            return False

        for idx, attr in enumerate(config['attributes']):
            if attr.get('name') == name:
                del config['attributes'][idx]
                return True

        return False

    def check_references(
        self,
        config: Dict,
        bsl_code: str,
        name: str
    ) -> List[str]:
                                                                         
        references = []

                                       
        patterns = [
            f"Объект.{name}",
            f"Object.{name}",
        ]

        for pattern in patterns:
            if pattern in bsl_code:
                references.append(f"BSL code: {pattern}")

                                                   
        if 'forms' in config:
            for form_idx, form in enumerate(config['forms']):
                if 'elements' not in form:
                    continue

                for elem_idx, element in enumerate(form['elements']):
                    if element.get('attribute') == name:
                        references.append(
                            f"Form element: forms[{form_idx}].elements[{elem_idx}] "
                            f"(name={element.get('name')})"
                        )

        return references

                                                               

    def _get_type(self, elem: "etree._Element", ns: Dict[str, str]) -> Optional[str]:
                                                  
        type_elem = elem.find(".//ns:Type/v8:Type", namespaces=ns)
        if type_elem is not None and type_elem.text:
            type_text = type_elem.text
            if ':' in type_text:
                return type_text.split(':')[-1]
            return type_text
        return None

    def _normalize_type(self, type_name: str) -> str:
                                                  
        type_map = {
            'string': 'string',
            'String': 'string',
            'Boolean': 'boolean',
            'boolean': 'boolean',
            'Number': 'number',
            'number': 'number',
            'Date': 'date',
            'date': 'date',
            'ValueStorage': 'value_storage',
        }
        return type_map.get(type_name, type_name)
