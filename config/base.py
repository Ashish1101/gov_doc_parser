from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal, Type, Union, get_origin, get_args
from dataclasses import dataclass

class DependencyConfig(BaseModel):
    """Configuration for dependencies that will be passed to the model"""
    name: str
    type: Union[Type, Any]  # Changed from Type to Union[Type, Any] to handle complex types
    description: str
    required: bool = True

    class Config:
        arbitrary_types_allowed = True  # Allow arbitrary types including generics

    def validate_type(self, value: Any) -> bool:
        """Validate complex types including Lists and other generic types"""
        base_type = get_origin(self.type) or self.type
        if base_type is list:
            if not isinstance(value, list):
                return False
            # Get the type argument of the list
            item_type = get_args(self.type)[0]
            # Check each item in the list
            return all(isinstance(item, item_type) for item in value)
        return isinstance(value, base_type)

class BaseConfig(BaseModel):
    model_type: Literal["openai", "anthropic"]  # Add more as needed
    api_key: str
    model_name: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    additional_params: Dict[str, Any] = {}
    dependencies: Dict[str, DependencyConfig] = {}
    chunk_size: Optional[int] = 4000  # Added chunk_size with default value

    class Config:
        arbitrary_types_allowed = True

@dataclass
class AgentDependencies:
    file_path: str
    additional_context: Dict[str, Any] = None 