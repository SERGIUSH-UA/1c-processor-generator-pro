   

import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class SVGConversionError(Exception):
                                           
    pass


class SVGValidationError(Exception):
                                           
    pass


class SVGConverter:
                                                          

    def __init__(self):
                                                                 
        self._cairosvg_available = self._check_cairosvg()
        self._pillow_available = self._check_pillow()

        if not self._cairosvg_available and not self._pillow_available:
            logger.warning(
                "Neither cairosvg nor Pillow+svglib is available. "
                "SVG conversion will not work. Install with: pip install cairosvg Pillow"
            )

    def _check_cairosvg(self) -> bool:
                                             
        try:
            import cairosvg
            logger.debug("cairosvg library is available")
            return True
        except ImportError:
            logger.debug("cairosvg library is not available")
            return False
        except OSError as e:
                                                                                     
            logger.debug(f"cairosvg installed but cairo library not found: {e}")
            return False

    def _check_pillow(self) -> bool:
                                           
        try:
            from PIL import Image
            logger.debug("Pillow library is available")
            return True
        except ImportError:
            logger.debug("Pillow library is not available")
            return False

    def validate_svg(self, svg_path: str) -> bool:
                   
        svg_path = Path(svg_path)

                           
        if not svg_path.exists():
            raise SVGValidationError(f"SVG file not found: {svg_path}")

                              
        if svg_path.suffix.lower() != '.svg':
            raise SVGValidationError(
                f"Invalid file extension: {svg_path.suffix}. Expected .svg"
            )

                                 
        if svg_path.stat().st_size == 0:
            raise SVGValidationError(f"SVG file is empty: {svg_path}")

                             
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
        except ET.ParseError as e:
            raise SVGValidationError(f"Invalid SVG XML structure: {e}")

                                     
                                                
        if not (root.tag == 'svg' or root.tag.endswith('}svg')):
            raise SVGValidationError(
                f"Root element must be <svg>, found: {root.tag}"
            )

        logger.debug(f"SVG validation passed: {svg_path}")
        return True

    def get_svg_dimensions(self, svg_path: str) -> Tuple[Optional[int], Optional[int]]:
                   
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()

                                                
            width_str = root.get('width')
            height_str = root.get('height')

            if width_str and height_str:
                                                                
                width = int(''.join(filter(str.isdigit, width_str)))
                height = int(''.join(filter(str.isdigit, height_str)))
                return (width, height)

                                   
            viewbox = root.get('viewBox')
            if viewbox:
                parts = viewbox.split()
                if len(parts) == 4:
                    width = int(float(parts[2]))
                    height = int(float(parts[3]))
                    return (width, height)

        except Exception as e:
            logger.debug(f"Could not extract SVG dimensions: {e}")

        return (None, None)

    def convert_svg_to_png(
        self,
        svg_path: str,
        output_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        dpi: int = 96,
        background: str = 'transparent'
    ) -> str:
                   
                        
        self.validate_svg(svg_path)

                                        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

                                            
        if width is None and height is None:
            svg_width, svg_height = self.get_svg_dimensions(svg_path)
            if svg_width and svg_height:
                width, height = svg_width, svg_height
                logger.debug(f"Using SVG native dimensions: {width}x{height}")
            else:
                                                      
                width, height = 300, 300
                logger.debug(f"Using default dimensions: {width}x{height}")

                                             
        if self._cairosvg_available:
            try:
                return self._convert_with_cairosvg(
                    svg_path, output_path, width, height, dpi, background
                )
            except Exception as e:
                logger.warning(f"cairosvg conversion failed: {e}. Trying fallback...")

                                           
        if self._pillow_available:
            try:
                return self._convert_with_pillow(
                    svg_path, output_path, width, height
                )
            except Exception as e:
                logger.error(f"Pillow conversion failed: {e}")
                raise SVGConversionError(
                    f"All conversion methods failed. Last error: {e}"
                )

                                         
        raise SVGConversionError(
            "No SVG conversion library available. "
            "Install cairosvg or Pillow: pip install cairosvg Pillow"
        )

    def _convert_with_cairosvg(
        self,
        svg_path: str,
        output_path: Path,
        width: Optional[int],
        height: Optional[int],
        dpi: int,
        background: str
    ) -> str:
                                                 
        import cairosvg

        logger.debug(
            f"Converting {svg_path} → {output_path} "
            f"(size: {width}x{height}, dpi: {dpi})"
        )

                        
        kwargs = {
            'url': str(svg_path),
            'write_to': str(output_path),
            'dpi': dpi
        }

        if width:
            kwargs['output_width'] = width
        if height:
            kwargs['output_height'] = height

                             
        if background != 'transparent':
            kwargs['background'] = background

                 
        cairosvg.svg2png(**kwargs)

        logger.info(f"Successfully converted SVG to PNG: {output_path}")
        return str(output_path)

    def _convert_with_pillow(
        self,
        svg_path: str,
        output_path: Path,
        width: Optional[int],
        height: Optional[int]
    ) -> str:
                   
        from PIL import Image

                                             
                                                                                
        raise SVGConversionError(
            "Pillow-based SVG conversion not yet implemented. "
            "Please install cairosvg: pip install cairosvg"
        )

    def optimize_size(
        self,
        png_path: str,
        max_size_kb: int = 100,
        quality: int = 85
    ) -> int:
                   
        if not self._pillow_available:
            logger.warning("Pillow not available, skipping optimization")
            return Path(png_path).stat().st_size

        try:
            from PIL import Image

            png_path = Path(png_path)
            original_size = png_path.stat().st_size

                                                       
            if original_size <= max_size_kb * 1024:
                logger.debug(
                    f"PNG already under size limit: "
                    f"{original_size / 1024:.1f}KB <= {max_size_kb}KB"
                )
                return original_size

                               
            img = Image.open(png_path)

                                    
            img.save(
                png_path,
                'PNG',
                optimize=True,
                compress_level=9                       
            )

            new_size = png_path.stat().st_size
            reduction = (1 - new_size / original_size) * 100

            logger.info(
                f"Optimized PNG: {original_size / 1024:.1f}KB → "
                f"{new_size / 1024:.1f}KB ({reduction:.1f}% reduction)"
            )

            return new_size

        except Exception as e:
            logger.warning(f"PNG optimization failed: {e}")
                                             
            return Path(png_path).stat().st_size
