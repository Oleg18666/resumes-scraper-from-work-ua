"""Data models for Work.ua scraper."""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List
from enum import Enum


class EmploymentType(Enum):
    """Employment type enumeration."""
    FULL_TIME = 1
    PART_TIME = 2
    REMOTE = 3
    PROJECT = 4
    INTERNSHIP = 5


class Gender(Enum):
    """Gender enumeration."""
    MALE = 1
    FEMALE = 2
    NOT_SPECIFIED = 3


class TaskType(Enum):
    """Task type for queue."""
    SEARCH_PAGE = "search_page"
    RESUME_PAGE = "resume_page"


class TaskStatus(Enum):
    """Task status."""
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"


@dataclass
class Resume:
    """Resume data model - matches DB schema."""
    resume_id: int
    resume_date: date
    person_name: str
    position: str
    source_url: str
    
    # Optional fields
    desired_salary: Optional[int] = None
    employment_type: Optional[int] = None
    birthday: Optional[date] = None
    city: Optional[str] = None
    gender: Optional[int] = None
    education_level: Optional[str] = None
    work_experience_years: Optional[float] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def extract_resume_id_from_url(cls, url: str) -> Optional[int]:
        """Extract resume ID from URL like /resumes/4122953/."""
        import re
        match = re.search(r'/resumes/(\d+)/', url)
        return int(match.group(1)) if match else None


@dataclass
class ResumeDetails:
    """Extended resume details (raw text fields)."""
    resume_id: int
    work_experience_raw: Optional[str] = None
    education_raw: Optional[str] = None
    additional_education_raw: Optional[str] = None
    skills_raw: Optional[str] = None
    languages_raw: Optional[str] = None
    recommendations_raw: Optional[str] = None
    additional_info_raw: Optional[str] = None


@dataclass
class ResumePhoto:
    """Resume photo data."""
    resume_id: int
    photo: bytes
    content_type: str = "image/jpeg"
    hash: Optional[str] = None  # MD5 or SHA256 hash for deduplication


@dataclass
class SearchTask:
    """Search page scraping task."""
    url: str
    category: int
    city_id: int
    page_number: int
    days_filter: Optional[int] = None
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class ResumeTask:
    """Resume page scraping task."""
    url: str
    resume_id: int
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class ResumeCard:
    """Brief resume info from search results page."""
    resume_id: int
    url: str
    position: str
    person_name: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None
    education_level: Optional[str] = None
    employment_types: List[int] = field(default_factory=list)
