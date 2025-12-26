   

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from lxml import etree

logger = logging.getLogger(__name__)


@dataclass
class ElementNode:
           
    name: str
    element_type: str
    element: etree._Element                        
    parent: Optional['ElementNode'] = None
    children: List['ElementNode'] = field(default_factory=list)
    depth: int = 0
    index: int = 0                                      
    path: Optional[str] = None                                                        

    def is_leaf(self) -> bool:
                                                         
        return len(self.children) == 0

    def is_root(self) -> bool:
                                                       
        return self.parent is None

    def get_siblings(self) -> List['ElementNode']:
                                                      
        if self.parent:
            return self.parent.children
        return []

    def get_ancestors(self) -> List['ElementNode']:
                                                             
        ancestors = []
        current = self.parent
        while current:
            ancestors.insert(0, current)
            current = current.parent
        return ancestors

    def find_child(self, name: str) -> Optional['ElementNode']:
                                        
        for child in self.children:
            if child.name == name:
                return child
        return None


class HierarchicalExtractor:
           

                                            
    NAMESPACES = {
        "v8": "http://v8.1c.ru/8.1/data/core",
        "ns": "http://v8.1c.ru/8.3/MDClasses",
        "form": "http://v8.1c.ru/8.3/xcf/logform",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance"
    }

    def __init__(self):
                                               
        pass

    def extract_form_elements_tree(
        self,
        form_root: etree._Element,
        form_index: int = 0
    ) -> List[ElementNode]:
                   
        root_elements = []

                                                             
                                                                             
        containers = form_root.xpath(".//*[local-name()='ChildItems']")
        child_items_container = containers[0] if containers else None
        if child_items_container is None:
            logger.debug("No ChildItems container found in form")
            return root_elements

                                                                                  
                                                                                       
        for index, item_elem in enumerate(child_items_container):
            node = self._extract_element_recursive(
                item_elem,
                parent_node=None,
                depth=0,
                index=index,
                form_index=form_index,
                parent_path=f"forms[{form_index}].elements"
            )
            if node:
                root_elements.append(node)

        return root_elements

    def _extract_element_recursive(
        self,
        element: etree._Element,
        parent_node: Optional[ElementNode],
        depth: int,
        index: int,
        form_index: int,
        parent_path: str
    ) -> Optional[ElementNode]:
                   
                                                                       
                                                                
        name = element.get("name")
        if not name:
            logger.debug(f"Element at depth {depth} has no 'name' attribute, skipping")
            return None

                          
        elem_type = self._get_element_type(element)
        if not elem_type:
            logger.debug(f"Element {name} has no type, skipping")
            return None

                    
        path = f"{parent_path}[{index}]"

                     
        node = ElementNode(
            name=name,
            element_type=elem_type,
            element=element,
            parent=parent_node,
            depth=depth,
            index=index,
            path=path
        )

                                                                
        if self._supports_children(elem_type):
                                                                                           
            containers = element.xpath(".//*[local-name()='ChildItems']")
            children_container = containers[0] if containers else None
            if children_container is not None:
                child_index = 0
                                                                                        
                for child_elem in children_container:
                    child_node = self._extract_element_recursive(
                        child_elem,
                        parent_node=node,
                        depth=depth + 1,
                        index=child_index,
                        form_index=form_index,
                        parent_path=f"{path}.child_items"
                    )
                    if child_node:
                        node.children.append(child_node)
                        child_index += 1

        return node

    def _get_element_type(self, element: etree._Element) -> Optional[str]:
                   
                                                                  
                                                                
        tag = element.tag
        if isinstance(tag, str):
                                                                        
            return tag.split('}')[-1] if '}' in tag else tag
        return None

    def _supports_children(self, element_type: str) -> bool:
                   
                                                 
        container_types = {
            'UsualGroup',
            'CommandBarGroup',
            'Page',
            'Pages',
            'ColumnGroup',
            'FormGroup'
        }
        return element_type in container_types

    def find_element_path(
        self,
        root_elements: List[ElementNode],
        element_name: str
    ) -> Optional[str]:
                   
        for root in root_elements:
            path = self._find_element_path_recursive(root, element_name)
            if path:
                return path
        return None

    def _find_element_path_recursive(
        self,
        node: ElementNode,
        element_name: str
    ) -> Optional[str]:
                   
                            
        if node.name == element_name:
            return node.path

                         
        for child in node.children:
            path = self._find_element_path_recursive(child, element_name)
            if path:
                return path

        return None

    def get_insertion_point(
        self,
        root_elements: List[ElementNode],
        parent_name: Optional[str],
        position: str = 'end'
    ) -> Tuple[Optional[str], int]:
                   
        if parent_name is None:
                                 
            parent_path = root_elements[0].path.rsplit('[', 1)[0] if root_elements else "forms[0].elements"

            if position == 'start':
                return (parent_path, 0)
            elif position == 'end':
                return (parent_path, len(root_elements))
            elif position.isdigit():
                index = int(position)
                return (parent_path, min(index, len(root_elements)))
            else:
                return (parent_path, len(root_elements))

                          
        parent_node = self._find_node_by_name(root_elements, parent_name)
        if not parent_node:
            logger.warning(f"Parent element '{parent_name}' not found")
            return (None, 0)

                                           
        if not self._supports_children(parent_node.element_type):
            logger.warning(f"Parent element '{parent_name}' of type '{parent_node.element_type}' cannot have children")
            return (None, 0)

                                            
        parent_path = f"{parent_node.path}.child_items"

                         
        if position == 'start':
            return (parent_path, 0)
        elif position == 'end':
            return (parent_path, len(parent_node.children))
        elif position.isdigit():
            index = int(position)
            return (parent_path, min(index, len(parent_node.children)))
        else:
            return (parent_path, len(parent_node.children))

    def _find_node_by_name(
        self,
        root_elements: List[ElementNode],
        name: str
    ) -> Optional[ElementNode]:
                   
        for root in root_elements:
            node = self._find_node_by_name_recursive(root, name)
            if node:
                return node
        return None

    def _find_node_by_name_recursive(
        self,
        node: ElementNode,
        name: str
    ) -> Optional[ElementNode]:
                   
        if node.name == name:
            return node

        for child in node.children:
            found = self._find_node_by_name_recursive(child, name)
            if found:
                return found

        return None

    def flatten_tree(
        self,
        root_elements: List[ElementNode]
    ) -> Dict[str, ElementNode]:
                   
        flat_dict = {}

        for root in root_elements:
            self._flatten_recursive(root, flat_dict)

        return flat_dict

    def _flatten_recursive(
        self,
        node: ElementNode,
        flat_dict: Dict[str, ElementNode]
    ):
                   
        flat_dict[node.name] = node

        for child in node.children:
            self._flatten_recursive(child, flat_dict)

    def compare_trees(
        self,
        original_roots: List[ElementNode],
        modified_roots: List[ElementNode]
    ) -> Dict[str, Any]:
                   
        changes = {
            'added': [],
            'deleted': [],
            'moved': [],
            'modified': []
        }

                            
        original_flat = self.flatten_tree(original_roots)
        modified_flat = self.flatten_tree(modified_roots)

                                
        original_names = set(original_flat.keys())
        modified_names = set(modified_flat.keys())

        added_names = modified_names - original_names
        deleted_names = original_names - modified_names
        common_names = original_names & modified_names

                       
        for name in added_names:
            node = modified_flat[name]
            changes['added'].append({
                'name': name,
                'type': node.element_type,
                'path': node.path,
                'depth': node.depth,
                'parent': node.parent.name if node.parent else None
            })

                         
        for name in deleted_names:
            node = original_flat[name]
            changes['deleted'].append({
                'name': name,
                'type': node.element_type,
                'path': node.path,
                'depth': node.depth,
                'parent': node.parent.name if node.parent else None
            })

                                                                    
        for name in common_names:
            orig_node = original_flat[name]
            mod_node = modified_flat[name]

                                                        
            orig_parent = orig_node.parent.name if orig_node.parent else None
            mod_parent = mod_node.parent.name if mod_node.parent else None

            if orig_parent != mod_parent or orig_node.index != mod_node.index:
                changes['moved'].append({
                    'name': name,
                    'type': mod_node.element_type,
                    'from_path': orig_node.path,
                    'to_path': mod_node.path,
                    'from_parent': orig_parent,
                    'to_parent': mod_parent,
                    'from_index': orig_node.index,
                    'to_index': mod_node.index
                })

                                                                         
                                                                  
            if orig_node.element_type != mod_node.element_type:
                changes['modified'].append({
                    'name': name,
                    'path': mod_node.path,
                    'changes': {
                        'type': {
                            'old': orig_node.element_type,
                            'new': mod_node.element_type
                        }
                    }
                })

        return changes

    def print_tree(
        self,
        root_elements: List[ElementNode],
        indent: str = "",
        show_path: bool = False
    ) -> str:
                   
        lines = []

        for i, root in enumerate(root_elements):
            lines.extend(self._print_node(root, indent, i == len(root_elements) - 1, show_path))

        return '\n'.join(lines)

    def _print_node(
        self,
        node: ElementNode,
        indent: str,
        is_last: bool,
        show_path: bool
    ) -> List[str]:
                   
        lines = []

                             
        marker = "└─" if is_last else "├─"
        path_str = f" [{node.path}]" if show_path else ""
        lines.append(f"{indent}{marker} {node.name} ({node.element_type}){path_str}")

                         
        child_indent = indent + ("   " if is_last else "│  ")
        for i, child in enumerate(node.children):
            child_is_last = (i == len(node.children) - 1)
            lines.extend(self._print_node(child, child_indent, child_is_last, show_path))

        return lines
