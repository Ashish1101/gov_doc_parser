from typing import List, Type
from datetime import date
from pydantic import BaseModel
from processors.base import DocumentProcessor
from processors.data_classes.form_16_dataclass import CertificateDetails, DeducteeDetails, DeductorDetails, Form16Output, PaymentSummary, TaxDeductedSummary, TaxDeductionDeposit, TaxDepositDetails, VerificationDetails
from tools import extract_text_from_file
from agent.factory import AIAgentFactory
from config.base import BaseConfig, AgentDependencies, DependencyConfig


class Form16Processor(DocumentProcessor[Form16Output]):
    def __init__(self, agent_factory: AIAgentFactory, config: BaseConfig):
        # Get the JSON schema for validation but don't use it for dependencies
        self.output_schema = Form16Output.model_json_schema()
        
        # Define dependencies but make them all optional since we'll extract them from the document
        config.dependencies = {
            "deductor_details": DependencyConfig(
                name="deductor_details",
                type=DeductorDetails,
                description="Deductor details",
                required=False
            ),
            "deductee_details": DependencyConfig(
                name="deductee_details",
                type=DeducteeDetails,
                description="Deductee details",
                required=False
            ),
            "certificate_details": DependencyConfig(
                name="certificate_details",
                type=CertificateDetails,
                description="Certificate details",
                required=False
            ),
            "summary_of_payment": DependencyConfig(
                name="summary_of_payment",
                type=List[PaymentSummary],
                description="Summary of payment",
                required=False
            ),
            "summary_of_tax_deducted_at_source": DependencyConfig(
                name="summary_of_tax_deducted_at_source",
                type=List[TaxDeductedSummary],
                description="Summary of tax deducted at source",
                required=False
            ),  
            "details_of_tax_deposited": DependencyConfig(   
                name="details_of_tax_deposited",
                type=List[TaxDepositDetails],
                description="Details of tax deposited",
                required=False
            ),
            "verification_details": DependencyConfig(
                name="verification_details",
                type=VerificationDetails,
                description="Verification details",
                required=False
            ),
            "tax_deposited_in_respect_of_deduction": DependencyConfig(
                name="tax_deposited_in_respect_of_deduction",
                type=List[TaxDeductionDeposit],
                description="Tax deposited in respect of deduction",
                required=False
            )
        }
        super().__init__(agent_factory, config)

    @property
    def output_type(self) -> Type[Form16Output]:
        return Form16Output

    @property
    def system_prompt(self) -> str:
        return """You are a specialized Form 16 parser. Your task is to extract information 
        from Form 16 documents and structure it according to the specified format..."""

    async def process(self, file_path: str, **dependencies) -> Form16Output:
        # Validate any provided dependencies, but don't require them
        validated_deps = self.dependency_manager.validate_dependencies(dependencies)
        
        # Store file path
        self.file_path = file_path
        
        # Get file type and process accordingly
        file_type = self._get_file_type(file_path)
        if file_type == "pdf":
            content = await self._process_pdf(file_path)
            # Join PDF chunks with newlines
            extracted_text = "\n".join(content) if isinstance(content, list) else str(content)
        elif file_type in ["jpg", "jpeg", "png"]:
            content = await self._process_image(file_path)
            extracted_text = str(content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        prompt = f"""Please extract and structure the following Form 16 text.
        
        Document Text:
        {extracted_text}
        
        Please extract all required information and format it according to the specified structure, including:
        - Deductor details (employer's information)
        - Deductee details (employee's information)
        - Certificate details
        - Payment summaries
        - Tax deduction summaries
        - Tax deposit details
        - Verification details
        - Tax deduction deposits
        """
        
        result = await self.agent.run(
            prompt,
            deps=AgentDependencies(file_path=file_path, additional_context=validated_deps),
            result_type=Form16Output
        )
        
        # Handle pydantic_ai RunResult
        return result.data

    def validate(self, data: Form16Output) -> bool:
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Check deductor details
                if not all([data.deductor_details.name, data.deductor_details.address, 
                           data.deductor_details.pan, data.deductor_details.tan]):
                    raise ValueError("Missing deductor details")

                # Check deductee details  
                if not all([data.deductee_details.name, data.deductee_details.address,
                           data.deductee_details.pan]):
                    raise ValueError("Missing deductee details")

                # Check certificate details
                if not all([data.certificate_details.certificate_number,
                           data.certificate_details.last_updated_date,
                           data.certificate_details.assessment_year,
                           data.certificate_details.period.from_date,
                           data.certificate_details.period.to_date]):
                    raise ValueError("Missing certificate details")

                # Check payment summaries
                if not data.summary_of_payment:
                    raise ValueError("Missing payment summary")

                # Check tax deducted summaries
                if not data.summary_of_tax_deducted_at_source:
                    raise ValueError("Missing tax deducted summary")

                # Check tax deposit details
                if not data.details_of_tax_deposited:
                    raise ValueError("Missing tax deposit details")

                # Check verification details
                if not all([data.verification_details.name,
                           data.verification_details.designation,
                           data.verification_details.verification_statement,
                           data.verification_details.place_and_date_of_verification]):
                    raise ValueError("Missing verification details")

                # Check tax deduction deposits
                if not data.tax_deposited_in_respect_of_deduction:
                    raise ValueError("Missing tax deduction deposits")

                return True

            except ValueError as e:
                print(f"Validation failed on attempt {retry_count + 1}: {str(e)}")
                retry_count += 1
                if retry_count == max_retries:
                    return False
                continue