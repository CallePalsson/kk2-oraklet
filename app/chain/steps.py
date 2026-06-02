import json
from typing import Any

from app.config import settings
from app.chain.runnable import Runnable
from app.schemas import (
    LLMRunnerOutput,
    PromptBuilderInput,
    PromptBuilderOutput,
    ResponseParserOutput,
)


_text_generator: Any | None = None


def get_text_generator() -> Any:
    global _text_generator

    if _text_generator is None:
        from transformers import pipeline

        _text_generator = pipeline(
            "text-generation",
            model=settings.model_name,
        )

    return _text_generator


class PromptBuilder(Runnable[PromptBuilderInput, PromptBuilderOutput]):
    def invoke(self, value: PromptBuilderInput) -> PromptBuilderOutput:
        stats_json = json.dumps(value.stats, ensure_ascii=False, indent=2)
        prompt = (
            "Du är ett data-orakel som svarar kort på svenska.\n"
            "Använd bara statistiken från datasetet när du svarar.\n\n"
            f"Statistik:\n{stats_json}\n\n"
            f"Fråga: {value.question}\n"
            "Svar:"
        )
        return PromptBuilderOutput(question=value.question, prompt=prompt)


class LLMRunner(Runnable[PromptBuilderOutput, LLMRunnerOutput]):
    def invoke(self, value: PromptBuilderOutput) -> LLMRunnerOutput:
        generator = get_text_generator()

        try:
            result = generator(
                value.prompt,
                max_new_tokens=120,
                do_sample=False,
                return_full_text=False,
            )
        except Exception as exc:
            raise RuntimeError("Could not generate an answer with SmolLLM") from exc

        raw_text = result[0]["generated_text"]
        return LLMRunnerOutput(
            question=value.question,
            raw_text=raw_text,
            model=settings.model_name,
        )


class ResponseParser(Runnable[LLMRunnerOutput, ResponseParserOutput]):
    def invoke(self, value: LLMRunnerOutput) -> ResponseParserOutput:
        answer = value.raw_text.strip()
        if "Svar:" in answer:
            answer = answer.split("Svar:", maxsplit=1)[-1].strip()

        if not answer:
            answer = "Jag kunde inte hitta ett tydligt svar i modellens output."

        return ResponseParserOutput(
            question=value.question,
            answer=answer,
            model=value.model,
        )
