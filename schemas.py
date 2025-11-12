"""
Database Schemas for Swarajyache Armar

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase of the class name.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import date, time


class Appointment(BaseModel):
    """
    Customer appointment bookings
    Collection name: "appointment"
    """
    name: str = Field(..., description="Customer full name")
    phone: str = Field(..., description="Contact phone number")
    email: Optional[EmailStr] = Field(None, description="Email address")
    service: str = Field(..., description="Selected service")
    preferred_date: date = Field(..., description="Preferred appointment date")
    preferred_time: Optional[str] = Field(None, description="Preferred time slot (e.g., 11:00 AM)")
    message: Optional[str] = Field(None, description="Additional notes from customer")


class QuoteRequest(BaseModel):
    """
    Quote enquiry from website visitors
    Collection name: "quoterequest"
    """
    name: str = Field(...)
    phone: str = Field(...)
    email: Optional[EmailStr] = None
    requirement: str = Field(..., description="Brief about requirement")
    budget: Optional[str] = Field(None, description="Budget range if any")


class Service(BaseModel):
    """
    Service catalog
    Collection name: "service"
    """
    title: str
    description: Optional[str] = None
    starting_price: float = Field(..., ge=0)
    unit: str = Field("per unit", description="Pricing unit label")
    featured: bool = Field(False)


class GalleryImage(BaseModel):
    """
    Image gallery items
    Collection name: "galleryimage"
    """
    url: str = Field(..., description="Public image URL")
    title: Optional[str] = None
    category: Optional[str] = None
