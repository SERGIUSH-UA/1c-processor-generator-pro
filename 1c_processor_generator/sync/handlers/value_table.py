   

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..base_handler import BaseElementHandler, ChangeType, ElementChange

if TYPE_CHECKING:
    from lxml import etree


class ValueTableHandler(BaseElementHandler):
           

    @property
    def element_type_name(self) -> str:
        return "value_table"

    @property
    def yaml_section(self) -> str:
        return "forms[].value_tables"

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
        data['name'] = name if name else "UnknownValueTable"

                                       
        columns = []
        for col in elem.xpath(".//form:Column", namespaces=ns):
            col_name = col.get("name")
            if col_name:
                col_data = {'name': col_name}

                      
                type_elem = col.find(".//v8:Type", namespaces=ns)
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
        tables = {}

        if form_root is None:
            return tables

                                                       
        for attr in form_root.xpath(".//form:Attribute", namespaces=ns):
            type_elem = attr.find(".//v8:Type", namespaces=ns)
            if type_elem is not None and type_elem.text:
                if 'ValueTable' in type_elem.text:
                    name = attr.get("name")
                    if name:
                        tables[name] = attr

        return tables

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
                                      
        if 'forms' not in config or form_index >= len(config['forms']):
            return False

        form = config['forms'][form_index]
        if 'value_tables' not in form:
            form['value_tables'] = []

        existing_names = [vt.get('name') for vt in form['value_tables']]
        if data.get('name') in existing_names:
            return False

        form['value_tables'].append(data)
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
        if 'value_tables' not in form:
            return False

        for idx, vt in enumerate(form['value_tables']):
            if vt.get('name') == name:
                del form['value_tables'][idx]
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
            f"Элементы.{name}",
            f"Items.{name}",
        ]

        for pattern in patterns:
            if pattern in bsl_code:
                references.append(f"BSL code: {pattern}")

        return references
