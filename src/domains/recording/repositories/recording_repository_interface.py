"""Recording repository interface - Domain abstraction."""
from abc import ABC, abstractmethod
from typing import List, Optional
from domains.recording.entities.service_tier import ServiceTier, ServiceOption


class IRecordingRepository(ABC):
    """
    Recording repository interface.
    
    Follows Repository pattern and Dependency Inversion Principle.
    """
    
    @abstractmethod
    def get_service_tiers(self) -> List[ServiceTier]:
        """Get all service tiers (Basic and Premium)."""
        pass
    
    @abstractmethod
    def get_service_tier_by_id(self, tier_id: str) -> Optional[ServiceTier]:
        """Get service tier by ID."""
        pass
    
    @abstractmethod
    def get_service_option_by_id(self, option_id: str) -> Optional[ServiceOption]:
        """Get service option by ID."""
        pass

