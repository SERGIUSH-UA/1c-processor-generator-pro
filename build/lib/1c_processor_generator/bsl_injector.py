   

import re
from pathlib import Path
from typing import Dict, Optional, Tuple

                                                     
from .pro._gc import get_generation_context

                                       
_gen_ctx = get_generation_context()
FORM_EVENT_SIGNATURES = _gen_ctx["form_event_signatures"]
ELEMENT_EVENT_SIGNATURES = _gen_ctx["element_event_signatures"]
EVENT_HANDLER_TEMPLATE = _gen_ctx["event_handler_template"]
SERVER_CALL_TEMPLATE = _gen_ctx["server_call_template"]
SERVER_PROCEDURE_TEMPLATE = _gen_ctx["server_procedure_template"]
LONG_OPERATION_CLIENT_BUTTON_TEMPLATE = _gen_ctx["long_operation_client_button_template"]
LONG_OPERATION_SERVER_START_TEMPLATE = _gen_ctx["long_operation_server_start_template"]
LONG_OPERATION_CLIENT_COMPLETION_TEMPLATE = _gen_ctx["long_operation_client_completion_template"]


class BSLInjector:
                                                            

    @staticmethod
    def has_bsl_signature(code: str) -> bool:
                   
        stripped = code.strip()
        return (
            stripped.startswith("&") or
            stripped.startswith("Процедура") or
            stripped.startswith("Функция") or
            stripped.startswith("Procedure") or
            stripped.startswith("Function") or
            stripped.startswith("Асинх") or                             
            stripped.startswith("Async")
        )

    def __init__(
        self,
        handlers_dir: Optional[Path] = None,
        handlers_file: Optional[Path] = None,
    ):
                   
        self.handlers_dir = None
        self._loaded_handlers: Dict[str, str] = {}
        self._helper_procedures_cache: Dict[str, str] = {}                    
        self._documentation_from_handlers: Optional[str] = None                                                           
        self._object_module_from_handlers: Optional[str] = None                                                                    

                                                     
        if handlers_file:
            self.load_handlers_from_single_file(handlers_file)
                                                  
        elif handlers_dir:
            self.handlers_dir = Path(handlers_dir)

    def load_handlers_from_single_file(self, bsl_file: Path) -> None:
                   
        from .bsl_splitter import BSLSplitter

        bsl_file = Path(bsl_file)

        if not bsl_file.exists():
            print(f"❌ BSL файл не знайдено: {bsl_file}")
            return

        print(f"📦 Завантаження BSL handlers з монолітного файлу {bsl_file.name}...")

        try:
                                                                                 
            splitter = BSLSplitter(bsl_file)

                                                                               
            documentation = splitter.extract_documentation_region()
            if documentation:
                self._documentation_from_handlers = documentation

                                                                                
            object_module_code = splitter.extract_object_module_region()
            if object_module_code:
                self._object_module_from_handlers = object_module_code

                                 
            procedures = splitter.extract_procedures()

                              
            self._loaded_handlers = procedures

            print(f"✅ Завантажено {len(procedures)} процедур з {bsl_file.name}")

        except Exception as e:
            print(f"❌ Помилка завантаження BSL файлу: {e}")
            import traceback
            traceback.print_exc()

    def load_handler(self, handler_name: str, handlers_dir: Optional[Path] = None) -> Optional[str]:
                   
                                                              
        if handler_name in self._loaded_handlers:
            return self._loaded_handlers[handler_name]

                                                       
        search_dir = Path(handlers_dir) if handlers_dir else self.handlers_dir

                                                                   
        if not search_dir:
            return None

                              
        handler_file = search_dir / f"{handler_name}.bsl"

        if not handler_file.exists():
            print(f"⚠️  BSL файл не знайдено: {handler_file}")
            return None

        try:
                                                           
            code = handler_file.read_text(encoding="utf-8-sig").strip()
            self._loaded_handlers[handler_name] = code
            return code
        except Exception as e:
            import traceback
            print(f"❌ Помилка читання {handler_file}: {e}")
            traceback.print_exc()
            return None

    def wrap_handler_code(
        self,
        code: str,
        handler_name: str,
        event_signature: dict,
    ) -> str:
                   
                                                                             
        if self.has_bsl_signature(code):
            return code

                                    
        return EVENT_HANDLER_TEMPLATE.format(
            directive=event_signature["directive"],
            handler_name=handler_name,
            params=event_signature["params"],
            body=self._indent_code(code),
        )

    def wrap_server_call_handler(
        self,
        client_code: str,
        server_code: str,
        client_handler: str,
        server_handler: str,
        params: str,
    ) -> str:
                   
                                                             
        if client_code:
                                                  
            if self.has_bsl_signature(client_code):
                client_proc = client_code
            else:
                client_proc = EVENT_HANDLER_TEMPLATE.format(
                    directive="НаКлиенте",
                    handler_name=client_handler,
                    params=params,
                    body=self._indent_code(client_code),
                )
        else:
                                                         
            client_proc = SERVER_CALL_TEMPLATE.format(
                client_handler=client_handler,
                params=params,
                server_handler=server_handler,
            )

                            
        if server_code:
                                                                       
            if self.has_bsl_signature(server_code):
                server_proc = server_code
            else:
                                            
                server_body = self._indent_code(server_code)
                server_proc = SERVER_PROCEDURE_TEMPLATE.format(
                    server_handler=server_handler
                ).replace(
                    "// Вставить содержимое обработчика.",
                    server_body
                )
        else:
                                                            
            server_proc = SERVER_PROCEDURE_TEMPLATE.format(
                server_handler=server_handler
            )

        return f"{client_proc}\n\n{server_proc}"

    def wrap_command_handler(
        self,
        code: str,
        handler_name: str,
        is_client: bool = True,
    ) -> str:
                   
                                                     
        if self.has_bsl_signature(code):
            return code

        directive = "НаКлиенте" if is_client else "НаСервере"
        return EVENT_HANDLER_TEMPLATE.format(
            directive=directive,
            handler_name=handler_name,
            params="Команда",
            body=self._indent_code(code),
        )

    def _extract_and_store_helpers(
        self,
        code: str,
        handler_name: str,
        form,
    ) -> str:
                   
        main_code, helpers = self._extract_main_and_helpers(code, handler_name)
        if helpers:
            form.helper_procedures.update(helpers)
        return main_code

    def _load_server_handler(
        self,
        handler_name: str,
        suffix: str,
        handlers_dir: Optional[Path],
        used_handlers: set,
    ) -> Optional[str]:
                   
        server_handler = f"{handler_name}{suffix}"
        server_code = self.load_handler(server_handler, handlers_dir)
        if server_code:
            used_handlers.add(server_handler)
        return server_code

    def _wrap_with_signature(
        self,
        code: str,
        handler_name: str,
        directive: str,
        params: str = "",
    ) -> str:
                   
        if self.has_bsl_signature(code):
            return code

        return EVENT_HANDLER_TEMPLATE.format(
            directive=directive,
            handler_name=handler_name,
            params=params,
            body=self._indent_code(code),
        )

    def inject_form_handlers(self, form, handlers_dir: Optional[Path] = None) -> set:
                   
        used_handlers = set()

                                             
        for event_name, handler_name in list(form.events.items()):
                                                                         
            code = self.load_handler(handler_name, handlers_dir)

            if code:
                used_handlers.add(handler_name)

                                                                
                if not hasattr(form, "events_bsl"):
                    form.events_bsl = {}

                event_sig = FORM_EVENT_SIGNATURES.get(event_name)
                if not event_sig:
                    print(f"⚠️  Невідома подія форми: {event_name}")
                    continue

                                                          
                if "server_call" in event_sig:
                    server_handler = event_sig["server_call"]
                    server_code = self.load_handler(server_handler, handlers_dir)
                    if server_code:
                        used_handlers.add(server_handler)

                                                                         
                    main_client_code = self._extract_and_store_helpers(code, handler_name, form)
                    main_server_code = self._extract_and_store_helpers(server_code, server_handler, form) if server_code else ""

                    wrapped = self.wrap_server_call_handler(
                        client_code=main_client_code,
                        server_code=main_server_code,
                        client_handler=handler_name,
                        server_handler=server_handler,
                        params=event_sig["params"],
                    )
                else:
                                       
                    main_code = self._extract_and_store_helpers(code, handler_name, form)
                    wrapped = self.wrap_handler_code(main_code, handler_name, event_sig)

                form.events_bsl[handler_name] = wrapped

                                              
        for cmd in form.commands:
                                            
            code = self.load_handler(cmd.action, handlers_dir)

            if code:
                used_handlers.add(cmd.action)

                                                      
                main_code = self._extract_and_store_helpers(code, cmd.action, form)

                                                   
                wrapped = self.wrap_command_handler(main_code, cmd.action, is_client=True)

                                      
                cmd.bsl_code = wrapped

                                                                      
                server_code = self._load_server_handler(cmd.action, "НаСервере", handlers_dir, used_handlers)

                if server_code:
                                                                              
                    main_server_code = self._extract_and_store_helpers(server_code, f"{cmd.action}НаСервере", form)

                                                   
                    server_wrapped = self._wrap_with_signature(main_server_code, f"{cmd.action}НаСервере", "НаСервере", "")

                                                
                    cmd.bsl_code = f"{cmd.bsl_code}\n\n{server_wrapped}"

                                                       
        for elem in form.elements:
            if not elem.event_handlers:
                continue

            for event_name, handler_name in elem.event_handlers.items():
                code = self.load_handler(handler_name, handlers_dir)

                if code:
                    used_handlers.add(handler_name)

                    event_sig = ELEMENT_EVENT_SIGNATURES.get(event_name)
                    if not event_sig:
                        print(f"⚠️  Невідома подія елемента: {event_name}")
                        continue

                                                              
                    if "server_call_suffix" in event_sig:
                        server_handler = f"{handler_name}{event_sig['server_call_suffix']}"
                        server_code = self._load_server_handler(handler_name, event_sig['server_call_suffix'], handlers_dir, used_handlers)

                                                                             
                        main_client_code = self._extract_and_store_helpers(code, handler_name, form)
                        main_server_code = self._extract_and_store_helpers(server_code, server_handler, form) if server_code else ""

                                                                                         
                        wrapped = self.wrap_server_call_handler(
                            client_code=main_client_code,
                            server_code=main_server_code,
                            client_handler=handler_name,
                            server_handler=server_handler,
                            params=event_sig["params"],
                        )
                    else:
                                           
                        main_code = self._extract_and_store_helpers(code, handler_name, form)
                        wrapped = self.wrap_handler_code(main_code, handler_name, event_sig)

                                           
                    if not hasattr(elem, "bsl_code"):
                        elem.bsl_code = {}
                    elem.bsl_code[event_name] = wrapped

                                                               
        documentation_parts = []
        if form.documentation:                                       
            documentation_parts.append(form.documentation)
        if self._documentation_from_handlers:                            
            documentation_parts.append(self._documentation_from_handlers)

        if documentation_parts:
            form.documentation = '\n\n'.join(documentation_parts)
            print(f"📚 Об'єднано документацію для форми {form.name} ({len(form.documentation)} символів)")

        return used_handlers

    def inject_forms_handlers(self, processor) -> set:
                   
                                     
        if not processor.forms:
            return set()

                                                                     
        has_any_handlers = (self.handlers_dir or self._loaded_handlers or
                           any(form.handlers_dir for form in processor.forms))

        if not has_any_handlers:
                                              
            return set()

        total_used_handlers = set()

        for form in processor.forms:
                                                    
            form_handlers_dir = None
            if form.handlers_dir:
                                             
                form_handlers_dir = Path(form.handlers_dir)
                                                                                    
                if not form_handlers_dir.is_absolute() and self.handlers_dir:
                    form_handlers_dir = self.handlers_dir / form.handlers_dir

                                                
            used_handlers = self.inject_form_handlers(form, form_handlers_dir)
            total_used_handlers.update(used_handlers)

        if total_used_handlers:
            print(f"✅ BSL handlers інжектовано для {len(processor.forms)} форм: {len(total_used_handlers)} обробників")

        return total_used_handlers

    def _inject_standalone_helpers(self, form, used_handlers: set) -> None:
                   
                                                                 
        standalone_helpers = {}
        for proc_name, proc_code in self._loaded_handlers.items():
            if proc_name not in used_handlers:
                standalone_helpers[proc_name] = proc_code

        if standalone_helpers:
                                                  
            form.helper_procedures.update(standalone_helpers)
            print(f"✅ Додано {len(standalone_helpers)} standalone helpers: {', '.join(list(standalone_helpers.keys())[:5])}{'...' if len(standalone_helpers) > 5 else ''}")

    def inject_long_operation_handlers(self, processor) -> set:
                   
                                                         
        long_operation_commands = []
        for form in processor.forms:
            for cmd in form.commands:
                if cmd.long_operation:
                    long_operation_commands.append((form, cmd))

        if not long_operation_commands:
            return set()                                                   

        print(f"🔄 Генерація long operation handlers ({len(long_operation_commands)} команд)...")

                                                                                  
        used_handlers = set()

        for form, cmd in long_operation_commands:
            settings = cmd.long_operation_settings
            if settings is None:
                                                              
                from .models import LongOperationSettings
                settings = LongOperationSettings()

                                                                 
            validate_handler_name = f'{cmd.name}ПроверкаПередЗапуском'
            validate_code = self.load_handler(validate_handler_name, form.handlers_dir or self.handlers_dir)

            complete_handler_name = f'{cmd.name}ОбработкаРезультата'
            complete_code = self.load_handler(complete_handler_name, form.handlers_dir or self.handlers_dir)

                                                                                
            waiting_params_parts = []
            if settings.show_progress:
                waiting_params_parts.append(f'\tПараметрыОжидания.ВыводитьОкноОжидания = Истина;')
                waiting_params_parts.append(f'\tПараметрыОжидания.ТекстСообщения = "{settings.progress_message}";')
            else:
                waiting_params_parts.append(f'\tПараметрыОжидания.ВыводитьОкноОжидания = Ложь;')

            if settings.output_messages:
                waiting_params_parts.append(f'\tПараметрыОжидания.ВыводитьСообщения = Истина;')

            if settings.output_progress:
                waiting_params_parts.append(f'\tПараметрыОжидания.ВыводитьПрогрессВыполнения = Истина;')

            waiting_params_code = "\n".join(waiting_params_parts)

                                                    
            validation_call = ""
            if validate_code:
                validation_call = f"""Если НЕ {cmd.name}ПроверкаПередЗапуском() Тогда
\t\tВозврат;
\tКонецЕсли;
\t"""

                                                               
            client_button_code = LONG_OPERATION_CLIENT_BUTTON_TEMPLATE.format(
                command_name=cmd.name,
                validation_call=validation_call,
                waiting_params_code=waiting_params_code
            )

                                                           
            if settings.use_additional_parameters:
                parameters_code = """// Передаем все атрибуты формы
\tДля Каждого Реквизит Из ПолучитьРеквизиты() Цикл
\t\tПараметрыЗадания.Вставить(Реквизит.Имя, ЭтотОбъект[Реквизит.Имя]);
\tКонецЦикла;"""
            else:
                parameters_code = ""                                                             

                               
            if settings.wait_completion_initial > 0:
                wait_initial_code = f"\tПараметрыВыполнения.ОжидатьЗавершение = {settings.wait_completion_initial};"
            else:
                wait_initial_code = ""

                                                                                 
            server_start_code = LONG_OPERATION_SERVER_START_TEMPLATE.format(
                command_name=cmd.name,
                parameters_code=parameters_code,
                job_title=cmd.title_ru,
                wait_initial_code=wait_initial_code,
                processor_name=processor.name
            )

                                                                                   
            completion_parts = [
                '&НаКлиенте',
                f'Процедура {cmd.name}Завершение(Результат, ДополнительныеПараметры) Экспорт',
                '\t',
                '\t// Проверка отмены операции',
                '\tЕсли Результат = Неопределено Тогда',
                '\t\tСообщить("Операция отменена пользователем");',
                '\t\tВозврат;',
                '\tКонецЕсли;',
                '\t',
                '\t// Проверка ошибок',
                '\tЕсли Результат.Статус = "Ошибка" Тогда',
                '\t\tПоказатьПредупреждение(, Результат.КраткоеПредставлениеОшибки);',
                '\t\tВозврат;',
                '\tКонецЕсли;',
                '\t'
            ]

            if complete_code:
                                                                
                completion_parts.extend([
                    '\t// Получение результата из хранилища',
                    '\tРезультатОперации = ПолучитьИзВременногоХранилища(Результат.АдресРезультата);',
                    '\t',
                    f'\t{cmd.name}ОбработкаРезультата(РезультатОперации);',
                    '\t'
                ])

            completion_parts.extend([
                '\tСообщить("Операция успешно завершена!");',
                '\t',
                'КонецПроцедуры'
            ])

            completion_handler_code = '\n'.join(completion_parts)

                                                                 
            server_handler_name = f'{cmd.name}НаСервере'
            server_handler_code = self.load_handler(server_handler_name, form.handlers_dir or self.handlers_dir)

            if not server_handler_code:
                raise FileNotFoundError(
                    f"❌ Long operation command '{cmd.name}' requires handler file: {server_handler_name}.bsl\n\n"
                    f"Create this file with the following signature:\n"
                    f"&НаСервере\n"
                    f"Процедура {server_handler_name}(Параметры, АдресРезультата) Экспорт\n"
                    f"    // Your business logic here\n"
                    f"    // Store result: ПоместитьВоВременноеХранилище(Результат, АдресРезультата);\n"
                    f"КонецПроцедуры"
                )

                                                                                   
            processor.long_operation_handlers[f'{cmd.name}Кнопка'] = client_button_code
            processor.long_operation_handlers[f'{cmd.name}ЗапуститьВФоне'] = server_start_code
            processor.long_operation_handlers[f'{cmd.name}Завершение'] = completion_handler_code
            processor.long_operation_handlers[f'{cmd.name}НаСервере'] = server_handler_code

                                                                            
            used_handlers.add(server_handler_name)

                                                   
            handler_count = 4                                                 
            optional_handlers = []

            if validate_code:
                processor.long_operation_handlers[validate_handler_name] = validate_code
                used_handlers.add(validate_handler_name)
                handler_count += 1
                optional_handlers.append('ПроверкаПередЗапуском')

            if complete_code:
                processor.long_operation_handlers[complete_handler_name] = complete_code
                used_handlers.add(complete_handler_name)
                handler_count += 1
                optional_handlers.append('ОбработкаРезультата')

                           
            optional_str = f" + {', '.join(optional_handlers)}" if optional_handlers else ""
            print(f"   ✅ {cmd.name}: {handler_count} handlers (Кнопка, ЗапуститьВФoне, Завершение, НаСервере{optional_str})")

        return used_handlers

    def inject_all_handlers(self, processor) -> None:
                   
                                
        if not processor.forms:
            print("⚠️  Немає форм для інжекції BSL handlers")
            return

                                                    
        has_any_handlers = (self.handlers_dir or self._loaded_handlers or
                           any(form.handlers_dir for form in processor.forms))

        if not has_any_handlers:
            print("⚠️  Немає BSL handlers для інжекції")
            return

                                                  
        if self._loaded_handlers:
            print(f"📦 Використання попередньо завантажених BSL handlers...")
        elif self.handlers_dir:
            print(f"📦 Завантаження BSL handlers з {self.handlers_dir}...")
        else:
                                 
            print(f"📦 Завантаження BSL handlers з form-specific директорій...")

                                                     
        total_used_handlers = self.inject_forms_handlers(processor)

                                                     
        long_op_used_handlers = self.inject_long_operation_handlers(processor)
        total_used_handlers.update(long_op_used_handlers)

                                                               
        if self._loaded_handlers and processor.forms:
            self._inject_standalone_helpers(processor.forms[0], total_used_handlers)

    def _split_procedures(self, code: str) -> Tuple[str, Dict[str, str]]:
                   
        procedures = {}
        preamble_lines = []                           
        current_proc_name = None
        current_proc_lines = []
        depth = 0
        found_first_procedure = False                                        

                                                  
        proc_start_pattern = re.compile(
            r'^\s*(?:&\w+\s+)?(?:Процедура|Функция|Procedure|Function|Асинх|Async)\s+(\w+)',
            re.IGNORECASE
        )
        proc_end_pattern = re.compile(
            r'^\s*(?:КонецПроцедуры|КонецФункции|EndProcedure|EndFunction)',
            re.IGNORECASE
        )

        lines = code.split('\n')

                                                                                        
        directive_pattern = re.compile(r'^\s*&\w+\s*$', re.IGNORECASE)

        for i, line in enumerate(lines):
                                                   
            match = proc_start_pattern.match(line)
            if match and depth == 0:
                                                         
                if current_proc_name and current_proc_lines:
                    procedures[current_proc_name] = '\n'.join(current_proc_lines)

                                                       
                found_first_procedure = True

                                                                   
                                                                             
                if preamble_lines and directive_pattern.match(preamble_lines[-1]):
                    directive_line = preamble_lines.pop()
                    current_proc_lines = [directive_line, line]
                else:
                    current_proc_lines = [line]

                                          
                current_proc_name = match.group(1)
                depth = 1
                continue

                                                               
            if not found_first_procedure:
                preamble_lines.append(line)
                continue

                                         
            if current_proc_name:
                current_proc_lines.append(line)

                                              
                if proc_end_pattern.match(line):
                    depth -= 1
                    if depth == 0:
                                             
                        procedures[current_proc_name] = '\n'.join(current_proc_lines)
                        current_proc_name = None
                        current_proc_lines = []
                                                                             
                elif proc_start_pattern.match(line):
                    depth += 1

                                                          
        if current_proc_name and current_proc_lines:
            procedures[current_proc_name] = '\n'.join(current_proc_lines)

                                                                      
                                                             
        while preamble_lines:
            last_line = preamble_lines[-1].strip()
                                                               
            if not last_line or last_line.startswith('//') or '======' in last_line:
                preamble_lines.pop()
            else:
                break

                                                                             
        preamble = '\n'.join(preamble_lines).strip()

        return preamble, procedures

    def _extract_main_and_helpers(self, code: str, handler_name: str) -> Tuple[str, Dict[str, str]]:
                   
                                                                
        preamble, procedures = self._split_procedures(code)

                                                         
                                                                   
        if preamble:
                                                                
                                                      
            return preamble, procedures

                                                                  
        if procedures:
                                                                     
            if len(procedures) == 1:
                                                         
                proc_code = list(procedures.values())[0]
                return proc_code, {}

                                                                          
            main_proc_code = None
            helpers = {}

            for proc_name, proc_code in procedures.items():
                                                     
                if (proc_name == handler_name or
                    handler_name.endswith(proc_name) or
                    proc_name.startswith(handler_name)):
                    main_proc_code = proc_code
                else:
                    helpers[proc_name] = proc_code

                                                                           
            if main_proc_code is None:
                first_name = list(procedures.keys())[0]
                main_proc_code = procedures[first_name]
                                                           
                helpers.pop(first_name, None)

            return main_proc_code, helpers

                                                                    
                                                    
        return code, {}

    @staticmethod
    def _indent_code(code: str, indent: str = "\t") -> str:
                   
        lines = code.split("\n")
        return "\n".join(f"{indent}{line}" if line.strip() else line for line in lines)
