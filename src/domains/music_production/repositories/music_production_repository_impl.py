"""Music production repository implementation - Mock data with pricing tiers."""
from typing import List, Optional
from domains.music_production.repositories.music_production_repository_interface import IMusicProductionRepository
from domains.music_production.entities.service_tier import ServiceTier, ServiceOption, ServiceOptionId


class MusicProductionRepository(IMusicProductionRepository):
    """Repository implementation for music production service tiers and options."""
    
    # Basic tier options
    BASIC_OPTIONS = [
        ServiceOption(
            id=ServiceOptionId("production_basic_set"),
            name="پروداکشن بیسیک مجموعه",
            price="5"
        ),
        ServiceOption(
            id=ServiceOptionId("production_arin_rad"),
            name="پروداکشن با آرین راد",
            price="8"
        ),
    ]
    
    # Premium tier options
    PREMIUM_OPTIONS = [
        ServiceOption(
            id=ServiceOptionId("production_mendesan"),
            name="پروداکشن با مندسن",
            price="15"
        ),
        ServiceOption(
            id=ServiceOptionId("production_shayan_roohi"),
            name="پروداکشن با شایان روحی",
            price="15"
        ),
        ServiceOption(
            id=ServiceOptionId("production_ashkan_akai"),
            name="پروداکشن با اشکان آکای",
            price="15"
        ),
        ServiceOption(
            id=ServiceOptionId("production_aiyhoud"),
            name="پروداکشن با عیهود",
            price="15"
        ),
        ServiceOption(
            id=ServiceOptionId("production_difo"),
            name="پروداکشن با دیفو",
            price="15"
        ),
    ]
    
    SERVICE_TIERS = [
        ServiceTier(
            id="basic",
            name="پروداکشن بیسیک دوپیوم",
            options=BASIC_OPTIONS
        ),
        ServiceTier(
            id="premium",
            name="پروداکشن پریمیوم دوپیوم",
            description=(
                "🟡 طرح \"پروداکشن پرایم\"\n"
                "در این طرح تو تمامی روند با همفکری همدیگه در قالب یک پروژه مشترک کار رو پیش ببرید.\n\n"
                "⭕️ نکته مهم اینه که در طرح پرایم، نیاز نیست تمام مبلغ رو یکجا پرداخت کنید "
                "و توی دوپیوم میتونید در قالب دو قسط هزینه همکاری رو پرداخت کنید."
            ),
            options=PREMIUM_OPTIONS
        ),
    ]
    
    def get_service_tiers(self) -> List[ServiceTier]:
        """Get all service tiers."""
        return self.SERVICE_TIERS.copy()
    
    def get_service_tier_by_id(self, tier_id: str) -> Optional[ServiceTier]:
        """Get service tier by ID."""
        for tier in self.SERVICE_TIERS:
            if tier.id == tier_id:
                return tier
        return None
    
    def get_service_option_by_id(self, option_id: str) -> Optional[ServiceOption]:
        """Get service option by ID."""
        for option in self.BASIC_OPTIONS:
            if option.id.value == option_id:
                return option
        
        for option in self.PREMIUM_OPTIONS:
            if option.id.value == option_id:
                return option
        
        return None

