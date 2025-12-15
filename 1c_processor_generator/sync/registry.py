   

import logging
from typing import Dict, Iterator, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .base_handler import BaseElementHandler

logger = logging.getLogger(__name__)


class HandlerRegistry:
           

    _instance: Optional["HandlerRegistry"] = None
    _handlers: Dict[str, "BaseElementHandler"]
    _initialized: bool

    def __new__(cls) -> "HandlerRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers = {}
            cls._instance._initialized = False
        return cls._instance

    @classmethod
    def instance(cls) -> "HandlerRegistry":
                   
        registry = cls()
        if not registry._initialized:
            registry._register_builtin_handlers()
            registry._initialized = True
        return registry

    @classmethod
    def reset(cls) -> None:
                   
        if cls._instance is not None:
            cls._instance._handlers.clear()
            cls._instance._initialized = False

    def register(self, handler: "BaseElementHandler") -> None:
                   
        name = handler.element_type_name
        if name in self._handlers:
            logger.warning(f"Handler for '{name}' already registered, replacing")
        self._handlers[name] = handler
        logger.debug(f"Registered handler for '{name}'")

    def unregister(self, element_type: str) -> bool:
                   
        if element_type in self._handlers:
            del self._handlers[element_type]
            logger.debug(f"Unregistered handler for '{element_type}'")
            return True
        return False

    def get(self, element_type: str) -> Optional["BaseElementHandler"]:
                   
        return self._handlers.get(element_type)

    def all_handlers(self) -> Dict[str, "BaseElementHandler"]:
                   
        return self._handlers.copy()

    def handler_names(self) -> Iterator[str]:
                   
        return iter(self._handlers.keys())

    def __contains__(self, element_type: str) -> bool:
                                             
        return element_type in self._handlers

    def __len__(self) -> int:
                                            
        return len(self._handlers)

    def _register_builtin_handlers(self) -> None:
                   
                                                        
        from .handlers import (
            AttributeHandler,
            FormElementHandler,
            CommandHandler,
            TabularSectionHandler,
            ValueTableHandler,
            FormAttributeHandler,
            FormHandler,
            TemplateHandler,
            FormParameterHandler,
        )

        builtin_handlers = [
            AttributeHandler(),
            FormElementHandler(),
            CommandHandler(),
            TabularSectionHandler(),
            ValueTableHandler(),
            FormAttributeHandler(),
            FormHandler(),
            TemplateHandler(),
            FormParameterHandler(),
        ]

        for handler in builtin_handlers:
            self.register(handler)

        logger.info(f"Registered {len(builtin_handlers)} built-in handlers")
