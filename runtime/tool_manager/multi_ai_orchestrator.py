import asyncio
import logging
from agents.gpt_agent.agent import GPTAgent
from agents.gemini_agent.agent import GeminiAgent
from agents.claude_agent.agent import ClaudeAgent
from runtime.tool_manager.consensus_manager import ConsensusManager

logger = logging.getLogger("MultiAIOrchestrator")

class MultiAIOrchestrator:
    """
    Orchestrates multiple AI agents to get a combined trading decision.
    """
    def __init__(self):
        self.agents = {
            "GPT": GPTAgent(),
            "Gemini": GeminiAgent(),
            "Claude": ClaudeAgent()
        }
        self.consensus_manager = ConsensusManager()

    async def get_combined_decision(self, market_data: dict) -> dict:
        """
        Request decisions from all agents in parallel and aggregate them.
        """
        logger.info(f"Requesting decisions from {len(self.agents)} agents...")
        
        # Run agents in parallel using threads to avoid blocking
        tasks = []
        agent_names = list(self.agents.keys())
        
        for name in agent_names:
            tasks.append(self._get_agent_decision(name, market_data))
        
        results = await asyncio.gather(*tasks)
        
        agent_results = dict(zip(agent_names, results))
        
        # Aggregate results using ConsensusManager
        final_decision = self.consensus_manager.aggregate_decisions(agent_results)
        
        # Add individual agent decisions to metadata for logging/storage
        final_decision["metadata"]["individual_decisions"] = agent_results
        
        return final_decision

    async def _get_agent_decision(self, agent_name, market_data):
        try:
            # Using to_thread because agent.make_decision is currently synchronous
            loop = asyncio.get_running_loop()
            decision = await loop.run_in_executor(None, self.agents[agent_name].make_decision, market_data)
            return decision
        except Exception as e:
            logger.error(f"Error getting decision from {agent_name}: {e}")
            return None
