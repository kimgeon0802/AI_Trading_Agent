Volatility measures the magnitude of price fluctuations. While volatility creates trading opportunities, excessive volatility poses significant risks to capital preservation.

Use `change_rate` and `volume` data provided in the `market_data` to assess current volatility levels.

- When a stock shows extreme price range (e.g., high `change_rate` volatility) without clear fundamental news in `gpt_result`, increase risk awareness.
- If GPT confidence is low and volatility is high, a 'HOLD' or 'REJECT' decision is often more prudent than 'BUY'.

- **Anti-Hallucination Rule**: Claude must not generate or hallucinate metrics like "Historical Volatility," "ATR," or "Standard Deviation" if they are not explicitly present in the input `market_data`.
- **Contextual Awareness**: Focus on the *volatility observed in the provided daily change data* rather than inferred long-term statistical volatility.

- High volatility alone does not guarantee high returns; it often increases the risk of premature stop-outs.
- Low volume during high price volatility is a significant risk signal.