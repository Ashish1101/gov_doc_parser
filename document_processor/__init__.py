from typing import Dict, Any, Optional
import asyncio
import json
from datetime import date, datetime
from main import DocumentProcessor

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

class DocumentExtractor:
    """
    Main interface for document information extraction
    """
    def __init__(self, 
                 api_key: str,
                 model_type: str = "openai",
                 model_name: str = "gpt-4"):
        self.processor = DocumentProcessor(
            api_key=api_key,
            model_type=model_type,
            model_name=model_name
        )

    def extract(self, 
                file_path: str, 
                doc_type: str,
                as_json: bool = True) -> Dict[str, Any]:
        """
        Extract information from a document.
        
        Args:
            file_path (str): Path to the document file
            doc_type (str): Type of document ('form16', 'aadhaar_front', 'aadhaar_back', 'pan')
            as_json (bool): Whether to return result as JSON string (default: True)
            
        Returns:
            Dict[str, Any] or str: Extracted information as dictionary or JSON string
        """
        result = asyncio.run(self.processor.process(file_path, doc_type))
        
        if as_json:
            return json.dumps(result, cls=CustomJSONEncoder)
        return result

    async def extract_async(self, 
                          file_path: str, 
                          doc_type: str,
                          as_json: bool = True) -> Dict[str, Any]:
        """
        Extract information from a document asynchronously.
        
        Args:
            file_path (str): Path to the document file
            doc_type (str): Type of document ('form16', 'aadhaar_front', 'aadhaar_back', 'pan')
            as_json (bool): Whether to return result as JSON string (default: True)
            
        Returns:
            Dict[str, Any] or str: Extracted information as dictionary or JSON string
        """
        result = await self.processor.process(file_path, doc_type)
        
        if as_json:
            return json.dumps(result, cls=CustomJSONEncoder)
        return result 