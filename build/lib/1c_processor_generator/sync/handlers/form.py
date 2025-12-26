   

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..base_handler import BaseElementHandler, ChangeType, ElementChange

if TYPE_CHECKING:
    from lxml import etree


class FormHandler(BaseElementHandler):
           

    @property
    def element_type_name(self) -> str:
        return "form"

    @property
    def yaml_section(self) -> str:
        return "forms"

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

                                              
        name_elem = elem.find(".//ns:Name", namespaces=ns)
        if name_elem is not None and name_elem.text:
            data['name'] = name_elem.text
        else:
                           
            name = elem.get("name")
            data['name'] = name if name else "UnknownForm"

        return data

    def get_elements_from_tree(
        self,
        tree: "etree._ElementTree",
        namespaces: Optional[Dict[str, str]] = None,
        form_root: Optional["etree._Element"] = None
    ) -> Dict[str, "etree._Element"]:
                                           
        ns = namespaces or self.NAMESPACES
        forms = {}

                                                      
        for form in tree.xpath("//ns:Form", namespaces=ns):
            name_elem = form.find(".//ns:Name", namespaces=ns)
            if name_elem is not None and name_elem.text:
                forms[name_elem.text] = form

        return forms

    def compare_element_details(
        self,
        name: str,
        original: "etree._Element",
        modified: "etree._Element",
        namespaces: Optional[Dict[str, str]] = None
    ) -> List[ElementChange]:
                                                               
                                                                
                                                       
        return []

    def add_to_yaml(
        self,
        config: Dict,
        data: Dict,
        form_index: int = 0,
        parent_path: Optional[str] = None,
        insertion_index: Optional[int] = None
    ) -> bool:
                               
        if 'forms' not in config:
            config['forms'] = []

        existing_names = [f.get('name') for f in config['forms']]
        if data.get('name') in existing_names:
            return False

        config['forms'].append(data)
        return True

    def delete_from_yaml(
        self,
        config: Dict,
        name: str,
        form_index: int = 0,
        parent_path: Optional[str] = None,
        force: bool = False
    ) -> bool:
                                    
        if 'forms' not in config:
            return False

        for idx, form in enumerate(config['forms']):
            if form.get('name') == name:
                del config['forms'][idx]
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
            f'ОткрытьФорму("{name}"',
            f"ОткрытьФорму('{name}'",
            f'OpenForm("{name}"',
            f"OpenForm('{name}'",
        ]

        for pattern in patterns:
            if pattern in bsl_code:
                references.append(f"BSL code: {pattern}")

        return references
