
import importlib.util
import importlib.abc
import struct
import sys
from pathlib import Path
from typing import Any, Optional

                                           

_PRO_MODULE_NOTICE = ""

                                

SUPPORTED_VERSIONS = ('cp310', 'cp311', 'cp312', 'cp313', 'cp314')
SUPPORTED_PLATFORMS = ('win_amd64', 'win32')

                                                            
                                                  
MODULE_MAP = {
    'a': '_lic',
    'b': '_ex',
    'c': '_const',
    'd': '_wm',
    'e': '_lc',
    'f': '_u',
    'g': '_lp',
    'h': '_df',
    'i': '_pim',
    'j': '_xc',
    'k': '_cg',
    'l': '_ec',
    'm': '_gc',
    'n': '_ep',
    'o': '_ccm',
    'p': '_bsp',
    
    'q': '_er',
    'r': '_e2m',
    
    's': '_vc',
}

def _get_python_tag() -> str:
                                                 
    major, minor = sys.version_info[:2]
    return f"cp{major}{minor}"

def _get_platform_tag() -> str:
                                                          
    if sys.platform != 'win32':
        raise RuntimeError(
            "1c-processor-generator PRO features require Windows.\n"
            f"Current platform: {sys.platform}\n"
            "XML generation is available on all platforms."
        )
    is_64bit = struct.calcsize("P") * 8 == 64
    return 'win_amd64' if is_64bit else 'win32'

                

_loaded_modules: dict = {}

def _load_module_from_path(pyd_path: Path, module_name: str) -> Any:
                                                
    spec = importlib.util.spec_from_file_location(module_name, pyd_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to create module spec for {pyd_path}")

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except OSError as e:
                                                                      
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

def _get_module(logical_name: str) -> Any:
                                                                               
    if logical_name in _loaded_modules:
        return _loaded_modules[logical_name]

    py_tag = _get_python_tag()
    platform_tag = _get_platform_tag()

                             
    if py_tag not in SUPPORTED_VERSIONS:
        supported_str = ", ".join([v.replace("cp", "3.") for v in SUPPORTED_VERSIONS])
        raise ImportError(
            f"Python {sys.version_info.major}.{sys.version_info.minor} is not supported.\n"
            f"Supported versions: Python {supported_str}"
        )

                         
    pyd_name = MODULE_MAP.get(logical_name, logical_name)
    base_dir = Path(__file__).parent

                   
                                                              
                                                      
                                                                

    search_paths = [
        base_dir / "_bins" / platform_tag / py_tag / f"{pyd_name}.pyd",
        base_dir / f"{pyd_name}.pyd",
        base_dir / f"{pyd_name}.{py_tag}-{platform_tag}.pyd",
    ]

    for pyd_path in search_paths:
        if pyd_path.exists():
                                                                        
            pyd_dir = str(pyd_path.parent)
            if pyd_dir not in sys.path:
                sys.path.insert(0, pyd_dir)

                                                                                  
            module = _load_module_from_path(pyd_path, pyd_name)
            _loaded_modules[logical_name] = module
            return module

               
    paths_str = "\n  - ".join(str(p) for p in search_paths)
    raise ImportError(
        f"PRO module '{logical_name}' ({pyd_name}.pyd) not found for Python {py_tag} on {platform_tag}.\n"
        f"Searched:\n  - {paths_str}\n\n"
        f"Install correct version: pip install 1c-processor-generator"
    )

                       

                                                                       

                                                  
_REVERSE_MODULE_MAP = {v: k for k, v in MODULE_MAP.items()}

class _ProModuleFinder(importlib.abc.MetaPathFinder):
           

    def find_spec(self, fullname, path, target=None):
                                    
        if not fullname.startswith("1c_processor_generator.pro."):
            return None

                                                                                        
        parts = fullname.split(".")
        if len(parts) != 3:
            return None

        submodule = parts[2]                                             

                                                          
        if submodule in _REVERSE_MODULE_MAP:
            logical_name = _REVERSE_MODULE_MAP[submodule]
        elif submodule in MODULE_MAP:
            logical_name = submodule
        else:
            return None

                              
        return importlib.util.spec_from_loader(
            fullname,
            _ProModuleLoader(logical_name),
            origin="pro._bins"
        )

class _ProModuleLoader(importlib.abc.Loader):
                                                             

    def __init__(self, logical_name: str):
        self.logical_name = logical_name

    def create_module(self, spec):
                                                       
        if self.logical_name in _loaded_modules:
            return _loaded_modules[self.logical_name]
        return None

    def exec_module(self, module):
                                                            
        if self.logical_name not in _loaded_modules:
            loaded = _get_module(self.logical_name)
                                           
            for attr in dir(loaded):
                if not attr.startswith('_'):
                    setattr(module, attr, getattr(loaded, attr))
                                          
            for attr in ['__doc__', '__file__', '__name__']:
                if hasattr(loaded, attr):
                    try:
                        setattr(module, attr, getattr(loaded, attr))
                    except AttributeError:
                        pass

                    
sys.meta_path.insert(0, _ProModuleFinder())

                     

class _LazyModule:
                                                                               

    def __init__(self, logical_name: str):
        object.__setattr__(self, '_logical_name', logical_name)
        object.__setattr__(self, '_module', None)

    def _ensure_loaded(self) -> Any:
        if object.__getattribute__(self, '_module') is None:
            name = object.__getattribute__(self, '_logical_name')
            module = _get_module(name)
            object.__setattr__(self, '_module', module)
        return object.__getattribute__(self, '_module')

    def __getattr__(self, name: str) -> Any:
        return getattr(self._ensure_loaded(), name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._ensure_loaded(), name, value)

                                 

                                      
_license_module = _LazyModule('a')
_exceptions_module = _LazyModule('b')
_licensed_compiler_module = _LazyModule('e')
_utils_module = _LazyModule('f')
_version_checker_module = _LazyModule('s')
_conf_cfg_module = _LazyModule('o')
_designer_finder_module = _LazyModule('h')
_persistent_ib_module = _LazyModule('i')
_epf_compiler_module = _LazyModule('l')

                                         
class _ExportsNamespace:
                                     

    @property
    def LicenseManager(self):
        return _license_module.LicenseManager

    @property
    def get_license_manager(self):
        return _license_module.get_license_manager

    @property
    def LicenseError(self):
        return _exceptions_module.LicenseError

    @property
    def ActivationError(self):
        return _exceptions_module.ActivationError

    @property
    def VerificationError(self):
        return _exceptions_module.VerificationError

    @property
    def LicensedEPFCompiler(self):
        return _licensed_compiler_module.LicensedEPFCompiler

    @property
    def generate_uuid(self):
        return _utils_module.generate_uuid

_exports = _ExportsNamespace()

                                                                           
                                                 
def __getattr__(name: str) -> Any:
                                                    
    if name == 'LicenseManager':
        return _license_module.LicenseManager
    elif name == 'get_license_manager':
        return _license_module.get_license_manager
    elif name == 'LicenseError':
        return _exceptions_module.LicenseError
    elif name == 'ActivationError':
        return _exceptions_module.ActivationError
    elif name == 'VerificationError':
        return _exceptions_module.VerificationError
    elif name == 'LicensedEPFCompiler':
        return _licensed_compiler_module.LicensedEPFCompiler
    elif name == 'generate_uuid':
        return _utils_module.generate_uuid
    elif name == 'EXCEL_TO_MXL_AVAILABLE':
        return False                                         
    elif name == 'ExcelToMXLConverter':
        return None
    elif name == 'convert_excel_to_mxl':
        return None
    
    elif name == 'check_version_in_background':
        return _version_checker_module.check_version_in_background
    
    elif name == 'send_first_run_telemetry':
        return _license_module.send_first_run_telemetry
    elif name == 'run_setup_command':
        return _conf_cfg_module.run_setup_command
    elif name == 'DesignerFinder':
        return _designer_finder_module.DesignerFinder
    elif name == 'PersistentIBManager':
        return _persistent_ib_module.PersistentIBManager
    elif name == 'EPFCompiler':
        return _epf_compiler_module.EPFCompiler
    raise AttributeError(f"module 'pro' has no attribute '{name}'")

__all__ = [
                                     
    "LicenseManager",
    "get_license_manager",
    "LicenseError",
    "ActivationError",
    "VerificationError",
    
    "EXCEL_TO_MXL_AVAILABLE",
    "ExcelToMXLConverter",
    "convert_excel_to_mxl",
]
