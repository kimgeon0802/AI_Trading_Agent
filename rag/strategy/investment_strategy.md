Investment strategy is the application of disciplined principles to buy or sell securities based on data-driven analysis and risk management, rather than emotional reaction.

This framework acts as the overarching guide for the ClaudeAgent when validating GPT’s decisions. It ensures that the AI checks for logic, risk, and data consistency.

- **Consistency Check**: Does the GPT's "BUY" or "SELL" decision logically follow from the provided `market_data` (e.g., price change, volume, momentum)?
- **Data-Driven Analysis**: Do not form a conviction based on sentiments or external news that are not provided in the `market_data`.
- **Logic Validation**: If the GPT decision is "HOLD", does it align with the absence of strong bullish/bearish signals in the current data?

- **Anti-Hallucination Rule**: Claude must not fabricate market events, macro trends, or technical indicator data (like moving averages) if they are not explicitly provided in the input. Use only provided fields like `change_rate`, `volume`, and `momentum_score`.
- **Contextual Awareness**: Always weigh the GPT's conclusion against the raw market signals provided.

- A strong momentum signal alone does not imply a "BUY"; volume confirmation and risk assessment are mandatory.
- A "HOLD" decision is not an inaction; it is a valid strategy to avoid risk when conditions are unclear.