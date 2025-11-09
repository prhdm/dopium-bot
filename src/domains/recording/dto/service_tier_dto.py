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
    is_hourly: bool = False
    
    @property
    def price_display(self) -> str:
        """Get formatted price display."""
        if self.is_hourly:
            return f"ساعتی {self.price}"
        return self.price


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

