"""
Image Processing Tools for OpenManus-Youtu Integrated Framework
Advanced image manipulation, analysis, and conversion capabilities
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, BinaryIO, Tuple
from pathlib import Path
import io
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw, ImageFont
    import numpy as np
    from PIL.ExifTags import TAGS
    IMAGE_TOOLS_AVAILABLE = True
except ImportError:
    IMAGE_TOOLS_AVAILABLE = False
    logger.warning("Image processing libraries not available. Install Pillow and numpy.")

class ImageProcessor:
    """Advanced image processing capabilities."""
    
    def __init__(self):
        self.supported_formats = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.max_dimensions = (10000, 10000)  # Max width/height
    
    async def resize_image(self, image_path: Union[str, Path], output_path: Union[str, Path],
                          size: Tuple[int, int], maintain_aspect: bool = True,
                          quality: int = 95) -> Dict[str, Any]:
        """Resize image with optional aspect ratio maintenance."""
        if not IMAGE_TOOLS_AVAILABLE:
            return {"error": "Image processing libraries not available"}
        
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                return {"error": f"Image file not found: {image_path}"}
            
            with Image.open(image_path) as img:
                original_size = img.size
                
                if maintain_aspect:
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                    new_size = img.size
                else:
                    img = img.resize(size, Image.Resampling.LANCZOS)
                    new_size = size
                
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save with appropriate format
                if output_path.suffix.lower() in ['.jpg', '.jpeg']:
                    img = img.convert('RGB')
                    img.save(output_path, 'JPEG', quality=quality)
                else:
                    img.save(output_path)
                
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "original_size": original_size,
                    "new_size": new_size,
                    "maintained_aspect": maintain_aspect
                }
                
        except Exception as e:
            logger.error(f"Image resize failed: {e}")
            return {"error": str(e)}
    
    async def convert_format(self, image_path: Union[str, Path], output_path: Union[str, Path],
                            output_format: str, quality: int = 95) -> Dict[str, Any]:
        """Convert image to different format."""
        if not IMAGE_TOOLS_AVAILABLE:
            return {"error": "Image processing libraries not available"}
        
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                return {"error": f"Image file not found: {image_path}"}
            
            with Image.open(image_path) as img:
                original_format = img.format
                
                # Convert to RGB for JPEG
                if output_format.upper() in ['JPG', 'JPEG']:
                    img = img.convert('RGB')
                
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save in new format
                if output_format.upper() in ['JPG', 'JPEG']:
                    img.save(output_path, 'JPEG', quality=quality)
                else:
                    img.save(output_path, output_format.upper())
                
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "original_format": original_format,
                    "new_format": output_format.upper()
                }
                
        except Exception as e:
            logger.error(f"Image format conversion failed: {e}")
            return {"error": str(e)}
    
    async def apply_filters(self, image_path: Union[str, Path], output_path: Union[str, Path],
                           filters: List[str]) -> Dict[str, Any]:
        """Apply various filters to image."""
        if not IMAGE_TOOLS_AVAILABLE:
            return {"error": "Image processing libraries not available"}
        
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                return {"error": f"Image file not found: {image_path}"}
            
            with Image.open(image_path) as img:
                applied_filters = []
                
                for filter_name in filters:
                    filter_name = filter_name.lower()
                    
                    if filter_name == 'blur':
                        img = img.filter(ImageFilter.BLUR)
                        applied_filters.append('blur')
                    elif filter_name == 'sharpen':
                        img = img.filter(ImageFilter.SHARPEN)
                        applied_filters.append('sharpen')
                    elif filter_name == 'edge_enhance':
                        img = img.filter(ImageFilter.EDGE_ENHANCE)
                        applied_filters.append('edge_enhance')
                    elif filter_name == 'emboss':
                        img = img.filter(ImageFilter.EMBOSS)
                        applied_filters.append('emboss')
                    elif filter_name == 'contour':
                        img = img.filter(ImageFilter.CONTOUR)
                        applied_filters.append('contour')
                    elif filter_name == 'grayscale':
                        img = ImageOps.grayscale(img)
                        applied_filters.append('grayscale')
                    elif filter_name == 'invert':
                        img = ImageOps.invert(img)
                        applied_filters.append('invert')
                    elif filter_name == 'mirror':
                        img = ImageOps.mirror(img)
                        applied_filters.append('mirror')
                    elif filter_name == 'flip':
                        img = ImageOps.flip(img)
                        applied_filters.append('flip')
                
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                img.save(output_path)
                
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "applied_filters": applied_filters
                }
                
        except Exception as e:
            logger.error(f"Image filter application failed: {e}")
            return {"error": str(e)}
    
    async def adjust_brightness_contrast(self, image_path: Union[str, Path], output_path: Union[str, Path],
                                       brightness: float = 1.0, contrast: float = 1.0,
                                       saturation: float = 1.0) -> Dict[str, Any]:
        """Adjust brightness, contrast, and saturation."""
        if not IMAGE_TOOLS_AVAILABLE:
            return {"error": "Image processing libraries not available"}
        
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                return {"error": f"Image file not found: {image_path}"}
            
            with Image.open(image_path) as img:
                # Adjust brightness
                if brightness != 1.0:
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(brightness)
                
                # Adjust contrast
                if contrast != 1.0:
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(contrast)
                
                # Adjust saturation (only for RGB images)
                if saturation != 1.0 and img.mode == 'RGB':
                    enhancer = ImageEnhance.Color(img)
                    img = enhancer.enhance(saturation)
                
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                img.save(output_path)
                
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "brightness": brightness,
                    "contrast": contrast,
                    "saturation": saturation
                }
                
        except Exception as e:
            logger.error(f"Image adjustment failed: {e}")
            return {"error": str(e)}
    
    async def crop_image(self, image_path: Union[str, Path], output_path: Union[str, Path],
                        crop_box: Tuple[int, int, int, int]) -> Dict[str, Any]:
        """Crop image to specified box."""
        if not IMAGE_TOOLS_AVAILABLE:
            return {"error": "Image processing libraries not available"}
        
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                return {"error": f"Image file not found: {image_path}"}
            
            with Image.open(image_path) as img:
                original_size = img.size
                
                # Validate crop box
                left, top, right, bottom = crop_box
                if (left < 0 or top < 0 or right > original_size[0] or bottom > original_size[1] or
                    left >= right or top >= bottom):
                    return {"error": "Invalid crop box coordinates"}
                
                cropped_img = img.crop(crop_box)
                
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                cropped_img.save(output_path)
                
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "original_size": original_size,
                    "crop_box": crop_box,
                    "cropped_size": cropped_img.size
                }
                
        except Exception as e:
            logger.error(f"Image crop failed: {e}")
            return {"error": str(e)}
    
    async def add_text_watermark(self, image_path: Union[str, Path], output_path: Union[str, Path],
                                text: str, position: Tuple[int, int] = (10, 10),
                                font_size: int = 20, color: str = "white",
                                opacity: int = 128) -> Dict[str, Any]:
        """Add text watermark to image."""
        if not IMAGE_TOOLS_AVAILABLE:
            return {"error": "Image processing libraries not available"}
        
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                return {"error": f"Image file not found: {image_path}"}
            
            with Image.open(image_path) as img:
                # Create a copy for watermarking
                watermarked = img.copy()
                
                # Create drawing context
                draw = ImageDraw.Draw(watermarked)
                
                # Try to load a font, fallback to default
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                # Add text with specified color and opacity
                draw.text(position, text, fill=color, font=font)
                
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                watermarked.save(output_path)
                
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "watermark_text": text,
                    "position": position,
                    "font_size": font_size,
                    "color": color
                }
                
        except Exception as e:
            logger.error(f"Text watermark addition failed: {e}")
            return {"error": str(e)}
    
    async def get_image_info(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """Get comprehensive image information."""
        if not IMAGE_TOOLS_AVAILABLE:
            return {"error": "Image processing libraries not available"}
        
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                return {"error": f"Image file not found: {image_path}"}
            
            with Image.open(image_path) as img:
                info = {
                    "filename": image_path.name,
                    "file_size": image_path.stat().st_size,
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                    "exif_data": {}
                }
                
                # Extract EXIF data
                if hasattr(img, '_getexif') and img._getexif() is not None:
                    exif_data = {}
                    for tag_id, value in img._getexif().items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                    info["exif_data"] = exif_data
                
                # Color palette info
                if img.mode == 'P':
                    info["palette"] = {
                        "colors": len(img.getcolors(maxcolors=256*256*256)),
                        "palette_size": len(img.palette.getdata()[1]) // 3
                    }
                
                return {
                    "success": True,
                    "info": info
                }
                
        except Exception as e:
            logger.error(f"Image info extraction failed: {e}")
            return {"error": str(e)}
    
    async def create_thumbnail(self, image_path: Union[str, Path], output_path: Union[str, Path],
                              size: Tuple[int, int] = (128, 128), quality: int = 95) -> Dict[str, Any]:
        """Create thumbnail of image."""
        if not IMAGE_TOOLS_AVAILABLE:
            return {"error": "Image processing libraries not available"}
        
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                return {"error": f"Image file not found: {image_path}"}
            
            with Image.open(image_path) as img:
                # Create thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save thumbnail
                if output_path.suffix.lower() in ['.jpg', '.jpeg']:
                    img = img.convert('RGB')
                    img.save(output_path, 'JPEG', quality=quality)
                else:
                    img.save(output_path)
                
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "thumbnail_size": img.size,
                    "original_size": Image.open(image_path).size
                }
                
        except Exception as e:
            logger.error(f"Thumbnail creation failed: {e}")
            return {"error": str(e)}
    
    async def batch_process(self, image_paths: List[Union[str, Path]], 
                           operation: str, **kwargs) -> Dict[str, Any]:
        """Batch process multiple images."""
        if not IMAGE_TOOLS_AVAILABLE:
            return {"error": "Image processing libraries not available"}
        
        try:
            results = []
            successful = 0
            failed = 0
            
            for image_path in image_paths:
                try:
                    if operation == "resize":
                        result = await self.resize_image(image_path, **kwargs)
                    elif operation == "convert":
                        result = await self.convert_format(image_path, **kwargs)
                    elif operation == "filters":
                        result = await self.apply_filters(image_path, **kwargs)
                    elif operation == "adjust":
                        result = await self.adjust_brightness_contrast(image_path, **kwargs)
                    elif operation == "crop":
                        result = await self.crop_image(image_path, **kwargs)
                    elif operation == "thumbnail":
                        result = await self.create_thumbnail(image_path, **kwargs)
                    else:
                        result = {"error": f"Unknown operation: {operation}"}
                    
                    if result.get("success"):
                        successful += 1
                    else:
                        failed += 1
                    
                    results.append({
                        "image_path": str(image_path),
                        "result": result
                    })
                    
                except Exception as e:
                    failed += 1
                    results.append({
                        "image_path": str(image_path),
                        "result": {"error": str(e)}
                    })
            
            return {
                "success": True,
                "operation": operation,
                "total_images": len(image_paths),
                "successful": successful,
                "failed": failed,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return {"error": str(e)}

# Global image processor instance
image_processor = ImageProcessor()

# Convenience functions
async def resize_image_file(image_path: Union[str, Path], output_path: Union[str, Path],
                           size: Tuple[int, int], maintain_aspect: bool = True) -> Dict[str, Any]:
    """Resize image."""
    return await image_processor.resize_image(image_path, output_path, size, maintain_aspect)

async def convert_image_format(image_path: Union[str, Path], output_path: Union[str, Path],
                              output_format: str) -> Dict[str, Any]:
    """Convert image format."""
    return await image_processor.convert_format(image_path, output_path, output_format)

async def apply_image_filters(image_path: Union[str, Path], output_path: Union[str, Path],
                             filters: List[str]) -> Dict[str, Any]:
    """Apply filters to image."""
    return await image_processor.apply_filters(image_path, output_path, filters)

async def get_image_information(image_path: Union[str, Path]) -> Dict[str, Any]:
    """Get image information."""
    return await image_processor.get_image_info(image_path)

async def create_image_thumbnail(image_path: Union[str, Path], output_path: Union[str, Path],
                                size: Tuple[int, int] = (128, 128)) -> Dict[str, Any]:
    """Create image thumbnail."""
    return await image_processor.create_thumbnail(image_path, output_path, size)