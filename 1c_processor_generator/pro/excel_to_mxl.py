   
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .excel_reader import (
    ExcelReader, CellData, MergeRange, NamedArea,
    ColumnDef, RowDef, check_openpyxl_available, PARAMETER_PATTERN
)
from .mxl_builder import MXLBuilder, MXLCell, MXLRow


class ExcelToMXLConverter:
           

                             
    BSP_AREA_ALIASES = {
                     
        "header": "Заголовок",
        "заголовок": "Заголовок",
        "шапка": "Заголовок",

                      
        "tableheader": "ШапкаТаблицы",
        "шапкатаблицы": "ШапкаТаблицы",
        "columnheaders": "ШапкаТаблицы",

                      
        "row": "СтрокаТаблицы",
        "строка": "СтрокаТаблицы",
        "строкатаблицы": "СтрокаТаблицы",
        "datarow": "СтрокаТаблицы",

                
        "footer": "Подвал",
        "подвал": "Подвал",
        "итого": "Итого",
        "total": "Итого",
    }

    def __init__(
        self,
        languages: Optional[List[str]] = None,
        default_language: str = "ru"
    ):
                   
        if not check_openpyxl_available():
            raise ImportError(
                "openpyxl is required for Excel → MXL conversion. "
                "Install it with: pip install openpyxl>=3.1.0"
            )

        self.languages = languages or ["ru", "uk"]
        self.default_language = default_language

    def convert(
        self,
        excel_path: str,
        output_path: Optional[str] = None,
        sheet_name: Optional[str] = None
    ) -> str:
                   
        with ExcelReader(excel_path, sheet_name) as reader:
            mxl_content = self._convert_workbook(reader)

        if output_path:
            Path(output_path).write_text(mxl_content, encoding="utf-8-sig")

        return mxl_content

    def convert_to_binary(
        self,
        excel_path: str,
        sheet_name: Optional[str] = None
    ) -> bytes:
                   
        mxl_content = self.convert(excel_path, sheet_name=sheet_name)
                                             
        return mxl_content.encode("utf-8-sig")

    def _convert_workbook(self, reader: ExcelReader) -> str:
                                      
        builder = MXLBuilder(default_language=self.default_language)
        builder.add_language_settings(self.languages)

                             
        cells = reader.get_cells()
        columns = reader.get_columns()
        merged = reader.get_merged_cells()
        named_areas = reader.get_named_areas()
        min_row, min_col, max_row, max_col = reader.get_dimensions()

                     
        for col_def in columns:
            builder.add_column(col_def.index, int(col_def.width))

                               
        self._build_rows(builder, reader, cells, min_row, max_row, min_col, max_col)

                          
        for merge in merged:
                                        
            builder.add_merge(
                row=merge.start_row - 1,
                col=merge.start_col - 1,
                width=merge.width
            )

                         
        for area in named_areas:
            self._add_named_area(builder, area)

        return builder.build()

    def _build_rows(
        self,
        builder: MXLBuilder,
        reader: ExcelReader,
        cells: Dict[Tuple[int, int], CellData],
        min_row: int,
        max_row: int,
        min_col: int,
        max_col: int
    ):
                                        
        rows = reader.get_rows()
        row_heights = {r.index: r.height for r in rows}

        for row_idx in range(min_row, max_row + 1):
            row_cells = []

            for col_idx in range(min_col, max_col + 1):
                cell_data = cells.get((row_idx, col_idx))
                if cell_data:
                    mxl_cell = self._create_cell(builder, cell_data)
                    row_cells.append(mxl_cell)

                                            
            height = row_heights.get(row_idx - 1)
            height_int = int(height) if height and height != 15.0 else None

            builder.add_row(
                index=row_idx - 1,                   
                cells=row_cells,
                height=height_int
            )

    def _create_cell(self, builder: MXLBuilder, cell_data: CellData) -> MXLCell:
                                                   
                      
        text = cell_data.value
        text_localized = None
        parameter = None
        has_parameter = False

                              
        if text and cell_data.parameters:
            has_parameter = True

                                                                       
            if len(cell_data.parameters) == 1:
                match = PARAMETER_PATTERN.fullmatch(text.strip())
                if match:
                                                                     
                    parameter = cell_data.parameters[0]
                    text = None

                                               
        if text:
            text_localized = {lang: text for lang in self.languages}

                         
        borders = None
        if any([cell_data.border_left, cell_data.border_right,
                cell_data.border_top, cell_data.border_bottom]):
            borders = {
                "left": cell_data.border_left,
                "right": cell_data.border_right,
                "top": cell_data.border_top,
                "bottom": cell_data.border_bottom,
            }

        return builder.create_cell(
            col_index=cell_data.col - 1,                   
            text_localized=text_localized,
            parameter=parameter,
            font_bold=cell_data.font_bold,
            font_size=cell_data.font_size,
            horizontal_alignment=cell_data.horizontal_alignment,
            vertical_alignment=cell_data.vertical_alignment,
            has_parameter=has_parameter,
            wrap_text=cell_data.wrap_text,
            borders=borders
        )

    def _add_named_area(self, builder: MXLBuilder, area: NamedArea):
                                                    
                                
        name = area.name
        name_lower = name.lower().replace("_", "").replace(" ", "")

                               
        if name_lower in self.BSP_AREA_ALIASES:
            name = self.BSP_AREA_ALIASES[name_lower]

                                                
        begin_row = area.start_row - 1 if area.start_row > 0 else -1
        end_row = area.end_row - 1 if area.end_row > 0 else -1
        begin_col = area.start_col - 1 if area.start_col > 0 else -1
        end_col = area.end_col - 1 if area.end_col > 0 else -1

        builder.add_named_area(
            name=name,
            area_type=area.area_type,
            begin_row=begin_row,
            end_row=end_row,
            begin_col=begin_col,
            end_col=end_col
        )


def convert_excel_to_mxl(
    excel_path: str,
    output_path: Optional[str] = None,
    languages: Optional[List[str]] = None
) -> str:
           
    converter = ExcelToMXLConverter(languages=languages)
    return converter.convert(excel_path, output_path)
