   

from pathlib import Path
from typing import Optional
from jinja2 import Environment

from .models import Template
from .constants import ENCODING_UTF8_BOM


def generate_template_ext_xml(template: Template) -> str:
           
    if template.template_type == "HTMLDocument":
                                                                                 
        return '''<?xml version="1.0" encoding="UTF-8"?>
<Help xmlns="http://v8.1c.ru/8.3/xcf/extrnprops" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.11">
\t<Page>ru</Page>
\t<Page>uk</Page>
\t<Page>en</Page>
</Help>'''
    else:
                                                                   
        return '''<?xml version="1.0" encoding="UTF-8"?>
<Template xmlns="http://v8.1c.ru/8.3/xcf/extfile" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" format="Packed" formatVersion="15">
\t<data/>
</Template>'''


def write_template_content(
    template: Template,
    content_dir: Path,
    dry_run: bool = False
) -> str:
           
    if template.template_type == "HTMLDocument":
                                                                        
        for lang in ["ru", "uk", "en"]:
            content_file = content_dir / f"{lang}.html"
            if not dry_run:
                content_file.write_text(template.content, encoding="utf-8")
        return f"Template/ru.html, uk.html, en.html ({len(template.content)} bytes)"

    elif template.template_type == "SpreadsheetDocument":
        content_file = content_dir / "Template.mxl"
        if not dry_run:
            content_file.write_bytes(template.content_binary)
        return f"Template/Template.mxl ({len(template.content_binary)} bytes)"

    else:
                                            
        content_file = content_dir / "Template.txt"
        if not dry_run:
            content_file.write_text(template.content or "", encoding="utf-8")
        return f"Template/Template.txt ({len(template.content or '')} bytes)"


def generate_template_files(
    template: Template,
    templates_root_dir: Path,
    env: Environment,
    namespaces: str,
    platform_version: str,
    dry_run: bool = False
) -> None:
           
    template_name = template.name
    print(f"      Template '{template_name}'...")

                               
                                
                                             
                                                         
    template_dir = templates_root_dir / template_name
    template_ext_dir = template_dir / "Ext"
    template_content_dir = template_ext_dir / "Template"

    if not dry_run:
        templates_root_dir.mkdir(parents=True, exist_ok=True)
        template_dir.mkdir(parents=True, exist_ok=True)
        template_ext_dir.mkdir(parents=True, exist_ok=True)
        template_content_dir.mkdir(parents=True, exist_ok=True)

                                                      
    meta_template = env.get_template("template_meta.xml.j2")
    meta_content = meta_template.render(
        template=template,
        namespaces=namespaces,
        version=platform_version,
    )

    template_meta_xml = templates_root_dir / f"{template_name}.xml"
    if not dry_run:
        template_meta_xml.write_text(meta_content, encoding=ENCODING_UTF8_BOM)
    print(f"         {'📄' if dry_run else '✅'} {template_meta_xml.name}")

                                                               
    ext_template_xml = template_ext_dir / "Template.xml"
    ext_xml_content = generate_template_ext_xml(template)
    if not dry_run:
        ext_template_xml.write_text(ext_xml_content, encoding=ENCODING_UTF8_BOM)

                               
    content_description = write_template_content(template, template_content_dir, dry_run)
    print(f"         {'📄' if dry_run else '✅'} {content_description}")


def generate_all_templates(
    templates: list,
    processor_dir: Path,
    env: Environment,
    namespaces: str,
    platform_version: str,
    dry_run: bool = False
) -> None:
           
    if not templates:
        return

    print(f"\n   Generating templates...")

    templates_root_dir = processor_dir / "Templates"

    for template in templates:
        generate_template_files(
            template=template,
            templates_root_dir=templates_root_dir,
            env=env,
            namespaces=namespaces,
            platform_version=platform_version,
            dry_run=dry_run
        )

    print(f"      Templates generated: {len(templates)}")
