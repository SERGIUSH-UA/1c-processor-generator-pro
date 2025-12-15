   

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..base_handler import BaseElementHandler, ChangeType, ElementChange

if TYPE_CHECKING:
    from lxml import etree


class TemplateHandler(BaseElementHandler):
           

    @property
    def element_type_name(self) -> str:
        return "template"

    @property
    def yaml_section(self) -> str:
        return "templates"

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
        if name_elem is not None and name_elem.text:
            data['name'] = name_elem.text
        else:
                           
            name = elem.get("name")
            data['name'] = name if name else "UnknownTemplate"

                                                                
        type_elem = elem.find(".//ns:Properties/ns:TemplateType", namespaces=ns)
        if type_elem is not None and type_elem.text:
            data['type'] = type_elem.text

                                
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
        templates = {}

                                                      
        for tmpl in tree.xpath("//ns:Template", namespaces=ns):
                                      
            name_elem = tmpl.find(".//ns:Properties/ns:Name", namespaces=ns)
            if name_elem is not None and name_elem.text:
                templates[name_elem.text] = tmpl
            else:
                                                         
                name_elem = tmpl.find("ns:Name", namespaces=ns)
                if name_elem is not None and name_elem.text:
                    templates[name_elem.text] = tmpl

        return templates

    def compare_element_details(
        self,
        name: str,
        original: "etree._Element",
        modified: "etree._Element",
        namespaces: Optional[Dict[str, str]] = None
    ) -> List[ElementChange]:
                                    
        ns = namespaces or self.NAMESPACES
        changes = []

                               
        orig_type = self._get_template_type(original, ns)
        mod_type = self._get_template_type(modified, ns)
        if orig_type != mod_type:
            changes.append(self._create_change(
                ChangeType.TYPE_CHANGE,
                self.get_xpath(modified) + "/TemplateType",
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

        return changes

    def add_to_yaml(
        self,
        config: Dict,
        data: Dict,
        form_index: int = 0,
        parent_path: Optional[str] = None,
        insertion_index: Optional[int] = None
    ) -> bool:
                                   
        if 'templates' not in config:
            config['templates'] = []

                             
        existing_names = [t.get('name') for t in config['templates']]
        if data.get('name') in existing_names:
            return False

                                                       
        if 'type' in data:
            data['type'] = data['type']                                                  

                                
        if insertion_index is not None and 0 <= insertion_index <= len(config['templates']):
            config['templates'].insert(insertion_index, data)
        else:
            config['templates'].append(data)

        return True

    def delete_from_yaml(
        self,
        config: Dict,
        name: str,
        form_index: int = 0,
        parent_path: Optional[str] = None,
        force: bool = False
    ) -> bool:
                                        
        if 'templates' not in config:
            return False

        for idx, tmpl in enumerate(config['templates']):
            if tmpl.get('name') == name:
                del config['templates'][idx]
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
            f'ПолучитьМакет("{name}")',
            f"ПолучитьМакет('{name}')",
            f'GetTemplate("{name}")',
            f"GetTemplate('{name}')",
            f'GetForm("{name}")',                                      
            f'"{name}"',                            
        ]

        for pattern in patterns:
            if pattern in bsl_code:
                references.append(f"BSL code: {pattern}")

                                                                            
        if 'templates' in config:
            for tmpl in config['templates']:
                if tmpl.get('name') == name and tmpl.get('auto_field'):
                    field_name = tmpl.get('field_name', f'{name}Field')
                    references.append(
                        f"Auto-generated form element: {field_name} "
                        f"(auto_field=true)"
                    )

                                                                             
        if 'forms' in config:
            for form_idx, form in enumerate(config['forms']):
                if 'elements' not in form:
                    continue

                for elem_idx, element in enumerate(form['elements']):
                                                                   
                    if element.get('template') == name:
                        references.append(
                            f"Form element: forms[{form_idx}].elements[{elem_idx}] "
                            f"(name={element.get('name')}) references template"
                        )

        return references

                                                               

    def _get_template_type(
        self,
        elem: "etree._Element",
        ns: Dict[str, str]
    ) -> Optional[str]:
                                                 
        type_elem = elem.find(".//ns:Properties/ns:TemplateType", namespaces=ns)
        if type_elem is not None and type_elem.text:
            return type_elem.text
        return None
