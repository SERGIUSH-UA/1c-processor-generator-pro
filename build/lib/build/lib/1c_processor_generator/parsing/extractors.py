   

from typing import Dict, List, Any, Optional
from .schemas import PropSpec, ElementSchema


def normalize_multilang(config: Dict[str, Any], fields: Optional[List[str]] = None) -> Dict[str, Any]:
           
    if fields is None:
        fields = ["synonym", "title", "tooltip", "input_hint"]

    result = config.copy()

    for field in fields:
        if field in config and isinstance(config[field], dict):
            nested = config[field]
            for lang in ["ru", "uk", "en"]:
                if lang in nested:
                    result[f"{field}_{lang}"] = nested[lang]
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
