   

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
try:
    from lxml import etree as ET
    from lxml import etree                  
except ImportError:
    import xml.etree.ElementTree as ET
    etree = ET                           
import logging

from .hierarchical_extractor import HierarchicalExtractor, ElementNode           

logger = logging.getLogger(__name__)


class ChangeType(Enum):
                                           
    RENAME = "rename"
    TYPE_CHANGE = "type_change"
    PROPERTY_CHANGE = "property_change"
    ADD = "add"
    DELETE = "delete"


class ElementType(Enum):
                                                             
    ATTRIBUTE = "attribute"
    FORM_ELEMENT = "form_element"
    COMMAND = "command"
    TABULAR_SECTION = "tabular_section"
    TABULAR_SECTION_COLUMN = "tabular_section_column"
    VALUE_TABLE = "value_table"                                      
    VALUE_TABLE_COLUMN = "value_table_column"
    FORM_ATTRIBUTE = "form_attribute"
    FORM = "form"                                  
    TEMPLATE = "template"                               
    FORM_PARAMETER = "form_parameter"                            


@dataclass
class XMLChange:
                                                                                

    change_type: ChangeType
    element_type: ElementType
    xpath: str                           
    old_value: Any
    new_value: Any
    element_name: Optional[str] = None                                                  
    property_name: Optional[str] = None                            

                                                     
    parent_path: Optional[str] = None                                                      
    insertion_index: Optional[int] = None                                          
    depth: int = 0                                 
    parent_name: Optional[str] = None                          

    def __str__(self) -> str:
                                                   
        if self.change_type == ChangeType.RENAME:
            return f"{self.element_type.value} renamed: '{self.old_value}' → '{self.new_value}'"

        elif self.change_type == ChangeType.PROPERTY_CHANGE:
            return (f"{self.element_type.value} '{self.element_name}' "
                   f"property '{self.property_name}' changed: "
                   f"'{self.old_value}' → '{self.new_value}'")

        elif self.change_type == ChangeType.TYPE_CHANGE:
            return (f"{self.element_type.value} '{self.element_name}' "
                   f"type changed: {self.old_value} → {self.new_value}")

        elif self.change_type == ChangeType.ADD:
            return f"{self.element_type.value} added: '{self.new_value}'"

        elif self.change_type == ChangeType.DELETE:
            return f"{self.element_type.value} deleted: '{self.old_value}'"

        return f"{self.change_type.value} in {self.element_type.value}"


class XMLDiffer:
           

                                         
    NAMESPACES = {
        'v8': 'http://v8.1c.ru/8.1/data/core',
        'ns': 'http://v8.1c.ru/8.3/MDClasses',                                         
        'xr': 'http://v8.1c.ru/8.3/xcf/readable',
        'app': 'http://v8.1c.ru/8.2/managed-application/core',
        'form': 'http://v8.1c.ru/8.3/xcf/logform',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    def __init__(self, original_xml_path: str, modified_xml_path: str):
                   
        self.original_xml_path = original_xml_path
        self.modified_xml_path = modified_xml_path

        try:
                                  
            self.original_tree = ET.parse(original_xml_path)
            self.modified_tree = ET.parse(modified_xml_path)

                                           
            self.original_form_trees: Dict[str, ET.ElementTree] = {}
            self.modified_form_trees: Dict[str, ET.ElementTree] = {}

            original_form_paths = self._get_form_xml_paths(original_xml_path)
            modified_form_paths = self._get_form_xml_paths(modified_xml_path)

                                  
            for form_name, form_path in original_form_paths.items():
                try:
                    self.original_form_trees[form_name] = ET.parse(form_path)
                    logger.debug(f"Parsed original Form.xml: {form_name}")
                except Exception as e:
                    logger.warning(f"Failed to parse original {form_path}: {e}")

                                  
            for form_name, form_path in modified_form_paths.items():
                try:
                    self.modified_form_trees[form_name] = ET.parse(form_path)
                    logger.debug(f"Parsed modified Form.xml: {form_name}")
                except Exception as e:
                    logger.warning(f"Failed to parse modified {form_path}: {e}")

        except Exception as e:
            logger.error(f"Failed to parse XML files: {e}")
            raise

        self.changes: List[XMLChange] = []

    def detect_changes(self) -> List[XMLChange]:
                   
        logger.info("Detecting changes between XML files...")
        self.changes = []

                                         
        self._compare_attributes()
        self._compare_forms()                                   
        self._compare_form_elements()
        self._compare_commands()
        self._compare_tabular_sections()
        self._compare_value_tables()           
        self._compare_form_attributes()           
        self._compare_templates()                               
        self._compare_form_parameters()                            

        logger.info(f"Detected {len(self.changes)} changes")
        return self.changes

    def _compare_attributes(self):
                                                 
        logger.debug("Comparing processor attributes...")

        original_attrs = self._get_processor_attributes(self.original_tree)
        modified_attrs = self._get_processor_attributes(self.modified_tree)

                                                           
        self._compare_elements(
            original_attrs,
            modified_attrs,
            ElementType.ATTRIBUTE,
            self._compare_attribute_details
        )

    def _compare_form_elements(self):
                   
        logger.debug("Comparing form elements...")

                                                                        
        form_original = self._get_form_xml(self.original_tree, form_name="Форма")
        form_modified = self._get_form_xml(self.modified_tree, form_name="Форма")

        if form_original is None or form_modified is None:
                                                                                     
            if form_original is None:
                logger.warning("Original Form.xml not found - cannot detect form element changes")
            if form_modified is None:
                logger.warning("Modified Form.xml not found - cannot detect form element changes")
            return

                                              
        original_roots = self._get_form_elements_hierarchical(form_original, form_index=0)
        modified_roots = self._get_form_elements_hierarchical(form_modified, form_index=0)

                                      
        self._compare_form_elements_hierarchical(original_roots, modified_roots)

    def _compare_form_elements_hierarchical(
        self,
        original_roots: List[ElementNode],
        modified_roots: List[ElementNode]
    ):
                   
                                                          
        extractor = HierarchicalExtractor()
        tree_changes = extractor.compare_trees(original_roots, modified_roots)

                                                              
        for added in tree_changes['added']:
            self.changes.append(XMLChange(
                change_type=ChangeType.ADD,
                element_type=ElementType.FORM_ELEMENT,
                xpath=f"//form:Item[@name='{added['name']}']",
                old_value=None,
                new_value=added['name'],
                element_name=added['name'],
                parent_path=added['path'].rsplit('.child_items[', 1)[0] if '.child_items[' in added['path'] else None,
                insertion_index=int(added['path'].rsplit('[', 1)[1].rstrip(']')) if '[' in added['path'] else 0,
                depth=added['depth'],
                parent_name=added.get('parent')
            ))

        for deleted in tree_changes['deleted']:
            self.changes.append(XMLChange(
                change_type=ChangeType.DELETE,
                element_type=ElementType.FORM_ELEMENT,
                xpath=f"//form:Item[@name='{deleted['name']}']",
                old_value=deleted['name'],
                new_value=None,
                element_name=deleted['name'],
                parent_path=deleted['path'].rsplit('.child_items[', 1)[0] if '.child_items[' in deleted['path'] else None,
                insertion_index=None,
                depth=deleted['depth'],
                parent_name=deleted.get('parent')
            ))

        for moved in tree_changes['moved']:
                                                     
            self.changes.append(XMLChange(
                change_type=ChangeType.PROPERTY_CHANGE,
                element_type=ElementType.FORM_ELEMENT,
                xpath=f"//form:Item[@name='{moved['name']}']",
                old_value=moved['from_path'],
                new_value=moved['to_path'],
                element_name=moved['name'],
                property_name='position',
                parent_path=moved['to_path'].rsplit('.child_items[', 1)[0] if '.child_items[' in moved['to_path'] else None,
                insertion_index=moved['to_index'],
                depth=0,                        
                parent_name=moved.get('to_parent')
            ))

        for modified in tree_changes['modified']:
                                     
            self.changes.append(XMLChange(
                change_type=ChangeType.PROPERTY_CHANGE,
                element_type=ElementType.FORM_ELEMENT,
                xpath=f"//form:Item[@name='{modified['name']}']",
                old_value=modified['changes'],
                new_value=modified['changes'],
                element_name=modified['name'],
                property_name='attributes',
                parent_path=modified['path'].rsplit('.child_items[', 1)[0] if '.child_items[' in modified['path'] else None
            ))

    def _compare_commands(self):
                   
        logger.debug("Comparing commands...")

                                                   
        form_original = self._get_form_xml(self.original_tree, form_name="Форма")
        form_modified = self._get_form_xml(self.modified_tree, form_name="Форма")

        if form_original is None or form_modified is None:
            if form_original is None:
                logger.warning("Original Form.xml not found - cannot detect command changes")
            if form_modified is None:
                logger.warning("Modified Form.xml not found - cannot detect command changes")
                                                                      
            if form_original is None:
                form_original = self.original_tree.getroot()
            if form_modified is None:
                form_modified = self.modified_tree.getroot()

        original_commands = self._get_commands_from_form(form_original)
        modified_commands = self._get_commands_from_form(form_modified)

        self._compare_elements(
            original_commands,
            modified_commands,
            ElementType.COMMAND,
            self._compare_command_details
        )

    def _compare_tabular_sections(self):
                                                         
        logger.debug("Comparing tabular sections...")

        original_sections = self._get_tabular_sections(self.original_tree)
        modified_sections = self._get_tabular_sections(self.modified_tree)

                                             
        self._compare_elements(
            original_sections,
            modified_sections,
            ElementType.TABULAR_SECTION,
            self._compare_tabular_section_details
        )

                                             
        for name in original_sections.keys() & modified_sections.keys():
            orig_cols = self._get_tabular_columns(original_sections[name])
            mod_cols = self._get_tabular_columns(modified_sections[name])

            self._compare_elements(
                orig_cols,
                mod_cols,
                ElementType.TABULAR_SECTION_COLUMN,
                self._compare_column_details,
                parent_name=name
            )

    def _compare_value_tables(self):
                   
        logger.debug("Comparing value tables...")

                        
        orig_form = self._get_form_xml(self.original_tree)
        mod_form = self._get_form_xml(self.modified_tree)

        if orig_form is None or mod_form is None:
            logger.debug("No form XML found, skipping value table comparison")
            return

                          
        original_tables = self._get_value_tables(orig_form)
        modified_tables = self._get_value_tables(mod_form)

                                         
        self._compare_elements(
            original_tables,
            modified_tables,
            ElementType.VALUE_TABLE,
            self._compare_value_table_details
        )

                                                 
        for name in original_tables.keys() & modified_tables.keys():
            orig_cols = self._get_value_table_columns(original_tables[name])
            mod_cols = self._get_value_table_columns(modified_tables[name])

            self._compare_elements(
                orig_cols,
                mod_cols,
                ElementType.VALUE_TABLE_COLUMN,
                self._compare_column_details,
                parent_name=name
            )

    def _compare_form_attributes(self):
                   
        logger.debug("Comparing form attributes...")

                        
        orig_form = self._get_form_xml(self.original_tree)
        mod_form = self._get_form_xml(self.modified_tree)

        if orig_form is None or mod_form is None:
            logger.debug("No form XML found, skipping form attribute comparison")
            return

                             
        original_attrs = self._get_form_attributes(orig_form)
        modified_attrs = self._get_form_attributes(mod_form)

                                 
        self._compare_elements(
            original_attrs,
            modified_attrs,
            ElementType.FORM_ATTRIBUTE,
            self._compare_form_attribute_details
        )

    def _compare_templates(self):
                   
        logger.debug("Comparing templates...")

        original_templates = self._get_templates(self.original_tree)
        modified_templates = self._get_templates(self.modified_tree)

                           
        self._compare_elements(
            original_templates,
            modified_templates,
            ElementType.TEMPLATE,
            self._compare_template_details
        )

    def _compare_form_parameters(self):
                   
        logger.debug("Comparing form parameters...")

                        
        orig_form = self._get_form_xml(self.original_tree)
        mod_form = self._get_form_xml(self.modified_tree)

        if orig_form is None or mod_form is None:
            logger.debug("No form XML found, skipping form parameter comparison")
            return

                             
        original_params = self._get_form_parameters(orig_form)
        modified_params = self._get_form_parameters(mod_form)

                                 
        self._compare_elements(
            original_params,
            modified_params,
            ElementType.FORM_PARAMETER,
            self._compare_form_parameter_details
        )

    def _compare_elements(
        self,
        original: Dict[str, etree._Element],
        modified: Dict[str, etree._Element],
        element_type: ElementType,
        detail_comparer,
        parent_name: Optional[str] = None
    ):
                   
        original_names = set(original.keys())
        modified_names = set(modified.keys())

                             
        added = modified_names - original_names
        for name in added:
            xpath = self._get_element_xpath(modified[name])
            self.changes.append(XMLChange(
                change_type=ChangeType.ADD,
                element_type=element_type,
                xpath=xpath,
                old_value=None,
                new_value=name,
                element_name=parent_name
            ))

                               
        deleted = original_names - modified_names
        for name in deleted:
            xpath = self._get_element_xpath(original[name])
            self.changes.append(XMLChange(
                change_type=ChangeType.DELETE,
                element_type=element_type,
                xpath=xpath,
                old_value=name,
                new_value=None,
                element_name=parent_name
            ))

                                                                                          
        if added and deleted:
            self._detect_renames(original, modified, added, deleted, element_type)

                                            
        common = original_names & modified_names
        for name in common:
            detail_comparer(name, original[name], modified[name])

    def _detect_renames(
        self,
        original: Dict[str, etree._Element],
        modified: Dict[str, etree._Element],
        added: set,
        deleted: set,
        element_type: ElementType
    ):
                   
                                                                 
        for old_name in list(deleted):
            for new_name in list(added):
                old_elem = original[old_name]
                new_elem = modified[new_name]

                                                                          
                if self._elements_similar(old_elem, new_elem):
                    xpath = self._get_element_xpath(new_elem)
                    self.changes.append(XMLChange(
                        change_type=ChangeType.RENAME,
                        element_type=element_type,
                        xpath=xpath,
                        old_value=old_name,
                        new_value=new_name
                    ))
                    deleted.remove(old_name)
                    added.remove(new_name)
                    break

    def _elements_similar(self, elem1: etree._Element, elem2: etree._Element) -> bool:
                   
                              
        if elem1.tag != elem2.tag:
            return False

                                          
        if len(elem1) != len(elem2):
            return False

                                                           
                                                                                   
                                                      
        return True

                                                                         

    def _compare_attribute_details(
        self,
        name: str,
        original: etree._Element,
        modified: etree._Element
    ):
                                                       
                      
        orig_type = self._get_attribute_type(original)
        mod_type = self._get_attribute_type(modified)
        if orig_type != mod_type:
            xpath = self._get_element_xpath(modified) + "/Type"
            self.changes.append(XMLChange(
                change_type=ChangeType.TYPE_CHANGE,
                element_type=ElementType.ATTRIBUTE,
                xpath=xpath,
                old_value=orig_type,
                new_value=mod_type,
                element_name=name
            ))

                                 
        self._compare_multilang_property(
            name, original, modified, "Synonym", ElementType.ATTRIBUTE
        )

                         
        self._compare_multilang_property(
            name, original, modified, "Tooltip", ElementType.ATTRIBUTE
        )

    def _compare_form_element_details(
        self,
        name: str,
        original: etree._Element,
        modified: etree._Element
    ):
                                                
                       
        self._compare_multilang_property(
            name, original, modified, "Title", ElementType.FORM_ELEMENT
        )

                         
        self._compare_multilang_property(
            name, original, modified, "ToolTip", ElementType.FORM_ELEMENT
        )

                                       
        orig_width = self._get_element_text(original, ".//Width")
        mod_width = self._get_element_text(modified, ".//Width")
        if orig_width != mod_width:
            xpath = self._get_element_xpath(modified) + "/Width"
            self.changes.append(XMLChange(
                change_type=ChangeType.PROPERTY_CHANGE,
                element_type=ElementType.FORM_ELEMENT,
                xpath=xpath,
                old_value=orig_width,
                new_value=mod_width,
                element_name=name,
                property_name="width"
            ))

    def _compare_command_details(
        self,
        name: str,
        original: etree._Element,
        modified: etree._Element
    ):
                                           
                       
        self._compare_multilang_property(
            name, original, modified, "Title", ElementType.COMMAND
        )

                         
        self._compare_multilang_property(
            name, original, modified, "ToolTip", ElementType.COMMAND
        )

    def _compare_tabular_section_details(
        self,
        name: str,
        original: etree._Element,
        modified: etree._Element
    ):
                                                   
        self._compare_multilang_property(
            name, original, modified, "Synonym", ElementType.TABULAR_SECTION
        )

    def _compare_column_details(
        self,
        name: str,
        original: etree._Element,
        modified: etree._Element
    ):
                                                          
                      
        orig_type = self._get_attribute_type(original)
        mod_type = self._get_attribute_type(modified)
        if orig_type != mod_type:
            xpath = self._get_element_xpath(modified) + "/Type"
            self.changes.append(XMLChange(
                change_type=ChangeType.TYPE_CHANGE,
                element_type=ElementType.TABULAR_SECTION_COLUMN,
                xpath=xpath,
                old_value=orig_type,
                new_value=mod_type,
                element_name=name
            ))

    def _compare_value_table_details(
        self,
        name: str,
        original: etree._Element,
        modified: etree._Element
    ):
                   
                                                                                     
                                                                            
        pass

    def _compare_form_attribute_details(
        self,
        name: str,
        original: etree._Element,
        modified: etree._Element
    ):
                   
                                                                    
                                                        
        pass

    def _compare_template_details(
        self,
        name: str,
        original: etree._Element,
        modified: etree._Element
    ):
                   
                               
        orig_type = self._get_template_type(original)
        mod_type = self._get_template_type(modified)
        if orig_type != mod_type:
            xpath = self._get_element_xpath(modified) + "/TemplateType"
            self.changes.append(XMLChange(
                change_type=ChangeType.TYPE_CHANGE,
                element_type=ElementType.TEMPLATE,
                xpath=xpath,
                old_value=orig_type,
                new_value=mod_type,
                element_name=name
            ))

                         
        self._compare_multilang_property(
            name, original, modified, "Synonym", ElementType.TEMPLATE
        )

    def _compare_form_parameter_details(
        self,
        name: str,
        original: etree._Element,
        modified: etree._Element
    ):
                   
                      
        orig_type = self._get_parameter_type(original)
        mod_type = self._get_parameter_type(modified)
        if orig_type != mod_type:
            xpath = self._get_element_xpath(modified) + "/Type"
            self.changes.append(XMLChange(
                change_type=ChangeType.TYPE_CHANGE,
                element_type=ElementType.FORM_PARAMETER,
                xpath=xpath,
                old_value=orig_type,
                new_value=mod_type,
                element_name=name
            ))

                              
        orig_key = self._get_key_parameter(original)
        mod_key = self._get_key_parameter(modified)
        if orig_key != mod_key:
            xpath = self._get_element_xpath(modified) + "/KeyParameter"
            self.changes.append(XMLChange(
                change_type=ChangeType.PROPERTY_CHANGE,
                element_type=ElementType.FORM_PARAMETER,
                xpath=xpath,
                old_value=orig_key,
                new_value=mod_key,
                element_name=name,
                property_name="key_parameter"
            ))

                         
        self._compare_multilang_property(
            name, original, modified, "Synonym", ElementType.FORM_PARAMETER
        )

    def _get_template_type(self, elem: etree._Element) -> Optional[str]:
                                                                          
        type_elem = elem.find(".//ns:Properties/ns:TemplateType", namespaces=self.NAMESPACES)
        if type_elem is not None and type_elem.text:
            return type_elem.text
        return None

    def _get_parameter_type(self, elem: etree._Element) -> Optional[str]:
                                      
        type_elem = elem.find(".//v8:Type", namespaces=self.NAMESPACES)
        if type_elem is not None and type_elem.text:
            type_text = type_elem.text
            if ':' in type_text:
                return type_text.split(':')[-1]
            return type_text
        return None

    def _get_key_parameter(self, elem: etree._Element) -> bool:
                                                         
        key_elem = elem.find(".//*[local-name()='KeyParameter']")
        if key_elem is not None and key_elem.text:
            return key_elem.text.lower() == 'true'
        return False

    def _compare_multilang_property(
        self,
        element_name: str,
        original: etree._Element,
        modified: etree._Element,
        property_name: str,
        element_type: ElementType
    ):
                   
        orig_values = self._get_multilang_text(original, property_name)
        mod_values = self._get_multilang_text(modified, property_name)

                                                                                
                                                                        
                                           
        common_langs = set(orig_values.keys()) & set(mod_values.keys())

                                                  
        has_changes = False
        changed_langs = []
        for lang in common_langs:
            if orig_values[lang] != mod_values[lang]:
                has_changes = True
                changed_langs.append(lang)

                                                       
                                                                  
        if has_changes:
            xpath = self._get_element_xpath(modified) + f"/{property_name}"
                                                                     
            old_parts = [f"{lang}:'{orig_values[lang]}'" for lang in changed_langs]
            new_parts = [f"{lang}:'{mod_values[lang]}'" for lang in changed_langs]
            old_str = ", ".join(old_parts)
            new_str = ", ".join(new_parts)

            self.changes.append(XMLChange(
                change_type=ChangeType.PROPERTY_CHANGE,
                element_type=element_type,
                xpath=xpath,
                old_value=old_str,
                new_value=new_str,
                element_name=element_name,
                property_name=property_name.lower()
            ))

            logger.debug(f"Multilang property changed: {property_name} - {changed_langs}")

                                                                      

    def _get_processor_attributes(self, tree: etree._ElementTree) -> Dict[str, etree._Element]:
                                                    
        attrs = {}
                                        
        for attr in tree.xpath("//ns:Attribute", namespaces=self.NAMESPACES):
            name_elem = attr.find(".//ns:Properties/ns:Name", namespaces=self.NAMESPACES)
            if name_elem is not None and name_elem.text:
                attrs[name_elem.text] = attr
        return attrs

    def _get_form_xml_paths(self, main_xml_path: str) -> Dict[str, str]:
                   
        import json
        from pathlib import Path

        main_path = Path(main_xml_path)
        parent_dir = main_path.parent

                                                                                
        processor_name = None
        metadata_path = parent_dir / "metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    processor_name = metadata.get("processor_name")
                    if processor_name:
                        logger.debug(f"Read processor_name from metadata.json: {processor_name}")
            except Exception as e:
                logger.debug(f"Failed to read metadata.json: {e}")

                                                  
        if not processor_name:
            processor_name = main_path.stem

        forms_dir = parent_dir / processor_name / "Forms"

        form_paths = {}

        if not forms_dir.exists():
            logger.debug(f"No Forms directory found: {forms_dir}")
            return form_paths

                                          
        for form_dir in forms_dir.iterdir():
            if form_dir.is_dir():
                                                              
                form_xml = form_dir / "Ext" / "Form.xml"
                if form_xml.exists():
                    form_paths[form_dir.name] = str(form_xml)
                    logger.debug(f"Found Form.xml: {form_dir.name} → {form_xml}")

        return form_paths

    def _get_form_xml(self, tree: ET.ElementTree, form_name: str = "Форма") -> Optional[ET.Element]:
                   
                                                              
        if tree == self.original_tree:
            form_trees = self.original_form_trees
            tree_type = "original"
        elif tree == self.modified_tree:
            form_trees = self.modified_form_trees
            tree_type = "modified"
        else:
            logger.warning("Unknown tree passed to _get_form_xml")
            return None

                                         
        form_tree = form_trees.get(form_name)
        if form_tree is None:
                                                                          
            logger.debug(f"Form '{form_name}' not found in parsed Form.xml files, trying main XML")
            try:
                form = tree.xpath("//Form", namespaces=self.NAMESPACES)
                if form:
                    logger.debug(f"Found form embedded in main XML ({tree_type})")
                    return form[0]
            except:
                pass
            logger.debug(f"Form '{form_name}' not found in {tree_type} XML")
            return None

                                                              
        return form_tree.getroot()

    def _get_form_elements(self, form_root: etree._Element) -> Dict[str, etree._Element]:
                                                  
        elements = {}
                                                                                     
        for elem in form_root.xpath(".//*[local-name()='InputField' or local-name()='Button' or local-name()='Table' or local-name()='UsualGroup' or local-name()='Pages' or local-name()='LabelField' or local-name()='CheckBoxField' or local-name()='RadioButtonField']"):
                                                       
            elem_name = elem.get("name")
            if elem_name:
                elements[elem_name] = elem
        return elements

    def _get_form_elements_hierarchical(
        self,
        form_root: etree._Element,
        form_index: int = 0
    ) -> List[ElementNode]:
                   
        extractor = HierarchicalExtractor()
        return extractor.extract_form_elements_tree(form_root, form_index)

    def _get_element_events(self, elem: etree._Element) -> Dict[str, str]:
                   
        events = {}
        try:
                                                                          
            events_containers = elem.xpath(".//*[local-name()='Events']")
            if not events_containers:
                return events

            events_container = events_containers[0]

                                            
            for event in events_container:
                                            
                event_name = event.get("name")
                if not event_name:
                    continue

                                                     
                action_elems = event.xpath(".//*[local-name()='Action']")
                if action_elems and action_elems[0].text:
                    handler_name = action_elems[0].text.strip()
                    events[event_name] = handler_name
                    logger.debug(f"Found event: {event_name} → {handler_name}")

        except Exception as e:
            logger.debug(f"Failed to extract events from element: {e}")

        return events

    def _get_element_properties(self, elem: etree._Element) -> Dict[str, Any]:
                   
        props = {}
        try:
                                                 
            numeric_props = {
                'Width': 'width',
                'Height': 'height',
                'FormWidth': 'form_width',
                'FormHeight': 'form_height'
            }
            for xml_name, yaml_name in numeric_props.items():
                prop_elems = elem.xpath(f".//*[local-name()='{xml_name}']")
                if prop_elems and prop_elems[0].text:
                    try:
                        props[yaml_name] = int(prop_elems[0].text)
                    except ValueError:
                        logger.debug(f"Invalid numeric value for {xml_name}: {prop_elems[0].text}")

                                
            boolean_props = {
                'MultiLine': 'multiline',
                'HorizontalStretch': 'horizontal_stretch',
                'VerticalStretch': 'vertical_stretch',
                'Hyperlink': 'hyperlink',
                'ShowTitle': 'show_title',
                'Zoomable': 'zoomable',
                'Edit': 'edit',
                'Protection': 'protection',
                'VerticalScrollBar': 'vertical_scrollbar',
                'HorizontalScrollBar': 'horizontal_scrollbar',
                'ShowGrid': 'show_grid',
                'ShowHeaders': 'show_headers'
            }
            for xml_name, yaml_name in boolean_props.items():
                prop_elems = elem.xpath(f".//*[local-name()='{xml_name}']")
                if prop_elems and prop_elems[0].text:
                    props[yaml_name] = prop_elems[0].text.strip().lower() == 'true'

                                              
            enum_props = {
                'TitleLocation': 'title_location',
                'Behavior': 'behavior',
                'GroupDirection': 'group_direction',
                'PictureSize': 'picture_size',
                'PagesRepresentation': 'pages_representation',
                'RadioButtonType': 'radio_button_type',
                'ButtonType': 'button_type',
                'Representation': 'representation',
                'WindowOpeningMode': 'window_opening_mode',
                'CommandBarLocation': 'command_bar_location'
            }
            for xml_name, yaml_name in enum_props.items():
                prop_elems = elem.xpath(f".//*[local-name()='{xml_name}']")
                if prop_elems and prop_elems[0].text:
                    props[yaml_name] = prop_elems[0].text.strip()

                                                      
            input_hint = self._get_multilang_text(elem, "InputHint")
            for lang, text in input_hint.items():
                props[f'input_hint_{lang}'] = text

                                           
            choice_list_containers = elem.xpath(".//*[local-name()='ChoiceList']")
            if choice_list_containers:
                items = []
                                                             
                for item_elem in choice_list_containers[0].xpath(".//*[local-name()='Item']"):
                    if item_elem.text:
                        items.append(item_elem.text.strip())
                if items:
                    props['choice_list'] = items

        except Exception as e:
            logger.debug(f"Failed to extract properties from element: {e}")

        return props

    def _get_commands(self, tree: etree._ElementTree) -> Dict[str, etree._Element]:
                   
        commands = {}
        try:
            for cmd in tree.xpath("//form:Command", namespaces=self.NAMESPACES):
                name_elem = cmd.find("form:Name", namespaces=self.NAMESPACES)
                if name_elem is not None and name_elem.text:
                    commands[name_elem.text] = cmd
        except:
            pass
        return commands

    def _get_commands_from_form(self, form_root: etree._Element) -> Dict[str, etree._Element]:
                   
        commands = {}
        try:
                                                                  
                                                                            
            for cmd in form_root.xpath(".//form:Command", namespaces=self.NAMESPACES):
                name = cmd.get("name")                        
                if name:
                    commands[name] = cmd
        except Exception as e:
            logger.debug(f"Failed to extract commands from form: {e}")
        return commands

    def _get_tabular_sections(self, tree: etree._ElementTree) -> Dict[str, etree._Element]:
                                                
        sections = {}
        for section in tree.xpath("//ns:ChildObjects/ns:TabularSection", namespaces=self.NAMESPACES):
            name_elem = section.find(".//ns:Properties/ns:Name", namespaces=self.NAMESPACES)
            if name_elem is not None and name_elem.text:
                sections[name_elem.text] = section
        return sections

    def _get_tabular_columns(self, section: etree._Element) -> Dict[str, etree._Element]:
                                                     
        columns = {}
        for col in section.xpath(".//ns:ChildObjects/ns:Attribute", namespaces=self.NAMESPACES):
            name_elem = col.find(".//ns:Properties/ns:Name", namespaces=self.NAMESPACES)
            if name_elem is not None and name_elem.text:
                columns[name_elem.text] = col
        return columns

    def _get_value_tables(self, form_root: etree._Element) -> Dict[str, etree._Element]:
                   
        value_tables = {}

                                                                                  
        for attr in form_root.xpath(".//*[local-name()='Attribute']"):
            attr_name = attr.get("name")
                                             
            type_elem = attr.find(".//v8:Type", namespaces=self.NAMESPACES)

            if attr_name and type_elem is not None:
                                             
                type_text = type_elem.text or ""
                if "ValueTable" in type_text:
                    value_tables[attr_name] = attr

        return value_tables

    def _get_value_table_columns(self, value_table_elem: etree._Element) -> Dict[str, etree._Element]:
                   
        columns = {}

                                                                          
        for col in value_table_elem.xpath(".//v8:Column", namespaces=self.NAMESPACES):
            name_elem = col.find("v8:Name", namespaces=self.NAMESPACES)
            if name_elem is not None and name_elem.text:
                columns[name_elem.text] = col

        return columns

    def _get_form_attributes(self, form_root: etree._Element) -> Dict[str, etree._Element]:
                   
        form_attributes = {}

                                                                                               
                                                                                  
                                              
        for attr in form_root.xpath(".//*[local-name()='Attribute']"):
            attr_name = attr.get("name")                        

            if attr_name is None:
                continue

                                                        
            if attr_name == "Объект":
                continue

                                                             
                                                   
            type_elem = attr.find(".//v8:Type", namespaces=self.NAMESPACES)
            if type_elem is not None:
                type_text = type_elem.text or ""
                if "ValueTable" in type_text:
                    continue                    

                                                                                
            form_attributes[attr_name] = attr

        return form_attributes

    def _get_templates(self, tree: etree._ElementTree) -> Dict[str, etree._Element]:
                   
        templates = {}

                                               
        for tmpl in tree.xpath("//ns:Template", namespaces=self.NAMESPACES):
                                      
            name_elem = tmpl.find(".//ns:Properties/ns:Name", namespaces=self.NAMESPACES)
            if name_elem is not None and name_elem.text:
                templates[name_elem.text] = tmpl
            else:
                                                                       
                name_elem = tmpl.find("ns:Name", namespaces=self.NAMESPACES)
                if name_elem is not None and name_elem.text:
                    templates[name_elem.text] = tmpl

        return templates

    def _get_form_parameters(self, form_root: etree._Element) -> Dict[str, etree._Element]:
                   
        parameters = {}

                                                   
        for param in form_root.xpath(".//form:Parameters/form:Parameter", namespaces=self.NAMESPACES):
            name = param.get("name")
            if name:
                parameters[name] = param

                                                        
        if not parameters:
            for param in form_root.xpath(".//*[local-name()='Parameter']"):
                name = param.get("name")
                if name:
                    parameters[name] = param

        return parameters

    def _get_attribute_type(self, attr_elem: etree._Element) -> str:
                                                            
        type_elem = attr_elem.find(".//v8:Type", namespaces=self.NAMESPACES)
        if type_elem is not None and type_elem.text:
                                                                                           
            return type_elem.text.split(':')[-1]
        return "unknown"

    def _get_multilang_text(self, elem: etree._Element, property_name: str) -> Dict[str, str]:
                   
        result = {}
        prop_path = f".//ns:{property_name}" if property_name in ["Synonym", "Tooltip"] else f".//{property_name}"

        prop_elem = elem.find(prop_path, namespaces=self.NAMESPACES)
        if prop_elem is None:
            return result

                                       
        for item in prop_elem.xpath(".//v8:item", namespaces=self.NAMESPACES):
            lang_elem = item.find("v8:lang", namespaces=self.NAMESPACES)
            content_elem = item.find("v8:content", namespaces=self.NAMESPACES)

            if lang_elem is not None and content_elem is not None:
                result[lang_elem.text] = content_elem.text or ""

        return result

    def _get_element_text(self, elem: etree._Element, xpath: str) -> Optional[str]:
                                                   
        found = elem.find(xpath, namespaces=self.NAMESPACES)
        return found.text if found is not None else None

    def _get_element_xpath(self, elem: etree._Element) -> str:
                                           
        tree = elem.getroottree()
        return tree.getpath(elem)

    def get_changes_by_type(self, element_type: ElementType) -> List[XMLChange]:
                                                       
        return [c for c in self.changes if c.element_type == element_type]

    def get_changes_by_change_type(self, change_type: ChangeType) -> List[XMLChange]:
                                                      
        return [c for c in self.changes if c.change_type == change_type]

    def _compare_forms(self):
                   
        logger.debug("Comparing forms...")

                                                   
        original_forms = set(self.original_form_trees.keys())
        modified_forms = set(self.modified_form_trees.keys())

                                                            
        added_forms = modified_forms - original_forms
        for form_name in added_forms:
            logger.debug(f"Detected added form: {form_name}")
            self.changes.append(XMLChange(
                change_type=ChangeType.ADD,
                element_type=ElementType.FORM,
                xpath=f"/Forms/{form_name}",                
                old_value=None,
                new_value=form_name,
                element_name=form_name
            ))

                                                              
        deleted_forms = original_forms - modified_forms
        for form_name in deleted_forms:
            logger.debug(f"Detected deleted form: {form_name}")
            self.changes.append(XMLChange(
                change_type=ChangeType.DELETE,
                element_type=ElementType.FORM,
                xpath=f"/Forms/{form_name}",                
                old_value=form_name,
                new_value=None,
                element_name=form_name
            ))

        logger.debug(f"Forms comparison: {len(added_forms)} added, {len(deleted_forms)} deleted")

    def print_summary(self):
                                                               
        if not self.changes:
            print("No changes detected.")
            return

        print(f"\n{'='*70}")
        print(f"Detected {len(self.changes)} changes:")
        print(f"{'='*70}\n")

                               
        by_type = {}
        for change in self.changes:
            elem_type = change.element_type.value
            if elem_type not in by_type:
                by_type[elem_type] = []
            by_type[elem_type].append(change)

                       
        for elem_type, changes in sorted(by_type.items()):
            print(f"\n{elem_type.upper()} ({len(changes)} changes):")
            print("-" * 70)
            for change in changes:
                print(f"  • {change}")

        print(f"\n{'='*70}\n")
