"""
Document Processing Service
Handles parsing, chunking, and preprocessing of documents for RAG.
"""

import hashlib
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import re

import PyPDF2
from docx import Document

from ..config.settings import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Document processing and chunking service."""
    
    def __init__(self):
        self.chunk_size = settings.MAX_CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    def extract_text_from_pdf(self, file_content: bytes) -> Dict[str, Any]:
        """Extract text from PDF content."""
        try:
            from io import BytesIO
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            
            text_content = []
            metadata = {
                "total_pages": len(pdf_reader.pages),
                "title": pdf_reader.metadata.title if pdf_reader.metadata else None,
                "author": pdf_reader.metadata.author if pdf_reader.metadata else None
            }
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text_content.append({
                        "page": page_num + 1,
                        "text": page_text
                    })
            
            return {
                "text_content": text_content,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise
    
    def extract_text_from_docx(self, file_content: bytes) -> Dict[str, Any]:
        """Extract text from DOCX content."""
        try:
            from io import BytesIO
            doc = Document(BytesIO(file_content))
            
            text_content = []
            paragraphs = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraphs.append(paragraph.text)
            
            # Combine paragraphs into sections
            full_text = "\n".join(paragraphs)
            text_content.append({
                "page": 1,
                "text": full_text
            })
            
            metadata = {
                "total_pages": 1,
                "paragraph_count": len(paragraphs),
                "word_count": len(full_text.split())
            }
            
            return {
                "text_content": text_content,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to extract text from DOCX: {str(e)}")
            raise
    
    def extract_text_from_txt(self, file_content: bytes) -> Dict[str, Any]:
        """Extract text from plain text content."""
        try:
            text = file_content.decode('utf-8')
            
            text_content = [{
                "page": 1,
                "text": text
            }]
            
            metadata = {
                "total_pages": 1,
                "char_count": len(text),
                "word_count": len(text.split()),
                "line_count": len(text.splitlines())
            }
            
            return {
                "text_content": text_content,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to extract text from TXT: {str(e)}")
            raise
    
    def process_document(self, file_content: bytes, filename: str, file_type: str) -> Dict[str, Any]:
        """Process document and extract text based on file type."""
        logger.info(f"Processing document: {filename} (type: {file_type})")
        
        try:
            if file_type.lower() == 'pdf' or filename.lower().endswith('.pdf'):
                return self.extract_text_from_pdf(file_content)
            elif file_type.lower() in ['doc', 'docx'] or filename.lower().endswith(('.doc', '.docx')):
                return self.extract_text_from_docx(file_content)
            elif file_type.lower() == 'txt' or filename.lower().endswith('.txt'):
                return self.extract_text_from_txt(file_content)
            else:
                # Try to decode as text first
                try:
                    return self.extract_text_from_txt(file_content)
                except:
                    raise ValueError(f"Unsupported file type: {file_type}")
            
        except Exception as e:
            logger.error(f"Failed to process document {filename}: {str(e)}")
            raise
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text content."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.,!?;:()\-\'""]', ' ', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
    
    def create_chunks(self, text_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create semantic chunks from extracted text."""
        chunks = []
        
        for content in text_content:
            page_num = content.get("page", 1)
            text = self.clean_text(content["text"])
            
            if not text:
                continue
            
            # Split into sentences for better chunking
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            current_chunk = ""
            current_chunk_sentences = []
            
            for sentence in sentences:
                # Check if adding this sentence would exceed chunk size
                if len(current_chunk + " " + sentence) > self.chunk_size and current_chunk:
                    # Save current chunk
                    chunk_text = current_chunk.strip()
                    if chunk_text:
                        chunks.append({
                            "text": chunk_text,
                            "text_hash": self.generate_text_hash(chunk_text),
                            "page": page_num,
                            "sentence_count": len(current_chunk_sentences),
                            "char_count": len(chunk_text),
                            "word_count": len(chunk_text.split())
                        })
                    
                    # Start new chunk with overlap
                    if self.chunk_overlap > 0 and current_chunk_sentences:
                        overlap_sentences = current_chunk_sentences[-min(2, len(current_chunk_sentences)):]
                        current_chunk = " ".join(overlap_sentences)
                        current_chunk_sentences = overlap_sentences[:]
                    else:
                        current_chunk = ""
                        current_chunk_sentences = []
                
                # Add current sentence
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                current_chunk_sentences.append(sentence)
            
            # Add final chunk if there's remaining content
            if current_chunk.strip():
                chunk_text = current_chunk.strip()
                chunks.append({
                    "text": chunk_text,
                    "text_hash": self.generate_text_hash(chunk_text),
                    "page": page_num,
                    "sentence_count": len(current_chunk_sentences),
                    "char_count": len(chunk_text),
                    "word_count": len(chunk_text.split())
                })
        
        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks
    
    def generate_text_hash(self, text: str) -> str:
        """Generate SHA256 hash for text content."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def generate_document_hash(self, file_content: bytes) -> str:
        """Generate SHA256 hash for document content."""
        return hashlib.sha256(file_content).hexdigest()
    
    def validate_document(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Validate document size and format."""
        max_size = 50 * 1024 * 1024  # 50MB
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "file_size": len(file_content),
            "filename": filename
        }
        
        # Check file size
        if len(file_content) > max_size:
            validation_result["valid"] = False
            validation_result["errors"].append(f"File size ({len(file_content)} bytes) exceeds maximum allowed size ({max_size} bytes)")
        
        # Check if file is empty
        if len(file_content) == 0:
            validation_result["valid"] = False
            validation_result["errors"].append("File is empty")
        
        # Check filename
        if not filename or len(filename.strip()) == 0:
            validation_result["valid"] = False
            validation_result["errors"].append("Filename is required")
        
        # Check for supported extensions
        supported_extensions = ['.pdf', '.doc', '.docx', '.txt', '.md']
        if not any(filename.lower().endswith(ext) for ext in supported_extensions):
            validation_result["valid"] = False
            validation_result["errors"].append(f"Unsupported file type. Supported: {', '.join(supported_extensions)}")
        
        return validation_result
    
    def extract_document_metadata(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extract comprehensive document metadata."""
        metadata = {
            'filename': filename,
            'file_size': len(file_content),
            'file_hash': self.generate_document_hash(file_content),
        }
        
        # Detect file type
        file_ext = Path(filename).suffix.lower()
        if file_ext in ['.pdf']:
            metadata['file_type'] = 'PDF'
        elif file_ext in ['.doc', '.docx']:
            metadata['file_type'] = 'DOCX'
        elif file_ext in ['.txt']:
            metadata['file_type'] = 'TXT'
        elif file_ext in ['.md']:
            metadata['file_type'] = 'MARKDOWN'
        else:
            metadata['file_type'] = 'UNKNOWN'
        
        try:
            # Process document to get additional metadata
            document_data = self.process_document(file_content, filename, metadata['file_type'])
            if 'metadata' in document_data:
                metadata.update(document_data['metadata'])
                
            # Add text content length info
            if 'text_content' in document_data:
                total_text = ' '.join([content['text'] for content in document_data['text_content']])
                metadata['total_words'] = len(total_text.split())
                metadata['total_chars'] = len(total_text)
                
        except Exception as e:
            logger.error(f"Failed to extract extended metadata: {str(e)}")
            # Continue with basic metadata
        
        return metadata
    
    async def process_document_async(self, file_content: bytes, filename: str, user_id: str) -> Dict[str, Any]:
        """Async wrapper for document processing with full workflow."""
        try:
            # Validate document
            validation = self.validate_document(file_content, filename)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': 'Validation failed',
                    'validation_errors': validation['errors']
                }
            
            # Extract metadata
            metadata = self.extract_document_metadata(file_content, filename)
            
            # Process document content
            document_data = self.process_document(file_content, filename, metadata['file_type'])
            
            # Create chunks
            chunks = self.create_chunks(document_data['text_content'])
            
            return {
                'success': True,
                'metadata': metadata,
                'text_content': document_data['text_content'],
                'chunks': chunks,
                'validation': validation
            }
            
        except Exception as e:
            logger.error(f"Document processing failed for {filename}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# Global document processor instance
document_processor = DocumentProcessor()