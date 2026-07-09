import asyncio
import json
import re
import yaml

DEFAULT_RUNTIME = {
    "temperature": 0.2,
    "max_tokens": 2048,
    "top_p": 0.90,
    "presence_penalty": 0.0,
    "stop": ["---", "[SYSTEM LOG]"]
}

async def read_file(path: str) -> str:
    loop = asyncio.get_running_loop()

    def _read():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    return await loop.run_in_executor(None, _read)


def split_front_matter(content: str):
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)"
    match = re.match(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return "", content.strip()


def validate_config(raw_yaml: str) -> dict:
    if not raw_yaml.strip():
        return {"runtime_parameters": dict(DEFAULT_RUNTIME)}

    try:
        parsed = yaml.safe_load(raw_yaml)
    except yaml.YAMLError:
        return {"runtime_parameters": dict(DEFAULT_RUNTIME)}

    if not isinstance(parsed, dict):
        return {"runtime_parameters": dict(DEFAULT_RUNTIME)}

    runtime = parsed.get("runtime_parameters", {})
    if not isinstance(runtime, dict):
        runtime = {}

    runtime.setdefault("temperature", DEFAULT_RUNTIME["temperature"])
    runtime.setdefault("max_tokens", DEFAULT_RUNTIME["max_tokens"])
    runtime.setdefault("top_p", DEFAULT_RUNTIME["top_p"])
    runtime.setdefault("presence_penalty", DEFAULT_RUNTIME["presence_penalty"])
    runtime.setdefault("stop", list(DEFAULT_RUNTIME["stop"]))

    if "max_output_tokens" in runtime and "max_tokens" not in runtime:
        runtime["max_tokens"] = runtime.pop("max_output_tokens")

    stop = runtime.get("stop")
    if isinstance(stop, list):
        runtime["stop"] = stop
    else:
        runtime["stop"] = list(DEFAULT_RUNTIME["stop"])

    parsed["runtime_parameters"] = runtime
    return parsed


async def load_agent_config(path: str) -> dict:
    content = await read_file(path)
    raw_yaml, body = split_front_matter(content)
    config = validate_config(raw_yaml)
    config.setdefault("agent_name", "UNKNOWN")
    config.setdefault("model_target", "hermes-3-llama3-8b")
    config["system_instruction_body"] = body
    config.setdefault("runtime_parameters", dict(DEFAULT_RUNTIME))
    return config
