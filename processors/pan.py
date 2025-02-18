from typing import Type
from agent.factory import AIAgentFactory
from config.base import BaseConfig, DependencyConfig, AgentDependencies
from processors.base import DocumentProcessor
from processors.data_classes.pan_dataclass import PANData


class PANProcessor(DocumentProcessor[PANData]):
    def __init__(self, agent_factory: AIAgentFactory, config: BaseConfig):
        # Get the JSON schema for validation
        self.output_schema = PANData.model_json_schema()
        
        # Define dependencies
        config.dependencies = {
            "pan_number": DependencyConfig(
                name="pan_number", 
                type=str,
                description="PAN number",
                required=False
            ),
            "name": DependencyConfig(
                name="name",
                type=str, 
                description="Full name on PAN card",
                required=False
            ),
            "dob": DependencyConfig(
                name="dob",
                type=str,
                description="Date of birth",
                required=False
            ),
            "father_name": DependencyConfig(
                name="father_name",
                type=str,
                description="Father's name",
                required=False
            ),
            "gender": DependencyConfig(
                name="gender",
                type=str,
                description="Gender",
                required=False
            )
        }
        super().__init__(agent_factory, config)

    @property
    def output_type(self) -> Type[PANData]:
        return PANData
    
    @property
    def system_prompt(self) -> str:
        return """You are a specialized PAN card parser. Your task is to extract information from PAN card documents 
        and structure it according to the specified format. Please extract:
        - PAN number (10 character alphanumeric)
        - Full name as shown on card
        - Date of birth
        - Father's name
        - Gender
        
        Ensure all extracted information is accurate and properly formatted."""
    
    async def process(self, file_path: str, **dependencies) -> PANData:
        # Validate dependencies but don't require them
        validated_deps = self.dependency_manager.validate_dependencies(dependencies)
        
        # Store file path
        self.file_path = file_path
        
        # Get file type and extract text
        file_type = self._get_file_type(file_path)
        if file_type == "pdf":
            content = await self._process_pdf(file_path)
            extracted_text = "\n".join(content) if isinstance(content, list) else str(content)
        elif file_type in ["jpg", "jpeg", "png"]:
            content = await self._process_image(file_path)
            extracted_text = str(content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        prompt = f"""Please extract and structure the following PAN card text.
        
        Document Text:
        {extracted_text}
        
        Please extract all required information and format it according to the specified structure, including:
        - PAN number
        - Full name
        - Date of birth
        - Father's name 
        - Gender
        if not able to find, leave it blank.
        """

        result = await self.agent.run(
            prompt,
            deps=AgentDependencies(file_path=file_path, additional_context=validated_deps),
            result_type=PANData
        )
        
        return result.data

    def validate(self, data: PANData) -> bool:
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Check PAN number format (10 characters alphanumeric)
                if not (len(data.pan_number) == 10 and data.pan_number.isalnum()):
                    raise ValueError("Invalid PAN number format")

                # Check other required fields
                if not all([
                    data.name,
                    data.dob,
                    data.father_name,
                    data.gender
                ]):
                    raise ValueError("Missing required fields")

                return True

            except ValueError as e:
                print(f"Validation failed on attempt {retry_count + 1}: {str(e)}")
                retry_count += 1
                if retry_count == max_retries:
                    return False
                continue