   

from typing import List, Dict, Tuple
from .id_allocator import IDAllocator
from .pro._ep import ElementPreparerImpl


class ElementPreparer:
           

    def __init__(self, processor):
                                         
        self._impl = ElementPreparerImpl(processor, IDAllocator)
        self._processor = processor

    @property
    def processor(self):
                                                        
        return self._processor

    def prepare_form_elements(self, form) -> Tuple[List[Dict], int]:
                                        
        return self._impl.prepare_form_elements(form)

    def prepare_auto_command_bar(self, form, start_id: int) -> Tuple[List[Dict], int]:
                                              
        return self._impl.prepare_auto_command_bar(form, start_id)

    def _set_table_context(self, element, tabular_section: str, is_value_table: bool):
                                                        
        return self._impl._set_table_context(element, tabular_section, is_value_table)

    def _prepare_popup(self, elem, allocator):
                                                                  
        return self._impl._prepare_popup(elem, allocator)
