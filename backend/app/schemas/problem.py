from pydantic import BaseModel, ConfigDict


class ProblemListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    difficulty: str
    summary: str


class ProblemDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    difficulty: str
    summary: str
    requirements: str
    constraints: str
    key_concepts: str
