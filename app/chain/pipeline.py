from app.chain.steps import LLMRunner, PromptBuilder, ResponseParser


def build_chain():
    return PromptBuilder() | LLMRunner() | ResponseParser()
