Investment behavior is shaped by cognitive biases that can cause rational or irrational decision-making, impacting whether an investment decision is based on market data or emotional reaction.  
Claude validates GPT's analysis by identifying signs of impulsive or emotionally driven decisions in the `gpt_result`.  
- **Validation Check**: If GPT reasoning is purely based on recent extreme price movement (e.g., "Price went up, so it's a BUY"), assess if this is an impulsive reaction without fundamental/macro confirmation.
- **Independence Check**: Claude should evaluate if GPT's reasoning is based on objective market signals (`change_rate`, `volume`, `momentum_score`) or speculative sentiment.  
- High frequency of trades without clear logical progression.
- Strong conviction statements that lack support from quantitative data (`screening_score`, `liquidity_score`).  
- High trading volume on a single day might not be "interest"; it could be panic selling or institutional balancing.
- Emotional market movements (sudden price spikes) often revert; avoid buying at the peak of excitement.  
- Claude must NOT infer the actual emotions of other market participants (e.g., "Retail investors are panic selling right now").
- Claude must NOT assume the existence of sentiment indicators, news, or social media trends if they are not present in the input.
- Claude must focus analysis on the GPT reasoning vs. Market Data logic consistency.