   

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from lxml import etree


class ChangeType(Enum):
                                                
    ADD = "add"
    DELETE = "delete"
    RENAME = "rename"
    PROPERTY_CHANGE = "property_change"
    TYPE_CHANGE = "type_change"


@dataclass
class ElementChange:
                                                             
    change_type: ChangeType
    element_type: str                               
    xpath: str
    old_value: Any
    new_value: Any
    element_name: Optional[str] = None
    property_name: Optional[str] = None
                                            
    parent_path: Optional[str] = None
    insertion_index: Optional[int] = None
    depth: int = 0
    parent_name: Optional[str] = None


class BaseElementHandler(ABC):
           

                                      
    NAMESPACES = {
        'ns': 'http://v8.1c.ru/8.3/MDClasses',
        'v8': 'http://v8.1c.ru/8.1/data/core',
        'form': 'http://v8.1c.ru/8.3/xcf/logform',
        'xr': 'http://v8.1c.ru/8.3/xcf/readable',
    }

    @property
    @abstractmethod
    def element_type_name(self) -> str:
                   
        pass

    @property
    @abstractmethod
    def yaml_section(self) -> str:
                   
        pass

    @property
    def supports_nesting(self) -> bool:
                   
        return False

    @property
    def is_form_level(self) -> bool:
                   
        return False

    @abstractmethod
    def extract_from_xml(
        self,
        elem: "etree._Element",
        namespaces: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
                   
        pass

    @abstractmethod
    def get_elements_from_tree(
        self,
        tree: "etree._ElementTree",
        namespaces: Optional[Dict[str, str]] = None,
        form_root: Optional["etree._Element"] = None
    ) -> Dict[str, "etree._Element"]:
                   
        pass

    @abstractmethod
    def compare_element_details(
        self,
        name: str,
        original: "etree._Element",
        modified: "etree._Element",
        namespaces: Optional[Dict[str, str]] = None
    ) -> List[ElementChange]:
                   
        pass

    @abstractmethod
    def add_to_yaml(
        self,
        config: Dict,
        data: Dict,
        form_index: int = 0,
        parent_path: Optional[str] = None,
        insertion_index: Optional[int] = None
    ) -> bool:
                   
        pass

    @abstractmethod
    def delete_from_yaml(
        self,
        config: Dict,
        name: str,
        form_index: int = 0,
        parent_path: Optional[str] = None,
        force: bool = False
    ) -> bool:
                   
        pass

    def check_references(
        self,
        config: Dict,
        bsl_code: str,
        name: str
    ) -> List[str]:
                   
        return []

                                                              

    def get_multilang_text(
        self,
        elem: "etree._Element",
        prop_name: str,
        namespaces: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
                   
        ns = namespaces or self.NAMESPACES
        result = {}

                                    
        prop_elems = elem.xpath(f".//*[local-name()='{prop_name}']")
        if not prop_elems:
            return result

        prop_elem = prop_elems[0]

                                                    
        items = prop_elem.xpath(".//v8:item", namespaces=ns)
        if items:
            for item in items:
                lang_elem = item.find("v8:lang", namespaces=ns)
                content_elem = item.find("v8:content", namespaces=ns)
                if lang_elem is not None and content_elem is not None:
                    lang = lang_elem.text
                    content = content_elem.text or ""
                    if lang == "ru":
                        result["ru"] = content
                    elif lang == "uk":
                        result["uk"] = content
                    elif lang == "en":
                        result["en"] = content
        else:
                                          
            if prop_elem.text:
                result["ru"] = prop_elem.text

        return result

    def get_xpath(self, elem: "etree._Element") -> str:
                   
        parts = []
        current = elem
        while current is not None:
            parent = current.getparent()
            if parent is not None:
                siblings = [c for c in parent if c.tag == current.tag]
                if len(siblings) > 1:
                    index = siblings.index(current) + 1
                    parts.append(f"{current.tag.split('}')[-1]}[{index}]")
                else:
                    parts.append(current.tag.split('}')[-1])
            else:
                parts.append(current.tag.split('}')[-1])
            current = parent
        return "/" + "/".join(reversed(parts))

    def _create_change(
        self,
        change_type: ChangeType,
        xpath: str,
        old_value: Any,
        new_value: Any,
        element_name: Optional[str] = None,
        property_name: Optional[str] = None,
        **kwargs
    ) -> ElementChange:
                   
        return ElementChange(
            change_type=change_type,
            element_type=self.element_type_name,
            xpath=xpath,
            old_value=old_value,
            new_value=new_value,
            element_name=element_name,
            property_name=property_name,
            **kwargs
        )
