   

import re
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set, Tuple

from .models import generate_uuid, DynamicListColumn

logger = logging.getLogger(__name__)


@dataclass
class StubAttribute:
                                                         
    name: str
    type: str                                                                          
    length: int = 0                              
    digits: int = 15              
    fraction_digits: int = 2              
    uuid: str = field(default_factory=generate_uuid)


class QueryTextParser:
           

                                                                           
    STANDARD_DOCUMENT_ATTRS: Set[str] = {
                 
        'Ссылка', 'Дата', 'Номер', 'Проведен', 'ПометкаУдаления',
                 
        'Ref', 'Date', 'Number', 'Posted', 'DeletionMark',
    }

                                                                          
    STANDARD_CATALOG_ATTRS: Set[str] = {
                 
        'Ссылка', 'Код', 'Наименование', 'ПометкаУдаления',
        'Родитель', 'Владелец', 'Предопределенный', 'ЭтоГруппа',
                 
        'Ref', 'Code', 'Description', 'DeletionMark',
        'Parent', 'Owner', 'Predefined', 'IsFolder',
    }

                                               
    DATE_PATTERNS = [
        r'.*Дата.*', r'.*Date.*', r'.*Период.*', r'.*Period.*',
    ]

    NUMBER_PATTERNS = [
        r'.*Сумма.*', r'.*Количество.*', r'.*Курс.*', r'.*Кратность.*',
        r'.*Amount.*', r'.*Quantity.*', r'.*Rate.*', r'.*Price.*',
        r'.*Цена.*', r'.*Стоимость.*', r'.*Cost.*',
    ]

    BOOLEAN_PATTERNS = [
        r'.*Проведен.*', r'.*Posted.*', r'.*ПометкаУдаления.*',
        r'.*DeletionMark.*', r'.*ЭтоГруппа.*', r'.*IsFolder.*',
    ]

    def __init__(self):
                                                             
        self._date_patterns = [re.compile(p, re.IGNORECASE) for p in self.DATE_PATTERNS]
        self._number_patterns = [re.compile(p, re.IGNORECASE) for p in self.NUMBER_PATTERNS]
        self._boolean_patterns = [re.compile(p, re.IGNORECASE) for p in self.BOOLEAN_PATTERNS]

    def extract_stub_attributes(
        self,
        query_text: str,
        main_table: Optional[str] = None
    ) -> List[StubAttribute]:
                   
        if not query_text:
            return []

                                                 
        metadata_type = self._get_metadata_type(main_table)
        standard_attrs = (
            self.STANDARD_DOCUMENT_ATTRS if metadata_type == "Document"
            else self.STANDARD_CATALOG_ATTRS
        )

                                             
        table_aliases = self._parse_from_clause(query_text)

                                        
        fields = self._parse_select_clause(query_text)

                                                          
        attributes = []
        seen_names: Set[str] = set()

        for field_name, source_table, source_field in fields:
                                      
            if field_name in standard_attrs or source_field in standard_attrs:
                logger.debug(f"Skipping standard attribute: {field_name}")
                continue

                             
            if field_name in seen_names:
                continue
            seen_names.add(field_name)

                        
            attr_type = self._infer_type(field_name, source_field, source_table, table_aliases)

            attr = StubAttribute(
                name=field_name,
                type=attr_type,
                length=0 if attr_type == "string" else 0,
                digits=15 if attr_type == "number" else 0,
                fraction_digits=2 if attr_type == "number" else 0,
            )
            attributes.append(attr)
            logger.debug(f"Extracted attribute: {field_name} -> {attr_type}")

        return attributes

    def extract_from_columns(
        self,
        columns: List[DynamicListColumn],
        main_table: str
    ) -> List[StubAttribute]:
                   
        if not columns or not main_table:
            return []

                                                 
        metadata_type = self._get_metadata_type(main_table)
        standard_attrs = (
            self.STANDARD_DOCUMENT_ATTRS if metadata_type == "Document"
            else self.STANDARD_CATALOG_ATTRS
        )

        attributes = []
        seen_names: Set[str] = set()

        for col in columns:
            field_name = col.field

                                      
            if field_name in standard_attrs:
                logger.debug(f"Skipping standard attribute: {field_name}")
                continue

                             
            if field_name in seen_names:
                continue
            seen_names.add(field_name)

                                             
            attr_type = self._infer_type_from_name(field_name)

            attr = StubAttribute(
                name=field_name,
                type=attr_type,
                length=0 if attr_type == "string" else 0,
                digits=15 if attr_type == "number" else 0,
                fraction_digits=2 if attr_type == "number" else 0,
            )
            attributes.append(attr)
            logger.debug(f"Extracted from column: {field_name} -> {attr_type}")

        return attributes

    def _get_metadata_type(self, main_table: Optional[str]) -> str:
                                                                          
        if not main_table:
            return "Document"           

        main_table_lower = main_table.lower()
        if main_table_lower.startswith("document.") or main_table_lower.startswith("документ."):
            return "Document"
        elif main_table_lower.startswith("catalog.") or main_table_lower.startswith("справочник."):
            return "Catalog"
        else:
            return "Document"           

    def _parse_from_clause(self, query_text: str) -> Dict[str, Tuple[str, str]]:
                   
        aliases: Dict[str, Tuple[str, str]] = {}

                                                     
                                           
        patterns = [
                               
            r'(?:ИЗ|FROM)\s+Документ\.(\w+)\s+(?:КАК|AS)\s+(\w+)',
                                 
            r'(?:ИЗ|FROM)\s+Справочник\.(\w+)\s+(?:КАК|AS)\s+(\w+)',
                               
            r'(?:ИЗ|FROM)\s+Document\.(\w+)\s+(?:КАК|AS)\s+(\w+)',
                              
            r'(?:ИЗ|FROM)\s+Catalog\.(\w+)\s+(?:КАК|AS)\s+(\w+)',
        ]

        metadata_types = ["Document", "Catalog", "Document", "Catalog"]

        for pattern, meta_type in zip(patterns, metadata_types):
            for match in re.finditer(pattern, query_text, re.IGNORECASE):
                name, alias = match.groups()
                aliases[alias] = (meta_type, name)
                logger.debug(f"Found table alias: {alias} -> {meta_type}.{name}")

                                                           
        patterns_no_alias = [
            r'(?:ИЗ|FROM)\s+Документ\.(\w+)(?:\s|$|,)',
            r'(?:ИЗ|FROM)\s+Справочник\.(\w+)(?:\s|$|,)',
            r'(?:ИЗ|FROM)\s+Document\.(\w+)(?:\s|$|,)',
            r'(?:ИЗ|FROM)\s+Catalog\.(\w+)(?:\s|$|,)',
        ]

        for pattern, meta_type in zip(patterns_no_alias, metadata_types):
            for match in re.finditer(pattern, query_text, re.IGNORECASE):
                name = match.group(1)
                                              
                aliases[name] = (meta_type, name)

        return aliases

    def _parse_select_clause(self, query_text: str) -> List[Tuple[str, Optional[str], str]]:
                   
        fields: List[Tuple[str, Optional[str], str]] = []

                                      
                                                                                          
                                                                                     
        select_match = re.search(
            r'(?:ВЫБРАТЬ|SELECT)\s+(.+?)\n\s*(?:ИЗ|FROM)\s+',
            query_text,
            re.IGNORECASE | re.DOTALL
        )

        if not select_match:
                                                                   
            select_match = re.search(
                r'(?:ВЫБРАТЬ|SELECT)\s+(.+?)\s+(?:ИЗ|FROM)\s+\w+\.',
                query_text,
                re.IGNORECASE | re.DOTALL
            )

        if not select_match:
            logger.warning("Could not find SELECT ... FROM in query_text")
            return fields

        select_part = select_match.group(1)

                                          
        literal_pattern = r'"[^"]*"\s+(?:КАК|AS)\s+\w+'
        select_part = re.sub(literal_pattern, '', select_part)

                                                
        pattern_with_alias = r'(\w+)\.(\w+)\s+(?:КАК|AS)\s+(\w+)'
        for match in re.finditer(pattern_with_alias, select_part, re.IGNORECASE):
            table_alias, source_field, field_alias = match.groups()
            fields.append((field_alias, table_alias, source_field))

                                                      
                                                             
        already_matched = set()
        for f in fields:
            already_matched.add(f[2])                

        pattern_no_alias = r'(\w+)\.(\w+)(?=\s*,|\s*$|\s+(?:ИЗ|FROM))'
        for match in re.finditer(pattern_no_alias, select_part, re.IGNORECASE):
            table_alias, source_field = match.groups()
                                                             
            check_str = f"{table_alias}.{source_field}"
            if check_str not in [f"{f[1]}.{f[2]}" for f in fields]:
                fields.append((source_field, table_alias, source_field))

        return fields

    def _infer_type(
        self,
        field_name: str,
        source_field: str,
        source_table: Optional[str],
        table_aliases: Dict[str, Tuple[str, str]]
    ) -> str:
                   
                                                   
        name_type = self._infer_type_from_name(field_name)
        if name_type != "string":
            return name_type

                                      
        source_type = self._infer_type_from_name(source_field)
        if source_type != "string":
            return source_type

                                                                         
                                                                  
                                                       
        ref_patterns = [
            r'.*Организация$', r'.*Organization$',
            r'.*Контрагент$', r'.*Counterparty$', r'.*Partner$',
            r'.*Номенклатура$', r'.*Product$', r'.*Item$',
            r'.*Валюта$', r'.*Currency$',
            r'.*Склад$', r'.*Warehouse$',
            r'.*Сотрудник$', r'.*Employee$',
            r'.*Пользователь$', r'.*User$',
            r'.*Подразделение$', r'.*Department$',
            r'.*Договор$', r'.*Contract$',
        ]

        for pattern in ref_patterns:
            if re.match(pattern, field_name, re.IGNORECASE) or re.match(pattern, source_field, re.IGNORECASE):
                                                                                 
                                                                        
                return "string"

        return "string"

    def _infer_type_from_name(self, field_name: str) -> str:
                                                       
                             
        for pattern in self._date_patterns:
            if pattern.match(field_name):
                return "date"

                               
        for pattern in self._number_patterns:
            if pattern.match(field_name):
                return "number"

                                
        for pattern in self._boolean_patterns:
            if pattern.match(field_name):
                return "boolean"

        return "string"


def extract_stub_attributes_for_dynamic_list(
    query_text: Optional[str],
    columns: Optional[List[DynamicListColumn]],
    main_table: Optional[str],
) -> List[StubAttribute]:
           
    parser = QueryTextParser()

                          
    if query_text:
        attrs = parser.extract_stub_attributes(query_text, main_table)
        if attrs:
            return attrs

                         
    if columns:
        return parser.extract_from_columns(columns, main_table)

    return []
