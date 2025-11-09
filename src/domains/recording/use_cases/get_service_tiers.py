"""Get service tiers use case."""
from typing import List
from domains.recording.repositories import IRecordingRepository
from domains.recording.dto import ServiceTierDTO, ServiceOptionDTO


class GetServiceTiersUseCase:
    """Use case to get all service tiers."""
    
    def __init__(self, recording_repository: IRecordingRepository):
        """Initialize use case."""
        self._repository = recording_repository
    
    def execute(self) -> List[ServiceTierDTO]:
        """Execute use case - get all service tiers."""
        tiers = self._repository.get_service_tiers()
        
        return [
            ServiceTierDTO(
                id=tier.id,
                name=tier.name,
                description=tier.description,
                options=[
                    ServiceOptionDTO(
                        id=option.id.value,
                        name=option.name,
                        price=option.price,
                        description=option.description,
                        is_hourly=option.is_hourly
                    )
                    for option in tier.options
                ]
            )
            for tier in tiers
        ]

