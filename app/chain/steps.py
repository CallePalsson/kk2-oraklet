import json

from app.chain.runnable import Runnable
from app.schemas import PromptBuilderInput, PromptBuilderOutput


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
