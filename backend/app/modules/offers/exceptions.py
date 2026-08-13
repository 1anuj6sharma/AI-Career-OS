from app.core.exception import CareerOSException, ResourceNotFoundException


class CareerOfferNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Career Offer")
