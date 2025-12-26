   

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class StructuralUpdate:
           
    operation: str                     
    element_type: str                                                
    element_name: str
    element_data: Optional[Dict[str, Any]] = None
    form_index: int = 0
    parent_path: Optional[str] = None                                
    insertion_index: Optional[int] = None                            
    depth: int = 0                          


class ChangeFormatter:
           

    def __init__(self, use_unicode: bool = True):
                   
        self.use_unicode = use_unicode

                                
        if use_unicode:
            self.symbols = {
                'add': '➕',
                'delete': '➖',
                'modify': '🔄',
                'tree': '└─',
                'branch': '├─',
                'indent': '│  ',
                'space': '   '
            }
        else:
            self.symbols = {
                'add': '[+]',
                'delete': '[-]',
                'modify': '[~]',
                'tree': '`-',
                'branch': '+-',
                'indent': '|  ',
                'space': '   '
            }

    def format_change(
        self,
        update: StructuralUpdate,
        mode: str = 'simple',
        config: Optional[Dict[str, Any]] = None,
        references: Optional[List[str]] = None
    ) -> str:
                   
        if mode == 'simple':
            return self._format_simple(update)
        elif mode == 'detailed':
            return self._format_detailed(update, references)
        elif mode == 'hierarchical':
            return self._format_hierarchical(update, config, references)
        else:
            logger.warning(f"Unknown format mode: {mode}, using simple")
            return self._format_simple(update)

    def _format_simple(self, update: StructuralUpdate) -> str:
                   
        symbol = self.symbols.get(update.operation, '?')
        op = update.operation.upper()
        elem_type = update.element_type.replace('_', ' ')
        name = update.element_name

        return f"{symbol} {op} {elem_type}: {name}"

    def _format_detailed(
        self,
        update: StructuralUpdate,
        references: Optional[List[str]] = None
    ) -> str:
                   
        lines = []

                
        symbol = self.symbols.get(update.operation, '?')
        op = update.operation.upper()
        elem_type = update.element_type.replace('_', ' ')
        lines.append(f"{symbol} {op} {elem_type}: {update.element_name}")

                  
        metadata = []
        metadata.append(f"  Form: index {update.form_index}")

        if update.parent_path:
            metadata.append(f"  Parent: {update.parent_path}")

        if update.insertion_index is not None:
            metadata.append(f"  Position: index {update.insertion_index}")

        if update.depth > 0:
            metadata.append(f"  Depth: {update.depth} level(s)")

        if update.element_data:
                                               
            if 'type' in update.element_data:
                metadata.append(f"  Type: {update.element_data['type']}")
            if 'attribute' in update.element_data:
                metadata.append(f"  Attribute: {update.element_data['attribute']}")
            if 'value_table' in update.element_data:
                metadata.append(f"  ValueTable: {update.element_data['value_table']}")

        lines.extend(metadata)

                                
        if references:
            lines.append(f"  References: {len(references)}")
            for ref in references[:3]:                
                lines.append(f"    - {ref}")
            if len(references) > 3:
                lines.append(f"    ... and {len(references) - 3} more")

        return '\n'.join(lines)

    def _format_hierarchical(
        self,
        update: StructuralUpdate,
        config: Optional[Dict[str, Any]],
        references: Optional[List[str]] = None
    ) -> str:
                   
        lines = []

                
        symbol = self.symbols.get(update.operation, '?')
        op = update.operation.upper()
        elem_type = update.element_type.replace('_', ' ')
        lines.append(f"{symbol} {op} {elem_type}: {update.element_name}")

                              
        if config and update.parent_path:
            path_parts = self._parse_path(update.parent_path)
            lines.append("\n  Hierarchy:")
            lines.extend(self._format_path_hierarchy(path_parts, config, update))
        elif config:
                               
            lines.append(f"\n  Location: Top-level in form {update.form_index}")

                    
        if references:
            lines.append(f"\n  {self.symbols['modify']} References ({len(references)}):")
            for ref in references[:5]:
                lines.append(f"    - {ref}")
            if len(references) > 5:
                lines.append(f"    ... and {len(references) - 5} more")

        return '\n'.join(lines)

    def format_references(
        self,
        references: List[str],
        max_display: int = 10,
        title: str = "References found"
    ) -> str:
                   
        if not references:
            return "No references found"

        lines = []
        lines.append(f"{self.symbols['modify']} {title} ({len(references)}):")

        for i, ref in enumerate(references[:max_display]):
            lines.append(f"  {i+1}. {ref}")

        if len(references) > max_display:
            remaining = len(references) - max_display
            lines.append(f"  ... and {remaining} more")

        return '\n'.join(lines)

    def format_summary(
        self,
        updates: List[StructuralUpdate],
        title: str = "Structural Changes Summary"
    ) -> str:
                   
        if not updates:
            return "No structural changes"

        lines = []
        lines.append(f"\n{'=' * 60}")
        lines.append(f"{title}")
        lines.append(f"{'=' * 60}")

                            
        add_count = sum(1 for u in updates if u.operation == 'add')
        delete_count = sum(1 for u in updates if u.operation == 'delete')
        modify_count = sum(1 for u in updates if u.operation == 'modify')

        lines.append(f"\nTotal: {len(updates)} change(s)")
        if add_count > 0:
            lines.append(f"  {self.symbols['add']} Add: {add_count}")
        if delete_count > 0:
            lines.append(f"  {self.symbols['delete']} Delete: {delete_count}")
        if modify_count > 0:
            lines.append(f"  {self.symbols['modify']} Modify: {modify_count}")

                               
        lines.append("\nBy element type:")
        type_counts = {}
        for update in updates:
            elem_type = update.element_type
            type_counts[elem_type] = type_counts.get(elem_type, 0) + 1

        for elem_type, count in sorted(type_counts.items()):
            lines.append(f"  - {elem_type.replace('_', ' ')}: {count}")

                          
        lines.append(f"\nChanges:")
        for i, update in enumerate(updates, 1):
            symbol = self.symbols.get(update.operation, '?')
            lines.append(f"  {i}. {symbol} {update.operation.upper()} "
                        f"{update.element_type}: {update.element_name}")

        lines.append(f"{'=' * 60}\n")
        return '\n'.join(lines)

    def _parse_path(self, path: str) -> List[Dict[str, Any]]:
                   
        components = []
        parts = path.replace('[', '.').replace(']', '').split('.')

        i = 0
        while i < len(parts):
            if not parts[i]:
                i += 1
                continue

            component = {'key': parts[i]}

                                                    
            if i + 1 < len(parts) and parts[i + 1].isdigit():
                component['index'] = int(parts[i + 1])
                i += 2
            else:
                i += 1

            components.append(component)

        return components

    def _format_path_hierarchy(
        self,
        path_parts: List[Dict[str, Any]],
        config: Dict[str, Any],
        update: StructuralUpdate
    ) -> List[str]:
                   
        lines = []
        current = config
        indent_level = 0

        for i, part in enumerate(path_parts):
            is_last = (i == len(path_parts) - 1)
            symbol = self.symbols['tree'] if is_last else self.symbols['branch']
            indent = self.symbols['indent'] * indent_level

                         
            key = part['key']
            index = part.get('index')

                                         
            try:
                if index is not None:
                    current = current[key][index]
                    name = current.get('name', f'{key}[{index}]')
                    elem_type = current.get('type', current.get('element_type', key))
                    lines.append(f"  {indent}{symbol} {elem_type}: {name}")
                else:
                    current = current.get(key, {})
                    lines.append(f"  {indent}{symbol} {key}")
            except (KeyError, IndexError, TypeError):
                lines.append(f"  {indent}{symbol} {key}[{index if index is not None else '?'}]")

            indent_level += 1

                                                    
        final_indent = self.symbols['indent'] * indent_level
        symbol = self.symbols.get(update.operation, '?')
        lines.append(f"  {final_indent}{self.symbols['tree']} {symbol} {update.element_name} "
                    f"[{update.operation.upper()}]")

        return lines

    def format_conflict(
        self,
        element_name: str,
        element_type: str,
        reason: str,
        suggestions: Optional[List[str]] = None
    ) -> str:
                   
        lines = []
        lines.append(f"\n⚠️  CONFLICT: {element_type} '{element_name}'")
        lines.append(f"Reason: {reason}")

        if suggestions:
            lines.append("\nSuggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                lines.append(f"  {i}. {suggestion}")

        return '\n'.join(lines)

    def format_warning(
        self,
        message: str,
        details: Optional[List[str]] = None
    ) -> str:
                   
        lines = []
        lines.append(f"⚠️  WARNING: {message}")

        if details:
            for detail in details:
                lines.append(f"  - {detail}")

        return '\n'.join(lines)

    def format_success(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
                   
        lines = []
        lines.append(f"✅ {message}")

        if details:
            for key, value in details.items():
                lines.append(f"  {key}: {value}")

        return '\n'.join(lines)
