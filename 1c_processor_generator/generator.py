   

import os
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, BaseLoader, TemplateNotFound
from typing import Optional

from .models import Processor
from .constants import (
    CLASS_ID_EXTERNAL_DATA_PROCESSOR,
    XML_NAMESPACES,
    FORM_XML_NAMESPACES,
    ENCODING_UTF8_BOM,
    EMPTY_BSL_TEMPLATE,
    OBJECT_MODULE_TEMPLATE,
    FORM_MODULE_TEMPLATE,
    get_embedded_template,
    has_embedded_templates,
)
                                                                        
                                                                            
                                                                         
from .pro._gc import get_generation_context, finalize_module
from .validators import ProcessorValidator
from .assertion_helper import get_test_infrastructure_bsl, should_add_test_infrastructure
from .post_validator import PostGenerationValidator
from .id_allocator import IDAllocator
from .element_preparer import ElementPreparer


class _EmbeddedTemplateLoader(BaseLoader):
           

    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self._file_loader = FileSystemLoader(str(template_dir))

    def get_source(self, environment, template):
                                                     
        content = get_embedded_template(template)
        if content is not None:
            return content, template, lambda: True

                                                    
        return self._file_loader.get_source(environment, template)


class ProcessorGenerator:
                                        

    def __init__(self, processor: Processor):
        self.processor = processor

                                                          
                                                                                  
        self._gen_ctx = get_generation_context()

                                                                                 
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(
            loader=_EmbeddedTemplateLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
                                                                             
                                                                
        self.env.filters['x'] = self._xml_escape

    @staticmethod
    def _xml_escape(value):
                   
        if value is None:
            return ''
        s = str(value)
                                                       
        s = s.replace('&', '&amp;')
        s = s.replace('<', '&lt;')
        s = s.replace('>', '&gt;')
        return s

    def _detect_is_value_table(self, table_elem, form) -> bool:
                   
                                           
        explicit_value = table_elem.properties.get("is_value_table")
        if explicit_value is not None:
            return explicit_value

                                                                      
        ts_name = table_elem.tabular_section
        if ts_name and form.value_table_attributes:
            return any(vt.name == ts_name for vt in form.value_table_attributes)

        return False

    def validate(self) -> bool:
                                                
        print("🔍 Валідація BSL коду та структури обробки...")
        validator = ProcessorValidator(self.processor)
        is_valid, errors, warnings = validator.validate()

        if warnings:
            print("⚠️  Попередження:")
            for warning in warnings:
                print(f"   - {warning}")

        if not is_valid:
            print("❌ Помилки валідації:")
            for error in errors:
                print(f"   - {error}")
            return False

        print("✅ Валідація пройдена успішно")
        return True

    def _render_namespaces(self, namespaces: dict) -> str:
                                        
        return " ".join([f'{k}="{v}"' for k, v in namespaces.items()])

    def _generate_object_module_code(self) -> str:
                   
        import re

                                                                   
        if not should_add_test_infrastructure(self.processor) or not self.processor.forms:
            raw_code = OBJECT_MODULE_TEMPLATE
                                                                                      
            result = finalize_module(
                module_code=raw_code,
                seed=self.processor.name,
                current_element_id=self._id_allocator.current_id if hasattr(self, '_id_allocator') else 1,
                module_type="object"
            )
            return result["code"]

                                          
        all_commands = []
        for form in self.processor.forms:
            all_commands.extend(form.commands)

        if not all_commands:
            raw_code = OBJECT_MODULE_TEMPLATE
                                                                                      
            result = finalize_module(
                module_code=raw_code,
                seed=self.processor.name,
                current_element_id=self._id_allocator.current_id if hasattr(self, '_id_allocator') else 1,
                module_type="object"
            )
            return result["code"]

                                                             
        exported_procedures = []

        for cmd in all_commands:
            if not hasattr(cmd, 'bsl_code') or not cmd.bsl_code:
                continue

                                                     
                                                                             
            pattern = r'&НаСервере\s+Процедура\s+(\w+)\(\)(.*?)КонецПроцедуры'
            matches = re.findall(pattern, cmd.bsl_code, re.DOTALL)

            if matches:
                for proc_name, proc_body in matches:
                                                  
                                                                          
                    adapted_body = proc_body.replace('Объект.', '')

                                                                                   
                    adapted_body = re.sub(r'\s*ОтправитьСообщение\([^)]+\);?\s*', '', adapted_body)

                                                                          
                    exported_proc = f"""Процедура {cmd.action}() Экспорт{adapted_body}
КонецПроцедуры"""
                    exported_procedures.append(exported_proc)

                                                             
        procedures_code = "\n\n".join(exported_procedures) if exported_procedures else "// Публичные функции"

        raw_code = f"""#Область ПрограммныйИнтерфейс

// Публичные функции доступные через COM (v2.16.0+)

{procedures_code}

#КонецОбласти

#Область СлужебныеПроцедурыИФункции

// Вспомогательные функции

#КонецОбласти"""

                                                                                  
        result = finalize_module(
            module_code=raw_code,
            seed=self.processor.name,
            current_element_id=self._id_allocator.current_id if hasattr(self, '_id_allocator') else 1,
            module_type="object"
        )
        return result["code"]

    def _generate_form_module_code(self, form) -> str:
                   
        handlers = []

                                                                   
        form_event_sigs = self._gen_ctx["form_event_signatures"]
        element_event_sigs = self._gen_ctx["element_event_signatures"]
        event_handler_tpl = self._gen_ctx["event_handler_template"]
        server_call_tpl = self._gen_ctx["server_call_template"]
        server_proc_tpl = self._gen_ctx["server_procedure_template"]

                                            
        form_events = form.events
        form_events_bsl = form.events_bsl if hasattr(form, "events_bsl") else {}
        form_elements = form.elements
        commands = form.commands

                                         
        for event_name, handler_name in form_events.items():
                                                   
            if handler_name in form_events_bsl:
                                                     
                handlers.append(form_events_bsl[handler_name])
            elif event_name in form_event_sigs:
                sig = form_event_sigs[event_name]

                                                                         
                if "server_call" in sig:
                                                               
                    client_code = server_call_tpl.format(
                        client_handler=handler_name,
                        params=sig["params"],
                        server_handler=sig["server_call"],
                    )
                    handlers.append(client_code)

                                        
                    server_code = server_proc_tpl.format(
                        server_handler=sig["server_call"]
                    )
                    handlers.append(server_code)
                else:
                                                                  
                    code = event_handler_tpl.format(
                        directive=sig["directive"],
                        handler_name=handler_name,
                        params=sig["params"],
                        body="// Вставить содержимое обработчика.",
                    )
                    handlers.append(code)

                                                   
        for elem in form_elements:
            if elem.event_handlers:
                for event_name, handler_name in elem.event_handlers.items():
                                                           
                    if hasattr(elem, "bsl_code") and event_name in elem.bsl_code:
                                                             
                        handlers.append(elem.bsl_code[event_name])
                    elif event_name in element_event_sigs:
                        sig = element_event_sigs[event_name]

                                                                
                        if "server_call_suffix" in sig:
                            server_handler = handler_name + sig["server_call_suffix"]

                                                  
                            client_code = server_call_tpl.format(
                                client_handler=handler_name,
                                params=sig["params"],
                                server_handler=server_handler,
                            )
                            handlers.append(client_code)

                                                
                            server_code = server_proc_tpl.format(
                                server_handler=server_handler
                            )
                            handlers.append(server_code)
                        else:
                                                
                            code = event_handler_tpl.format(
                                directive=sig["directive"],
                                handler_name=handler_name,
                                params=sig["params"],
                                body="// Вставить содержимое обработчика.",
                            )
                            handlers.append(code)

                                    
        command_handlers = []
        for cmd in commands:
                                                                                                
            if hasattr(cmd, "long_operation") and cmd.long_operation:
                continue

                                                   
            if hasattr(cmd, "bsl_code") and cmd.bsl_code:
                command_handlers.append(cmd.bsl_code)
            else:
                                       
                cmd_handler = f"""&НаКлиенте
Процедура {cmd.action}(Команда)
\t// Вставить содержимое обработчика.
КонецПроцедуры"""
                command_handlers.append(cmd_handler)

                                 
        handlers_code = "\n\n".join(handlers) if handlers else "// Обработчики событий формы"
        commands_code = "\n\n".join(command_handlers) if command_handlers else "// Обработчики команд формы"

                                                                          
        helpers_parts = []

                                                                    
        from .template_bsl_generator import generate_template_helpers
        template_helpers = generate_template_helpers(self.processor)
        if template_helpers:
            helpers_parts.append(template_helpers)

                                        
        if hasattr(form, "helper_procedures") and form.helper_procedures:
            helpers_parts.extend(form.helper_procedures.values())

        helpers_code = "\n\n".join(helpers_parts) if helpers_parts else "// Вспомогательные функции"

                                                    
                                                                        
        module_parts = []

                                      
        if hasattr(form, "documentation") and form.documentation:
            module_parts.append(f"""#Область Документация

{form.documentation}

#КонецОбласти""")

                                            
        long_operations_code = ""
        if hasattr(self.processor, "long_operation_handlers") and self.processor.long_operation_handlers:
            handlers_list = list(self.processor.long_operation_handlers.values())
            long_operations_code = "\n\n".join(handlers_list)

                                
        module_parts.append(f"""#Область ОбработчикиСобытийФормы

{handlers_code}

#КонецОбласти

#Область ОбработчикиСобытийЭлементовШапкиФормы

// Обработчики событий элементов формы

#КонецОбласти

#Область ОбработчикиКомандФормы

{commands_code}

#КонецОбласти
""")

                                                            
        if long_operations_code:
            module_parts.append(f"""#Область ДлительныеОперации

{long_operations_code}

#КонецОбласти
""")

                                           
        module_parts.append(f"""#Область СлужебныеПроцедурыИФункции

{helpers_code}

#КонецОбласти""")

                                                                       
        if should_add_test_infrastructure(self.processor):
            test_infrastructure_code = get_test_infrastructure_bsl()
            module_parts.append(f"""#Область ТестоваяИнфраструктура

{test_infrastructure_code}

#КонецОбласти""")

                               
        raw_code = "\n\n".join(module_parts)

                                                                                  
                                                                      
                                                           
        result = finalize_module(
            module_code=raw_code,
            seed=f"{self.processor.name}_{form.name}",
            current_element_id=self._id_allocator.current_id if hasattr(self, '_id_allocator') else 1,
            module_type="form"
        )
        return result["code"]

    def _set_table_context(self, element, tabular_section, is_value_table):
                   
                                                                   
        if element.element_type in ["InputField", "LabelField", "CheckBoxField", "PictureField", "RadioButtonField", "HTMLDocumentField"]:
            if element.attribute and "data_path" not in element.properties:
                                                            
                if is_value_table:
                    element.properties["data_path"] = f"{tabular_section}.{element.attribute}"
                else:
                    element.properties["data_path"] = f"Объект.{tabular_section}.{element.attribute}"

                                                                            
        elif element.element_type == "ColumnGroup":
            for child in element.child_items:
                self._set_table_context(child, tabular_section, is_value_table)

    def _prepare_table_element(self, table_elem, table_id: int, allocator: IDAllocator, form):
                   
                                                                                            
                                                                            
        if table_elem.child_items:
                                                                                           
            child_items = []
                                                   
            is_value_table = self._detect_is_value_table(table_elem, form)

            for child_elem in table_elem.child_items:
                                                                                   
                self._set_table_context(child_elem, table_elem.tabular_section, is_value_table)

                child_data = self._process_form_element(child_elem, allocator, form)
                child_items.append(child_data)

            return {
                "tabular_section": table_elem.tabular_section,
                "is_value_table": is_value_table,
                "is_dynamic_list": table_elem.properties.get("is_dynamic_list", False),
                "events": table_elem.event_handlers,
                "child_items": child_items,                                                         
                "columns": [],                                                  
            }

                                               
        is_value_table = self._detect_is_value_table(table_elem, form)
        is_dynamic_list = table_elem.properties.get("is_dynamic_list", False)

                                                
        dynamic_list_attributes = form.dynamic_list_attributes
        value_table_attributes = form.value_table_attributes

                                                              
        if is_dynamic_list:
                                            
            dl_attr = next(
                (dl for dl in dynamic_list_attributes if dl.name == table_elem.tabular_section), None
            )

            columns = []
            if dl_attr:
                if dl_attr.columns:
                                                                      
                    for col in dl_attr.columns:
                        col_id = allocator.allocate_table_column(f"{dl_attr.name}{col.field}")
                        columns.append({
                            "type": "LabelField",
                            "name": f"{dl_attr.name}{col.field}",
                            "data_path": f"{dl_attr.name}.{col.field}",
                            "title_ru": col.title_ru if col.title_ru else col.field,
                            "title_uk": col.title_uk if col.title_uk else col.field,
                            "width": col.width,
                            "id": col_id
                        })
                elif not dl_attr.manual_query:
                                                                                                           
                    col_id = allocator.allocate_table_column(f"{dl_attr.name}Description")
                    columns.append({
                        "type": "LabelField",
                        "name": f"{dl_attr.name}Description",
                        "data_path": f"{dl_attr.name}.Description",
                        "title_ru": "Наименование",
                        "title_uk": "Найменування",
                        "width": None,
                        "id": col_id
                    })

            return {
                "tabular_section": table_elem.tabular_section,
                "is_value_table": True,                                                  
                "is_dynamic_list": True,
                "events": table_elem.event_handlers,
                "columns": columns,
            }

                                                   
        columns_source = None
        if is_value_table:
            columns_source = next(
                (vt for vt in value_table_attributes if vt.name == table_elem.tabular_section), None
            )
        else:
                                                                      
            columns_source = next(
                (ts for ts in self.processor.tabular_sections if ts.name == table_elem.tabular_section), None
            )

        if not columns_source:
                                                                     
            return {
                "tabular_section": table_elem.tabular_section,
                "is_value_table": is_value_table,
                "events": table_elem.event_handlers,
                "columns": [],
            }

                         
        columns = []
                                                                  
        if not is_value_table:
            col_id = allocator.allocate_table_column("НомерСтроки")
            columns.append({"type": "LineNumber", "name": "НомерСтроки", "id": col_id})

                                  
        for col in columns_source.columns:
            col_type = "CheckBox" if col.type in ["boolean", "xs:boolean"] else "InputField"
            col_id = allocator.allocate_table_column(col.name)
            columns.append({"type": col_type, "name": col.name, "id": col_id, "read_only": col.read_only})

        table_data = {
            "tabular_section": table_elem.tabular_section,
            "is_value_table": is_value_table,
            "events": table_elem.event_handlers,
            "columns": columns,
        }

        return table_data

    def _process_form_element(self, element, allocator: IDAllocator, form):
                   
                                                                        
        elem_id = allocator.allocate(element.element_type, element.name)

                                   
        elem_data = {
            "type": element.element_type,
            "name": element.name,
            "id": elem_id,
            "properties": element.properties,
            "events": element.event_handlers,
        }

                                                             
        if element.element_type in ["InputField", "LabelField", "RadioButtonField", "CheckBoxField", "SpreadSheetDocumentField", "HTMLDocumentField"]:
            elem_data["attribute"] = element.attribute

                                                       
            is_form_attribute = any(fa.name == element.attribute for fa in form.form_attributes)
            elem_data["is_form_attribute"] = is_form_attribute

        elif element.element_type == "Button":
            elem_data["command"] = element.command

        elif element.element_type == "Table":
                                                              
            table_data = self._prepare_table_element(element, elem_id, allocator, form)
            elem_data.update(table_data)

        elif element.element_type == "ButtonGroup":
                                                         
            child_items = []
            if element.child_items:
                for child_elem in element.child_items:
                                                                          
                    child_data = self._process_form_element(child_elem, allocator, form)
                    child_items.append(child_data)

            elem_data["child_items"] = child_items

        elif element.element_type == "UsualGroup":
                                               
            child_items = []
            if element.child_items:
                for child_elem in element.child_items:
                                                                              
                    child_data = self._process_form_element(child_elem, allocator, form)
                    child_items.append(child_data)

            elem_data["child_items"] = child_items

        elif element.element_type == "ColumnGroup":
                                                                    
                                                                  
            child_items = []
            for child_elem in element.child_items:
                                                                                                   
                child_data = self._process_form_element(child_elem, allocator, form)
                child_items.append(child_data)

            elem_data["child_items"] = child_items

                                                                          
                                                                       

        return elem_data

    def _generate_local_pictures(self, form, form_ext_dir: Path, config_dir: Path = None) -> None:
                   
        from .svg_converter import SVGConverter
        import logging

        logger = logging.getLogger(__name__)
        converter = SVGConverter()

                                                            
        def process_elements(elements, level=0):
            for elem in elements:
                elem_properties = elem.properties or {}
                elem_name = elem.name

                                                   
                if 'svg_source' in elem_properties:
                    svg_source = elem_properties['svg_source']

                    logger.info(f"{'  ' * level}🎨 Processing SVG for element '{elem_name}'")

                                      
                    svg_path = Path(svg_source)
                    if not svg_path.is_absolute() and config_dir:
                        svg_path = config_dir / svg_source

                    if not svg_path.exists():
                        logger.error(f"{'  ' * level}❌ SVG file not found: {svg_path}")
                        continue

                    try:
                                                                   
                        items_dir = form_ext_dir / "Items" / elem_name
                        items_dir.mkdir(parents=True, exist_ok=True)

                                               
                        output_png = items_dir / "Picture.png"

                                                                                               
                                                                                        
                        width = elem_properties.get('svg_width') or elem_properties.get('width')
                        height = elem_properties.get('svg_height') or elem_properties.get('height')

                                               
                        logger.debug(f"{'  ' * level}   Converting: {svg_path} → {output_png}")
                        converter.convert_svg_to_png(
                            svg_path=str(svg_path),
                            output_path=str(output_png),
                            width=width,
                            height=height,
                            dpi=96
                        )

                                                               
                        try:
                            new_size = converter.optimize_size(str(output_png), max_size_kb=100)
                            logger.debug(
                                f"{'  ' * level}   PNG size: {new_size / 1024:.1f} KB"
                            )
                        except Exception as e:
                            logger.debug(f"{'  ' * level}   PNG optimization skipped: {e}")

                                                                                
                        del elem_properties['svg_source']

                                                                     
                                                                                  
                        elem_properties['local_picture'] = True

                        logger.info(
                            f"{'  ' * level}✅ Local picture generated: "
                            f"Items/{elem_name}/Picture.png"
                        )

                    except Exception as e:
                        logger.error(
                            f"{'  ' * level}❌ Failed to convert SVG for '{elem_name}': {e}"
                        )
                                                                                  
                        if 'svg_source' in elem_properties:
                            del elem_properties['svg_source']

                                                        
                if elem.child_items:
                    process_elements(elem.child_items, level + 1)
                elif 'child_items' in elem_properties:
                    process_elements(elem_properties['child_items'], level + 1)

                                      
        if form.elements:
            process_elements(form.elements)

    def _prepare_form_elements(self, form):
                   
                                                 
        preparer = ElementPreparer(self.processor)
        return preparer.prepare_form_elements(form)

    def _prepare_popup_element(self, elem, allocator: IDAllocator):
                   
        preparer = ElementPreparer(self.processor)
        return preparer._prepare_popup(elem, allocator)

    def _prepare_auto_command_bar(self, allocator_or_start_id, form):
                   
        preparer = ElementPreparer(self.processor)

                                                                     
        if isinstance(allocator_or_start_id, int):
            start_id = allocator_or_start_id
        else:
            start_id = allocator_or_start_id.current

        elements, _ = preparer.prepare_auto_command_bar(form, start_id)
        return elements

    def _save_snapshot(self, output_dir: Path, main_xml_path: Path, form_module_code: str):
                   
        import json
        from datetime import datetime

        snapshot_dir = output_dir / "_snapshot"
        snapshot_dir.mkdir(parents=True, exist_ok=True)

                           
        original_xml = snapshot_dir / "original.xml"
        if main_xml_path.exists():
            shutil.copy2(main_xml_path, original_xml)

                                    
        original_handlers = snapshot_dir / "original_handlers.bsl"
        original_handlers.write_text(form_module_code, encoding=ENCODING_UTF8_BOM)

                       
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "processor_name": self.processor.name,
            "platform_version": self.processor.platform_version,
            "config_dir": getattr(self.processor, 'config_dir', None),
            "generator_version": "2.25.0"                   
        }

        metadata_file = snapshot_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"📸 Snapshot saved to {snapshot_dir}")

    def save_snapshot_from_epf(
        self,
        epf_path: Path,
        output_dir: Path,
        compiler
    ) -> bool:
                   
        import json
        import tempfile
        from datetime import datetime

                                   
        snapshot_dir = output_dir / "_snapshot"
        snapshot_dir.mkdir(parents=True, exist_ok=True)

                                                                           
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_export = Path(temp_dir) / "export"
            temp_export.mkdir()

                           
            if not compiler.decompile_epf(epf_path, temp_export, timeout=120):
                print("   ❌ Failed to decompile EPF for snapshot")
                return False

                                               
                                                                               
            processor_name = self.processor.name
            exported_xml = temp_export / f"{processor_name}.xml"
            exported_dir = temp_export / processor_name

            if not exported_xml.exists():
                print(f"   ❌ Exported XML not found: {exported_xml}")
                return False

                                       
            original_xml = snapshot_dir / "original.xml"
            shutil.copy2(exported_xml, original_xml)

                                                                                  
            if exported_dir.exists():
                snapshot_processor_dir = snapshot_dir / processor_name
                if snapshot_processor_dir.exists():
                    shutil.rmtree(snapshot_processor_dir)
                shutil.copytree(exported_dir, snapshot_processor_dir)

                                                       
                form_xml_files = list(snapshot_processor_dir.glob("Forms/*/Ext/Form.xml"))
            else:
                print(f"   ⚠️  Exported processor directory not found: {exported_dir}")

                                                                       
                                   
            object_module_path = exported_dir / "Ext" / "ObjectModule.bsl"
            combined_bsl = ""

            if object_module_path.exists():
                with open(object_module_path, 'r', encoding='utf-8-sig') as f:
                    combined_bsl = f.read()

                                              
            forms_dir = exported_dir / "Forms"
            if forms_dir.exists():
                for form_dir in forms_dir.iterdir():
                    if form_dir.is_dir():
                        form_module_path = form_dir / "Ext" / "Form" / "Module.bsl"
                        if form_module_path.exists():
                            with open(form_module_path, 'r', encoding='utf-8-sig') as f:
                                form_bsl = f.read()
                                if combined_bsl:
                                    combined_bsl += "\n\n" + form_bsl
                                else:
                                    combined_bsl = form_bsl

                                        
            original_handlers = snapshot_dir / "original_handlers.bsl"
            original_handlers.write_text(combined_bsl, encoding=ENCODING_UTF8_BOM)

                           
            metadata = {
                "generated_at": datetime.now().isoformat(),
                "processor_name": self.processor.name,
                "platform_version": self.processor.platform_version,
                "config_dir": getattr(self.processor, 'config_dir', None),
                "generator_version": "2.32.0",                   
                "snapshot_type": "epf_export",                                         
                "has_form_xml": len(form_xml_files) if 'form_xml_files' in locals() else 0
            }

            metadata_file = snapshot_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"📸 Snapshot saved from EPF export to {snapshot_dir}")
        if 'form_xml_files' in locals():
            print(f"   ✅ Includes {len(form_xml_files)} Form.xml files for sync tool")

        return True

    def generate(self, output_dir: str, dry_run: bool = False, save_snapshot: bool = True) -> Optional[Path]:
                   
                   
        if not self.validate():
            return None

        if dry_run:
            print("\n🔍 DRY RUN MODE - файли не будуть створені\n")

        output_path = Path(output_dir)
        processor_name = self.processor.name

                                                               
        processor_root = output_path / processor_name

        if not dry_run:
            processor_root.mkdir(parents=True, exist_ok=True)

                                      
        processor_dir = processor_root / processor_name
        ext_dir = processor_dir / "Ext"

        if not dry_run:
            for dir_path in [processor_dir, ext_dir]:
                dir_path.mkdir(parents=True, exist_ok=True)

        print(f"📁 {'[DRY RUN] Структура папок:' if dry_run else 'Створення структури папок:'} {processor_root}")

                                                          
        print(f"📝 {'[DRY RUN] Генерація' if dry_run else 'Генерація'} головного XML файлу...")
        template = self.env.get_template("processor.xml.j2")
        content = template.render(
            processor=self.processor,
            namespaces=self._render_namespaces(XML_NAMESPACES),
            version=self.processor.platform_version,
            class_id=CLASS_ID_EXTERNAL_DATA_PROCESSOR,
        )

        main_xml = processor_root / f"{processor_name}.xml"
        if not dry_run:
                                                              
            main_xml.write_text(content, encoding=ENCODING_UTF8_BOM)
        print(f"   {'📄' if dry_run else '✅'} {main_xml} ({len(content)} bytes)")

                             
        print(f"📝 {'[DRY RUN] Генерація' if dry_run else 'Генерація'} модуля об'єкта...")
        object_module = ext_dir / "ObjectModule.bsl"
                                                                     
        if self.processor.object_module_bsl:
            object_module_code = self.processor.object_module_bsl
        else:
            object_module_code = self._generate_object_module_code()
        if not dry_run:
            object_module.write_text(object_module_code, encoding=ENCODING_UTF8_BOM)
        print(f"   {'📄' if dry_run else '✅'} {object_module} ({len(object_module_code)} bytes)")

                                       
        forms_to_generate = self.processor.forms

        if forms_to_generate:
            for form in forms_to_generate:
                form_name = form.name
                print(f"\n📝 Генерація форми '{form_name}'...")

                                                    
                forms_dir_for_form = processor_dir / "Forms" / form_name
                form_ext_dir_for_form = forms_dir_for_form / "Ext" / "Form"

                if not dry_run:
                    forms_dir_for_form.mkdir(parents=True, exist_ok=True)
                    form_ext_dir_for_form.mkdir(parents=True, exist_ok=True)

                                                                                    
                                                                                                           
                    config_dir = Path(self.processor.config_dir) if hasattr(self.processor, 'config_dir') and self.processor.config_dir else None
                    self._generate_local_pictures(form, form_ext_dir_for_form, config_dir)

                                                                                      
                preparer = ElementPreparer(self.processor)
                form_elements, next_id = preparer.prepare_form_elements(form)
                                                       
                auto_command_bar_elements, _ = preparer.prepare_auto_command_bar(form, next_id)

                                        
                form_module_code = self._generate_form_module_code(form)

                                                    
                commands = []
                for idx, cmd in enumerate(form.commands, start=1):
                    cmd_data = {
                        "id": idx,
                        "name": cmd.name,
                        "title_ru": cmd.title_ru,
                        "title_uk": cmd.title_uk,
                        "action": cmd.action,
                        "tooltip_ru": cmd.tooltip_ru,
                        "tooltip_uk": cmd.tooltip_uk,
                        "picture": cmd.picture,
                        "shortcut": cmd.shortcut,
                    }
                    commands.append(cmd_data)

                                                      
                value_table_attributes = []
                next_attr_id = 2                    
                for vt_attr in form.value_table_attributes:
                                             
                    columns_with_id = []
                    for idx, col in enumerate(vt_attr.columns, start=1):
                        col_data = {
                            "id": idx,
                            "name": col.name,
                            "type": col.type,
                            "synonym_ru": col.synonym_ru,
                            "synonym_uk": col.synonym_uk,
                            "length": col.length,
                            "digits": col.digits,
                            "fraction_digits": col.fraction_digits,
                        }
                        columns_with_id.append(col_data)

                    vt_data = {
                        "id": next_attr_id,
                        "name": vt_attr.name,
                        "title_ru": vt_attr.title_ru,
                        "title_uk": vt_attr.title_uk,
                        "columns": columns_with_id,
                    }
                    value_table_attributes.append(vt_data)
                    next_attr_id += 1

                                                                    
                form_attributes_list = []
                for fa_attr in form.form_attributes:
                    from .constants import TYPE_MAPPING

                                                                                      
                    xml_type = TYPE_MAPPING.get(fa_attr.type, fa_attr.type)

                    fa_data = {
                        "id": next_attr_id,
                        "name": fa_attr.name,
                        "type": fa_attr.type,                                             
                        "xml_type": xml_type,                                                  
                        "title_ru": fa_attr.title_ru,
                        "title_uk": fa_attr.title_uk,
                        "title_en": fa_attr.title_en,
                    }

                                                          
                    if fa_attr.type == "planner":
                        fa_data["time_scale"] = fa_attr.time_scale or "Hour"
                        fa_data["time_scale_interval"] = fa_attr.time_scale_interval
                        fa_data["time_scale_format"] = fa_attr.time_scale_format or 'DF="HH:mm"'
                        fa_data["display_current_date"] = fa_attr.display_current_date
                        fa_data["show_weekends"] = fa_attr.show_weekends

                    form_attributes_list.append(fa_data)
                    next_attr_id += 1

                                                       
                dynamic_list_attributes = []
                for dl_attr in form.dynamic_list_attributes:
                                                                           
                    has_table = any(
                        elem.element_type == "Table"
                        and elem.properties.get("is_dynamic_list", False)
                        and elem.tabular_section == dl_attr.name
                        for elem in form.elements
                    )

                    dl_data = {
                        "id": next_attr_id,
                        "name": dl_attr.name,
                        "title_ru": dl_attr.title_ru,
                        "title_uk": dl_attr.title_uk,
                        "manual_query": dl_attr.manual_query,
                        "main_table": dl_attr.main_table,
                        "query_text": dl_attr.query_text,
                        "key_fields": dl_attr.key_fields,
                        "use_always_fields": dl_attr.use_always_fields if has_table else [],
                        "functional_options": dl_attr.functional_options,
                        "auto_save_user_settings": dl_attr.auto_save_user_settings,
                        "main_attribute": dl_attr.main_attribute,
                        "dynamic_data_read": bool(dl_attr.main_table),
                                                                           
                        "filter_setting_id": dl_attr.filter_setting_id,
                        "order_setting_id": dl_attr.order_setting_id,
                        "appearance_setting_id": dl_attr.appearance_setting_id,
                        "items_setting_id": dl_attr.items_setting_id,
                    }
                    dynamic_list_attributes.append(dl_data)
                    next_attr_id += 1

                                                       
                command_pictures = {cmd["name"]: cmd.get("picture") for cmd in commands if cmd.get("picture")}

                                                      
                template = self.env.get_template("form_meta.xml.j2")
                content = template.render(
                    processor=self.processor,
                    namespaces=self._render_namespaces(XML_NAMESPACES),
                    version=self.processor.platform_version,
                    form=form,
                )

                forms_root_dir = processor_dir / "Forms"
                form_meta_xml = forms_root_dir / f"{form_name}.xml"
                if not dry_run:
                                                                      
                    form_meta_xml.write_text(content, encoding=ENCODING_UTF8_BOM)
                print(f"   {'📄' if dry_run else '✅'} {form_meta_xml} ({len(content)} bytes)")

                                                      
                template = self.env.get_template("form.xml.j2")
                content = template.render(
                    processor=self.processor,
                    commands=commands,
                    command_pictures=command_pictures,
                    form_elements=form_elements,
                    auto_command_bar_elements=auto_command_bar_elements,
                    form_attributes=form_attributes_list,
                    value_table_attributes=value_table_attributes,
                    dynamic_list_attributes=dynamic_list_attributes,
                    namespaces=self._render_namespaces(FORM_XML_NAMESPACES),
                    version=self.processor.platform_version,
                    form=form,
                )

                                                               
                import re
                                                                                               
                content = re.sub(r'(>)(\t|<)', r'\1\n\2', content)
                                                                            
                content = re.sub(r'\n\n\n+', '\n', content)

                form_xml = form_ext_dir_for_form.parent / "Form.xml"
                if not dry_run:
                                                                      
                    form_xml.write_text(content, encoding=ENCODING_UTF8_BOM)
                print(f"   {'📄' if dry_run else '✅'} {form_xml} ({len(content)} bytes)")

                                                     
                form_module = form_ext_dir_for_form / "Module.bsl"
                if not dry_run:
                    form_module.write_text(form_module_code, encoding=ENCODING_UTF8_BOM)
                print(f"   {'📄' if dry_run else '✅'} {form_module} ({len(form_module_code)} bytes)")

                                                                       
        if self.processor.templates:
            from .template_xml_generator import generate_all_templates
            generate_all_templates(
                templates=self.processor.templates,
                processor_dir=processor_dir,
                env=self.env,
                namespaces=self._render_namespaces(XML_NAMESPACES),
                platform_version=self.processor.platform_version,
                dry_run=dry_run
            )

        if dry_run:
            print(f"\n✅ DRY RUN завершено успішно!")
            print(f"📊 Форм: {len(forms_to_generate)}")
            print(f"📊 Атрибутів: {len(self.processor.attributes)}")
            print(f"📊 Табличних частин: {len(self.processor.tabular_sections)}")
            print(f"📂 Папка (не створена): {processor_root}")
            return None                            
        else:
            print(f"\n🎉 Обробка '{processor_name}' успішно згенерована!")
            print(f"📊 Згенеровано форм: {len(forms_to_generate)}")
            print(f"📂 Розташування: {processor_root}")
            print(f"\n💡 Відкрийте в 1C: Файл → Відкрити → {processor_root / main_xml.name}")

                                                   
            if forms_to_generate:                                 
                post_validator = PostGenerationValidator(self.processor, output_path)
                validation_passed = post_validator.validate_generation(verbose=True)

                if not validation_passed:
                    print("\n⚠️  WARNING: Post-generation validation detected issues.")
                    print("    The processor was generated, but may have missing elements.")
                    print("    Please review the validation report above.")

                                                    
            if save_snapshot and forms_to_generate:
                                                          
                combined_bsl = ""
                for form in forms_to_generate:
                    form_module_code = self._generate_form_module_code(form)
                    combined_bsl += form_module_code + "\n\n"

                self._save_snapshot(
                    output_dir=output_path,
                    main_xml_path=main_xml,
                    form_module_code=combined_bsl.strip()
                )

        return processor_root                                              


def create_minimal_processor(name: str, platform_version: str = "2.11") -> Processor:
           
    from .models import FormElement

    processor = Processor(
        name=name,
        platform_version=platform_version,
    )

                                  
    processor.add_attribute(
        name="ТекстоваяСтрока",
        type="string",
        synonym_ru="Текстовая строка",
        synonym_uk="Текстовий рядок",
        length=100,
    )

                     
    form = processor.add_form(name="Форма", default=True)

                                 
    form.elements.append(FormElement(
        element_type="InputField",
        name="ТекстоваяСтрока",
        attribute="ТекстоваяСтрока",
    ))

    return processor
