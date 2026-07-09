# Think Tank Pipeline

A 100% local, closed-loop research automation system. Three specialized agents (SCUBA, MOZART, PNUT) execute a rolling critique loop against a local LLM inference endpoint, iterating until configurable quality thresholds are met.

## Architecture

```
FILESYSTEM (SOUL.md configs) ──> THINK TANK ENGINE ──> LOCAL INFERENCE (Ollama/vLLM)
                                         │                        │
                                         │                        v
                                         └── PNUT AUDITOR <─── Response
                                                │
                                   If score < threshold: critique loops back
                                   If score >= threshold: writes judgementday.md
```

## Requirements

- Python 3.10+
- [httpx](https://www.python-httpx.org/) + [PyYAML](https://pyyaml.org/)
- Optional: [Crawl4AI](https://github.com/unclecode/crawl4ai) (for web scraping)
- Optional: Ollama or vLLM server running locally

## Quick Start

```bash
pip install httpx pyyaml

# Run with mock data (no LLM required):
python think_tank/think_tank_orchestrator.py

# Run against a local Ollama endpoint:
python -c "
import asyncio
from engine.orchestrator import ThinkTankOrchestrator

async def main():
    orch = ThinkTankOrchestrator(
        target_url='https://example.com/research-target',
        use_local_llm=True,
        inference_endpoint='http://localhost:11434/v1/chat/completions'
    )
    await orch.execute_symphony()

asyncio.run(main())
"
```

## Agent SOUL.md Files

Each agent is configured by a `SOUL.md` file containing YAML front-matter and identity instructions:

| Agent | File | Role |
|-------|------|------|
| SCUBA | `think_tank/scuba/SOUL.md` | Web extraction & scraping |
| MOZART | `think_tank/mozart/SOUL.md` | Data synthesis & categorization |
| PNUT | `think_tank/pnut/SOUL.md` | Factual audit & critique scoring |

All runtime parameters (temperature, max_tokens, top_p, stop sequences) are configurable per agent via the front-matter block.

## Pipeline Flow

1. **SCUBA** scrapes the target URL (via Crawl4AI or local LLM)
2. **MOZART** synthesizes the raw data into a structured thematic brief
3. **PNUT** scores the output (0.00–1.00) and extracts critique text
4. If score >= threshold: writes `think_tank/judgementday.md` and completes
5. If score < threshold: critique feeds back into the next iteration's prompt
6. If max iterations reached without meeting threshold: pipeline fails

## Database

Telemetry is logged to `pipeline.db` (SQLite):

- `pipeline_runs` — run metadata and status (RUNNING/REJECTED/COMPLETED/FAILED)
- `iteration_telemetry` — per-iteration outputs, scores, and critique summaries

## Configuration Reference

```python
ThinkTankOrchestrator(
    target_url="https://...",       # Research target
    project_threshold=0.95,         # Minimum PNUT score (0.0–1.0)
    max_iterations=3,               # Max retry loops before failure
    inference_endpoint="http://localhost:11434/v1/chat/completions",
    use_local_llm=False             # Set True to use real LLM inference
)
```
