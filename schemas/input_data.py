from pydantic import BaseModel


class InputData(BaseModel):
    mark: float
    knowledge_level: str
    learning_style: str
    subject: str
