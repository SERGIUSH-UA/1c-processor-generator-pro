   

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


class BSLChangeType(Enum):
                                       
    PROCEDURE_ADDED = "procedure_added"
    PROCEDURE_DELETED = "procedure_deleted"
    PROCEDURE_MODIFIED = "procedure_modified"
    REGION_ADDED = "region_added"
    REGION_DELETED = "region_deleted"


@dataclass
class BSLProcedure:
                                                 
    name: str
    is_function: bool                                         
    signature: str                                                    
    body: str                                              
    full_text: str                             
    line_number: int                        
    directives: List[str]                                          

    def normalize_body(self) -> str:
                   
                                     
        body = re.sub(r'//.*?$', '', self.body, flags=re.MULTILINE)

                                 
        body = re.sub(r'\s+', ' ', body)

                                            
        return body.strip()


@dataclass
class BSLRegion:
                                                               
    name: str
    content: str
    line_number: int


@dataclass
class BSLChange:
                                                 
    change_type: BSLChangeType
    procedure_name: Optional[str] = None
    old_code: Optional[str] = None
    new_code: Optional[str] = None
    region_name: Optional[str] = None

    def __str__(self) -> str:
                                                   
        if self.change_type == BSLChangeType.PROCEDURE_ADDED:
            return f"Procedure added: {self.procedure_name}"
        elif self.change_type == BSLChangeType.PROCEDURE_DELETED:
            return f"Procedure deleted: {self.procedure_name}"
        elif self.change_type == BSLChangeType.PROCEDURE_MODIFIED:
            return f"Procedure modified: {self.procedure_name}"
        elif self.change_type == BSLChangeType.REGION_ADDED:
            return f"Region added: {self.region_name}"
        elif self.change_type == BSLChangeType.REGION_DELETED:
            return f"Region deleted: {self.region_name}"
        return str(self.change_type.value)


class BSLDiffer:
           

                                    
    PROCEDURE_PATTERN = re.compile(
        r'(?P<directives>(?:&[А-ЯЁа-яёA-Za-z]+\s*)*)'
        r'(?P<type>Процедура|Функция)\s+'
        r'(?P<name>[А-ЯЁа-яёA-Za-z0-9_]+)'
        r'\s*\((?P<params>[^)]*)\)'
        r'(?P<export>\s+Экспорт)?'
        r'(?P<body>.*?)'
        r'Конец(?:Процедуры|Функции)',
        re.DOTALL | re.MULTILINE | re.IGNORECASE
    )

    REGION_PATTERN = re.compile(
        r'#Область\s+(?P<name>[^\r\n]+)'
        r'(?P<content>.*?)'
        r'#КонецОбласті',
        re.DOTALL | re.MULTILINE | re.IGNORECASE
    )

    def __init__(self, original_bsl: str, modified_bsl: str):
                   
        self.original_bsl = original_bsl
        self.modified_bsl = modified_bsl
        self.changes: List[BSLChange] = []

                          
        self.original_procedures = self._parse_procedures(original_bsl)
        self.modified_procedures = self._parse_procedures(modified_bsl)

                       
        self.original_regions = self._parse_regions(original_bsl)
        self.modified_regions = self._parse_regions(modified_bsl)

    def detect_changes(self) -> List[BSLChange]:
                   
        logger.info("Detecting changes in BSL code...")
        self.changes = []

        self._compare_procedures()
        self._compare_regions()

        logger.info(f"Detected {len(self.changes)} BSL changes")
        return self.changes

    def _compare_procedures(self):
                                                                    
        original_names = set(self.original_procedures.keys())
        modified_names = set(self.modified_procedures.keys())

                               
        added = modified_names - original_names
        for name in added:
            proc = self.modified_procedures[name]
            self.changes.append(BSLChange(
                change_type=BSLChangeType.PROCEDURE_ADDED,
                procedure_name=name,
                new_code=proc.full_text
            ))

                                 
        deleted = original_names - modified_names
        for name in deleted:
            proc = self.original_procedures[name]
            self.changes.append(BSLChange(
                change_type=BSLChangeType.PROCEDURE_DELETED,
                procedure_name=name,
                old_code=proc.full_text
            ))

                                  
        common = original_names & modified_names
        for name in common:
            orig_proc = self.original_procedures[name]
            mod_proc = self.modified_procedures[name]

                                       
            if orig_proc.normalize_body() != mod_proc.normalize_body():
                self.changes.append(BSLChange(
                    change_type=BSLChangeType.PROCEDURE_MODIFIED,
                    procedure_name=name,
                    old_code=orig_proc.full_text,
                    new_code=mod_proc.full_text
                ))

    def _compare_regions(self):
                                                                 
        original_names = set(self.original_regions.keys())
        modified_names = set(self.modified_regions.keys())

                            
        added = modified_names - original_names
        for name in added:
            self.changes.append(BSLChange(
                change_type=BSLChangeType.REGION_ADDED,
                region_name=name,
                new_code=self.modified_regions[name].content
            ))

                              
        deleted = original_names - modified_names
        for name in deleted:
            self.changes.append(BSLChange(
                change_type=BSLChangeType.REGION_DELETED,
                region_name=name,
                old_code=self.original_regions[name].content
            ))

    def _parse_procedures(self, code: str) -> Dict[str, BSLProcedure]:
                   
        procedures = {}

        for match in self.PROCEDURE_PATTERN.finditer(code):
            directives_text = match.group('directives') or ''
            proc_type = match.group('type')
            name = match.group('name')
            params = match.group('params') or ''
            export = match.group('export') or ''
            body = match.group('body')

                              
            directives = re.findall(r'&([А-ЯЁа-яёA-Za-z]+)', directives_text)

                             
            signature = f"{directives_text}{proc_type} {name}({params}){export}"

                                     
            full_text = match.group(0)

                             
            line_number = code[:match.start()].count('\n') + 1

            is_function = proc_type.lower() == 'функция'

            procedures[name] = BSLProcedure(
                name=name,
                is_function=is_function,
                signature=signature,
                body=body,
                full_text=full_text,
                line_number=line_number,
                directives=directives
            )

        return procedures

    def _parse_regions(self, code: str) -> Dict[str, BSLRegion]:
                   
        regions = {}

        for match in self.REGION_PATTERN.finditer(code):
            name = match.group('name').strip()
            content = match.group('content')
            line_number = code[:match.start()].count('\n') + 1

            regions[name] = BSLRegion(
                name=name,
                content=content,
                line_number=line_number
            )

        return regions

    def get_added_procedures(self) -> List[BSLChange]:
                                       
        return [c for c in self.changes
                if c.change_type == BSLChangeType.PROCEDURE_ADDED]

    def get_deleted_procedures(self) -> List[BSLChange]:
                                         
        return [c for c in self.changes
                if c.change_type == BSLChangeType.PROCEDURE_DELETED]

    def get_modified_procedures(self) -> List[BSLChange]:
                                          
        return [c for c in self.changes
                if c.change_type == BSLChangeType.PROCEDURE_MODIFIED]

    def print_summary(self):
                                                                   
        if not self.changes:
            print("No BSL changes detected.")
            return

        print(f"\n{'='*70}")
        print(f"Detected {len(self.changes)} BSL changes:")
        print(f"{'='*70}\n")

                              
        added_procs = self.get_added_procedures()
        deleted_procs = self.get_deleted_procedures()
        modified_procs = self.get_modified_procedures()

        if added_procs:
            print(f"\nADDED PROCEDURES ({len(added_procs)}):")
            print("-" * 70)
            for change in added_procs:
                print(f"  • {change.procedure_name}")

        if deleted_procs:
            print(f"\nDELETED PROCEDURES ({len(deleted_procs)}):")
            print("-" * 70)
            for change in deleted_procs:
                print(f"  • {change.procedure_name}")

        if modified_procs:
            print(f"\nMODIFIED PROCEDURES ({len(modified_procs)}):")
            print("-" * 70)
            for change in modified_procs:
                print(f"  • {change.procedure_name}")

        print(f"\n{'='*70}\n")

    def get_procedure_diff(self, procedure_name: str) -> Optional[tuple]:
                   
        for change in self.changes:
            if (change.change_type == BSLChangeType.PROCEDURE_MODIFIED and
                change.procedure_name == procedure_name):
                return (change.old_code, change.new_code)
        return None


class BSLCodeExtractor:
           

    @staticmethod
    def extract_from_xml(xml_path: str) -> str:
                   
        from lxml import etree

        try:
            tree = etree.parse(xml_path)

                                                                        
                                       
                                                               

            module_paths = [
                ".//FormModule",
                ".//ObjectModule",
                ".//Module"
            ]

            for path in module_paths:
                module = tree.find(path)
                if module is not None and module.text:
                    return module.text.strip()

            logger.warning(f"No BSL module found in {xml_path}")
            return ""

        except Exception as e:
            logger.error(f"Failed to extract BSL from {xml_path}: {e}")
            return ""

    @staticmethod
    def extract_from_bsl_file(bsl_path: str) -> str:
                   
        try:
            with open(bsl_path, 'r', encoding='utf-8-sig') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read BSL file {bsl_path}: {e}")
            return ""
