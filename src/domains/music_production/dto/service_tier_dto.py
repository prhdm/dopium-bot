"""Service tier DTOs."""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ServiceOptionDTO:
    """Service option DTO."""
    
    id: str
    name: str
    price: str
    description: Optional[str] = None


@dataclass
class ServiceTierDTO:
    """Service tier DTO."""
    
    id: str
    name: str
    description: Optional[str] = None
    options: List[ServiceOptionDTO] = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = []

