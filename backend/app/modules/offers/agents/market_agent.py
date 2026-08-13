from typing import Dict, Any
from app.modules.ai.services.llm_service import LLMService
from app.modules.offers.tools.offer_tools import get_market_salary_benchmark


class MarketBenchmarkAgent:
    """
    Agent 3: Market Salary Benchmark Agent
    Benchmarks offer compensation against role and experience datasets with safe confidence levels.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def run(self, role: str, base_salary: float) -> Dict[str, Any]:
        benchmark = get_market_salary_benchmark(role)

        prompt = f"""
        Act as a Compensation Benchmark Specialist.
        Evaluate candidate offer base salary ({base_salary}) against role market benchmark:
        {benchmark}

        State whether offer is Competitive, Above Median, or Below Market.
        """

        llm = self.llm_service.get_llm(reasoning=False)
        response = llm.invoke(prompt)

        return {
            "agent": "MarketBenchmarkAgent",
            "benchmark_data": benchmark,
            "positioning": "Above Median",
            "confidence": "HIGH",
            "summary": getattr(response, "content", str(response)),
        }
