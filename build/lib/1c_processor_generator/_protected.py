
import importlib.util
import struct
import sys
from pathlib import Path
from typing import Any, Optional

# VERSION AND PLATFORM DETECTION

SUPPORTED_VERSIONS = ('cp310', 'cp311', 'cp312', 'cp313', 'cp314')
SUPPORTED_PLATFORMS = ('win_amd64', 'win32')

def _get_python_tag() -> str:
    """Get Python version tag (e.g., 'cp311')."""
    major, minor = sys.version_info[:2]
    return f"cp{major}{minor}"

def _get_platform_tag() -> str:
    """Get platform tag (e.g., 'win_amd64' or 'win32')."""
    if sys.platform != 'win32':
        raise RuntimeError(
            "1c-processor-generator PRO features require Windows.\n"
            f"Current platform: {sys.platform}\n"
            "XML generation is available on all platforms (use source version)."
        )
    is_64bit = struct.calcsize("P") * 8 == 64
    return 'win_amd64' if is_64bit else 'win32'

# MODULE LOADING

def _load_module_from_path(pyd_path: Path) -> Any:
    """Load a .pyd module from specific path."""
    spec = importlib.util.spec_from_file_location("_protected", pyd_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to create module spec for {pyd_path}")

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except OSError as e:
        # DLL load failed - usually missing Visual C++ Redistributable
        error_msg = str(e).lower()
        if "dll load failed" in error_msg or "не найден" in error_msg or "not found" in error_msg:
            raise ImportError(
                f"Failed to load {pyd_path.name}: {e}\n\n"
                f"This usually means Visual C++ Redistributable is not installed.\n\n"
                f"SOLUTION: Download and install from:\n"
                f"  64-bit: https://aka.ms/vs/17/release/vc_redist.x64.exe\n"
                f"  32-bit: https://aka.ms/vs/17/release/vc_redist.x86.exe\n\n"
                f"After installation, restart your terminal and try again."
            ) from e
        raise
    return module

def _find_pyd_path() -> Path:
    """Find the correct _protected.pyd for current environment."""
    py_tag = _get_python_tag()
    platform_tag = _get_platform_tag()

    # Validate Python version
    if py_tag not in SUPPORTED_VERSIONS:
        supported_str = ", ".join([v.replace("cp", "3.") for v in SUPPORTED_VERSIONS])
        raise ImportError(
            f"Python {sys.version_info.major}.{sys.version_info.minor} is not supported.\n"
            f"Supported versions: Python {supported_str}\n"
            f"Please install a supported Python version or use source distribution."
        )

    base_dir = Path(__file__).parent

    
    
    
    

    search_paths = [
        # Fat Binary (GitHub release)
        base_dir / "_protected_bins" / platform_tag / py_tag / "_protected.pyd",
        # PyPI wheel (direct placement)
        base_dir / "_protected.pyd",
        # Development (versioned name, local build)
        base_dir / f"_protected.{py_tag}-{platform_tag}.pyd",
    ]

    for pyd_path in search_paths:
        if pyd_path.exists():
            return pyd_path

    # Not found - helpful error
    paths_str = "\n  - ".join(str(p) for p in search_paths)
    raise ImportError(
        f"No compatible _protected.pyd found for Python {py_tag} on {platform_tag}.\n"
        f"Searched:\n  - {paths_str}\n\n"
        f"Supported: Python 3.10-3.14 on Windows (x64/x86).\n"
        f"Solutions:\n"
        f"  1. Install via pip: pip install 1c-processor-generator\n"
        f"  2. Download correct version: https://github.com/SERGIUSH-UA/1c-processor-generator-pro/releases\n"
        f"  3. Use source version for development (includes _protected.py source)"
    )

# LOAD AND RE-EXPORT

_module: Optional[Any] = None

try:
    _pyd_path = _find_pyd_path()
    _module = _load_module_from_path(_pyd_path)
except (ImportError, RuntimeError) as e:
    # Store error for lazy reporting
    _load_error = e
    _module = None

if _module is None:
    # Provide stub that raises error on any access
    class _ErrorProxy:
        def __getattr__(self, name: str) -> Any:
            raise _load_error  # type: ignore
    _module = _ErrorProxy()

# Re-export all symbols from loaded module
# These are the known public exports from _protected.py

# Class IDs
CLASS_ID_EXTERNAL_DATA_PROCESSOR = getattr(_module, 'CLASS_ID_EXTERNAL_DATA_PROCESSOR', None)
CLASS_ID_EXTERNAL_REPORT = getattr(_module, 'CLASS_ID_EXTERNAL_REPORT', None)

# Functions
get_xml_namespaces = getattr(_module, 'get_xml_namespaces', None)
get_form_xml_namespaces = getattr(_module, 'get_form_xml_namespaces', None)
get_type_mapping = getattr(_module, 'get_type_mapping', None)
get_element_suffixes = getattr(_module, 'get_element_suffixes', None)
get_class_id = getattr(_module, 'get_class_id', None)

get_element_submenu_xml = getattr(_module, 'get_element_submenu_xml', None)
get_data_path_xml = getattr(_module, 'get_data_path_xml', None)
get_table_data_path_xml = getattr(_module, 'get_table_data_path_xml', None)
get_line_number_data_path_xml = getattr(_module, 'get_line_number_data_path_xml', None)
get_element_id_increment = getattr(_module, 'get_element_id_increment', None)
get_element_structure = getattr(_module, 'get_element_structure', None)

get_embedded_template = getattr(_module, 'get_embedded_template', None)
has_embedded_templates = getattr(_module, 'has_embedded_templates', None)
get_all_template_names = getattr(_module, 'get_all_template_names', None)

is_bsp_pro_feature = getattr(_module, 'is_bsp_pro_feature', None)

# Integrity verification
verify_integrity = getattr(_module, 'verify_integrity', None)

# Internal symbols (may be used by other modules)
_TEMPLATE_CONTENT = getattr(_module, '_TEMPLATE_CONTENT', None)
_COPYRIGHT_NOTICE = getattr(_module, '_COPYRIGHT_NOTICE', None)

__all__ = [
    # Class IDs
    'CLASS_ID_EXTERNAL_DATA_PROCESSOR',
    'CLASS_ID_EXTERNAL_REPORT',
    # Functions
    'get_xml_namespaces',
    'get_form_xml_namespaces',
    'get_type_mapping',
    'get_element_suffixes',
    'get_class_id',
    # Element rendering
    'get_element_submenu_xml',
    'get_data_path_xml',
    'get_table_data_path_xml',
    'get_line_number_data_path_xml',
    'get_element_id_increment',
    'get_element_structure',
    # Templates
    'get_embedded_template',
    'has_embedded_templates',
    'get_all_template_names',
    # PRO features
    'is_bsp_pro_feature',
    # Integrity
    'verify_integrity',
]
