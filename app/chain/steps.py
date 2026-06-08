import json
from typing import Any

from transformers import pipeline

from app.chain.runnable import Runnable
from app.config import settings
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
        _text_generator = pipeline(
            task="text-generation",
            model=settings.model_name,
        )

    return _text_generator


class PromptBuilder(Runnable[PromptBuilderInput, PromptBuilderOutput]):
    def invoke(self, value: PromptBuilderInput) -> PromptBuilderOutput:
        stats_json = json.dumps(
            value.stats,
            ensure_ascii=False,
            separators=(",", ":"),
        )

        prompt = (
            "You are a data oracle.\n"
            "Answer only using information from the dataset statistics.\n"
            "Keep the answer very short.\n"
            "Never repeat the question.\n"
            "Do not invent information.\n"
            "If the answer is a number, return only the number.\n\n"
            f"Statistics:\n{stats_json}\n\n"
            f"Question: {value.question}\n"
            "Answer:"
        )

        return PromptBuilderOutput(
            question=value.question,
            prompt=prompt,
        )


class LLMRunner(Runnable[PromptBuilderOutput, LLMRunnerOutput]):
    def invoke(self, value: PromptBuilderOutput) -> LLMRunnerOutput:
        try:
            generator = get_text_generator()

            result = generator(
                value.prompt,
                max_new_tokens=20,
                temperature=0.1,
                do_sample=False,
                return_full_text=False,
                pad_token_id=generator.tokenizer.eos_token_id,
            )

            raw_text = result[0]["generated_text"]

        except Exception as exc:
            raise RuntimeError(
                "Could not generate an answer with the language model."
            ) from exc

        return LLMRunnerOutput(
            question=value.question,
            raw_text=raw_text,
            model=settings.model_name,
        )


class ResponseParser(Runnable[LLMRunnerOutput, ResponseParserOutput]):
    def invoke(self, value: LLMRunnerOutput) -> ResponseParserOutput:
        answer = value.raw_text.strip()


        if "Answer:" in answer:
            answer = answer.split("Answer:", maxsplit=1)[-1].strip()


        answer = answer.split("\n")[0].strip()


        if "Question:" in answer:
            answer = answer.split("Question:")[0].strip()

        answer = answer[:200].strip()

        if not answer:
            answer = (
                "The model could not generate a clear answer."
            )

        return ResponseParserOutput(
            question=value.question,
            answer=answer,
            model=value.model,
        )