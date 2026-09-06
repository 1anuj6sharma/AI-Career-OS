from app.core.exception import CareerOSException, ResourceNotFoundException


class JobOpportunityNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Job Opportunity")


class JobMatchNotFoundException(ResourceNotFoundException):
    def __init__(self):
        super().__init__("Job Match")
