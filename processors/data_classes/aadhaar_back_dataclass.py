from pydantic import BaseModel

class AadhaarBackOutput(BaseModel):
    aadhaar_number: str
    address: str
    pincode: str
    vid: str