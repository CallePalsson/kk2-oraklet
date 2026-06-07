import pytest

from app.chain.runnable import Runnable
from app.chain.steps import LLMRunner, PromptBuilder, ResponseParser
from app.schemas import (
    LLMRunnerOutput,
    PromptBuilderInput,
    PromptBuilderOutput,
    ResponseParserOutput,
)


class FakeLLMRunner(Runnable[PromptBuilderOutput, LLMRunnerOutput]):
    def invoke(self, value: PromptBuilderOutput) -> LLMRunnerOutput:
        return LLMRunnerOutput(
            question=value.question,
            raw_text="Svar: Bryggan har högst vattentemperatur.",
            model="fake-model",
        )


def test_prompt_builder_includes_question_and_stats() -> None:
    result = PromptBuilder().invoke(
        PromptBuilderInput(
            question="Vilken badplats har varmast vatten?",
            stats={"water_temp_c": {"max": 21.4}},
        )
    )

    assert "Vilken badplats har varmast vatten?" in result.prompt
    assert "water_temp_c" in result.prompt
    assert result.question == "Vilken badplats har varmast vatten?"


def test_response_parser_removes_answer_prefix() -> None:
    result = ResponseParser().invoke(
        LLMRunnerOutput(
            question="Vilken badplats har varmast vatten?",
            raw_text="Svar: Bryggan är varmast.",
            model="fake-model",
        )
    )

    assert result == ResponseParserOutput(
        question="Vilken badplats har varmast vatten?",
        answer="Bryggan är varmast.",
        model="fake-model",
    )


def test_chain_runs_steps_with_pipe_operator() -> None:
    chain = PromptBuilder() | FakeLLMRunner() | ResponseParser()

    result = chain.invoke(
        PromptBuilderInput(
            question="Vilken badplats har varmast vatten?",
            stats={"water_temp_c": {"max": 21.4}},
        )
    )

    assert result.answer == "Bryggan har högst vattentemperatur."
    assert result.model == "fake-model"


def test_llm_runner_handles_model_error(monkeypatch) -> None:
    def broken_generator():
        raise OSError("Model could not be loaded")

    monkeypatch.setattr(
        "app.chain.steps.get_text_generator",
        broken_generator,
    )

    with pytest.raises(RuntimeError, match="Could not generate"):
        LLMRunner().invoke(
            PromptBuilderOutput(
                question="Vilken badplats har varmast vatten?",
                prompt="Test prompt",
            )
        )
