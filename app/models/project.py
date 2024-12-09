from typing import Optional

from pydantic import BaseModel, Field

class CalculateQuery(BaseModel):
    userLatitude: Optional[float] = None
    userLongtitude: Optional[float] = None
    jobTitle: Optional[str] = None
    experience: Optional[int] = None

    locationWeight: Optional[float] = None
    companySizeWeight: Optional[float] = None
    jobTitleWeight: Optional[float] = None
    experienceWeight: Optional[float] = None
    salaryWeight: Optional[float] = None

class PointQuery(BaseModel):
    page: Optional[int] = None
    size: Optional[int] = None

class JobQuery(BaseModel):
    jobId: Optional[str] = None

class CompanyQuery(BaseModel):
    companyId: Optional[str] = None