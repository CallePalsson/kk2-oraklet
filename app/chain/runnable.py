from typing import Generic, TypeVar


InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")
NextOutputT = TypeVar("NextOutputT")


class Runnable(Generic[InputT, OutputT]):
    def __or__(
        self,
        other: "Runnable[OutputT, NextOutputT]",
    ) -> "RunnableSequence[InputT, NextOutputT]":
        if isinstance(self, RunnableSequence):
            return RunnableSequence([*self.steps, other])
        return RunnableSequence([self, other])

    def invoke(self, value: InputT) -> OutputT:
        raise NotImplementedError


class RunnableSequence(Runnable[InputT, OutputT]):
    def __init__(self, steps: list[Runnable]):
        self.steps = steps

    def __or__(
        self,
        other: Runnable[OutputT, NextOutputT],
    ) -> "RunnableSequence[InputT, NextOutputT]":
        return RunnableSequence([*self.steps, other])

    def invoke(self, value: InputT) -> OutputT:
        result = value
        for step in self.steps:
            result = step.invoke(result)
        return result
