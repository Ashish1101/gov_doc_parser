from datetime import date
from pydantic import BaseModel


class AadhaarFrontOutput(BaseModel):
    name: str
    dob: date
    gender: str
    address: str
    aadhaar_number: str
    pincode: str