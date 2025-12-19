   

import re
import logging
from dataclasses import dataclass, field
from typing import Set, Dict, List, Optional
from .models import Processor, DynamicListAttribute
from .query_text_parser import StubAttribute, extract_stub_attributes_for_dynamic_list

logger = logging.getLogger(__name__)


@dataclass
class StubMetadata:
                                                                         
    name: str
    metadata_type: str                           
    attributes: List[StubAttribute] = field(default_factory=list)

    def add_attribute(self, attr: StubAttribute) -> None:
                                                             
        existing_names = {a.name for a in self.attributes}
        if attr.name not in existing_names:
            self.attributes.append(attr)


@dataclass
class MetadataRequirements:
                                                             
    catalogs: Set[str] = field(default_factory=set)
    documents: Set[str] = field(default_factory=set)
    common_pictures: Set[str] = field(default_factory=set)
    common_modules: Set[str] = field(default_factory=set)                             
                                                                                  
    stub_metadata: Dict[str, StubMetadata] = field(default_factory=dict)

    def is_empty(self) -> bool:
                                                           
        return (len(self.catalogs) == 0 and len(self.documents) == 0 and
                len(self.common_pictures) == 0 and len(self.common_modules) == 0)

    def has_metadata(self) -> bool:
                                                                                                        
        return not self.is_empty()

    def get_stub_attributes(self, metadata_type: str, name: str) -> List[StubAttribute]:
                                                 
        key = f"{metadata_type}.{name}"
        if key in self.stub_metadata:
            return self.stub_metadata[key].attributes
        return []

    def add_stub_attribute(
        self,
        metadata_type: str,
        metadata_name: str,
        attribute: StubAttribute
    ) -> None:
                                             
        key = f"{metadata_type}.{metadata_name}"
        if key not in self.stub_metadata:
            self.stub_metadata[key] = StubMetadata(
                name=metadata_name,
                metadata_type=metadata_type,
            )
        self.stub_metadata[key].add_attribute(attribute)

    def __repr__(self) -> str:
        stub_info = f", stub_metadata={len(self.stub_metadata)} stubs" if self.stub_metadata else ""
        return f"MetadataRequirements(catalogs={sorted(self.catalogs)}, documents={sorted(self.documents)}, common_pictures={sorted(self.common_pictures)}{stub_info})"


class MetadataAnalyzer:
                                                                             

                                     
    CATALOG_REF_PATTERN = re.compile(r'CatalogRef\.(\w+)')
    DOCUMENT_REF_PATTERN = re.compile(r'DocumentRef\.(\w+)')
    CATALOG_MAIN_TABLE_PATTERN = re.compile(r'Catalog\.(\w+)')
    DOCUMENT_MAIN_TABLE_PATTERN = re.compile(r'Document\.(\w+)')
    COMMON_PICTURE_PATTERN = re.compile(r'CommonPicture\.(\w+)')

                                                               
    COMMON_MODULE_PATTERN = re.compile(r'\b([А-Яа-яЁё][А-Яа-яЁёA-Za-z0-9_]+)\.(Нужно|Вывести|Задать|Сведения|Выполнить|Получить|Установить)\w*\(', re.UNICODE)

    @staticmethod
    def analyze_processor(processor: Processor) -> MetadataRequirements:
                   
        requirements = MetadataRequirements()

                                       
        for attribute in processor.attributes:
            MetadataAnalyzer._extract_from_type(attribute.type, requirements)

                                            
        for tabular_section in processor.tabular_sections:
            for column in tabular_section.columns:
                MetadataAnalyzer._extract_from_type(column.type, requirements)

                        
        for form in processor.forms:
                                      
            for value_table in form.value_table_attributes:
                for column in value_table.columns:
                    MetadataAnalyzer._extract_from_type(column.type, requirements)

                                                                      
            for dynamic_list in form.dynamic_list_attributes:
                if dynamic_list.main_table:
                    MetadataAnalyzer._extract_from_main_table(dynamic_list.main_table, requirements)

                                                             
                MetadataAnalyzer._extract_stub_attributes_from_dynamic_list(
                    dynamic_list, requirements
                )

                                         
            for cmd in form.commands:
                if cmd.picture:
                    MetadataAnalyzer._extract_from_picture(cmd.picture, requirements)

                                                               
            MetadataAnalyzer._extract_pictures_from_elements(form.elements, requirements)

                                                                               
        if processor.bsp_config:
            MetadataAnalyzer._add_bsp_required_modules(processor.bsp_config, requirements)

        return requirements

    @staticmethod
    def _extract_from_type(type_string: str, requirements: MetadataRequirements) -> None:
                   
        if not type_string:
            return

                                    
        for match in MetadataAnalyzer.CATALOG_REF_PATTERN.finditer(type_string):
            catalog_name = match.group(1)
            requirements.catalogs.add(catalog_name)

                                     
        for match in MetadataAnalyzer.DOCUMENT_REF_PATTERN.finditer(type_string):
            document_name = match.group(1)
            requirements.documents.add(document_name)

    @staticmethod
    def _extract_from_main_table(main_table: str, requirements: MetadataRequirements) -> None:
                   
        if not main_table:
            return

                             
        catalog_match = MetadataAnalyzer.CATALOG_MAIN_TABLE_PATTERN.search(main_table)
        if catalog_match:
            catalog_name = catalog_match.group(1)
            requirements.catalogs.add(catalog_name)

                              
        document_match = MetadataAnalyzer.DOCUMENT_MAIN_TABLE_PATTERN.search(main_table)
        if document_match:
            document_name = document_match.group(1)
            requirements.documents.add(document_name)

    @staticmethod
    def _extract_from_picture(picture_string: str, requirements: MetadataRequirements) -> None:
                   
        if not picture_string:
            return

                                   
        match = MetadataAnalyzer.COMMON_PICTURE_PATTERN.search(picture_string)
        if match:
            picture_name = match.group(1)
            requirements.common_pictures.add(picture_name)

    @staticmethod
    def _extract_pictures_from_elements(elements: list, requirements: MetadataRequirements) -> None:
                   
        if not elements:
            return

        for elem in elements:
                                                         
            for prop_name in ('picture', 'choice_button_picture'):
                value = elem.properties.get(prop_name, '') if elem.properties else ''
                if value:
                    MetadataAnalyzer._extract_from_picture(value, requirements)

                                                       
            if elem.child_items:
                MetadataAnalyzer._extract_pictures_from_elements(elem.child_items, requirements)

    @staticmethod
    def _add_bsp_required_modules(bsp_config, requirements: MetadataRequirements) -> None:
                   
                                              
        if bsp_config.type == "PrintForm":
            requirements.common_modules.add("УправлениеПечатью")
            logger.info("Added BSP module stub: УправлениеПечатью")

                                                    
                                                                        
                                              

    @staticmethod
    def _extract_stub_attributes_from_dynamic_list(
        dynamic_list: DynamicListAttribute,
        requirements: MetadataRequirements
    ) -> None:
                   
                                                
        if not dynamic_list.main_table:
            return

                                              
        skip_validation = getattr(dynamic_list, 'skip_stub_validation', False)
        if skip_validation:
            logger.debug(f"Skipping stub attribute extraction for {dynamic_list.name} (skip_stub_validation=True)")
            return

                                              
        stub_attrs = extract_stub_attributes_for_dynamic_list(
            query_text=dynamic_list.query_text,
            columns=dynamic_list.columns if hasattr(dynamic_list, 'columns') else None,
            main_table=dynamic_list.main_table
        )

        if not stub_attrs:
            return

                                                 
        main_table = dynamic_list.main_table
        if main_table.lower().startswith("document.") or main_table.lower().startswith("документ."):
            metadata_type = "Document"
            metadata_name = main_table.split(".", 1)[1]
        elif main_table.lower().startswith("catalog.") or main_table.lower().startswith("справочник."):
            metadata_type = "Catalog"
            metadata_name = main_table.split(".", 1)[1]
        else:
            logger.warning(f"Unknown main_table format: {main_table}")
            return

                                        
        for attr in stub_attrs:
            requirements.add_stub_attribute(metadata_type, metadata_name, attr)

        logger.info(
            f"Extracted {len(stub_attrs)} stub attributes for {metadata_type}.{metadata_name} "
            f"from DynamicList '{dynamic_list.name}'"
        )

    @staticmethod
    def print_analysis(processor: Processor, requirements: MetadataRequirements) -> None:
                   
        print(f"\n=== Metadata Analysis for '{processor.name}' ===")
        print(f"\nCatalogs found ({len(requirements.catalogs)}):")
        for catalog in sorted(requirements.catalogs):
            print(f"  - {catalog}")

        print(f"\nDocuments found ({len(requirements.documents)}):")
        for document in sorted(requirements.documents):
            print(f"  - {document}")

        print(f"\nCommonPictures found ({len(requirements.common_pictures)}):")
        for picture in sorted(requirements.common_pictures):
            print(f"  - {picture}")

        if requirements.is_empty():
            print("\n⚠️ No CatalogRef/DocumentRef/CommonPicture found - Configuration generation not needed")
        else:
            total = len(requirements.catalogs) + len(requirements.documents) + len(requirements.common_pictures)
            print(f"\n✅ Total metadata objects: {total}")
            print(f"   UUID count needed: {MetadataAnalyzer.calculate_uuid_count(requirements)}")

    @staticmethod
    def calculate_uuid_count(requirements: MetadataRequirements) -> int:
                   
        base_uuids = 2                            
        catalog_uuids = len(requirements.catalogs) * 11
        document_uuids = len(requirements.documents) * 9
        picture_uuids = len(requirements.common_pictures) * 1

                                       
        stub_attr_uuids = sum(
            len(stub.attributes)
            for stub in requirements.stub_metadata.values()
        )

        return base_uuids + catalog_uuids + document_uuids + picture_uuids + stub_attr_uuids
