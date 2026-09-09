# Risk-Reward Ratio

## Core Principle
The Risk-Reward Ratio measures the potential reward for every dollar of risk taken on an investment. It is essential for determining if a potential trade is worth the risk.

## Analysis Relevance
- The RAG engine should use this ratio to validate the attractiveness of potential entries.

## Decision Guidelines
- Prefer trades where the potential reward significantly outweighs the potential risk.
- If the risk-reward ratio is unfavorable, lean towards a 'HOLD' or 'REJECT' decision.

## Strategy Validation Signals
- Successful strategies typically maintain a positive expected value, defined by favorable risk-reward ratios over multiple trades.

## Risk Signals
- A very low risk-reward ratio is a warning that the potential downside far exceeds the upside, regardless of confidence.

## Common Misinterpretations
- Assuming a high reward potential justifies taking unlimited risk.
- Calculating risk-reward ratios without accounting for the probability of the reward or the risk event.

## Anti-Hallucination Rules
- Do NOT fabricate price targets or stop-loss points to calculate a risk-reward ratio.
- Do NOT claim a trade has a specific ratio without having the necessary input price/target data.
