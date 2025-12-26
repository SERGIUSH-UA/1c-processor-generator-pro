   

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


class ExternalConnection(BaseConnection):
           

    def connect(self) -> bool:
                   
        if not HAS_COM_SUPPORT:
            logger.error("❌ pywin32 not installed. COM connections unavailable.")
            logger.info("   Install: pip install pywin32")
            raise ImportError("pywin32 required for COM connections")

        try:
            logger.info(f"Connecting to {self.ib_path} via External Connection...")

                                                      
            if self.debug:
                import sys as _sys
                thread_id = threading.get_ident()
                logger.debug(f"🔍 DEBUG: Thread ID: {thread_id}")
                logger.debug(f"🔍 DEBUG: Python version: {_sys.version}")
                logger.debug(f"🔍 DEBUG: pywin32 version: {win32com.__version__ if hasattr(win32com, '__version__') else 'unknown'}")

                try:
                    com_count = pythoncom._GetInterfaceCount()
                    logger.debug(f"🔍 DEBUG: COM Interface Count (before): {com_count}")
                except Exception as e:
                    logger.debug(f"🔍 DEBUG: COM Interface Count unavailable: {e}")

                                  
            logger.debug("Creating V83.COMConnector...")
            connector = win32com.client.Dispatch("V83.COMConnector")

            if self.debug:
                logger.debug(f"✅ V83.COMConnector created: {type(connector)}")
                try:
                    com_count = pythoncom._GetInterfaceCount()
                    logger.debug(f"🔍 DEBUG: COM Interface Count (after Dispatch): {com_count}")
                except:
                    pass

                                     
            conn_string = f"File='{self.ib_path}';Usr='';Pwd=''"
            if self.debug:
                logger.debug(f"🔍 DEBUG: Connection string: {conn_string}")

                     
            logger.debug("Calling connector.Connect()...")
            self.connection = connector.Connect(conn_string)

            if self.debug:
                logger.debug(f"✅ connector.Connect() successful: {type(self.connection)}")
                try:
                    com_count = pythoncom._GetInterfaceCount()
                    logger.debug(f"🔍 DEBUG: COM Interface Count (after Connect): {com_count}")
                except:
                    pass

            logger.info("✅ External Connection established")

                                                                
                                                                               
            if self.load_from_configuration:
                return self._load_from_configuration()
            else:
                return self._load_processor_external()

        except Exception as e:
            logger.error(f"❌ External Connection error: {e}")

                                       
            if self.debug:
                logger.error(f"🔍 DEBUG: Exception type: {type(e).__name__}")
                logger.error(f"🔍 DEBUG: Exception args: {e.args}")
                logger.error(f"🔍 DEBUG: Detailed traceback:")
                logger.error(traceback.format_exc())

                try:
                    com_count = pythoncom._GetInterfaceCount()
                    logger.error(f"🔍 DEBUG: COM Interface Count (on error): {com_count}")
                except:
                    pass

            return False

    def disconnect(self):
                                                     
        if self.connection:
            self.connection = None
            self.processor = None
            logger.info("Connection closed")

    def set_attribute(self, attr_name: str, value: Any):
                                            
        try:
                                                            
            obj = getattr(self.processor, "Объект", self.processor)
            setattr(obj, attr_name, value)
            logger.debug(f"Set {attr_name} = {value}")
        except Exception as e:
            logger.error(f"❌ Error setting {attr_name}: {e}")
            raise

    def get_attribute(self, attr_name: str) -> Any:
                                            
        try:
            obj = getattr(self.processor, "Объект", self.processor)
            return getattr(obj, attr_name)
        except Exception as e:
            logger.error(f"❌ Error reading {attr_name}: {e}")
            raise

    def execute_command(self, command_name: str):
                                        
        try:
                                         
            command_method = getattr(self.processor, command_name)
            command_method()
            logger.debug(f"Executed command: {command_name}")
        except Exception as e:
            logger.error(f"❌ Error executing command {command_name}: {e}")
            raise

    def execute_procedure(self, procedure_name: str):
                                    
        try:
            procedure = getattr(self.processor, procedure_name)
            procedure()
            logger.debug(f"Executed procedure: {procedure_name}")
        except Exception as e:
            logger.error(f"❌ Error executing procedure {procedure_name}: {e}")
            raise

    def fill_table(self, table_name: str, rows: List[Dict[str, Any]]):
                                             
        try:
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
            if hasattr(self.processor, "НачатьЗаписьСообщений"):
                self.processor.НачатьЗаписьСообщений()
                logger.debug("Message recording started")
            else:
                logger.warning("⚠️  Method НачатьЗаписьСообщений not found in processor")
        except Exception as e:
            logger.error(f"❌ Error starting message recording: {e}")

    def get_test_messages(self) -> List[str]:
                   
        try:
            if hasattr(self.processor, "ПолучитьТестовыеСообщения"):
                messages_array = self.processor.ПолучитьТестовыеСообщения()

                                                 
                messages = []
                for i in range(messages_array.Количество()):
                    messages.append(str(messages_array.Получить(i)))

                return messages
            else:
                logger.warning("⚠️  Method ПолучитьТестовыеСообщения not found in processor")
                return []

        except Exception as e:
            logger.error(f"❌ Error getting messages: {e}")
            return []
