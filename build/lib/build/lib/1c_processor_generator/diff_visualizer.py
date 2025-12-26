   

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from ruamel.yaml import YAML
from io import StringIO

logger = logging.getLogger(__name__)


@dataclass
class DiffLine:
                                                  
    line_number: Optional[int]
    content: str
    status: str                                               
    context: bool = False                                              


class DiffVisualizer:
           

    def __init__(self, context_lines: int = 3):
                   
        self.context_lines = context_lines
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
                                                         
        self.yaml.map_indent = 2
        self.yaml.sequence_indent = 2
        self.yaml.sequence_dash_offset = 0

    def visualize_yaml_change(
        self,
        element_type: str,
        element_name: str,
        operation: str,
        element_data: Optional[Dict[str, Any]],
        config: Dict[str, Any],
        yaml_path: Optional[str] = None
    ) -> str:
                   
        lines = []
        lines.append(f"\n{'=' * 70}")
        lines.append(f"YAML Change: {operation.upper()} {element_type}")
        lines.append(f"Element: {element_name}")

        if yaml_path:
            lines.append(f"Path: {yaml_path}")

        lines.append(f"{'-' * 70}")

        if operation == "add" and element_data:
            lines.append("\n[+] New element to be added:")
            lines.append(self._format_yaml_snippet(element_data, prefix="  + "))

        elif operation == "delete":
            lines.append("\n[-] Element to be deleted:")
                                           
            element = self._find_element_in_config(config, element_type, element_name)
            if element:
                lines.append(self._format_yaml_snippet(element, prefix="  - "))
            else:
                lines.append(f"  - {element_name}")

        elif operation == "modify" and element_data:
            lines.append("\n[~] Element will be modified:")
            old_element = self._find_element_in_config(config, element_type, element_name)
            if old_element:
                lines.append("\n  Before:")
                lines.append(self._format_yaml_snippet(old_element, prefix="    - "))
                lines.append("\n  After:")
                lines.append(self._format_yaml_snippet(element_data, prefix="    + "))
            else:
                lines.append(self._format_yaml_snippet(element_data, prefix="  ~ "))

        lines.append(f"{'=' * 70}\n")
        return "\n".join(lines)

    def visualize_bsl_change(
        self,
        procedure_name: str,
        old_code: Optional[str],
        new_code: Optional[str],
        operation: str
    ) -> str:
                   
        lines = []
        lines.append(f"\n{'=' * 70}")
        lines.append(f"BSL Change: {operation.upper()} procedure")
        lines.append(f"Procedure: {procedure_name}")
        lines.append(f"{'-' * 70}")

        if operation == "add" and new_code:
            lines.append("\n[+] New procedure:")
            lines.extend(self._format_bsl_code(new_code, prefix="  + ", start_line=1))

        elif operation == "delete" and old_code:
            lines.append("\n[-] Procedure to be deleted:")
            lines.extend(self._format_bsl_code(old_code, prefix="  - ", start_line=1))

        elif operation == "modify" and old_code and new_code:
            lines.append("\n[~] Procedure modifications:")
            diff_lines = self._compute_line_diff(old_code, new_code)
            lines.extend(self._format_diff_lines(diff_lines))

        lines.append(f"{'=' * 70}\n")
        return "\n".join(lines)

    def visualize_structural_change(
        self,
        element_type: str,
        element_name: str,
        operation: str,
        parent_path: Optional[str],
        insertion_index: Optional[int],
        config: Dict[str, Any]
    ) -> str:
                   
        lines = []
        lines.append(f"\n{'=' * 70}")
        lines.append(f"Structural Change: {operation.upper()} {element_type}")
        lines.append(f"Element: {element_name}")

        if parent_path:
            lines.append(f"Parent: {parent_path}")

        if insertion_index is not None:
            lines.append(f"Position: index {insertion_index}")

        lines.append(f"{'-' * 70}")

                                
        if parent_path:
            parent = self._get_element_by_path(config, parent_path)
            if parent:
                lines.append("\nContext:")
                lines.extend(self._format_hierarchy(parent, element_name, operation, insertion_index))

        lines.append(f"{'=' * 70}\n")
        return "\n".join(lines)

    def create_side_by_side(
        self,
        left_title: str,
        right_title: str,
        left_content: str,
        right_content: str,
        width: int = 35
    ) -> str:
                   
        lines = []
        separator = " | "
        total_width = width * 2 + len(separator)

                
        lines.append("=" * total_width)
        header = f"{left_title:<{width}}{separator}{right_title:<{width}}"
        lines.append(header)
        lines.append("=" * total_width)

                                  
        left_lines = left_content.split('\n')
        right_lines = right_content.split('\n')
        max_lines = max(len(left_lines), len(right_lines))

                            
        left_lines.extend([''] * (max_lines - len(left_lines)))
        right_lines.extend([''] * (max_lines - len(right_lines)))

                          
        for left, right in zip(left_lines, right_lines):
                                  
            left_display = left[:width - 3] + "..." if len(left) > width else left
            right_display = right[:width - 3] + "..." if len(right) > width else right

            line = f"{left_display:<{width}}{separator}{right_display:<{width}}"
            lines.append(line)

        lines.append("=" * total_width)
        return "\n".join(lines)

    def _format_yaml_snippet(self, data: Any, prefix: str = "") -> str:
                                                              
        stream = StringIO()
        self.yaml.dump(data, stream)
        yaml_str = stream.getvalue()

        if prefix:
            lines = yaml_str.split('\n')
            return '\n'.join(prefix + line for line in lines if line)
        return yaml_str

    def _format_bsl_code(
        self,
        code: str,
        prefix: str = "",
        start_line: int = 1
    ) -> List[str]:
                   
        lines = code.split('\n')
        formatted = []

        for i, line in enumerate(lines, start=start_line):
            line_num = f"{i:4d}"
            formatted.append(f"{prefix}{line_num} | {line}")

        return formatted

    def _compute_line_diff(self, old_code: str, new_code: str) -> List[DiffLine]:
                   
        diff_lines = []
        old_lines = old_code.split('\n')
        new_lines = new_code.split('\n')

                                                                    
        for i, line in enumerate(old_lines, start=1):
            diff_lines.append(DiffLine(
                line_number=i,
                content=line,
                status='removed'
            ))

        diff_lines.append(DiffLine(
            line_number=None,
            content="--- Changed to ---",
            status='separator'
        ))

        for i, line in enumerate(new_lines, start=1):
            diff_lines.append(DiffLine(
                line_number=i,
                content=line,
                status='added'
            ))

        return diff_lines

    def _format_diff_lines(self, diff_lines: List[DiffLine]) -> List[str]:
                                                           
        formatted = []

        for diff_line in diff_lines:
            if diff_line.status == 'separator':
                formatted.append(f"\n  {diff_line.content}\n")
            elif diff_line.status == 'removed':
                line_num = f"{diff_line.line_number:4d}" if diff_line.line_number else "    "
                formatted.append(f"  - {line_num} | {diff_line.content}")
            elif diff_line.status == 'added':
                line_num = f"{diff_line.line_number:4d}" if diff_line.line_number else "    "
                formatted.append(f"  + {line_num} | {diff_line.content}")
            elif diff_line.status == 'unchanged':
                line_num = f"{diff_line.line_number:4d}" if diff_line.line_number else "    "
                formatted.append(f"    {line_num} | {diff_line.content}")

        return formatted

    def _find_element_in_config(
        self,
        config: Dict[str, Any],
        element_type: str,
        element_name: str
    ) -> Optional[Dict[str, Any]]:
                   
                                        
        if element_type == "attribute":
            for attr in config.get('attributes', []):
                if attr.get('name') == element_name:
                    return attr

        elif element_type == "tabular_section":
            for ts in config.get('tabular_sections', []):
                if ts.get('name') == element_name:
                    return ts

        elif element_type in ["form_element", "form"]:
                             
            for form in config.get('forms', []):
                if element_type == "form" and form.get('name') == element_name:
                    return form

                                         
                for elem in form.get('elements', []):
                    if elem.get('name') == element_name:
                        return elem

        elif element_type == "command":
            for form in config.get('forms', []):
                for cmd in form.get('commands', []):
                    if cmd.get('name') == element_name:
                        return cmd

        elif element_type == "value_table":
            for form in config.get('forms', []):
                for vt in form.get('value_tables', []):
                    if vt.get('name') == element_name:
                        return vt

        elif element_type == "form_attribute":
            for form in config.get('forms', []):
                for fa in form.get('form_attributes', []):
                    if fa.get('name') == element_name:
                        return fa

        return None

    def _get_element_by_path(
        self,
        config: Dict[str, Any],
        path: str
    ) -> Optional[Any]:
                   
        try:
            current = config
            parts = path.replace('[', '.').replace(']', '').split('.')

            for part in parts:
                if not part:
                    continue

                if part.isdigit():
                    current = current[int(part)]
                else:
                    current = current.get(part)
                    if current is None:
                        return None

            return current
        except (KeyError, IndexError, TypeError, AttributeError):
            return None

    def _format_hierarchy(
        self,
        parent: Dict[str, Any],
        target_name: str,
        operation: str,
        insertion_index: Optional[int]
    ) -> List[str]:
                   
        lines = []

                          
        parent_name = parent.get('name', 'Unknown')
        parent_type = parent.get('type', parent.get('element_type', 'Unknown'))
        lines.append(f"  Parent: {parent_name} ({parent_type})")

                              
        children = parent.get('child_items', parent.get('elements', []))
        if children:
            lines.append(f"  Children ({len(children)}):")

            for idx, child in enumerate(children):
                child_name = child.get('name', 'Unknown')
                marker = ""

                if operation == "add" and insertion_index == idx:
                    lines.append(f"    {idx}. [+] >>> {target_name} will be inserted here <<<")
                    marker = " "

                status = "[-]" if (operation == "delete" and child_name == target_name) else "   "
                lines.append(f"    {marker}{idx}. {status} {child_name}")

                                 
            if operation == "add" and insertion_index == len(children):
                lines.append(f"    {len(children)}. [+] >>> {target_name} will be inserted here <<<")
        else:
            lines.append("  Children: (none)")
            if operation == "add":
                lines.append(f"    0. [+] >>> {target_name} will be first child <<<")

        return lines
