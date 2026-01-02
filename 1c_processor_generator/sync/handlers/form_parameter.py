   

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..base_handler import BaseElementHandler, ChangeType, ElementChange

if TYPE_CHECKING:
    from lxml import etree


class FormParameterHandler(BaseElementHandler):
           

    @property
    def element_type_name(self) -> str:
        return "form_parameter"

    @property
    def yaml_section(self) -> str:
        return "forms[].parameters"

    @property
    def is_form_level(self) -> bool:
        return True

    def extract_from_xml(
        self,
        elem: "etree._Element",
        namespaces: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
                                                   
        ns = namespaces or self.NAMESPACES
        data: Dict[str, Any] = {}

              
        name = elem.get("name")
        data['name'] = name if name else "UnknownParameter"

              
        type_elem = elem.find(".//v8:Type", namespaces=ns)
        if type_elem is not None and type_elem.text:
            type_text = type_elem.text
                                                                
            if ':' in type_text:
                type_name = type_text.split(':')[-1]
            else:
                type_name = type_text
            data['type'] = self._normalize_type(type_name)

                                
        key_param_elem = elem.find(".//*[local-name()='KeyParameter']")
        if key_param_elem is not None and key_param_elem.text:
            if key_param_elem.text.lower() == 'true':
                data['key_parameter'] = True

                                           
        synonym = self.get_multilang_text(elem, "Synonym", ns)
        if synonym:
            if 'ru' in synonym:
                data['synonym_ru'] = synonym['ru']
            if 'uk' in synonym:
                data['synonym_uk'] = synonym['uk']
            if 'en' in synonym:
                data['synonym_en'] = synonym['en']

        return data

    def get_elements_from_tree(
        self,
        tree: "etree._ElementTree",
        namespaces: Optional[Dict[str, str]] = None,
        form_root: Optional["etree._Element"] = None
    ) -> Dict[str, "etree._Element"]:
                                                
        ns = namespaces or self.NAMESPACES
        parameters = {}

        if form_root is None:
            return parameters

                                                   
        for param in form_root.xpath(".//form:Parameters/form:Parameter", namespaces=ns):
            name = param.get("name")
            if name:
                parameters[name] = param

                                                        
        if not parameters:
            for param in form_root.xpath(".//*[local-name()='Parameter']"):
                name = param.get("name")
                if name:
                    parameters[name] = param

        return parameters

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

                               
        orig_key = self._get_key_parameter(original)
        mod_key = self._get_key_parameter(modified)
        if orig_key != mod_key:
            changes.append(self._create_change(
                ChangeType.PROPERTY_CHANGE,
                self.get_xpath(modified) + "/KeyParameter",
                orig_key,
                mod_key,
                element_name=name,
                property_name="key_parameter"
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

        return changes

    def add_to_yaml(
        self,
        config: Dict,
        data: Dict,
        form_index: int = 0,
        parent_path: Optional[str] = None,
        insertion_index: Optional[int] = None
    ) -> bool:
                                         
        if 'forms' not in config or form_index >= len(config['forms']):
            return False

        form = config['forms'][form_index]
        if 'parameters' not in form:
            form['parameters'] = []

                             
        existing_names = [p.get('name') for p in form['parameters']]
        if data.get('name') in existing_names:
            return False

                                                                 
        if any(k.startswith('synonym_') for k in data.keys()):
            synonym = {}
            for lang in ('ru', 'uk', 'en'):
                key = f'synonym_{lang}'
                if key in data:
                    synonym[lang] = data.pop(key)
            if synonym:
                data['synonym'] = synonym

                                
        if insertion_index is not None and 0 <= insertion_index <= len(form['parameters']):
            form['parameters'].insert(insertion_index, data)
        else:
            form['parameters'].append(data)

        return True

    def delete_from_yaml(
        self,
        config: Dict,
        name: str,
        form_index: int = 0,
        parent_path: Optional[str] = None,
        force: bool = False
    ) -> bool:
                                              
        if 'forms' not in config or form_index >= len(config['forms']):
            return False

        form = config['forms'][form_index]
        if 'parameters' not in form:
            return False

        for idx, param in enumerate(form['parameters']):
            if param.get('name') == name:
                del form['parameters'][idx]
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
            f"Параметры.{name}",
            f"Parameters.{name}",
            f'"{name}"',
            f"'{name}'",
        ]

        for pattern in patterns:
            if pattern in bsl_code:
                references.append(f"BSL code: {pattern}")

        return references

                                                               

    def _get_type(
        self,
        elem: "etree._Element",
        ns: Dict[str, str]
    ) -> Optional[str]:
                                                  
        type_elem = elem.find(".//v8:Type", namespaces=ns)
        if type_elem is not None and type_elem.text:
            type_text = type_elem.text
            if ':' in type_text:
                return type_text.split(':')[-1]
            return type_text
        return None

    def _get_key_parameter(self, elem: "etree._Element") -> bool:
                                                       
        key_elem = elem.find(".//*[local-name()='KeyParameter']")
        if key_elem is not None and key_elem.text:
            return key_elem.text.lower() == 'true'
        return False

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
            'DateTime': 'date',
            'dateTime': 'date',
        }
        return type_map.get(type_name, type_name)
