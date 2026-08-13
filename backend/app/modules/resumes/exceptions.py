from app.core.exception import CareerOSException, ResourceNotFoundException


class ResumeNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Resume")


class ResumeVersionNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Resume Version")


class ResumeParsingException(CareerOSException):
    def __init__(self, message: str = "Failed to parse text from resume document"):
        super().__init__(message)


class FactCheckFailedException(CareerOSException):
    def __init__(self, message: str = "Fact check failed: Draft contains unverified or fabricated experience"):
        super().__init__(message)
