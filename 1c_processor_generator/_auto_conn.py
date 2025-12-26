   

import logging
import threading
import traceback
from typing import Any, List, Dict
from pathlib import Path

from ._conn import BaseConnection

                   
try:
    import win32com.client
    import pythoncom
    HAS_COM_SUPPORT = True
except ImportError:
    HAS_COM_SUPPORT = False

logger = logging.getLogger(__name__)


class AutomationServerConnection(BaseConnection):
           

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.automation = None                          
        self.form = None                             

    def connect(self) -> bool:
                   
        raise NotImplementedError(
            "AutomationServerConnection cannot be implemented due to COM limitations.\n"
            "\n"
            "V83.Application is not accessible from Python/PowerShell:\n"
            "  - Python: RPC_E_DISCONNECTED error\n"
            "  - PowerShell: Connect() succeeds but object is hollow\n"
            "  - Only works from 1C BSL code\n"
            "\n"
            "Forms also unavailable via V83.COMConnector:\n"
            "  - ПолучитьФорму fails with 'Интерактивные операции недоступны'\n"
            "  - External Connection is headless by design\n"
            "\n"
            "Use ExternalConnection (V83.COMConnector) for ObjectModule tests.\n"
            "See docs/research/V83_INVESTIGATION_REPORT.md for technical details."
        )

    def disconnect(self):
                                                             
        if self.form:
            self.form = None
        if self.automation:
                                                           
            self.automation = None
            self.connection = None
            self.processor = None
            logger.info("Connection closed")

    def set_attribute(self, attr_name: str, value: Any):
                   
        try:
                                           
            if self.form:
                obj = getattr(self.form, "Объект", None)
                if obj:
                    setattr(obj, attr_name, value)
                    logger.debug(f"Set {attr_name} = {value} (via form)")
                    return

                                   
            obj = getattr(self.processor, "Объект", self.processor)
            setattr(obj, attr_name, value)
            logger.debug(f"Set {attr_name} = {value}")

        except Exception as e:
            logger.error(f"❌ Error setting {attr_name}: {e}")
            raise

    def get_attribute(self, attr_name: str) -> Any:
                   
        try:
                                           
            if self.form:
                obj = getattr(self.form, "Объект", None)
                if obj:
                    return getattr(obj, attr_name)

                                   
            obj = getattr(self.processor, "Объект", self.processor)
            return getattr(obj, attr_name)

        except Exception as e:
            logger.error(f"❌ Error reading {attr_name}: {e}")
            raise

    def execute_command(self, command_name: str):
                   
        try:
            if self.form:
                                                      
                                                               
                command_handler = f"{command_name}НаСервере"
                if hasattr(self.form, command_handler):
                    handler = getattr(self.form, command_handler)
                    handler()
                    logger.debug(f"Executed form command: {command_handler}")
                    return

                                              
                if hasattr(self.form, command_name):
                    handler = getattr(self.form, command_name)
                    handler()
                    logger.debug(f"Executed form command: {command_name}")
                    return

                                          
            command_method = getattr(self.processor, command_name)
            command_method()
            logger.debug(f"Executed processor command: {command_name}")

        except Exception as e:
            logger.error(f"❌ Error executing command {command_name}: {e}")
            raise

    def execute_procedure(self, procedure_name: str):
                                    
        try:
                            
            if self.form and hasattr(self.form, procedure_name):
                procedure = getattr(self.form, procedure_name)
                procedure()
                logger.debug(f"Executed form procedure: {procedure_name}")
                return

                                   
            procedure = getattr(self.processor, procedure_name)
            procedure()
            logger.debug(f"Executed processor procedure: {procedure_name}")

        except Exception as e:
            logger.error(f"❌ Error executing procedure {procedure_name}: {e}")
            raise

    def fill_table(self, table_name: str, rows: List[Dict[str, Any]]):
                                             
        try:
                                   
            if self.form:
                obj = getattr(self.form, "Объект", None)
                if obj:
                    table = getattr(obj, table_name)
                    table.Очистить()

                    for row_data in rows:
                        row = table.Добавить()
                        for column, value in row_data.items():
                            setattr(row, column, value)

                    logger.debug(f"Filled {table_name}: {len(rows)} rows (via form)")
                    return

                                          
            obj = getattr(self.processor, "Объект", self.processor)
            table = getattr(obj, table_name)
            table.Очистить()

            for row_data in rows:
                row = table.Добавить()
                for column, value in row_data.items():
                    setattr(row, column, value)

            logger.debug(f"Filled {table_name}: {len(rows)} rows")

        except Exception as e:
            logger.error(f"❌ Error filling table {table_name}: {e}")
            raise

    def start_message_recording(self):
                   
        try:
            if self.form and hasattr(self.form, "НачатьЗаписьСообщений"):
                self.form.НачатьЗаписьСообщений()
                logger.debug("Message recording started (via form)")
                return

                                                      
            if hasattr(self.processor, "НачатьЗаписьСообщений"):
                self.processor.НачатьЗаписьСообщений()
                logger.debug("Message recording started (via processor)")
                return

            logger.warning("⚠️  Method НачатьЗаписьСообщений not found")

        except Exception as e:
            logger.error(f"❌ Error starting message recording: {e}")

    def get_test_messages(self) -> List[str]:
                   
        try:
                            
            if self.form and hasattr(self.form, "ПолучитьТестовыеСообщения"):
                messages_array = self.form.ПолучитьТестовыеСообщения()

                                                 
                messages = []
                for i in range(messages_array.Количество()):
                    messages.append(str(messages_array.Получить(i)))

                return messages

                                   
            if hasattr(self.processor, "ПолучитьТестовыеСообщения"):
                messages_array = self.processor.ПолучитьТестовыеСообщения()

                messages = []
                for i in range(messages_array.Количество()):
                    messages.append(str(messages_array.Получить(i)))

                return messages

            logger.warning("⚠️  Method ПолучитьТестовыеСообщения not found")
            return []

        except Exception as e:
            logger.error(f"❌ Error getting messages: {e}")
            return []

                                                          

    def get_form(self, form_name: str = "Форма"):
                   
        try:
            self.form = self.processor.ПолучитьФорму(form_name)
            logger.debug(f"Form '{form_name}' obtained")
            return self.form
        except Exception as e:
            logger.error(f"❌ Error getting form '{form_name}': {e}")
            raise

    def click_button(self, button_name: str):
                   
        if not self.form:
            raise RuntimeError("Form not loaded. Call get_form() first or use load_from_configuration=True")

        try:
                                             
                                              
            if hasattr(self.form, button_name):
                handler = getattr(self.form, button_name)
                handler()
                logger.debug(f"Button '{button_name}' clicked (direct handler)")
                return

                                      
            server_handler = f"{button_name}НаСервере"
            if hasattr(self.form, server_handler):
                handler = getattr(self.form, server_handler)
                handler()
                logger.debug(f"Button '{button_name}' clicked (server handler)")
                return

            logger.error(f"❌ Button handler '{button_name}' not found on form")
            raise AttributeError(f"Button handler '{button_name}' not found")

        except Exception as e:
            logger.error(f"❌ Error clicking button '{button_name}': {e}")
            raise

    def set_field_value(self, field_name: str, value: Any):
                   
        if not self.form:
                                   
            self.set_attribute(field_name, value)
            return

        try:
                                     
            if hasattr(self.form, "Elements"):
                element = getattr(self.form.Elements, field_name, None)
                if element:
                    element.Value = value
                    logger.debug(f"Field '{field_name}' set to {value} (via Elements)")
                    return

                                     
            obj = getattr(self.form, "Объект", None)
            if obj:
                setattr(obj, field_name, value)
                logger.debug(f"Field '{field_name}' set to {value} (via Объект)")
                return

            logger.warning(f"⚠️  Field '{field_name}' not found, using set_attribute")
            self.set_attribute(field_name, value)

        except Exception as e:
            logger.error(f"❌ Error setting field '{field_name}': {e}")
            raise

    def get_field_value(self, field_name: str) -> Any:
                   
        if not self.form:
                                   
            return self.get_attribute(field_name)

        try:
                                     
            if hasattr(self.form, "Elements"):
                element = getattr(self.form.Elements, field_name, None)
                if element:
                    return element.Value

                                     
            obj = getattr(self.form, "Объект", None)
            if obj:
                return getattr(obj, field_name)

            logger.warning(f"⚠️  Field '{field_name}' not found, using get_attribute")
            return self.get_attribute(field_name)

        except Exception as e:
            logger.error(f"❌ Error getting field '{field_name}': {e}")
            raise

    def get_table_element(self, table_name: str):
                   
        if not self.form:
            raise RuntimeError("Form not loaded. Call get_form() first")

        try:
            if hasattr(self.form, "Elements"):
                return getattr(self.form.Elements, table_name)
            raise AttributeError(f"Form.Elements.{table_name} not found")
        except Exception as e:
            logger.error(f"❌ Error getting table element '{table_name}': {e}")
            raise
