from agent.factory import AIAgentFactory
from processors.base import DocumentProcessor
from pydantic import ConfigDict
from dependencies.manager import DependencyConfig
from datetime import date
from typing import Type
from pydantic import BaseModel
from processors.data_classes.aadhaar_front_dataclass import AadhaarFrontOutput
from processors.data_classes.aadhaar_back_dataclass import AadhaarBackOutput
from config.base import BaseConfig, AgentDependencies

class AadhaarFrontProcessor(DocumentProcessor[AadhaarFrontOutput]):
    def __init__(self, agent_factory: AIAgentFactory, config: BaseConfig):
        # Define dependencies but make them all optional
        config.dependencies = {}  # No required dependencies for Aadhaar front
        super().__init__(agent_factory, config)

    @property
    def output_type(self) -> Type[AadhaarFrontOutput]:
        return AadhaarFrontOutput

    @property
    def system_prompt(self) -> str:
        return """You are a specialized Aadhaar card front parser. Your task is to extract information 
        from Aadhaar card front images and structure it according to the specified format..."""

    async def process(self, file_path: str, **dependencies) -> AadhaarFrontOutput:
        validated_deps = self.dependency_manager.validate_dependencies(dependencies)
        
        # Store file path
        self.file_path = file_path
        
        # Process image
        content = await self._process_image(file_path)
        extracted_text = str(content)
        
        prompt = f"""Please extract and structure the following Aadhaar card front text.
        
        Document Text:
        {extracted_text}
        
        Please extract all required information and format it according to the specified structure, including:
        - Name
        - Date of Birth
        - Gender
        - Address
        - Aadhaar Number
        - Pincode
        if fields not found, return None
        """
        
        result = await self.agent.run(
            prompt,
            deps=AgentDependencies(file_path=file_path, additional_context=validated_deps),
            result_type=AadhaarFrontOutput
        )
        
        return result.data

    def validate(self, data: AadhaarFrontOutput) -> bool:
        try:
            # Check all required fields
            if not all([
                data.name,
                data.dob,
                data.gender,
                data.address,
                data.aadhaar_number
            ]):
                return False
            
            # Validate Aadhaar number format (12 digits)
            if not data.aadhaar_number.isdigit() or len(data.aadhaar_number) != 12:
                return False
                
            return True
            
        except Exception as e:
            print(f"Validation error: {str(e)}")
            return False

class AadhaarBackProcessor(DocumentProcessor[AadhaarBackOutput]):
    def __init__(self, agent_factory: AIAgentFactory, config: BaseConfig):
        # Define dependencies but make them all optional
        config.dependencies = {}  # No required dependencies for Aadhaar back
        super().__init__(agent_factory, config)

    @property
    def output_type(self) -> Type[AadhaarBackOutput]:
        return AadhaarBackOutput

    @property
    def system_prompt(self) -> str:
        return """You are a specialized Aadhaar back parser. Extract the following information from the Aadhaar card back:
        - Aadhaar number (12 digits)
        - Complete address
        - Pincode (6 digits)
        - VID number
        
        Ensure all extracted information is accurate and properly formatted. if fields not found, return None"""

    async def process(self, file_path: str, **dependencies) -> AadhaarBackOutput:
        validated_deps = self.dependency_manager.validate_dependencies(dependencies)
        
        # Store file path
        self.file_path = file_path
        
        # Process image
        content = await self._process_image(file_path)
        extracted_text = str(content)
        
        prompt = f"""Please extract and structure the following Aadhaar back text.
        
        Document Text:
        {extracted_text}
        
        Please extract all required information and format it according to the specified structure, including:
        - Aadhaar number (12 digits)
        - Complete address
        - Pincode (6 digits)
        - VID number
        """
        
        result = await self.agent.run(
            prompt,
            deps=AgentDependencies(file_path=file_path, additional_context=validated_deps),
            result_type=AadhaarBackOutput
        )
        
        return result.data

    def validate(self, data: AadhaarBackOutput) -> bool:
        try:
            # Validate Aadhaar number format (12 digits)
            if not data.aadhaar_number or not data.aadhaar_number.isdigit() or len(data.aadhaar_number) != 12:
                return False

            # Validate address
            if not data.address or len(data.address.strip()) < 10:
                return False

            # Validate pincode (6 digits)
            if not data.pincode or not data.pincode.isdigit() or len(data.pincode) != 6:
                return False

            # Validate VID format (optional)
            if data.vid and (not data.vid.isdigit() or len(data.vid) != 16):
                return False

            return True
            
        except Exception as e:
            print(f"Validation error: {str(e)}")
            return False