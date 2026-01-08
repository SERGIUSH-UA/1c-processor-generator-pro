   

import sys
import argparse
from pathlib import Path

try:
    from .generator import ProcessorGenerator, create_minimal_processor
    from .models import Processor, ValidationConfig
    from .metadata_analyzer import MetadataAnalyzer
    from .yaml_parser import parse_yaml_config
    from .test_generator import TestGenerator
    from .sync_tool import run_sync
    from .pro import LicensedEPFCompiler
    from .pro import get_license_manager, send_first_run_telemetry
    from .pro import check_version_in_background
except ImportError:
                                                    
    from generator import ProcessorGenerator, create_minimal_processor
    from models import Processor, ValidationConfig
    from metadata_analyzer import MetadataAnalyzer
    from yaml_parser import parse_yaml_config
    from test_generator import TestGenerator
    from sync_tool import run_sync
    from pro import LicensedEPFCompiler
    from pro import get_license_manager, send_first_run_telemetry
    from pro import check_version_in_background


def create_example_processor() -> Processor:
                                                      
    processor = Processor(
        name="ПримерОбработки",
        synonym_ru="Пример обработки",
        synonym_uk="Приклад обробки",
        platform_version="2.11",
    )

              
    processor.add_attribute(
        name="ИсходныйПользователь",
        type="CatalogRef.Пользователи",
        synonym_ru="Исходный пользователь",
        synonym_uk="Вихідний користувач",
    )

    processor.add_attribute(
        name="ЦелевойПользователь",
        type="CatalogRef.Пользователи",
        synonym_ru="Целевой пользователь",
        synonym_uk="Цільовий користувач",
    )

                      
    ts = processor.add_tabular_section(
        name="Данные",
        synonym_ru="Данные",
        synonym_uk="Дані",
    )

    ts.columns.append(Processor.__dict__['add_attribute'].__func__(
        ts,
        name="Выбрано",
        type="boolean",
        synonym_ru="Выбрано",
        synonym_uk="Вибрано",
    ).__dict__)

    ts.columns.append(Processor.__dict__['add_attribute'].__func__(
        ts,
        name="Наименование",
        type="string",
        synonym_ru="Наименование",
        synonym_uk="Найменування",
        length=150,
    ).__dict__)

                    
    processor.add_form_element(
        element_type="InputField",
        name="ИсходныйПользователь",
        attribute="ИсходныйПользователь",
    )

    processor.add_form_element(
        element_type="InputField",
        name="ЦелевойПользователь",
        attribute="ЦелевойПользователь",
    )

    processor.add_form_element(
        element_type="Table",
        name="Данные",
        tabular_section="Данные",
    )

    return processor


def cmd_minimal(args):
                                              
    print(f"🚀 Створення мінімальної обробки '{args.name}' (версія {args.version})...")
    processor = create_minimal_processor(args.name, args.version)
    return generate_processor(args, processor)


def cmd_example(args):
                                           
    print("🚀 Створення прикладу обробки...")
    processor = create_example_processor()
    return generate_processor(args, processor)


def cmd_yaml(args):
                                                       
    if not args.config.exists():
        print(f"❌ Помилка: Файл не знайдено: {args.config}")
        sys.exit(1)

    print(f"🚀 Генерація обробки з YAML: {args.config}...")

    processor = parse_yaml_config(
        args.config,
        handlers_dir=args.handlers,
        handlers_file=args.handlers_file,
        normalize_bsl_escapes=getattr(args, 'normalize_bsl_escapes', False)
    )

    if not processor:
        print("❌ Помилка парсингу YAML")
        sys.exit(1)

    return generate_processor(args, processor)


def cmd_sync(args):
                                                                                
                          
    if not args.modified_xml.exists():
        print(f"❌ Помилка: Modified XML не знайдено: {args.modified_xml}")
        sys.exit(1)

    if not args.config.exists():
        print(f"❌ Помилка: Config YAML не знайдено: {args.config}")
        sys.exit(1)

    if not args.handlers.exists():
        print(f"❌ Помилка: Handlers file не знайдено: {args.handlers}")
        sys.exit(1)

                                  
    snapshot_dir = args.snapshot or (args.config.parent / "_snapshot")
    original_xml = snapshot_dir / "original.xml"

    if not original_xml.exists():
        print(f"❌ Помилка: Snapshot не знайдено: {original_xml}")
        print(f"   Генеруйте процесор ще раз щоб створити snapshot")
        sys.exit(1)

    print(f"🔄 Синхронізація змін...")
    print(f"   Original XML: {original_xml}")
    print(f"   Modified XML: {args.modified_xml}")
    print(f"   Config: {args.config}")
    print(f"   Handlers: {args.handlers}")

              
    exit_code = run_sync(
        original_xml=str(original_xml),
        modified_xml=str(args.modified_xml),
        config=str(args.config),
        handlers=str(args.handlers),
        auto_apply=args.auto_apply,
        json_output=args.json,
        llm_mode=args.llm_mode
    )

    sys.exit(exit_code)


def cmd_decompile(args):
                                                                     
    if not args.epf_file.exists():
        print(f"❌ Помилка: Бінарний файл не знайдено: {args.epf_file}")
        sys.exit(1)

    print(f"🔄 Розпакування бінарного файлу → XML: {args.epf_file}")

                                                                           
    compiler = LicensedEPFCompiler(args.compiler_path, use_persistent_ib=not args.no_persistent_ib)

    if not compiler.platform_path:
        print("❌ Компілятор не знайдено!")
        print("   Перевірте системні вимоги або вкажіть шлях через --compiler-path")
        sys.exit(1)

    if compiler.decompile_epf(args.epf_file, args.output):
        print(f"\n🎉 Готово! XML створено: {args.output}")
        xml_files = list(args.output.glob("*.xml"))
        print(f"📊 Створено файлів: {len(xml_files)}")
        sys.exit(0)
    else:
        print("\n❌ Помилка розпакування")
        sys.exit(1)


def cmd_features(args):
                                                                     
    import json

                           
    registry_path = Path(__file__).parent.parent / "docs" / "feature_registry.json"
    if not registry_path.exists():
        print("❌ feature_registry.json не знайдено!")
        print("   Запустіть: python scripts/generate_feature_registry.py")
        sys.exit(1)

    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

                          
    if args.json:
        if args.category:
            if args.category in registry["categories"]:
                output = {args.category: registry["categories"][args.category]}
            else:
                print(f"❌ Категорія '{args.category}' не знайдена")
                sys.exit(1)
        elif args.name:
            output = search_by_name(registry, args.name)
        elif args.search:
            output = search_features(registry, args.search)
        else:
            output = registry
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0

                 
    if args.category:
        print_category(registry, args.category)
    elif args.name:
        print_feature_details(registry, args.name)
    elif args.search:
        print_search_results(registry, args.search)
    else:
        print_overview(registry)

    return 0


def print_overview(registry: dict):
                                         
    print(f"1C Processor Generator v{registry['version']} - Feature Registry")
    print("=" * 60)
    print()
    for cat_name, cat_data in registry["categories"].items():
        count = cat_data.get("count", len(cat_data.get("items", [])))
        desc = cat_data.get("description", "")
        print(f"  {cat_name:12} ({count:3} items) - {desc}")
    print()
    print("Use --category <name> to see items in a category")
    print("Use --search <query> to search all features")
    print("Use --name <name> to see feature details")
    print("Use --json for machine-readable output")


def print_category(registry: dict, category: str):
                                       
    if category not in registry["categories"]:
        print(f"❌ Категорія '{category}' не знайдена")
        print(f"   Доступні: {', '.join(registry['categories'].keys())}")
        sys.exit(1)

    cat_data = registry["categories"][category]
    print(f"{category} - {cat_data.get('description', '')}")
    print("=" * 60)

    items = cat_data.get("items", [])
    if isinstance(items, list) and items:
                                                                                             
        if "wrong" in items[0]:
                                    
            for item in items:
                wrong = item.get("wrong", "")
                correct = item.get("correct", "")
                explanation = item.get("explanation", "")
                print(f"  ❌ {wrong}")
                print(f"  ✅ {correct}")
                print(f"     {explanation}")
                print()
        else:
                             
            for item in items:
                name = item.get("name", "")
                desc = item.get("description", "")
                since = item.get("since", "")
                since_str = f" (v{since})" if since else ""
                print(f"  {name:25} {desc}{since_str}")
    else:
                                                                   
        print(f"  Count: {cat_data.get('count', 0)}")
        print(f"  Source: {cat_data.get('source', '')}")
        if "common" in cat_data:
            print("  Common examples:")
            for item in cat_data["common"][:8]:
                print(f"    - {item}")


def print_feature_details(registry: dict, name: str):
                                              
    result = search_by_name(registry, name)
    if not result:
        print(f"❌ Фіча '{name}' не знайдена")
        sys.exit(1)

    for cat_name, items in result.items():
        print(f"Category: {cat_name}")
        for item in items:
            print(f"  Name: {item.get('name', '')}")
            print(f"  Description: {item.get('description', '')}")
            print(f"  Docs: {item.get('docs', '')}")
            if "since" in item:
                print(f"  Since: v{item['since']}")
            if "options" in item:
                print("  Options:")
                for opt in item["options"]:
                    print(f"    - {opt}")
            if "capabilities" in item:
                print("  Capabilities:")
                for cap in item["capabilities"]:
                    print(f"    - {cap}")
            print()


def print_search_results(registry: dict, query: str):
                              
    results = search_features(registry, query)
    if not results:
        print(f"❌ Нічого не знайдено для '{query}'")
        sys.exit(1)

    total = sum(len(items) for items in results.values())
    print(f"Found {total} results for '{query}':")
    print("=" * 60)

    for cat_name, items in results.items():
        print(f"\n[{cat_name}]")
        for item in items:
            name = item.get("name", "")
            desc = item.get("description", "")
            print(f"  {name:25} {desc}")


def search_by_name(registry: dict, name: str) -> dict:
                                       
    results = {}
    name_lower = name.lower()

    for cat_name, cat_data in registry["categories"].items():
        items = cat_data.get("items", [])
        if isinstance(items, list):
            matches = [item for item in items if item.get("name", "").lower() == name_lower]
            if matches:
                results[cat_name] = matches

    return results


def search_features(registry: dict, query: str) -> dict:
                                                         
    results = {}
    query_lower = query.lower()

    for cat_name, cat_data in registry["categories"].items():
        items = cat_data.get("items", [])
        if isinstance(items, list):
            matches = [
                item for item in items
                if query_lower in item.get("name", "").lower()
                or query_lower in item.get("description", "").lower()
            ]
            if matches:
                results[cat_name] = matches

    return results


                                                                               
                                     
                                                                               

def cmd_activate(args):
                                          
    print(f"🔑 Активація ліцензії: {args.license_key[:8]}***")
    print()

    mgr = get_license_manager()
    result = mgr.activate_license(args.license_key)

    if result.success:
        print("=" * 60)
        print("✅ Ліцензія успішно активована!")
        print("=" * 60)
        print()
        print(f"   Тип: {result.license_type}")
        if result.expires_at:
            print(f"   Діє до: {result.expires_at[:10]}")
        else:
            print(f"   Діє: безстроково")
        print()
        print("   Тепер ви можете використовувати --output-format epf")
        print("=" * 60)
        return 0
    else:
        print("=" * 60)
        print("❌ Помилка активації")
        print("=" * 60)
        print()
        print(f"   {result.error_message}")
        print()
        print("   Перевірте правильність ліцензійного ключа.")
        print("   Підтримка: itdeo.tech@gmail.com")
        print("=" * 60)
        return 1


def cmd_license_status(args):
                                           
    mgr = get_license_manager()
    status = mgr.get_license_status()

    print("=" * 60)
    print("📋 Статус ліцензії 1C Processor Generator")
    print("=" * 60)
    print()

    if status.is_licensed:
        license_type_names = {
            "quarter": "Квартальна",
            "year": "Річна",
            "lifetime": "Довічна",
        }
        type_name = license_type_names.get(status.license_type, status.license_type)

        print(f"   Статус: ✅ PRO активовано")
        print(f"   Тип: {type_name}")
        if status.license_key:
            print(f"   Ключ: {status.license_key}")

        if status.expires_at:
            print(f"   Діє до: {status.expires_at[:10]}")
            if status.days_until_expiry is not None:
                print(f"   Залишилось: {status.days_until_expiry} днів")
        else:
            print(f"   Діє: безстроково")

        print(f"   Машин: {status.machines_used}/{status.machines_limit}")

        if status.is_offline:
            print()
            print(f"   ⚠️  Офлайн режим")
            if status.grace_period_remaining is not None:
                print(f"   Grace period: {status.grace_period_remaining} днів залишилось")

        print()
        print("   Доступні функції:")
        for feature in status.features:
            feature_names = {
                "epf_compilation": "EPF компіляція",
                "check_config": "Семантична валідація",
                "check_modules": "Синтаксична валідація",
            }
            print(f"     ✓ {feature_names.get(feature, feature)}")

        if status.watermark_removed:
            print()
            print("   ✓ Watermark видалено назавжди")
    else:
        print(f"   Статус: FREE (безкоштовна версія)")
        print()
        print("   Обмеження:")
        print("     • Тільки XML генерація (без EPF)")
        print("     • Watermark у згенерованому коді")
        print()
        print("   Upgrade to PRO: https://itdeo.tech/1c-processor-generator/#pricing")

    print()
    print("=" * 60)

                            
    if args.show_machine_id:
        print()
        print(f"   Machine ID: {mgr.machine_id}")
        print("   (використовується для активації ліцензії)")

    return 0


def cmd_setup_1c(args):
                                 
    from .pro import run_setup_command
    return run_setup_command(check=args.check, dry_run=args.dry_run)


def cmd_clear_cache(args):
           
    from .pro._pim import PersistentIBManager
    from .pro.constants import EPF_COMPILER_PERSISTENT_IB

                                                 
    manager = PersistentIBManager(designer_path=None)
    cache_info = manager.get_cache_info()

                             
    if args.info:
        if cache_info:
            print("📂 Persistent IB cache:")
            print(f"   Path: {cache_info['path']}")
            print(f"   Platform: {cache_info.get('platform_version', 'unknown')}")
            print(f"   Created: {cache_info.get('created_at', 'unknown')}")
        else:
            print("📂 Cache not found (clean)")
        return 0

                    
    if not cache_info:
        print("✓ Cache already clean")
        return 0

    print(f"🗑️  Clearing persistent IB cache...")
    print(f"   Path: {cache_info['path']}")
    if "platform_version" in cache_info:
        print(f"   Platform: {cache_info['platform_version']}")

    if manager._clear_ib():
        print("✓ Cache cleared successfully")
        return 0
    else:
        print("✗ Failed to clear cache")
        return 1


def cmd_excel2mxl(args):
                                                              
    try:
        from .pro import ExcelToMXLConverter, EXCEL_TO_MXL_AVAILABLE
    except ImportError:
        EXCEL_TO_MXL_AVAILABLE = False

    if not EXCEL_TO_MXL_AVAILABLE:
        print("❌ Для конвертації Excel → MXL потрібна бібліотека openpyxl")
        print()
        print("   Встановіть:")
        print("   pip install openpyxl>=3.1.0")
        return 1

                           
    input_path = args.input
    if args.output:
        output_path = args.output
    else:
                                 
        if input_path.lower().endswith('.xlsx'):
            output_path = input_path[:-5] + '.mxl'
        else:
            output_path = input_path + '.mxl'

                     
    languages = args.languages if args.languages else ["ru", "uk"]

    print(f"🔄 Конвертація Excel → MXL...")
    print(f"   Вхід: {input_path}")
    print(f"   Вихід: {output_path}")
    print(f"   Мови: {', '.join(languages)}")
    if args.sheet:
        print(f"   Лист: {args.sheet}")
    print()

    try:
        converter = ExcelToMXLConverter(languages=languages)
        converter.convert(input_path, output_path, args.sheet)

        print("✅ MXL успішно створено!")
        print()
        print("   Використання в YAML:")
        print("   ```yaml")
        print("   templates:")
        print(f"     - name: ПФ_MXL_Шаблон")
        print("       type: SpreadsheetDocument")
        print(f"       file: {output_path}")
        print("   ```")
        return 0

    except FileNotFoundError:
        print(f"❌ Файл не знайдено: {input_path}")
        return 1
    except Exception as e:
        print(f"❌ Помилка конвертації: {e}")
        return 1


def cmd_trial(args):
                                                    
    print(f"🎁 Запит trial ліцензії для: {args.email}")
    print()

    mgr = get_license_manager()
    result = mgr.request_trial(args.email)

    if result.success:
        print("=" * 60)
        print("✅ Trial активовано!")
        print("=" * 60)
        print()
        print(f"   Тип: TRIAL (7 днів)")
        if result.expires_at:
            print(f"   Закінчується: {result.expires_at[:10]}")
        print()
        print("   Доступні функції:")
        print("     ✓ EPF компіляція")
        print("     ✓ Семантична валідація")
        print()
        print("   ⚠️  Примітка: trial не знімає watermark з коду")
        print()
        print("   Придбати повну версію:")
        print("   https://itdeo.tech/1c-processor-generator/#pricing")
        print()
        print("=" * 60)
        return 0
    else:
        print("=" * 60)
        print("❌ Помилка запиту trial")
        print("=" * 60)
        print()
        print(f"   {result.error_message}")
        print()
        print("   Можливі причини:")
        print("     • Email вже використовувався для trial")
        print("     • Ця машина вже мала trial раніше")
        print("     • Сервер ліцензій недоступний")
        print()
        print("   Придбати ліцензію:")
        print("   https://itdeo.tech/1c-processor-generator/#pricing")
        print()
        print("=" * 60)
        return 1


def _adjust_platform_version_for_epf(args, processor):
                                                                    
    try:
        from .pro._evh import adjust_platform_version
        return adjust_platform_version(args, processor)
    except ImportError:
        return None


def generate_processor(args, processor):
                                                                      
                                  
    output_dir = args.output or Path.cwd() / "tmp"

    if args.dry_run:
        print(f"🔍 Dry run режим - файли не будуть створені")

                                                                          
                                         
    if args.output_format == "epf" and not args.dry_run:
        adjusted_version = _adjust_platform_version_for_epf(args, processor)
        if adjusted_version:
            processor.platform_version = adjusted_version

                   
    generator = ProcessorGenerator(processor)
    processor_root = generator.generate(str(output_dir), dry_run=args.dry_run)

    if not processor_root:
        print("\n❌ Помилка генерації XML")
        sys.exit(1)

                                           
    if args.output_format == "epf" and not args.dry_run:
        compile_to_epf(args, processor, processor_root, output_dir, generator)
    else:
        print("\n✨ Готово!")

    return 0


def has_validation_config(processor):
           
                                                                   
    if processor.validation.syntax_check_enabled or processor.validation.semantic_check_enabled:
        return True

    return False


def compile_to_epf(args, processor, processor_root, output_dir, generator):
                                   
    print("\n🔧 Генерація вихідного файлу...")

                                                                         
    compiler = LicensedEPFCompiler(args.compiler_path, use_persistent_ib=not args.no_persistent_ib)

    if not compiler.platform_path:
        print("❌ Компілятор не знайдено!")
        print("   Перевірте системні вимоги або вкажіть шлях через --compiler-path")
        print("   Альтернатива: використайте --output-format xml та скомпілюйте вручну")
        sys.exit(1)

    xml_root = processor_root / f"{processor.name}.xml"
    epf_path = output_dir / f"{processor.name}.epf"

                                                      
    requirements = MetadataAnalyzer.analyze_processor(processor)
    needs_validation = has_validation_config(processor)

                                
                                       
                                            
                                                                                
    if requirements.has_metadata() or needs_validation:
        if requirements.has_metadata():
            print(f"   Виявлено метадані: {len(requirements.catalogs)} catalogs, {len(requirements.documents)} documents, {len(requirements.common_pictures)} common_pictures")
        if needs_validation:
            print(f"   Виявлено налаштування валідації (синтаксична: {processor.validation.syntax_check_enabled}, семантична: {processor.validation.semantic_check_enabled})")
        print("   Використовую Configuration mode для валідації та/або підтримки метаданих...")
        compilation_success = compiler.compile_epf_with_configuration(
            output_dir,
            epf_path,
            processor,
            requirements,
            ignore_validation_errors=args.ignore_validation_errors
        )
    else:
        print("   Метаданих не виявлено, валідація не налаштована, використовую швидкий режим компіляції...")
        compilation_success = compiler.compile_epf(xml_root, epf_path)

    if compilation_success:
        print(f"\n🎉 Готово! Бінарний файл створено: {epf_path}")
        print(f"📊 Розмір: {epf_path.stat().st_size:,} bytes")

                                                                          
                                                       
        print(f"\n📸 Створюю snapshot з бінарного файлу експорту...")
        if generator.save_snapshot_from_epf(epf_path, output_dir, compiler):
            print(f"✅ Snapshot збережено (включає Form.xml файли для sync tool)")
        else:
            print(f"⚠️  Помилка збереження snapshot (але Бінарний файл створено успішно)")

                                                         
        if processor.tests_config:
            generate_tests(processor, epf_path, output_dir, args.compiler_path, compiler.last_temp_ib)
    else:
        print("\n❌ Помилка генерації")
        print(f"   XML файли збережено: {processor_root}")
        sys.exit(1)


def generate_tests(processor, epf_path, output_dir, compiler_path=None, temp_ib_path=None):
                                                             
    if not processor.tests_config:
        return

    print("\n🧪 Генерація автоматичних тестів...")

    try:
                                     
        tests_dir = output_dir / processor.name / "tests"

                                                                           
        if temp_ib_path and temp_ib_path.exists():
            print(f"   ✅ Використання temp_ib з компіляції: {temp_ib_path}")
            print(f"      (обробка вже в конфігурації - без security warning)")
            persistent_ib_path = temp_ib_path
        else:
                                                                
            print("   ⚠️  temp_ib не знайдено, використовую persistent_ib...")
            if not compiler_path:
                compiler_path = LicensedEPFCompiler.find_platform()
                if not compiler_path:
                    print("⚠️  Компілятор не знайдено - тести згенеровано без оптимізації")
                    persistent_ib_path = None
                else:
                    print(f"   Компілятор знайдено")
                    persistent_ib_path = LicensedEPFCompiler.get_persistent_ib(compiler_path, timeout=60)
            else:
                persistent_ib_path = LicensedEPFCompiler.get_persistent_ib(compiler_path, timeout=60)

                                  
        test_gen = TestGenerator(
            processor=processor,
            tests_config=processor.tests_config,
            output_dir=tests_dir,
            epf_path=epf_path,
            persistent_ib_path=persistent_ib_path,
        )

                         
        if test_gen.generate():
            print(f"✅ Тести згенеровано: {tests_dir}")
            print(f"   Declarative: {len(processor.tests_config.declarative_tests)}")
            if processor.tests_config.procedural_tests:
                print(f"   Procedural: {len(processor.tests_config.procedural_tests.procedures)}")

                                                                              
            if processor.tests_config.procedural_tests:
                print("\n💉 Інжектування procedural tests в ObjectModule...")

                                     
                processor_xml_dir = output_dir / processor.name                  
                clean_objectmodule = processor_xml_dir / processor.name / "Ext" / "ObjectModule.bsl"

                                                              
                                                                                                         
                                       
                                                        
                                                                         
                                                                                               
                validation_processor_name = f"{processor.name}_Validation"
                validation_xml_dir = output_dir / validation_processor_name

                                                             
                import shutil
                if validation_xml_dir.exists():
                    print(f"   🗑️  Видалення старої validation директорії...")
                    shutil.rmtree(validation_xml_dir)

                print(f"   📋 Копіювання {processor_xml_dir} → {validation_xml_dir}...")
                shutil.copytree(processor_xml_dir, validation_xml_dir)

                if validation_xml_dir.exists():
                    print(f"   ✅ Створено validation директорію: {validation_xml_dir}")

                                                                                                   
                    old_inner_dir = validation_xml_dir / processor.name
                    new_inner_dir = validation_xml_dir / validation_processor_name
                    if old_inner_dir.exists():
                        old_inner_dir.rename(new_inner_dir)
                        print(f"   🔄 Перейменовано внутрішню папку: {processor.name}/ → {validation_processor_name}/")

                                                                                               
                    xml_files_updated = 0
                    for xml_file in validation_xml_dir.rglob("*.xml"):
                        xml_content = xml_file.read_text(encoding="utf-8")
                        original_content = xml_content

                                                               
                        xml_content = xml_content.replace(
                            f"<Name>{processor.name}</Name>",
                            f"<Name>{validation_processor_name}</Name>"
                        )
                        xml_content = xml_content.replace(
                            f"<v8:content>{processor.name}</v8:content>",
                            f"<v8:content>{validation_processor_name}</v8:content>"
                        )
                        xml_content = xml_content.replace(
                            f"ExternalDataProcessorObject.{processor.name}",
                            f"ExternalDataProcessorObject.{validation_processor_name}"
                        )
                        xml_content = xml_content.replace(
                            f"ExternalDataProcessor.{processor.name}.",
                            f"ExternalDataProcessor.{validation_processor_name}."
                        )

                        if xml_content != original_content:
                            xml_file.write_text(xml_content, encoding="utf-8")
                            xml_files_updated += 1

                                                                                 
                    old_xml = validation_xml_dir / f"{processor.name}.xml"
                    new_xml = validation_xml_dir / f"{validation_processor_name}.xml"
                    if old_xml.exists():
                        old_xml.rename(new_xml)

                    print(f"   🔄 Оновлено {xml_files_updated} XML файлів з новим ім'ям процесора")
                    print(f"   🔄 Перейменовано головний XML: {processor.name}.xml → {validation_processor_name}.xml")
                else:
                    print(f"   ❌ ПОМИЛКА: Validation директорія НЕ створена!")
                    raise Exception("Failed to create validation directory")

                                                                             
                test_objectmodule = validation_xml_dir / validation_processor_name / "Ext" / "ObjectModule.bsl"

                print(f"   🔍 Перевірка шляхів:")
                print(f"      Clean ObjectModule: {clean_objectmodule} (exists: {clean_objectmodule.exists()})")
                print(f"      Test ObjectModule: {test_objectmodule} (exists: {test_objectmodule.exists()})")

                if test_gen.inject_procedural_tests_into_objectmodule(
                    objectmodule_path=clean_objectmodule,
                    output_path=test_objectmodule
                ):
                    print(f"   ✅ Procedural tests інжектовано в ObjectModule")
                    print(f"   📊 ObjectModule розмір: {test_objectmodule.stat().st_size:,} bytes")

                                                                   
                    test_epf_path = epf_path.parent / f"{epf_path.stem}_Tests.epf"
                    print(f"\n🔧 Компіляція test binary: {test_epf_path.name}...")

                                                                
                    if not compiler_path:
                        compiler_path = LicensedEPFCompiler.find_platform()

                    if compiler_path:
                        try:
                            test_compiler = LicensedEPFCompiler(compiler_path)

                                                                                    
                                                                                             
                                                                
                                                                                                                                                                          
                            test_xml_root = validation_xml_dir / f"{validation_processor_name}.xml"
                            print(f"   📁 Test XML root: {test_xml_root} (exists: {test_xml_root.exists()})")
                            print(f"   ⚡ Using fast mode for test binary (validation already done for clean EPF)...")

                            test_success = test_compiler.compile_epf(test_xml_root, test_epf_path)

                            if test_success:
                                print(f"   ✅ Test Бінарний файл створено: {test_epf_path}")
                                print(f"   📊 Розмір: {test_epf_path.stat().st_size:,} bytes")
                                print(f"\n💡 Запустіть тести: python -m 1c_processor_generator.test_runner --tests-config {tests_dir.parent / 'tests.yaml'}")
                            else:
                                print(f"   ⚠️  Помилка компіляції test binary")
                                print(f"   📁 Validation XML збережено: {validation_xml_dir}")
                        except Exception as test_compile_error:
                            print(f"   ❌ Exception під час компіляції test binary: {test_compile_error}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"   ⚠️  Компілятор не знайдено - тестовий файл не створено")
                else:
                    print(f"   ⚠️  Помилка інжекту procedural tests")
            else:
                print(f"\n💡 Запустіть тести: python -m 1c_processor_generator.test_runner {tests_dir}")
        else:
            print("⚠️  Помилка генерації тестів")
    except Exception as e:
        print(f"⚠️  Помилка генерації тестів: {e}")
        import traceback
        traceback.print_exc()


def create_parser():
                                                              
    parser = argparse.ArgumentParser(
        prog="python -m 1c_processor_generator",
        description="🛠️  Генератор зовнішніх обробок 1C",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Приклади:
  # Генерація мінімальної обробки
  python -m 1c_processor_generator minimal МояОбробка

  # Генерація EPF (нова можливість v2.8.0+)
  python -m 1c_processor_generator minimal МояОбробка --output-format epf

  # YAML з EPF компіляцією
  python -m 1c_processor_generator yaml --config config.yaml --handlers-file handlers.bsl --output-format epf

  # Розпакування бінарного файлу → XML
  python -m 1c_processor_generator decompile MyProcessor.epf --output MyProcessor_XML

  # Синхронізація змін з Конфігуратора (v2.25.0+)
  python -m 1c_processor_generator sync --modified-xml Modified.xml --config config.yaml --handlers handlers.bsl

  # Синхронізація в LLM режимі (автоматично + JSON output)
  python -m 1c_processor_generator sync --modified-xml Modified.xml --config config.yaml --handlers handlers.bsl --llm-mode
        """
    )

                 
    subparsers = parser.add_subparsers(dest="command", help="Доступні команди", required=True)

                     
    parser_minimal = subparsers.add_parser("minimal", help="Створити мінімальну обробку")
    parser_minimal.add_argument("name", help="Назва обробки (PascalCase, кирилиця)")
    parser_minimal.add_argument("version", nargs="?", default="2.11",
                               help="Версія формату XML (за замовчуванням 2.11)")
                                
    parser_minimal.add_argument("--output", "-o", type=Path, help="Директорія для виводу (за замовчуванням ./tmp)")
    parser_minimal.add_argument("--output-format", choices=["xml", "epf"], default="xml",
                               help="Формат виводу: xml (за замовчуванням) або epf")
    parser_minimal.add_argument("--compiler-path", type=str, help="Явний шлях до компілятора")
    parser_minimal.add_argument("--no-persistent-ib", action="store_true",
                               help="Вимкнути persistent IB кеш (повільніше, v2.8.1+)")
    parser_minimal.add_argument("--ignore-validation-errors", action="store_true",
                               help="Ігнорувати помилки BSL валідації під час компіляції (за замовчуванням зупиняється при помилках, v2.12.0+)")
    parser_minimal.add_argument("--dry-run", action="store_true", help="Перевірка без створення файлів")
    parser_minimal.set_defaults(func=cmd_minimal)

                     
    parser_example = subparsers.add_parser("example", help="Створити приклад обробки з табличною частиною")
                                
    parser_example.add_argument("--output", "-o", type=Path, help="Директорія для виводу (за замовчуванням ./tmp)")
    parser_example.add_argument("--output-format", choices=["xml", "epf"], default="xml",
                               help="Формат виводу: xml (за замовчуванням) або epf")
    parser_example.add_argument("--compiler-path", type=str, help="Явний шлях до компілятора")
    parser_example.add_argument("--no-persistent-ib", action="store_true",
                               help="Вимкнути persistent IB кеш (повільніше, v2.8.1+)")
    parser_example.add_argument("--ignore-validation-errors", action="store_true",
                               help="Ігнорувати помилки BSL валідації під час компіляції (за замовчуванням зупиняється при помилках, v2.12.0+)")
    parser_example.add_argument("--dry-run", action="store_true", help="Перевірка без створення файлів")
    parser_example.set_defaults(func=cmd_example)

                  
    parser_yaml = subparsers.add_parser("yaml", help="Створити обробку з YAML конфігурації (рекомендовано для LLM)")
    parser_yaml.add_argument("--config", "-c", type=Path, required=True, help="Шлях до YAML конфігурації")
    parser_yaml.add_argument("--handlers", type=Path, help="Директорія з окремими BSL файлами (старий підхід)")
    parser_yaml.add_argument("--handlers-file", type=Path,
                            help="Монолітний BSL файл з усіма процедурами (новий підхід, v2.7.0+)")
                             
    parser_yaml.add_argument("--output", "-o", type=Path, help="Директорія для виводу (за замовчуванням ./tmp)")
    parser_yaml.add_argument("--output-format", choices=["xml", "epf"], default="xml",
                            help="Формат виводу: xml (за замовчуванням) або epf")
    parser_yaml.add_argument("--compiler-path", type=str, help="Явний шлях до компілятора")
    parser_yaml.add_argument("--no-persistent-ib", action="store_true",
                            help="Вимкнути persistent IB кеш (повільніше, v2.8.1+)")
    parser_yaml.add_argument("--ignore-validation-errors", action="store_true",
                            help="Ігнорувати помилки BSL валідації під час компіляції (за замовчуванням зупиняється при помилках, v2.12.0+)")
    parser_yaml.add_argument("--normalize-bsl-escapes", action="store_true",
                            help="Нормалізувати escape-послідовності (\\n→newline) в BSL запитах (v2.72.0+)")
    parser_yaml.add_argument("--dry-run", action="store_true", help="Перевірка без створення файлів")
    parser_yaml.set_defaults(func=cmd_yaml)

                       
    parser_decompile = subparsers.add_parser("decompile", help="Розпакувати EPF назад в XML формат (v2.8.1+)")
    parser_decompile.add_argument("epf_file", type=Path, help="Шлях до EPF файлу для декомпіляції")
    parser_decompile.add_argument("--output", "-o", type=Path, required=True,
                                 help="Директорія для XML файлів (обов'язково)")
    parser_decompile.add_argument("--compiler-path", type=str, help="Явний шлях до компілятора")
    parser_decompile.add_argument("--no-persistent-ib", action="store_true", help="Вимкнути persistent IB кеш")
    parser_decompile.set_defaults(func=cmd_decompile)

                             
    parser_sync = subparsers.add_parser("sync",
                                       help="Синхронізувати зміни з відредагованого EPF/XML назад в YAML+BSL (v2.25.0+)")
    parser_sync.add_argument("--modified-xml", type=Path, required=True,
                            help="Шлях до відредагованого XML файлу (з Конфігуратора)")
    parser_sync.add_argument("--config", "-c", type=Path, required=True,
                            help="Шлях до YAML config файлу для оновлення")
    parser_sync.add_argument("--handlers", type=Path, required=True,
                            help="Шлях до BSL handlers файлу для оновлення")
    parser_sync.add_argument("--snapshot", type=Path,
                            help="Директорія зі snapshot (за замовчуванням: config_dir/_snapshot/)")
    parser_sync.add_argument("--auto-apply", action="store_true",
                            help="Автоматично застосувати зміни без підтвердження")
    parser_sync.add_argument("--json", action="store_true",
                            help="Вивід результатів у JSON форматі")
    parser_sync.add_argument("--llm-mode", action="store_true",
                            help="LLM-friendly режим (auto-apply + JSON output + structured data)")
    parser_sync.set_defaults(func=cmd_sync)

                                 
    parser_features = subparsers.add_parser("features",
                                           help="Показати доступні можливості генератора (v2.44.0+)")
    parser_features.add_argument("--category", "-c", type=str,
                                help="Показати фічі певної категорії (elements, events, types, cli, tools)")
    parser_features.add_argument("--search", "-s", type=str,
                                help="Пошук по назві або опису")
    parser_features.add_argument("--name", "-n", type=str,
                                help="Показати деталі конкретної фічі")
    parser_features.add_argument("--json", "-j", action="store_true",
                                help="Вивід у JSON форматі (для програмного використання)")
    parser_features.set_defaults(func=cmd_features)

                                               
    parser_activate = subparsers.add_parser("activate",
                                           help="Активувати PRO ліцензію")
    parser_activate.add_argument("license_key",
                                help="Ліцензійний ключ (формат: PRO-XXXX-XXXX-XXXX)")
    parser_activate.set_defaults(func=cmd_activate)

                                                  
    parser_license = subparsers.add_parser("license-status",
                                          help="Показати статус ліцензії")
    parser_license.add_argument("--show-machine-id", action="store_true",
                               help="Показати Machine ID (для підтримки)")
    parser_license.set_defaults(func=cmd_license_status)

                   
    parser_trial = subparsers.add_parser("trial",
                                        help="Запросити 7-денну пробну PRO ліцензію")
    parser_trial.add_argument("email",
                             help="Email адреса для отримання trial")
    parser_trial.set_defaults(func=cmd_trial)

                                 
    parser_setup = subparsers.add_parser("setup-1c",
                                         help="Налаштувати 1C для EPF компіляції")
    parser_setup.add_argument("--dry-run", action="store_true",
                             help="Показати зміни без застосування")
    parser_setup.add_argument("--check", action="store_true",
                             help="Перевірити конфігурацію (exit code 0/1)")
    parser_setup.set_defaults(func=cmd_setup_1c)

                                    
    parser_clear_cache = subparsers.add_parser("clear-cache",
                                                help="Очистити persistent IB кеш (v2.66.1+)")
    parser_clear_cache.add_argument("--info", action="store_true",
                                    help="Показати інформацію про кеш без очищення")
    parser_clear_cache.set_defaults(func=cmd_clear_cache)

                                  
    parser_excel2mxl = subparsers.add_parser("excel2mxl",
                                              help="Конвертувати Excel (.xlsx) в MXL формат для друкованих форм")
    parser_excel2mxl.add_argument("input",
                                  help="Шлях до Excel файлу (.xlsx)")
    parser_excel2mxl.add_argument("-o", "--output",
                                  help="Шлях до MXL файлу (за замовчуванням: input.mxl)")
    parser_excel2mxl.add_argument("-s", "--sheet",
                                  help="Назва листа (за замовчуванням: активний)")
    parser_excel2mxl.add_argument("-l", "--languages", nargs="+", default=["ru", "uk"],
                                  help="Мови для локалізації (за замовчуванням: ru uk)")
    parser_excel2mxl.set_defaults(func=cmd_excel2mxl)

    return parser


def main():
                             
                                                             
    send_first_run_telemetry()

                                                           
    check_version_in_background()

    parser = create_parser()
    args = parser.parse_args()

                                   
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
