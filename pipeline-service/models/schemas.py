from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime, date


class CustomerBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    account_balance: float = Field(default=0.0, ge=0)


class CustomerCreate(CustomerBase):
    customer_id: str = Field(..., min_length=1, max_length=50)


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    account_balance: Optional[float] = Field(None, ge=0)


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    customer_id: str
    created_at: Optional[datetime] = None


class PaginatedResponse(BaseModel):
    data: list[CustomerResponse]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool


class IngestResponse(BaseModel):
    status: str
    records_processed: int
    message: Optional[str] = None
    performance: Optional[dict] = None
    timestamp: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
