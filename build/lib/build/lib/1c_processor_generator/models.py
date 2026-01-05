   

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from uuid import uuid4


def generate_uuid() -> str:
                                                  
    return str(uuid4()).lower()


@dataclass
class Column:
                                   
    name: str
    type: str
    synonym_ru: Optional[str] = None
    synonym_uk: Optional[str] = None
    synonym_en: Optional[str] = None
    length: Optional[int] = None              
    digits: Optional[int] = None              
    fraction_digits: Optional[int] = None              
    read_only: bool = False                                
    uuid: str = field(default_factory=generate_uuid)

    def __post_init__(self):
        if not self.synonym_ru:
            self.synonym_ru = self.name
        if not self.synonym_uk:
            self.synonym_uk = self.name
        if not self.synonym_en:
            self.synonym_en = self.name


@dataclass
class TabularSection:
                                  
    name: str
    synonym_ru: Optional[str] = None
    synonym_uk: Optional[str] = None
    synonym_en: Optional[str] = None
    columns: List[Column] = field(default_factory=list)
    uuid: str = field(default_factory=generate_uuid)
    type_id: str = field(default_factory=generate_uuid)
    value_id: str = field(default_factory=generate_uuid)
    row_type_id: str = field(default_factory=generate_uuid)
    row_value_id: str = field(default_factory=generate_uuid)

    def __post_init__(self):
        if not self.synonym_ru:
            self.synonym_ru = self.name
        if not self.synonym_uk:
            self.synonym_uk = self.name
        if not self.synonym_en:
            self.synonym_en = self.name


@dataclass
class Attribute:
                          
    name: str
    type: str
    synonym_ru: Optional[str] = None
    synonym_uk: Optional[str] = None
    synonym_en: Optional[str] = None
    length: Optional[int] = None              
    digits: Optional[int] = None              
    fraction_digits: Optional[int] = None              
    uuid: str = field(default_factory=generate_uuid)

    def __post_init__(self):
        if not self.synonym_ru:
            self.synonym_ru = self.name
        if not self.synonym_uk:
            self.synonym_uk = self.name
        if not self.synonym_en:
            self.synonym_en = self.name


                                                      


@dataclass
class AppearanceStyle:
           
    back_color: Optional[str] = None               
    text_color: Optional[str] = None               
    font_bold: Optional[bool] = None
    font_italic: Optional[bool] = None
    visible: Optional[bool] = None
    enabled: Optional[bool] = None


@dataclass
class ConditionalFilter:
           
    field: str                                      
    comparison: str = "Equal"                             
    value: Any = None                                      
    value_type: str = "string"                                    


@dataclass
class ConditionalAppearanceItem:
           
    name: str
    selection: List[str] = field(default_factory=list)
    filter: Optional[ConditionalFilter] = None
    appearance: Optional[AppearanceStyle] = None
    uuid: str = field(default_factory=generate_uuid)


@dataclass
class FormElement:
                                                                
    element_type: str                                                                                           
    name: str
    attribute: Optional[str] = None                              
    tabular_section: Optional[str] = None             
    command: Optional[str] = None              
    event_handlers: Dict[str, str] = field(default_factory=dict)                             
    properties: Dict[str, any] = field(default_factory=dict)                                                                                  
    child_items: List = field(default_factory=list)                                       
    conditional_appearances: List[ConditionalAppearanceItem] = field(default_factory=list)                                  


@dataclass
class FormGroup:
                                                         
    group_type: str                                             
    name: str
    title_ru: Optional[str] = None
    title_uk: Optional[str] = None
    title_en: Optional[str] = None
    group_direction: str = "Vertical"                            
    representation: str = "None"                                                                    
    show_title: bool = False
    child_items: List = field(default_factory=list)                                                    
    properties: Dict[str, any] = field(default_factory=dict)                         


@dataclass
class LongOperationSettings:
           
                
    show_progress: bool = True                                                 
    allow_cancel: bool = True                                                      
    progress_message: str = "Выполнение операции..."                           
    progress_message_uk: Optional[str] = "Виконання операції..."                           
    progress_message_en: Optional[str] = "Operation in progress..."                           

                       
    timeout_seconds: int = 300                                                                    
    wait_completion_initial: float = 0                                                                         

                      
    use_additional_parameters: bool = False                                                     
    output_messages: bool = True                                                       
    output_progress: bool = False                                                     

    def get_progress_message(self, language: str = "ru") -> str:
                                                             
        if language == "uk" and self.progress_message_uk:
            return self.progress_message_uk
        elif language == "en" and self.progress_message_en:
            return self.progress_message_en
        return self.progress_message


@dataclass
class Command:
                       
    name: str
    title_ru: str
    title_uk: str
    title_en: Optional[str] = None
    action: str = ""                         
    tooltip_ru: Optional[str] = None
    tooltip_uk: Optional[str] = None
    tooltip_en: Optional[str] = None
    picture: Optional[str] = None                                         
    shortcut: Optional[str] = None                    
    uuid: str = field(default_factory=generate_uuid)
    bsl_code: Optional[str] = None                                                

                                                 
    long_operation: bool = False                             
    long_operation_settings: Optional[LongOperationSettings] = None                                  

    def __post_init__(self):
                                                                        
        if self.long_operation and self.long_operation_settings is None:
            self.long_operation_settings = LongOperationSettings()


@dataclass
class FormAttribute:
           
    name: str
    type: str                                                                    
    synonym_ru: Optional[str] = None
    synonym_uk: Optional[str] = None
    synonym_en: Optional[str] = None
    title_ru: Optional[str] = None
    title_uk: Optional[str] = None
    title_en: Optional[str] = None
    id: int = 1                     

                                          
    time_scale: Optional[str] = None                          
    time_scale_interval: int = 1
    time_scale_format: Optional[str] = None                      
    display_current_date: bool = True
    show_weekends: bool = True

    def __post_init__(self):
        if not self.synonym_ru:
            self.synonym_ru = self.name
        if not self.synonym_uk:
            self.synonym_uk = self.name
        if not self.synonym_en:
            self.synonym_en = self.name
        if not self.title_ru:
            self.title_ru = self.synonym_ru
        if not self.title_uk:
            self.title_uk = self.synonym_uk
        if not self.title_en:
            self.title_en = self.synonym_en
                                                       
        if self.type == "planner" and self.time_scale and not self.time_scale_format:
            formats = {
                "Hour": 'DF="HH:mm"',
                "Day": 'DF="d"',
                "Week": 'DF="ddd, d MMMM"',
                "Month": 'DF="MMMM yyyy"',
            }
            self.time_scale_format = formats.get(self.time_scale, 'DF="HH:mm"')


@dataclass
class FormParameter:
           
    name: str
    type: str                                                                                
    synonym_ru: Optional[str] = None
    synonym_uk: Optional[str] = None
    synonym_en: Optional[str] = None
    key_parameter: bool = False                                  
    uuid: str = field(default_factory=generate_uuid)

    def __post_init__(self):
        if not self.synonym_ru:
            self.synonym_ru = self.name
        if not self.synonym_uk:
            self.synonym_uk = self.name
        if not self.synonym_en:
            self.synonym_en = self.name


@dataclass
class TemplatePlaceholder:
           
    name: str                                            
    bsl_value: Optional[str] = None                                 
    attribute: Optional[str] = None                                                        


@dataclass
class TemplateAssets:
           
    styles: List[dict] = field(default_factory=list)                                            
    scripts: List[dict] = field(default_factory=list)                                          


@dataclass
class Template:
           
    name: str
    template_type: str                                           
    file_path: Optional[str] = None                                    
    content: Optional[str] = None                                          
    content_binary: Optional[bytes] = None                                                   
    uuid: str = field(default_factory=generate_uuid)

                                
    auto_field: bool = False                                                            
    field_name: Optional[str] = None                                              
    target_form: Optional[str] = None                                           
    automation_file: Optional[str] = None                                 
    placeholders: List[TemplatePlaceholder] = field(default_factory=list)
    assets: Optional[TemplateAssets] = None

    def __post_init__(self):
        valid_types = {"HTMLDocument", "SpreadsheetDocument"}
        if self.template_type not in valid_types:
            raise ValueError(
                f"Template '{self.name}': Invalid template_type '{self.template_type}'. "
                f"Valid types: {valid_types}"
            )


@dataclass
class ValueTableAttribute:
                                  
    name: str
    title_ru: Optional[str] = None
    title_uk: Optional[str] = None
    title_en: Optional[str] = None
    columns: List[Column] = field(default_factory=list)
    id: int = 1


@dataclass
class ValueTreeAttribute:
           
    name: str
    title_ru: Optional[str] = None
    title_uk: Optional[str] = None
    title_en: Optional[str] = None
    columns: List[Column] = field(default_factory=list)
    id: int = 1                     


@dataclass
class DynamicListParameter:
                                     
    name: str
    type: str                                               
    default_value: Optional[any] = None                             


@dataclass
class DynamicListColumn:
                                                      
    field: str                                                           
    title_ru: Optional[str] = None                                                    
    title_uk: Optional[str] = None
    title_en: Optional[str] = None
    width: Optional[int] = None                                                                                      


@dataclass
class DynamicListAttribute:
                                        
    name: str
    title_ru: Optional[str] = None
    title_uk: Optional[str] = None
    title_en: Optional[str] = None
    manual_query: bool = False                                                           
    main_table: Optional[str] = None                                                                                
    query_text: Optional[str] = None                                     
    key_fields: List[str] = field(default_factory=list)                                                                                                            
    parameters: List[DynamicListParameter] = field(default_factory=list)                    
    use_always_fields: List[str] = field(default_factory=list)                                
    functional_options: List[str] = field(default_factory=list)                       
    auto_save_user_settings: Optional[bool] = None                        
    main_attribute: bool = False                                 
    columns: List[DynamicListColumn] = field(default_factory=list)                                     
    skip_stub_validation: bool = False                                                                      
    id: int = 1                     

                                                                     
    filter_setting_id: str = field(default_factory=generate_uuid)
    order_setting_id: str = field(default_factory=generate_uuid)
    appearance_setting_id: str = field(default_factory=generate_uuid)
    items_setting_id: str = field(default_factory=generate_uuid)

    def __post_init__(self):
        if not self.title_ru:
            self.title_ru = self.name
        if not self.title_uk:
            self.title_uk = self.name
        if not self.title_en:
            self.title_en = self.name

                                                                   
        if not self.manual_query and not self.main_table:
            raise ValueError(f"DynamicList '{self.name}': main_table обов'язковий для manual_query=false")


@dataclass
class Form:
                          
    name: str                                                     
    default: bool = False                                
    include: Optional[str] = None                                           
    handlers_dir: Optional[str] = None                                        
    handlers_file: Optional[str] = None                                                                      

                    
    elements: List[FormElement] = field(default_factory=list)
    auto_command_bar_elements: List[FormElement] = field(default_factory=list)
    form_groups: List[FormGroup] = field(default_factory=list)
    command_bars: List[FormGroup] = field(default_factory=list)

                   
    commands: List[Command] = field(default_factory=list)

                 
    events: Dict[str, str] = field(default_factory=dict)                             
    events_bsl: Dict[str, str] = field(default_factory=dict)                     

                       
    properties: Dict[str, any] = field(default_factory=dict)                         

                                                                 
    parameters: List[FormParameter] = field(default_factory=list)

                                            
    form_attributes: List[FormAttribute] = field(default_factory=list)                                                    
    value_table_attributes: List[ValueTableAttribute] = field(default_factory=list)
    value_tree_attributes: List[ValueTreeAttribute] = field(default_factory=list)                                
    dynamic_list_attributes: List[DynamicListAttribute] = field(default_factory=list)

                                                          
    helper_procedures: Dict[str, str] = field(default_factory=dict)                                 

                                          
    documentation_file: Optional[str] = None                                                     
    documentation: Optional[str] = None                                                             

                    
    uuid: str = field(default_factory=generate_uuid)

                                                 
    conditional_appearances: List[ConditionalAppearanceItem] = field(default_factory=list)


@dataclass
class ValidationConfig:
           
                                       
    syntax_check_enabled: bool = True                                    
    check_thin_client: bool = True                             
    check_server: bool = True                          
    check_web_client: bool = False                         
    check_external_connection: bool = False                      
    check_thick_client: bool = False                    

                                      
    semantic_check_enabled: bool = False                                                                 
    check_incorrect_references: bool = True                               
    check_handlers_existence: bool = True                                     
    check_empty_handlers: bool = True                                  
    check_unreference_procedures: bool = False                                                   
    check_extended_modules: bool = True                                              

                                                          
    @property
    def check_modules_enabled(self) -> bool:
                                                                       
        return self.syntax_check_enabled

    @property
    def check_config_enabled(self) -> bool:
                                                                         
        return self.semantic_check_enabled


                                                      


@dataclass
class BSPCommand:
           
    id: str                                                                       
    title_ru: str                                                                
    title_uk: Optional[str] = None                                
    title_en: Optional[str] = None                                
    usage: str = "CallOfServerMethod"                                                                          
    modifier: Optional[str] = None                                                        
    handler: Optional[str] = None                                                                      
    template_name: Optional[str] = None                                               
    show_notification: bool = True                                                                  
    check_posting: bool = True                                                    
    hide: bool = False                                                      
    replaced_commands: Optional[str] = None                                               
    uuid: str = field(default_factory=generate_uuid)

    def __post_init__(self):
        if not self.title_uk:
            self.title_uk = self.title_ru
        if not self.title_en:
            self.title_en = self.title_ru


@dataclass
class BSPConfig:
           
    type: str                                                                                        
    version: str = "1.0"                                                     
    safe_mode: bool = True                                                         
    information: Optional[str] = None                                                 
    targets: List[str] = field(default_factory=list)                                     
    commands: List[BSPCommand] = field(default_factory=list)                   
    print_handler: str = "Печать"                                              
    uuid: str = field(default_factory=generate_uuid)

                          
    VALID_TYPES = {
        "PrintForm",                          
        "ObjectFilling",                          
        "CreationOfRelatedObjects",                             
        "Report",                     
        "AdditionalDataProcessor",                            
        "AdditionalReport",                         
        "MessageTemplate",                      
    }

    def __post_init__(self):
        if self.type not in self.VALID_TYPES:
            raise ValueError(
                f"BSPConfig: Invalid type '{self.type}'. "
                f"Valid types: {self.VALID_TYPES}"
            )
        if not self.targets:
            raise ValueError("BSPConfig: 'targets' cannot be empty")
        if not self.commands:
            raise ValueError("BSPConfig: 'commands' cannot be empty")


@dataclass
class Processor:
                             
    name: str
    synonym_ru: Optional[str] = None
    synonym_uk: Optional[str] = None
    synonym_en: Optional[str] = None
    platform_version: str = "2.11"                     
    attributes: List[Attribute] = field(default_factory=list)
    tabular_sections: List[TabularSection] = field(default_factory=list)

                                          
                                                                             
    languages: List[str] = field(default_factory=lambda: ["ru", "uk", "en"])

                                 
    forms: List[Form] = field(default_factory=list)

                                   
    templates: List[Template] = field(default_factory=list)

                                               
    object_module_bsl: Optional[str] = None                                  
    object_module_from_handlers: Optional[str] = None                                                                  

                      
    main_uuid: str = field(default_factory=generate_uuid)
    object_id: str = field(default_factory=generate_uuid)
    type_id: str = field(default_factory=generate_uuid)
    value_id: str = field(default_factory=generate_uuid)
    form_uuid: str = field(default_factory=generate_uuid)

                                                
    validation: ValidationConfig = field(default_factory=ValidationConfig)

                                        
    tests_config: Optional[TestsConfig] = None                                           

                                        
                                                                                                                                      
    long_operation_handlers: Dict[str, str] = field(default_factory=dict)

                                              
                                                                                        
    bsp_config: Optional[BSPConfig] = None

    def __post_init__(self):
        if not self.synonym_ru:
            self.synonym_ru = self.name
        if not self.synonym_uk:
            self.synonym_uk = self.name
        if not self.synonym_en:
            self.synonym_en = self.name

    def add_attribute(self, name: str, type: str, **kwargs) -> Attribute:
                             
        attr = Attribute(name=name, type=type, **kwargs)
        self.attributes.append(attr)
        return attr

    def add_tabular_section(self, name: str, **kwargs) -> TabularSection:
                                     
        ts = TabularSection(name=name, **kwargs)
        self.tabular_sections.append(ts)
        return ts

                                 
    def add_form(self, name: str, default: bool = False, **kwargs) -> Form:
                          
        form = Form(name=name, default=default, **kwargs)
        self.forms.append(form)
        return form

    def get_default_form(self) -> Optional[Form]:
                                             
        for form in self.forms:
            if form.default:
                return form
                                                          
        return self.forms[0] if self.forms else None

    def get_form_by_name(self, name: str) -> Optional[Form]:
                                     
        for form in self.forms:
            if form.name == name:
                return form
        return None


                                               


@dataclass
class MessageAssertion:
           
                                 
    contains: Optional[str] = None                              
    equals: Optional[str] = None                                 
    count: Optional[int] = None                            

                                           
    matches: Optional[str] = None                      
    starts_with: Optional[str] = None                  
    ends_with: Optional[str] = None                      


@dataclass
class TableAssertion:
           
    table_name: str                                                                        
    row_count: Optional[int] = None                                      
    columns: List[str] = field(default_factory=list)                               
    row_data: Optional[Dict[int, Dict[str, any]]] = None                                                           


@dataclass
class ExceptionAssertion:
           
    raised: bool = True                                                  
    contains: Optional[str] = None                                 


@dataclass
class TestAssertion:
           
                                  
                                                                                     
    attributes: Dict[str, any] = field(default_factory=dict)

    messages: List[MessageAssertion] = field(default_factory=list)                         
    tables: List[TableAssertion] = field(default_factory=list)                     
    exception: Optional[ExceptionAssertion] = None                        


@dataclass
class TestSetup:
           
    attributes: Dict[str, any] = field(default_factory=dict)                                           
    table_rows: Dict[str, List[Dict[str, any]]] = field(default_factory=dict)                                              


@dataclass
class TestFixture:
           
    name: str                                          
    setup: TestSetup                                                         


@dataclass
class DeclarativeTest:
           
    name: str                                                                                       
    description: Optional[str] = None                       
    use_fixtures: List[str] = field(default_factory=list)                                               
    setup: Optional[TestSetup] = None                                                             
    execute_command: Optional[str] = None                             
    execute_procedure: Optional[str] = None                                                      
    assert_result: Optional[TestAssertion] = None                                 


@dataclass
class ProceduralTests:
           
    file: str                                                                                                
    procedures: List[str] = field(default_factory=list)                                        


@dataclass
class ObjectModuleTestsConfig:
           
    declarative: List[DeclarativeTest] = field(default_factory=list)                      
    procedural: Optional[ProceduralTests] = None                                         


@dataclass
class FormTestsConfig:
           
    name: str              
    declarative: List[DeclarativeTest] = field(default_factory=list)                      
    procedural: Optional[ProceduralTests] = None                                        


@dataclass
class TestsConfig:
           
                                              
    objectmodule_tests: Optional[ObjectModuleTestsConfig] = None                      
    forms: List[FormTestsConfig] = field(default_factory=list)                  

                                              
    fixtures: Dict[str, TestFixture] = field(default_factory=dict)

                                   
    persistent_ib_path: Optional[str] = None                         
    timeout: int = 300                                               
