import pydantic as pydantic
from pydantic import ConfigDict


class _BaseSchema(pydantic.BaseModel):
    model_config = ConfigDict(from_attributes=True)
