"""Recording repository implementation - Mock data with pricing tiers."""
from typing import List, Optional
from domains.recording.repositories.recording_repository_interface import IRecordingRepository
from domains.recording.entities.service_tier import ServiceTier, ServiceOption, ServiceOptionId


class RecordingRepository(IRecordingRepository):
    """Repository implementation for recording service tiers and options."""
    
    # Basic tier options
    BASIC_OPTIONS = [
        ServiceOption(
            id=ServiceOptionId("basic_hourly"),
            name="رکورد (بیسیک)",
            price="1",
            is_hourly=True
        ),
        ServiceOption(
            id=ServiceOptionId("basic_arin_rad"),
            name="رکورد نظارت آرین راد",
            price="1/2",
            is_hourly=True
        ),
    ]
    
    # Premium tier options
    PREMIUM_OPTIONS = [
        ServiceOption(
            id=ServiceOptionId("premium_shayan_roohi"),
            name="رکورد با نظارت شایان روحی",
            price="2",
            is_hourly=False
        ),
        ServiceOption(
            id=ServiceOptionId("premium_mendesan"),
            name="رکورد با نظارت مندسن",
            price="2",
            is_hourly=False
        ),
        ServiceOption(
            id=ServiceOptionId("premium_ashkan_akai"),
            name="رکورد با نظارت اشکان آکای",
            price="3",
            is_hourly=False
        ),
        ServiceOption(
            id=ServiceOptionId("premium_aiyhoud"),
            name="رکورد با نظارت عیهود",
            price="3",
            is_hourly=False
        ),
    ]
    
    SERVICE_TIERS = [
        ServiceTier(
            id="basic",
            name="گزینه ۱: رکورد های بیسیک",
            options=BASIC_OPTIONS
        ),
        ServiceTier(
            id="premium",
            name="گزینه ۲: رکورد پریمیوم (نظارتی)",
            description=(
                "🔻 رکورد های نظارتی ( طرح صدابرداری پریمیوم ):\n"
                "در این طرح محدودیت زمانی وجود نداره و آرتیستی که انتخاب میکنید "
                "به صورت اختصاصی برای هر ترک شما، به نظارت و صدابرداری آهنگتون می‌پردازه "
                "( قیمت ها برای هر آهنگ ⬇️ )"
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
        # Search in basic options
        for option in self.BASIC_OPTIONS:
            if option.id.value == option_id:
                return option
        
        # Search in premium options
        for option in self.PREMIUM_OPTIONS:
            if option.id.value == option_id:
                return option
        
        return None
