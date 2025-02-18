from typing import Any, Dict, Type, Optional
from pydantic import BaseModel
from pydantic_ai.models.openai import OpenAIModel as PydanticOpenAI
from .base import BaseAIModel

class OpenAIModel(PydanticOpenAI, BaseAIModel):
    def __init__(self, 
                 model_name: str,
                 api_key: str,
                #  max_tokens: Optional[int] = None,
                #  temperature: float = 0.7,
                 **kwargs):
        super().__init__(
            model_name=model_name,
            api_key=api_key,
            # max_tokens=max_tokens,
            # temperature=temperature,
            **kwargs
        )

    async def generate(self, 
                      prompt: str, 
                      output_type: Type[BaseModel],
                      **kwargs) -> Any:
        return await super().generate(prompt, output_type, **kwargs)

    def get_model_config(self) -> Dict[str, Any]:
        return {
            "model_type": "openai",
            "model_name": self.model_name
        }

    def __str__(self) -> str:
        return self.model_name 