from app.core.exception import CareerOSException, ResourceNotFoundException


class LearningPathNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Learning Path")


class LearningTopicNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Learning Topic")


class LearningResourceNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Learning Resource")
