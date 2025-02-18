from typing import List
from pydantic import BaseModel


class DeductorDetails(BaseModel):
    name: str
    address: str 
    pan: str
    tan: str

class DeducteeDetails(BaseModel):
    name: str
    address: str
    pan: str

class Period(BaseModel):
    from_date: str
    to_date: str

class CertificateDetails(BaseModel):
    certificate_number: str
    last_updated_date: str
    assessment_year: str
    period: Period

class PaymentSummary(BaseModel):
    amount: str
    nature: str
    date: str

class TaxDeductedSummary(BaseModel):
    quarter: str
    receipt_numbers: str
    amount_of_tax_deducted: str
    amount_of_tax_deposited: str

class ChallanDetails(BaseModel):
    challan_identification_number: str
    bsr_code: str
    date_of_deposit: str
    challan_serial_number: str
    status_of_matching_with_oltas: str

class TaxDepositDetails(BaseModel):
    tax_deposited_through_book_adjustment: str
    tax_deposited_through_challan: List[ChallanDetails]

class VerificationDetails(BaseModel):
    name: str
    designation: str
    verification_statement: str
    place_and_date_of_verification: str

class TaxDeductionDeposit(BaseModel):
    s_no: str
    amount_of_tax_deducted: str

class Form16Output(BaseModel):
    deductor_details: DeductorDetails
    deductee_details: DeducteeDetails
    certificate_details: CertificateDetails
    summary_of_payment: List[PaymentSummary]
    summary_of_tax_deducted_at_source: List[TaxDeductedSummary]
    details_of_tax_deposited: List[TaxDepositDetails]
    verification_details: VerificationDetails
    tax_deposited_in_respect_of_deduction: List[TaxDeductionDeposit]