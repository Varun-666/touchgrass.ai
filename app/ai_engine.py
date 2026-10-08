import json
import os
import re
from functools import lru_cache
from typing import Any

from .schemas import Mission, MissionRequest

MODEL_ID = os.getenv("TOUCHGRASS_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")
MAX_NEW_TOKENS = int(os.getenv("TOUCHGRASS_MAX_NEW_TOKENS", "320"))
TEMPERATURE = float(os.getenv("TOUCHGRASS_TEMPERATURE", "0.75"))

SYSTEM_PROMPT = """You are TouchGrass, a concise outdoor activity designer.
Your job is to turn a user's preferences into one safe, realistic outdoor mission.
The mission must make the screen interaction short and encourage the user to put the phone away.
Do not suggest dangerous activities, restricted-area entry, approaching wildlife, consuming wild plants,
climbing unsafe structures, or anything requiring specialist equipment.
Return ONLY valid JSON with exactly these keys:
{
  \"title\": string,
  \"reason\": string,
  \"duration_minutes\": integer,
  \"steps\": [string, string, string],
  \"look_for\": [string, string, string],
  \"phone_rule\": string,
  \"safety\": string,
  \"closing_line\": string
}
Keep every string short. The activity must be doable by an ordinary person.
"""


@lru_cache(maxsize=1)
def load_model():
    """Load the open-weight model once and keep it in memory."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype="auto",
        device_map="auto",
    )
    model.eval()
    return tokenizer, model


def _device_name(model: Any) -> str:
    try:
        return str(model.device)
    except Exception:
        return "auto"


def _build_prompt(request: MissionRequest) -> str:
    interests = ", ".join(request.interests) if request.interests else "no specific interests"
    return (
        f"Mode: {request.mode}\n"
        f"Available time: {request.duration} minutes\n"
        f"Energy: {request.energy}\n"
        f"Setting: {request.setting}\n"
        f"Interests: {interests}\n"
        f"Goal: {request.goal}\n"
        "Create one mission. Prefer observation, walking, gardening, reflection, or gentle exploration."
    )


def _extract_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None


def _fallback(request: MissionRequest, reason: str = "local model fallback") -> Mission:
    presets = {
        "nature": {
            "title": "The 5-Senses Walk",
            "reason": "A low-pressure way to notice details you normally walk past.",
            "steps": [
                "Walk slowly for five minutes without your phone in your hand.",
                "Find one thing to notice with each sense, without touching unknown plants.",
                "Sit or stand still for two minutes and notice what changed around you.",
            ],
            "look_for": ["bird sounds", "leaf shapes", "moving shadows"],
        },
        "explore": {
            "title": "The One-Block Detour",
            "reason": "A tiny change of route can make a familiar place feel new.",
            "steps": [
                "Choose a safe, familiar starting point.",
                "Take a different pedestrian route for ten minutes.",
                "Return using your normal route and name one new detail you noticed.",
            ],
            "look_for": ["interesting buildings", "trees or gardens", "small local details"],
        },
        "garden": {
            "title": "Garden Detective",
            "reason": "A short observation round helps you care for plants before changing anything.",
            "steps": [
                "Walk around your plants and inspect leaves and soil visually.",
                "Note one plant that looks different from yesterday or last week.",
                "Remove only obvious dead material if you already know the plant is safe to handle.",
            ],
            "look_for": ["dry soil", "yellowing leaves", "new growth"],
        },
    }
    p = presets[request.mode]
    return Mission(
        **p,
        duration_minutes=request.duration,
        phone_rule="Set a timer if needed, then keep the phone in your pocket for the rest of the mission.",
        safety="Stay in a familiar safe area, follow local rules, and do not approach wildlife or consume unknown plants.",
        closing_line="Mission accepted. Now go do it.",
        model=f"fallback ({reason})",
        local=True,
    )


def generate_mission(request: MissionRequest) -> Mission:
    try:
        tokenizer, model = load_model()
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_prompt(request)},
        ]
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        )
        inputs = {key: value.to(model.device) for key, value in inputs.items()}
        import torch
        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=True,
                temperature=TEMPERATURE,
                top_p=0.9,
            )
        generated = outputs[0][inputs["input_ids"].shape[-1]:]
        raw = tokenizer.decode(generated, skip_special_tokens=True)
        data = _extract_json(raw)
        if not data:
            return _fallback(request, "model returned non-JSON")

        data["duration_minutes"] = request.duration
        data["model"] = MODEL_ID
        data["local"] = True
        mission = Mission.model_validate(data)
        if len(mission.steps) != 3 or len(mission.look_for) != 3:
            return _fallback(request, "invalid mission shape")
        return mission
    except Exception as exc:
        # The fallback keeps the demo usable when a model cannot load, while the
        # normal path above remains fully local/open-model inference.
        return _fallback(request, type(exc).__name__)


def model_status() -> dict[str, Any]:
    if load_model.cache_info().currsize:
        try:
            _, model = load_model()
            return {"loaded": True, "model": MODEL_ID, "device": _device_name(model), "local": True}
        except Exception as exc:
            return {"loaded": False, "model": MODEL_ID, "device": "unknown", "local": True, "error": type(exc).__name__}
    return {
        "loaded": False,
        "model": MODEL_ID,
        "device": "not loaded",
        "local": True,
        "note": "Model loads on the first mission generation.",
    }
