from app.core.exception import CareerOSException, ResourceNotFoundException


class JobNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Job")


class ApplicationNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Application")


class CompanyNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Company")


class ContactNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Contact")


class TaskNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Task")


class NoteNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Job Note")


class InvalidStatusTransitionException(CareerOSException):
    def __init__(self, message: str = "Invalid status transition."):
        super().__init__(message)
