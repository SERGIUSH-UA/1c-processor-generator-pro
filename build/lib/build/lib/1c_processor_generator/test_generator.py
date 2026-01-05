   

import logging
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader

from .models import TestsConfig, Processor

logger = logging.getLogger(__name__)


class TestGenerator:
           

    def __init__(
        self,
        processor: Processor,
        tests_config: TestsConfig,
        output_dir: Path,
        epf_path: Path,
        persistent_ib_path: Optional[Path] = None,
    ):
                   
        self.processor = processor
        self.tests_config = tests_config
        self.output_dir = Path(output_dir)
        self.epf_path = Path(epf_path)
        self.persistent_ib_path = persistent_ib_path

                            
        templates_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
                                                 
        self.jinja_env.globals["repr"] = repr

    def generate(self) -> bool:
                   
        try:
                                         
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Генерація тестів в {self.output_dir}...")

                                      
            self._generate_conftest()

                                                  
            self._generate_test_file()

                                                       
            if self.tests_config.procedural_tests:
                self._copy_procedural_tests()

                                      
            (self.output_dir / "__init__.py").write_text("# Auto-generated tests\n")

            logger.info("✅ Тести згенеровано успішно")
            return True

        except Exception as e:
            logger.error(f"❌ Помилка генерації тестів: {e}")
            return False

    def _generate_conftest(self):
                                            
        logger.info("Генерація conftest.py...")

        template = self.jinja_env.get_template("conftest.py.j2")
        content = template.render(
            processor_name=self.processor.name,
            epf_path=str(self.epf_path.absolute()),
            persistent_ib_path=str(self.persistent_ib_path.absolute()) if self.persistent_ib_path else None,
            use_external_connection=self.tests_config.use_external_connection,
            use_automation_server=self.tests_config.use_automation_server,
            load_from_configuration=True,                                                 
        )

        output_file = self.output_dir / "conftest.py"
        output_file.write_text(content, encoding="utf-8")
        logger.info(f"✅ {output_file}")

    def _generate_test_file(self):
                                             
        logger.info(f"Генерація test_{self.processor.name}.py...")

        template = self.jinja_env.get_template("test_file.py.j2")
        content = template.render(
            processor_name=self.processor.name,
            tests_config=self.tests_config,
            declarative_tests=self.tests_config.declarative_tests,
            procedural_tests=self.tests_config.procedural_tests,
        )

        output_file = self.output_dir / f"test_{self.processor.name}.py"
        output_file.write_text(content, encoding="utf-8")
        logger.info(f"✅ {output_file}")

    def _copy_procedural_tests(self):
                                                    
        if not self.tests_config.procedural_tests:
            return

        logger.info("Копіювання процедурних тестів...")

        source = Path(self.tests_config.procedural_tests.file)
        if not source.exists():
            logger.warning(f"⚠️  BSL файл не знайдено: {source}")
            return

                                          
        dest = self.output_dir / source.name
        dest.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        logger.info(f"✅ Скопійовано {source} -> {dest}")

    def inject_procedural_tests_into_objectmodule(
        self,
        objectmodule_path: Path,
        output_path: Path
    ) -> bool:
                   
        if not self.tests_config.procedural_tests:
            logger.info("⏭️  Немає procedural tests для інжекту")
            return False

        try:
            logger.info("💉 Інжектування procedural tests в ObjectModule...")

                                        
            if not objectmodule_path.exists():
                logger.error(f"❌ ObjectModule не знайдено: {objectmodule_path}")
                return False

            objectmodule_content = objectmodule_path.read_text(encoding="utf-8-sig")

                                               
            tests_bsl_path = Path(self.tests_config.procedural_tests.file)
            if not tests_bsl_path.exists():
                logger.error(f"❌ Procedural tests BSL не знайдено: {tests_bsl_path}")
                return False

            tests_content = tests_bsl_path.read_text(encoding="utf-8-sig")

                                        
            test_procedures = self._extract_test_procedures(tests_content)

            if not test_procedures:
                logger.warning("⚠️  Не знайдено test procedures в BSL файлі")
                return False

            logger.info(f"📋 Знайдено {len(test_procedures)} test procedure(s)")

                                                         
            injected_content = self._inject_procedures(objectmodule_content, test_procedures)

                                    
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(injected_content, encoding="utf-8-sig")

            logger.info(f"✅ ObjectModule з тестами: {output_path}")
            logger.info(f"📊 Інжектовано процедур: {len(test_procedures)}")

            return True

        except Exception as e:
            logger.error(f"❌ Помилка інжекту procedural tests: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _extract_test_procedures(self, bsl_content: str) -> list:
                   
        import re

        procedures = []

                                                                              
                                             
        pattern = r'(&НаСервере\s+)?(Процедура|Функция)\s+([А-Яа-яA-Za-z0-9_]+)\s*\([^)]*\).*?Конец(Процедуры|Функции)'

        matches = re.finditer(pattern, bsl_content, re.DOTALL | re.IGNORECASE)

        for match in matches:
            procedure_text = match.group(0)
            procedure_name = match.group(3)

                                                                
            if procedure_name.startswith("Тест_"):
                                               
                if "Экспорт" not in procedure_text:
                                                       
                    procedure_text = procedure_text.replace(
                        f"{match.group(2)} {procedure_name}",
                        f"{match.group(2)} {procedure_name}() Экспорт",
                        1
                    )

                procedures.append({
                    "name": procedure_name,
                    "text": procedure_text,
                    "type": match.group(2)                        
                })

                logger.debug(f"  ✓ Extracted: {procedure_name}")

        return procedures

    def _inject_procedures(self, objectmodule_content: str, test_procedures: list) -> str:
                   
                                 
        injection = "\n\n#Область Тестування\n\n"
        injection += "// ========================================================================\n"
        injection += "// AUTO-GENERATED TEST PROCEDURES (v2.23.0+)\n"
        injection += "// \n"
        injection += "// ⚠️ WARNING: This ObjectModule contains test procedures.\n"
        injection += "//            For production EPF, use clean ObjectModule without tests.\n"
        injection += "//            This version is used ONLY for test_runner.py\n"
        injection += "// ========================================================================\n\n"

        for proc in test_procedures:
            injection += proc["text"] + "\n\n"

        injection += "#КонецОбласти // Тестування\n"

                                                                        
                                            
        result = objectmodule_content.rstrip() + "\n" + injection

        return result
