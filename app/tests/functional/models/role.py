from pydantic import BaseModel


class Role(BaseModel):
    id: str | None = None
    name: str | None = None
