"""
Document AI Service
Uses Gemini AI to generate descriptions and extract topics from documents.
"""

import logging
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentAIService:
    """Service for AI-powered document analysis using Gemini."""
    
    def __init__(self):
        self.max_content_length = 30000  # Limit content sent to AI
        self.initialized = False
        self.gemini_service = None
        self.default_model = None
    
    async def initialize(self) -> bool:
        """Initialize the Gemini AI service."""
        try:
            # Import the model router
            from app.services.model_router import model_router
            
            # Check if any Gemini models are available
            available_models = model_router.get_available_models()
            gemini_models = [model for model in available_models if model.startswith('gemini')]
            
            if gemini_models:
                self.gemini_service = model_router
                self.default_model = gemini_models[0]  # Use first available Gemini model
                self.initialized = True
                logger.info(f"Document AI service initialized with model: {self.default_model}")
                return True
            else:
                logger.warning("No Gemini models available in model router")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Document AI service: {str(e)}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if service is initialized."""
        return self.initialized and self.gemini_service is not None
    
    async def generate_document_metadata(
        self, 
        text_content: str, 
        filename: str, 
        file_type: str = None
    ) -> Dict[str, Any]:
        """
        Generate AI metadata for a document.
        
        Args:
            text_content: Extracted text from document
            filename: Original filename
            file_type: File extension/type
        
        Returns:
            Dict with AI-generated summary, description, and topics
        """
        if not self.is_initialized():
            logger.error("Document AI service not initialized")
            return {
                'success': False,
                'error': 'AI service not available',
                'ai_summary': None,
                'ai_detailed_description': None,
                'ai_topics': []
            }
        
        try:
            # Truncate content if too long
            truncated_content = self._truncate_content(text_content)
            
            # Create the prompt
            prompt = self._create_analysis_prompt(truncated_content, filename, file_type)
            
            # Call Gemini AI
            response = await self._call_gemini(prompt)
            
            if response['success']:
                # Parse the AI response
                parsed = self._parse_ai_response(response['content'])
                
                return {
                    'success': True,
                    'ai_summary': parsed['summary'],
                    'ai_detailed_description': parsed['detailed_description'],
                    'ai_topics': parsed['topics'],
                    'generated_at': datetime.utcnow(),
                    'content_length': len(truncated_content),
                    'was_truncated': len(text_content) > self.max_content_length
                }
            else:
                return {
                    'success': False,
                    'error': response.get('error', 'AI processing failed'),
                    'ai_summary': None,
                    'ai_detailed_description': None,
                    'ai_topics': []
                }
        
        except Exception as e:
            logger.error(f"Document AI analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'ai_summary': None,
                'ai_detailed_description': None,
                'ai_topics': []
            }
    
    def _truncate_content(self, content: str) -> str:
        """Truncate content to fit within AI token limits."""
        if len(content) <= self.max_content_length:
            return content
        
        # Try to truncate at paragraph boundaries
        paragraphs = content.split('\n\n')
        truncated = ""
        
        for paragraph in paragraphs:
            if len(truncated) + len(paragraph) + 2 <= self.max_content_length:
                if truncated:
                    truncated += '\n\n'
                truncated += paragraph
            else:
                break
        
        # If no complete paragraphs fit, just truncate at character limit
        if not truncated:
            truncated = content[:self.max_content_length]
        
        return truncated
    
    def _create_analysis_prompt(self, content: str, filename: str, file_type: str = None) -> str:
        """Create the prompt for AI analysis."""
        
        file_info = f"Filename: {filename}"
        if file_type:
            file_info += f"\nFile type: {file_type}"
        
        prompt = f"""Analyze the following document and provide a structured response.

{file_info}

Document Content:
{content}

Please provide your analysis in the following JSON format:
{{
    "summary": "A concise 1-2 sentence summary of what this document is about",
    "detailed_description": "A more detailed 2-3 paragraph description explaining the document's content, purpose, and key information",
    "topics": ["topic1", "topic2", "topic3", "topic4", "topic5"]
}}

Requirements:
- Summary should be 1-2 sentences maximum
- Detailed description should be 2-3 paragraphs explaining what the document contains and its purpose
- Topics should be 3-7 key topics/themes/subjects covered in the document
- All topics should be specific and relevant
- Respond ONLY with valid JSON, no additional text

JSON Response:"""

        return prompt
    
    async def _call_gemini(self, prompt: str) -> Dict[str, Any]:
        """Call the Gemini AI service."""
        try:
            # Create a ModelMessage from the prompt
            from app.services.model_router import ModelMessage, ModelRole
            
            messages = [ModelMessage(role=ModelRole.USER, content=prompt)]
            
            # Use the model router to generate response
            response = await self.gemini_service.generate_response(
                messages=messages,
                model=self.default_model,
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=1000
            )
            
            return {
                'success': True,
                'content': response.content
            }
        
        except Exception as e:
            logger.error(f"Gemini API call failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response and extract structured data."""
        try:
            # Clean the response - remove any markdown formatting
            cleaned = response_text.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Parse JSON
            parsed = json.loads(cleaned)
            
            # Validate required fields
            summary = parsed.get('summary', '').strip()
            detailed_description = parsed.get('detailed_description', '').strip()
            topics = parsed.get('topics', [])
            
            # Ensure topics is a list
            if not isinstance(topics, list):
                topics = []
            
            # Clean and validate topics
            clean_topics = []
            for topic in topics[:7]:  # Max 7 topics
                if isinstance(topic, str) and topic.strip():
                    clean_topics.append(topic.strip())
            
            return {
                'summary': summary if summary else 'Document uploaded successfully',
                'detailed_description': detailed_description if detailed_description else 'Content extracted and processed',
                'topics': clean_topics
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            logger.error(f"Response was: {response_text}")
            
            # Fallback: try to extract information using simple parsing
            return self._fallback_parse(response_text)
        
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return self._get_default_metadata()
    
    def _fallback_parse(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing when JSON parsing fails."""
        lines = response_text.split('\n')
        
        summary = "Document processed successfully"
        detailed_description = "Content has been extracted and analyzed"
        topics = []
        
        # Try to extract some basic information
        for line in lines:
            line = line.strip()
            if line.lower().startswith('summary'):
                parts = line.split(':', 1)
                if len(parts) > 1:
                    summary = parts[1].strip().strip('"')
        
        return {
            'summary': summary,
            'detailed_description': detailed_description,
            'topics': topics
        }
    
    def _get_default_metadata(self) -> Dict[str, Any]:
        """Get default metadata when AI processing fails."""
        return {
            'summary': 'Document uploaded and processed',
            'detailed_description': 'The document has been successfully uploaded and its content extracted for processing.',
            'topics': []
        }


# Global instance
document_ai_service = DocumentAIService()