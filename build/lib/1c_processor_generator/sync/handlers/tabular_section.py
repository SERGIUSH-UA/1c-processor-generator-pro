   

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..base_handler import BaseElementHandler, ChangeType, ElementChange

if TYPE_CHECKING:
    from lxml import etree


class TabularSectionHandler(BaseElementHandler):
           

    @property
    def element_type_name(self) -> str:
        return "tabular_section"

    @property
    def yaml_section(self) -> str:
        return "tabular_sections"

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
        data['name'] = name_elem.text if name_elem is not None and name_elem.text else "UnknownTS"

                                
        synonym = self.get_multilang_text(elem, "Synonym", ns)
        if synonym:
            if 'ru' in synonym:
                data['synonym_ru'] = synonym['ru']
            if 'uk' in synonym:
                data['synonym_uk'] = synonym['uk']
            if 'en' in synonym:
                data['synonym_en'] = synonym['en']

                 
        columns = []
        for col in elem.xpath(".//ns:Attribute", namespaces=ns):
            col_name = col.find(".//ns:Properties/ns:Name", namespaces=ns)
            if col_name is not None and col_name.text:
                col_data = {'name': col_name.text}

                             
                type_elem = col.find(".//ns:Type/v8:Type", namespaces=ns)
                if type_elem is not None and type_elem.text:
                    type_text = type_elem.text
                    if ':' in type_text:
                        col_data['type'] = type_text.split(':')[-1]
                    else:
                        col_data['type'] = type_text

                columns.append(col_data)

        if columns:
            data['columns'] = columns

        return data

    def get_elements_from_tree(
        self,
        tree: "etree._ElementTree",
        namespaces: Optional[Dict[str, str]] = None,
        form_root: Optional["etree._Element"] = None
    ) -> Dict[str, "etree._Element"]:
                                                      
        ns = namespaces or self.NAMESPACES
        sections = {}

        for ts in tree.xpath("//ns:TabularSection", namespaces=ns):
            name_elem = ts.find(".//ns:Properties/ns:Name", namespaces=ns)
            if name_elem is not None and name_elem.text:
                sections[name_elem.text] = ts

        return sections

    def compare_element_details(
        self,
        name: str,
        original: "etree._Element",
        modified: "etree._Element",
        namespaces: Optional[Dict[str, str]] = None
    ) -> List[ElementChange]:
                                           
        ns = namespaces or self.NAMESPACES
        changes = []

                         
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
                                          
        if 'tabular_sections' not in config:
            config['tabular_sections'] = []

        existing_names = [ts.get('name') for ts in config['tabular_sections']]
        if data.get('name') in existing_names:
            return False

        config['tabular_sections'].append(data)
        return True

    def delete_from_yaml(
        self,
        config: Dict,
        name: str,
        form_index: int = 0,
        parent_path: Optional[str] = None,
        force: bool = False
    ) -> bool:
                                               
        if 'tabular_sections' not in config:
            return False

        for idx, ts in enumerate(config['tabular_sections']):
            if ts.get('name') == name:
                del config['tabular_sections'][idx]
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

        return references
