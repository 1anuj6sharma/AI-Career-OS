from app.core.exception import CareerOSException, ResourceNotFoundException


class CareerRoadmapNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Career Roadmap")


class CareerMilestoneNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Career Milestone")
