   

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict


@dataclass
class PropSpec:
                                                

    key: str             
    target: Optional[str] = None                                         
    multilang: bool = False                                 
    default: Any = None                                 


@dataclass
class ElementSchema:
                                                 

    element_type: str
    props: List[PropSpec] = field(default_factory=list)
    has_attribute: bool = False                                
    has_command: bool = False          
    has_tabular_section: bool = False         
    has_children: bool = False                                        
    children_key: str = "elements"                               


                                                                               
                                
                                                                               

MULTILANG_TITLE = [
    PropSpec("title", multilang=True),
    PropSpec("tooltip", multilang=True),
]

ALIGNMENT_PROPS = [
    PropSpec("horizontal_align"),
    PropSpec("vertical_align"),
]

SIZE_PROPS = [
    PropSpec("width"),
    PropSpec("height"),
    PropSpec("horizontal_stretch"),
    PropSpec("vertical_stretch"),
]


                                                                               
                                
                                                                               

SCHEMAS: Dict[str, ElementSchema] = {
                                                                               
                                     
                                                                               
    "InputField": ElementSchema(
        element_type="InputField",
        has_attribute=True,
        props=[
            *MULTILANG_TITLE,
            PropSpec("tooltip", multilang=True),
            PropSpec("input_hint", multilang=True),
            *SIZE_PROPS,
            *ALIGNMENT_PROPS,
            PropSpec("read_only"),
            PropSpec("multi_line", target="multiline"),
            PropSpec("multiline"),
            PropSpec("password_mode"),
            PropSpec("text_edit"),
            PropSpec("auto_max_width"),
            PropSpec("auto_max_height"),
            PropSpec("title_location"),
            PropSpec("choice_list"),
            PropSpec("choice_mode"),
            PropSpec("choice_folders_and_items"),
            PropSpec("quick_choice"),
            PropSpec("choice_history_on_input"),
                                                            
            PropSpec("title_text_color"),
            PropSpec("title_font"),
            PropSpec("text_color"),
            PropSpec("back_color"),
            PropSpec("border_color"),
            PropSpec("font"),
            PropSpec("choice_button_picture"),
        ],
    ),
                                                                               
                                                       
                                                                               
    "LabelField": ElementSchema(
        element_type="LabelField",
        has_attribute=True,
        props=[
            *MULTILANG_TITLE,
            PropSpec("data_path"),
            PropSpec("hyperlink"),
            *ALIGNMENT_PROPS,
        ],
    ),
                                                                               
                                           
                                                                               
    "LabelDecoration": ElementSchema(
        element_type="LabelDecoration",
        props=[
            *MULTILANG_TITLE,
            PropSpec("formatted"),                                          
            PropSpec("hyperlink"),
            PropSpec("font"),
            *ALIGNMENT_PROPS,
        ],
    ),
                                                                               
                                                
                                                                               
    "PictureDecoration": ElementSchema(
        element_type="PictureDecoration",
        props=[
            PropSpec("svg_source"),
            PropSpec("picture"),
            PropSpec("svg_width"),
            PropSpec("svg_height"),
            PropSpec("form_width"),
            PropSpec("form_height"),
            PropSpec("width"),
            PropSpec("height"),
            PropSpec("alignment"),
            PropSpec("hyperlink"),
            PropSpec("picture_size", default="Proportionally"),
            PropSpec("zoomable"),
        ],
    ),
                                                                               
                                                             
                                                                               
    "PictureField": ElementSchema(
        element_type="PictureField",
        has_attribute=True,
        props=[
            PropSpec("title_location"),
            PropSpec("picture_size"),
            PropSpec("zoomable"),
            PropSpec("width"),
            PropSpec("height"),
        ],
    ),
                                                                               
                                                                
                                                                               
    "Table": ElementSchema(
        element_type="Table",
        has_tabular_section=True,
        has_children=True,
        props=[
            PropSpec("read_only"),
            PropSpec("height"),
            PropSpec("horizontal_stretch"),
            PropSpec("is_value_table"),
            PropSpec("is_dynamic_list"),
                                                 
            PropSpec("representation"),                            
            PropSpec("initial_tree_view"),                                                                
            PropSpec("show_root"),                         
            PropSpec("allow_root_choice"),                 
            PropSpec("choice_folders_and_items"),                                            
        ],
    ),
                                                                               
                                             
                                                                               
    "Button": ElementSchema(
        element_type="Button",
        has_command=True,
        props=[
            PropSpec("width"),
            PropSpec("representation"),
            *ALIGNMENT_PROPS,
        ],
    ),
                                                                               
                                  
                                                                               
    "RadioButtonField": ElementSchema(
        element_type="RadioButtonField",
        has_attribute=True,
        props=[
            PropSpec("radio_button_type"),
            PropSpec("choice_list"),
            PropSpec("title_location"),
        ],
    ),
                                                                               
                               
                                                                               
    "CheckBoxField": ElementSchema(
        element_type="CheckBoxField",
        has_attribute=True,
        props=[
            PropSpec("width"),
            PropSpec("title_location"),
        ],
    ),
                                                                               
                                                          
                                                                               
    "SpreadSheetDocumentField": ElementSchema(
        element_type="SpreadSheetDocumentField",
        has_attribute=True,
        props=[
            PropSpec("title_location"),
            PropSpec("vertical_scrollbar"),
            PropSpec("horizontal_scrollbar"),
            PropSpec("show_grid"),
            PropSpec("show_headers"),
            PropSpec("edit"),
            PropSpec("protection"),
        ],
    ),
                                                                               
                                             
                                                                               
    "HTMLDocumentField": ElementSchema(
        element_type="HTMLDocumentField",
        has_attribute=True,
        props=[
            PropSpec("title_location"),
            PropSpec("width"),
            PropSpec("height"),
            PropSpec("horizontal_stretch"),
            PropSpec("vertical_stretch"),
            PropSpec("stretch"),
            PropSpec("template", target="template_ref"),
        ],
    ),
                                                                               
                                               
                                                                               
    "CalendarField": ElementSchema(
        element_type="CalendarField",
        has_attribute=True,
        props=[
            PropSpec("title_location"),
            PropSpec("width"),
            PropSpec("height"),
            PropSpec("show_current_date"),
            PropSpec("first_day_of_week"),
            PropSpec("begin_of_representation_period"),
            PropSpec("end_of_representation_period"),
        ],
    ),
                                                                               
                                           
                                                                               
    "ChartField": ElementSchema(
        element_type="ChartField",
        has_attribute=True,
        props=[
            PropSpec("title_location"),
            PropSpec("width"),
            PropSpec("height"),
            PropSpec("chart_type"),
            PropSpec("show_legend"),
            PropSpec("transparent_background"),
        ],
    ),
                                                                               
                                                                    
                                                                               
    "PlannerField": ElementSchema(
        element_type="PlannerField",
        has_attribute=True,
        props=[
            PropSpec("title_location"),
            PropSpec("width"),
            PropSpec("height"),
            PropSpec("enable_drag"),                             
            PropSpec("show_weekends"),
            PropSpec("period"),
            PropSpec("representation"),
        ],
    ),
                                                                               
                                  
                                                                               
    "UsualGroup": ElementSchema(
        element_type="UsualGroup",
        has_children=True,
        props=[
            *MULTILANG_TITLE,
            PropSpec("show_title", default=False),
            PropSpec("group_direction", default="Vertical"),
            PropSpec("representation", default="None"),
            PropSpec("behavior"),
            PropSpec("read_only"),
        ],
    ),
                                                                               
                                
                                                                               
    "ButtonGroup": ElementSchema(
        element_type="ButtonGroup",
        has_children=True,
        props=[
            *MULTILANG_TITLE,
            PropSpec("group_direction", default="Horizontal"),
        ],
    ),
                                                                               
                                         
                                                                               
    "ColumnGroup": ElementSchema(
        element_type="ColumnGroup",
        has_children=True,
        props=[
            *MULTILANG_TITLE,
            PropSpec("group_layout", default="Horizontal"),
            PropSpec("show_in_header", default=True),
            *ALIGNMENT_PROPS,
        ],
    ),
                                                                               
                            
                                                                               
    "Popup": ElementSchema(
        element_type="Popup",
        has_children=True,
        children_key="child_items",
        props=[
            *MULTILANG_TITLE,
            PropSpec("picture"),
            PropSpec("representation"),
        ],
    ),
                                                                               
                                 
                                                                 
                                                                               
    "Pages": ElementSchema(
        element_type="Pages",
        has_children=True,
        children_key="pages",                     
        props=[
            PropSpec("pages_representation", default="TabsOnTop"),
        ],
    ),
                                                                               
                                            
                                                                               
    "Page": ElementSchema(
        element_type="Page",
        has_children=True,
        children_key="elements",
        props=[
            PropSpec("title", multilang=True),
        ],
    ),
}


                                                                               
                    
                                                                               

                                        
COLUMN_GROUP_ALLOWED_CHILDREN = {"LabelField", "InputField", "CheckBoxField", "PictureField"}


def get_schema(element_type: str) -> Optional[ElementSchema]:
           
    return SCHEMAS.get(element_type)
