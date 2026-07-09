import asyncio
import os
import uuid
from .config_loader import load_agent_config
from .inference_client import InferenceClient, OLLAMA_ENDPOINT
from .agents import ScubaAgent, MozartAgent, PnutAgent
from .critique_accumulator import CritiqueAccumulator
from .database import init_db, create_run, update_run_status, insert_iteration, DB_PATH as DEFAULT_DB_PATH

JUDGEMENT_DAY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   "think_tank", "judgementday.md")
SCUBA_SOUL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "architect", "SOUL.md")
MOZART_SOUL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "think_tank", "mozart", "SOUL.md")
PNUT_SOUL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "think_tank", "pnut", "SOUL.md")


class ThinkTankOrchestrator:
    def __init__(self, target_url: str, project_threshold: float = 0.95,
                 max_iterations: int = 3, inference_endpoint: str = OLLAMA_ENDPOINT,
                 use_local_llm: bool = False, db_path: str = None):
        self.target_url = target_url
        self.threshold = project_threshold
        self.max_iterations = max_iterations
        self.iteration_count = 0
        self.use_local_llm = use_local_llm

        self.critique_accumulator = CritiqueAccumulator()
        self.inference_client = InferenceClient(endpoint=inference_endpoint) if use_local_llm else None

        self.scuba = ScubaAgent(soul_path=SCUBA_SOUL_PATH)
        self.mozart = MozartAgent(soul_path=MOZART_SOUL_PATH)
        self.pnut = PnutAgent(soul_path=PNUT_SOUL_PATH)

        self.db_path = db_path or DEFAULT_DB_PATH
        self.run_id = None

    async def initialize(self):
        await self.scuba.load_config()
        await self.mozart.load_config()
        await self.pnut.load_config()
        init_db(self.db_path)
        self.run_id = create_run(self.target_url, self.db_path)

    async def run_scuba(self, url: str) -> str:
        critique_block = self.critique_accumulator.build_telemetry_block()
        raw_data = await self.scuba.run(
            url=url,
            critique_block=critique_block,
            inference_client=self.inference_client,
            model_target=self.scuba.config.get("model_target"),
            runtime_params=self.scuba.config.get("runtime_parameters")
        )
        scuba_path = os.path.join(
            os.path.dirname(self.db_path) if self.db_path else "/tmp",
            f"scuba_output_i{self.iteration_count}.md"
        )
        insert_iteration(self.run_id, self.iteration_count, scuba_raw_output_path=scuba_path,
                         pnut_critique_summary=None, db_path=self.db_path)
        return raw_data

    async def run_mozart(self, raw_markdown: str) -> str:
        critique_block = self.critique_accumulator.build_telemetry_block()
        synthesis = await self.mozart.run(
            raw_markdown=raw_markdown,
            critique_block=critique_block,
            inference_client=self.inference_client,
            model_target=self.mozart.config.get("model_target"),
            runtime_params=self.mozart.config.get("runtime_parameters")
        )
        insert_iteration(self.run_id, self.iteration_count,
                         mozart_synthesis_path="in_memory",
                         pnut_critique_summary=None, db_path=self.db_path)
        return synthesis

    async def run_pnut(self, synthesis: str) -> tuple:
        critique_block = self.critique_accumulator.build_telemetry_block()
        score, critique, final_output = await self.pnut.run(
            synthesis=synthesis,
            critique_block=critique_block,
            inference_client=self.inference_client,
            model_target=self.pnut.config.get("model_target"),
            runtime_params=self.pnut.config.get("runtime_parameters")
        )
        insert_iteration(self.run_id, self.iteration_count,
                         pnut_score=score, pnut_critique_summary=critique,
                         db_path=self.db_path)
        return score, critique, final_output

    async def execute_symphony(self):
        print("=" * 60)
        print("THINK TANK AUTOMATION FLEET: INITIALIZING RUN STATE")
        print("=" * 60)

        await self.initialize()

        while self.iteration_count < self.max_iterations:
            print(f"\n--- EXECUTION CYCLE: ITERATION LEVEL {self.iteration_count + 1} ---")

            raw_data = await self.run_scuba(self.target_url)
            synthesis = await self.run_mozart(raw_data)
            score, critique, final_output = await self.run_pnut(synthesis)

            print(f"[SYSTEM LOG] PNUT Evaluation Certainty Score: {score}")

            if score >= self.threshold and final_output is not None:
                print("\n" + "=" * 60)
                print(f"TARGET THRESHOLD MATCHED ({score} >= {self.threshold})")
                print("Writing final telemetry report to: judgementday.md")
                print("=" * 60)

                os.makedirs(os.path.dirname(JUDGEMENT_DAY_PATH), exist_ok=True)
                with open(JUDGEMENT_DAY_PATH, "w") as f:
                    f.write(final_output)

                update_run_status(self.run_id, "COMPLETED", self.iteration_count, self.db_path)
                if self.inference_client:
                    await self.inference_client.close()
                return True
            else:
                print(f"REJECTION STATE triggered. Certainty score {score} "
                      f"falls below target requirement ({self.threshold}).")
                if critique:
                    self.critique_accumulator.append(critique)
                self.iteration_count += 1
                update_run_status(self.run_id, "REJECTED", self.iteration_count, self.db_path)

        print("\nPipeline execution terminated: Max iteration ceiling reached "
              "without meeting target threshold limits.")
        update_run_status(self.run_id, "FAILED", self.iteration_count, self.db_path)
        if self.inference_client:
            await self.inference_client.close()
        return False
