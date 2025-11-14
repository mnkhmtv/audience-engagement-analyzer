from pydantic import BaseModel
from pydantic import ConfigDict


class Entity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

