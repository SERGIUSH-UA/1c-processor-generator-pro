   

import re
from typing import Dict, List, Any, Optional, Union
from .schemas import PropSpec, ElementSchema


                                              
DEFAULT_LANGUAGES = ["ru", "uk", "en"]


def parse_multilang_value(
    value: Union[str, List[str], Dict[str, str]],
    languages: List[str]
) -> Dict[str, str]:
           
    if not languages:
        languages = DEFAULT_LANGUAGES

                                             
    if isinstance(value, dict):
        return value

                                                            
    if isinstance(value, list):
        if not value:
                                                          
            return {lang: "" for lang in languages}
        result = {}
        for i, lang in enumerate(languages):
            result[lang] = value[i] if i < len(value) else value[0]
        return result

                                                            
    if isinstance(value, str):
                                                               
                                           
        if '|' in value:
                                                         
            parts = re.split(r'(?<!\\)\|', value)
                             
            parts = [p.strip().replace('\\|', '|') for p in parts]

                                                            
            if len(parts) > 1:
                result = {}
                for i, lang in enumerate(languages):
                    result[lang] = parts[i] if i < len(parts) else parts[0]
                return result
            else:
                                                                                
                return {lang: parts[0] for lang in languages}

                                               
        return {lang: value for lang in languages}

                                 
    return {lang: str(value) for lang in languages}


def normalize_multilang(
    config: Dict[str, Any],
    fields: Optional[List[str]] = None,
    languages: Optional[List[str]] = None
) -> Dict[str, Any]:
           
    if fields is None:
        fields = ["synonym", "title", "tooltip", "input_hint"]

    if languages is None:
        languages = DEFAULT_LANGUAGES

    result = config.copy()

    for field in fields:
        if field not in config:
            continue

        value = config[field]

                                                       
        if any(f"{field}_{lang}" in config for lang in languages):
            continue

                                              
        parsed = parse_multilang_value(value, languages)

                                       
        for lang, text in parsed.items():
            result[f"{field}_{lang}"] = text

                                   
        if field in result:
            del result[field]

    return result


def extract_props(config: Dict[str, Any], schema: ElementSchema) -> Dict[str, Any]:
           
    props: Dict[str, Any] = {}

    for spec in schema.props:
        if spec.multilang:
            _extract_multilang_prop(config, props, spec.key)
        else:
            _extract_simple_prop(config, props, spec)

    return props


def _extract_multilang_prop(config: Dict[str, Any], props: Dict[str, Any], key: str) -> None:
           
    has_any = any(f"{key}_{lang}" in config for lang in ["ru", "uk", "en"])

    if has_any:
        for lang in ["ru", "uk", "en"]:
            full_key = f"{key}_{lang}"
            if full_key in config:
                props[full_key] = config[full_key]

                                                   
    if key in config:
        props[key] = config[key]


def _extract_simple_prop(config: Dict[str, Any], props: Dict[str, Any], spec: PropSpec) -> None:
           
    if spec.key in config:
        target = spec.target or spec.key
        props[target] = config[spec.key]
    elif spec.default is not None:
        target = spec.target or spec.key
        props[target] = spec.default


def extract_simple_props(config: Dict[str, Any], props: Dict[str, Any], keys: List[str]) -> None:
           
    for key in keys:
        if key in config:
            props[key] = config[key]
