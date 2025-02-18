from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Any, Type, List, Union
from pydantic import BaseModel
from agent.factory import AIAgentFactory
from dependencies.manager import DependencyManager
from config.base import AgentDependencies, BaseConfig
from PyPDF2 import PdfReader
from PIL import Image
import numpy as np
import cv2
import pytesseract


T = TypeVar('T', bound=BaseModel)

class DocumentProcessor(ABC, Generic[T]):
    """Abstract base class for document processors"""
    
    def __init__(self, agent_factory: AIAgentFactory, config: BaseConfig):
        self.agent = agent_factory.create_agent(
            config=config,
            output_type=self.output_type,
            system_prompt=self.system_prompt
        )
        self.dependency_manager = DependencyManager(config.dependencies)
        self.chunk_size = config.chunk_size or 4000  # Default chunk size
        self.file_path = None  # Initialize file_path
    
    @abstractmethod
    async def process(self, file_path: str, **dependencies) -> T:
        """Process the document and return structured data"""
        self.file_path = file_path  # Store file_path
        validated_deps = self.dependency_manager.validate_dependencies(dependencies)
        
        file_type = self._get_file_type(file_path)
        if file_type == "pdf":
            content = await self._process_pdf(file_path)
        elif file_type in ["jpg", "jpeg", "png"]:
            content = await self._process_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
            
        return await self._process_content(content, validated_deps)

    async def _process_pdf(self, file_path: str) -> List[str]:
        """Extract text from PDF in chunks"""
        reader = PdfReader(file_path)
        chunks = []
        current_chunk = ""
        
        for page in reader.pages:
            text = page.extract_text()
            if len(current_chunk) + len(text) > self.chunk_size:
                chunks.append(current_chunk)
                current_chunk = text
            else:
                current_chunk += text
                
        if current_chunk:
            chunks.append(current_chunk)
        return chunks

    async def _process_image(self, file_path: str) -> str:
        """Process image using OCR"""
        # Read image using OpenCV
        # Install OpenCV using: pip install opencv-python
        image = cv2.imread(file_path)
        if image is None:
            raise ValueError(f"Failed to load image: {file_path}")
            
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to preprocess the image
        threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Perform OCR using Tesseract
        try:
            text = pytesseract.image_to_string(threshold)
        except Exception as e:
            raise RuntimeError(f"OCR failed: {str(e)}")
            
        if not text.strip():
            raise ValueError("No text was extracted from the image")
            
        return text.strip()

    async def _process_content(self, content: Union[List[str], str], dependencies: Dict[str, Any]) -> T:
        """Process extracted content using AI agent"""
        if isinstance(content, list):
            # Process chunks
            results = []
            for chunk in content:
                result = await self.agent.run(
                    chunk,
                    deps=AgentDependencies(file_path=self.file_path, additional_context=dependencies)
                )
                results.append(result)
            # Merge results
            return self._merge_results(results)
        else:
            # Process single content
            # Ensure content is a string
            content_str = str(content) if content is not None else ""
            return await self.agent.run(
                content_str,
                deps=AgentDependencies(file_path=self.file_path, additional_context=dependencies)
            )

    def _merge_results(self, results: List[T]) -> T:
        """Merge multiple results into single output"""
        # Implementation will depend on specific output type
        raise NotImplementedError("Merge strategy must be implemented in derived classes")

    def _get_file_type(self, file_path: str) -> str:
        """Determine file type from path"""
        return file_path.split('.')[-1].lower()

    @abstractmethod
    def validate(self, data: T) -> bool:
        """Validate the extracted data"""
        pass

    @property
    @abstractmethod
    def output_type(self) -> Type[T]:
        """Return the output type for this processor"""
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this processor"""
        pass