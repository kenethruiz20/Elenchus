"""
Content Extraction Service
Extracts text content from various document formats for AI processing.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import io

logger = logging.getLogger(__name__)


class ContentExtractor:
    """Service for extracting text content from various document formats."""
    
    def __init__(self):
        self.supported_formats = {
            '.txt': self._extract_text,
            '.pdf': self._extract_pdf,
            '.docx': self._extract_docx,
            '.doc': self._extract_doc,
            '.csv': self._extract_csv,
        }
    
    def can_extract(self, filename: str) -> bool:
        """Check if file format is supported for content extraction."""
        file_ext = Path(filename).suffix.lower()
        return file_ext in self.supported_formats
    
    async def extract_content(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract text content from file.
        
        Args:
            file_content: Raw file bytes
            filename: Original filename with extension
        
        Returns:
            Dict with extracted content and metadata
        """
        try:
            file_ext = Path(filename).suffix.lower()
            
            if file_ext not in self.supported_formats:
                return {
                    'success': False,
                    'error': f'Unsupported file format: {file_ext}',
                    'text_content': None,
                    'metadata': {}
                }
            
            # Call appropriate extraction method
            extractor = self.supported_formats[file_ext]
            result = await extractor(file_content, filename)
            
            return {
                'success': True,
                'text_content': result['text'],
                'metadata': result.get('metadata', {}),
                'format': file_ext,
                'char_count': len(result['text']) if result['text'] else 0
            }
            
        except Exception as e:
            logger.error(f"Content extraction failed for {filename}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text_content': None,
                'metadata': {}
            }
    
    async def _extract_text(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extract content from plain text files."""
        try:
            text = file_content.decode('utf-8')
            return {
                'text': text,
                'metadata': {
                    'encoding': 'utf-8',
                    'lines': len(text.split('\n'))
                }
            }
        except UnicodeDecodeError:
            # Try other encodings
            for encoding in ['latin-1', 'cp1252']:
                try:
                    text = file_content.decode(encoding)
                    return {
                        'text': text,
                        'metadata': {
                            'encoding': encoding,
                            'lines': len(text.split('\n'))
                        }
                    }
                except UnicodeDecodeError:
                    continue
            
            raise Exception("Unable to decode text file")
    
    async def _extract_pdf(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extract text from PDF files."""
        try:
            import PyPDF2
            
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_parts = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_parts.append(page_text)
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {str(e)}")
            
            full_text = '\n\n'.join(text_parts)
            
            return {
                'text': full_text,
                'metadata': {
                    'pages': len(pdf_reader.pages),
                    'pages_extracted': len(text_parts),
                    'title': pdf_reader.metadata.get('/Title') if pdf_reader.metadata else None,
                    'author': pdf_reader.metadata.get('/Author') if pdf_reader.metadata else None,
                }
            }
            
        except ImportError:
            raise Exception("PyPDF2 not installed - cannot extract PDF content")
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    async def _extract_docx(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extract text from DOCX files."""
        try:
            import python_docx
            from python_docx import Document
            
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)
            
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            # Extract from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        text_parts.append(' | '.join(row_text))
            
            full_text = '\n\n'.join(text_parts)
            
            # Extract document properties
            core_props = doc.core_properties
            
            return {
                'text': full_text,
                'metadata': {
                    'paragraphs': len(doc.paragraphs),
                    'tables': len(doc.tables),
                    'title': core_props.title if hasattr(core_props, 'title') else None,
                    'author': core_props.author if hasattr(core_props, 'author') else None,
                    'subject': core_props.subject if hasattr(core_props, 'subject') else None,
                }
            }
            
        except ImportError:
            raise Exception("python-docx not installed - cannot extract DOCX content")
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {str(e)}")
    
    async def _extract_doc(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extract text from DOC files."""
        # For now, return error as DOC extraction requires more complex libraries
        raise Exception("DOC format extraction not yet implemented - please convert to DOCX")
    
    async def _extract_csv(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extract content from CSV files."""
        try:
            import csv
            import io
            
            # Try to decode the CSV
            try:
                text_data = file_content.decode('utf-8')
            except UnicodeDecodeError:
                text_data = file_content.decode('latin-1')
            
            csv_file = io.StringIO(text_data)
            
            # Detect delimiter
            sample = text_data[:1024]
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            csv_file.seek(0)
            reader = csv.reader(csv_file, delimiter=delimiter)
            
            rows = list(reader)
            
            if not rows:
                return {
                    'text': '',
                    'metadata': {'rows': 0, 'columns': 0}
                }
            
            # Format as readable text
            headers = rows[0] if rows else []
            data_rows = rows[1:] if len(rows) > 1 else []
            
            text_parts = []
            
            if headers:
                text_parts.append("Headers: " + " | ".join(headers))
                text_parts.append("=" * 50)
            
            # Include first few rows as sample
            sample_rows = data_rows[:10]  # First 10 rows
            for i, row in enumerate(sample_rows):
                if len(row) == len(headers):
                    row_text = []
                    for j, cell in enumerate(row):
                        if j < len(headers):
                            row_text.append(f"{headers[j]}: {cell}")
                        else:
                            row_text.append(cell)
                    text_parts.append(f"Row {i+1}: " + " | ".join(row_text))
                else:
                    text_parts.append(f"Row {i+1}: " + " | ".join(row))
            
            if len(data_rows) > 10:
                text_parts.append(f"\n... and {len(data_rows) - 10} more rows")
            
            full_text = '\n'.join(text_parts)
            
            return {
                'text': full_text,
                'metadata': {
                    'rows': len(rows),
                    'columns': len(headers),
                    'headers': headers,
                    'delimiter': delimiter,
                    'sample_rows_shown': min(10, len(data_rows))
                }
            }
            
        except Exception as e:
            raise Exception(f"CSV extraction failed: {str(e)}")


# Global instance
content_extractor = ContentExtractor()