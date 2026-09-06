from app.core.exception import CareerOSException


class AIExecutionException(CareerOSException):
    def __init__(self, message: str = "AI Agentic execution error"):
        super().__init__(message)


class PendingActionNotFoundException(CareerOSException):
    def __init__(self):
        super().__init__("Pending action not found")
