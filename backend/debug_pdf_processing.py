#!/usr/bin/env python3
"""
Debug what happens during PDF processing.
"""

import asyncio
from pathlib import Path

async def debug_processing():
    """Debug the document processing for a PDF."""
    
    # Read the actual PDF file that's failing
    pdf_files = list(Path("/tmp").glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in /tmp. Let me create a test PDF...")
        # Create a minimal valid PDF
        test_pdf = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Times-Roman >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000274 00000 n
trailer
<< /Size 5 /Root 1 0 R >>
startxref
365
%%EOF"""
        
        with open("/tmp/test_minimal.pdf", "wb") as f:
            f.write(test_pdf)
        
        file_content = test_pdf
        filename = "test_minimal.pdf"
    else:
        pdf_file = pdf_files[0]
        with open(pdf_file, "rb") as f:
            file_content = f.read()
        filename = pdf_file.name
    
    print(f"Testing PDF: {filename} ({len(file_content)} bytes)")
    
    # Test document processor
    from app.services.document_processor import document_processor
    
    result = await document_processor.process_document_async(
        file_content,
        filename,
        "test_user_id"
    )
    
    print(f"\nDocument Processor Result:")
    print(f"  Success: {result['success']}")
    print(f"  Error: {result.get('error', 'None')}")
    print(f"  Chunks: {len(result.get('chunks', []))}")
    
    if result.get('chunks'):
        print(f"  First chunk preview: {str(result['chunks'][0])[:200]}...")
        
        # Check for language field in chunk data
        chunk_data = result['chunks'][0]
        if 'language' in str(chunk_data):
            print(f"  ⚠️  Language field found in chunk data!")
    
    # Test content extractor
    from app.services.content_extractor import content_extractor
    
    if content_extractor.can_extract(filename):
        print(f"\nContent Extractor Test:")
        extraction_result = await content_extractor.extract_content(file_content, filename)
        print(f"  Success: {extraction_result['success']}")
        if extraction_result['success']:
            print(f"  Text length: {len(extraction_result['text_content'])}")
            print(f"  Preview: {extraction_result['text_content'][:100]}...")
        else:
            print(f"  Error: {extraction_result['error']}")

if __name__ == "__main__":
    asyncio.run(debug_processing())