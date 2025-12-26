   

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from ruamel.yaml import YAML

from .xml_differ import XMLDiffer, ChangeType, ElementType, XMLChange
from .bsl_differ import BSLDiffer, BSLCodeExtractor
from .change_mapper import ChangeMapper, YAMLUpdate, BSLUpdate, StructuralUpdate
from .yaml_patcher import YAMLPatcher
from .diff_visualizer import DiffVisualizer           
from .change_formatter import ChangeFormatter           
from .yaml_comment_utils import update_value_preserving_comments           

logger = logging.getLogger(__name__)


class SyncTool:
           

    def __init__(
        self,
        original_xml: str,
        modified_xml: str,
        config_path: str,
        handlers_path: str,
        auto_apply: bool = False,
        json_output: bool = False,
        llm_mode: bool = False
    ):
                   
        self.original_xml = original_xml
        self.modified_xml = modified_xml
        self.config_path = config_path
        self.handlers_path = handlers_path

                                                          
        if llm_mode:
            auto_apply = True
            json_output = True

        self.auto_apply = auto_apply
        self.json_output = json_output
        self.llm_mode = llm_mode

                               
        self.xml_differ = XMLDiffer(original_xml, modified_xml)
        self.mapper = ChangeMapper(config_path)

                                                               
        self.modified_tree = self.xml_differ.modified_tree

                                                                      
        self.bsl_differ = None

                 
        self.yaml_updates: List[YAMLUpdate] = []
        self.bsl_updates: List[BSLUpdate] = []
        self.structural_updates: List[StructuralUpdate] = []                                  

    def run(self) -> Dict:
                   
        logger.info("Starting sync process...")

                                    
        xml_changes = self.xml_differ.detect_changes()

                                    
        bsl_changes = self._detect_bsl_changes()

                                        
        self.yaml_updates = self.mapper.map_xml_changes(xml_changes)
        self.bsl_updates = self.mapper.map_bsl_changes(bsl_changes)

                                                       
        self.structural_updates = self._detect_structural_changes(xml_changes)

                                                                                   
        if not self.auto_apply:
            if not self._resolve_conflicts():
                logger.info("Sync cancelled by user")
                return {"status": "cancelled", "reason": "user_cancelled"}

                               
        backup_dir = self._create_backup()

                               
        try:
            self._apply_yaml_updates()
            self._apply_bsl_updates()
            self._apply_structural_updates()           

            result = {
                "status": "success",
                "backup_dir": backup_dir,
                "changes_applied": {
                    "yaml_updates": len(self.yaml_updates),
                    "bsl_updates": len(self.bsl_updates),
                    "structural_updates": len(self.structural_updates)           
                }
            }

            if self.llm_mode:
                result["details"] = self._get_llm_friendly_summary()

            logger.info("Sync completed successfully")
            return result

        except Exception as e:
            logger.error(f"Sync failed: {e}")
                                 
            self._restore_from_backup(backup_dir)
            return {
                "status": "error",
                "error": str(e),
                "backup_restored": True
            }

    def _detect_bsl_changes(self) -> List:
                                                                      
                                       
        original_bsl = self._extract_bsl_from_snapshot()

                                                                                
        modified_bsl = self._extract_bsl_from_modified()

        if not original_bsl or not modified_bsl:
            logger.warning("Could not extract BSL code for comparison")
            return []

                 
        self.bsl_differ = BSLDiffer(original_bsl, modified_bsl)
        return self.bsl_differ.detect_changes()

    def _extract_bsl_from_snapshot(self) -> str:
                   
        snapshot_dir = Path(self.original_xml).parent

                                                       
        handlers_snapshot = snapshot_dir / "original_handlers.bsl"
        if handlers_snapshot.exists():
            return BSLCodeExtractor.extract_from_bsl_file(str(handlers_snapshot))

                                    
        return BSLCodeExtractor.extract_from_xml(self.original_xml)

    def _extract_bsl_from_modified(self) -> str:
                   
        modified_xml_path = Path(self.modified_xml)
        modified_dir = modified_xml_path.parent

                                          
        processor_name = modified_xml_path.stem

                                                               
        processor_dir = modified_dir / processor_name

        collected_bsl = []

                                         
        object_module_path = processor_dir / "Ext" / "ObjectModule.bsl"
        if object_module_path.exists():
            object_module_bsl = BSLCodeExtractor.extract_from_bsl_file(str(object_module_path))
            if object_module_bsl:
                collected_bsl.append(object_module_bsl)
                logger.info(f"Read ObjectModule.bsl ({len(object_module_bsl)} chars)")

                                                    
        forms_dir = processor_dir / "Forms"
        if forms_dir.exists():
            for form_dir in forms_dir.iterdir():
                if form_dir.is_dir():
                    form_module_path = form_dir / "Ext" / "Form" / "Module.bsl"
                    if form_module_path.exists():
                        form_bsl = BSLCodeExtractor.extract_from_bsl_file(str(form_module_path))
                        if form_bsl:
                            collected_bsl.append(form_bsl)
                            logger.info(f"Read {form_dir.name}/Module.bsl ({len(form_bsl)} chars)")

                                                     
        if collected_bsl:
            combined = "\n\n".join(collected_bsl)
            logger.info(f"Total modified BSL: {len(combined)} chars from {len(collected_bsl)} modules")
            return combined

                                                           
        logger.warning(f"No .bsl files found in export directory: {processor_dir}")
        logger.warning("Expected structure: ProcessorName/Ext/ObjectModule.bsl or ProcessorName/Forms/*/Ext/Form/Module.bsl")
        return ""

    def _detect_structural_changes(self, xml_changes: List) -> List[StructuralUpdate]:
                   
        structural_updates = []

        for change in xml_changes:
            if change.change_type == ChangeType.ADD:
                                                                
                element_data = self._extract_element_data(change)
                element_data['_xpath'] = change.xpath                                         

                structural_updates.append(StructuralUpdate(
                    operation="add",
                    element_type=self._map_element_type(change.element_type),
                    element_data=element_data,
                    parent_path=change.parent_path,                               
                    insertion_index=change.insertion_index,
                    depth=change.depth
                ))

            elif change.change_type == ChangeType.DELETE:
                                 
                element_name = change.old_value or "unknown"
                structural_updates.append(StructuralUpdate(
                    operation="delete",
                    element_type=self._map_element_type(change.element_type),
                    element_data={
                        "name": element_name,
                        "_xpath": change.xpath
                    },
                    references=[],                                                    
                    parent_path=change.parent_path,                               
                    insertion_index=None,                         
                    depth=change.depth
                ))

        return structural_updates

    def _map_element_type(self, xml_element_type: ElementType) -> str:
                                                                         
        mapping = {
            ElementType.ATTRIBUTE: "attribute",
            ElementType.FORM_ELEMENT: "form_element",
            ElementType.COMMAND: "command",
            ElementType.TABULAR_SECTION: "tabular_section",
            ElementType.TABULAR_SECTION_COLUMN: "tabular_column",
            ElementType.VALUE_TABLE: "value_table",           
            ElementType.VALUE_TABLE_COLUMN: "value_table_column",
            ElementType.FORM_ATTRIBUTE: "form_attribute",
            ElementType.FORM: "form"                                  
        }
        return mapping.get(xml_element_type, "unknown")

    def _extract_element_data(self, xml_change: XMLChange) -> Dict:
                   
        try:
            from lxml import etree as ET
        except ImportError:
            logger.warning("lxml not available, using minimal extraction")
            return {"name": xml_change.new_value or "NewElement"}

                                                                         
        element_name = xml_change.new_value or "NewElement"

        try:
                                                                    
            elem = None

            if xml_change.element_type == ElementType.ATTRIBUTE:
                                                     
                attrs = self.xml_differ._get_processor_attributes(self.modified_tree)
                elem = attrs.get(element_name)
                if elem is not None:
                    return self._parse_attribute_data(elem)

            elif xml_change.element_type == ElementType.FORM_ELEMENT:
                                   
                form_root = self.xml_differ._get_form_xml(self.modified_tree)
                if form_root is not None:
                    elements = self.xml_differ._get_form_elements(form_root)
                    elem = elements.get(element_name)
                    if elem is not None:
                        return self._parse_form_element_data(elem)

            elif xml_change.element_type == ElementType.COMMAND:
                              
                commands = self.xml_differ._get_commands(self.modified_tree)
                elem = commands.get(element_name)
                if elem is not None:
                    return self._parse_command_data(elem)

            elif xml_change.element_type == ElementType.TABULAR_SECTION:
                                      
                sections = self.xml_differ._get_tabular_sections(self.modified_tree)
                elem = sections.get(element_name)
                if elem is not None:
                    return self._parse_tabular_section_data(elem)

            elif xml_change.element_type == ElementType.VALUE_TABLE:
                                            
                form_root = self.xml_differ._get_form_xml(self.modified_tree)
                if form_root is not None:
                    value_tables = self.xml_differ._get_value_tables(form_root)
                    elem = value_tables.get(element_name)
                    if elem is not None:
                        return self._parse_value_table_data(elem)

            elif xml_change.element_type == ElementType.FORM_ATTRIBUTE:
                                               
                form_root = self.xml_differ._get_form_xml(self.modified_tree)
                if form_root is not None:
                    form_attrs = self.xml_differ._get_form_attributes(form_root)
                    elem = form_attrs.get(element_name)
                    if elem is not None:
                        return self._parse_form_attribute_data(elem)

            elif xml_change.element_type == ElementType.FORM:
                                         
                return self._parse_form_data(element_name)

                                                       
            logger.warning(f"Element '{element_name}' not found for type {xml_change.element_type}")
            return {"name": element_name}

        except Exception as e:
            logger.error(f"Failed to extract element data: {e}")
            return {"name": element_name}

    def _parse_attribute_data(self, elem) -> Dict:
                                                              
        from lxml import etree as ET

        NAMESPACES = self.xml_differ.NAMESPACES
        data = {}

                         
        name_elem = elem.find(".//ns:Properties/ns:Name", namespaces=NAMESPACES)
        data['name'] = name_elem.text if name_elem is not None else "UnknownAttr"

                                                           
        type_str = self.xml_differ._get_attribute_type(elem)
        if type_str and type_str != "unknown":
                                                   
            if type_str in ["decimal", "double", "float"]:
                data['type'] = "number"
            elif type_str == "string":
                data['type'] = "string"
            elif type_str == "boolean":
                data['type'] = "boolean"
            elif type_str in ["date", "dateTime"]:
                data['type'] = "date"
            else:
                data['type'] = type_str

                                                         
            if data.get('type') == "number":
                digits_elem = elem.find(".//ns:Properties/ns:Type/v8:NumberQualifiers/v8:Digits", namespaces=NAMESPACES)
                if digits_elem is not None and digits_elem.text:
                    data['digits'] = int(digits_elem.text)

                fraction_elem = elem.find(".//ns:Properties/ns:Type/v8:NumberQualifiers/v8:FractionDigits", namespaces=NAMESPACES)
                if fraction_elem is not None and fraction_elem.text:
                    data['fraction_digits'] = int(fraction_elem.text)

                                                       
        synonym_values = self.xml_differ._get_multilang_text(elem, "Synonym")
        for lang, text in synonym_values.items():
            data[f'synonym_{lang}'] = text

        return data

    def _parse_form_element_data(self, elem) -> Dict:
                   
        from lxml import etree as ET

        NAMESPACES = self.xml_differ.NAMESPACES
        data = {}

                                                             
                                                                                    
        data['name'] = elem.get("name", "UnknownElement")

                                                    
                                                                     
        tag = elem.tag
        if isinstance(tag, str):
                                                                       
            element_type = tag.split('}')[-1] if '}' in tag else tag
            data['type'] = element_type

                                                                      
        datapath_elems = elem.xpath(".//*[local-name()='DataPath']")
        if datapath_elems and datapath_elems[0].text:
                                                                                     
            datapath_text = datapath_elems[0].text
            parts = datapath_text.split(".")
            if len(parts) > 1:
                data['attribute'] = parts[-1]
            else:
                                                      
                data['attribute'] = datapath_text

                                                     
        title_values = self.xml_differ._get_multilang_text(elem, "Title")
        for lang, text in title_values.items():
            data[f'title_{lang}'] = text

                                     
        readonly_elems = elem.xpath(".//*[local-name()='ReadOnly']")
        if readonly_elems and readonly_elems[0].text:
            readonly_text = readonly_elems[0].text.strip().lower()
            if readonly_text == "true":
                data['read_only'] = True

                                                                    
                                                                          
        child_containers = elem.xpath(".//*[local-name()='ChildItems']")
        if child_containers:
            child_items_container = child_containers[0]
            children = []
                                                                           
            for child_elem in child_items_container:
                                
                child_data = self._parse_form_element_data(child_elem)
                if child_data:
                    children.append(child_data)

            if children:
                data['child_items'] = children

                                                              
        element_events = self.xml_differ._get_element_events(elem)
        if element_events:
            data['events'] = element_events

                                                                  
        element_properties = self.xml_differ._get_element_properties(elem)
        if element_properties:
                                             
            data.update(element_properties)

        return data

    def _parse_command_data(self, elem) -> Dict:
                                                  
        NAMESPACES = self.xml_differ.NAMESPACES
        data = {}

                         
        name_elem = elem.find("form:Name", namespaces=NAMESPACES)
        data['name'] = name_elem.text if name_elem is not None else "UnknownCommand"

                
        action_elem = elem.find("form:Action", namespaces=NAMESPACES)
        if action_elem is not None and action_elem.text:
            data['action'] = action_elem.text

                                                     
        title_values = self.xml_differ._get_multilang_text(elem, "Title")
        for lang, text in title_values.items():
            data[f'title_{lang}'] = text

        return data

    def _parse_tabular_section_data(self, elem) -> Dict:
                                                          
        NAMESPACES = self.xml_differ.NAMESPACES
        data = {}

                         
        name_elem = elem.find(".//ns:Properties/ns:Name", namespaces=NAMESPACES)
        data['name'] = name_elem.text if name_elem is not None else "UnknownSection"

                                                       
        synonym_values = self.xml_differ._get_multilang_text(elem, "Synonym")
        for lang, text in synonym_values.items():
            data[f'synonym_{lang}'] = text

                                                                             
        columns = []
        for col in elem.findall(".//ns:ChildObjects/ns:Attribute", namespaces=NAMESPACES):
            col_name = col.find(".//ns:Properties/ns:Name", namespaces=NAMESPACES)
            if col_name is not None:
                col_data = {"name": col_name.text}

                             
                col_type_elem = col.find(".//ns:Properties/ns:Type/v8:Type", namespaces=NAMESPACES)
                if col_type_elem is not None and col_type_elem.text:
                    type_str = col_type_elem.text.split(":")[-1]                            
                                       
                    if type_str in ["decimal", "double", "float"]:
                        col_data['type'] = "number"
                    elif type_str == "string":
                        col_data['type'] = "string"
                    elif type_str == "boolean":
                        col_data['type'] = "boolean"
                    elif type_str in ["date", "dateTime"]:
                        col_data['type'] = "date"

                                                                 
                    if col_data.get('type') == "number":
                        digits_elem = col.find(".//ns:Properties/ns:Type/v8:NumberQualifiers/v8:Digits", namespaces=NAMESPACES)
                        if digits_elem is not None and digits_elem.text:
                            col_data['digits'] = int(digits_elem.text)

                        fraction_elem = col.find(".//ns:Properties/ns:Type/v8:NumberQualifiers/v8:FractionDigits", namespaces=NAMESPACES)
                        if fraction_elem is not None and fraction_elem.text:
                            col_data['fraction_digits'] = int(fraction_elem.text)

                                
                col_synonym = self.xml_differ._get_multilang_text(col, "Synonym")
                for lang, text in col_synonym.items():
                    col_data[f'synonym_{lang}'] = text

                columns.append(col_data)

        if columns:
            data['columns'] = columns

        return data

    def _parse_value_table_data(self, elem) -> Dict:
                   
        NAMESPACES = self.xml_differ.NAMESPACES
        data = {}

                         
        name_elem = elem.find("form:Name", namespaces=NAMESPACES)
        data['name'] = name_elem.text if name_elem is not None else "UnknownValueTable"

                                                                        
        columns = []
        for col in elem.findall(".//v8:Column", namespaces=NAMESPACES):
            col_name = col.find("v8:Name", namespaces=NAMESPACES)
            if col_name is not None:
                col_data = {"name": col_name.text}

                             
                col_type = col.find("v8:ValueType/v8:Type", namespaces=NAMESPACES)
                if col_type is not None and col_type.text:
                                                                               
                    type_str = col_type.text.split(":")[-1]
                    col_data['type'] = type_str

                columns.append(col_data)

        if columns:
            data['columns'] = columns

        return data

    def _parse_form_attribute_data(self, elem) -> Dict:
                   
        NAMESPACES = self.xml_differ.NAMESPACES
        data = {}

                                                             
                                                                                    
        data['name'] = elem.get("name", "UnknownFormAttr")

                                                   
                                                                 
        type_elems = elem.xpath(".//v8:Type", namespaces=NAMESPACES)
        if type_elems and type_elems[0].text:
                                                                                  
            type_text = type_elems[0].text
                                      
            if "SpreadsheetDocument" in type_text:
                data['type'] = "SpreadsheetDocument"
            elif "BinaryData" in type_text:
                data['type'] = "BinaryData"
            elif "Picture" in type_text:
                data['type'] = "Picture"
            elif "ValueStorage" in type_text:
                data['type'] = "ValueStorage"
            elif "FormDataTree" in type_text:
                data['type'] = "FormDataTree"
            elif "FormDataCollection" in type_text:
                data['type'] = "FormDataCollection"
            elif "decimal" in type_text:
                data['type'] = "number"
            elif "string" in type_text:
                data['type'] = "string"
            elif "boolean" in type_text:
                data['type'] = "boolean"
            elif "date" in type_text or "dateTime" in type_text:
                data['type'] = "date"
            else:
                data['type'] = "unknown"

        return data

    def _parse_form_data(self, form_name: str) -> Dict:
                   
        data = {'name': form_name}

        try:
                                                             
            form_root = self.xml_differ._get_form_xml(self.modified_tree, form_name=form_name)

            if form_root is None:
                logger.warning(f"Form.xml not found for form '{form_name}'")
                return data

                                                                 
            elements_tree = self.xml_differ._get_form_elements_hierarchical(form_root)
            if elements_tree:
                                                              
                data['elements'] = self._convert_elements_tree_to_yaml(elements_tree)

                              
            commands_dict = self.xml_differ._get_commands_from_form(form_root)
            if commands_dict:
                commands = []
                for cmd_name, cmd_elem in commands_dict.items():
                    cmd_data = self._parse_command_data(cmd_elem)
                    commands.append(cmd_data)
                data['commands'] = commands

                                                                 
            form_attrs_dict = self.xml_differ._get_form_attributes(form_root)
            if form_attrs_dict:
                form_attributes = []
                for attr_name, attr_elem in form_attrs_dict.items():
                    attr_data = self._parse_form_attribute_data(attr_elem)
                    form_attributes.append(attr_data)
                data['form_attributes'] = form_attributes

                                  
            value_tables_dict = self.xml_differ._get_value_tables(form_root)
            if value_tables_dict:
                value_tables = []
                for vt_name, vt_elem in value_tables_dict.items():
                    vt_data = self._parse_value_table_data(vt_elem)
                    value_tables.append(vt_data)
                data['value_table_attributes'] = value_tables

                                                                  
                                                                                
                                           
            data['default'] = (form_name == "Форма")

            logger.debug(f"Parsed form data for '{form_name}': {len(data.get('elements', []))} elements, "
                        f"{len(data.get('commands', []))} commands")

        except Exception as e:
            logger.error(f"Failed to parse form data for '{form_name}': {e}")

        return data

    def _convert_elements_tree_to_yaml(self, elements_tree: List) -> List[Dict]:
                   
        result = []
        for element_node in elements_tree:
                                                 
            elem_data = self._parse_form_element_data(element_node.element)

                                             
            if element_node.children:
                elem_data['child_items'] = self._convert_elements_tree_to_yaml(element_node.children)

            result.append(elem_data)

        return result

    def _extract_form_index_from_xpath(self, xpath: str) -> int:
                   
        import re

                                           
        match = re.search(r'/Form\[(\d+)\]', xpath)
        if match:
                                                                      
            return int(match.group(1)) - 1

                               
        return 0

    def _resolve_conflicts(self) -> bool:
                   
        if not self.yaml_updates and not self.bsl_updates and not self.structural_updates:
            print("\nNo changes detected.")
            return False

                                         
        diff_viz = DiffVisualizer(context_lines=3)
        formatter = ChangeFormatter(use_unicode=True)

        print("\n" + "=" * 70)
        print("CONFLICT RESOLUTION")
        print("=" * 70)
        print("\nOptions for each change:")
        print("  [y] Apply this change")
        print("  [n] Skip this change")
        print("  [a] Apply all remaining changes")
        print("  [s] Skip all remaining changes")
        print("  [d] Show detailed information with diff preview")
        print("  [p] Show side-by-side preview")
        print("  [q] Quit without applying any changes")
        print("=" * 70)

                                       
        all_updates = []

                          
        for update in self.yaml_updates:
            all_updates.append(("YAML", update))

                         
        for update in self.bsl_updates:
            all_updates.append(("BSL", update))

                                
        for update in self.structural_updates:
            all_updates.append(("STRUCTURAL", update))

                                
        approved_yaml = []
        approved_bsl = []
        approved_structural = []

        auto_approve_all = False

        for idx, (change_type, update) in enumerate(all_updates, start=1):
                                                  
            if auto_approve_all:
                if change_type == "YAML":
                    approved_yaml.append(update)
                elif change_type == "BSL":
                    approved_bsl.append(update)
                elif change_type == "STRUCTURAL":
                    approved_structural.append(update)
                continue

                                                          
            print(f"\n[{idx}/{len(all_updates)}] {change_type} Change:")
            print("-" * 70)

                                                                                  
            if change_type == "STRUCTURAL":
                formatted = formatter.format_change(update, mode='simple')
                print(f"  {formatted}")
            else:
                print(f"  {update}")

                                                    
            if change_type == "STRUCTURAL" and hasattr(update, 'references') and update.references:
                print(f"\n  ⚠️  WARNING: Found {len(update.references)} references:")
                for ref in update.references[:3]:                           
                    print(f"      - {ref}")
                if len(update.references) > 3:
                    print(f"      ... and {len(update.references) - 3} more")
                print("\n  ⚠️  Applying this change may break existing code!")

                               
            while True:
                choice = input("\nDecision [y/n/a/s/d/q]: ").strip().lower()

                if choice == 'y':
                    if change_type == "YAML":
                        approved_yaml.append(update)
                    elif change_type == "BSL":
                        approved_bsl.append(update)
                    elif change_type == "STRUCTURAL":
                        approved_structural.append(update)
                    print("✓ Change will be applied")
                    break

                elif choice == 'n':
                    print("✗ Change skipped")
                    break

                elif choice == 'a':
                                                  
                    if change_type == "YAML":
                        approved_yaml.append(update)
                    elif change_type == "BSL":
                        approved_bsl.append(update)
                    elif change_type == "STRUCTURAL":
                        approved_structural.append(update)
                    auto_approve_all = True
                    print("✓ This and all remaining changes will be applied")
                    break

                elif choice == 's':
                                                 
                    print("✗ All remaining changes skipped")
                                
                    self.yaml_updates = approved_yaml
                    self.bsl_updates = approved_bsl
                    self.structural_updates = approved_structural

                    total_approved = len(approved_yaml) + len(approved_bsl) + len(approved_structural)
                    print(f"\n{total_approved} change(s) approved, {len(all_updates) - idx} skipped")
                    return total_approved > 0

                elif choice == 'd':
                                                                  
                    print("\n" + "=" * 70)
                    print("DETAILED VIEW")
                    print("=" * 70)

                    if change_type == "STRUCTURAL":
                                                                   
                        detailed = formatter.format_change(update, mode='detailed', references=update.references)
                        print(detailed)

                                                  
                        if update.operation == "add" and update.element_data:
                            viz = diff_viz.visualize_yaml_change(
                                element_type=update.element_type,
                                element_name=update.element_data.get('name', 'unknown'),
                                operation=update.operation,
                                element_data=update.element_data,
                                config=self.config,
                                yaml_path=update.parent_path
                            )
                            print(viz)

                    elif change_type == "BSL":
                                            
                        viz = diff_viz.visualize_bsl_change(
                            procedure_name=update.procedure_name,
                            old_code=update.old_code,
                            new_code=update.new_code,
                            operation=update.update_type
                        )
                        print(viz)

                    elif change_type == "YAML":
                                                  
                        print(f"  Path: {update.path}")
                        print(f"  Section: {update.section}")
                        print(f"  Element: {update.element_name}")
                        print(f"  Old value: {update.old_value}")
                        print(f"  New value: {update.new_value}")

                    print("=" * 70)
                    continue             

                elif choice == 'p':
                                                        
                    print("\n" + "=" * 70)
                    print("SIDE-BY-SIDE PREVIEW")
                    print("=" * 70)

                    if change_type == "BSL" and update.old_code and update.new_code:
                                                          
                        side_by_side = diff_viz.create_side_by_side(
                            left_title="Before",
                            right_title="After",
                            left_content=update.old_code,
                            right_content=update.new_code,
                            width=35
                        )
                        print(side_by_side)
                    elif change_type == "STRUCTURAL":
                                                    
                        viz = diff_viz.visualize_structural_change(
                            element_type=update.element_type,
                            element_name=update.element_data.get('name', 'unknown') if update.element_data else 'unknown',
                            operation=update.operation,
                            parent_path=update.parent_path,
                            insertion_index=update.insertion_index,
                            config=self.config
                        )
                        print(viz)
                    else:
                        print("  Preview not available for this change type")

                    print("=" * 70)
                    continue             

                elif choice == 'q':
                    print("\n✗ Sync cancelled")
                    return False

                else:
                    print("Invalid choice. Please enter y/n/a/s/d/p/q")
                    continue

                                                       
        self.yaml_updates = approved_yaml
        self.bsl_updates = approved_bsl
        self.structural_updates = approved_structural

        total_approved = len(approved_yaml) + len(approved_bsl) + len(approved_structural)

        if total_approved == 0:
            print("\n✗ No changes approved")
            return False

        print(f"\n✓ {total_approved} change(s) approved")
        return True

    def _create_backup(self) -> str:
                   
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(self.config_path).parent / f".sync_backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)

                            
        shutil.copy2(self.config_path, backup_dir / Path(self.config_path).name)

                             
        if os.path.exists(self.handlers_path):
            shutil.copy2(self.handlers_path, backup_dir / Path(self.handlers_path).name)

        logger.info(f"Created backup in {backup_dir}")
        return str(backup_dir)

    def _restore_from_backup(self, backup_dir: str):
                                        
        backup_path = Path(backup_dir)

                      
        yaml_backup = backup_path / Path(self.config_path).name
        if yaml_backup.exists():
            shutil.copy2(yaml_backup, self.config_path)

                     
        bsl_backup = backup_path / Path(self.handlers_path).name
        if bsl_backup.exists():
            shutil.copy2(bsl_backup, self.handlers_path)

        logger.info(f"Restored files from backup {backup_dir}")

    def _apply_yaml_updates(self):
                                                
        if not self.yaml_updates:
            return

        logger.info(f"Applying {len(self.yaml_updates)} YAML updates...")

                                                           
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.default_flow_style = False
                                                         
        yaml.map_indent = 2
        yaml.sequence_indent = 2
        yaml.sequence_dash_offset = 0

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.load(f)

                           
        for update in self.yaml_updates:
            self._apply_single_yaml_update(config, update)

                             
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)

        logger.info("YAML updates applied successfully")

    def _apply_single_yaml_update(self, config: dict, update: YAMLUpdate):
                   
                                                                              
        path_parts = self._parse_update_path(update.path)

                            
        current = config
        for part in path_parts[:-1]:
            if isinstance(part, str):
                current = current[part]
            elif isinstance(part, int):
                current = current[part]

                                     
        final_key = path_parts[-1]

                                                           
                                                                                        
                                                                       
        if self._is_multilang_property_key(final_key) and update.new_value is None:
            if final_key in current and current[final_key] is not None:
                logger.debug(f"Preserving multilingual property {final_key} "
                           f"(missing in modified XML but exists in YAML)")
                return                                             

                                                                              
        if final_key == 'events' and isinstance(update.new_value, dict):
                                                                         
            if 'events' in current:
                                         
                if isinstance(current['events'], dict):
                    current['events'].update(update.new_value)
                else:
                                               
                    current['events'] = update.new_value
            else:
                                              
                update_value_preserving_comments(current, final_key, update.new_value)
            return

                                                                            
        if final_key in ['synonym', 'title', 'tooltip']:
                                                                                    
            if isinstance(update.new_value, str) and ':' in update.new_value:
                                   
                lang_values = {}
                for part in update.new_value.split(', '):
                    if ':' in part:
                        lang, value = part.split(':', 1)
                        lang_values[lang] = value.strip("'\"")

                                                        
                update_value_preserving_comments(current, final_key, lang_values)
            else:
                                                        
                update_value_preserving_comments(current, final_key, update.new_value)
        else:
                                 
                                                                                         
            update_value_preserving_comments(current, final_key, update.new_value)

    def _is_multilang_property_key(self, key: str) -> bool:
                   
        if not isinstance(key, str):
            return False

                                                
        for lang in ['_ru', '_uk', '_en']:
            if key.endswith(lang):
                                                                
                prefix = key[:-len(lang)]
                                                                  
                multilang_prefixes = ['title', 'tooltip', 'input_hint', 'synonym']
                if prefix in multilang_prefixes:
                    return True

        return False

    def _parse_update_path(self, path: str) -> List:
                   
        import re

        parts = []
        pattern = r'(\w+)|\[(\d+)\]'

        for match in re.finditer(pattern, path):
            if match.group(1):              
                parts.append(match.group(1))
            elif match.group(2):         
                parts.append(int(match.group(2)))

        return parts

    def _apply_bsl_updates(self):
                                                 
        if not self.bsl_updates:
            return

        logger.info(f"Applying {len(self.bsl_updates)} BSL updates...")

                                    
        with open(self.handlers_path, 'r', encoding='utf-8-sig') as f:
            current_bsl = f.read()

                           
        for update in self.bsl_updates:
            current_bsl = self._apply_single_bsl_update(current_bsl, update)

                               
        with open(self.handlers_path, 'w', encoding='utf-8-sig') as f:
            f.write(current_bsl)

        logger.info("BSL updates applied successfully")

    def _build_procedure_regex(self, procedure_name: str) -> 're.Pattern':
                   
        import re

                                                                 
        escaped_name = re.escape(procedure_name)

                       
        pattern = re.compile(
            rf'(?:&[А-ЯЁа-яёA-Za-z]+\s*)*'                                         
            rf'(?:Процедура|Функция)\s+'                                    
            rf'{escaped_name}'                                         
            rf'\s*\([^)]*\)'                                            
            rf'(?:\s+Экспорт)?'                                       
            rf'.*?'                                             
            rf'Конец(?:Процедуры|Функции)',               
            re.DOTALL | re.IGNORECASE                                              
        )

        return pattern

    def _apply_single_bsl_update(self, bsl_code: str, update: BSLUpdate) -> str:
                                                
        import re

        if update.update_type == "add":
                                                                                
                                          
            if '#КонецОбласті' in bsl_code:
                                      
                last_region_end = bsl_code.rfind('#КонецОбласті')
                                  
                bsl_code = (bsl_code[:last_region_end] +
                           '\n' + update.new_code + '\n\n' +
                           bsl_code[last_region_end:])
            else:
                             
                bsl_code += '\n\n' + update.new_code

        elif update.update_type == "delete":
                              
                                          
            if update.old_code and update.old_code in bsl_code:
                bsl_code = bsl_code.replace(update.old_code, '')

        elif update.update_type == "modify":
                                                                                
            if update.new_code and update.procedure_name:
                                                                                    
                pattern = self._build_procedure_regex(update.procedure_name)

                                           
                match = pattern.search(bsl_code)
                if match:
                                                             
                    bsl_code = pattern.sub(update.new_code, bsl_code, count=1)
                    logger.debug(f"Modified procedure '{update.procedure_name}' using regex matching")
                else:
                                                       
                    logger.warning(f"Could not find procedure '{update.procedure_name}' to modify")
                                                                                   
                    if update.old_code and update.old_code in bsl_code:
                        bsl_code = bsl_code.replace(update.old_code, update.new_code)
                        logger.debug(f"Modified procedure '{update.procedure_name}' using exact string matching (fallback)")
                    else:
                        logger.error(f"Failed to modify procedure '{update.procedure_name}' - not found in BSL code")

        return bsl_code

    def _apply_structural_updates(self):
                   
        if not self.structural_updates:
            return

        logger.info(f"Applying {len(self.structural_updates)} structural updates...")

                                              
        bsl_code = ""
        if os.path.exists(self.handlers_path):
            with open(self.handlers_path, 'r', encoding='utf-8-sig') as f:
                bsl_code = f.read()

                                
        patcher = YAMLPatcher(self.config_path, bsl_code)

                                      
        for update in self.structural_updates:
            success = self._apply_single_structural_update(patcher, update)

            if not success:
                logger.warning(f"Failed to apply structural update: {update}")

                            
        warnings = patcher.get_warnings()
        if warnings:
            for warning in warnings:
                logger.warning(warning)

                           
        if patcher.save():
            logger.info("Structural updates applied successfully")
        else:
            raise Exception("Failed to save structural updates to YAML")

    def _apply_single_structural_update(self, patcher: YAMLPatcher,
                                       update: StructuralUpdate) -> bool:
                   
        element_name = update.element_data.get('name', 'unknown')
        xpath = update.element_data.get('_xpath', '')

                                                                        
        form_index = self._extract_form_index_from_xpath(xpath) if xpath else 0

                                                     
        clean_data = {k: v for k, v in update.element_data.items() if not k.startswith('_')}

        if update.operation == "add":
                         
            if update.element_type == "attribute":
                return patcher.add_attribute(clean_data)

            elif update.element_type == "form_element":
                                                                  
                if update.parent_path:
                    return patcher.add_form_element_nested(
                        form_index,
                        clean_data,
                        parent_path=update.parent_path,
                        insertion_index=update.insertion_index
                    )
                else:
                    return patcher.add_form_element(form_index, clean_data, position=update.insertion_index)

            elif update.element_type == "command":
                return patcher.add_command(form_index, clean_data)

            elif update.element_type == "tabular_section":
                return patcher.add_tabular_section(clean_data)

            elif update.element_type == "value_table":
                                             
                return patcher.add_value_table(form_index, clean_data)

            elif update.element_type == "form_attribute":
                                                
                return patcher.add_form_attribute(form_index, clean_data)

            elif update.element_type == "form":
                                             
                return patcher.add_form(clean_data)

            else:
                logger.warning(f"Add operation not yet supported for {update.element_type}")
                return False

        elif update.operation == "delete":
                                                      
            if update.element_type == "attribute":
                return patcher.delete_attribute(element_name, force=False)

            elif update.element_type == "form_element":
                                                                  
                if update.parent_path:
                    return patcher.delete_form_element_nested(
                        form_index,
                        element_name,
                        parent_path=update.parent_path,
                        force=False
                    )
                else:
                    return patcher.delete_form_element(form_index, element_name, force=False)

            elif update.element_type == "command":
                return patcher.delete_command(form_index, element_name, force=False)

            elif update.element_type == "tabular_section":
                return patcher.delete_tabular_section(element_name, force=False)

            elif update.element_type == "value_table":
                                             
                return patcher.delete_value_table(form_index, element_name, force=False)

            elif update.element_type == "form_attribute":
                                                
                return patcher.delete_form_attribute(form_index, element_name, force=False)

            elif update.element_type == "form":
                                             
                return patcher.delete_form(element_name, force=False)

            else:
                logger.warning(f"Delete operation not yet supported for {update.element_type}")
                return False

        return False

    def _get_llm_friendly_summary(self) -> Dict:
                   
        return {
            "yaml_changes": [
                {
                    "path": u.path,
                    "section": u.section,
                    "element_name": u.element_name,
                    "old_value": u.old_value,
                    "new_value": u.new_value
                }
                for u in self.yaml_updates
            ],
            "bsl_changes": [
                {
                    "type": u.update_type,
                    "procedure_name": u.procedure_name,
                    "has_code_change": u.old_code != u.new_code if u.old_code and u.new_code else True
                }
                for u in self.bsl_updates
            ],
            "structural_changes": [
                {
                    "operation": u.operation,
                    "element_type": u.element_type,
                    "element_name": u.element_data.get('name', 'unknown'),
                    "has_references": len(u.references) > 0 if u.references else False,
                    "reference_count": len(u.references) if u.references else 0
                }
                for u in self.structural_updates
            ],
            "summary": {
                "total_changes": len(self.yaml_updates) + len(self.bsl_updates) + len(self.structural_updates),
                "yaml_updates": len(self.yaml_updates),
                "bsl_updates": len(self.bsl_updates),
                "structural_updates": len(self.structural_updates),
                "affected_sections": list(set(u.section for u in self.yaml_updates))
            }
        }

    def print_results(self, result: Dict):
                                                                   
        if self.json_output:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("\n" + "=" * 70)
            print("SYNC RESULT")
            print("=" * 70)
            print(f"\nStatus: {result['status']}")

            if result['status'] == 'success':
                print(f"Backup created: {result['backup_dir']}")
                print(f"\nChanges applied:")
                print(f"  • YAML updates: {result['changes_applied']['yaml_updates']}")
                print(f"  • BSL updates: {result['changes_applied']['bsl_updates']}")
                if 'structural_updates' in result['changes_applied']:
                    print(f"  • Structural updates: {result['changes_applied']['structural_updates']}")
            elif result['status'] == 'error':
                print(f"\nError: {result['error']}")
                if result.get('backup_restored'):
                    print("Files restored from backup")

            print("\n" + "=" * 70)


def run_sync(
    original_xml: str,
    modified_xml: str,
    config: str,
    handlers: str,
    auto_apply: bool = False,
    json_output: bool = False,
    llm_mode: bool = False
) -> int:
           
                       
    log_level = logging.INFO if not llm_mode else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s'
    )

    try:
        tool = SyncTool(
            original_xml=original_xml,
            modified_xml=modified_xml,
            config_path=config,
            handlers_path=handlers,
            auto_apply=auto_apply,
            json_output=json_output,
            llm_mode=llm_mode
        )

        result = tool.run()
        tool.print_results(result)

        return 0 if result['status'] == 'success' else 1

    except Exception as e:
        logger.exception("Sync failed with exception")
        if json_output or llm_mode:
            print(json.dumps({"status": "error", "error": str(e)}, indent=2))
        else:
            print(f"\nERROR: {e}")
        return 1
