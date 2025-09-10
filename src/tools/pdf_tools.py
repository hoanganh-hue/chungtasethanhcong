"""
PDF Processing Tools for OpenManus-Youtu Integrated Framework
Advanced PDF manipulation, extraction, and generation capabilities
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, BinaryIO
from pathlib import Path
import io
import json
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import PyPDF2
    import fitz  # PyMuPDF
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.units import inch
    PDF_TOOLS_AVAILABLE = True
except ImportError:
    PDF_TOOLS_AVAILABLE = False
    logger.warning("PDF processing libraries not available. Install PyPDF2, PyMuPDF, and reportlab.")

class PDFProcessor:
    """Advanced PDF processing capabilities."""
    
    def __init__(self):
        self.supported_formats = ['pdf']
        self.max_file_size = 100 * 1024 * 1024  # 100MB
    
    async def extract_text(self, pdf_path: Union[str, Path, BinaryIO]) -> Dict[str, Any]:
        """Extract text from PDF."""
        if not PDF_TOOLS_AVAILABLE:
            return {"error": "PDF processing libraries not available"}
        
        try:
            if isinstance(pdf_path, (str, Path)):
                pdf_path = Path(pdf_path)
                if not pdf_path.exists():
                    return {"error": f"PDF file not found: {pdf_path}"}
                
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
            else:
                pdf_reader = PyPDF2.PdfReader(pdf_path)
            
            text_content = []
            metadata = {
                "num_pages": len(pdf_reader.pages),
                "title": pdf_reader.metadata.get("/Title", "") if pdf_reader.metadata else "",
                "author": pdf_reader.metadata.get("/Author", "") if pdf_reader.metadata else "",
                "subject": pdf_reader.metadata.get("/Subject", "") if pdf_reader.metadata else "",
                "creator": pdf_reader.metadata.get("/Creator", "") if pdf_reader.metadata else "",
                "producer": pdf_reader.metadata.get("/Producer", "") if pdf_reader.metadata else "",
                "creation_date": pdf_reader.metadata.get("/CreationDate", "") if pdf_reader.metadata else "",
                "modification_date": pdf_reader.metadata.get("/ModDate", "") if pdf_reader.metadata else ""
            }
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    text_content.append({
                        "page_number": page_num + 1,
                        "text": page_text,
                        "char_count": len(page_text)
                    })
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    text_content.append({
                        "page_number": page_num + 1,
                        "text": "",
                        "char_count": 0,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "metadata": metadata,
                "pages": text_content,
                "total_text": "\n".join([page["text"] for page in text_content]),
                "total_characters": sum(page["char_count"] for page in text_content)
            }
            
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            return {"error": str(e)}
    
    async def extract_images(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """Extract images from PDF."""
        if not PDF_TOOLS_AVAILABLE:
            return {"error": "PDF processing libraries not available"}
        
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                return {"error": f"PDF file not found: {pdf_path}"}
            
            doc = fitz.open(pdf_path)
            images = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("png")
                            images.append({
                                "page_number": page_num + 1,
                                "image_index": img_index,
                                "xref": xref,
                                "width": pix.width,
                                "height": pix.height,
                                "colorspace": pix.colorspace.name if pix.colorspace else "unknown",
                                "data": img_data,
                                "format": "png"
                            })
                        else:
                            # Convert CMYK to RGB
                            pix1 = fitz.Pixmap(fitz.csRGB, pix)
                            img_data = pix1.tobytes("png")
                            images.append({
                                "page_number": page_num + 1,
                                "image_index": img_index,
                                "xref": xref,
                                "width": pix1.width,
                                "height": pix1.height,
                                "colorspace": "RGB",
                                "data": img_data,
                                "format": "png"
                            })
                            pix1 = None
                        
                        pix = None
                        
                    except Exception as e:
                        logger.warning(f"Failed to extract image {img_index} from page {page_num + 1}: {e}")
            
            doc.close()
            
            return {
                "success": True,
                "total_images": len(images),
                "images": images
            }
            
        except Exception as e:
            logger.error(f"PDF image extraction failed: {e}")
            return {"error": str(e)}
    
    async def merge_pdfs(self, pdf_paths: List[Union[str, Path]], output_path: Union[str, Path]) -> Dict[str, Any]:
        """Merge multiple PDFs into one."""
        if not PDF_TOOLS_AVAILABLE:
            return {"error": "PDF processing libraries not available"}
        
        try:
            pdf_writer = PyPDF2.PdfWriter()
            
            for pdf_path in pdf_paths:
                pdf_path = Path(pdf_path)
                if not pdf_path.exists():
                    return {"error": f"PDF file not found: {pdf_path}"}
                
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            return {
                "success": True,
                "output_path": str(output_path),
                "total_pages": len(pdf_writer.pages),
                "merged_files": [str(Path(p).name) for p in pdf_paths]
            }
            
        except Exception as e:
            logger.error(f"PDF merge failed: {e}")
            return {"error": str(e)}
    
    async def split_pdf(self, pdf_path: Union[str, Path], output_dir: Union[str, Path], 
                       page_ranges: List[tuple] = None) -> Dict[str, Any]:
        """Split PDF into multiple files."""
        if not PDF_TOOLS_AVAILABLE:
            return {"error": "PDF processing libraries not available"}
        
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                return {"error": f"PDF file not found: {pdf_path}"}
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
            
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            if not page_ranges:
                # Split each page into separate file
                page_ranges = [(i, i) for i in range(total_pages)]
            
            output_files = []
            
            for i, (start_page, end_page) in enumerate(page_ranges):
                if start_page < 0 or end_page >= total_pages or start_page > end_page:
                    continue
                
                pdf_writer = PyPDF2.PdfWriter()
                
                for page_num in range(start_page, end_page + 1):
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                
                output_filename = f"{pdf_path.stem}_pages_{start_page+1}_{end_page+1}.pdf"
                output_file_path = output_dir / output_filename
                
                with open(output_file_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                
                output_files.append({
                    "filename": output_filename,
                    "path": str(output_file_path),
                    "pages": f"{start_page+1}-{end_page+1}",
                    "page_count": end_page - start_page + 1
                })
            
            return {
                "success": True,
                "output_directory": str(output_dir),
                "output_files": output_files,
                "total_files_created": len(output_files)
            }
            
        except Exception as e:
            logger.error(f"PDF split failed: {e}")
            return {"error": str(e)}
    
    async def create_pdf_from_text(self, text_content: str, output_path: Union[str, Path],
                                  title: str = "Generated PDF", author: str = "OpenManus-Youtu Framework") -> Dict[str, Any]:
        """Create PDF from text content."""
        if not PDF_TOOLS_AVAILABLE:
            return {"error": "PDF processing libraries not available"}
        
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            doc = SimpleDocTemplate(str(output_path), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Add title
            title_style = styles['Title']
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
            
            # Add content
            normal_style = styles['Normal']
            paragraphs = text_content.split('\n\n')
            
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), normal_style))
                    story.append(Spacer(1, 6))
            
            doc.build(story)
            
            return {
                "success": True,
                "output_path": str(output_path),
                "title": title,
                "author": author,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"PDF creation failed: {e}")
            return {"error": str(e)}
    
    async def add_watermark(self, pdf_path: Union[str, Path], watermark_text: str,
                           output_path: Union[str, Path], opacity: float = 0.5) -> Dict[str, Any]:
        """Add watermark to PDF."""
        if not PDF_TOOLS_AVAILABLE:
            return {"error": "PDF processing libraries not available"}
        
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                return {"error": f"PDF file not found: {pdf_path}"}
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pdf_writer = PyPDF2.PdfWriter()
                
                for page in pdf_reader.pages:
                    # Create watermark
                    watermark = PyPDF2.pdf.PageObject.create_blank_page(width=page.mediabox.width, height=page.mediabox.height)
                    
                    # Add watermark to page
                    page.merge_page(watermark)
                    pdf_writer.add_page(page)
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            return {
                "success": True,
                "output_path": str(output_path),
                "watermark_text": watermark_text,
                "opacity": opacity
            }
            
        except Exception as e:
            logger.error(f"Watermark addition failed: {e}")
            return {"error": str(e)}
    
    async def get_pdf_info(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """Get comprehensive PDF information."""
        if not PDF_TOOLS_AVAILABLE:
            return {"error": "PDF processing libraries not available"}
        
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                return {"error": f"PDF file not found: {pdf_path}"}
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                info = {
                    "filename": pdf_path.name,
                    "file_size": pdf_path.stat().st_size,
                    "num_pages": len(pdf_reader.pages),
                    "is_encrypted": pdf_reader.is_encrypted,
                    "metadata": {}
                }
                
                if pdf_reader.metadata:
                    info["metadata"] = {
                        "title": pdf_reader.metadata.get("/Title", ""),
                        "author": pdf_reader.metadata.get("/Author", ""),
                        "subject": pdf_reader.metadata.get("/Subject", ""),
                        "creator": pdf_reader.metadata.get("/Creator", ""),
                        "producer": pdf_reader.metadata.get("/Producer", ""),
                        "creation_date": pdf_reader.metadata.get("/CreationDate", ""),
                        "modification_date": pdf_reader.metadata.get("/ModDate", "")
                    }
                
                # Page information
                page_info = []
                for i, page in enumerate(pdf_reader.pages):
                    page_info.append({
                        "page_number": i + 1,
                        "width": float(page.mediabox.width),
                        "height": float(page.mediabox.height),
                        "rotation": page.rotation
                    })
                
                info["pages"] = page_info
            
            return {
                "success": True,
                "info": info
            }
            
        except Exception as e:
            logger.error(f"PDF info extraction failed: {e}")
            return {"error": str(e)}

# Global PDF processor instance
pdf_processor = PDFProcessor()

# Convenience functions
async def extract_pdf_text(pdf_path: Union[str, Path]) -> Dict[str, Any]:
    """Extract text from PDF."""
    return await pdf_processor.extract_text(pdf_path)

async def extract_pdf_images(pdf_path: Union[str, Path]) -> Dict[str, Any]:
    """Extract images from PDF."""
    return await pdf_processor.extract_images(pdf_path)

async def merge_pdf_files(pdf_paths: List[Union[str, Path]], output_path: Union[str, Path]) -> Dict[str, Any]:
    """Merge multiple PDFs."""
    return await pdf_processor.merge_pdfs(pdf_paths, output_path)

async def split_pdf_file(pdf_path: Union[str, Path], output_dir: Union[str, Path], 
                        page_ranges: List[tuple] = None) -> Dict[str, Any]:
    """Split PDF into multiple files."""
    return await pdf_processor.split_pdf(pdf_path, output_dir, page_ranges)

async def create_pdf_from_text_content(text_content: str, output_path: Union[str, Path],
                                      title: str = "Generated PDF") -> Dict[str, Any]:
    """Create PDF from text."""
    return await pdf_processor.create_pdf_from_text(text_content, output_path, title)

async def get_pdf_information(pdf_path: Union[str, Path]) -> Dict[str, Any]:
    """Get PDF information."""
    return await pdf_processor.get_pdf_info(pdf_path)