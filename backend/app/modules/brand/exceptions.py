from app.core.exception import CareerOSException, ResourceNotFoundException


class PortfolioNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Portfolio Profile")


class ContentItemNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Content Item")
