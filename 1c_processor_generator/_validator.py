   

from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
import logging

                        
logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
                                           
    line: int
    column: int
    message: str
    severity: str                              
    module: str = "Unknown"                                  

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] Line {self.line}, Col {self.column}: {self.message}"


@dataclass
class ValidationResult:
                                        
    success: bool
    epf_path: Path

                
    error_count: int
    warning_count: int

                      
    errors: List[ValidationError]

                          
    elapsed_time: float           
    log_content: str
    log_file: Optional[Path] = None

    def __str__(self) -> str:
        if self.success:
            return f"✓ Validation passed ({self.elapsed_time:.1f}s)"
        else:
            return (f"✗ Validation failed: {self.error_count} errors, "
                   f"{self.warning_count} warnings ({self.elapsed_time:.1f}s)")


class EPFValidator:
           

    def __init__(self, platform_path: Optional[str] = None):
                   
        self.platform_path = platform_path
        self.validator_epf = Path(__file__).parent / "resources" / "validator.epf"
        logger.debug("EPFValidator initialized")

    def validate_epf(
        self,
        epf_path: Path,
        timeout: int = 60,
        keep_log: bool = False
    ) -> ValidationResult:
                   
        raise NotImplementedError(
            "EPF validation requires PRO license. "
            "Contact support for licensing options."
        )
