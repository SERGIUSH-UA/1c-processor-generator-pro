   

from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class BaseConnection(ABC):
           

    def __init__(
        self,
        epf_path: Path,
        ib_path: Path,
        load_from_configuration: bool = False,
        processor_name: Optional[str] = None,
        debug: bool = False,
    ):
                   
        self.epf_path = epf_path
        self.ib_path = ib_path
        self.load_from_configuration = load_from_configuration
        self.processor_name = processor_name
        self.debug = debug

                                                
        self.connection = None
        self.processor = None

    @abstractmethod
    def connect(self) -> bool:
                   
        pass

    @abstractmethod
    def disconnect(self):
                                                     
        pass

    def get_processor(self):
                   
        return self.processor

    @abstractmethod
    def set_attribute(self, attr_name: str, value: Any):
                   
        pass

    @abstractmethod
    def get_attribute(self, attr_name: str) -> Any:
                   
        pass

    @abstractmethod
    def execute_command(self, command_name: str):
                   
        pass

    @abstractmethod
    def execute_procedure(self, procedure_name: str):
                   
        pass

    @abstractmethod
    def fill_table(self, table_name: str, rows: List[Dict[str, Any]]):
                   
        pass

    @abstractmethod
    def start_message_recording(self):
                                                                    
        pass

    @abstractmethod
    def get_test_messages(self) -> List[str]:
                   
        pass

                                                              

    def _load_processor_external(self) -> bool:
                   
        try:
            logger.info(f"Loading processor: {self.epf_path}...")

                                            
            self.processor = self.connection.ExternalDataProcessors.Create(str(self.epf_path))

            logger.info("✅ Processor loaded")
            return True

        except Exception as e:
            logger.error(f"❌ Processor loading error: {e}")
            return False

    def _load_from_configuration(self) -> bool:
                   
        try:
            logger.info(f"Loading processor from configuration: {self.processor_name}_Validation...")

                                                        
                                                                              
            processor_full_name = f"{self.processor_name}_Validation"

                                                                               
            self.processor = getattr(
                self.connection.DataProcessors,
                processor_full_name
            ).Create()

            logger.info("✅ Processor loaded from configuration (no security warning)")
            return True

        except AttributeError:
            logger.error(f"❌ Processor '{processor_full_name}' not found in configuration")
            logger.error(f"   Ensure temp_ib contains Configuration with processor")
            return False

        except Exception as e:
            logger.error(f"❌ Configuration processor loading error: {e}")
            return False
