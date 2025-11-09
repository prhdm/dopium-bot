"""Service tier and pricing entities."""
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ServiceOptionId:
    """Service option ID value object."""
    value: str
    
    def __str__(self) -> str:
        return self.value


@dataclass
class ServiceOption:
    """Service option entity."""
    
    id: ServiceOptionId
    name: str
    price: str  # e.g., "1", "1/2", "2", "3"
    description: Optional[str] = None
    is_hourly: bool = False  # True for hourly pricing, False for per-track
    
    def __post_init__(self) -> None:
        """Validate service option."""
        if not self.name or not self.name.strip():
            raise ValueError("Service option name cannot be empty")
        if not self.price or not self.price.strip():
            raise ValueError("Service option price cannot be empty")
    
    def __eq__(self, other: object) -> bool:
        """Options are equal if they have the same ID."""
        if not isinstance(other, ServiceOption):
            return False
        return self.id.value == other.id.value
    
    def __hash__(self) -> int:
        return hash(self.id.value)


@dataclass
class ServiceTier:
    """Service tier entity (Basic or Premium)."""
    
    id: str  # "basic" or "premium"
    name: str
    description: Optional[str] = None
    options: List[ServiceOption] = None
    
    def __post_init__(self) -> None:
        """Validate service tier."""
        if not self.name or not self.name.strip():
            raise ValueError("Service tier name cannot be empty")
        if self.options is None:
            object.__setattr__(self, 'options', [])

