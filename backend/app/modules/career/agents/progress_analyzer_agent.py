from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService


class ProgressAnalyzerAgent:
    """
    Agent 5: Progress Analyzer Agent
    Interprets hard metrics (task completion %, interview score progression, application conversion).
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Act as an Executive Career Performance Auditor.
        Analyze candidate performance data:

        Hard Metrics:
        - Task Completion Rate: {metrics_data.get('task_completion_rate')}% ({metrics_data.get('completed_tasks')}/{metrics_data.get('total_tasks')})
        - Application Response Rate: {metrics_data.get('application_response_rate')}%
        - Average Mock Interview Score: {metrics_data.get('interview_score_avg')}/100

        Provide:
        1. Performance Velocity Evaluation
        2. Execution Bottlenecks
        3. Strategic Focus Shift
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "ProgressAnalyzerAgent",
            "execution_velocity": "HIGH" if metrics_data.get("task_completion_rate", 0) > 75 else "MEDIUM",
            "primary_bottleneck": "System Design Practice" if metrics_data.get("interview_score_avg", 0) < 80 else "Application Volume",
            "analysis_summary": getattr(response, "content", str(response)),
        }
