from app.core.exception import CareerOSException, ResourceNotFoundException


class InterviewNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Interview")


class InterviewQuestionNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Interview Question")


class InterviewAnswerNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Interview Answer")


class InterviewAlreadyCompletedException(CareerOSException):
    def __init__(self):
        super().__init__("This interview session has already been completed.")
