   

from dataclasses import dataclass, field
from typing import Dict, Optional

                                                   
from .pro._gc import get_generation_context

                                               
_gen_ctx = get_generation_context()
ELEMENT_ID_INCREMENTS = _gen_ctx["element_id_increments"]


@dataclass
class IDAllocator:
           

    _start_id: int = 1
    _current_id: int = field(default=1, init=False)
    _allocations: Dict[str, int] = field(default_factory=dict, init=False)
    _debug: bool = False

    def __post_init__(self):
                                                  
        self._current_id = self._start_id

    def allocate(self, element_type: str, element_name: Optional[str] = None) -> int:
                   
        allocated_id = self._current_id
        increment = ELEMENT_ID_INCREMENTS.get(element_type, 3)              
        self._current_id += increment

                                         
        if self._debug:
            key = f"{element_type}:{element_name or 'unnamed'}@{allocated_id}"
            self._allocations[key] = increment

        return allocated_id

    def allocate_table_column(self, column_name: Optional[str] = None) -> int:
                   
        return self.allocate("TableColumn", column_name)

    def allocate_page(self, page_name: Optional[str] = None) -> int:
                   
        return self.allocate("Page", page_name)

    def peek(self) -> int:
                   
        return self._current_id

    def skip(self, count: int) -> None:
                   
        self._current_id += count

    def reserve(self, count: int) -> int:
                   
        start_id = self._current_id
        self._current_id += count
        return start_id

    @property
    def current(self) -> int:
                                                
        return self._current_id

    def reset(self, start_id: int = 1) -> None:
                   
        self._current_id = start_id
        self._allocations.clear()

    def get_allocations(self) -> Dict[str, int]:
                   
        return self._allocations.copy()

    def __repr__(self) -> str:
        return f"IDAllocator(current={self._current_id}, allocations={len(self._allocations)})"


def create_allocator(start_id: int = 1, debug: bool = False) -> IDAllocator:
           
    return IDAllocator(_start_id=start_id, _debug=debug)
