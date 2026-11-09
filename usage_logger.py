"""Reusable token and cost logger for LLM API calls.

Framework-agnostic: it takes plain numbers (model name, token counts), so it
works with any SDK or provider. Each call becomes one JSON line in a log file.

Example:
    logger = UsageLogger("usage_log.jsonl")
    entry = logger.log(
        model="claude-haiku-5-5",
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        latency_s=1.2,
        project="summarizer",        # any extra fields are stored as-is
    )
    print(logger.report())
"""
import json
from datetime import datetime, timezone
from pathlib import Path

# USD per million tokens (input, output), for prompts up to 100K tokens.
# Taken from third-party pages quoting Anthropic's pricing; verify against the
# official pricing page, and pass your own dict to UsageLogger(prices=...) to override.
DEFAULT_PRICES = {
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00),
}


class UsageLogger:
    def __init__(self, log_file="usage_log.jsonl", prices=None):
        self.log_file = Path(log_file)
        self.prices = dict(DEFAULT_PRICES if prices is None else prices)

    def estimate_cost(self, model, input_tokens, output_tokens):
        """Estimated USD cost, or None if the model's price is unknown."""
        if model not in self.prices:
            return None
        price_in, price_out = self.prices[model]
        return (input_tokens * price_in + output_tokens * price_out) / 1_000_000

    def log(self, model, input_tokens, output_tokens, latency_s=None, **extra):
        """Append one call to the log file and return the stored record."""
        cost = self.estimate_cost(model, input_tokens, output_tokens)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "est_cost_usd": None if cost is None else round(cost, 6),
            "latency_s": None if latency_s is None else round(latency_s, 2),
            **extra,
        }
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def read_entries(self):
        """All logged calls as a list of dicts (empty if there is no log yet)."""
        if not self.log_file.exists():
            return []
        text = self.log_file.read_text(encoding="utf-8")
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    def report(self):
        """Totals per model as a printable string."""
        entries = self.read_entries()
        if not entries:
            return "No usage logged yet."

        totals = {}
        unpriced = 0
        for e in entries:
            t = totals.setdefault(e["model"], {"calls": 0, "in": 0, "out": 0, "cost": 0.0})
            t["calls"] += 1
            t["in"] += e["input_tokens"]
            t["out"] += e["output_tokens"]
            if e.get("est_cost_usd") is None:
                unpriced += 1
            else:
                t["cost"] += e["est_cost_usd"]

        lines = []
        grand = 0.0
        for model, t in totals.items():
            lines.append(
                f"{model}: {t['calls']} calls, {t['in']:,} in, {t['out']:,} out, ~${t['cost']:.4f}"
            )
            grand += t["cost"]
        lines.append(f"TOTAL: ~${grand:.4f}")
        if unpriced:
            lines.append(f"({unpriced} call(s) had no known price and are counted as $0)")
        return "\n".join(lines)
