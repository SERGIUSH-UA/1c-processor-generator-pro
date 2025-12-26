   

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..base_handler import BaseElementHandler, ChangeType, ElementChange

if TYPE_CHECKING:
    from lxml import etree


class FormAttributeHandler(BaseElementHandler):
           

    @property
    def element_type_name(self) -> str:
        return "form_attribute"

    @property
    def yaml_section(self) -> str:
        return "forms[].form_attributes"

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
        data['name'] = name if name else "UnknownFormAttr"

              
        type_elem = elem.find(".//v8:Type", namespaces=ns)
        if type_elem is not None and type_elem.text:
            type_text = type_elem.text
            if ':' in type_text:
                data['type'] = type_text.split(':')[-1]
            else:
                data['type'] = type_text

        return data

    def get_elements_from_tree(
        self,
        tree: "etree._ElementTree",
        namespaces: Optional[Dict[str, str]] = None,
        form_root: Optional["etree._Element"] = None
    ) -> Dict[str, "etree._Element"]:
                                                
        ns = namespaces or self.NAMESPACES
        attrs = {}

        if form_root is None:
            return attrs

                                                 
        for attr in form_root.xpath(".//form:Attribute", namespaces=ns):
            type_elem = attr.find(".//v8:Type", namespaces=ns)
            is_value_table = False
            if type_elem is not None and type_elem.text:
                if 'ValueTable' in type_elem.text:
                    is_value_table = True

            if not is_value_table:
                name = attr.get("name")
                                                
                if name and name not in ('Object', 'Объект'):
                    attrs[name] = attr

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
        if 'form_attributes' not in form:
            form['form_attributes'] = []

        existing_names = [fa.get('name') for fa in form['form_attributes']]
        if data.get('name') in existing_names:
            return False

        form['form_attributes'].append(data)
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
        if 'form_attributes' not in form:
            return False

        for idx, fa in enumerate(form['form_attributes']):
            if fa.get('name') == name:
                del form['form_attributes'][idx]
                return True

        return False

    def check_references(
        self,
        config: Dict,
        bsl_code: str,
        name: str
    ) -> List[str]:
                                                            
        references = []

        if name in bsl_code:
            references.append(f"BSL code: {name}")

        return references

    def _get_type(self, elem: "etree._Element", ns: Dict[str, str]) -> Optional[str]:
                                        
        type_elem = elem.find(".//v8:Type", namespaces=ns)
        if type_elem is not None and type_elem.text:
            type_text = type_elem.text
            if ':' in type_text:
                return type_text.split(':')[-1]
            return type_text
        return None
