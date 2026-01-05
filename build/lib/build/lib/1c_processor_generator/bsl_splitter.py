   

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .constants import ENCODING_UTF8_BOM


class BSLSplitter:
                                                                       

                                          

                                                         
                                                                                         
    PROCEDURE_PATTERN = re.compile(
        r'(?:^|\n)'                                 
        r'((?:&[^\n]+\n)+)?'                                                     
        r'\s*'                   
        r'(Процедура|Функция|Procedure|Function|Асинх|Async)'                
        r'\s+'           
        r'(\w+)'                                    
        r'\s*\('                     
        r'([^)]*)'                                                 
        r'\)'                    
        r'(.*?)'                                        
        r'(КонецПроцедуры|КонецФункции|EndProcedure|EndFunction)',                            
        re.DOTALL | re.MULTILINE | re.IGNORECASE
    )

                                       
    COMMENTS_BEFORE_PROCEDURE = re.compile(
        r'((?:^|\n)(?://[^\n]*\n)+)',                    
        re.MULTILINE
    )

                                           
    DOCUMENTATION_REGION_PATTERN = re.compile(
        r'#Область\s+Документация\s*\n(.*?)\n#КонецОбласти',
        re.DOTALL | re.IGNORECASE
    )

                                            
                                                                         
                                                           
                                                                                          
    OBJECT_MODULE_REGION_PATTERN = re.compile(
        r"(?:^|\n)#(?:Область|Region)\s+(?:Модуль(?:Объекта|Об['\u0027]?єкта)|ObjectModule)\s*\n(.*?)\n#(?:КонецОбласти|EndRegion)",
        re.DOTALL | re.IGNORECASE
    )

    def __init__(self, bsl_file_path: Path):
                   
        self.bsl_file_path = Path(bsl_file_path)

        if not self.bsl_file_path.exists():
            raise FileNotFoundError(f"BSL файл не знайдено: {self.bsl_file_path}")

                                  
        self.content = self._load_file()

    def _load_file(self) -> str:
                   
        try:
                                   
            return self.bsl_file_path.read_text(encoding=ENCODING_UTF8_BOM)
        except UnicodeDecodeError:
                                               
            try:
                return self.bsl_file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                                                                     
                return self.bsl_file_path.read_text(encoding="windows-1251")

    def extract_documentation_region(self) -> Optional[str]:
                   
        match = self.DOCUMENTATION_REGION_PATTERN.search(self.content)

        if not match:
            return None

                                           
        documentation = match.group(1).strip()

                                                                     
        self.content = self.content[:match.start()] + self.content[match.end():]

        print(f"  ✓ Витягнуто регіон Документация ({len(documentation)} символів)")

        return documentation

    def extract_object_module_region(self) -> Optional[str]:
                   
        match = self.OBJECT_MODULE_REGION_PATTERN.search(self.content)

        if not match:
            return None

                                           
        object_module_code = match.group(1).strip()

                                                                     
        self.content = self.content[:match.start()] + self.content[match.end():]

        print(f"  ✓ Витягнуто регіон МодульОбъекта ({len(object_module_code)} символів)")

        return object_module_code

    def extract_procedures(self) -> Dict[str, str]:
                   
        procedures = {}

                                       
        for match in self.PROCEDURE_PATTERN.finditer(self.content):
            directive = match.group(1)                       
            proc_type = match.group(2)                         
            proc_name = match.group(3)         
            params = match.group(4)                
            body = match.group(5)             
            end_tag = match.group(6)                                     

                                           
            full_code = self._assemble_procedure(
                directive=directive,
                proc_type=proc_type,
                proc_name=proc_name,
                params=params,
                body=body,
                end_tag=end_tag
            )

            procedures[proc_name] = full_code

            print(f"  ✓ Витягнуто процедуру: {proc_name}")

        if not procedures:
            print(f"⚠️  Не знайдено процедур у файлі {self.bsl_file_path}")

        return procedures

    def _assemble_procedure(
        self,
        directive: Optional[str],
        proc_type: str,
        proc_name: str,
        params: str,
        body: str,
        end_tag: str
    ) -> str:
                   
        parts = []

                            
        if directive:
            parts.append(directive.strip())

                             
        parts.append(f"{proc_type} {proc_name}({params})")

                        
        parts.append(body)

                         
        parts.append(end_tag)

        return "\n".join(parts)

    def split_to_directory(self, output_dir: Path) -> Dict[str, Path]:
                   
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        procedures = self.extract_procedures()
        file_paths = {}

        print(f"\n📂 Збереження {len(procedures)} процедур у {output_dir}...")

        for proc_name, proc_code in procedures.items():
            file_path = output_dir / f"{proc_name}.bsl"

                                                              
            file_path.write_text(proc_code, encoding=ENCODING_UTF8_BOM)

            file_paths[proc_name] = file_path
            print(f"  ✓ {file_path.name}")

        return file_paths

    @staticmethod
    def validate_bsl_file(bsl_file: Path) -> Tuple[bool, str]:
                   
        if not bsl_file.exists():
            return False, f"Файл не знайдено: {bsl_file}"

        if not bsl_file.is_file():
            return False, f"Шлях не є файлом: {bsl_file}"

        if bsl_file.suffix.lower() not in [".bsl", ".txt"]:
            return False, f"Невірне розширення файлу: {bsl_file.suffix} (очікується .bsl)"

                                          
        try:
            content = bsl_file.read_text(encoding=ENCODING_UTF8_BOM)
            if not content.strip():
                return False, f"Файл порожній: {bsl_file}"
        except Exception as e:
            return False, f"Помилка читання файлу: {e}"

        return True, ""


def split_bsl_file(bsl_file: Path, output_dir: Path) -> Optional[Dict[str, Path]]:
           
    try:
                   
        is_valid, error = BSLSplitter.validate_bsl_file(bsl_file)
        if not is_valid:
            print(f"❌ {error}")
            return None

                    
        splitter = BSLSplitter(bsl_file)
        return splitter.split_to_directory(output_dir)

    except Exception as e:
        print(f"❌ Помилка розділення BSL файлу: {e}")
        import traceback
        traceback.print_exc()
        return None
