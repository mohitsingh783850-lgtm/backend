from pydantic import BaseModel, EmailStr
from pydantic import BaseModel, Field
from typing import List, Optional

class TalentRequest(BaseModel):
    # Contact Person
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    
    # Company Details
    company_name: str
    website: Optional[str] = None
    industry: str
    company_phone: Optional[str] = None
    address: str
    
    req_age: Optional[str] = None
    req_education: Optional[str] = None
    req_sex: Optional[str] = None
    req_skills: Optional[str] = None
    experience: Optional[str] = None

    
    # Job Details
    specialization: str
    pronoun: Optional[str] = None
    position: str
    openings: int
    location: str
    pay_range: str
    job_description: str

class JobApplication(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    address: str
    sex: Optional[str] = None
    age: Optional[int] = None
    education: str
    skills: str
    experience: Optional[str] = None
    qualities: str
    additional_info: Optional[str] = None

class ContactMessage(BaseModel):
    name: str
    phone: str
    email: EmailStr
    subject: str
    message: str

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str 

class UserLogin(BaseModel):
    email: EmailStr
    password: str 

class JobModel(BaseModel):
    title: str = "Software Engineer"
    location: str
    website: str
    salary: str
    experience_needed: str
    apply_within: str
    requirements: dict
    description: List[str]
    responsibilities: List[str]
    advantages: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Software Engineer",
                "location": "San Francisco, California",
                "website": "http://www.example.com",
                "salary": "$200 - $300 Per Month",
                "experience_needed": "2-3 Yrs",
                "apply_within": "25th March, 2026",
                "requirements": {
                    "age": "25th March, 2025",
                    "sex": "Male/ Female",
                    "education": "CSE Engineer"
                },
                "description": ["Text snippet 1", "Text snippet 2"],
                "responsibilities": ["Task 1", "Task 2"],
                "advantages": ["Benefit 1"]
            }
        }

class PersonalInfoSchema(BaseModel):
    fullName: str = Field(..., min_length=1)
    address: Optional[str] = ""
    phoneNumber: Optional[str] = ""
    email: EmailStr

class EducationSchema(BaseModel):
    school: Optional[str] = ""
    degree: Optional[str] = ""
    yearCompleted: Optional[str] = ""

class EmploymentSchema(BaseModel):
    company: Optional[str] = ""
    position: Optional[str] = ""
    dates: Optional[str] = ""

class JobApplicationSchema(BaseModel):
    positionApplied: str = Field(..., min_length=1)
    personalInfo: PersonalInfoSchema
    education: EducationSchema
    employment: EmploymentSchema
    skills: Optional[str] = ""
    
# Rebuilding models to ensure type safety
UserRegister.model_rebuild()
UserLogin.model_rebuild()
TalentRequest.model_rebuild()
JobApplication.model_rebuild()