"""Get service tier options use case."""
from domains.music_production.repositories import IMusicProductionRepository
from domains.music_production.dto import ServiceTierDTO, ServiceOptionDTO


class GetServiceTierOptionsUseCase:
    """Use case to get options for a specific tier."""
    
    def __init__(self, repository: IMusicProductionRepository):
        """Initialize use case."""
        self._repository = repository
    
    def execute(self, tier_id: str) -> ServiceTierDTO:
        """
        Execute use case - get tier and its options.
        
        Args:
            tier_id: Tier ID ("basic" or "premium")
            
        Returns:
            ServiceTierDTO with options
            
        Raises:
            ValueError: If tier not found
        """
        tier = self._repository.get_service_tier_by_id(tier_id)
        
        if not tier:
            raise ValueError(f"Service tier with ID {tier_id} not found")
        
        return ServiceTierDTO(
            id=tier.id,
            name=tier.name,
            description=tier.description,
            options=[
                ServiceOptionDTO(
                    id=option.id.value,
                    name=option.name,
                    price=option.price,
                    description=option.description
                )
                for option in tier.options
            ]
        )

