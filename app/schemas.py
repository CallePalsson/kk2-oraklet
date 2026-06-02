from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class UploadDataResponse(BaseModel):
    rows: int
    columns: list[str]
    dtypes: dict[str, str]


class DataStatsResponse(BaseModel):
    stats: dict


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    answer: str
    model: str


class PromptBuilderInput(BaseModel):
    question: str
    stats: dict


class PromptBuilderOutput(BaseModel):
    question: str
    prompt: str


class LLMRunnerOutput(BaseModel):
    question: str
    raw_text: str
    model: str


class ResponseParserOutput(BaseModel):
    question: str
    answer: str
    model: str
