from datetime import date
from pydantic import BaseModel

class PANData(BaseModel):
    pan_number: str
    name: str
    dob: date
    gender: str
    father_name: str
    