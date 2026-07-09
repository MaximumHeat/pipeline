import asyncio
import os
import re
from .config_loader import load_agent_config

SCUBA_SOUL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "architect", "SOUL.md")
MOZART_SOUL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "think_tank", "mozart", "SOUL.md")
PNUT_SOUL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "think_tank", "pnut", "SOUL.md")


class ScubaAgent:
    def __init__(self, soul_path: str = SCUBA_SOUL_PATH):
        self.soul_path = soul_path
        self.config = None

    async def load_config(self):
        self.config = await load_agent_config(self.soul_path)
        return self.config

    def build_system_prompt(self) -> str:
        return self.config.get("system_instruction_body", "")

    def build_user_prompt(self, url: str, critique_block: str = "") -> str:
        parts = [f"### EXECUTION TARGET INGEST\n{url}"]
        if critique_block:
            parts.append(critique_block)
        return "\n\n".join(parts)

    async def run(self, url: str, critique_block: str = "", inference_client=None,
                  model_target: str = None, runtime_params: dict = None) -> str:
        if self.config is None:
            await self.load_config()
        print(f"\n[SCUBA] Infiltrating target source: {url}...")
        if critique_block:
            print(f"[SCUBA] Adjusting collection parameters based on feedback: {critique_block}")

        if inference_client is not None:
            system_prompt = self.build_system_prompt()
            user_prompt = self.build_user_prompt(url, critique_block)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            model = model_target or self.config.get("model_target", "hermes-3-llama3-8b")
            params = runtime_params or self.config.get("runtime_parameters", {})
            resp = await inference_client.complete(model, messages, params)
            choices = resp.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""

        try:
            from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
            browser_conf = BrowserConfig(headless=True)
            run_conf = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
            async with AsyncWebCrawler(config=browser_conf) as crawler:
                result = await crawler.arun(url=url, config=run_conf)
                if result.success:
                    return result.markdown
                return f"Extraction Error: {result.error_message}"
        except ImportError:
            print("[SCUBA] Warning: Crawl4AI package not detected. Utilizing local fallback simulation...")
            await asyncio.sleep(1.5)
            return f"# Raw Data Mock for {url}\n- Sourced clothing logistics metric: 42% margin gap in vintage wholesale supply chains."


class MozartAgent:
    def __init__(self, soul_path: str = MOZART_SOUL_PATH):
        self.soul_path = soul_path
        self.config = None

    async def load_config(self):
        self.config = await load_agent_config(self.soul_path)
        return self.config

    def build_system_prompt(self) -> str:
        return self.config.get("system_instruction_body", "")

    def build_user_prompt(self, raw_markdown: str, critique_block: str = "") -> str:
        parts = [f"### EXECUTION TARGET INGEST\n{raw_markdown}"]
        if critique_block:
            parts.append(critique_block)
        return "\n\n".join(parts)

    async def run(self, raw_markdown: str, critique_block: str = "",
                  inference_client=None, model_target: str = None,
                  runtime_params: dict = None) -> str:
        if self.config is None:
            await self.load_config()
        print("\n[MOZART] Composing raw text block into thematic categories...")

        if inference_client is not None:
            system_prompt = self.build_system_prompt()
            user_prompt = self.build_user_prompt(raw_markdown, critique_block)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            model = model_target or self.config.get("model_target", "hermes-3-llama3-8b")
            params = runtime_params or self.config.get("runtime_parameters", {})
            resp = await inference_client.complete(model, messages, params)
            choices = resp.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""

        await asyncio.sleep(1)
        return (
            "## MOZART SYNTHESIS REPORT\n"
            "### CATEGORIZED DATA BLOCKS\n"
            f"{raw_markdown}\n\n"
            "### IDENTIFIED ANOMALIES & OPPORTUNITIES\n"
            "- Unbranded premium garments pass through corporate sorting chains due to low employee visual pattern recognition.\n"
            "### TECHNICAL SYSTEM OBSTACLES\n"
            "- Low throughput capability on basic scraping parameters if CAPTCHAs are triggered."
        )


class PnutAgent:
    SCORE_PATTERN = re.compile(r"([01]\.\d{2})")

    def __init__(self, soul_path: str = PNUT_SOUL_PATH):
        self.soul_path = soul_path
        self.config = None

    async def load_config(self):
        self.config = await load_agent_config(self.soul_path)
        return self.config

    def build_system_prompt(self) -> str:
        return self.config.get("system_instruction_body", "")

    def build_user_prompt(self, synthesis: str, critique_block: str = "") -> str:
        parts = [f"### EXECUTION TARGET INGEST\n{synthesis}"]
        if critique_block:
            parts.append(critique_block)
        return "\n\n".join(parts)

    @classmethod
    def extract_score(cls, text: str) -> float:
        matches = cls.SCORE_PATTERN.findall(text)
        if matches:
            return float(matches[-1])
        return 0.0

    @classmethod
    def extract_critique(cls, text: str) -> str:
        lines = text.strip().split("\n")
        critique_lines = []
        in_critique = False
        for line in lines:
            if re.search(r"(?i)(critique|feedback|missing|failure|vector|error|issue|gap)", line):
                if not in_critique:
                    critique_lines.append(line.strip("- ").strip())
                else:
                    critique_lines.append(line.strip("- ").strip())
                in_critique = True
            elif in_critique and line.strip():
                critique_lines.append(line.strip("- ").strip())
            else:
                in_critique = False
        if critique_lines:
            return " ".join(critique_lines)
        return ""

    async def run(self, synthesis: str, critique_block: str = "",
                  inference_client=None, model_target: str = None,
                  runtime_params: dict = None) -> tuple:
        if self.config is None:
            await self.load_config()
        print("\n[PNUT] Conducting critical review and calculating factual certainty...")

        if inference_client is not None:
            system_prompt = self.build_system_prompt()
            user_prompt = self.build_user_prompt(synthesis, critique_block)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            model = model_target or self.config.get("model_target", "hermes-3-llama3-8b")
            params = runtime_params or self.config.get("runtime_parameters", {})
            resp = await inference_client.complete(model, messages, params)
            choices = resp.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content", "")
            else:
                content = ""
            if not content:
                return 0.0, "", None
            score = self.extract_score(content)
            critique = self.extract_critique(content)
            if score >= 0.95:
                final_report = (
                    f"# JUDGEMENT DAY REPORT\n"
                    "### FINAL VERIFIED FINDINGS\n"
                    f"{synthesis}\n\n"
                    "### CRITIQUE & SYSTEM LOGIC VERIFIED\n"
                    f"{critique}\n"
                    f"- Final Certainty Threshold Achieved: {score}"
                )
                return score, critique, final_report
            return score, critique, None

        await asyncio.sleep(1.5)
        score = 0.88
        critique = "Missing explicit volume data points on Midwestern independent clothing hubs."
        return score, critique, None
