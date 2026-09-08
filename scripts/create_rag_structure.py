import os

files = [
    "rag/README.md",
    "rag/fundamental/financial_statement.md",
    "rag/fundamental/valuation.md",
    "rag/fundamental/intrinsic_value.md",
    "rag/technical/moving_average.md",
    "rag/technical/rsi.md",
    "rag/technical/macd.md",
    "rag/technical/volume.md",
    "rag/macro/interest_rate.md",
    "rag/macro/inflation.md",
    "rag/macro/exchange_rate.md",
    "rag/macro/business_cycle.md",
    "rag/strategy/value_investing.md",
    "rag/strategy/momentum.md",
    "rag/strategy/trend_following.md",
    "rag/strategy/mean_reversion.md",
    "rag/psychology/behavioral_finance.md",
    "rag/psychology/loss_aversion.md",
    "rag/psychology/confirmation_bias.md",
    "rag/psychology/fear_greed.md",
    "rag/risk/position_sizing.md",
    "rag/risk/diversification.md",
    "rag/risk/drawdown.md",
    "rag/risk/risk_reward.md",
    "rag/investors/benjamin_graham.md",
    "rag/investors/warren_buffett.md",
    "rag/investors/peter_lynch.md",
    "rag/investors/howard_marks.md"
]

for f in files:
    with open(f, 'w') as file:
        pass
print("All files created.")
