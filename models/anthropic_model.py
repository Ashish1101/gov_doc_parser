from typing import Any, Dict, Type, Optional
from pydantic import BaseModel
from anthropic import Anthropic
from .base import BaseAIModel

class AnthropicModel(BaseAIModel):
    def __init__(self, 
                 api_key: str,
                 model_name: str = "claude-3",
                 temperature: float = 0.7,
                 max_tokens: Optional[int] = None,
                 **kwargs):
        self.client = Anthropic(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.additional_params = kwargs

    async def generate(self, 
                      prompt: str, 
                      output_type: Type[BaseModel],
                      **kwargs) -> Any:
        response = await self.client.messages.create(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        # Parse response into output_type
        return output_type.parse_raw(response.content)

    def get_model_config(self) -> Dict[str, Any]:
        return {
            "model_type": "anthropic",
            "model_name": self.model_name,
            "temperature": self.temperature
        } 