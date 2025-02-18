from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel

class BaseAIModel(ABC):
    """Abstract base class for AI models"""
    
    @abstractmethod
    async def generate(self, 
                      prompt: str, 
                      output_type: Type[BaseModel],
                      **kwargs) -> BaseModel:
        """Generate response from the AI model"""
        pass

    @abstractmethod
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration"""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """String representation of the model"""
        pass 