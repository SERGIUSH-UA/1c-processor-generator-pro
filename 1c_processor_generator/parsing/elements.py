   

from typing import Dict, Optional, List, Any, Callable
from ..models import FormElement
from .schemas import SCHEMAS, ElementSchema, COLUMN_GROUP_ALLOWED_CHILDREN, get_schema
from .extractors import normalize_multilang, extract_props


class ElementParser:
           

    def __init__(self):
                                                         
        self._custom_parsers: Dict[str, Callable[[Dict[str, Any]], Optional[FormElement]]] = {
            "Pages": self._parse_pages,
            "ColumnGroup": self._parse_column_group,
        }

    def parse(self, config: Dict[str, Any]) -> Optional[FormElement]:
                   
                                     
        config = normalize_multilang(config)
        elem_type = config.get("type")

        if not elem_type:
            print("⚠️ Element config missing 'type' field")
            return None

                        
        if elem_type in self._custom_parsers:
            return self._custom_parsers[elem_type](config)

                              
        schema = get_schema(elem_type)
        if not schema:
            print(f"⚠️ Unknown element type: {elem_type}")
            return None

        return self._parse_by_schema(config, schema)

    def _parse_by_schema(self, config: Dict[str, Any], schema: ElementSchema) -> FormElement:
                   
        props = extract_props(config, schema)

                                                                                   
        tabular_section = None
        if schema.has_tabular_section:
            tabular_section = self._get_tabular_section(config, props)

        elem = FormElement(
            element_type=schema.element_type,
            name=config["name"],
            attribute=config.get("attribute") if schema.has_attribute else None,
            command=config.get("command") if schema.has_command else None,
            tabular_section=tabular_section,
            event_handlers=config.get("events", {}),
            properties=props,
        )

                                             
        if schema.has_children:
            children_key = schema.children_key
                                                               
            children_config = config.get(children_key, config.get("child_items", []))
            child_items = self._parse_children(children_config)
            elem.child_items = child_items

        return elem

    def _parse_children(self, children_config: List[Dict[str, Any]]) -> List[FormElement]:
                   
        children = []
        for child_config in children_config:
            child = self.parse(child_config)
            if child:
                children.append(child)
        return children

    def _get_tabular_section(self, config: Dict[str, Any], props: Dict[str, Any]) -> Optional[str]:
                   
                                                                                    
        if "value_table" in config:
            props["is_value_table"] = True
            return config["value_table"]
        return config.get("tabular_section")

                                                                               
                                       
                                                                               

    def _parse_pages(self, config: Dict[str, Any]) -> FormElement:
                   
        schema = get_schema("Pages")
        props = extract_props(config, schema)

        pages_elem = FormElement(
            element_type="Pages",
            name=config["name"],
            properties=props,
        )

                          
        pages_config = config.get("pages", [])
        for page_config in pages_config:
            page_config = normalize_multilang(page_config)
            title = page_config.get("title", page_config["name"])

                                                
            page = FormElement(
                element_type="Page",
                name=page_config["name"],
                properties={
                    "title_ru": page_config.get("title_ru", title),
                    "title_uk": page_config.get("title_uk", title),
                    "title_en": page_config.get("title_en", title),
                },
            )

                                            
            children_config = page_config.get("elements", page_config.get("child_items", []))
            for child_config in children_config:
                child = self.parse(child_config)
                if child:
                    page.child_items.append(child)

            pages_elem.child_items.append(page)

        return pages_elem

    def _parse_column_group(self, config: Dict[str, Any]) -> FormElement:
                   
        schema = get_schema("ColumnGroup")
        props = extract_props(config, schema)
        name = config["name"]

                                                          
        children_config = config.get("elements", config.get("child_items", []))
        child_items = []

        for child_config in children_config:
            child_type = child_config.get("type")

                                                
            if child_type not in COLUMN_GROUP_ALLOWED_CHILDREN:
                print(
                    f"⚠️ ColumnGroup '{name}' може містити тільки field елементи "
                    f"({', '.join(COLUMN_GROUP_ALLOWED_CHILDREN)}). Знайдено: {child_type}"
                )
                continue

            child = self.parse(child_config)
            if child:
                child_items.append(child)

        return FormElement(
            element_type="ColumnGroup",
            name=name,
            properties=props,
            child_items=child_items,
        )
