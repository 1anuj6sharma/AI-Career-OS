from app.core.exception import CareerOSException, ResourceNotFoundException


class ProfessionalContactNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Professional Contact")


class OutreachMessageNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Outreach Message Draft")
