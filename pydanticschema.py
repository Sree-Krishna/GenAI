from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import List, Optional
import re

# Define the Pydantic model with Field descriptions
class Location(BaseModel):
    state: Optional[str] = Field(None, description="State of residence or job location.")
    country: Optional[str] = Field(None, description="Country of residence or job location.")

class Website(BaseModel):
    github: Optional[str] = Field(None, description="GitHub profile URL.")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL.")
    portfolio: Optional[str] = Field(None, description="Portfolio URL.")
    others: Optional[List[str]] = Field(None, description="Any other website or profile URLs as a list.")

class EducationDetails(BaseModel):
    awards: Optional[str] = Field(None, description="Awards, honors, and recognitions received.")
    relevant_courses: Optional[List[str]] = Field(None, description="List of relevant courses taken.")
    clubs: Optional[str] = Field(None, description="Clubs or extracurricular activities.")

class Education(BaseModel):
    degree: str = Field(..., description="Degree obtained: the values should be strictly masters, bachelors, or doctorate, inferred from abbreviations or titles.")
    major: Optional[str] = Field(None, description="Field of study.")
    location: Location = Field(..., description="Location of the institution.")
    institution: Optional[str] = Field(None, description="Name of the educational institution.")
    start_date: Optional[str] = Field(None, description="Start date of the education in the format month/year.")
    end_date: Optional[str] = Field(None, description="End date of the education in the format month/year, if completed.")
    details: Optional[EducationDetails] = Field(None, description="Details about awards, relevant courses, and clubs.")

    @field_validator('degree')
    @classmethod
    def validate_degree(cls, value):
        # Validate that the degree is inferred as masters, bachelors, or doctorate
        degree_map = {
            "B.Sc.": "bachelors",
            "Bachelors": "bachelors",
            "M.Sc.": "masters",
            "Masters": "masters",
            "Ph.D.": "doctorate",
            "Doctorate": "doctorate"
        }
        return degree_map.get(value, value)

class JobLocation(BaseModel):
    city: Optional[str] = Field(None, description="City where the job is located.")
    state: Optional[str] = Field(None, description="State where the job is located.")
    country: Optional[str] = Field(None, description="Country where the job is located.")

class WorkExperience(BaseModel):
    job_title: Optional[str] = Field(None, description="Title of the job role.")
    company: Optional[str] = Field(None, description="Company where the individual worked.")
    start_date: Optional[str] = Field(None, description="Start date of the job in the format month/year.")
    end_date: Optional[str] = Field(None, description="End date of the job in the format month/year, if applicable.")
    location: Optional[JobLocation] = Field(None, description="Location details for the job (city, state, country).")
    responsibilities: Optional[List[str]] = Field(None, description="Key responsibilities and accomplishments in the role.")

class ResumeData(BaseModel):
    name: str = Field(..., description="The full name of the individual, extracted in lowercase.")
    current_location: Location = Field(..., description="The current location (state and country) of the individual.")
    email: str = Field(..., description="The email address of the individual, case-sensitive.")
    phone_number: str = Field(..., description="The phone number of the individual in the format +1 (xxx) xxx-xxxx.")
    websites: Website = Field(..., description="Various websites associated with the individual such as GitHub, LinkedIn, portfolio, and others.")
    professional_summary: Optional[str] = Field(None, description="A summary of the individual's professional background. If missing, the value should be null.")
    education: List[Education] = Field(..., description="A list of education entries, each containing degree, institution, location, and related details.")
    work_experience: List[WorkExperience] = Field(..., description="A list of work experience entries, each containing job title, company, location, and responsibilities.")
    skills: List[str] = Field(..., description="A list of individual skills, case-sensitive, split if grouped inside brackets or separated by commas.")

    # Use field_validator to replace the deprecated @validator
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, value):
        # Ensure the phone number is in the format +1 (xxx) xxx-xxxx
        pattern = r'^\+1 \(\d{3}\) \d{3}-\d{4}$'
        if not re.match(pattern, value):
            # Convert the phone number to the required format if possible
            digits = re.sub(r'\D', '', value)
            if len(digits) == 10:
                return f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            else:
                raise ValueError("Phone number must follow the format +1 (xxx) xxx-xxxx")
        return value

    @field_validator('skills')
    @classmethod
    def validate_skills(cls, value):
        # Validate that skills are individual and case-sensitive, split if needed
        if ',' in value:
            raise ValueError('Skills should be individual items, not separated by commas.')
        return value