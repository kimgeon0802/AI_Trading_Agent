import logging
from agents.gpt_agent.agent import GPTAgent
from agents.claude_agent.agent import ClaudeMockAgent
from agents.multi_ai.consensus_manager import ConsensusManager

logger = logging.getLogger("MultiAIOrchestrator")

class MultiAIOrchestrator:
    def __init__(self):
        self.gpt_agent = GPTAgent()
        self.claude_agent = ClaudeMockAgent()
        self.consensus_manager = ConsensusManager()

    def execute(self, market_data: dict) -> dict:
        """
        Orchestrate decision making from GPT and Claude agents.
        """
        agent_results = {}
        
        # 1. Execute GPT
        try:
            agent_results["gpt"] = self.gpt_agent.make_decision(market_data)
        except Exception as e:
            logger.error(f"Error executing GPTAgent: {e}")
            agent_results["gpt"] = None
            
        # 2. Execute Claude
        try:
            agent_results["claude"] = self.claude_agent.make_decision(market_data)
        except Exception as e:
            logger.error(f"Error executing ClaudeMockAgent: {e}")
            agent_results["claude"] = None
            
        # 3. Consensus
        consensus = self.consensus_manager.get_consensus(agent_results)
        
        # 4. Construct Final Result (compatible with existing structures)
        final_result = {
            "decision": consensus["decision"],
            "confidence": consensus["confidence"],
            "reasoning": consensus["reasoning"],
            "risks": self._aggregate_risks(agent_results),
            "expected_result": self._aggregate_expected_results(agent_results),
            "consensus": {
                "method": consensus["consensus_type"],
                "participants": consensus["participating_agents"]
            },
            "agent_results": agent_results
        }
        return final_result

    def _aggregate_risks(self, agent_results: dict) -> str:
        risks = []
        for name, res in agent_results.items():
            if res and "risks" in res:
                risks.append(f"{name.upper()}: {res['risks']}")
        return "; ".join(risks) if risks else "No specific risks reported."

    def _aggregate_expected_results(self, agent_results: dict) -> str:
        results = []
        for name, res in agent_results.items():
            if res and "expected_result" in res:
                results.append(f"{name.upper()}: {res['expected_result']}")
        return "; ".join(results) if results else "No specific expected results reported."
