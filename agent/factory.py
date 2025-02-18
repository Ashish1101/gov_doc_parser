from typing import Type, Dict, Any
from pydantic_ai import Agent
from config.base import BaseConfig
from models.base import BaseAIModel
from models.openai_model import OpenAIModel
from models.anthropic_model import AnthropicModel

class AIAgentFactory:
    MODEL_MAPPING = {
        "openai": OpenAIModel,
        "anthropic": AnthropicModel,
        # Add more model implementations here
    }

    @staticmethod
    def create_model(config: BaseConfig) -> BaseAIModel:
        model_class = AIAgentFactory.MODEL_MAPPING.get(config.model_type)
        if not model_class:
            raise ValueError(f"Unsupported model type: {config.model_type}")
        
        return model_class(
            model_name=config.model_name,
            api_key=config.api_key,
            # max_tokens=config.max_tokens,
            # temperature=config.temperature,
            **config.additional_params
        )

    @staticmethod
    def create_agent(config: BaseConfig, 
                    output_type: Type, 
                    system_prompt: str) -> Agent:
        model = AIAgentFactory.create_model(config)
        
        return Agent(
            model=model,
            result_type=output_type,
            system_prompt=system_prompt
        ) 